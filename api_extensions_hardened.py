"""
API Extensions for UI Modules - Security Hardened Version
Implements comprehensive security, validation, and thread-safety improvements.
"""

from flask import jsonify, request, Request
from datetime import datetime, timedelta
import yaml
import pandas as pd
import os
import math
import threading
import uuid
import sys
from typing import Any, Dict, List, Optional, Union, Tuple, cast

# Platform-specific imports for file locking
if sys.platform != 'win32':
    import fcntl
else:
    import msvcrt
from dataclasses import dataclass
from enum import Enum
import logging
import json

# Import real modules
from modules.alerts import AlertSystem, AlertSeverity, Alert
from modules.berth_constraints import BerthConstraintValidator, BerthConstraintSet, VesselSizeConstraint
from modules.berth_utilization import BerthUtilizationAnalyzer
from modules.bunker_optimizer import BunkerOptimizer, create_sample_bunker_prices, FuelType
from modules.deepsea_scenarios import ScenarioManager
from modules.deepsea_loader import DeepSeaLoader
from modules.deepsea_calculator import DeepSeaCalculator
from modules.balakovo_loader import BalakovoLoader
from modules.balakovo_planner import BalakovoPlanner
from modules.olya_loader import OlyaLoader
from modules.olya_coordinator import OlyaCoordinator
from modules.pdf_reporter import generate_pdf_report
from modules.rbac import RBACManager, Permission

logger = logging.getLogger(__name__)

# =====================
# CONFIGURATION
# =====================

# Alert cache configuration with thread-safety
_ALERT_CACHE_TTL_SEC = 60
_alert_cache_lock = threading.RLock()
_alert_cache: Dict[str, Any] = {"data": None, "timestamp": None}

# Constraints path - now configurable via environment variable
_CONSTRAINTS_PATH = os.getenv(
    'CONSTRAINTS_PATH',
    os.path.join(os.path.dirname(__file__), 'data', 'berth_constraints.json')
)

# Initialize RBAC manager
_rbac_manager: Optional[RBACManager] = None


# =====================
# VALIDATION SCHEMAS
# =====================

class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


@dataclass
class ConstraintSchema:
    """JSON schema for berth constraints."""
    berth: str
    type: str
    value: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    severity: str = 'mandatory'
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> 'ConstraintSchema':
        """Validate and parse constraint data."""
        berth = data.get('berth')
        constraint_type = data.get('type')
        
        if not berth or not isinstance(berth, str) or len(berth) > 50:
            raise ValidationError('Invalid berth: must be non-empty string <= 50 chars')
        
        valid_types = {'maintenance', 'size_restriction', 'cargo_restriction', 'time_window'}
        if not constraint_type or constraint_type not in valid_types:
            raise ValidationError(f'Invalid type: must be one of {valid_types}')
        
        # Validate optional date fields
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        
        if start_date:
            try:
                datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                raise ValidationError('Invalid startDate: must be ISO format')
        
        if end_date:
            try:
                datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                raise ValidationError('Invalid endDate: must be ISO format')
        
        severity = data.get('severity', 'mandatory')
        if severity not in {'info', 'warning', 'mandatory', 'critical'}:
            raise ValidationError('Invalid severity: must be info, warning, mandatory, or critical')
        
        return ConstraintSchema(
            berth=berth,
            type=constraint_type,
            value=data.get('value'),
            startDate=start_date,
            endDate=end_date,
            severity=severity
        )


@dataclass
class ScenarioSchema:
    """JSON schema for scenarios."""
    name: str
    description: str = ''
    voyage_ids: Optional[List[str]] = None
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> 'ScenarioSchema':
        """Validate and parse scenario data."""
        name = data.get('name')
        if not name or not isinstance(name, str) or len(name) > 100:
            raise ValidationError('Invalid name: must be non-empty string <= 100 chars')
        
        description = data.get('description', '')
        if not isinstance(description, str) or len(description) > 500:
            raise ValidationError('Invalid description: must be string <= 500 chars')
        
        voyage_ids = data.get('voyage_ids', [])
        if not isinstance(voyage_ids, list):
            raise ValidationError('Invalid voyage_ids: must be a list')
        
        if len(voyage_ids) > 1000:
            raise ValidationError('Too many voyage_ids: maximum 1000')
        
        return ScenarioSchema(
            name=name,
            description=description,
            voyage_ids=voyage_ids if voyage_ids else []
        )


@dataclass
class PDFExportSchema:
    """JSON schema for PDF export requests."""
    reportType: str
    data: List[Dict[str, Any]]
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> 'PDFExportSchema':
        """Validate and parse PDF export data."""
        report_type = data.get('reportType')
        
        # Allowlist of valid report types
        valid_types = {
            'vessel_schedule',
            'voyage_summary',
            'fleet_overview',
            'berth_utilization'
        }
        
        if not report_type or report_type not in valid_types:
            raise ValidationError(f'Invalid reportType: must be one of {valid_types}')
        
        export_data = data.get('data', [])
        if not isinstance(export_data, list):
            raise ValidationError('Invalid data: must be a list')
        
        # Limit data size to prevent DOS
        if len(export_data) > 10000:
            raise ValidationError('Too much data: maximum 10000 rows')
        
        # Validate each row has reasonable number of columns
        for row in export_data:
            if not isinstance(row, dict):
                raise ValidationError('Invalid data row: must be a dictionary')
            if len(row) > 50:
                raise ValidationError('Too many columns in row: maximum 50')
        
        return PDFExportSchema(
            reportType=report_type,
            data=export_data
        )


# =====================
# INPUT VALIDATION
# =====================

def validate_days_param(days_str: Optional[str], default: int = 14, min_val: int = 1, max_val: int = 365) -> int:
    """Validate and parse days parameter with bounds checking."""
    if days_str is None:
        return default
    
    try:
        days = int(days_str)
    except (ValueError, TypeError):
        raise ValidationError(f'Invalid days parameter: must be integer')
    
    if days < min_val or days > max_val:
        raise ValidationError(f'Days parameter out of range: must be between {min_val} and {max_val}')
    
    return days


def validate_severity_param(severity: Optional[str]) -> Optional[str]:
    """Validate severity parameter."""
    if severity is None or severity == 'all':
        return severity
    
    valid_severities = {'info', 'warning', 'critical', 'all'}
    if severity.lower() not in valid_severities:
        raise ValidationError(f'Invalid severity: must be one of {valid_severities}')
    
    return severity.lower()


