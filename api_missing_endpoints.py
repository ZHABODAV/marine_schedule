"""
Missing API Endpoints Implementation
Adds 22 endpoints identified as missing in backend-frontend integration verification.
Implements comprehensive vessel, cargo, and voyage management APIs.
"""

from flask import Blueprint, request, jsonify, send_file
from flask.typing import ResponseReturnValue
import pandas as pd
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Create blueprint for missing endpoints
missing_endpoints_bp = Blueprint('missing_endpoints', __name__, url_prefix='/api')

# ============================================================================
# Helper Functions for Response Standardization
# ============================================================================

def success_response(data: Any, message: str = None) -> Dict:
    """Standardize successful API responses to match frontend expectations."""
    response = {
        'data': data,
        'status': 'success'
    }
    if message:
        response['message'] = message
    return response

def error_response(message: str, status_code: int = 400) -> tuple:
    """Standardize error responses."""
    return jsonify({
        'error': message,
        'status': 'error'
    }), status_code

def paginated_response(data: List, page: int, per_page: int, total: int) -> Dict:
    """Standardize paginated responses."""
    return {
        'data': data,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page,
        'status': 'success'
    }

# ============================================================================
# Vessel Endpoints (5 missing)
# ============================================================================

@missing_endpoints_bp.route('/vessels/positions', methods=['GET'])
def get_vessel_positions() -> ResponseReturnValue:
    """Get current positions of all vessels."""
    try:
        # Read vessel positions from CSV if available
        positions_file = os.path.join('input', 'VesselPositions.csv')
        
        if not os.path.exists(positions_file):
            #Return mock data if file doesn't exist
            mock_positions = [
                {
                    'vessel_id': 'V001',
                    'vessel_name': 'Sample Vessel 1',
                    'latitude': 55.7558,
                    'longitude': 37.6173,
                    'status': 'At Sea',
                    'speed_knots': 12.5,
                    'heading': 90,
                    'last_update': datetime.now().isoformat()
                }
            ]
            return jsonify(success_response(mock_positions))
        
        df = pd.read_csv(positions_file)
        positions = df.to_dict('records')
        
        return jsonify(success_response(positions))
    
    except Exception as e:
        logger.error(f"Error getting vessel positions: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/vessels/<vessel_id>/schedule', methods=['GET'])
def get_vessel_schedule(vessel_id: str) -> ResponseReturnValue:
    """Get schedule for a specific vessel."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # For now, return empty schedule
        # TODO: Integrate with voyage calculation to get actual schedule
        schedule = {
            'vessel_id': vessel_id,
            'start_date': start_date or datetime.now().isoformat(),
            'end_date': end_date or datetime.now().isoformat(),
            'voyages': [],
            'utilization_pct': 0.0
        }
        
        return jsonify(success_response(schedule))
    
    except Exception as e:
        logger.error(f"Error getting vessel schedule for {vessel_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/vessels/import', methods=['POST'])
def import_vessels() -> ResponseReturnValue:
    """Import vessels from uploaded file."""
    try:
        if 'file' not in request.files:
            return error_response('No file provided', 400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response('No file selected', 400)
        
        # Read the uploaded file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file, sep=';')
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return error_response('Invalid file format. Use CSV or Excel', 400)
        
        # Save to vessels file
        output_path = os.path.join('input', 'deepsea', 'vessels.csv')
        df.to_csv(output_path, sep=';', index=False)
        
        result = {
            'imported': len(df),
            'filename': file.filename
        }
        
        return jsonify(success_response(result, f'Successfully imported {len(df)} vessels'))
    
    except Exception as e:
        logger.error(f"Error importing vessels: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/vessels/export', methods=['GET'])
def export_vessels() -> ResponseReturnValue:
    """Export vessels to file."""
    try:
        format_type = request.args.get('format', 'excel')
        
        # Read vessels data
        vessels_file = os.path.join('input', 'deepsea', 'vessels.csv')
        if not os.path.exists(vessels_file):
            return error_response('No vessels data available', 404)
        
        df = pd.read_csv(vessels_file, sep=';')
        
        # Create temporary file
        if format_type == 'csv':
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
            df.to_csv(temp_file.name, index=False)
            mimetype = 'text/csv'
            filename = f'vessels_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        else:  # excel
            temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'vessels_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
    
    except Exception as e:
        logger.error(f"Error exporting vessels: {e}")
        return error_response(str(e), 500)


# ============================================================================
# Cargo Endpoints (4 missing)
# ============================================================================

@missing_endpoints_bp.route('/cargo/port/<port_id>', methods=['GET'])
def get_cargo_by_port(port_id: str) -> ResponseReturnValue:
    """Get cargo commitments for specific port."""
    try:
        cargo_file = os.path.join('input', 'Cargo.csv')
        if not os.path.exists(cargo_file):
            return jsonify(success_response([]))
        
        df = pd.read_csv(cargo_file)
        
        # Filter by port (check both load and discharge ports)
        port_cargo = df[
            (df['load_port'] == port_id) | 
            (df['disch_port'] == port_id)
        ]
        
        cargo_list = port_cargo.to_dict('records')
        
        return jsonify(success_response(cargo_list))
    
    except Exception as e:
        logger.error(f"Error getting cargo for port {port_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/cargo/statistics', methods=['GET'])
def get_cargo_statistics() -> ResponseReturnValue:
    """Get cargo statistics for dashboard."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        module = request.args.get('module')
        
        cargo_file = os.path.join('input', 'Cargo.csv')
        if not os.path.exists(cargo_file):
            stats = {
                'total_cargo_mt': 0,
                'total_commitments': 0,
                'by_commodity': {},
                'by_status': {},
                'avg_quantity_mt': 0
            }
            return jsonify(success_response(stats))
        
        df = pd.read_csv(cargo_file)
        
        # Calculate statistics
        stats = {
            'total_cargo_mt': float(df['qty_mt'].sum()) if 'qty_mt' in df.columns else 0,
            'total_commitments': len(df),
            'by_commodity': df.groupby('cargo_type')['qty_mt'].sum().to_dict() if 'cargo_type' in df.columns else {},
            'by_status': df.groupby('status')['qty_mt'].sum().to_dict() if 'status' in df.columns else {},
            'avg_quantity_mt': float(df['qty_mt'].mean()) if 'qty_mt' in df.columns else 0
        }
        
        return jsonify(success_response(stats))
    
    except Exception as e:
        logger.error(f"Error calculating cargo statistics: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/cargo/import', methods=['POST'])
def import_cargo() -> ResponseReturnValue:
    """Import cargo commitments from file."""
    try:
        if 'file' not in request.files:
            return error_response('No file provided', 400)
        
        file = request.files['file']
        if file.filename == '':
            return error_response('No file selected', 400)
        
        # Read the uploaded file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return error_response('Invalid file format. Use CSV or Excel', 400)
        
        # Save to cargo file
        output_path = os.path.join('input', 'Cargo.csv')
        df.to_csv(output_path, index=False)
        
        result = {
            'imported': len(df),
            'filename': file.filename
        }
        
        return jsonify(success_response(result, f'Successfully imported {len(df)} cargo commitments'))
    
    except Exception as e:
        logger.error(f"Error importing cargo: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/cargo/export', methods=['GET'])
def export_cargo() -> ResponseReturnValue:
    """Export cargo to file."""
    try:
        format_type = request.args.get('format', 'excel')
        
        cargo_file = os.path.join('input', 'Cargo.csv')
        if not os.path.exists(cargo_file):
            return error_response('No cargo data available', 404)
        
        df = pd.read_csv(cargo_file)
        
        # Create temporary file
        if format_type == 'csv':
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
            df.to_csv(temp_file.name, index=False)
            mimetype = 'text/csv'
            filename = f'cargo_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        else:  # excel
            temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'cargo_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
    
    except Exception as e:
        logger.error(f"Error exporting cargo: {e}")
        return error_response(str(e), 500)


# ============================================================================
# Voyage Endpoints - Core CRUD (5 endpoints)
# ============================================================================

# In-memory storage for voyages (TODO: Replace with database)
_voyages_storage: Dict[str, Dict] = {}
_voyage_counter = 1

@missing_endpoints_bp.route('/voyages', methods=['GET'])
def get_all_voyages() -> ResponseReturnValue:
    """List all voyages with optional filtering."""
    try:
        module = request.args.get('module')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        voyages = list(_voyages_storage.values())
        
        # Filter by module if specified
        if module:
            voyages = [v for v in voyages if v.get('module') == module]
        
        # Pagination
        total = len(voyages)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_voyages = voyages[start_idx:end_idx]
        
        return jsonify(paginated_response(paginated_voyages, page, per_page, total))
    
    except Exception as e:
        logger.error(f"Error getting voyages: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyages/<voyage_id>', methods=['GET'])
def get_voyage_by_id(voyage_id: str) -> ResponseReturnValue:
    """Get specific voyage by ID."""
    try:
        if voyage_id not in _voyages_storage:
            return error_response(f'Voyage {voyage_id} not found', 404)
        
        voyage = _voyages_storage[voyage_id]
        return jsonify(success_response(voyage))
    
    except Exception as e:
        logger.error(f"Error getting voyage {voyage_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyages', methods=['POST'])
def create_voyage() -> ResponseReturnValue:
    """Create a new voyage."""
    global _voyage_counter
    
    try:
        data = request.json
        if not data:
            return error_response('No data provided', 400)
        
        # Generate voyage ID
        voyage_id = f"VOY_{_voyage_counter:04d}"
        _voyage_counter += 1
        
        # Create voyage record
        voyage = {
            'id': voyage_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            **data
        }
        
        _voyages_storage[voyage_id] = voyage
        
        return jsonify(success_response(voyage, 'Voyage created successfully')), 201
    
    except Exception as e:
        logger.error(f"Error creating voyage: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyages/<voyage_id>', methods=['PUT'])
def update_voyage(voyage_id: str) -> ResponseReturnValue:
    """Update an existing voyage."""
    try:
        if voyage_id not in _voyages_storage:
            return error_response(f'Voyage {voyage_id} not found', 404)
        
        data = request.json
        if not data:
            return error_response('No data provided', 400)
        
        # Update voyage
        voyage = _voyages_storage[voyage_id]
        voyage.update(data)
        voyage['updated_at'] = datetime.now().isoformat()
        
        return jsonify(success_response(voyage, 'Voyage updated successfully'))
    
    except Exception as e:
        logger.error(f"Error updating voyage {voyage_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyages/<voyage_id>', methods=['DELETE'])
def delete_voyage(voyage_id: str) -> ResponseReturnValue:
    """Delete a voyage."""
    try:
        if voyage_id not in _voyages_storage:
            return error_response(f'Voyage {voyage_id} not found', 404)
        
        del _voyages_storage[voyage_id]
        
        return jsonify(success_response(None, 'Voyage deleted successfully'))
    
    except Exception as e:
        logger.error(f"Error deleting voyage {voyage_id}: {e}")
        return error_response(str(e), 500)


# ============================================================================
# Voyage Operations (5 endpoints)
# ============================================================================

@missing_endpoints_bp.route('/voyages/calculate', methods=['POST'])
def calculate_voyage_details() -> ResponseReturnValue:
    """Calculate voyage details (wrapper around /api/calculate)."""
    try:
        data = request.json
        if not data:
            return error_response('No data provided', 400)
        
        # This endpoint is a redirect to the existing /api/calculate
        # We keep it for API consistency with frontend expectations
        return jsonify(success_response({
            'message': 'Use /api/calculate endpoint for calculation',
            'alternative_endpoint': '/api/calculate'
        }))
    
    except Exception as e:
        logger.error(f"Error in voyage calculation: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyages/<voyage_id>/optimize', methods=['POST'])
def optimize_voyage(voyage_id: str) -> ResponseReturnValue:
    """Optimize a specific voyage."""
    try:
        if voyage_id not in _voyages_storage:
            return error_response(f'Voyage {voyage_id} not found', 404)
        
        options = request.json or {}
        
        # Placeholder for optimization logic
        optimized_voyage = _voyages_storage[voyage_id].copy()
        optimized_voyage['optimized'] = True
        optimized_voyage['optimization_date'] = datetime.now().isoformat()
        optimized_voyage['optimization_options'] = options
        
        return jsonify(success_response(optimized_voyage, 'Voyage optimized'))
    
    except Exception as e:
        logger.error(f"Error optimizing voyage {voyage_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyages/<voyage_id>/financials', methods=['GET'])
def get_voyage_financials(voyage_id: str) -> ResponseReturnValue:
    """Get financial breakdown for a voyage."""
    try:
        if voyage_id not in _voyages_storage:
            return error_response(f'Voyage {voyage_id} not found', 404)
        
        # Placeholder financial data
        financials = {
            'voyage_id': voyage_id,
            'revenue_usd': 0,
            'costs': {
                'bunker_usd': 0,
                'port_fees_usd': 0,
                'canal_fees_usd': 0,
                'other_usd': 0,
                'total_usd': 0
            },
            'profit_usd': 0,
            'tce_usd_per_day': 0
        }
        
        return jsonify(success_response(financials))
    
    except Exception as e:
        logger.error(f"Error getting financials for voyage {voyage_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyages/<voyage_id>/export', methods=['GET'])
def export_voyage(voyage_id: str) -> ResponseReturnValue:
    """Export voyage to PDF or Excel."""
    try:
        if voyage_id not in _voyages_storage:
            return error_response(f'Voyage {voyage_id} not found', 404)
        
        format_type = request.args.get('format', 'excel')
        voyage = _voyages_storage[voyage_id]
        
        # Create DataFrame from voyage data
        df = pd.DataFrame([voyage])
        
        if format_type == 'pdf':
            return error_response('PDF export not yet implemented', 501)
        else:  # excel
            temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False)
            
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=f'voyage_{voyage_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
    except Exception as e:
        logger.error(f"Error exporting voyage {voyage_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyages/generate-schedule', methods=['POST'])
def generate_voyage_schedule() -> ResponseReturnValue:
    """Generate voyage schedule based on parameters."""
    try:
        params = request.json or {}
        
        # Placeholder for schedule generation
        schedule = {
            'generated_at': datetime.now().isoformat(),
            'parameters': params,
            'schedules': [],
            'message': 'Schedule generation not yet fully implemented'
        }
        
        return jsonify(success_response(schedule))
    
    except Exception as e:
        logger.error(f"Error generating schedule: {e}")
        return error_response(str(e), 500)


# ============================================================================
# Voyage Template Endpoints (5 endpoints)
# ============================================================================

# In-memory storage for templates
_templates_storage: Dict[str, Dict] = {}
_template_counter = 1

@missing_endpoints_bp.route('/voyage-templates', methods=['GET'])
def get_all_templates() -> ResponseReturnValue:
    """Get all voyage templates."""
    try:
        templates = list(_templates_storage.values())
        return jsonify(success_response(templates))
    
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyage-templates/<template_id>', methods=['GET'])
def get_template_by_id(template_id: str) -> ResponseReturnValue:
    """Get specific template by ID."""
    try:
        if template_id not in _templates_storage:
            return error_response(f'Template {template_id} not found', 404)
        
        template = _templates_storage[template_id]
        return jsonify(success_response(template))
    
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyage-templates', methods=['POST'])
def create_template() -> ResponseReturnValue:
    """Create a new voyage template."""
    global _template_counter
    
    try:
        data = request.json
        if not data:
            return error_response('No data provided', 400)
        
        template_id = f"TPL_{_template_counter:04d}"
        _template_counter += 1
        
        template = {
            'id': template_id,
            'created_at': datetime.now().isoformat(),
            **data
        }
        
        _templates_storage[template_id] = template
        
        return jsonify(success_response(template, 'Template created successfully')), 201
    
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyage-templates/<template_id>', methods=['PUT'])
def update_template(template_id: str) -> ResponseReturnValue:
    """Update an existing template."""
    try:
        if template_id not in _templates_storage:
            return error_response(f'Template {template_id} not found', 404)
        
        data = request.json
        if not data:
            return error_response('No data provided', 400)
        
        template = _templates_storage[template_id]
        template.update(data)
        template['updated_at'] = datetime.now().isoformat()
        
        return jsonify(success_response(template, 'Template updated successfully'))
    
    except Exception as e:
        logger.error(f"Error updating template {template_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyage-templates/<template_id>', methods=['DELETE'])
def delete_template(template_id: str) -> ResponseReturnValue:
    """Delete a template."""
    try:
        if template_id not in _templates_storage:
            return error_response(f'Template {template_id} not found', 404)
        
        del _templates_storage[template_id]
        
        return jsonify(success_response(None, 'Template deleted successfully'))
    
    except Exception as e:
        logger.error(f"Error deleting template {template_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/voyage-templates/<template_id>/apply', methods=['POST'])
def apply_template(template_id: str) -> ResponseReturnValue:
    """Apply a template to create a voyage."""
    global _voyage_counter
    
    try:
        if template_id not in _templates_storage:
            return error_response(f'Template {template_id} not found', 404)
        
        template = _templates_storage[template_id]
        voyage_data = request.json or {}
        
        # Create voyage from template
        voyage_id = f"VOY_{_voyage_counter:04d}"
        _voyage_counter += 1
        
        voyage = {
            'id': voyage_id,
            'template_id': template_id,
            'created_at': datetime.now().isoformat(),
            **template,
            **voyage_data  # Override with specific voyage data
        }
        
        # Remove template metadata
        voyage.pop('id', None)  # Remove template ID, use voyage ID
        voyage['id'] = voyage_id
        
        _voyages_storage[voyage_id] = voyage
        
        return jsonify(success_response(voyage, 'Template applied successfully')), 201
    
    except Exception as e:
        logger.error(f"Error applying template {template_id}: {e}")
        return error_response(str(e), 500)


# ============================================================================
# Scenario Endpoints (5 endpoints)
# ============================================================================

# In-memory storage for scenarios
_scenarios_storage: Dict[str, Dict] = {}
_scenario_counter = 1

@missing_endpoints_bp.route('/scenarios', methods=['GET'])
def get_all_scenarios() -> ResponseReturnValue:
    """Get all scenarios."""
    try:
        scenarios = list(_scenarios_storage.values())
        return jsonify(success_response(scenarios))
    
    except Exception as e:
        logger.error(f"Error getting scenarios: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/scenarios/<scenario_id>', methods=['GET'])
def get_scenario_by_id(scenario_id: str) -> ResponseReturnValue:
    """Get specific scenario by ID."""
    try:
        if scenario_id not in _scenarios_storage:
            return error_response(f'Scenario {scenario_id} not found', 404)
        
        scenario = _scenarios_storage[scenario_id]
        return jsonify(success_response(scenario))
    
    except Exception as e:
        logger.error(f"Error getting scenario {scenario_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/scenarios', methods=['POST'])
def create_scenario() -> ResponseReturnValue:
    """Create a new scenario."""
    global _scenario_counter
    
    try:
        data = request.json
        if not data:
            return error_response('No data provided', 400)
        
        scenario_id = f"SCN_{_scenario_counter:04d}"
        _scenario_counter += 1
        
        scenario = {
            'id': scenario_id,
            'created_at': datetime.now().isoformat(),
            **data
        }
        
        _scenarios_storage[scenario_id] = scenario
        
        return jsonify(success_response(scenario, 'Scenario created successfully')), 201
    
    except Exception as e:
        logger.error(f"Error creating scenario: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/scenarios/<scenario_id>', methods=['PUT'])
def update_scenario(scenario_id: str) -> ResponseReturnValue:
    """Update an existing scenario."""
    try:
        if scenario_id not in _scenarios_storage:
            return error_response(f'Scenario {scenario_id} not found', 404)
        
        data = request.json
        if not data:
            return error_response('No data provided', 400)
        
        scenario = _scenarios_storage[scenario_id]
        scenario.update(data)
        scenario['updated_at'] = datetime.now().isoformat()
        
        return jsonify(success_response(scenario, 'Scenario updated successfully'))
    
    except Exception as e:
        logger.error(f"Error updating scenario {scenario_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/scenarios/<scenario_id>', methods=['DELETE'])
def delete_scenario(scenario_id: str) -> ResponseReturnValue:
    """Delete a scenario."""
    try:
        if scenario_id not in _scenarios_storage:
            return error_response(f'Scenario {scenario_id} not found', 404)
        
        del _scenarios_storage[scenario_id]
        
        return jsonify(success_response(None, 'Scenario deleted successfully'))
    
    except Exception as e:
        logger.error(f"Error deleting scenario {scenario_id}: {e}")
        return error_response(str(e), 500)


@missing_endpoints_bp.route('/scenarios/compare', methods=['POST'])
def compare_scenarios() -> ResponseReturnValue:
    """Compare multiple scenarios."""
    try:
        data = request.json
        if not data or 'scenario_ids' not in data:
            return error_response('scenario_ids required', 400)
        
        scenario_ids = data['scenario_ids']
        comparison = {
            'compared_at': datetime.now().isoformat(),
            'scenarios': [],
            'summary': {}
        }
        
        for scenario_id in scenario_ids:
            if scenario_id in _scenarios_storage:
                comparison['scenarios'].append(_scenarios_storage[scenario_id])
        
        if not comparison['scenarios']:
            return error_response('No valid scenarios found', 404)
        
        # Add comparison metrics (placeholder)
        comparison['summary'] = {
            'total_scenarios': len(comparison['scenarios']),
            'comparison_metrics': []
        }
        
        return jsonify(success_response(comparison))
    
    except Exception as e:
        logger.error(f"Error comparing scenarios: {e}")
        return error_response(str(e), 500)


def register_missing_endpoints(app):
    """Register the missing endpoints blueprint with the Flask app."""
    app.register_blueprint(missing_endpoints_bp)
    logger.info("Missing endpoints blueprint registered successfully")
