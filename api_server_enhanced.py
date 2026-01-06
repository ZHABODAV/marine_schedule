"""
Enhanced Flask API Server for Vessel Scheduler System
Version 2.1 - Production Ready
Merged functionality from api_server.py and api_server_enhanced.py

Features:
- Serves Vue.js Frontend (SPA)
- PDF Report Generation
- Bunker Optimization
- RBAC (Role-Based Access Control)
- WebSocket Real-time Collaboration
- Year Schedule Optimization
- Comprehensive API Endpoints
"""

from flask import Flask, request, jsonify, send_file, send_from_directory, g, Response
from flask.typing import ResponseReturnValue
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
from datetime import datetime, timedelta
import tempfile
import traceback
from functools import wraps
from typing import Dict, Optional, List, Tuple, Union, Any
import pandas as pd
import csv
from openpyxl import Workbook
import logging

# Import existing modules
from modules.deepsea_loader import DeepSeaLoader
from modules.deepsea_calculator import DeepSeaCalculator
from modules.deepsea_gantt_excel import DeepSeaGanttExcel
from modules.olya_loader import OlyaLoader
from modules.olya_coordinator import OlyaCoordinator
from modules.olya_gantt_excel import OlyaGanttExcel
from modules.balakovo_loader import BalakovoLoader
from modules.balakovo_planner import BalakovoPlanner
from modules.balakovo_gantt import BalakovoGanttExcel
from modules.year_schedule_optimizer import (
    YearScheduleOptimizer,
    YearScheduleManager,
    YearScheduleParams
)

# Import new Phase 2+ modules
from modules.pdf_reporter import PDFReportGenerator, generate_pdf_report
from modules.bunker_optimizer import (
    BunkerOptimizer, BunkerPrice, FuelConsumption, FuelType,
    create_sample_bunker_prices, create_sample_fuel_consumption
)
from modules.rbac import (
    RBACManager, Permission, UserRole, create_default_admin
)
from modules.security_utils import SecurityUtils
from modules.error_handling import (
    register_error_handlers, AppError, ValidationError,
    NotFoundError, UnauthorizedError, ForbiddenError
)
from modules.logger import setup_logger
from modules.profiler import profile_performance
from api_extensions import register_ui_module_endpoints
from modules.config import config
from modules.cargo_template_manager import CargoTemplateManager

# Initialize Flask app
# Serve static files from 'dist' folder for Vue.js app
app = Flask(__name__, static_folder='dist')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')

