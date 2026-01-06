"""
Test script for PDF Report Generator with all 4 report types.

Tests:
1. Comprehensive Voyage Report
2. Fleet Analysis Report
3. Schedule Timeline Report
4. Financial Analysis Report
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from modules.pdf_reporter import PDFReportGenerator
import os
import sys

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def generate_sample_voyage_data(num_voyages=15):
    """Generate sample voyage data for testing."""
    vessels = ['MV Aurora', 'MV Borealis', 'MV Celestia', 'MV Draco', 'MV Eclipse']
    ports_load = ['Rotterdam', 'Hamburg', 'Antwerp', 'Singapore', 'Shanghai']
    ports_discharge = ['New York', 'Houston', 'Los Angeles', 'Mumbai', 'Dubai']
    
    data = []
    for i in range(num_voyages):
        voyage = {
            'voyage_id': f'V-2025-{i+1:03d}',
            'vessel_name': np.random.choice(vessels),
            'load_port': np.random.choice(ports_load),
            'discharge_port': np.random.choice(ports_discharge),
            'distance_nm': np.random.randint(3000, 12000),
            'duration_days': np.random.uniform(10, 45),
            'cargo_mt': np.random.randint(30000, 75000),
            'freight_rate': np.random.uniform(25, 85),
            'revenue_usd': 0,  # Will calculate
            'cost_usd': 0,  # Will calculate
        }
        
        # Calculate revenue and costs
        voyage['revenue_usd'] = voyage['cargo_mt'] * voyage['freight_rate']
        voyage['cost_usd'] = voyage['revenue_usd'] * np.random.uniform(0.55, 0.75)
        
        data.append(voyage)
    
    return pd.DataFrame(data)


def generate_sample_fleet_data(num_vessels=8):
    """Generate sample fleet data for testing."""
    vessel_types = ['Bulk Carrier', 'Container Ship', 'Tanker', 'General Cargo']
    flags = ['Panama', 'Liberia', 'Marshall Islands', 'Singapore']
    
    data = []
    for i in range(num_vessels):
        vessel = {
            'vessel_name': f'MV Vessel-{i+1}',
            'vessel_type': np.random.choice(vessel_types),
            'dwt_mt': np.random.randint(35000, 85000),
            'speed_kts': np.random.uniform(12, 18),
            'age_years': np.random.randint(5, 25),
            'flag': np.random.choice(flags),
        }
        data.append(vessel)
    
    return pd.DataFrame(data)


def generate_sample_utilization_data(fleet_data):
    """Generate sample utilization data based on fleet."""
    data = []
    for _, vessel in fleet_data.iterrows():
        util = {
            'vessel_name': vessel['vessel_name'],
            'utilization_pct': np.random.uniform(65, 95),
            'active_days': np.random.randint(250, 350),
            'idle_days': np.random.randint(10, 50),
        }
        data.append(util)
    
    return pd.DataFrame(data)


def generate_sample_performance_data(fleet_data):
    """Generate sample performance metrics."""
    data = []
    for _, vessel in fleet_data.iterrows():
        perf = {
            'vessel_name': vessel['vessel_name'],
            'avg_speed_kts': vessel['speed_kts'] + np.random.uniform(-1, 1),
            'fuel_efficiency': np.random.uniform(20, 45),
            'downtime_days': np.random.randint(5, 30),
            'voyages_completed': np.random.randint(8, 24),
        }
        data.append(perf)
    
    return pd.DataFrame(data)


def generate_sample_schedule_data(num_tasks=12):
    """Generate sample schedule data with tasks."""
    vessels = ['MV Aurora', 'MV Borealis', 'MV Celestia', 'MV Draco', 'MV Eclipse']
    statuses = ['completed', 'in_progress', 'pending', 'delayed']
    
    start_date = datetime.now()
    data = []
    
    for i in range(num_tasks):
        task_start = start_date + timedelta(days=i*7)
        task_duration = np.random.randint(5, 21)
        
        task = {
            'task_name': f'Voyage Task {i+1}',
            'vessel_name': np.random.choice(vessels),
            'start_date': task_start,
            'end_date': task_start + timedelta(days=task_duration),
            'status': np.random.choice(statuses),
            'progress_pct': np.random.uniform(0, 100),
        }
        data.append(task)
    
    return pd.DataFrame(data)


def generate_sample_milestones():
    """Generate sample project milestones."""
    milestones = [
        {
            'name': 'Q1 Fleet Inspection',
            'date': '2025-03-31',
            'description': 'Complete annual inspection for all vessels'
        },
        {
            'name': 'Q2 Performance Review',
            'date': '2025-06-30',
            'description': 'Mid-year fleet performance assessment'
        },
        {
            'name': 'Q3 Dry Dock Schedule',
            'date': '2025-09-30',
            'description': 'Scheduled maintenance and repairs'
        },
        {
            'name': 'Q4 Year-End Summary',
            'date': '2025-12-31',
            'description': 'Annual financial and operational review'
        }
    ]
    return milestones


def generate_sample_financial_data(num_entries=20):
    """Generate sample financial data."""
    cost_categories = ['Fuel', 'Port Charges', 'Crew Wages', 'Maintenance', 'Insurance', 'Administration']
    
    data = []
    for i in range(num_entries):
        entry = {
            'voyage_id': f'V-2025-{(i % 15) + 1:03d}',
            'cost_category': np.random.choice(cost_categories),
            'cost_usd': np.random.uniform(50000, 500000),
            'revenue_usd': np.random.uniform(800000, 2500000),
        }
        data.append(entry)
    
    return pd.DataFrame(data)


def generate_sample_revenue_projections():
    """Generate sample revenue projections."""
    periods = ['Q1-2025', 'Q2-2025', 'Q3-2025', 'Q4-2025']
    
    data = []
    base_revenue = 5000000
    for i, period in enumerate(periods):
        projection = {
            'period': period,
            'projected_revenue': base_revenue * (1 + i * 0.08),
            'actual_revenue': base_revenue * (1 + i * 0.08) * np.random.uniform(0.9, 1.1),
            'variance': 0  # Will calculate
        }
        projection['variance'] = projection['actual_revenue'] - projection['projected_revenue']
        data.append(projection)
    
    return pd.DataFrame(data)


def test_comprehensive_report(generator):
    """Test comprehensive voyage report generation."""
    print("\n" + "="*60)
    print("Testing Comprehensive Voyage Report...")
    print("="*60)
    
    voyage_data = generate_sample_voyage_data(15)
    
    try:
        filepath = generator.generate_comprehensive_report(
            voyage_data=voyage_data,
            filename="test_comprehensive_report.pdf",
            title="Comprehensive Voyage Analysis Report"
        )
        print(f" Report generated successfully: {filepath}")
        print(f"  - Voyages analyzed: {len(voyage_data)}")
        print(f"  - Total revenue: ${voyage_data['revenue_usd'].sum():,.2f}")
        print(f"  - Total cost: ${voyage_data['cost_usd'].sum():,.2f}")
        return True
    except Exception as e:
        print(f" Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fleet_report(generator):
    """Test fleet analysis report generation."""
    print("\n" + "="*60)
    print("Testing Fleet Analysis Report...")
    print("="*60)
    
    fleet_data = generate_sample_fleet_data(8)
    utilization_data = generate_sample_utilization_data(fleet_data)
    performance_data = generate_sample_performance_data(fleet_data)
    
    try:
        filepath = generator.generate_fleet_report(
            fleet_data=fleet_data,
            utilization_data=utilization_data,
            performance_data=performance_data,
            filename="test_fleet_report.pdf"
        )
        print(f" Report generated successfully: {filepath}")
        print(f"  - Vessels analyzed: {len(fleet_data)}")
        print(f"  - Average utilization: {utilization_data['utilization_pct'].mean():.1f}%")
        print(f"  - Total capacity: {fleet_data['dwt_mt'].sum():,.0f} MT")
        return True
    except Exception as e:
        print(f" Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schedule_report(generator):
    """Test schedule timeline report generation."""
    print("\n" + "="*60)
    print("Testing Schedule Timeline Report...")
    print("="*60)
    
    schedule_data = generate_sample_schedule_data(12)
    milestones = generate_sample_milestones()
    
    try:
        filepath = generator.generate_schedule_report(
            schedule_data=schedule_data,
            milestones=milestones,
            filename="test_schedule_report.pdf"
        )
        print(f" Report generated successfully: {filepath}")
        print(f"  - Tasks scheduled: {len(schedule_data)}")
        print(f"  - Milestones: {len(milestones)}")
        print(f"  - Time span: {(schedule_data['end_date'].max() - schedule_data['start_date'].min()).days} days")
        return True
    except Exception as e:
        print(f" Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_financial_report(generator):
    """Test financial analysis report generation."""
    print("\n" + "="*60)
    print("Testing Financial Analysis Report...")
    print("="*60)
    
    financial_data = generate_sample_financial_data(20)
    revenue_projections = generate_sample_revenue_projections()
    
    try:
        filepath = generator.generate_financial_report(
            financial_data=financial_data,
            revenue_projections=revenue_projections,
            filename="test_financial_report.pdf"
        )
        print(f" Report generated successfully: {filepath}")
        print(f"  - Financial entries: {len(financial_data)}")
        print(f"  - Total revenue: ${financial_data['revenue_usd'].sum():,.2f}")
        print(f"  - Total costs: ${financial_data['cost_usd'].sum():,.2f}")
        return True
    except Exception as e:
        print(f" Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test execution function."""
    print("\n" + "="*70)
    print(" PDF REPORT GENERATOR - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize generator
    output_dir = "output/reports/tests"
    os.makedirs(output_dir, exist_ok=True)
    generator = PDFReportGenerator(output_dir=output_dir)
    
    print(f"\nOutput Directory: {output_dir}")
    
    # Run all tests
    results = {
        'Comprehensive Report': test_comprehensive_report(generator),
        'Fleet Report': test_fleet_report(generator),
        'Schedule Report': test_schedule_report(generator),
        'Financial Report': test_financial_report(generator),
    }
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = " PASSED" if passed else " FAILED"
        print(f"{test_name:.<50} {status}")
    
    print("\n" + "-"*70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    print("="*70)
    
    if passed_tests == total_tests:
        print("\n All tests passed! PDF reports generated successfully.")
    else:
        print(f"\n  {total_tests - passed_tests} test(s) failed. Please review errors above.")
    
    print(f"\nGenerated reports are available in: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    main()