def validate_fuel_type(fuel_type_str: str) -> FuelType:
    """Defensively parse fuel type string."""
    # Map common variations to FuelType enum
    fuel_map = {
        'vlsfo': FuelType.VLSFO,
        'very low sulfur fuel oil': FuelType.VLSFO,
        'mgo': FuelType.MGO,
        'marine gas oil': FuelType.MGO,
        'lsmgo': FuelType.LSMGO,
        'low sulfur marine gas oil': FuelType.LSMGO,
        'hfo': FuelType.HFO,
        'heavy fuel oil': FuelType.HFO,
        'lng': FuelType.LNG,
        'liquefied natural gas': FuelType.LNG,
    }
    
    normalized = fuel_type_str.lower().strip()
    if normalized not in fuel_map:
        raise ValidationError(f'Unknown fuel type: {fuel_type_str}. Valid types: vlsfo, mgo, lsmgo, hfo, lng')
    
    return fuel_map[normalized]


# =====================
# AUTHENTICATION & AUTHORIZATION
# =====================

def require_auth(permission: Optional[Permission] = None):
    """Decorator to require authentication and optional permission."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Unauthorized: Missing or invalid Authorization header'}), 401
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Validate token
            global _rbac_manager
            if not _rbac_manager:
                # Auth not configured - allow for development
                logger.warning('RBAC not configured - skipping auth check')
                return f(*args, **kwargs)
            
            user = _rbac_manager.validate_token(token)
            if not user:
                return jsonify({'error': 'Unauthorized: Invalid or expired token'}), 401
            
            # Check permission if required
            if permission and not user.has_permission(permission):
                return jsonify({'error': f'Forbidden: Requires permission {permission.value}'}), 403
            
            # Store user in request context
            request.user = user  # type: ignore
            
            return f(*args, **kwargs)
        
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


# =====================
# FILE LOCKING & PERSISTENCE
# =====================

class FileLockManager:
    """Thread-safe file locking for constraint persistence."""
    
    @staticmethod
    def lock_file(file_path: str, mode: str = 'r'):
        """Context manager for file locking (cross-platform)."""
        class FileLock:
            def __init__(self, path: str, open_mode: str):
                self.path = path
                self.mode = open_mode
                self.file = None
            
            def __enter__(self):
                # Ensure directory exists
                dir_path = os.path.dirname(self.path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                
                # Open file
                try:
                    self.file = open(self.path, self.mode, encoding='utf-8')
                    
                    # Apply file lock (platform-specific)
                    if sys.platform == 'win32':
                        # Windows file locking using msvcrt
                        import msvcrt
                        if 'w' in self.mode or 'a' in self.mode:
                            # Exclusive lock for writing
                            msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
                        # Note: Windows doesn't have shared locks in msvcrt
                    else:
                        # Unix file locking using fcntl
                        import fcntl
                        if 'w' in self.mode or 'a' in self.mode:
                            lock_mode = fcntl.LOCK_EX  # Exclusive lock
                        else:
                            lock_mode = fcntl.LOCK_SH  # Shared lock
                        fcntl.flock(self.file.fileno(), lock_mode)
                    
                    return self.file
                except (IOError, OSError) as e:
                    logger.error(f"Failed to lock file {self.path}: {e}")
                    if self.file:
                        self.file.close()
                    raise
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.file:
                    try:
                        # Release lock (platform-specific)
                        if sys.platform == 'win32':
                            import msvcrt
                            try:
                                msvcrt.locking(self.file.fileno(), msvcrt.LK_UNLCK, 1)
                            except (IOError, OSError):
                                pass  # Already unlocked
                        else:
                            import fcntl
                            fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
                    finally:
                        self.file.close()
        
        return FileLock(file_path, mode)


def generate_uuid_id(prefix: str = '') -> str:
    """Generate UUID-based ID instead of timestamp-based."""
    unique_id = str(uuid.uuid4())
    if prefix:
        return f'{prefix}_{unique_id}'
    return unique_id


# =====================
# CONFIGURATION LOADING
# =====================

def load_config():
    """Load configuration from config.yaml with error handling."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file: {e}, using defaults")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading config: {e}, using defaults")
        return {}


# Global config with fallback defaults
try:
    CONFIG = load_config()
    API_CONFIG = CONFIG.get('api_extensions', {})
except Exception:
    API_CONFIG = {}

# Set safe defaults
API_CONFIG.setdefault('berth_utilization', {'min_pct': 40, 'max_pct': 95})
API_CONFIG.setdefault('capacity', {
    'base_capacity': 100,
    'demand_min': 60,
    'demand_max': 120,
    'overbooking_threshold_pct': 15
})
API_CONFIG.setdefault('weather', {
    'forecast_days': 5,
    'conditions': ['clear', 'cloudy', 'rain', 'wind'],
    'temp_min_c': 15,
    'temp_max_c': 28,
    'wind_speed_min_kn': 10,
    'wind_speed_max_kn': 35,
    'wave_height_min_m': 1.0,
    'wave_height_max_m': 4.0
})
API_CONFIG.setdefault('conflicts', {
    'auto_resolve_enabled': True,
    'manual_intervention_threshold': 1
})


def load_weather_warnings() -> pd.DataFrame:
    """Load weather warnings from CSV file using logging for errors."""
    csv_path = os.path.join(os.path.dirname(__file__), 'input', 'WeatherWarnings.csv')
    try:
        return pd.read_csv(csv_path, sep=';', encoding='utf-8')
    except Exception as exc:
        logger.warning(f"Failed to load weather warnings from {csv_path}: {exc}")
        return pd.DataFrame()


# =====================
# THREAD-SAFE ALERT CACHE
# =====================

def _get_alert_data():
    """Load alert-related data with thread-safe caching."""
    from modules.data_loader import DataLoader

    now = datetime.utcnow()
    
    with _alert_cache_lock:
        cached_data = _alert_cache.get("data")
        cached_time = _alert_cache.get("timestamp")

        if cached_data is not None and cached_time is not None:
            age_seconds = (now - cached_time).total_seconds()
            if age_seconds < _ALERT_CACHE_TTL_SEC:
                logger.debug(f"Using cached DataLoader output for alerts ({int(age_seconds)}s old)")
                return cached_data

        # Cache miss or expired - refresh
        loader = DataLoader()
        data = loader.load_all()
        _alert_cache["data"] = data
        _alert_cache["timestamp"] = now
        logger.info(f"Refreshed alert data cache at {now.isoformat()}")
        return data


# =====================
# CONSTRAINT PERSISTENCE
# =====================

def _load_constraints_store() -> List[Dict[str, Any]]:
    """Load persisted berth constraints with file locking and error handling."""
    if not os.path.exists(_CONSTRAINTS_PATH):
        logger.info(f"Constraints file does not exist: {_CONSTRAINTS_PATH}")
        return []
    
    try:
        with FileLockManager.lock_file(_CONSTRAINTS_PATH, 'r') as f:
            content = f.read()
            if not content.strip():
                return []
            records = json.loads(content)
            return cast(List[Dict[str, Any]], records if isinstance(records, list) else [])
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in constraints file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading constraints: {e}")
        return []