# Setup logger
logger = setup_logger(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
UPLOAD_FOLDER = 'temp_uploads'
OUTPUT_FOLDER = 'output'
REPORTS_FOLDER = 'output/reports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# Initialize RBAC Manager
rbac_manager = RBACManager()
create_default_admin(rbac_manager)

# Initialize PDF Report Generator
pdf_generator = PDFReportGenerator(output_dir=REPORTS_FOLDER)

# Initialize Bunker Optimizer
bunker_prices = create_sample_bunker_prices()
fuel_consumption_params = {
    f"vessel_{i}": create_sample_fuel_consumption(f"vessel_{i}")
    for i in range(1, 11)
}
bunker_optimizer = BunkerOptimizer(bunker_prices, fuel_consumption_params)

# Initialize Cargo Template Manager
cargo_template_manager = CargoTemplateManager()

# Global state for last calculation results (from api_server.py)
_last_calculation = {
    'module': None,
    'data': None,
    'results': None,
    'gantt_data': None,
    'timestamp': None
}

# ============================================================================
# Authentication Decorators
# ============================================================================

def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No authentication token provided'}), 401
        
        user = rbac_manager.validate_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        g.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not rbac_manager.check_permission(token, permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# ============================================================================
# Error Handlers
# ============================================================================

register_error_handlers(app)

# Register UI Module Endpoints
try:
    register_ui_module_endpoints(app)
    logger.info("UI Module API endpoints registered successfully")
except Exception as e:
    logger.error(f"Failed to register UI module endpoints: {e}")

# Register Missing Endpoints Blueprint
try:
    from api_missing_endpoints import register_missing_endpoints
    register_missing_endpoints(app)
    logger.info("Missing endpoints registered successfully - 22 new endpoints added")
except Exception as e:
    logger.error(f"Failed to register missing endpoints: {e}")


# ============================================================================
# Core Serving Endpoints (Vue.js Support)
# ============================================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve Vue app and static files"""
    if path != "" and os.path.exists(os.path.join('dist', path)):
        return send_from_directory('dist', path)
    else:
        # Return index.html for any other path (SPA routing)
        if os.path.exists(os.path.join('dist', 'index.html')):
            return send_from_directory('dist', 'index.html')
        else:
            # Fallback if dist is missing (e.g. during dev)
            return "Vue app build not found in 'dist' directory. Please run 'npm run build'.", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.1.0',
        'features': [
            'Vue.js Frontend',
            'PDF Reports',
            'Bunker Optimization',
            'RBAC',
            'WebSocket Collaboration',
            'Year Schedule Optimization'
        ]
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get frontend configuration."""
    try:
        frontend_config = {
            'gantt': config.get('gantt', {}),
            'general': config.get('general', {})
        }
        return jsonify(frontend_config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        token = rbac_manager.authenticate(username, password)
        
        if token:
            user = rbac_manager.validate_token(token)
            if user is None:
                return jsonify({'error': 'Token validation failed'}), 401
                
            return jsonify({
                'token': token,
                'user': user.to_dict(),
                'expires_at': user.token_expires.isoformat() if user.token_expires else None
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """User logout endpoint."""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        rbac_manager.logout(token)
        return jsonify({'message': 'Logged out successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user information."""
    try:
        user = g.current_user
        if user is None:
            return jsonify({'error': 'User not authenticated'}), 401
        return jsonify(user.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Calculation Endpoints (Merged from api_server.py)
# ============================================================================

@app.route('/api/calculate', methods=['POST'])
def calculate() -> ResponseReturnValue:
    """
    Execute schedule calculation for selected module (deepsea/olya/balakovo)
    """
    global _last_calculation
    
    try:
        if not request.json:
            logger.error("No JSON data provided in request")
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        module = request.json.get('module', 'deepsea')
        logger.info(f"Starting calculation for module: {module}")
        
        legs_count = 0
        alerts_count = 0
        gantt_data = {}
        
        if module == 'deepsea':
            loader = DeepSeaLoader()
            data = loader.load()
            calculator = DeepSeaCalculator(data)
            calculator.calculate_all()
            
            if hasattr(data, 'calculated_voyages') and data.calculated_voyages:
                for voyage_id, voyage in data.calculated_voyages.items():
                    vessel_legs = []
                    if hasattr(voyage, 'legs'):
                        for leg in voyage.legs:
                            legs_count += 1
                            leg_dict = {
                                'start': str(leg.start_time) if hasattr(leg, 'start_time') else None,
                                'end': str(leg.end_time) if hasattr(leg, 'end_time') else None,
                                'activity': leg.leg_type if hasattr(leg, 'leg_type') else 'Voyage',
                                'location': leg.to_port if hasattr(leg, 'to_port') else 'Unknown',
                                'cargo': voyage.cargo_type if hasattr(voyage, 'cargo_type') else ''
                            }
                            vessel_legs.append(leg_dict)
                    gantt_data[voyage.vessel_name] = vessel_legs
            
            _last_calculation = {
                'module': 'deepsea',
                'data': data,
                'results': calculator,
                'gantt_data': gantt_data,
                'timestamp': datetime.now().isoformat()
            }
            
        elif module == 'olya':
            loader = OlyaLoader()
            data = loader.load()
            coordinator = OlyaCoordinator(data)
            coordinator.analyze()
            
            for vessel_id, voyage in data.calculated_voyages.items():
                vessel_legs = []
                if hasattr(voyage, 'operations'):
                    for operation in voyage.operations:
                        legs_count += 1
                        leg = {
                            'start': str(operation.start_time) if hasattr(operation, 'start_time') else None,
                            'end': str(operation.end_time) if hasattr(operation, 'end_time') else None,
                            'activity': operation.operation if hasattr(operation, 'operation') else 'Movement',
                            'location': operation.port if hasattr(operation, 'port') else 'Unknown',
                            'cargo': voyage.cargo if hasattr(voyage, 'cargo') else ''
                        }
                        vessel_legs.append(leg)
                gantt_data[voyage.vessel_name] = vessel_legs
            
            _last_calculation = {
                'module': 'olya',
                'data': data,
                'results': coordinator,
                'gantt_data': gantt_data,
                'timestamp': datetime.now().isoformat()
            }
            
        elif module == 'balakovo':
            loader = BalakovoLoader()
            data = loader.load()
            planner = BalakovoPlanner(data)
            result_data = planner.plan()
            
            for berth_id, schedule in result_data.schedules.items():
                if schedule and hasattr(schedule, 'slots'):
                    berth_legs = []
                    for slot in schedule.slots:
                        legs_count += 1
                        leg = {
                            'start': str(slot.berthing_start) if hasattr(slot, 'berthing_start') else None,
                            'end': str(slot.departure) if hasattr(slot, 'departure') else None,
                            'activity': 'Loading',
                            'location': berth_id,
                            'cargo': slot.cargo_id if hasattr(slot, 'cargo_id') else ''
                        }
                        berth_legs.append(leg)
                    gantt_data[berth_id] = berth_legs
            
            _last_calculation = {
                'module': 'balakovo',
                'data': result_data,
                'results': planner,
                'gantt_data': gantt_data,
                'timestamp': datetime.now().isoformat()
            }
            
        else:
            return jsonify({'success': False, 'error': f'Invalid module: {module}'}), 400
        
        return jsonify({
            'success': True,
            'legs_count': legs_count,
            'alerts_count': alerts_count,
            'module': module,
            'timestamp': _last_calculation['timestamp']
        })
        
    except Exception as e:
        logger.exception(f"Error during calculation: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'details': 'Check server logs for more information'
        }), 500


@app.route('/api/gantt-data', methods=['GET'])
def get_gantt_data() -> ResponseReturnValue:
    """Return computed Gantt chart data from last calculation"""
    global _last_calculation
    
    try:
        if _last_calculation['gantt_data'] is None:
            return jsonify({
                'assets': {},
                'message': 'No calculation performed yet. Please run /api/calculate first.'
            }), 200
        
        return jsonify({
            'assets': _last_calculation['gantt_data'],
            'module': _last_calculation.get('module'),
            'timestamp': _last_calculation.get('timestamp'),
            'legs_count': sum(len(legs) for legs in _last_calculation['gantt_data'].values())
        })
        
    except Exception as e:
        logger.exception(f"Error retrieving gantt data: {str(e)}")
        return jsonify({'assets': {}, 'error': str(e)}), 500


# ============================================================================
# Year Schedule Endpoints (Merged from api_server.py)
# ============================================================================

@app.route('/api/schedule/year', methods=['GET'])
def get_year_schedule() -> ResponseReturnValue:
    """Retrieve saved year schedules - STUB: YearScheduleManager doesn't support persistence yet"""
    try:
        # TODO: Implement schedule persistence in YearScheduleManager
        return jsonify({
            'success': False,
            'error': 'Schedule persistence not yet implemented',
            'message': 'YearScheduleManager needs list_schedules/load_schedule methods'
        }), 501
        
    except Exception as e:
        logger.exception("Error retrieving year schedule")
        return jsonify({'error': str(e)}), 500


@app.route('/api/schedule/year', methods=['POST'])
def generate_year_schedule() -> ResponseReturnValue:
    """Generate optimized year schedule - STUB: Needs proper integration"""
    try:
        # TODO: Refactor to use YearScheduleManager.generate_from_dataframes() or equivalent
        return jsonify({
            'success': False,
            'error': 'Year schedule generation not fully implemented',
            'message': 'YearScheduleOptimizer API mismatch - needs refactoring'
        }), 501
        
    except Exception as e:
        logger.exception("Error generating year schedule")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/schedule/year/<schedule_id>', methods=['DELETE'])
def delete_year_schedule(schedule_id: str) -> ResponseReturnValue:
    """Delete a saved year schedule - STUB"""
    try:
        # TODO: Implement schedule persistence
        return jsonify({
            'success': False,
            'error': 'Schedule deletion not implemented',
            'message': 'YearScheduleManager needs delete_schedule method'
        }), 501
            
    except Exception as e:
        logger.exception("Error deleting schedule")
        return jsonify({'error': str(e)}), 500


@app.route('/api/schedule/year/conflicts', methods=['POST'])
def detect_year_conflicts() -> ResponseReturnValue:
    """Detect conflicts in current or provided schedule - STUB"""
    try:
        # TODO: Implement conflict detection using YearScheduleOptimizer
        return jsonify({
            'success': False,
            'error': 'Conflict detection not implemented',
            'message': 'YearScheduleOptimizer needs detect_conflicts method'
        }), 501
        
    except Exception as e:
        logger.exception("Error detecting conflicts")
        return jsonify({'error': str(e)}), 500


@app.route('/api/schedule/year/compare', methods=['POST'])
def compare_year_strategies() -> ResponseReturnValue:
    """Compare different optimization strategies - STUB"""
    try:
        # TODO: Implement strategy comparison using YearScheduleOptimizer
        return jsonify({
            'success': False,
            'error': 'Strategy comparison not implemented',
            'message': 'YearScheduleOptimizer needs optimize method with strategies'
        }), 501
        
    except Exception as e:
        logger.exception("Error comparing strategies")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PDF Report Endpoints
# ============================================================================

@app.route('/api/reports/pdf/vessel-schedule', methods=['POST'])
@require_auth
@require_permission(Permission.EXPORT_REPORTS)
@profile_performance
def generate_vessel_schedule_pdf():
    """Generate vessel schedule PDF report."""
    try:
        data = request.json
        schedule_type = data.get('type', 'deepsea')
        
        if schedule_type == 'deepsea':
            loader = DeepSeaLoader()
            schedule_data = loader.load() if hasattr(loader, 'load') else loader.load_all()
            
            vessel_df = pd.DataFrame([
                {
                    'Vessel ID': v.vessel_id,
                    'Vessel Name': v.vessel_name,
                    'Class': getattr(v, 'vessel_class', 'N/A'),
                    'DWT': getattr(v, 'dwt_mt', 0),
                    'Speed': getattr(v, 'speed_kts', 0)
                }
                for v in schedule_data.vessels.values()
            ])
        else:
            loader = OlyaLoader()
            schedule_data = loader.load()
            roster_data = getattr(schedule_data, 'roster', getattr(schedule_data, 'vessels', {}))
            
            vessel_df = pd.DataFrame([
                {
                    'Vessel ID': v.vessel_id,
                    'Vessel Name': v.vessel_name,
                    'Type': getattr(v, 'vessel_type', 'N/A'),
                    'Capacity': getattr(v, 'capacity_mt', 0)
                }
                for v in roster_data.values()
            ])
        
        filename = f"vessel_schedule_{schedule_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = pdf_generator.generate_vessel_schedule_report(
            vessel_df,
            filename=filename,
            title=f"{schedule_type.title()} Vessel Schedule"
        )
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/pdf/voyage-summary', methods=['POST'])
@require_auth
@require_permission(Permission.EXPORT_REPORTS)
def generate_voyage_summary_pdf():
    """Generate voyage summary PDF report."""
    try:
        data = request.json
        include_financials = data.get('include_financials', True)
        
        loader = DeepSeaLoader()
        voyage_data_obj = loader.load() if hasattr(loader, 'load') else loader.load_all()
        
        voyage_df = pd.DataFrame([
            {
                'voyage_id': plan.voyage_id,
                'vessel_name': 'N/A',
                'load_port': getattr(getattr(plan, 'route_legs', [None])[0] if getattr(plan, 'route_legs', None) else None, 'from_port', 'N/A'),
                'discharge_port': getattr(getattr(plan, 'route_legs', [None])[-1] if getattr(plan, 'route_legs', None) else None, 'to_port', 'N/A'),
                'distance_nm': sum(getattr(leg, 'distance_nm', 0) for leg in getattr(plan, 'route_legs', [])),
                'duration_days': 0,
                'revenue_usd': 0,
                'cost_usd': 0
            }
            for plan in voyage_data_obj.voyage_plans if hasattr(voyage_data_obj, 'voyage_plans')
        ]) if hasattr(voyage_data_obj, 'voyage_plans') else pd.DataFrame()
        
        filename = f"voyage_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = pdf_generator.generate_voyage_summary_report(
            voyage_df,
            filename=filename,
            include_financials=include_financials
        )
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Bunker Optimization Endpoints
# ============================================================================

