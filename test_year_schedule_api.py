"""
Test Year Schedule API Endpoints
=================================
Tests the new /api/schedule/year endpoints with different configurations
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:5000/api"


def test_generate_year_schedule():
    """Test POST /api/schedule/year - Generate optimized schedule"""
    print("\n" + "="*80)
    print("TEST 1: Generate Year Schedule")
    print("="*80)
    
    # Test 1: Max Revenue Strategy
    print("\n>> Test 1a: Max Revenue Strategy")
    payload = {
        "module": "deepsea",
        "strategy": "maxrevenue",
        "config": {
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "min_utilization_pct": 70.0,
            "max_utilization_pct": 95.0
        },
        "save_as": f"test_maxrev_{int(datetime.now().timestamp())}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/schedule/year", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f" Success: {data.get('success')}")
            print(f" Strategy: {data.get('strategy')}")
            print(f" KPIs:")
            kpis = data.get('kpis', {})
            print(f"  - Total Revenue: ${kpis.get('total_revenue_usd', 0):,.0f}")
            print(f"  - Total Cost: ${kpis.get('total_cost_usd', 0):,.0f}")
            print(f"  - Total Profit: ${kpis.get('total_profit_usd', 0):,.0f}")
            print(f"  - Total Voyages: {kpis.get('total_voyages', 0)}")
            print(f"  - Fleet Utilization: {kpis.get('fleet_utilization_pct', 0):.1f}%")
            print(f"  - Optimality Score: {kpis.get('optimality_score', 0):.1f}/100")
            print(f" Conflicts: {data.get('conflicts', {}).get('count', 0)}")
            print(f" Saved: {data.get('saved')}")
        else:
            print(f" Error: {response.text}")
    except Exception as e:
        print(f" Exception: {e}")
    
    # Test 1b: Min Cost Strategy
    print("\n>> Test 1b: Min Cost Strategy")
    payload['strategy'] = 'mincost'
    payload['save_as'] = f"test_mincost_{int(datetime.now().timestamp())}"
    
    try:
        response = requests.post(f"{BASE_URL}/schedule/year", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f" Success - Optimality Score: {data.get('kpis', {}).get('optimality_score', 0):.1f}/100")
        else:
            print(f" Error: {response.status_code}")
    except Exception as e:
        print(f" Exception: {e}")
    
    # Test 1c: Balanced Strategy
    print("\n>> Test 1c: Balanced Strategy")
    payload['strategy'] = 'balance'
    payload['save_as'] = f"test_balance_{int(datetime.now().timestamp())}"
    
    try:
        response = requests.post(f"{BASE_URL}/schedule/year", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f" Success - Optimality Score: {data.get('kpis', {}).get('optimality_score', 0):.1f}/100")
        else:
            print(f" Error: {response.status_code}")
    except Exception as e:
        print(f" Exception: {e}")


def test_list_schedules():
    """Test GET /api/schedule/year?list=true - List all schedules"""
    print("\n" + "="*80)
    print("TEST 2: List All Schedules")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/schedule/year?list=true")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f" Success: {data.get('success')}")
            print(f" Total Schedules: {data.get('count', 0)}")
            
            schedules = data.get('schedules', [])
            if schedules:
                print("\nSchedules:")
                for s in schedules[:5]:  # Show first 5
                    print(f"  - {s.get('schedule_id')}: {s.get('strategy')} (Score: {s.get('optimality_score', 0):.1f})")
            else:
                print("  No schedules found")
        else:
            print(f" Error: {response.text}")
    except Exception as e:
        print(f" Exception: {e}")


def test_get_specific_schedule():
    """Test GET /api/schedule/year?schedule_id=XXX - Get specific schedule"""
    print("\n" + "="*80)
    print("TEST 3: Get Specific Schedule")
    print("="*80)
    
    # First get list to find a schedule
    try:
        response = requests.get(f"{BASE_URL}/schedule/year?list=true")
        if response.status_code == 200:
            schedules = response.json().get('schedules', [])
            if schedules:
                schedule_id = schedules[0].get('schedule_id')
                print(f"\n>> Retrieving schedule: {schedule_id}")
                
                response = requests.get(f"{BASE_URL}/schedule/year?schedule_id={schedule_id}")
                if response.status_code == 200:
                    data = response.json()
                    print(f" Success: {data.get('success')}")
                    schedule = data.get('schedule', {})
                    print(f" Strategy: {schedule.get('strategy')}")
                    print(f" Created: {schedule.get('created_at')}")
                else:
                    print(f" Error: {response.status_code}")
            else:
                print("No schedules available to test")
    except Exception as e:
        print(f" Exception: {e}")


def test_detect_conflicts():
    """Test POST /api/schedule/year/conflicts - Detect conflicts"""
    print("\n" + "="*80)
    print("TEST 4: Detect Conflicts")
    print("="*80)
    
    payload = {
        "module": "deepsea"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/schedule/year/conflicts", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f" Success: {data.get('success')}")
            print(f" Total Conflicts: {data.get('total_conflicts', 0)}")
            print(f" Errors: {data.get('errors', 0)}")
            print(f" Warnings: {data.get('warnings', 0)}")
            
            summary = data.get('summary', {})
            print(f" Summary:")
            print(f"  - Critical: {summary.get('critical', 0)}")
            print(f"  - Minor: {summary.get('minor', 0)}")
            print(f"  - Vessel Overlaps: {summary.get('vessel_overlaps', 0)}")
            
            conflicts = data.get('conflicts', [])
            if conflicts:
                print(f"\nFirst conflict:")
                c = conflicts[0]
                print(f"  Type: {c.get('type')}")
                print(f"  Severity: {c.get('severity')}")
                print(f"  Description: {c.get('description', '')[:100]}")
        else:
            print(f" Error: {response.text}")
    except Exception as e:
        print(f" Exception: {e}")


def test_compare_strategies():
    """Test POST /api/schedule/year/compare - Compare strategies"""
    print("\n" + "="*80)
    print("TEST 5: Compare Optimization Strategies")
    print("="*80)
    
    payload = {
        "module": "deepsea",
        "strategies": ["maxrevenue", "mincost", "balance"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/schedule/year/compare", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f" Success: {data.get('success')}")
            print(f" Best Strategy: {data.get('best_strategy')}")
            print(f" Recommendation: {data.get('recommendation')}")
            
            print("\nComparison:")
            comparison = data.get('comparison', {})
            for strategy, metrics in comparison.items():
                if 'error' not in metrics:
                    print(f"\n  {strategy.upper()}:")
                    print(f"    Revenue: ${metrics.get('total_revenue_usd', 0):,.0f}")
                    print(f"    Cost: ${metrics.get('total_cost_usd', 0):,.0f}")
                    print(f"    Profit: ${metrics.get('total_profit_usd', 0):,.0f}")
                    print(f"    Utilization: {metrics.get('fleet_utilization_pct', 0):.1f}%")
                    print(f"    Optimality: {metrics.get('optimality_score', 0):.1f}/100")
                    print(f"    Conflicts: {metrics.get('conflicts_detected', 0)}")
                else:
                    print(f"\n  {strategy.upper()}: Error - {metrics.get('error')}")
        else:
            print(f" Error: {response.text}")
    except Exception as e:
        print(f" Exception: {e}")


def test_delete_schedule():
    """Test DELETE /api/schedule/year/<id> - Delete schedule"""
    print("\n" + "="*80)
    print("TEST 6: Delete Schedule")
    print("="*80)
    
    # Create a test schedule first
    payload = {
        "module": "deepsea",
        "strategy": "balance",
        "save_as": f"test_delete_{int(datetime.now().timestamp())}"
    }
    
    try:
        # Create
        response = requests.post(f"{BASE_URL}/schedule/year", json=payload)
        if response.status_code == 200:
            schedule_id = response.json().get('schedule_id')
            print(f" Created test schedule: {schedule_id}")
            
            # Delete
            response = requests.delete(f"{BASE_URL}/schedule/year/{schedule_id}")
            if response.status_code == 200:
                data = response.json()
                print(f" Deleted successfully: {data.get('message')}")
            else:
                print(f" Delete failed: {response.status_code}")
        else:
            print(f" Create failed: {response.status_code}")
    except Exception as e:
        print(f" Exception: {e}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("YEAR SCHEDULE API TEST SUITE")
    print("="*80)
    print(f"API Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(f"http://localhost:5000/api/health")
        if response.status_code == 200:
            print(f" Server is running")
        else:
            print(f" Server health check failed")
            exit(1)
    except Exception as e:
        print(f" Cannot connect to server: {e}")
        print(f"\nPlease start the server first:")
        print(f"  python api_server.py")
        exit(1)
    
    # Run tests
    test_generate_year_schedule()
    test_list_schedules()
    test_get_specific_schedule()
    test_detect_conflicts()
    test_compare_strategies()
    test_delete_schedule()
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")