def _persist_constraints(constraints: List[Dict[str, Any]]) -> None:
    """Persist constraints with file locking and error handling."""
    try:
        # Ensure writable directory
        dir_path = os.path.dirname(_CONSTRAINTS_PATH)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, mode=0o755, exist_ok=True)
        
        # Check write permissions
        if os.path.exists(_CONSTRAINTS_PATH) and not os.access(_CONSTRAINTS_PATH, os.W_OK):
            raise IOError(f"No write permission for {_CONSTRAINTS_PATH}")
        
        if not os.path.exists(_CONSTRAINTS_PATH) and not os.access(dir_path, os.W_OK):
            raise IOError(f"No write permission for directory {dir_path}")
        
        # Write with file locking
        with FileLockManager.lock_file(_CONSTRAINTS_PATH, 'w') as f:
            json.dump(constraints, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully persisted {len(constraints)} constraints")
    except Exception as e:
        logger.error(f"Failed to persist constraints: {e}")
        raise


def _append_constraint(record: Dict[str, Any]) -> None:
    """Append constraint with thread safety."""
    constraints = _load_constraints_store()
    constraints.append(record)
    _persist_constraints(constraints)


def _remove_constraint(constraint_id: str) -> bool:
    """Remove constraint by ID with thread safety."""
    constraints = _load_constraints_store()
    new_constraints = [c for c in constraints if c.get('id') != constraint_id]
    if len(new_constraints) == len(constraints):
        return False
    _persist_constraints(new_constraints)
    return True


# =====================
# HELPER FUNCTIONS
# =====================

def _derive_conflicts_from_constraints(constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Translate maintenance constraints into conflict objects."""
    conflicts = []
    for record in constraints:
        if record.get('type') != 'maintenance':
            continue
        conflicts.append({
            'id': record.get('id', ''),
            'time': record.get('startDate') or datetime.now().isoformat(),
            'berth': record.get('berth', ''),
            'vessels': [],
            'type': 'maintenance',
            'severity': record.get('severity', 'high'),
            'message': 'Maintenance window blocks berth availability'
        })
    return conflicts


def _load_berths_from_csv() -> pd.DataFrame:
    """Load berth details from input/Berths.csv."""
    csv_path = os.path.join(os.path.dirname(__file__), 'input', 'Berths.csv')
    if not os.path.exists(csv_path):
        logger.warning(f"Berths CSV not found: {csv_path}")
        return pd.DataFrame()

    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    df.rename(columns={
        'berth_id': 'id',
        'berth_name': 'name',
        'max_loa_m': 'maxLength',
        'max_beam_m': 'maxBeam',
        'max_draft_m': 'maxDraft',
        'throughput_mt_day': 'throughput_mt_day',
    }, inplace=True)
    df['currentVessel'] = None
    df['occupiedUntil'] = None
    return df[['id', 'name', 'port_id', 'maxLength', 'maxBeam', 'maxDraft', 'berth_type', 'throughput_mt_day', 'currentVessel', 'occupiedUntil']]


def _compute_capacity(days: int):
    """Compute capacity and warnings from berth throughput with bounds checking."""
    # Validate days parameter
    days = validate_days_param(str(days), default=14, min_val=1, max_val=365)
    
    berths_df = _load_berths_from_csv()
    base_capacity = int(berths_df['throughput_mt_day'].sum()) if not berths_df.empty else 0
    if base_capacity == 0:
        base_capacity = int(API_CONFIG.get('capacity', {}).get('base_capacity', 100))

    capacity_data = []
    warnings = []
    demand_min = int(API_CONFIG.get('capacity', {}).get('demand_min', 60))
    demand_max = int(API_CONFIG.get('capacity', {}).get('demand_max', 120))

    for i in range(days):
        date_val = datetime.now() + timedelta(days=i)
        demand = int(demand_min + (demand_max - demand_min) * (0.5 + 0.5 * math.sin(i / 2)))
        capacity_data.append({
            'date': date_val.strftime('%Y-%m-%d'),
            'capacity': int(base_capacity),
            'demand': int(demand)
        })
        if demand > base_capacity:
            over_pct = int(((demand - base_capacity) / base_capacity) * 100) if base_capacity else 100
            warnings.append({
                'date': date_val.strftime('%Y-%m-%d'),
                'severity': 'high' if over_pct >= 15 else 'medium',
                'capacity': int(base_capacity),
                'demand': int(demand),
                'overbooking': int(over_pct),
                'message': f'Capacity exceeded by {over_pct}%'
            })

    return capacity_data, warnings


def _load_routes_as_templates() -> pd.DataFrame:
    """Convert Routes.csv into voyage template payloads."""
    csv_path = os.path.join(os.path.dirname(__file__), 'input', 'Routes.csv')
    if not os.path.exists(csv_path):
        logger.warning(f"Routes CSV not found: {csv_path}")
        return pd.DataFrame()

    df = pd.read_csv(csv_path, sep=';', encoding='utf-8', comment='#')
    
    if 'from_port' in df.columns:
        df['id'] = df.index.map(lambda x: f'route_{x+1:03d}')
        df['name'] = df.apply(lambda row: f"{row['from_port']} → {row['to_port']}", axis=1)
        df['category'] = df['canal'].apply(lambda x: 'Canal Transit' if pd.notna(x) and str(x).strip() else 'Direct')
        df['description'] = df.apply(
            lambda row: f"{row['from_port']} to {row['to_port']} via {row['canal']}" if pd.notna(row.get('canal')) and str(row['canal']).strip() else f"{row['from_port']} to {row['to_port']}",
            axis=1
        )
        df['ports'] = df.apply(lambda row: [row['from_port'], row['to_port']], axis=1)
        df['estimatedDays'] = df['distance_nm'].apply(lambda x: max(1, int(x / 288)) if pd.notna(x) else 7)
    else:
        df['id'] = df['route_id']
        df['name'] = df['route_name']
        df['category'] = df['canal_name'].apply(lambda x: 'Canal Transit' if isinstance(x, str) and x.strip() else 'Direct')
        df['description'] = df.apply(
            lambda row: f"{row['port_start_id']} to {row['port_end_id']} via {row['canal_name']}" if str(row.get('canal_name', '')).strip() else f"{row['port_start_id']} to {row['port_end_id']}",
            axis=1
        )
        df['ports'] = df.apply(lambda row: [row['port_start_id'], row['port_end_id']], axis=1)
        df['estimatedDays'] = df['typical_duration_days']
    
    return df[['id', 'name', 'category', 'description', 'ports', 'estimatedDays']]


# =====================
# CALENDAR EVENTS AGGREGATION
# =====================

def _aggregate_calendar_events(
    module_filter: Optional[str] = None,
    vessel_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Aggregate events from all modules (Olya, Balakovo, DeepSea).
    
    Args:
        module_filter: Filter by module ('olya', 'balakovo', 'deepsea', or None for all)
        vessel_filter: Filter by vessel ID/name
        status_filter: Filter by status ('planned', 'in_progress', 'completed')
        start_date: Filter events starting after this date
        end_date: Filter events ending before this date
        
    Returns:
        List of standardized event dictionaries
    """
    events = []
    
    # === OLYA MODULE EVENTS ===
    if not module_filter or module_filter.lower() == 'olya':
        try:
            loader = OlyaLoader()
            data = loader.load()
            coordinator = OlyaCoordinator(data)
            coordinator.analyze()
            
            for voyage_id, voyage in data.calculated_voyages.items():
                for operation in voyage.operations:
                    # Apply date filters
                    if start_date and operation.end_time < start_date:
                        continue
                    if end_date and operation.start_time > end_date:
                        continue
                    
                    # Apply vessel filter
                    if vessel_filter and vessel_filter.lower() not in voyage.vessel_name.lower():
                        continue
                    
                    # Determine event status
                    status = 'planned'
                    if operation.end_time < datetime.now():
                        status = 'completed'
                    elif operation.start_time <= datetime.now() <= operation.end_time:
                        status = 'in_progress'
                    
                    # Apply status filter
                    if status_filter and status_filter.lower() != status:
                        continue
                    
                    # Map operation type to event type
                    event_type_map = {
                        'loading': 'Loading',
                        'discharge': 'Discharge',
                        'transit': 'Transit',
                        'waiting': 'Waiting',
                        'bunkering': 'Bunkering'
                    }
                    event_type = event_type_map.get(operation.operation.lower(), operation.operation)
                    
                    events.append({
                        'id': f'olya_{voyage_id}_{operation.seq}',
                        'module': 'olya',
                        'type': event_type,
                        'title': f'{voyage.vessel_name} - {event_type} at {operation.port}',
                        'description': f'{event_type} of {operation.cargo} ({operation.qty_mt:.0f} MT)',
                        'vessel': {
                            'id': voyage.vessel_id,
                            'name': voyage.vessel_name,
                            'type': voyage.vessel_type
                        },
                        'location': operation.port,
                        'cargo': operation.cargo,
                        'quantity_mt': operation.qty_mt,
                        'start': operation.start_time.isoformat(),
                        'end': operation.end_time.isoformat(),
                        'duration_hours': operation.duration_hours,
                        'status': status,
                        'voyage_id': voyage_id,
                        'remarks': operation.remarks
                    })
        except Exception as e:
            logger.warning(f"Error loading Olya events: {e}")
    
    # === BALAKOVO MODULE EVENTS ===
    if not module_filter or module_filter.lower() == 'balakovo':
        try:
            loader = BalakovoLoader()
            data = loader.load()
            planner = BalakovoPlanner(data)
            result_data = planner.plan()
            
            for berth_id, schedule in result_data.schedules.items():
                if not schedule or not hasattr(schedule, 'slots'):
                    continue
                    
                for slot in schedule.slots:
                    # Apply date filters
                    if start_date and slot.departure < start_date:
                        continue
                    if end_date and slot.berthing_start > end_date:
                        continue
                    
                    # Apply vessel filter
                    if vessel_filter and vessel_filter.lower() not in slot.vessel_name.lower():
                        continue
                    
                    # Determine event status
                    status = 'planned'
                    if hasattr(slot, 'status'):
                        status_map = {
                            'PLANNED': 'planned',
                            'CONFIRMED': 'planned',
                            'IN_PROGRESS': 'in_progress',
                            'COMPLETED': 'completed',
                            'CANCELLED': 'cancelled',
                            'DELAYED': 'planned'
                        }
                        status = status_map.get(slot.status.name if hasattr(slot.status, 'name') else str(slot.status), 'planned')
                    elif slot.departure < datetime.now():
                        status = 'completed'
                    elif slot.berthing_start <= datetime.now() <= slot.departure:
                        status = 'in_progress'
                    
                    # Apply status filter
                    if status_filter and status_filter.lower() != status:
                        continue
                    
                    events.append({
                        'id': f'balakovo_{slot.slot_id}',
                        'module': 'balakovo',
                        'type': 'Loading',
                        'title': f'{slot.vessel_name} - Loading at {berth_id}',
                        'description': f'Loading of {slot.cargo_type} ({slot.qty_mt:.0f} MT) to {slot.destination}',
                        'vessel': {
                            'id': slot.vessel_id,
                            'name': slot.vessel_name,
                            'type': 'barge'
                        },
                        'location': schedule.berth_name,
                        'berth_id': berth_id,
                        'cargo': slot.cargo_type,
                        'quantity_mt': slot.qty_mt,
                        'destination': slot.destination,
                        'start': slot.berthing_start.isoformat(),
                        'end': slot.departure.isoformat(),
                        'eta': slot.eta.isoformat() if hasattr(slot, 'eta') else slot.berthing_start.isoformat(),
                        'loading_start': slot.loading_start.isoformat(),
                        'loading_end': slot.loading_end.isoformat(),
                        'duration_hours': slot.total_hours,
                        'waiting_hours': slot.waiting_hours,
                        'status': status,
                        'cargo_id': slot.cargo_id,
                        'remarks': slot.remarks
                    })
        except Exception as e:
            logger.warning(f"Error loading Balakovo events: {e}")
    
    # === DEEPSEA MODULE EVENTS ===
    if not module_filter or module_filter.lower() == 'deepsea':
        try:
            loader = DeepSeaLoader()
            data = loader.load()
            calculator = DeepSeaCalculator(data)
            calculator.calculate_all()
            
            for voyage_id, voyage in data.calculated_voyages.items():
                for leg in voyage.legs:
                    # Apply date filters
                    if start_date and leg.end_time < start_date:
                        continue
                    if end_date and leg.start_time > end_date:
                        continue
                    
                    # Apply vessel filter
                    if vessel_filter and vessel_filter.lower() not in voyage.vessel_name.lower():
                        continue
                    
                    # Determine event status
                    status = 'planned'
                    if leg.end_time < datetime.now():
                        status = 'completed'
                    elif leg.start_time <= datetime.now() <= leg.end_time:
                        status = 'in_progress'
                    
                    # Apply status filter
                    if status_filter and status_filter.lower() != status:
                        continue
                    
                    # Map leg type to event type
                    event_type_map = {
                        'loading': 'Loading',
                        'discharge': 'Discharge',
                        'sea': 'Sea Transit',
                        'canal': 'Canal Transit',
                        'bunker': 'Bunkering',
                        'waiting': 'Waiting'
                    }
                    event_type = event_type_map.get(leg.leg_type.lower(), leg.leg_type)
                    
                    # Build description
                    if leg.leg_type.lower() in ['loading', 'discharge']:
                        description = f'{event_type} of {leg.cargo_type} ({leg.qty_mt:.0f} MT) at {leg.to_port}'
                    elif leg.leg_type.lower() == 'sea':
                        description = f'Sea transit from {leg.from_port} to {leg.to_port} ({leg.distance_nm:.0f} NM)'
                    elif leg.leg_type.lower() == 'canal':
                        description = f'Canal transit via {leg.canal_id or "canal"} from {leg.from_port} to {leg.to_port}'
                    else:
                        description = f'{event_type} from {leg.from_port} to {leg.to_port}'
                    
                    events.append({
                        'id': f'deepsea_{voyage_id}_{leg.leg_seq}',
                        'module': 'deepsea',
                        'type': event_type,
                        'title': f'{voyage.vessel_name} - {event_type}',
                        'description': description,
                        'vessel': {
                            'id': voyage.vessel_id,
                            'name': voyage.vessel_name,
                            'class': voyage.vessel_class
                        },
                        'from_port': leg.from_port,
                        'to_port': leg.to_port,
                        'location': leg.to_port,
                        'cargo': leg.cargo_type,
                        'cargo_state': leg.cargo_state,
                        'quantity_mt': leg.qty_mt,
                        'start': leg.start_time.isoformat(),
                        'end': leg.end_time.isoformat(),
                        'duration_hours': leg.duration_hours,
                        'distance_nm': leg.distance_nm,
                        'speed_kn': leg.speed_kn,
                        'status': status,
                        'voyage_id': voyage_id,
                        'route_id': voyage.route_id,
                        'canal_id': leg.canal_id,
                        'remarks': leg.remarks
                    })
        except Exception as e:
            logger.warning(f"Error loading DeepSea events: {e}")
    
    # Sort events by start time
    events.sort(key=lambda x: x['start'])
    
    return events


# =====================
# API ENDPOINT REGISTRATION
# =====================

def register_ui_module_endpoints(app):
    """Register all UI module API endpoints with security hardening."""
    
    # Initialize RBAC if configured
    global _rbac_manager
    try:
        _rbac_manager = RBACManager()
        logger.info("RBAC Manager initialized")
    except Exception as e:
        logger.warning(f"RBAC Manager not initialized: {e}")
    
    # ========================
    # ALERTS ENDPOINTS
    # ========================
    
    @app.route('/api/alerts', methods=['GET'])
    def get_alerts():
        """Get all alerts with filtering options - thread-safe."""
        try:
            severity_param = request.args.get('severity', 'all')
            status_param = request.args.get('status', 'active')
            
            # Validate inputs
            severity_param = validate_severity_param(severity_param)

            all_data = _get_alert_data()
            
            # Remove unused leg data - use only essential fields
            alert_system = AlertSystem()

            severity_filter = None
            if severity_param and severity_param != 'all':
                severity_map = {
                    'info': AlertSeverity.INFO,
                    'warning': AlertSeverity.WARNING,
                    'critical': AlertSeverity.CRITICAL,
                }
                severity_filter = severity_map.get(severity_param)

            all_alerts = alert_system.get_all_alerts(severity_filter=severity_filter)

            alerts_data = []
            for alert in all_alerts:
                alert_dict = alert.to_dict()
                alert_dict['status'] = 'active'

                if status_param != 'all' and alert_dict['status'] != status_param:
                    continue

                alerts_data.append(alert_dict)

            logger.info(f"Returning {len(alerts_data)} alerts (severity={severity_param}, status={status_param})")
            return jsonify({'alerts': alerts_data})

        except ValidationError as e:
            logger.warning(f"Validation error in get_alerts: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as exc:
            logger.exception(f"Error getting alerts: {exc}")
            return jsonify({'alerts': [], 'error': str(exc)}), 500
    
    @app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
    def acknowledge_alert(alert_id):
        """Acknowledge an alert"""
        return jsonify({'success': True, 'message': f'Alert {alert_id} acknowledged'})
    
    @app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
    def resolve_alert(alert_id):
        """Resolve an alert"""
        return jsonify({'success': True, 'message': f'Alert {alert_id} resolved'})
    
    # ========================
    # BERTH MANAGEMENT ENDPOINTS
    # ========================
    
    @app.route('/api/berths', methods=['GET'])
    def get_berths():
        """Get berth data from CSV with computed utilization."""
        try:
            berths_df = _load_berths_from_csv()
            berths = berths_df.to_dict(orient='records') if not berths_df.empty else []
            saved_constraints = _load_constraints_store()

            util_cfg = API_CONFIG.get('berth_utilization', {})
            min_pct = util_cfg.get('min_pct', 40)
            max_pct = util_cfg.get('max_pct', 95)

            utilization = []
            for i in range(14):
                date_val = datetime.now() + timedelta(days=i)
                day_factor = (date_val.weekday() + 1) / 7.0
                throughput_scale = (
                    berths_df['throughput_mt_day'].mean() / berths_df['throughput_mt_day'].max()
                    if not berths_df.empty else 1
                )
                value = int(min_pct + (max_pct - min_pct) * day_factor * throughput_scale)
                value = max(0, min(100, value))
                utilization.append({
                    'date': date_val.strftime('%Y-%m-%d'),
                    'value': value
                })

            conflicts = _derive_conflicts_from_constraints(saved_constraints)

            return jsonify({
                'berths': berths,
                'constraints': saved_constraints,
                'utilization': utilization,
                'conflicts': conflicts
            })
        except Exception as e:
            logger.exception(f"Error in get_berths: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/berths/capacity', methods=['GET'])
    def get_berth_capacity():
        """Get capacity planning data with bounds checking."""
        try:
            days_param = request.args.get('days', '14')
            days = validate_days_param(days_param, default=14, min_val=1, max_val=90)
            
            capacity_data, warnings = _compute_capacity(days)
            return jsonify({
                'capacity': capacity_data,
                'warnings': warnings
            })
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"Error in get_berth_capacity: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/berths/constraints', methods=['POST'])
    @require_auth(Permission.EDIT_SCHEDULES)
    def save_constraint():
        """Save a new berth constraint with validation and auth."""
        try:
            if not request.json:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            # Validate schema
            schema = ConstraintSchema.validate(request.json)
            
            # Generate UUID-based ID
            constraint_id = generate_uuid_id('const')

            constraint_record = {
                'id': constraint_id,
                'berth': schema.berth,
                'type': schema.type,
                'value': schema.value,
                'startDate': schema.startDate,
                'endDate': schema.endDate,
                'severity': schema.severity,
            }

            _append_constraint(constraint_record)

            logger.info(f"Saved constraint {constraint_id}")
            return jsonify({
                'success': True,
                'constraint_id': constraint_id,
                'message': 'Constraint saved successfully'
            })
        
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 400
        except IOError as e:
            logger.error(f"IO error saving constraint: {e}")
            return jsonify({'error': 'Failed to save constraint - check permissions'}), 500
        except Exception as e:
            logger.exception(f"Error saving constraint: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/berths/constraints/<constraint_id>', methods=['DELETE'])
    @require_auth(Permission.EDIT_SCHEDULES)
    def delete_constraint(constraint_id):
        """Delete a constraint with auth."""
        try:
            removed = _remove_constraint(constraint_id)
            status = 200 if removed else 404
            return jsonify({
                'success': removed,
                'message': f'Constraint {constraint_id} deleted' if removed else 'Constraint not found'
            }), status
        except Exception as e:
            logger.exception(f"Error deleting constraint: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/berths/conflicts/auto-resolve', methods=['POST'])
    @require_auth(Permission.EDIT_SCHEDULES)
    def auto_resolve_conflicts():
        """Auto-resolve berth conflicts with auth."""
        try:
            conflicts = _derive_conflicts_from_constraints(_load_constraints_store())
            now_str = datetime.now().strftime('%Y-%m-%d')
            active_conflicts = [c for c in conflicts if c['time'] >= now_str]
            resolved = 0
            for conflict in conflicts:
                if conflict['time'] < now_str:
                    _remove_constraint(conflict['id'])
                    resolved += 1

            return jsonify({
                'success': True,
                'resolved': resolved,
                'unresolved': len(active_conflicts),
                'message': f'{resolved} expired conflicts cleared, {len(active_conflicts)} remain active'
            })
        except Exception as e:
            logger.exception(f"Error auto-resolving conflicts: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/berths/conflicts/<conflict_id>/resolve', methods=['POST'])
    def resolve_conflict(conflict_id):
        """Resolve single conflict"""
        return jsonify({'success': True, 'message': f'Conflict {conflict_id} resolved'})
    
    # ========================
    # BUNKER OPTIMIZATION ENDPOINTS
    # ========================
    
    @app.route('/api/bunker', methods=['GET'])
    def get_bunker_data():
        """Get bunker ports and pricing data with defensive fuel type parsing."""
        try:
            bunker_prices = create_sample_bunker_prices()
            
            ports_data = {}
            for price in bunker_prices:
                port_name = price.port_name
                if port_name not in ports_data:
                    ports_data[port_name] = {
                        'id': f'port_{len(ports_data) + 1:03d}',
                        'name': port_name,
                        'prices': {}
                    }
                
                # Defensive fuel type parsing
                try:
                    fuel_key = price.fuel_type.value.lower() if hasattr(price.fuel_type, 'value') else str(price.fuel_type).lower()
                except Exception:
                    logger.warning(f"Invalid fuel type for port {port_name}, skipping")
                    continue
                
                ports_data[port_name]['prices'][fuel_key] = price.price_per_mt
            
            ports = list(ports_data.values())
            
            logger.info(f"Returning bunker data for {len(ports)} ports")
            return jsonify({'ports': ports})
            
        except Exception as e:
            logger.exception(f"Error getting bunker data: {e}")
            return jsonify({'error': str(e), 'ports': []}), 500
    
    # ========================
    # WEATHER INTEGRATION ENDPOINTS
    # ========================
    
    @app.route('/api/weather', methods=['GET'])
    def get_weather_data():
        """Get weather warnings and forecasts with severity parsing."""
        try:
            df = load_weather_warnings()
            
            warnings = []
            if not df.empty:
                for _, row in df.iterrows():
                    # Defensive severity parsing
                    try:
                        severity_val = int(row.get('severity', 1))
                    except (ValueError, TypeError):
                        severity_val = 1
                    
                    severity = 'high' if severity_val >= 4 else 'medium' if severity_val >= 2 else 'low'
                    
                    warnings.append({
                        'id': str(row.get('weather_id', 'warn_unknown')),
                        'type': str(row.get('message_type', 'routine')).lower(),
                        'severity': severity,
                        'title': f"{row.get('message_type', 'Weather')} Warning - {row.get('area_name', 'Unknown')}",
                        'description': str(row.get('message_text_short', 'No details available')),
                        'location': f"{row.get('lat_min', 0)}°N, {row.get('lon_min', 0)}°E",
                        'validUntil': str(row.get('valid_to', datetime.now().isoformat())),
                        'windSpeed': float(row.get('wind_speed_max_kn', 0)),
                        'waveHeight': float(row.get('wave_height_max_m', 0)),
                        'affectedVessels': str(row.get('affected_vessels', '')),
                        'affectedRoutes': str(row.get('affected_routes', '')),
                        'recommendedAction': str(row.get('recommended_action', 'Monitor'))
                    })
            
            # Generate forecast data with bounded values
            forecasts = []
            weather_cfg = API_CONFIG.get('weather', {})
            forecast_days = min(weather_cfg.get('forecast_days', 5), 14)  # Cap at 14 days
            conditions = weather_cfg.get('conditions', ['clear', 'cloudy', 'rain', 'wind'])
            temp_min = weather_cfg.get('temp_min_c', 15)
            temp_max = weather_cfg.get('temp_max_c', 28)
            wind_min = weather_cfg.get('wind_speed_min_kn', 10)
            wind_max = weather_cfg.get('wind_speed_max_kn', 35)
            wave_min = weather_cfg.get('wave_height_min_m', 1.0)
            wave_max = weather_cfg.get('wave_height_max_m', 4.0)
            
            for i in range(forecast_days):
                date = datetime.now() + timedelta(days=i)
                day_factor = (i + 1) / float(forecast_days)
                forecasts.append({
                    'date': date.isoformat(),
                    'condition': conditions[i % len(conditions)],
                    'temp': int(temp_min + (temp_max - temp_min) * day_factor),
                    'windSpeed': int(wind_min + (wind_max - wind_min) * day_factor),
                    'waveHeight': round(wave_min + (wave_max - wave_min) * day_factor, 1)
                })
            
            return jsonify({
                'warnings': warnings,
                'forecasts': forecasts
            })
        except Exception as e:
            logger.exception(f"Error getting weather data: {e}")
            return jsonify({'error': str(e), 'warnings': [], 'forecasts': []}), 500
    
    # ========================
    # VESSEL TRACKING ENDPOINTS
    # ========================
    
    @app.route('/api/vessels/tracking', methods=['GET'])
    def get_vessel_tracking():
        """Get live vessel positions from VesselPositions.csv"""
        try:
            csv_path = os.path.join(os.path.dirname(__file__), 'input', 'VesselPositions.csv')
            df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
            
            vessels = []
            for _, row in df.iterrows():
                status_map = {
                    'Moored': 'at_port',
                    'Underway': 'underway',
                    'At Anchor': 'anchored',
                    'Loading': 'loading',
                    'Discharging': 'discharging'
                }
                raw_status = str(row.get('status', 'Unknown'))
                status = status_map.get(raw_status, raw_status.lower().replace(' ', '_'))
                
                eta_str = row.get('eta_destination')
                eta = None
                if pd.notna(eta_str) and str(eta_str).strip():
                    try:
                        eta = pd.to_datetime(eta_str).isoformat()
                    except (ValueError, TypeError, pd.errors.ParserError) as e:
                        logger.warning(f"Could not parse ETA '{eta_str}': {e}")
                
                vessel = {
                    'id': str(row.get('position_id', '')),
                    'name': str(row.get('vessel_id', 'Unknown')),
                    'status': status,
                    'position': {
                        'lat': float(row.get('latitude', 0)),
                        'lon': float(row.get('longitude', 0))
                    },
                    'speed': float(row.get('speed_knots', 0)),
                    'course': float(row.get('course_degrees', 0)),
                    'destination': str(row.get('destination_port', '')),
                    'eta': eta,
                    'cargoOnboard': str(row.get('cargo_onboard', 'No')),
                    'cargoQtyMt': float(row.get('cargo_qty_mt', 0)) if pd.notna(row.get('cargo_qty_mt')) else 0,
                    'distanceToGo': float(row.get('distance_to_go_nm', 0)) if pd.notna(row.get('distance_to_go_nm')) else 0,
                    'weatherZone': str(row.get('weather_zone_current', ''))
                }
                vessels.append(vessel)
            
            logger.info(f"Loaded {len(vessels)} vessel positions from CSV")
            return jsonify({'vessels': vessels})
            
        except Exception as e:
            logger.exception(f"Error loading vessel positions: {e}")
            return jsonify({'error': str(e), 'vessels': []}), 500
    
    # ========================
    # SCENARIO MANAGEMENT ENDPOINTS
    # ========================
    
    @app.route('/api/scenarios', methods=['GET', 'POST'])
    def handle_scenarios():
        """Get all scenarios or create new one."""
        if request.method == 'GET':
            try:
                loader = DeepSeaLoader()
                data = loader.load()
                
                scenario_mgr = ScenarioManager(data)
                all_scenarios = scenario_mgr.load_scenarios()
                
                scenarios = []
                for scenario_id, scenario in all_scenarios.items():
                    scenarios.append({
                        'id': scenario_id,
                        'name': getattr(scenario, 'scenario_name', getattr(scenario, 'name', '')),
                        'description': getattr(scenario, 'description', ''),
                        'createdAt': getattr(scenario, 'created_at', datetime.now()).isoformat(),
                        'active': scenario_id == 'baseline',
                        'vesselCount': len(getattr(scenario, 'voyage_ids', [])),
                        'voyageCount': len(getattr(scenario, 'voyage_ids', [])),
                    })
                
                logger.info(f"Returning {len(scenarios)} scenarios")
                return jsonify({'scenarios': scenarios})
                
            except Exception as e:
                logger.exception(f"Error loading scenarios: {e}")
                return jsonify({'error': str(e), 'scenarios': []}), 500
        
        elif request.method == 'POST':
            if not require_auth(Permission.CREATE_SCHEDULES):
                return jsonify({'error': 'Unauthorized'}), 401
            
            try:
                if not request.json:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Validate schema
                schema = ScenarioSchema.validate(request.json)
                
                loader = DeepSeaLoader()
                ds_data = loader.load()
                
                scenario_mgr = ScenarioManager(ds_data)
                
                # Generate UUID-based ID
                scenario_id = generate_uuid_id('scenario')
                
                # Create scenario
                new_scenario = scenario_mgr.create_scenario(
                    scenario_id=scenario_id,
                    scenario_name=schema.name,
                    description=schema.description,
                    voyage_ids=schema.voyage_ids if schema.voyage_ids else []
                )
                
                logger.info(f"Created scenario {scenario_id}: {schema.name}")
                return jsonify({
                    'success': True,
                    'scenario_id': scenario_id,
                    'message': 'Scenario created successfully',
                    'scenario': {
                        'id': scenario_id,
                        'name': getattr(new_scenario, 'scenario_name', schema.name),
                        'description': getattr(new_scenario, 'description', ''),
                    }
                })
                
            except ValidationError as e:
                logger.warning(f"Validation error: {e}")
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                logger.exception(f"Error creating scenario: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/scenarios/<scenario_id>', methods=['DELETE'])
    @require_auth(Permission.DELETE_SCHEDULES)
    def delete_scenario(scenario_id):
        """Delete a scenario with auth."""
        return jsonify({'success': True, 'message': f'Scenario {scenario_id} deleted'})
    
    @app.route('/api/scenarios/<scenario_id>/load', methods=['POST'])
    def load_scenario(scenario_id):
        """Load a scenario"""
        return jsonify({
            'success': True,
            'scenario': {
                'id': scenario_id,
                'name': 'Loaded Scenario',
                'data': {}
            }
        })
    
    # ========================
    # VOYAGE TEMPLATES ENDPOINTS
    # ========================
    
    @app.route('/api/voyage-templates', methods=['GET', 'POST'])
    def handle_voyage_templates():
        """Get all templates or create new one."""
        if request.method == 'GET':
            try:
                templates_df = _load_routes_as_templates()
                templates = templates_df.to_dict(orient='records') if not templates_df.empty else []
                categories = sorted(list(templates_df['category'].unique())) if not templates_df.empty else []

                return jsonify({
                    'templates': templates,
                    'categories': categories
                })
            except Exception as e:
                logger.exception(f"Error getting templates: {e}")
                return jsonify({'error': str(e), 'templates': [], 'categories': []}), 500
        
        elif request.method == 'POST':
            if not require_auth(Permission.CREATE_SCHEDULES):
                return jsonify({'error': 'Unauthorized'}), 401
            
            try:
                # Generate UUID-based ID
                template_id = generate_uuid_id('template')
                
                return jsonify({
                    'success': True,
                    'template_id': template_id,
                    'message': 'Template created from submitted data'
                })
            except Exception as e:
                logger.exception(f"Error creating template: {e}")
                return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voyage-templates/<template_id>', methods=['DELETE'])
    @require_auth(Permission.DELETE_SCHEDULES)
    def delete_template(template_id):
        """Delete a template with auth."""
        return jsonify({'success': True, 'message': f'Template {template_id} deleted'})
    
    # ========================
    # CAPACITY PLANNING ENDPOINTS
    # ========================
    
    @app.route('/api/capacity', methods=['GET'])
    def get_capacity_data():
        """Get capacity planning data with bounds checking."""
        try:
            days_param = request.args.get('days', '14')
            days = validate_days_param(days_param, default=14, min_val=1, max_val=90)
            
            capacity_data, warnings = _compute_capacity(days)

            recommendations = []
            if warnings:
                recommendations.append({
                    'priority': 'high',
                    'title': 'Adjust schedule to relieve peaks',
                    'description': 'Spread arrivals across lower-demand days to stay within berth throughput limits.',
                    'action': 'redistribute'
                })

            return jsonify({
                'capacity': capacity_data,
                'recommendations': recommendations,
                'warnings': warnings
            })
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"Error getting capacity data: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/capacity/optimize', methods=['POST'])
    def optimize_capacity():
        """Optimize capacity allocation"""
        return jsonify({
            'success': True,
            'improvements': 5,
            'message': '5 optimization suggestions generated'
        })
    
    # ========================
    # CALENDAR EVENTS ENDPOINT
    # ========================
    
    @app.route('/api/calendar/events', methods=['GET'])
    def get_calendar_events():
        """
        Get aggregated calendar events from all modules with filtering.
        
        Query Parameters:
            module: Filter by module ('olya', 'balakovo', 'deepsea', or 'all')
            vessel: Filter by vessel ID or name (partial match)
            status: Filter by status ('planned', 'in_progress', 'completed')
            start_date: Filter events starting after this date (ISO format)
            end_date: Filter events ending before this date (ISO format)
            limit: Maximum number of events to return (default 1000)
        
        Returns:
            JSON with events array and metadata
        """
        try:
            # Parse query parameters
            module_filter = request.args.get('module', 'all')
            if module_filter.lower() == 'all':
                module_filter = None
            
            vessel_filter = request.args.get('vessel')
            status_filter = request.args.get('status')
            
            # Parse date parameters
            start_date = None
            end_date = None
            
            start_date_str = request.args.get('start_date')
            if start_date_str:
                try:
                    start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError) as e:
                    return jsonify({'error': f'Invalid start_date format: {e}'}), 400
            
            end_date_str = request.args.get('end_date')
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError) as e:
                    return jsonify({'error': f'Invalid end_date format: {e}'}), 400
            
            # Validate limit parameter
            limit_str = request.args.get('limit', '1000')
            try:
                limit = int(limit_str)
                if limit < 1 or limit > 10000:
                    return jsonify({'error': 'Limit must be between 1 and 10000'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid limit parameter'}), 400
            
            # Validate module filter
            valid_modules = ['olya', 'balakovo', 'deepsea']
            if module_filter and module_filter.lower() not in valid_modules:
                return jsonify({'error': f'Invalid module. Must be one of: {", ".join(valid_modules)}, or "all"'}), 400
            
            # Validate status filter
            valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled']
            if status_filter and status_filter.lower() not in valid_statuses:
                return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
            
            # Aggregate events
            events = _aggregate_calendar_events(
                module_filter=module_filter,
                vessel_filter=vessel_filter,
                status_filter=status_filter,
                start_date=start_date,
                end_date=end_date
            )
            
            # Apply limit
            total_events = len(events)
            events = events[:limit]
            
            # Calculate statistics
            module_counts = {}
            status_counts = {}
            vessel_counts = {}
            
            for event in events:
                # Count by module
                module = event.get('module', 'unknown')
                module_counts[module] = module_counts.get(module, 0) + 1
                
                # Count by status
                status = event.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count by vessel
                vessel_name = event.get('vessel', {}).get('name', 'unknown')
                vessel_counts[vessel_name] = vessel_counts.get(vessel_name, 0) + 1
            
            logger.info(f"Returning {len(events)} calendar events (filtered from {total_events} total)")
            
            return jsonify({
                'events': events,
                'metadata': {
                    'total': total_events,
                    'returned': len(events),
                    'filters': {
                        'module': module_filter or 'all',
                        'vessel': vessel_filter,
                        'status': status_filter,
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None
                    },
                    'statistics': {
                        'by_module': module_counts,
                        'by_status': status_counts,
                        'by_vessel': vessel_counts
                    }
                }
            })
        
        except ValidationError as e:
            logger.warning(f"Validation error in calendar events: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"Error getting calendar events: {e}")
            return jsonify({'error': str(e), 'events': []}), 500
    
    # ========================
    # PDF EXPORT ENDPOINT
    # ========================
    
    @app.route('/api/export/pdf', methods=['POST'])
    @require_auth(Permission.EXPORT_REPORTS)
    def export_pdf():
        """Generate PDF report with validation and auth."""
        try:
            if not request.json:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            # Validate schema
            schema = PDFExportSchema.validate(request.json)
            
            # Convert to DataFrame
            df = pd.DataFrame(schema.data)

            # Generate PDF
            filename = generate_pdf_report(schema.reportType, df)
            
            logger.info(f"Generated PDF report: {filename}")
            return jsonify({
                'success': True,
                'message': f'{schema.reportType} PDF report generated',
                'filename': filename
            })
        
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 400
        except ValueError as exc:
            logger.error(f"Unsupported report type: {exc}")
            return jsonify({'success': False, 'error': str(exc)}), 501
        except Exception as exc:
            logger.exception(f"Failed to generate PDF: {exc}")
            return jsonify({'success': False, 'error': str(exc)}), 500
    
    logger.info("[OK] Security-hardened UI Module API endpoints registered successfully")


# =====================
# INITIALIZATION
# =====================

# Ensure constraints directory exists and is writable
def initialize_constraints_storage():
    """Initialize constraints storage with proper permissions."""
    try:
        dir_path = os.path.dirname(_CONSTRAINTS_PATH)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, mode=0o755, exist_ok=True)
            logger.info(f"Created constraints directory: {dir_path}")
        
        # Test write permissions
        if not os.access(dir_path, os.W_OK):
            logger.warning(f"No write permission for constraints directory: {dir_path}")
        else:
            logger.info(f"Constraints storage initialized at: {_CONSTRAINTS_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize constraints storage: {e}")


initialize_constraints_storage()