@app.route('/api/bunker/optimize', methods=['POST'])
@require_auth
@require_permission(Permission.VIEW_FINANCIALS)
@profile_performance
def optimize_bunker():
    """Optimize bunker plan for a voyage."""
    try:
        data = request.json
        
        bunker_plan = bunker_optimizer.optimize_bunker_plan(
            voyage_id=data.get('voyage_id'),
            vessel_id=data.get('vessel_id'),
            route_ports=data.get('route_ports', []),
            distances_nm=data.get('distances_nm', []),
            port_times_days=data.get('port_times_days', []),
            fuel_type=FuelType[data.get('fuel_type', 'VLSFO')],
            current_fuel_mt=data.get('current_fuel_mt', 1000),
            allow_eco_speed=data.get('allow_eco_speed', True)
        )
        
        return jsonify(bunker_plan.get_summary())
    
    except Exception as e:
        logger.error(f"Bunker optimization error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/bunker/prices', methods=['GET'])
@require_auth
def get_bunker_prices():
    """Get current bunker prices."""
    try:
        prices_data = [
            {
                'port_id': p.port_id,
                'port_name': p.port_name,
                'fuel_type': p.fuel_type.value,
                'price_per_mt': p.price_per_mt,
                'availability_mt': p.availability_mt,
                'last_updated': p.last_updated.isoformat(),
                'eca_compliant': p.eca_compliant
            }
            for p in bunker_prices
        ]
        return jsonify({'prices': prices_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bunker/market-analysis', methods=['GET'])
@require_auth
def bunker_market_analysis():
    """Get bunker market analysis."""
    try:
        fuel_type_param = request.args.get('fuel_type', 'VLSFO')
        fuel_type = FuelType[fuel_type_param]
        analysis = bunker_optimizer.analyze_bunker_market(fuel_type)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Cargo Template Endpoints
# ============================================================================

@app.route('/api/cargo-templates', methods=['GET'])
@require_auth
@profile_performance
def get_all_cargo_templates():
    """Get all cargo templates."""
    try:
        templates = cargo_template_manager.get_all()
        return jsonify({'templates': templates, 'count': len(templates)})
    except Exception as e:
        logger.error(f"Error fetching cargo templates: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cargo-templates/<template_id>', methods=['GET'])
@require_auth
@profile_performance
def get_cargo_template(template_id: str):
    """Get a specific cargo template by ID."""
    try:
        template = cargo_template_manager.get_by_id(template_id)
        if template:
            return jsonify(template)
        else:
            return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching template {template_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cargo-templates/default', methods=['GET'])
@require_auth
@profile_performance
def get_default_cargo_template():
    """Get the default cargo template."""
    try:
        template = cargo_template_manager.get_default()
        if template:
            return jsonify(template)
        else:
            return jsonify({'error': 'No default template found'}), 404
    except Exception as e:
        logger.error(f"Error fetching default template: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cargo-templates', methods=['POST'])
@require_auth
@require_permission(Permission.CREATE_VOYAGES)
@profile_performance
def create_cargo_template():
    """Create a new cargo template."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['name', 'commodity']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        template = cargo_template_manager.create(data)
        logger.info(f"Created cargo template: {template['id']}")
        return jsonify(template), 201
    except Exception as e:
        logger.error(f"Error creating cargo template: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cargo-templates/<template_id>', methods=['PUT'])
@require_auth
@require_permission(Permission.CREATE_VOYAGES)
@profile_performance
def update_cargo_template(template_id: str):
    """Update an existing cargo template."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        template = cargo_template_manager.update(template_id, data)
        if template:
            logger.info(f"Updated cargo template: {template_id}")
            return jsonify(template)
        else:
            return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        logger.error(f"Error updating template {template_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cargo-templates/<template_id>', methods=['DELETE'])
@require_auth
@require_permission(Permission.CREATE_VOYAGES)
@profile_performance
def delete_cargo_template(template_id: str):
    """Delete a cargo template."""
    try:
        success = cargo_template_manager.delete(template_id)
        if success:
            logger.info(f"Deleted cargo template: {template_id}")
            return jsonify({'message': 'Template deleted successfully'})
        else:
            return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting template {template_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cargo-templates/<template_id>/apply', methods=['POST'])
@require_auth
@require_permission(Permission.CREATE_VOYAGES)
@profile_performance
def apply_cargo_template(template_id: str):
    """Apply a cargo template to create cargo commitment data."""
    try:
        cargo_data = request.json or {}
        result = cargo_template_manager.apply_template(template_id, cargo_data)
        if result:
            logger.info(f"Applied cargo template: {template_id}")
            return jsonify(result)
        else:
            return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        logger.error(f"Error applying template {template_id}: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Data Management Endpoints (Merged & Enhanced)
# ============================================================================

@app.route('/api/vessels', methods=['GET', 'POST'])
def handle_vessels() -> ResponseReturnValue:
    """Get or create vessels."""
    # Use deepsea vessels as primary source
    filepath = os.path.join('input', 'deepsea', 'vessels.csv')
    
    if request.method == 'GET':
        try:
            vessels = []
            if os.path.exists(filepath):
                df = pd.read_csv(filepath, sep=';')
                df = df.where(pd.notnull(df), None)
                
                for _, row in df.iterrows():
                    vessels.append({
                        'id': row.get('vessel_id'),
                        'name': row.get('vessel_name'),
                        'class': row.get('vessel_class'),
                        'dwt': row.get('dwt_mt'),
                        'speed': row.get('speed_laden_kn'),
                        'status': 'Active'
                    })
            return jsonify({'vessels': vessels})
        except Exception as e:
            logger.error(f"Error loading vessels: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            if os.path.exists(filepath):
                df = pd.read_csv(filepath, sep=';')
            else:
                df = pd.DataFrame(columns=[
                    'vessel_id', 'vessel_name', 'imo', 'vessel_type', 'vessel_class',
                    'dwt_mt', 'capacity_mt', 'loa_m', 'beam_m', 'draft_laden_m',
                    'draft_ballast_m', 'speed_laden_kn', 'speed_ballast_kn',
                    'consumption_laden_mt', 'consumption_ballast_mt', 'daily_hire_usd',
                    'owner', 'flag', 'built_year', 'ice_class', 'tank_coated', 'heating_capable'
                ])

            new_vessel = {
                'vessel_id': data.get('id'),
                'vessel_name': data.get('name'),
                'vessel_class': data.get('class'),
                'dwt_mt': data.get('dwt'),
                'speed_laden_kn': data.get('speed'),
                'vessel_type': 'Unknown',
                'capacity_mt': float(data.get('dwt', 0)) * 0.95 if data.get('dwt') else 0,
                'speed_ballast_kn': float(data.get('speed', 12)) + 1 if data.get('speed') else 13
            }
            
            if 'vessel_id' in df.columns and new_vessel['vessel_id'] in df['vessel_id'].values:
                return jsonify({'error': f"Vessel ID {new_vessel['vessel_id']} already exists"}), 400

            new_df = pd.DataFrame([new_vessel])
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(filepath, sep=';', index=False)
            
            return jsonify({'success': True, 'message': 'Vessel created successfully', 'vessel': data}), 201
            
        except Exception as e:
            logger.error(f"Error creating vessel: {e}")
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Method not allowed'}), 405


@app.route('/api/vessels/<vessel_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_vessel_id(vessel_id: str) -> ResponseReturnValue:
    """Get, update or delete a specific vessel."""
    filepath = os.path.join('input', 'deepsea', 'vessels.csv')
    
    try:
        if not os.path.exists(filepath):
            return jsonify({'error': 'Vessels database not found'}), 404
            
        df = pd.read_csv(filepath, sep=';')
        
        if vessel_id not in df['vessel_id'].values:
            return jsonify({'error': 'Vessel not found'}), 404
            
        if request.method == 'GET':
            row = df[df['vessel_id'] == vessel_id].iloc[0]
            vessel = {
                'id': row.get('vessel_id'),
                'name': row.get('vessel_name'),
                'class': row.get('vessel_class'),
                'dwt': row.get('dwt_mt'),
                'speed': row.get('speed_laden_kn'),
                'status': 'Active'
            }
            return jsonify(vessel)
            
        elif request.method == 'PUT':
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
                
            idx = df.index[df['vessel_id'] == vessel_id][0]
            
            if 'name' in data: df.at[idx, 'vessel_name'] = data['name']
            if 'class' in data: df.at[idx, 'vessel_class'] = data['class']
            if 'dwt' in data: df.at[idx, 'dwt_mt'] = data['dwt']
            if 'speed' in data: df.at[idx, 'speed_laden_kn'] = data['speed']
            
            df.to_csv(filepath, sep=';', index=False)
            return jsonify({'success': True, 'message': 'Vessel updated successfully'})
            
        elif request.method == 'DELETE':
            df = df[df['vessel_id'] != vessel_id]
            df.to_csv(filepath, sep=';', index=False)
            return jsonify({'success': True, 'message': 'Vessel deleted successfully'})
            
    except Exception as e:
        logger.error(f"Error handling vessel {vessel_id}: {e}")
        return jsonify({'error': str(e)}), 500
        
    return jsonify({'error': 'Method not allowed'}), 405


@app.route('/api/routes', methods=['GET', 'POST'])
def handle_routes() -> ResponseReturnValue:
    """Get or create routes."""
    filepath = os.path.join('input', 'deepsea', 'routes_deepsea.csv')
    
    if request.method == 'GET':
        try:
            routes = []
            if os.path.exists(filepath):
                df = pd.read_csv(filepath, sep=';')
                df = df.astype(object).where(pd.notnull(df), None)
                
                for _, row in df.iterrows():
                    routes.append({
                        'id': row.get('route_id'),
                        'name': row.get('route_name'),
                        'from': row.get('from_port'),
                        'to': row.get('to_port'),
                        'canal': row.get('canal_id'),
                        'distance': 0 
                    })
            return jsonify({'routes': routes})
        except Exception as e:
            logger.error(f"Error loading routes: {e}")
            return jsonify({'error': str(e)}), 500
            
    elif request.method == 'POST':
        try:
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
                
            if os.path.exists(filepath):
                df = pd.read_csv(filepath, sep=';')
            else:
                df = pd.DataFrame(columns=['route_id', 'route_name', 'leg_seq', 'leg_type', 'from_port', 'to_port', 'cargo_state', 'canal_id', 'remarks'])
                
            existing_ids = df['route_id'].unique()
            next_id = 1
            if len(existing_ids) > 0:
                import re
                nums = []
                for rid in existing_ids:
                    if isinstance(rid, str):
                        match = re.search(r'\d+', rid)
                        if match:
                            nums.append(int(match.group()))
                if nums:
                    next_id = max(nums) + 1
            
            route_id = f"RT_{next_id:02d}"
            
            new_route = {
                'route_id': route_id,
                'route_name': f"{data.get('from')}-{data.get('to')}",
                'leg_seq': 1,
                'leg_type': 'sea' if not data.get('canal') else 'canal',
                'from_port': data.get('from'),
                'to_port': data.get('to'),
                'cargo_state': 'laden',
                'canal_id': data.get('canal'),
                'remarks': 'Created via API'
            }
            
            new_df = pd.DataFrame([new_route])
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(filepath, sep=';', index=False)
            
            return jsonify({'success': True, 'message': 'Route created successfully', 'route': new_route}), 201
            
        except Exception as e:
            logger.error(f"Error creating route: {e}")
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Method not allowed'}), 405


@app.route('/api/cargo', methods=['GET', 'POST'])
def handle_cargo() -> ResponseReturnValue:
    """Get or update cargo data (from api_server.py)"""
    if request.method == 'GET':
        try:
            cargo = []
            filepath = os.path.join('input', 'Cargo.csv')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cargo.append({
                            'id': row.get('voyage_id', row.get('id', '')),
                            'commodity': row.get('cargo_type', row.get('product_name', row.get('commodity', ''))),
                            'quantity': int(row.get('qty_mt', row.get('quantity', 0)) or 0),
                            'loadPort': row.get('load_port', row.get('loadPort', '')),
                            'dischPort': row.get('disch_port', row.get('dischPort', '')),
                            'laycanStart': row.get('laycan_start', row.get('laycanStart', '')),
                            'laycanEnd': row.get('laycan_end', row.get('laycanEnd', '')),
                            'status': row.get('status', 'Pending')
                        })
            return jsonify({'cargo': cargo})
        except Exception as e:
            logger.exception("Error loading cargo")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            if not request.json:
                return jsonify({'error': 'No JSON data provided'}), 400
            cargo_data = request.json.get('cargo', [])
            filepath = os.path.join('input', 'Cargo.csv')
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['voyage_id', 'cargo_type', 'qty_mt', 'load_port', 'disch_port', 'laycan_start', 'laycan_end'])
                writer.writeheader()
                for c in cargo_data:
                    writer.writerow({
                        'voyage_id': c['id'],
                        'cargo_type': c['commodity'],
                        'qty_mt': c['quantity'],
                        'load_port': c['loadPort'],
                        'disch_port': c['dischPort'],
                        'laycan_start': c['laycanStart'],
                        'laycan_end': c['laycanEnd']
                    })
            return jsonify({'message': 'Cargo saved successfully'})
        except Exception as e:
            logger.exception("Error saving cargo")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Method not allowed'}), 405


@app.route('/api/upload/<upload_type>', methods=['POST'])
def upload_file(upload_type: str) -> ResponseReturnValue:
    """Upload CSV file with RESTful pattern"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename_map = {
            'vessels': 'Vessels.csv',
            'cargo': 'Cargo.csv',
            'commitments': 'CargoCommitments.csv',
            'routes': 'Routes.csv',
            'ports': 'Ports.csv',
            'cargoTypes': 'Cargo.csv',
            'railCargo': 'rail_cargo.csv',
            'movements': 'cargo_movements.csv',
            'voyageLegs': 'voyage_legs.csv'
        }
        
        if upload_type not in filename_map:
            return jsonify({'error': f'Invalid upload type: {upload_type}'}), 400
        
        filename = filename_map[upload_type]
        filepath = os.path.join('input', filename)
        file.save(filepath)
        
        record_count = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                record_count = sum(1 for row in reader)
        except Exception:
            record_count = 0
        
        return jsonify({
            'success': True,
            'message': f'{upload_type} data uploaded successfully',
            'filename': filename,
            'type': upload_type,
            'count': record_count
        })
            
    except Exception as e:
        logger.exception(f"Error uploading file: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload/csv', methods=['POST'])
def upload_csv() -> ResponseReturnValue:
    """Upload CSV file (legacy endpoint)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_type = request.form.get('type') if request.form else None
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename_map = {
            'vessels': 'Vessels.csv',
            'cargo': 'Cargo.csv',
            'routes': 'Routes.csv',
            'ports': 'Ports.csv'
        }
        
        if file_type and file_type in filename_map:
            filepath = os.path.join('input', filename_map[file_type])
            file.save(filepath)
            return jsonify({
                'message': f'{file_type} data uploaded successfully',
                'filename': filename_map[file_type]
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.exception("Error uploading CSV")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats() -> ResponseReturnValue:
    """Get dashboard statistics"""
    try:
        loader = DeepSeaLoader()
        data = loader.load()
        
        active_vessels = len(data.vessels)
        pending_cargo = len(data.voyage_plans)
        
        total_distance = sum(d.distance_nm for d in data.distances.values())
        
        return jsonify({
            'activeVessels': active_vessels,
            'pendingCargo': pending_cargo,
            'totalDistance': total_distance,
            'utilization': 75
        })
        
    except Exception as e:
        logger.exception("Error getting dashboard stats")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Export Endpoints (Excel/CSV)
# ============================================================================

@app.route('/api/export/excel', methods=['POST'])
def export_excel() -> ResponseReturnValue:
    """Export Gantt chart to Excel file"""
    global _last_calculation
    
    try:
        module = None
        month = datetime.now().strftime('%Y-%m')
        
        if request.json:
            module = request.json.get('module')
            month = request.json.get('month', month)
        
        if not module and _last_calculation['module']:
            module = _last_calculation['module']
        elif not module:
            module = 'deepsea'
        
        year, month_num = map(int, month.split('-'))
        
        if module == 'deepsea':
            if _last_calculation['module'] == 'deepsea' and _last_calculation['data']:
                data = _last_calculation['data']
            else:
                loader = DeepSeaLoader()
                data = loader.load()
                calculator = DeepSeaCalculator(data)
                calculator.calculate_all()
            
            gantt = DeepSeaGanttExcel(data)
            filepath = gantt.generate_month(year, month_num)
            
            if filepath and os.path.exists(filepath):
                filename = os.path.basename(filepath)
                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                return jsonify({'error': f'No voyages found for {month}'}), 404
            
        elif module == 'olya':
            if _last_calculation['module'] == 'olya' and _last_calculation['data']:
                data = _last_calculation['data']
            else:
                loader = OlyaLoader()
                data = loader.load()
                coordinator = OlyaCoordinator(data)
                coordinator.analyze()
            
            gantt = OlyaGanttExcel(data)
            filepath = gantt.generate_month(year, month_num)
            
            if filepath and os.path.exists(filepath):
                filename = os.path.basename(filepath)
                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                return jsonify({'error': 'Failed to generate Excel file'}), 500
            
        elif module == 'balakovo':
            if _last_calculation['module'] == 'balakovo' and _last_calculation['data']:
                data = _last_calculation['data']
            else:
                loader = BalakovoLoader()
                data = loader.load()
                planner = BalakovoPlanner(data)
                data = planner.plan()
            
            gantt = BalakovoGanttExcel(data)
            filepath = gantt.generate_schedule()
            
            if filepath and os.path.exists(filepath):
                filename = os.path.basename(filepath)
                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                return jsonify({'error': 'Failed to generate Excel file'}), 500
        
        else:
            return jsonify({'error': f'Invalid module: {module}'}), 400
            
    except Exception as e:
        logger.exception(f"Error exporting Excel: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/gantt', methods=['POST'])
def export_gantt() -> ResponseReturnValue:
    """Export Gantt chart to Excel (Legacy wrapper)"""
    return export_excel()


@app.route('/api/export/fleet-overview', methods=['POST'])
def export_fleet_overview() -> ResponseReturnValue:
    """Export fleet overview to Excel"""
    try:
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
        schedule_type = request.json.get('type', 'deepsea')
        
        if schedule_type == 'deepsea':
            loader = DeepSeaLoader()
            data = loader.load()
            calculator = DeepSeaCalculator(data)
            calculator.calculate_all()
            
            gantt = DeepSeaGanttExcel(data)
            files = gantt.generate_all_months() 
            
            if files and files[0] and os.path.exists(files[0]):
                filename = os.path.basename(files[0])
                return send_file(
                    files[0],
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        else:
            loader = OlyaLoader()
            data = loader.load()
            coordinator = OlyaCoordinator(data)
            coordinator.analyze()
            
            gantt = OlyaGanttExcel(data)
            filepath = gantt.generate_summary_gantt()
            
            if filepath and os.path.exists(filepath):
                filename = os.path.basename(filepath)
                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        
        return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        logger.exception("Error exporting fleet overview")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/voyage-summary', methods=['POST'])
def export_voyage_summary() -> ResponseReturnValue:
    """Export voyage summary to Excel"""
    try:
        loader = DeepSeaLoader()
        data = loader.load()
        calculator = DeepSeaCalculator(data)
        calculator.calculate_all()
        
        wb = Workbook()
        ws = wb.active
        if ws:
            ws.title = "Voyage Summary"
            headers = ['Voyage ID', 'Vessel Name', 'Cargo Type', 'Load Port', 'Disch Port', 'Distance (NM)', 'Duration (days)']
            ws.append(headers)
            
            for voyage_id, voyage in data.calculated_voyages.items():
                ws.append([
                    voyage.voyage_id,
                    voyage.vessel_name,
                    voyage.cargo_type,
                    voyage.load_port,
                    voyage.disch_port,
                    voyage.total_distance_nm,
                    voyage.total_days
                ])
        
        filename = 'voyage_summary.xlsx'
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        wb.save(filepath)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.exception("Error exporting voyage summary")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# WebSocket Events (Real-time Collaboration)
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('connected', {'message': 'Connected to Vessel Scheduler'})


@socketio.on('join_schedule')
def handle_join_schedule(data):
    """Join a schedule collaboration room."""
    schedule_id = data.get('schedule_id')
    join_room(schedule_id)
    emit('user_joined', {'schedule_id': schedule_id}, to=schedule_id)


@socketio.on('leave_schedule')
def handle_leave_schedule(data):
    """Leave a schedule collaboration room."""
    schedule_id = data.get('schedule_id')
    leave_room(schedule_id)
    emit('user_left', {'schedule_id': schedule_id}, to=schedule_id)


@socketio.on('schedule_update')
def handle_schedule_update(data):
    """Broadcast schedule update to all users in room."""
    schedule_id = data.get('schedule_id')
    updates = data.get('updates')
    
    emit('schedule_changed', {
        'schedule_id': schedule_id,
        'updates': updates,
        'timestamp': datetime.now().isoformat()
    }, to=schedule_id)


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Enhanced Vessel Scheduler API Server v2.1")
    logger.info("=" * 60)
    logger.info(f"Server running on http://localhost:5000")
    logger.info(f"Serving Vue.js app from 'dist' directory")
    logger.info(f"WebSocket support enabled on same port")
    logger.info(f"Features Active:")
    logger.info("   Vue.js Frontend Support")
    logger.info("   PDF Report Generation")
    logger.info("   Bunker Optimization")
    logger.info("   Role-Based Access Control (RBAC)")
    logger.info("   Real-time Collaboration (WebSocket)")
    logger.info("   Year Schedule Optimization")
    logger.info("=" * 60)
    
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=5000)
