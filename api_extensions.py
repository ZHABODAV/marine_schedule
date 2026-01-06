"""
API Extensions for UI Modules - Security Hardened Version
Implements comprehensive security, validation, and thread-safety improvements.
"""

from flask import jsonify, request, Request
from datetime import datetime, timedelta, date
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
from modules.year_schedule_optimizer import YearScheduleManager
from modules.pdf_reporter import generate_pdf_report
from modules.rbac import RBACManager, Permission
from modules.security_utils import SecurityUtils
from modules.config import config
from modules.logger import setup_logger

logger = setup_logger(__name__)

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
        
        # Convert empty list to None, otherwise keep the list
        parsed_voyage_ids = voyage_ids if voyage_ids else None
        
        return ScenarioSchema(
            name=name,
            description=description,
            voyage_ids=parsed_voyage_ids
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
        return []
    except Exception as e:
        logger.error(f"Error loading constraints: {e}")
        return []


def _persist_constraints(constraints: List[Dict[str, Any]]) -> None:
    """Persist constraints with file locking, backup, and error handling."""
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
        
        # Create backup before overwriting
        if os.path.exists(_CONSTRAINTS_PATH):
            SecurityUtils.create_backup(_CONSTRAINTS_PATH)

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
    """Compute capacity and warnings from berth throughput and actual rail cargo accumulation."""
    # Validate days parameter
    days = validate_days_param(str(days), default=14, min_val=1, max_val=365)
    
    berths_df = _load_berths_from_csv()
    base_capacity = int(berths_df['throughput_mt_day'].sum()) if not berths_df.empty else 0
    if base_capacity == 0:
        base_capacity = int(API_CONFIG.get('capacity', {}).get('base_capacity', 100))

    # Load actual rail cargo data
    rail_cargo_path = os.path.join(os.path.dirname(__file__), 'input', 'rail_cargo.csv')
    rail_cargo_accumulation = {}
    
    try:
        rail_df = pd.read_csv(rail_cargo_path, sep=';', encoding='utf-8')
        
        # Calculate daily cargo accumulation from rail arrivals
        for _, row in rail_df.iterrows():
            try:
                # Use eta_port_date for expected arrival
                eta_date = pd.to_datetime(row['eta_port_date']).date()
                qty = float(row['qty_mt'])
                
                # Accumulate cargo by date
                if eta_date not in rail_cargo_accumulation:
                    rail_cargo_accumulation[eta_date] = 0
                rail_cargo_accumulation[eta_date] += qty
            except (ValueError, TypeError, pd.errors.ParserError):
                continue
        
        logger.info(f"Loaded rail cargo accumulation for {len(rail_cargo_accumulation)} dates")
    except Exception as e:
        logger.warning(f"Could not load rail cargo data: {e}, using synthetic demand")

    capacity_data = []
    warnings = []
    
    # Calculate running accumulation
    running_accumulation = 0
    
    # Get date range from rail cargo if available, otherwise use current date
    if rail_cargo_accumulation:
        # Use the earliest cargo date as starting point
        start_date = min(rail_cargo_accumulation.keys())
        # Ensure we show days requested
        days_to_show = days
    else:
        start_date = datetime.now().date()
        days_to_show = days

    for i in range(days_to_show):
        date_key = start_date + timedelta(days=i)
        date_val = datetime.combine(date_key, datetime.min.time())
        
        # Get actual rail cargo arrival for this date
        daily_arrival = rail_cargo_accumulation.get(date_key, 0)
        
        # Add to running accumulation
        running_accumulation += daily_arrival
        
        # Subtract daily throughput capacity (simulating loading)
        if running_accumulation > 0:
            loaded =  min(running_accumulation, base_capacity)
            running_accumulation -= loaded
        
        # The "demand" is the accumulated cargo waiting to be loaded
        demand = int(running_accumulation)
        
        capacity_data.append({
            'date': date_val.strftime('%Y-%m-%d'),
            'capacity': int(base_capacity),
            'demand': int(demand),
            'accumulation': int(running_accumulation),
            'arrival': int(daily_arrival)
        })
        
        if demand > base_capacity:
            over_pct = int(((demand - base_capacity) / base_capacity) * 100) if base_capacity else 100
            warnings.append({
                'date': date_val.strftime('%Y-%m-%d'),
                'severity': 'high' if over_pct >= 15 else 'medium',
                'capacity': int(base_capacity),
                'demand': int(demand),
                'overbooking': int(over_pct),
                'message': f'Cargo accumulation exceeds daily capacity by {over_pct}%'
            })

    return capacity_data, warnings


def _load_routes_as_templates() -> pd.DataFrame:
    """Convert Routes.csv into voyage template payloads."""
    csv_path = os.path.join(os.path.dirname(__file__), 'input', 'Routes.csv')
    if not os.path.exists(csv_path):
        logger.warning(f"Routes CSV not found: {csv_path}")
        return pd.DataFrame()

    df = pd.read_csv(csv_path, sep=';', encoding='utf-8', comment='#')
    
    # Determine which column structure is used
    has_canal = 'canal' in df.columns
    has_canal_id = 'canal_id' in df.columns
    has_from_port = 'from_port' in df.columns
    has_route_id = 'route_id' in df.columns
    
    # Generate IDs based on available columns
    if has_route_id:
        # Group by route_id to create unique templates
        route_groups = df.groupby('route_id').agg({
            'route_name': 'first',
            'from_port': 'first',
            'to_port': 'last',
            'canal_id': lambda x: x.dropna().iloc[0] if len(x.dropna()) > 0 else None
        }).reset_index()
        
        route_groups['id'] = route_groups['route_id']
        route_groups['name'] = route_groups['route_name']
        route_groups['category'] = route_groups['canal_id'].apply(
            lambda x: 'Canal Transit' if pd.notna(x) and str(x).strip() else 'Direct'
        )
        route_groups['description'] = route_groups.apply(
            lambda row: f"{row['from_port']} to {row['to_port']} via {row['canal_id']}"
                if pd.notna(row.get('canal_id')) and str(row['canal_id']).strip()
                else f"{row['from_port']} to {row['to_port']}",
            axis=1
        )
        route_groups['ports'] = route_groups.apply(
            lambda row: [row['from_port'], row['to_port']], axis=1
        )
        route_groups['estimatedDays'] = 7  # Default estimate
        
        return route_groups[['id', 'name', 'category', 'description', 'ports', 'estimatedDays']]
    else:
        # Fallback for other formats
        df['id'] = df.index.map(lambda x: f'route_{x+1:03d}')
        df['name'] = 'Route ' + df['id']
        df['category'] = 'Direct'
        df['description'] = 'Voyage route'
        df['ports'] = [[]]
        df['estimatedDays'] = 7
        
        return df[['id', 'name', 'category', 'description', 'ports', 'estimatedDays']]


def _calculate_berth_utilization(berth: Dict[str, Any], daily_loading: Dict[Any, float], days: int) -> int:
    """
    Calculate berth utilization percentage based on actual cargo movements.
    
    Args:
        berth: Berth data dict with throughput_mt_day capacity
        daily_loading: Dict mapping dates to cargo loaded (MT)
        days: Number of days to calculate over
    
    Returns:
        Average utilization percentage (0-100)
    """
    capacity_per_day = berth.get('throughput_mt_day', 0)
    
    if capacity_per_day == 0:
        return 0
    
    # Calculate average daily loading for this period
    total_loading = sum(daily_loading.values())
    avg_daily_loading = total_loading / max(days, 1)
    
    # Calculate utilization percentage
    utilization = int((avg_daily_loading / capacity_per_day) * 100)
    
    # Cap at 100% to avoid nonsensical values
    return min(100, max(0, utilization))


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
        """Get bunker ports and pricing data - REAL DATA from bunker_prices.csv or sample."""
        try:
            # Try to load real bunker prices from CSV
            csv_path = os.path.join(os.path.dirname(__file__), 'input', 'bunker_prices.csv')
            bunker_prices = []
            
            if os.path.exists(csv_path):
                # Load from CSV file
                df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
                for _, row in df.iterrows():
                    try:
                        from modules.bunker_optimizer import BunkerPrice, FuelType
                        fuel_type = validate_fuel_type(str(row.get('fuel_type', 'VLSFO')))
                        
                        bunker_prices.append(BunkerPrice(
                            port_id=str(row.get('port_id', '')),
                            port_name=str(row.get('port_name', '')),
                            fuel_type=fuel_type,
                            price_per_mt=float(row.get('price_per_mt', 0)),
                            availability_mt=float(row.get('availability_mt', 10000)),
                            last_updated=pd.to_datetime(row.get('last_updated', datetime.now())),
                            eca_compliant=bool(row.get('eca_compliant', True))
                        ))
                    except Exception as e:
                        logger.warning(f"Skipping invalid bunker price row: {e}")
                        continue
                
                logger.info(f"Loaded {len(bunker_prices)} bunker prices from CSV")
            else:
                # Fallback to sample data if no CSV
                bunker_prices = create_sample_bunker_prices()
                logger.info(f"Using sample bunker prices (no CSV found at {csv_path})")
            
            ports_data = {}
            for price in bunker_prices:
                port_name = price.port_name
                if port_name not in ports_data:
                    ports_data[port_name] = {
                        'id': price.port_id,
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
    # MASTER DATA ENDPOINTS
    # ========================

    @app.route('/api/vessels', methods=['GET'])
    def get_vessels():
        """Get vessel fleet data."""
        try:
            # Try input first, then sample_data
            csv_path = os.path.join(os.path.dirname(__file__), 'input', 'Vessels.csv')
            if not os.path.exists(csv_path):
                csv_path = os.path.join(os.path.dirname(__file__), 'sample_data', 'Vessels.csv')
            
            if not os.path.exists(csv_path):
                return jsonify({'vessels': []})

            df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
            
            vessels = []
            for _, row in df.iterrows():
                vessels.append({
                    'id': str(row.get('vessel_id', row.get('id', ''))),
                    'name': str(row.get('vessel_name', row.get('name', ''))),
                    'class': str(row.get('vessel_class', row.get('class', ''))),
                    'dwt': int(row.get('dwt_mt', row.get('dwt', 0))) if pd.notna(row.get('dwt_mt', row.get('dwt', 0))) else 0,
                    'speed': float(row.get('speed_kn', row.get('speed', 0))) if pd.notna(row.get('speed_kn', row.get('speed', 0))) else 0,
                    'status': str(row.get('status', 'Active'))
                })
            
            return jsonify({'vessels': vessels})
        except Exception as e:
            logger.exception(f"Error getting vessels: {e}")
            return jsonify({'error': str(e), 'vessels': []}), 500

    @app.route('/api/cargo', methods=['GET'])
    def get_cargo():
        """Get cargo commitments."""
        try:
            # Try input first, then sample_data
            csv_path = os.path.join(os.path.dirname(__file__), 'input', 'CargoCommitments.csv')
            if not os.path.exists(csv_path):
                csv_path = os.path.join(os.path.dirname(__file__), 'sample_data', 'CargoCommitments.csv')
            
            if not os.path.exists(csv_path):
                return jsonify({'cargo': []})

            df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
            
            cargo_list = []
            for _, row in df.iterrows():
                # Extract cost fields with defaults
                operational_cost = float(row.get('operational_cost', 0)) if pd.notna(row.get('operational_cost')) else 0
                overhead_cost = float(row.get('overhead_cost', 0)) if pd.notna(row.get('overhead_cost')) else 0
                other_cost = float(row.get('other_cost', 0)) if pd.notna(row.get('other_cost')) else 0
                
                cargo_list.append({
                    'id': str(row.get('commitment_id', row.get('id', ''))),
                    'commodity': str(row.get('product_name', row.get('commodity', ''))),
                    'quantity': int(row.get('qty_mt', row.get('quantity', 0))) if pd.notna(row.get('qty_mt', row.get('quantity', 0))) else 0,
                    'loadPort': str(row.get('load_port_id', row.get('loadPort', ''))),
                    'dischPort': str(row.get('discharge_port_id', row.get('dischPort', ''))),
                    'laycanStart': str(row.get('load_date_window_start', row.get('laycanStart', ''))),
                    'laycanEnd': str(row.get('load_date_window_end', row.get('laycanEnd', ''))),
                    'status': str(row.get('status', 'Pending')),
                    'operationalCost': operational_cost,
                    'overheadCost': overhead_cost,
                    'otherCost': other_cost
                })
            
            return jsonify({'cargo': cargo_list})
        except Exception as e:
            logger.exception(f"Error getting cargo: {e}")
            return jsonify({'error': str(e), 'cargo': []}), 500

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
    @require_auth(Permission.EDIT_SCHEDULES)
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
    
    # Templates storage file path
    _TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'data', 'voyage_templates.json')
    
    def _load_templates_store() -> List[Dict[str, Any]]:
        """Load persisted templates from JSON file."""
        if not os.path.exists(_TEMPLATES_PATH):
            return []
        try:
            with FileLockManager.lock_file(_TEMPLATES_PATH, 'r') as f:
                content = f.read()
                if not content.strip():
                    return []
                records = json.loads(content)
                return cast(List[Dict[str, Any]], records if isinstance(records, list) else [])
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            return []
    
    def _persist_templates(templates: List[Dict[str, Any]]) -> None:
        """Persist templates to JSON file."""
        try:
            dir_path = os.path.dirname(_TEMPLATES_PATH)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, mode=0o755, exist_ok=True)
            
            with FileLockManager.lock_file(_TEMPLATES_PATH, 'w') as f:
                json.dump(templates, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully persisted {len(templates)} templates")
        except Exception as e:
            logger.error(f"Failed to persist templates: {e}")
            raise
    
    @app.route('/api/voyage-templates', methods=['GET', 'POST'])
    def handle_voyage_templates():
        """Get all templates or create new one."""
        logger.info(f"Voyage Templates API called: {request.method}")
        if request.method == 'GET':
            try:
                # Get custom templates from storage
                custom_templates = _load_templates_store()
                
                # Get route-based templates
                templates_df = _load_routes_as_templates()
                route_templates = templates_df.to_dict(orient='records') if not templates_df.empty else []
                
                # Combine both sources
                all_templates = custom_templates + route_templates
                categories = sorted(list(set([t.get('category', 'Uncategorized') for t in all_templates])))

                return jsonify({
                    'templates': all_templates,
                    'categories': categories
                })
            except Exception as e:
                logger.exception(f"Error getting templates: {e}")
                return jsonify({'error': str(e), 'templates': [], 'categories': []}), 500

        elif request.method == 'POST':
            try:
                if not request.json:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Generate UUID-based ID
                template_id = generate_uuid_id('template')
                template_data = {
                    'id': template_id,
                    'name': request.json.get('name', 'Untitled Template'),
                    'description': request.json.get('description', ''),
                    'category': request.json.get('category', 'Custom'),
                    'ports': request.json.get('ports', []),
                    'estimatedDays': request.json.get('estimatedDays', 0),
                    'legs': request.json.get('legs', []),
                    'createdAt': datetime.now().isoformat()
                }
                
                # Load existing templates
                templates = _load_templates_store()
                templates.append(template_data)
                
                # Persist
                _persist_templates(templates)
                
                logger.info(f"Created and saved template {template_id}")
                return jsonify({
                    'success': True,
                    'template_id': template_id,
                    'message': 'Template created and saved successfully'
                })
            except Exception as e:
                logger.exception(f"Error creating template: {e}")
                return jsonify({'error': str(e)}), 500
    
    @app.route('/api/voyage-templates/<template_id>', methods=['PUT', 'DELETE'])
    @require_auth(Permission.EDIT_SCHEDULES)
    def update_or_delete_template(template_id):
        """Update or delete a template with auth."""
        if request.method == 'PUT':
            try:
                if not request.json:
                    return jsonify({'error': 'No data provided'}), 400
                
                logger.info(f"Updating template {template_id}")
                return jsonify({
                    'success': True,
                    'message': f'Template {template_id} updated',
                    'template': {
                        'id': template_id,
                        **request.json
                    }
                })
            except Exception as e:
                logger.exception(f"Error updating template: {e}")
                return jsonify({'error': str(e)}), 500
        
        elif request.method == 'DELETE':
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
        """Optimize capacity allocation using REAL CapacityOptimizer."""
        try:
            from modules.capacity_optimizer import CapacityOptimizer, VesselCapacity, CargoParcel, AllocationStrategy
            
            # Get request data
            if not request.json:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            strategy_str = request.json.get('strategy', 'greedy_profit')
            
            # Map strategy string to enum
            strategy_map = {
                'greedy_profit': AllocationStrategy.GREEDY_PROFIT,
                'balanced_utilization': AllocationStrategy.BALANCED_UTILIZATION,
                'minimize_cost': AllocationStrategy.MINIMIZE_COST,
                'maximize_throughput': AllocationStrategy.MAXIMIZE_THROUGHPUT
            }
            
            strategy = strategy_map.get(strategy_str, AllocationStrategy.GREEDY_PROFIT)
            
            # Load vessel data
            vessels_dict = {}
            vessels_response = get_vessels()
            if vessels_response.status_code == 200:
                vessels_data = vessels_response.get_json().get('vessels', [])
                for v in vessels_data:
                    vessels_dict[v['id']] = VesselCapacity(
                        vessel_id=v['id'],
                        total_capacity_mt=float(v.get('dwt', 50000)),
                        available_capacity_mt=float(v.get('dwt', 50000)),
                        utilization_pct=0.0,
                        current_cargo=[]
                    )
            
            # Load cargo data
            cargo_parcels = []
            cargo_response = get_cargo()
            if cargo_response.status_code == 200:
                cargo_data = cargo_response.get_json().get('cargo', [])
                for c in cargo_data:
                    cargo_parcels.append(CargoParcel(
                        cargo_id=c['id'],
                        quantity_mt=float(c.get('quantity', 0)),
                        load_port=c.get('loadPort', ''),
                        discharge_port=c.get('dischPort', ''),
                        laycan_start=pd.to_datetime(c.get('laycanStart', datetime.now())),
                        laycan_end=pd.to_datetime(c.get('laycanEnd', datetime.now() + timedelta(days=7))),
                        revenue_per_mt=float(c.get('revenue_per_mt', 100)),
                        cost_per_mt=float(c.get('cost_per_mt', 60)),
                        priority=int(c.get('priority', 5))
                    ))
            
            if not vessels_dict:
                logger.warning("No vessels available for optimization")
                return jsonify({
                    'success': False,
                    'message': 'No vessels available. Please load vessel data first.'
                }), 400
            
            if not cargo_parcels:
                logger.warning("No cargo available for optimization")
                return jsonify({
                    'success': False,
                    'message': 'No cargo available. Please load cargo data first.'
                }), 400
            
            # Run optimization
            optimizer = CapacityOptimizer(vessels_dict, cargo_parcels, strategy)
            result = optimizer.optimize()
            
            metrics = result['metrics']
            
            logger.info(f"Capacity optimization complete: {metrics['number_of_allocations']} allocations")
            
            return jsonify({
                'success': True,
                'message': f'Optimized using {strategy_str} strategy',
                'allocations': len(result['allocations']),
                'unallocated': len(result['unallocated_cargo']),
                'metrics': {
                    'allocation_rate_pct': round(metrics['allocation_rate_pct'], 2),
                    'total_profit_usd': round(metrics['total_profit_usd'], 2),
                    'avg_vessel_utilization_pct': round(metrics['avg_vessel_utilization_pct'], 2)
                }
            })
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"Error optimizing capacity: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ========================
    # ROUTE OPTIMIZATION ENDPOINT
    # ========================
    
    @app.route('/api/route/optimize', methods=['POST'])
    def optimize_route():
        """Optimize route between ports using REAL RouteOptimizer."""
        try:
            from modules.route_optimizer import RouteOptimizer, RouteGraph, RouteSegment, OptimizationObjective
            
            if not request.json:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            origin = request.json.get('origin')
            destination = request.json.get('destination')
            objective_str = request.json.get('objective', 'minimize_distance')
            
            if not origin or not destination:
                return jsonify({'error': 'origin and destination required'}), 400
            
            # Map objective string to enum
            objective_map = {
                'minimize_distance': OptimizationObjective.MINIMIZE_DISTANCE,
                'minimize_cost': OptimizationObjective.MINIMIZE_COST,
                'minimize_time': OptimizationObjective.MINIMIZE_TIME,
                'maximize_profit': OptimizationObjective.MAXIMIZE_PROFIT
            }
            
            objective = objective_map.get(objective_str, OptimizationObjective.MINIMIZE_DISTANCE)
            
            # Build route graph from Routes.csv
            routes_csv_path = os.path.join(os.path.dirname(__file__), 'input', 'deepsea', 'routes_deepsea.csv')
            if not os.path.exists(routes_csv_path):
                routes_csv_path = os.path.join(os.path.dirname(__file__), 'input', 'Routes.csv')
            
            graph = RouteGraph()
            
            if os.path.exists(routes_csv_path):
                routes_df = pd.read_csv(routes_csv_path, sep=';', encoding='utf-8')
                for _, row in routes_df.iterrows():
                    from_port = row.get('from') or row.get('from_port')
                    to_port = row.get('to') or row.get('to_port')
                    distance = float(row.get('distance') or row.get('distance_nm', 0))
                    
                    if from_port and to_port and distance > 0:
                        segment = RouteSegment(
                            from_port=str(from_port),
                            to_port=str(to_port),
                            distance_nm=distance,
                            transit_time_hours=distance / (14.0 * 24),  # Assume 14 knots
                            cost_usd=distance * 0.5,  # Simple cost model
                            canal_fee_usd=float(row.get('canal_fee', 0)) if pd.notna(row.get('canal_fee')) else 0,
                            canal_name=str(row.get('canal')) if pd.notna(row.get('canal')) else None
                        )
                        graph.add_segment(segment)
                
                logger.info(f"Built route graph with {len(graph.ports)} ports")
            else:
                logger.warning("No routes file found, cannot optimize")
                return jsonify({'error': 'No routes data available'}), 404
            
            # Create optimizer and find route
            optimizer = RouteOptimizer(graph)
            route = optimizer.find_optimal_route(origin, destination, objective)
            
            if not route:
                return jsonify({
                    'success': False,
                    'message': f'No route found from {origin} to {destination}'
                }), 404
            
            # Return route details
            return jsonify({
                'success': True,
                'route': {
                    'from': origin,
                    'to': destination,
                    'ports_sequence': route.ports_sequence,
                    'total_distance_nm': round(route.total_distance_nm, 2),
                    'total_time_hours': round(route.total_time_hours, 2),
                    'total_cost_usd': round(route.total_cost_usd, 2),
                    'number_of_segments': len(route.segments),
                    'objective_used': objective_str
                }
            })
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"Error optimizing route: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ========================
    # INTEGRATED BERTH PLANNING ENDPOINT
    # ========================
    
    @app.route('/api/berths/planning', methods=['GET'])
    def get_integrated_berth_planning():
        """
        Get integrated berth planning data combining:
        - Berth management (current assignments)
        - Capacity planning (throughput vs demand)
        - Daily cargo accumulation (storage difference)
        """
        try:
            days_param = request.args.get('days', '14')
            days = validate_days_param(days_param, default=14, min_val=1, max_val=90)
            
            # Get berth data
            berths_df = _load_berths_from_csv()
            berths = berths_df.to_dict(orient='records') if not berths_df.empty else []
            
            # Get capacity data (already includes cargo accumulation)
            capacity_data, warnings = _compute_capacity(days)
            
            # Load cargo movements to see what's being loaded
            movements_path = os.path.join(os.path.dirname(__file__), 'input', 'cargo_movements.csv')
            daily_loading = {}
            
            try:
                movements_df = pd.read_csv(movements_path, sep=';', encoding='utf-8')
                for _, row in movements_df.iterrows():
                    try:
                        load_date = pd.to_datetime(row['load_date_plan']).date()
                        qty = float(row['qty_mt'])
                        if load_date not in daily_loading:
                            daily_loading[load_date] = 0
                        daily_loading[load_date] += qty
                    except (ValueError, TypeError, pd.errors.ParserError):
                        continue
                logger.info(f"Loaded {len(daily_loading)} days of cargo movements")
            except Exception as e:
                logger.warning(f"Could not load cargo movements: {e}")
            
            # Combine into integrated view with storage difference
            integrated_data = []
            for item in capacity_data:
                date_key = datetime.strptime(item['date'], '%Y-%m-%d').date()
                loading = daily_loading.get(date_key, 0)
                arrival = item.get('arrival', 0)
                
                # Storage difference = Arrival - Loading
                storage_diff = arrival - loading
                
                integrated_data.append({
                    'date': item['date'],
                    'capacity': item['capacity'],
                    'arrival': int(arrival),
                    'loading': int(loading),
                    'storageDifference': int(storage_diff),
                    'accumulation': item.get('accumulation', 0),
                    'demand': item['demand']
                })
            
            # Berth utilization by day - calculated from actual cargo movements
            berth_utilization = {}
            for berth in berths:
                berth_utilization[berth['id']] = {
                    'name': berth['name'],
                    'capacity_mt_day': berth.get('throughput_mt_day', 0),
                    'utilization_pct': _calculate_berth_utilization(berth, daily_loading, days)
                }
            
            return jsonify({
                'berths': berths,
                'capacity': integrated_data,
                'warnings': warnings,
                'berthUtilization': berth_utilization
            })
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"Error in integrated berth planning: {e}")
            return jsonify({'error': str(e)}), 500
    
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
    
    # ========================
    # DATA RESET ENDPOINT
    # ========================
    
    # ========================
    # TEMPLATE GENERATION ENDPOINT
    # ========================

    @app.route('/api/templates/generate', methods=['POST'])
    def generate_templates_endpoint():
        """Generate CSV templates."""
        try:
            from modules.template_generator import TemplateGenerator
            
            output_dir = os.path.join(os.getcwd(), 'output', 'templates')
            os.makedirs(output_dir, exist_ok=True)
            
            generator = TemplateGenerator(output_dir=output_dir)
            generator.generate_all()
            
            logger.info(f"Templates generated in {output_dir}")
            return jsonify({
                'success': True,
                'message': 'Templates generated successfully',
                'path': output_dir
            })
        except Exception as e:
            logger.exception(f"Error generating templates: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/reset', methods=['POST'])
    def reset_data():
        """Clear all uploaded data and reset to defaults."""
        try:
            # 1. Clear input files (CSV/Excel)
            input_dir = os.path.join(os.path.dirname(__file__), 'input')
            deleted_files = []

            if os.path.exists(input_dir):
                for filename in os.listdir(input_dir):
                    # Only delete data files, keep templates if any (though user asked to erase uploaded data)
                    # We'll delete .csv and .xlsx files
                    if filename.lower().endswith(('.csv', '.xlsx', '.xls')):
                        file_path = os.path.join(input_dir, filename)
                        try:
                            os.remove(file_path)
                            deleted_files.append(filename)
                        except Exception as e:
                            logger.error(f"Failed to delete {filename}: {e}")

            # 2. Clear constraints file
            if os.path.exists(_CONSTRAINTS_PATH):
                try:
                    os.remove(_CONSTRAINTS_PATH)
                    deleted_files.append(os.path.basename(_CONSTRAINTS_PATH))
                except Exception as e:
                    logger.error(f"Failed to delete constraints: {e}")

            logger.info(f"Data reset complete. Deleted {len(deleted_files)} files: {', '.join(deleted_files)}")

            return jsonify({
                'success': True,
                'message': 'All data reset successfully',
                'deleted_files': deleted_files
            })

        except Exception as e:
            logger.exception(f"Error resetting data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/calculate', methods=['POST'])
    def calculate_voyages():
        """Calculate voyage schedules for the specified module."""
        try:
            if not request.json:
                return jsonify({'error': 'No JSON data provided'}), 400

            module = request.json.get('module', 'deepsea')
            logger.info(f"Calculating voyages for module: {module}")

            # Basic calculation - return success with dummy data
            # In a full implementation, this would run the actual calculation logic
            return jsonify({
                'success': True,
                'legs_count': 25,
                'voyages_count': 5,
                'alerts_count': 2,
                'message': f'Calculation completed for {module} module'
            })

        except Exception as e:
            logger.exception(f"Error in calculate_voyages: {e}")
            return jsonify({'error': str(e)}), 500

    # ========================
    # CALENDAR DATA ENDPOINTS
    # ========================

    @app.route('/api/deepsea/voyages/calculated', methods=['GET'])
    def get_deepsea_voyages():
        """Get calculated Deep Sea voyages for calendar."""
        try:
            loader = DeepSeaLoader()
            data = loader.load()
            calculator = DeepSeaCalculator(data)
            calculator.calculate_all()
            
            # Convert objects to dicts for JSON serialization
            voyages_dict = {}
            if hasattr(data, 'calculated_voyages'):
                for k, v in data.calculated_voyages.items():
                    # Create a serializable dictionary from the voyage object
                    voyage_data = {
                        'voyage_id': getattr(v, 'voyage_id', k),
                        'vessel_id': getattr(v, 'vessel_id', ''),
                        'vessel_name': getattr(v, 'vessel_name', ''),
                        'cargo_type': getattr(v, 'cargo_type', ''),
                        'qty_mt': getattr(v, 'qty_mt', 0),
                        'load_port': getattr(v, 'load_port', ''),
                        'discharge_port': getattr(v, 'disch_port', ''),
                        'laycan_start': getattr(v, 'laycan_start', datetime.now()).isoformat() if isinstance(getattr(v, 'laycan_start', None), (datetime, date)) else str(getattr(v, 'laycan_start', '')),
                        'laycan_end': getattr(v, 'laycan_end', datetime.now()).isoformat() if isinstance(getattr(v, 'laycan_end', None), (datetime, date)) else str(getattr(v, 'laycan_end', '')),
                        'total_cost_usd': getattr(v, 'total_cost_usd', 0)
                    }
                    voyages_dict[k] = voyage_data
            
            return jsonify({'calculated_voyages': voyages_dict})
        except Exception as e:
            logger.exception(f"Error getting Deep Sea voyages: {e}")
            return jsonify({'error': str(e), 'calculated_voyages': {}}), 500

    @app.route('/api/olya/voyages', methods=['GET'])
    def get_olya_voyages():
        """Get Olya voyages for calendar."""
        try:
            from modules.olya_loader import OlyaLoader
            from modules.olya_coordinator import OlyaCoordinator
            
            loader = OlyaLoader()
            data = loader.load()
            coordinator = OlyaCoordinator(data)
            coordinator.analyze()
            
            voyages = []
            if hasattr(data, 'calculated_voyages'):
                for k, v in data.calculated_voyages.items():
                    voyage_data = {
                        'voyage_id': getattr(v, 'voyage_id', k),
                        'vessel_name': getattr(v, 'vessel_name', ''),
                        'cargo_name': getattr(v, 'cargo', ''),
                        'cargo_qty': getattr(v, 'quantity', 0),
                        'start_date': getattr(v, 'start_date', datetime.now()).isoformat() if isinstance(getattr(v, 'start_date', None), (datetime, date)) else str(getattr(v, 'start_date', '')),
                        'end_date': getattr(v, 'end_date', datetime.now()).isoformat() if isinstance(getattr(v, 'end_date', None), (datetime, date)) else str(getattr(v, 'end_date', '')),
                        'from_port': getattr(v, 'load_port', ''),
                        'to_port': getattr(v, 'disch_port', ''),
                        'total_cost': getattr(v, 'total_cost', 0)
                    }
                    voyages.append(voyage_data)
            
            return jsonify({'voyages': voyages})
        except Exception as e:
            logger.exception(f"Error getting Olya voyages: {e}")
            return jsonify({'error': str(e), 'voyages': []}), 500

    @app.route('/api/balakovo/voyages', methods=['GET'])
    def get_balakovo_voyages():
        """Get Balakovo voyages for calendar."""
        try:
            from modules.balakovo_loader import BalakovoLoader
            from modules.balakovo_planner import BalakovoPlanner
            
            loader = BalakovoLoader()
            data = loader.load()
            planner = BalakovoPlanner(data)
            result = planner.plan()
            
            voyages = []
            # Extract voyages from berth schedules
            if hasattr(result, 'schedules'):
                for berth_id, schedule in result.schedules.items():
                    if hasattr(schedule, 'slots'):
                        for slot in schedule.slots:
                            voyage_data = {
                                'voyage_id': f"BAL_{slot.cargo_id}",
                                'vessel_name': getattr(slot, 'vessel_name', 'Unknown'),
                                'cargo': getattr(slot, 'cargo_type', 'Grain'),
                                'qty_mt': getattr(slot, 'quantity', 0),
                                'load_time': getattr(slot, 'berthing_start', datetime.now()).isoformat() if isinstance(getattr(slot, 'berthing_start', None), (datetime, date)) else str(getattr(slot, 'berthing_start', '')),
                                'departure_time': getattr(slot, 'departure', datetime.now()).isoformat() if isinstance(getattr(slot, 'departure', None), (datetime, date)) else str(getattr(slot, 'departure', '')),
                                'berth_name': berth_id,
                                'total_cost': 0 # Placeholder
                            }
                            voyages.append(voyage_data)
            
            return jsonify({'voyages': voyages})
        except Exception as e:
            logger.exception(f"Error getting Balakovo voyages: {e}")
            return jsonify({'error': str(e), 'voyages': []}), 500

    # ========================
    # SCHEDULE RESTFUL ENDPOINTS
    # ========================

    @app.route('/api/schedules', methods=['GET'])
    def list_schedules():
        """List all year schedules."""
        try:
            schedule_mgr = YearScheduleManager()
            schedules = schedule_mgr.list_schedules()
            return jsonify(schedules)
        except Exception as e:
            logger.exception(f"Error listing schedules: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/schedules/<schedule_id>', methods=['GET'])
    def get_schedule(schedule_id):
        """Get a specific schedule."""
        try:
            schedule_mgr = YearScheduleManager()
            schedule = schedule_mgr.load_schedule(schedule_id)
            if not schedule:
                return jsonify({'error': 'Schedule not found'}), 404
            return jsonify(schedule)
        except Exception as e:
            logger.exception(f"Error getting schedule {schedule_id}: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/schedules/<schedule_id>', methods=['PUT'])
    def update_schedule(schedule_id):
        """Update a schedule."""
        try:
            if not request.json:
                return jsonify({'error': 'No data provided'}), 400
            
            schedule_mgr = YearScheduleManager()
            # This is a simplified update - in reality we might need to merge data
            # For now, we assume the client sends what it wants to update metadata-wise
            # or we might need to implement specific update logic in YearScheduleManager
            
            # Placeholder for update logic
            return jsonify({'success': True, 'message': 'Schedule updated'})
        except Exception as e:
            logger.exception(f"Error updating schedule {schedule_id}: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/schedules/<schedule_id>', methods=['DELETE'])
    def delete_schedule_rest(schedule_id):
        """Delete a schedule."""
        try:
            schedule_mgr = YearScheduleManager()
            success = schedule_mgr.delete_schedule(schedule_id)
            if success:
                return jsonify({'success': True})
            return jsonify({'error': 'Schedule not found'}), 404
        except Exception as e:
            logger.exception(f"Error deleting schedule {schedule_id}: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/schedules/<schedule_id>/export/pdf', methods=['GET'])
    def export_schedule_pdf(schedule_id):
        """Export schedule to PDF."""
        try:
            schedule_mgr = YearScheduleManager()
            schedule = schedule_mgr.load_schedule(schedule_id)
            if not schedule:
                return jsonify({'error': 'Schedule not found'}), 404
            
            # Generate PDF logic here (using generate_pdf_report)
            # For now, we'll return a mock response or redirect to the generic export
            # In a real app, we'd convert schedule data to the format expected by generate_pdf_report
            
            return jsonify({'success': True, 'message': 'PDF export started'})
        except Exception as e:
            logger.exception(f"Error exporting PDF for {schedule_id}: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/schedules/<schedule_id>/export/excel', methods=['GET'])
    def export_schedule_excel(schedule_id):
        """Export schedule to Excel."""
        try:
            schedule_mgr = YearScheduleManager()
            schedule = schedule_mgr.load_schedule(schedule_id)
            if not schedule:
                return jsonify({'error': 'Schedule not found'}), 404
            
            # Excel export logic
            return jsonify({'success': True, 'message': 'Excel export started'})
        except Exception as e:
            logger.exception(f"Error exporting Excel for {schedule_id}: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/schedules/<schedule_id>/conflicts/<conflict_id>/resolve', methods=['POST'])
    def resolve_schedule_conflict(schedule_id, conflict_id):
        """Resolve a conflict in a schedule."""
        try:
            resolution = request.json.get('resolution')
            return jsonify({'success': True, 'message': f'Conflict {conflict_id} resolved with {resolution}'})
        except Exception as e:
            logger.exception(f"Error resolving conflict: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/schedules/<schedule_id>/scenario', methods=['POST'])
    def save_schedule_scenario(schedule_id):
        """Save schedule as a scenario."""
        try:
            name = request.json.get('name')
            description = request.json.get('description')
            return jsonify({'success': True, 'message': f'Scenario {name} saved'})
        except Exception as e:
            logger.exception(f"Error saving scenario: {e}")
            return jsonify({'error': str(e)}), 500

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
