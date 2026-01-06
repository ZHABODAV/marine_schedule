"""
Flask Web Application for Maritime Voyage Planner
Integrates Python modules with web interface via REST API.
"""
import sys
import os

# Add project directory to Python path to enable imports
# This allows imports like 'from logging_config import ...' to work
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
import pandas as pd
import json
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any, Sequence
from importlib.metadata import version

# Import logging
from logging_config import setup_logger  # type: ignore

# Import modules
from modules.voyage_calculator import VoyageCalculator, calculate_voyage_schedule
from modules.voyage_tables import VoyageTableGenerator, create_voyage_tables
from modules.excel_gantt import create_gantt_charts
from modules.alerts import AlertSystem, run_all_checks
from modules.berth_utilization import BerthUtilizationAnalyzer, analyze_berth_utilization
from modules.balakovo_report import BalakovoReportGenerator, generate_balakovo_report

# Initialize logger
logger = setup_logger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Type aliases
DataRecord = Dict[str, Any]
DataStore = Dict[str, Any]  # Simplified typing to avoid strict type checking issues

# Constants for file upload validation
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Global data storage (in production, use database or session)
data_store: DataStore = {
    'ports': None,
    'fleet': None,
    'templates': None,
    'template_legs': None,
    'voyages': None,
    'constraints': None,
    'calculated_legs': None,
    'alerts': None
}

