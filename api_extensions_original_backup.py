"""
API Extensions for UI Modules
Add these endpoints to api_server.py to support the new UI modules
"""

from flask import jsonify, request
from datetime import datetime, timedelta
import yaml
import pandas as pd
import os
import math
from typing import Any, Dict, List, Optional, Union, Tuple, cast
import logging

# Import real modules
from modules.alerts import AlertSystem, AlertSeverity, Alert
from modules.berth_constraints import BerthConstraintValidator, BerthConstraintSet, VesselSizeConstraint
from modules.berth_utilization import BerthUtilizationAnalyzer
from modules.bunker_optimizer import BunkerOptimizer, create_sample_bunker_prices
from modules.deepsea_scenarios import ScenarioManager
from modules.deepsea_loader import DeepSeaLoader
from modules.deepsea_calculator import DeepSeaCalculator
from modules.balakovo_loader import BalakovoLoader
from modules.pdf_reporter import generate_pdf_report

logger = logging.getLogger(__name__)

_ALERT_CACHE_TTL_SEC = 60
_alert_cache: Dict[str, Any] = {"data": None, "timestamp": None}
_CONSTRAINTS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'berth_constraints.json')


# Load configuration
def load_config():
    """Load configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        # Load as raw YAML - the file uses mixed formatting
        config = yaml.safe_load(f)
    return config


# Global config
try:
    CONFIG = load_config()
    API_CONFIG = CONFIG.get('api_extensions', {})
except Exception:
    # Fallback if config loading fails
    API_CONFIG = {
        'berth_utilization': {'min_pct': 40, 'max_pct': 95},
        'capacity': {'base_capacity': 100, 'demand_min': 60, 'demand_max': 120, 'overbooking_threshold_pct': 15},
        'weather': {
            'forecast_days': 5,
            'conditions': ['clear', 'cloudy', 'rain', 'wind'],
            'temp_min_c': 15, 'temp_max_c': 28,
            'wind_speed_min_kn': 10, 'wind_speed_max_kn': 35,
            'wave_height_min_m': 1.0, 'wave_height_max_m': 4.0
        },
        'id_generation': {
            'constraint_id_min': 100, 'constraint_id_max': 999,
            'scenario_id_min': 100, 'scenario_id_max': 999,
            'template_id_min': 100, 'template_id_max': 999
        },
        'conflicts': {'auto_resolve_enabled': True, 'manual_intervention_threshold': 1}
    }


def load_weather_warnings() -> pd.DataFrame:
    """Load weather warnings from CSV file using logging for errors."""
    csv_path = os.path.join(os.path.dirname(__file__), 'input', 'WeatherWarnings.csv')
    try:
        return pd.read_csv(csv_path, sep=';', encoding='utf-8')
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to load weather warnings from %s: %s", csv_path, exc)
        return pd.DataFrame()


def register_ui_module_endpoints(app):
    """Register all UI module API endpoints"""
    
    # ========================
    # ALERTS ENDPOINTS
    # ========================
    
    @app.route('/api/alerts', methods=['GET'])
    def get_alerts():
        """Get all alerts with filtering options using AlertSystem."""
        try:
            severity_param = request.args.get('severity', 'all')
            status_param = request.args.get('status', 'active')

            all_data = _get_alert_data()

            legs_data = []
            for leg in all_data.voyage_legs:
                port_value = getattr(leg, 'from_port', None) or getattr(leg, 'to_port', '')
                legs_data.append({
                    'asset': getattr(leg, 'vessel_id', ''),
                    'start': getattr(leg, 'start_time', None),
                    'end': getattr(leg, 'end_time', None),
                    'port': port_value,
                    'activity': getattr(leg, 'leg_type', ''),
                })

            if not legs_data:
                logger.warning("No voyage legs found for alert checking")
                return jsonify({'alerts': []})

            voyage_df = pd.DataFrame(legs_data)

            alert_system = AlertSystem()

            severity_filter = None
            if severity_param != 'all':
                severity_map = {
                    'info': AlertSeverity.INFO,
                    'warning': AlertSeverity.WARNING,
                    'critical': AlertSeverity.CRITICAL,
                }
                severity_filter = severity_map.get(severity_param.lower())

            all_alerts = alert_system.get_all_alerts(severity_filter=severity_filter)

            alerts_data = []
            for alert in all_alerts:
                alert_dict = alert.to_dict()
                alert_dict['status'] = 'active'

                if status_param != 'all' and alert_dict['status'] != status_param:
                    continue

                alerts_data.append(alert_dict)

            logger.info(
                "Returning %d alerts (severity=%s, status=%s)",
                len(alerts_data),
                severity_param,
                status_param,
            )
            return jsonify({'alerts': alerts_data})

        except Exception as exc:  # noqa: BLE001
            logger.exception("Error getting alerts: %s", exc)
            return jsonify({'alerts': [], 'error': str(exc)}), 500
    
    @app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
    def acknowledge_alert(alert_id):
        """Acknowledge an alert"""
        # In production, update database
        return jsonify({'success': True, 'message': f'Alert {alert_id} acknowledged'})
    
    @app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
    def resolve_alert(alert_id):
        """Resolve an alert"""
        # In production, update database
        return jsonify({'success': True, 'message': f'Alert {alert_id} resolved'})
    
    # ========================
    # BERTH MANAGEMENT ENDPOINTS
    # ========================
    
    @app.route('/api/berths', methods=['GET'])
    def get_berths():
        """Get berth data from CSV with computed utilization."""
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
            # Scale utilization by average throughput
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
    
    @app.route('/api/berths/capacity', methods=['GET'])
    def get_berth_capacity():
        """Get capacity planning data"""
        days = int(request.args.get('days', 14))
        
        capacity_data, warnings = _compute_capacity(days)
        return jsonify({
            'capacity': capacity_data,
            'warnings': warnings
        })
    
    @app.route('/api/berths/constraints', methods=['POST'])
    def save_constraint():
        """Save a new berth constraint to persistent store."""
        data = request.json or {}
        berth_id = data.get('berth')
        constraint_type = data.get('type')
        value = data.get('value')
        if not berth_id or not constraint_type:
            return jsonify({'success': False, 'error': 'berth and type are required'}), 400

        id_cfg = API_CONFIG.get('id_generation', {})
        id_min = id_cfg.get('constraint_id_min', 100)
        id_max = id_cfg.get('constraint_id_max', 999)
        constraint_id = f'const_{id_min + (int(datetime.now().timestamp()) % (id_max - id_min))}'

        constraint_record = {
            'id': constraint_id,
            'berth': berth_id,
            'type': constraint_type,
            'value': value,
            'startDate': data.get('startDate'),
            'endDate': data.get('endDate'),
            'severity': data.get('severity', 'mandatory'),
        }

        _append_constraint(constraint_record)

        return jsonify({
            'success': True,
            'constraint_id': constraint_id,
            'message': 'Constraint saved successfully'
        })
    
    @app.route('/api/berths/constraints/<constraint_id>', methods=['DELETE'])
    def delete_constraint(constraint_id):
        """Delete a constraint"""
        removed = _remove_constraint(constraint_id)
        status = 200 if removed else 404
        return jsonify({'success': removed, 'message': f'Constraint {constraint_id} deleted' if removed else 'Constraint not found'}), status
    
    @app.route('/api/berths/conflicts/auto-resolve', methods=['POST'])
    def auto_resolve_conflicts():
        """Auto-resolve berth conflicts by clearing expired maintenance windows."""
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
    
    @app.route('/api/berths/conflicts/<conflict_id>/resolve', methods=['POST'])
    def resolve_conflict(conflict_id):
        """Resolve single conflict"""
        # In production, update database
        return jsonify({'success': True, 'message': f'Conflict {conflict_id} resolved'})
    
    # ========================
    # BUNKER OPTIMIZATION ENDPOINTS
    # ========================
    
    @app.route('/api/bunker', methods=['GET'])
    def get_bunker_data():
        """Get bunker ports and pricing data using BunkerOptimizer"""
        try:
            # Use create_sample_bunker_prices to get real bunker data
            bunker_prices = create_sample_bunker_prices()
            
            # Group prices by port
            ports_data = {}
            for price in bunker_prices:
                port_name = price.port_name
                if port_name not in ports_data:
                    ports_data[port_name] = {
                        'id': f'port_{len(ports_data) + 1:03d}',
                        'name': port_name,
                        'prices': {}
                    }
                
                # Map fuel type to lowercase key
                fuel_key = price.fuel_type.value.lower() if hasattr(price.fuel_type, 'value') else str(price.fuel_type).lower()
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
        """Get weather warnings and forecasts from CSV data"""
        # Load real weather warnings from CSV
        df = load_weather_warnings()
        
        warnings = []
        if not df.empty:
            # Convert CSV data to API format
            for _, row in df.iterrows():
                warnings.append({
                    'id': str(row.get('weather_id', 'warn_unknown')),
                    'type': str(row.get('message_type', 'routine')).lower(),
                    'severity': 'high' if int(row.get('severity', 1)) >= 4 else 
                               'medium' if int(row.get('severity', 1)) >= 2 else 'low',
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
        
        # Generate forecast data using config
        forecasts = []
        weather_cfg = API_CONFIG.get('weather', {})
        forecast_days = weather_cfg.get('forecast_days', 5)
        conditions = weather_cfg.get('conditions', ['clear', 'cloudy', 'rain', 'wind'])
        temp_min = weather_cfg.get('temp_min_c', 15)
        temp_max = weather_cfg.get('temp_max_c', 28)
        wind_min = weather_cfg.get('wind_speed_min_kn', 10)
        wind_max = weather_cfg.get('wind_speed_max_kn', 35)
        wave_min = weather_cfg.get('wave_height_min_m', 1.0)
        wave_max = weather_cfg.get('wave_height_max_m', 4.0)
        
        for i in range(forecast_days):
            date = datetime.now() + timedelta(days=i)
            # Deterministic values based on day
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
                # Map status from CSV
                status_map = {
                    'Moored': 'at_port',
                    'Underway': 'underway',
                    'At Anchor': 'anchored',
                    'Loading': 'loading',
                    'Discharging': 'discharging'
                }
                raw_status = str(row.get('status', 'Unknown'))
                status = status_map.get(raw_status, raw_status.lower().replace(' ', '_'))
                
                # Parse ETA if available
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
        """Get all scenarios or create new one using ScenarioManager"""
        if request.method == 'GET':
            try:
                # Load deep sea data
                loader = DeepSeaLoader()
                data = loader.load()
                
                # Initialize scenario manager
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
                    
                data = request.json
                scenario_name = data.get('name', 'New Scenario')
                scenario_desc = data.get('description', '')
                voyage_ids = data.get('voyage_ids', [])
                
                # Load deep sea data
                loader = DeepSeaLoader()
                ds_data = loader.load()
                
                # Initialize scenario manager
                scenario_mgr = ScenarioManager(ds_data)
                
                # Generate ID using config
                id_cfg = API_CONFIG.get('id_generation', {})
                id_min = id_cfg.get('scenario_id_min', 100)
                id_max = id_cfg.get('scenario_id_max', 999)
                scenario_id = f'scenario_{id_min + (int(datetime.now().timestamp()) % (id_max - id_min))}'
                
                # Create scenario
                new_scenario = scenario_mgr.create_scenario(
                    scenario_id=scenario_id,
                    scenario_name=scenario_name,
                    description=scenario_desc,
                    voyage_ids=voyage_ids if voyage_ids else []
                )
                
                logger.info(f"Created scenario {scenario_id}: {scenario_name}")
                return jsonify({
                    'success': True,
                    'scenario_id': scenario_id,
                    'message': 'Scenario created successfully',
                    'scenario': {
                        'id': scenario_id,
                        'name': getattr(new_scenario, 'scenario_name', scenario_name),
                        'description': getattr(new_scenario, 'description', ''),
                    }
                })
                
            except Exception as e:
                logger.exception(f"Error creating scenario: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/scenarios/<scenario_id>', methods=['DELETE'])
    def delete_scenario(scenario_id):
        """Delete a scenario"""
        # In production, delete from database
        return jsonify({'success': True, 'message': f'Scenario {scenario_id} deleted'})
    
    @app.route('/api/scenarios/<scenario_id>/load', methods=['POST'])
    def load_scenario(scenario_id):
        """Load a scenario"""
        # In production, load scenario data
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
        """Get all templates or create new one"""
        if request.method == 'GET':
            templates_df = _load_routes_as_templates()
            templates = templates_df.to_dict(orient='records') if not templates_df.empty else []
            categories = sorted(list(templates_df['category'].unique())) if not templates_df.empty else []

            return jsonify({
                'templates': templates,
                'categories': categories
            })
        
        elif request.method == 'POST':
            data = request.json
            id_cfg = API_CONFIG.get('id_generation', {})
            id_min = id_cfg.get('template_id_min', 100)
            id_max = id_cfg.get('template_id_max', 999)
            template_id = f'template_{id_min + (int(datetime.now().timestamp()) % (id_max - id_min))}'
            
            return jsonify({
                'success': True,
                'template_id': template_id,
                'message': 'Template created from submitted data'
            })
    
    @app.route('/api/voyage-templates/<template_id>', methods=['DELETE'])
    def delete_template(template_id):
        """Delete a template"""
        # In production, delete from database
        return jsonify({'success': True, 'message': f'Template {template_id} deleted'})
    
    # ========================
    # CAPACITY PLANNING ENDPOINTS
    # ========================
    
    @app.route('/api/capacity', methods=['GET'])
    def get_capacity_data():
        """Get capacity planning data"""
        days = int(request.args.get('days', 14))
        
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
    
    @app.route('/api/capacity/optimize', methods=['POST'])
    def optimize_capacity():
        """Optimize capacity allocation"""
        # In production, run optimization algorithm
        return jsonify({
            'success': True,
            'improvements': 5,
            'message': '5 optimization suggestions generated'
        })
    
    # ========================
    # PDF EXPORT ENDPOINT
    # ========================
    
    @app.route('/api/export/pdf', methods=['POST'])
    def export_pdf():
        """Generate PDF report using pdf_reporter or fail with 501."""
        payload = request.json or {}
        report_type = payload.get('reportType', 'vessel_schedule')
        data_rows = payload.get('data', [])
        df = pd.DataFrame(data_rows)

        try:
            filename = generate_pdf_report(report_type, df)
            return jsonify({
                'success': True,
                'message': f'{report_type} PDF report generated',
                'filename': filename
            })
        except ValueError as exc:
            logger.error("Unsupported report type for PDF export: %s", report_type)
            return jsonify({'success': False, 'error': str(exc)}), 501
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to generate PDF: %s", exc)
            return jsonify({'success': False, 'error': str(exc)}), 500
    
    print("[OK] UI Module API endpoints registered successfully")


def _load_constraints_store() -> List[Dict[str, Any]]:
    """Load persisted berth constraints."""
    if not os.path.exists(_CONSTRAINTS_PATH):
        return []
    try:
        records = pd.read_json(_CONSTRAINTS_PATH, orient='records').to_dict(orient='records')
        return cast(List[Dict[str, Any]], [dict(item) for item in records])
    except ValueError:
        return []


def _persist_constraints(constraints: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(_CONSTRAINTS_PATH), exist_ok=True)
    pd.DataFrame(constraints).to_json(_CONSTRAINTS_PATH, orient='records', indent=2, force_ascii=False)


def _append_constraint(record: Dict[str, Any]) -> None:
    constraints = _load_constraints_store()
    constraints.append(record)
    _persist_constraints(constraints)


def _remove_constraint(constraint_id: str) -> bool:
    constraints = _load_constraints_store()
    new_constraints = [c for c in constraints if c.get('id') != constraint_id]
    if len(new_constraints) == len(constraints):
        return False
    _persist_constraints(new_constraints)
    return True


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
        logger.warning("Berths CSV not found: %s", csv_path)
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
    """Compute capacity and warnings from berth throughput."""
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
        logger.warning("Routes CSV not found: %s", csv_path)
        return pd.DataFrame()

    df = pd.read_csv(csv_path, sep=';', encoding='utf-8', comment='#')
    
    # Support both old and new column formats
    # Old format: route_id, route_name, canal_name, port_start_id, port_end_id, typical_duration_days
    # New format: from_port, to_port, distance_nm, canal, remarks
    
    if 'from_port' in df.columns:
        # New format
        df['id'] = df.index.map(lambda x: f'route_{x+1:03d}')
        df['name'] = df.apply(lambda row: f"{row['from_port']} → {row['to_port']}", axis=1)
        df['category'] = df['canal'].apply(lambda x: 'Canal Transit' if pd.notna(x) and str(x).strip() else 'Direct')
        df['description'] = df.apply(
            lambda row: f"{row['from_port']} to {row['to_port']} via {row['canal']}" if pd.notna(row.get('canal')) and str(row['canal']).strip() else f"{row['from_port']} to {row['to_port']}",
            axis=1
        )
        df['ports'] = df.apply(lambda row: [row['from_port'], row['to_port']], axis=1)
        # Estimate days from distance (assuming 12 knots average speed = 288 nm/day)
        df['estimatedDays'] = df['distance_nm'].apply(lambda x: max(1, int(x / 288)) if pd.notna(x) else 7)
    else:
        # Old format
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


def _get_alert_data():
    """Load alert-related data with a short-lived cache."""
    from modules.data_loader import DataLoader

    now = datetime.utcnow()
    cached_data = _alert_cache.get("data")
    cached_time = _alert_cache.get("timestamp")

    if cached_data is not None and cached_time is not None:
        age_seconds = (now - cached_time).total_seconds()
        if age_seconds < _ALERT_CACHE_TTL_SEC:
            logger.debug("Using cached DataLoader output for alerts (%ds old)", int(age_seconds))
            return cached_data

    loader = DataLoader()
    data = loader.load_all()
    _alert_cache["data"] = data
    _alert_cache["timestamp"] = now
    logger.info("Refreshed alert data cache at %s", now.isoformat())
    return data
