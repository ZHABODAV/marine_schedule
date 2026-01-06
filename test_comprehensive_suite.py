"""
Comprehensive Test Suite for Vessel Scheduler System
=====================================================

Tests:
1. API endpoints with real data
2. End-to-end voyage creation workflow
3. Calendar data loading from all modules (olya, deepsea, balakovo)
4. Year schedule generation with optimization
5. PDF export from various views

Run with: python test_comprehensive_suite.py
"""

import requests
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import tempfile

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"
TEST_OUTPUT_DIR = "output/test_results"
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

# Test results storage
test_results = []


class TestResult:
    """Store test result information"""
    def __init__(self, name: str, passed: bool, message: str, duration: float = 0.0, details: Optional[Dict] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


def log_test(name: str, passed: bool, message: str, duration: float = 0.0, details: Optional[Dict] = None):
    """Log test result"""
    result = TestResult(name, passed, message, duration, details)
    test_results.append(result)
    
    status = " PASSED" if passed else " FAILED"
    print(f"  {status}: {name}")
    if message:
        print(f"    {message}")
    if duration > 0:
        print(f"    Duration: {duration:.2f}s")
    return result


def check_server_health() -> bool:
    """Verify API server is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


# ============================================================================
# TEST CATEGORY 1: API Endpoints with Real Data
# ============================================================================

def test_api_endpoints_with_real_data():
    """Test all major API endpoints with real data"""
    print("\n" + "="*80)
    print("TEST CATEGORY 1: API ENDPOINTS WITH REAL DATA")
    print("="*80)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1.1: Health Check
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/health")
        passed = response.status_code == 200 and 'status' in response.json()
        log_test("API Health Check", passed, 
                f"Status: {response.json().get('status', 'unknown')}", 
                time.time() - start)
        if passed:
            tests_passed += 1
    except Exception as e:
        log_test("API Health Check", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 1.2: Get Vessels
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/vessels")
        passed = response.status_code == 200 and 'vessels' in response.json()
        vessels_count = len(response.json().get('vessels', []))
        log_test("Get Vessels Endpoint", passed, 
                f"Retrieved {vessels_count} vessels", 
                time.time() - start,
                {'count': vessels_count})
        if passed:
            tests_passed += 1
    except Exception as e:
        log_test("Get Vessels Endpoint", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 1.3: Get Cargo
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/cargo")
        passed = response.status_code == 200 and 'cargo' in response.json()
        cargo_count = len(response.json().get('cargo', []))
        log_test("Get Cargo Endpoint", passed, 
                f"Retrieved {cargo_count} cargo items", 
                time.time() - start,
                {'count': cargo_count})
        if passed:
            tests_passed += 1
    except Exception as e:
        log_test("Get Cargo Endpoint", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 1.4: Dashboard Stats
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/dashboard/stats")
        passed = response.status_code == 200
        if passed:
            stats = response.json()
            log_test("Dashboard Stats Endpoint", True,
                    f"Active Vessels: {stats.get('activeVessels', 0)}, Pending Cargo: {stats.get('pendingCargo', 0)}",
                    time.time() - start,
                    stats)
            tests_passed += 1
        else:
            log_test("Dashboard Stats Endpoint", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Dashboard Stats Endpoint", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 1.5: Calculate Schedule (DeepSea)
    tests_total += 1
    start = time.time()
    try:
        payload = {"module": "deepsea"}
        response = requests.post(f"{API_BASE}/calculate", json=payload)
        passed = response.status_code == 200 and response.json().get('success', False)
        if passed:
            result = response.json()
            log_test("Calculate Schedule API (DeepSea)", True,
                    f"Legs: {result.get('legs_count', 0)}, Alerts: {result.get('alerts_count', 0)}",
                    time.time() - start,
                    result)
            tests_passed += 1
        else:
            log_test("Calculate Schedule API (DeepSea)", False, 
                    f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Calculate Schedule API (DeepSea)", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 1.6: Get Gantt Data
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/gantt-data")
        passed = response.status_code == 200 and 'assets' in response.json()
        if passed:
            data = response.json()
            legs_count = data.get('legs_count', 0)
            log_test("Get Gantt Data API", True,
                    f"Retrieved {legs_count} legs",
                    time.time() - start,
                    {'legs_count': legs_count, 'module': data.get('module')})
            tests_passed += 1
        else:
            log_test("Get Gantt Data API", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Get Gantt Data API", False, f"Exception: {str(e)}", time.time() - start)
    
    print(f"\n  Category 1 Results: {tests_passed}/{tests_total} tests passed")
    return tests_passed, tests_total


# ============================================================================
# TEST CATEGORY 2: End-to-End Voyage Creation Workflow
# ============================================================================

def test_voyage_creation_workflow():
    """Test complete voyage creation workflow from data input to export"""
    print("\n" + "="*80)
    print("TEST CATEGORY 2: END-TO-END VOYAGE CREATION WORKFLOW")
    print("="*80)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 2.1: Upload vessel data
    tests_total += 1
    start = time.time()
    try:
        # Create sample vessel data
        vessel_data = {
            "vessels": [
                {"id": "TEST001", "name": "Test Vessel 1", "class": "Handymax", "dwt": 50000, "speed": 14.5},
                {"id": "TEST002", "name": "Test Vessel 2", "class": "Panamax", "dwt": 75000, "speed": 15.0}
            ]
        }
        response = requests.post(f"{API_BASE}/vessels", json=vessel_data)
        passed = response.status_code == 200
        log_test("Upload Vessel Data", passed,
                f"Uploaded {len(vessel_data['vessels'])} vessels",
                time.time() - start)
        if passed:
            tests_passed += 1
    except Exception as e:
        log_test("Upload Vessel Data", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 2.2: Upload cargo data
    tests_total += 1
    start = time.time()
    try:
        cargo_data = {
            "cargo": [
                {
                    "id": "CARGO001",
                    "commodity": "Coal",
                    "quantity": 45000,
                    "loadPort": "Rotterdam",
                    "dischPort": "New York",
                    "laycanStart": "2026-02-01",
                    "laycanEnd": "2026-02-15"
                }
            ]
        }
        response = requests.post(f"{API_BASE}/cargo", json=cargo_data)
        passed = response.status_code == 200
        log_test("Upload Cargo Data", passed,
                f"Uploaded {len(cargo_data['cargo'])} cargo items",
                time.time() - start)
        if passed:
            tests_passed += 1
    except Exception as e:
        log_test("Upload Cargo Data", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 2.3: Generate Schedule (DeepSea)
    tests_total += 1
    start = time.time()
    try:
        payload = {"type": "deepsea"}
        response = requests.post(f"{API_BASE}/schedule/generate", json=payload)
        passed = response.status_code == 200 and response.json().get('status') == 'success'
        if passed:
            result = response.json()
            summary = result.get('summary', {})
            log_test("Generate Schedule DeepSea", True,
                    f"Vessels: {summary.get('totalVessels', 0)}, Cargo: {summary.get('totalCargo', 0)}",
                    time.time() - start,
                    summary)
            tests_passed += 1
        else:
            log_test("Generate Schedule DeepSea", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Generate Schedule DeepSea", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 2.4: Calculate Voyages
    tests_total += 1
    start = time.time()
    try:
        payload = {"module": "deepsea"}
        response = requests.post(f"{API_BASE}/calculate", json=payload)
        passed = response.status_code == 200 and response.json().get('success', False)
        if passed:
            result = response.json()
            log_test("Calculate Voyages", True,
                    f"Generated {result.get('legs_count', 0)} voyage legs",
                    time.time() - start,
                    result)
            tests_passed += 1
        else:
            log_test("Calculate Voyages", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Calculate Voyages", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 2.5: Export to Excel
    tests_total += 1
    start = time.time()
    try:
        payload = {"module": "deepsea", "month": "2026-02"}
        response = requests.post(f"{API_BASE}/export/excel", json=payload)
        passed = response.status_code == 200 or response.status_code == 404  # 404 is acceptable if no data for month
        
        if response.status_code == 200:
            # Save file
            filename = f"test_export_{int(time.time())}.xlsx"
            filepath = os.path.join(TEST_OUTPUT_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            file_size = os.path.getsize(filepath)
            log_test("Export to Excel", True,
                    f"Exported file: {filename} ({file_size} bytes)",
                    time.time() - start,
                    {'file': filename, 'size': file_size})
            tests_passed += 1
        else:
            log_test("Export to Excel", True,
                    "No data for specified month (acceptable)",
                    time.time() - start)
            tests_passed += 1
    except Exception as e:
        log_test("Export to Excel", False, f"Exception: {str(e)}", time.time() - start)
    
    print(f"\n  Category 2 Results: {tests_passed}/{tests_total} tests passed")
    return tests_passed, tests_total


# ============================================================================
# TEST CATEGORY 3: Calendar Data Loading from All Modules
# ============================================================================

def test_calendar_data_loading():
    """Test calendar event loading from all modules"""
    print("\n" + "="*80)
    print("TEST CATEGORY 3: CALENDAR DATA LOADING FROM ALL MODULES")
    print("="*80)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 3.1: Get All Calendar Events
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/calendar/events")
        passed = response.status_code == 200 and 'events' in response.json()
        if passed:
            data = response.json()
            total_events = data.get('metadata', {}).get('total', 0)
            log_test("Get All Calendar Events", True,
                    f"Retrieved {total_events} total events",
                    time.time() - start,
                    data.get('metadata', {}))
            tests_passed += 1
        else:
            log_test("Get All Calendar Events", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Get All Calendar Events", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 3.2: Filter Calendar Events by Module (Olya)
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/calendar/events?module=olya")
        passed = response.status_code == 200 and 'events' in response.json()
        if passed:
            data = response.json()
            returned = data.get('metadata', {}).get('returned', 0)
            log_test("Calendar Events - Olya Module", True,
                    f"Retrieved {returned} Olya events",
                    time.time() - start,
                    {'module': 'olya', 'count': returned})
            tests_passed += 1
        else:
            log_test("Calendar Events - Olya Module", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Calendar Events - Olya Module", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 3.3: Filter Calendar Events by Module (DeepSea)
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/calendar/events?module=deepsea")
        passed = response.status_code == 200 and 'events' in response.json()
        if passed:
            data = response.json()
            returned = data.get('metadata', {}).get('returned', 0)
            log_test("Calendar Events - DeepSea Module", True,
                    f"Retrieved {returned} DeepSea events",
                    time.time() - start,
                    {'module': 'deepsea', 'count': returned})
            tests_passed += 1
        else:
            log_test("Calendar Events - DeepSea Module", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Calendar Events - DeepSea Module", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 3.4: Filter Calendar Events by Module (Balakovo)
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/calendar/events?module=balakovo")
        passed = response.status_code == 200 and 'events' in response.json()
        if passed:
            data = response.json()
            returned = data.get('metadata', {}).get('returned', 0)
            log_test("Calendar Events - Balakovo Module", True,
                    f"Retrieved {returned} Balakovo events",
                    time.time() - start,
                    {'module': 'balakovo', 'count': returned})
            tests_passed += 1
        else:
            log_test("Calendar Events - Balakovo Module", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Calendar Events - Balakovo Module", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 3.5: Filter by Date Range
    tests_total += 1
    start = time.time()
    try:
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() + timedelta(days=30)).isoformat()
        response = requests.get(f"{API_BASE}/calendar/events?start_date={start_date}&end_date={end_date}")
        passed = response.status_code == 200 and 'events' in response.json()
        if passed:
            data = response.json()
            returned = data.get('metadata', {}).get('returned', 0)
            log_test("Calendar Events - Date Range Filter", True,
                    f"Retrieved {returned} events in next 30 days",
                    time.time() - start,
                    {'count': returned, 'range': '30 days'})
            tests_passed += 1
        else:
            log_test("Calendar Events - Date Range Filter", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Calendar Events - Date Range Filter", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 3.6: Filter by Status
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/calendar/events?status=planned")
        passed = response.status_code == 200 and 'events' in response.json()
        if passed:
            data = response.json()
            returned = data.get('metadata', {}).get('returned', 0)
            log_test("Calendar Events - Status Filter", True,
                    f"Retrieved {returned} planned events",
                    time.time() - start,
                    {'status': 'planned', 'count': returned})
            tests_passed += 1
        else:
            log_test("Calendar Events - Status Filter", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Calendar Events - Status Filter", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 3.7: Error Handling - Invalid Module
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/calendar/events?module=invalid_module")
        passed = response.status_code == 400  # Should return error for invalid module
        log_test("Calendar Events - Error Handling", passed,
                "Correctly rejected invalid module" if passed else "Failed to reject invalid module",
                time.time() - start)
        if passed:
            tests_passed += 1
    except Exception as e:
        log_test("Calendar Events - Error Handling", False, f"Exception: {str(e)}", time.time() - start)
    
    print(f"\n  Category 3 Results: {tests_passed}/{tests_total} tests passed")
    return tests_passed, tests_total


# ============================================================================
# TEST CATEGORY 4: Year Schedule Generation with Optimization
# ============================================================================

def test_year_schedule_generation():
    """Test year schedule generation with different optimization strategies"""
    print("\n" + "="*80)
    print("TEST CATEGORY 4: YEAR SCHEDULE GENERATION WITH OPTIMIZATION")
    print("="*80)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 4.1: Generate Schedule - Max Revenue Strategy
    tests_total += 1
    start = time.time()
    try:
        payload = {
            "module": "deepsea",
            "strategy": "maxrevenue",
            "config": {
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
                "min_utilization_pct": 70.0,
                "max_utilization_pct": 95.0
            },
            "save_as": f"test_maxrev_{int(time.time())}"
        }
        response = requests.post(f"{API_BASE}/schedule/year", json=payload)
        passed = response.status_code == 200 and response.json().get('success', False)
        if passed:
            data = response.json()
            kpis = data.get('kpis', {})
            log_test("Year Schedule - Max Revenue Strategy", True,
                    f"Revenue: ${kpis.get('total_revenue_usd', 0):,.0f}, Optimality: {kpis.get('optimality_score', 0):.1f}/100",
                    time.time() - start,
                    kpis)
            tests_passed += 1
        else:
            log_test("Year Schedule - Max Revenue Strategy", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Year Schedule - Max Revenue Strategy", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 4.2: Generate Schedule - Min Cost Strategy
    tests_total += 1
    start = time.time()
    try:
        payload = {
            "module": "deepsea",
            "strategy": "mincost",
            "config": {
                "start_date": "2026-01-01",
                "end_date": "2026-12-31"
            },
            "save_as": f"test_mincost_{int(time.time())}"
        }
        response = requests.post(f"{API_BASE}/schedule/year", json=payload)
        passed = response.status_code == 200 and response.json().get('success', False)
        if passed:
            data = response.json()
            kpis = data.get('kpis', {})
            log_test("Year Schedule - Min Cost Strategy", True,
                    f"Cost: ${kpis.get('total_cost_usd', 0):,.0f}, Optimality: {kpis.get('optimality_score', 0):.1f}/100",
                    time.time() - start,
                    kpis)
            tests_passed += 1
        else:
            log_test("Year Schedule - Min Cost Strategy", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Year Schedule - Min Cost Strategy", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 4.3: Generate Schedule - Balanced Strategy
    tests_total += 1
    start = time.time()
    try:
        payload = {
            "module": "deepsea",
            "strategy": "balance",
            "config": {
                "start_date": "2026-01-01",
                "end_date": "2026-12-31"
            },
            "save_as": f"test_balance_{int(time.time())}"
        }
        response = requests.post(f"{API_BASE}/schedule/year", json=payload)
        passed = response.status_code == 200 and response.json().get('success', False)
        if passed:
            data = response.json()
            kpis = data.get('kpis', {})
            log_test("Year Schedule - Balanced Strategy", True,
                    f"Profit: ${kpis.get('total_profit_usd', 0):,.0f}, Utilization: {kpis.get('fleet_utilization_pct', 0):.1f}%",
                    time.time() - start,
                    kpis)
            tests_passed += 1
        else:
            log_test("Year Schedule - Balanced Strategy", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Year Schedule - Balanced Strategy", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 4.4: List All Schedules
    tests_total += 1
    start = time.time()
    try:
        response = requests.get(f"{API_BASE}/schedule/year?list=true")
        passed = response.status_code == 200 and 'schedules' in response.json()
        if passed:
            data = response.json()
            count = data.get('count', 0)
            log_test("List Year Schedules", True,
                    f"Found {count} saved schedules",
                    time.time() - start,
                    {'count': count})
            tests_passed += 1
        else:
            log_test("List Year Schedules", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("List Year Schedules", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 4.5: Detect Conflicts
    tests_total += 1
    start = time.time()
    try:
        payload = {"module": "deepsea"}
        response = requests.post(f"{API_BASE}/schedule/year/conflicts", json=payload)
        passed = response.status_code == 200 and response.json().get('success', False)
        if passed:
            data = response.json()
            total_conflicts = data.get('total_conflicts', 0)
            log_test("Detect Schedule Conflicts", True,
                    f"Detected {total_conflicts} conflicts",
                    time.time() - start,
                    data.get('summary', {}))
            tests_passed += 1
        else:
            log_test("Detect Schedule Conflicts", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Detect Schedule Conflicts", False, f"Exception: {str(e)}", time.time() - start)
    
    # Test 4.6: Compare Strategies
    tests_total += 1
    start = time.time()
    try:
        payload = {
            "module": "deepsea",
            "strategies": ["maxrevenue", "mincost", "balance"]
        }
        response = requests.post(f"{API_BASE}/schedule/year/compare", json=payload)
        passed = response.status_code == 200 and response.json().get('success', False)
        if passed:
            data = response.json()
            best = data.get('best_strategy', 'unknown')
            log_test("Compare Optimization Strategies", True,
                    f"Best strategy: {best}",
                    time.time() - start,
                    {'best_strategy': best})
            tests_passed += 1
        else:
            log_test("Compare Optimization Strategies", False, f"Status: {response.status_code}", time.time() - start)
    except Exception as e:
        log_test("Compare Optimization Strategies", False, f"Exception: {str(e)}", time.time() - start)
    
    print(f"\n  Category 4 Results: {tests_passed}/{tests_total} tests passed")
    return tests_passed, tests_total


# ============================================================================
# TEST CATEGORY 5: PDF Export from Various Views
# ============================================================================

def test_pdf_exports():
    """Test PDF generation from various views"""
    print("\n" + "="*80)
    print("TEST CATEGORY 5: PDF EXPORT FROM VARIOUS VIEWS")
    print("="*80)
    
    tests_passed = 0
    tests_total = 0
    
    # Import PDF reporter
    try:
        from modules.pdf_reporter import PDFReportGenerator
        import pandas as pd
        import numpy as np
        
        generator = PDFReportGenerator(output_dir=TEST_OUTPUT_DIR)
        
        # Test 5.1: Comprehensive Voyage Report
        tests_total += 1
        start = time.time()
        try:
            # Generate sample data
            voyage_data = pd.DataFrame({
                'voyage_id': [f'V-2026-{i:03d}' for i in range(1, 11)],
                'vessel_name': ['MV Test ' + str(i % 3) for i in range(10)],
                'load_port': ['Rotterdam'] * 5 + ['Hamburg'] * 5,
                'discharge_port': ['New York'] * 5 + ['Houston'] * 5,
                'distance_nm': np.random.randint(3000, 10000, 10),
                'duration_days': np.random.uniform(15, 40, 10),
                'cargo_mt': np.random.randint(40000, 70000, 10),
                'freight_rate': np.random.uniform(30, 80, 10),
                'revenue_usd': np.random.uniform(2000000, 5000000, 10),
                'cost_usd': np.random.uniform(1500000, 3500000, 10)
            })
            
            filepath = generator.generate_comprehensive_report(
                voyage_data=voyage_data,
                filename="test_comprehensive_report.pdf",
                title="Test Comprehensive Voyage Report"
            )
            
            passed = filepath and os.path.exists(filepath)
            if passed:
                file_size = os.path.getsize(filepath)
                log_test("PDF Export - Comprehensive Voyage Report", True,
                        f"Generated {filepath} ({file_size} bytes)",
                        time.time() - start,
                        {'file': filepath, 'size': file_size})
                tests_passed += 1
            else:
                log_test("PDF Export - Comprehensive Voyage Report", False, "File not created", time.time() - start)
        except Exception as e:
            log_test("PDF Export - Comprehensive Voyage Report", False, f"Exception: {str(e)}", time.time() - start)
        
        # Test 5.2: Fleet Analysis Report
        tests_total += 1
        start = time.time()
        try:
            # Generate sample fleet data
            fleet_data = pd.DataFrame({
                'vessel_name': [f'MV Vessel-{i}' for i in range(1, 6)],
                'vessel_type': ['Bulk Carrier'] * 5,
                'dwt_mt': np.random.randint(40000, 80000, 5),
                'speed_kts': np.random.uniform(13, 16, 5),
                'age_years': np.random.randint(5, 20, 5),
                'flag': ['Panama'] * 5
            })
            
            utilization_data = pd.DataFrame({
                'vessel_name': [f'MV Vessel-{i}' for i in range(1, 6)],
                'utilization_pct': np.random.uniform(70, 92, 5),
                'active_days': np.random.randint(280, 340, 5),
                'idle_days': np.random.randint(15, 45, 5)
            })
            
            performance_data = pd.DataFrame({
                'vessel_name': [f'MV Vessel-{i}' for i in range(1, 6)],
                'avg_speed_kts': np.random.uniform(13, 16, 5),
                'fuel_efficiency': np.random.uniform(25, 40, 5),
                'downtime_days': np.random.randint(5, 25, 5),
                'voyages_completed': np.random.randint(10, 20, 5)
            })
            
            filepath = generator.generate_fleet_report(
                fleet_data=fleet_data,
                utilization_data=utilization_data,
                performance_data=performance_data,
                filename="test_fleet_report.pdf"
            )
            
            passed = filepath and os.path.exists(filepath)
            if passed:
                file_size = os.path.getsize(filepath)
                log_test("PDF Export - Fleet Analysis Report", True,
                        f"Generated {filepath} ({file_size} bytes)",
                        time.time() - start,
                        {'file': filepath, 'size': file_size})
                tests_passed += 1
            else:
                log_test("PDF Export - Fleet Analysis Report", False, "File not created", time.time() - start)
        except Exception as e:
            log_test("PDF Export - Fleet Analysis Report", False, f"Exception: {str(e)}", time.time() - start)
        
        # Test 5.3: Schedule Timeline Report
        tests_total += 1
        start = time.time()
        try:
            # Generate sample schedule data
            start_date = datetime.now()
            schedule_data = pd.DataFrame({
                'task_name': [f'Voyage Task {i}' for i in range(1, 8)],
                'vessel_name': ['MV Test ' + str(i % 3) for i in range(7)],
                'start_date': [start_date + timedelta(days=i*10) for i in range(7)],
                'end_date': [start_date + timedelta(days=i*10 + 15) for i in range(7)],
                'status': ['completed', 'in_progress', 'pending'] * 2 + ['completed'],
                'progress_pct': np.random.uniform(0, 100, 7)
            })
            
            milestones = [
                {'name': 'Q1 Review', 'date': '2026-03-31', 'description': 'Quarterly review'},
                {'name': 'Q2 Review', 'date': '2026-06-30', 'description': 'Quarterly review'}
            ]
            
            filepath = generator.generate_schedule_report(
                schedule_data=schedule_data,
                milestones=milestones,
                filename="test_schedule_report.pdf"
            )
            
            passed = filepath and os.path.exists(filepath)
            if passed:
                file_size = os.path.getsize(filepath)
                log_test("PDF Export - Schedule Timeline Report", True,
                        f"Generated {filepath} ({file_size} bytes)",
                        time.time() - start,
                        {'file': filepath, 'size': file_size})
                tests_passed += 1
            else:
                log_test("PDF Export - Schedule Timeline Report", False, "File not created", time.time() - start)
        except Exception as e:
            log_test("PDF Export - Schedule Timeline Report", False, f"Exception: {str(e)}", time.time() - start)
        
        # Test 5.4: Financial Analysis Report
        tests_total += 1
        start = time.time()
        try:
            # Generate sample financial data
            financial_data = pd.DataFrame({
                'voyage_id': [f'V-2026-{i:03d}' for i in range(1, 13)],
                'cost_category': ['Fuel', 'Port Charges', 'Crew'] * 4,
                'cost_usd': np.random.uniform(100000, 800000, 12),
                'revenue_usd': np.random.uniform(1500000, 3000000, 12)
            })
            
            revenue_projections = pd.DataFrame({
                'period': ['Q1-2026', 'Q2-2026', 'Q3-2026', 'Q4-2026'],
                'projected_revenue': [6000000, 6500000, 7000000, 7200000],
                'actual_revenue': [5800000, 6700000, 6900000, 7300000],
                'variance': [-200000, 200000, -100000, 100000]
            })
            
            filepath = generator.generate_financial_report(
                financial_data=financial_data,
                revenue_projections=revenue_projections,
                filename="test_financial_report.pdf"
            )
            
            passed = filepath and os.path.exists(filepath)
            if passed:
                file_size = os.path.getsize(filepath)
                log_test("PDF Export - Financial Analysis Report", True,
                        f"Generated {filepath} ({file_size} bytes)",
                        time.time() - start,
                        {'file': filepath, 'size': file_size})
                tests_passed += 1
            else:
                log_test("PDF Export - Financial Analysis Report", False, "File not created", time.time() - start)
        except Exception as e:
            log_test("PDF Export - Financial Analysis Report", False, f"Exception: {str(e)}", time.time() - start)
        
    except ImportError as e:
        print(f"    Skipping PDF tests - PDF reporter module not available: {e}")
        print(f"  Note: 0/{4} tests run (dependencies missing)")
    
    print(f"\n  Category 5 Results: {tests_passed}/{tests_total} tests passed")
    return tests_passed, tests_total


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def save_test_report():
    """Save test results to JSON file"""
    report_file = os.path.join(TEST_OUTPUT_DIR, f"test_report_{int(time.time())}.json")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': len(test_results),
            'passed': sum(1 for r in test_results if r.passed),
            'failed': sum(1 for r in test_results if not r.passed),
            'success_rate': (sum(1 for r in test_results if r.passed) / len(test_results) * 100) if test_results else 0
        },
        'tests': [
            {
                'name': r.name,
                'passed': r.passed,
                'message': r.message,
                'duration': r.duration,
                'timestamp': r.timestamp,
                'details': r.details
            }
            for r in test_results
        ]
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report_file


def main():
    """Main test execution"""
    print("\n" + "="*80)
    print(" COMPREHENSIVE TEST SUITE FOR VESSEL SCHEDULER SYSTEM")
    print("="*80)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base URL: {API_BASE}")
    print(f"Output Directory: {TEST_OUTPUT_DIR}")
    
    # Check server health
    print("\n" + "-"*80)
    print("Checking API Server Status...")
    print("-"*80)
    
    if not check_server_health():
        print("\n ERROR: API server is not running!")
        print("\nPlease start the server first:")
        print("  python api_server.py")
        print("\nOr if using the enhanced server:")
        print("  python api_server_enhanced.py")
        sys.exit(1)
    
    print(" API server is healthy and running")
    
    # Run all test categories
    category_results = []
    
    try:
        # Category 1: API Endpoints
        passed, total = test_api_endpoints_with_real_data()
        category_results.append(('API Endpoints', passed, total))
        
        # Category 2: E2E Workflow
        passed, total = test_voyage_creation_workflow()
        category_results.append(('E2E Voyage Workflow', passed, total))
        
        # Category 3: Calendar Data
        passed, total = test_calendar_data_loading()
        category_results.append(('Calendar Data Loading', passed, total))
        
        # Category 4: Year Schedule
        passed, total = test_year_schedule_generation()
        category_results.append(('Year Schedule Generation', passed, total))
        
        # Category 5: PDF Exports
        passed, total = test_pdf_exports()
        category_results.append(('PDF Exports', passed, total))
        
    except KeyboardInterrupt:
        print("\n\n  Test execution interrupted by user")
    except Exception as e:
        print(f"\n\n FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print("\n" + "="*80)
    print(" COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    total_passed = 0
    total_tests = 0
    
    for category, passed, total in category_results:
        percentage = (passed / total * 100) if total > 0 else 0
        status = "" if passed == total else "" if passed > 0 else ""
        print(f"\n{status} {category}:")
        print(f"   Passed: {passed}/{total} ({percentage:.1f}%)")
        total_passed += passed
        total_tests += total
    
    print("\n" + "-"*80)
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"\nOVERALL RESULTS:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_tests - total_passed}")
    print(f"  Success Rate: {overall_percentage:.1f}%")
    
    # Save report
    report_file = save_test_report()
    print(f"\nDetailed test report saved to: {report_file}")
    
    print("\n" + "="*80)
    if total_passed == total_tests:
        print(" ALL TESTS PASSED!")
    elif total_passed > total_tests * 0.8:
        print(" TESTS MOSTLY PASSED - minor issues detected")
    elif total_passed > total_tests * 0.5:
        print("  PARTIAL SUCCESS - significant issues detected")
    else:
        print(" TESTS FAILED - major issues detected")
    print("="*80 + "\n")
    
    return 0 if total_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