logger.info("Maritime Voyage Planner initializing...")
logger.info(f"Flask version: {version('flask')}")
logger.info(f"Pandas version: {pd.__version__}")
logger.debug(f"Initialized data_store with {len(data_store)} keys")

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_file('vessel_scheduler_enhanced.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_file(filename)

@app.route('/api/upload/<file_type>', methods=['POST'])
def upload_file(file_type):
    """Upload and parse Excel/CSV files."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    
    # Diagnostic logging to validate the filename type
    logger.debug(f"File received: filename={file.filename!r}, type={type(file.filename)}")
    
    if file.filename == '' or file.filename is None:
        logger.warning(f"Invalid filename: {file.filename!r}")
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Determine file type and read accordingly
        logger.debug(f"Processing file with extension check: {file.filename}")
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.stream, delimiter=';')  # Assuming semicolon delimiter as mentioned
        else:
            # For Excel files, read the stream directly and use ExcelFile to read multiple sheets efficiently
            workbook = pd.ExcelFile(file.stream)
            df = pd.read_excel(workbook, sheet_name=0)

        # Store based on file type
        if file_type == 'ports':
            data_store['ports'] = df.to_dict('records')
        elif file_type == 'fleet' or file_type == 'vessels':
            data_store['fleet'] = df.to_dict('records')
        elif file_type == 'templates':
            # Assume first sheet is Templates, second is TemplateLegs
            data_store['templates'] = df.to_dict('records')
            # For TemplateLegs, we need to read the second sheet
            if file.filename and not file.filename.endswith('.csv'):
                if len(workbook.sheet_names) > 1:
                    template_legs_df = pd.read_excel(workbook, sheet_name=1)
                    data_store['template_legs'] = template_legs_df.to_dict('records')
        elif file_type == 'voyages' or file_type == 'commitments':
            data_store['voyages'] = df.to_dict('records')
        elif file_type == 'constraints':
            data_store['constraints'] = df.to_dict('records')
        elif file_type == 'routes':
            data_store['routes'] = df.to_dict('records')
        elif file_type == 'cargoTypes':
            data_store['cargo_types'] = df.to_dict('records')
        elif file_type == 'railCargo':
            data_store['rail_cargo'] = df.to_dict('records')
        elif file_type == 'movements':
            data_store['movements'] = df.to_dict('records')
        elif file_type == 'voyageLegs':
            data_store['voyage_legs'] = df.to_dict('records')

        return jsonify({
            'success': True,
            'message': f'{file_type} data loaded successfully',
            'count': len(df)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calculate', methods=['POST'])
def calculate_voyages():
    """Calculate voyage schedules using the voyage calculator module."""
    try:
        # Check if all required data is loaded
        required = ['ports', 'fleet', 'templates', 'template_legs', 'voyages', 'constraints']
        missing = [r for r in required if data_store[r] is None]
        if missing:
            return jsonify({'error': f'Missing data: {", ".join(missing)}'}), 400

        # Convert back to DataFrame for processing
        voyages_df = pd.DataFrame(data_store['voyages'])

        # Use the voyage calculator module
        calculator = VoyageCalculator()
        result_df = calculator.calculate_voyage_from_df(voyages_df)

        # Store results
        data_store['calculated_legs'] = result_df.to_dict('records')

        # Run alerts
        alerts_system = run_all_checks(result_df)
        data_store['alerts'] = [alert.to_dict() for alert in alerts_system.get_all_alerts()]

        return jsonify({
            'success': True,
            'legs_count': len(result_df),
            'voyages_count': len(voyages_df),
            'alerts_count': len(data_store['alerts'])
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voyages', methods=['GET'])
def get_voyages():
    """Get calculated voyage data."""
    if data_store['calculated_legs'] is None:
        return jsonify({'error': 'No calculated data available'}), 404

    return jsonify({
        'voyages': data_store['voyages'] or [],
        'legs': data_store['calculated_legs'],
        'alerts': data_store['alerts'] or []
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alerts data."""
    if data_store['alerts'] is None:
        return jsonify({'alerts': []})

    return jsonify({'alerts': data_store['alerts']})

@app.route('/api/berth-utilization', methods=['GET'])
def get_berth_utilization():
    """Get berth utilization analysis."""
    if data_store['calculated_legs'] is None:
        return jsonify({'error': 'No calculated data available'}), 404

    try:
        legs_df = pd.DataFrame(data_store['calculated_legs'])
        analyzer = BerthUtilizationAnalyzer(legs_df)
        utilization_df = analyzer.calculate_all_ports_utilization()

        return jsonify({
            'utilization': utilization_df.to_dict('records')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/balakovo-report', methods=['POST'])
def generate_balakovo():
    """Generate Balakovo report."""
    if data_store['calculated_legs'] is None:
        return jsonify({'error': 'No calculated data available'}), 404

    port_name = (request.json or {}).get('port_name', 'Balakovo')

    try:
        legs_df = pd.DataFrame(data_store['calculated_legs'])
        generator = BalakovoReportGenerator(legs_df)

        # Generate summary data
        meal_report = generator.generate_meal_operations_report(port_name)
        oil_report = generator.generate_oil_operations_report(port_name)
        monthly_summary = generator.generate_monthly_summary(port_name)
        stats = generator.get_operation_statistics(port_name)

        return jsonify({
            'meal_operations': meal_report.to_dict('records') if not meal_report.empty else [],
            'oil_operations': oil_report.to_dict('records') if not oil_report.empty else [],
            'monthly_summary': monthly_summary.to_dict('records') if not monthly_summary.empty else [],
            'statistics': stats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/excel', methods=['POST'])
def export_excel():
    """Export results to Excel."""
    if data_store['calculated_legs'] is None:
        return jsonify({'error': 'No calculated data available'}), 404

    export_type = (request.json or {}).get('type', 'voyage_schedule')

    try:
        legs_df = pd.DataFrame(data_store['calculated_legs'])

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            temp_path = tmp.name

        if export_type == 'voyage_schedule':
            legs_df.to_excel(temp_path, index=False)
        elif export_type == 'gantt':
            create_gantt_charts(legs_df, temp_path)
        elif export_type == 'tables':
            create_voyage_tables(legs_df, temp_path)
        elif export_type == 'alerts' and data_store['alerts']:
            alerts_df = pd.DataFrame(data_store['alerts'])
            alerts_df.to_excel(temp_path, index=False)
        elif export_type == 'berth_utilization':
            analyzer = BerthUtilizationAnalyzer(legs_df)
            analyzer.generate_utilization_report(temp_path)
        elif export_type == 'balakovo':
            generate_balakovo_report(legs_df, temp_path)

        return send_file(temp_path, as_attachment=True, download_name=f'{export_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gantt-data', methods=['GET'])
def get_gantt_data():
    """Get data formatted for Gantt chart display."""
    if data_store['calculated_legs'] is None:
        return jsonify({'error': 'No calculated data available'}), 404

    try:
        legs_df = pd.DataFrame(data_store['calculated_legs'])

        # Group by asset
        assets = {}
        for _, leg in legs_df.iterrows():
            asset = leg['asset']
            if asset not in assets:
                assets[asset] = []
            assets[asset].append({
                'voyage_id': leg.get('voyage_id', ''),
                'leg_type': leg.get('leg_type', ''),
                'start_time': leg['start_time'].isoformat() if hasattr(leg['start_time'], 'isoformat') else str(leg['start_time']),
                'end_time': leg['end_time'].isoformat() if hasattr(leg['end_time'], 'isoformat') else str(leg['end_time']),
                'duration_hours': leg.get('duration_hours', 0),
                'port_start': leg.get('start_port', ''),
                'port_end': leg.get('end_port', '')
            })

        return jsonify({'assets': assets})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)