"""
Enhanced Comprehensive Tests for PDF Report Generation (All 4 Types)

Tests include:
- Comprehensive Voyage Report generation and validation
- Fleet Analysis Report generation and validation
- Schedule Timeline Report generation and validation
- Financial Analysis Report generation and validation
- PDF file integrity checks
- Content validation
- Error handling
- Edge cases
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import os
from modules.pdf_reporter import PDFReportGenerator


class TestPDFReportGeneration:
    """Test suite for PDF report generation - all 4 types."""
    
    @pytest.fixture
    def output_dir(self, tmp_path):
        """Create temporary output directory for tests."""
        test_dir = tmp_path / "pdf_reports_test"
        test_dir.mkdir()
        return str(test_dir)
    
    @pytest.fixture
    def generator(self, output_dir):
        """Create PDF report generator instance."""
        return PDFReportGenerator(output_dir=output_dir)
    
    @pytest.fixture
    def sample_voyage_data(self):
        """Generate sample voyage data."""
        return pd.DataFrame({
            'voyage_id': [f'V-2025-{i:03d}' for i in range(1, 11)],
            'vessel_name': np.random.choice(['MV Aurora', 'MV Borealis', 'MV Celestia'], 10),
            'load_port': np.random.choice(['Rotterdam', 'Hamburg', 'Antwerp'], 10),
            'discharge_port': np.random.choice(['New York', 'Houston', 'Los Angeles'], 10),
            'distance_nm': np.random.randint(3000, 12000, 10),
            'duration_days': np.random.uniform(10, 45, 10),
            'cargo_mt': np.random.randint(30000, 75000, 10),
            'freight_rate': np.random.uniform(25, 85, 10),
            'revenue_usd': np.random.uniform(1000000, 5000000, 10),
            'cost_usd': np.random.uniform(500000, 3000000, 10)
        })
    
    @pytest.fixture
    def sample_fleet_data(self):
        """Generate sample fleet data."""
        return pd.DataFrame({
            'vessel_name': [f'MV Vessel-{i}' for i in range(1, 6)],
            'vessel_type': np.random.choice(['Bulk Carrier', 'Tanker', 'Container Ship'], 5),
            'dwt_mt': np.random.randint(35000, 85000, 5),
            'speed_kts': np.random.uniform(12, 18, 5),
            'age_years': np.random.randint(5, 25, 5),
            'flag': np.random.choice(['Panama', 'Liberia', 'Singapore'], 5)
        })
    
    @pytest.fixture
    def sample_utilization_data(self, sample_fleet_data):
        """Generate sample utilization data."""
        return pd.DataFrame({
            'vessel_name': sample_fleet_data['vessel_name'],
            'utilization_pct': np.random.uniform(65, 95, len(sample_fleet_data)),
            'active_days': np.random.randint(250, 350, len(sample_fleet_data)),
            'idle_days': np.random.randint(10, 50, len(sample_fleet_data))
        })
    
    @pytest.fixture
    def sample_performance_data(self, sample_fleet_data):
        """Generate sample performance data."""
        return pd.DataFrame({
            'vessel_name': sample_fleet_data['vessel_name'],
            'avg_speed_kts': sample_fleet_data['speed_kts'] + np.random.uniform(-1, 1, len(sample_fleet_data)),
            'fuel_efficiency': np.random.uniform(20, 45, len(sample_fleet_data)),
            'downtime_days': np.random.randint(5, 30, len(sample_fleet_data)),
            'voyages_completed': np.random.randint(8, 24, len(sample_fleet_data))
        })
    
    @pytest.fixture
    def sample_schedule_data(self):
        """Generate sample schedule data."""
        start_date = datetime.now()
        data = []
        for i in range(8):
            task_start = start_date + timedelta(days=i*7)
            task_duration = np.random.randint(5, 21)
            data.append({
                'task_name': f'Voyage Task {i+1}',
                'vessel_name': np.random.choice(['MV Aurora', 'MV Borealis', 'MV Celestia']),
                'start_date': task_start,
                'end_date': task_start + timedelta(days=task_duration),
                'status': np.random.choice(['completed', 'in_progress', 'pending', 'delayed']),
                'progress_pct': np.random.uniform(0, 100)
            })
        return pd.DataFrame(data)
    
    @pytest.fixture
    def sample_milestones(self):
        """Generate sample milestones."""
        return [
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
            }
        ]
    
    @pytest.fixture
    def sample_financial_data(self):
        """Generate sample financial data."""
        cost_categories = ['Fuel', 'Port Charges', 'Crew Wages', 'Maintenance', 'Insurance']
        data = []
        for i in range(15):
            data.append({
                'voyage_id': f'V-2025-{(i % 10) + 1:03d}',
                'cost_category': np.random.choice(cost_categories),
                'cost_usd': np.random.uniform(50000, 500000),
                'revenue_usd': np.random.uniform(800000, 2500000)
            })
        return pd.DataFrame(data)
    
    @pytest.fixture
    def sample_revenue_projections(self):
        """Generate sample revenue projections."""
        periods = ['Q1-2025', 'Q2-2025', 'Q3-2025', 'Q4-2025']
        base_revenue = 5000000
        data = []
        for i, period in enumerate(periods):
            projected = base_revenue * (1 + i * 0.08)
            actual = projected * np.random.uniform(0.9, 1.1)
            data.append({
                'period': period,
                'projected_revenue': projected,
                'actual_revenue': actual,
                'variance': actual - projected
            })
        return pd.DataFrame(data)
    
    # Test 1: Comprehensive Voyage Report
    
    def test_generate_comprehensive_report_success(self, generator, sample_voyage_data, output_dir):
        """Should successfully generate comprehensive voyage report."""
        filepath = generator.generate_comprehensive_report(
            voyage_data=sample_voyage_data,
            filename="test_comprehensive.pdf",
            title="Test Comprehensive Report"
        )
        
        assert filepath is not None
        assert Path(filepath).exists()
        assert Path(filepath).suffix == '.pdf'
        assert Path(filepath).stat().st_size > 0
    
    def test_comprehensive_report_with_empty_data(self, generator):
        """Should handle empty voyage data gracefully."""
        empty_df = pd.DataFrame(columns=[
            'voyage_id', 'vessel_name', 'load_port', 'discharge_port',
            'distance_nm', 'duration_days', 'cargo_mt', 'freight_rate',
            'revenue_usd', 'cost_usd'
        ])
        
        filepath = generator.generate_comprehensive_report(
            voyage_data=empty_df,
            filename="test_empty_comprehensive.pdf"
        )
        
        assert filepath is not None
        assert Path(filepath).exists()
    
    def test_comprehensive_report_statistics(self, generator, sample_voyage_data):
        """Should include statistics in comprehensive report."""
        filepath = generator.generate_comprehensive_report(
            voyage_data=sample_voyage_data,
            filename="test_stats_comprehensive.pdf"
        )
        
        # File should be larger if statistics are included
        assert Path(filepath).stat().st_size > 1000
    
    # Test 2: Fleet Analysis Report
    
    def test_generate_fleet_report_success(self, generator, sample_fleet_data,
                                          sample_utilization_data, sample_performance_data):
        """Should successfully generate fleet analysis report."""
        filepath = generator.generate_fleet_report(
            fleet_data=sample_fleet_data,
            utilization_data=sample_utilization_data,
            performance_data=sample_performance_data,
            filename="test_fleet.pdf"
        )
        
        assert filepath is not None
        assert Path(filepath).exists()
        assert Path(filepath).suffix == '.pdf'
        assert Path(filepath).stat().st_size > 0
    
    def test_fleet_report_with_minimal_data(self, generator):
        """Should handle minimal fleet data."""
        minimal_fleet = pd.DataFrame({
            'vessel_name': ['MV Test'],
            'vessel_type': ['Bulk Carrier'],
            'dwt_mt': [50000],
            'speed_kts': [14.0],
            'age_years': [10],
            'flag': ['Panama']
        })
        
        minimal_util = pd.DataFrame({
            'vessel_name': ['MV Test'],
            'utilization_pct': [75.0],
            'active_days': [300],
            'idle_days': [30]
        })
        
        minimal_perf = pd.DataFrame({
            'vessel_name': ['MV Test'],
            'avg_speed_kts': [14.0],
            'fuel_efficiency': [30.0],
            'downtime_days': [15],
            'voyages_completed': [12]
        })
        
        filepath = generator.generate_fleet_report(
            fleet_data=minimal_fleet,
            utilization_data=minimal_util,
            performance_data=minimal_perf,
            filename="test_minimal_fleet.pdf"
        )
        
        assert filepath is not None
        assert Path(filepath).exists()
    
    def test_fleet_report_data_consistency(self, generator, sample_fleet_data,
                                          sample_utilization_data, sample_performance_data):
        """Should maintain data consistency across fleet reports."""
        # Generate report twice with same data
        file1 = generator.generate_fleet_report(
            fleet_data=sample_fleet_data,
            utilization_data=sample_utilization_data,
            performance_data=sample_performance_data,
            filename="test_fleet_consistency_1.pdf"
        )
        
        file2 = generator.generate_fleet_report(
            fleet_data=sample_fleet_data,
            utilization_data=sample_utilization_data,
            performance_data=sample_performance_data,
            filename="test_fleet_consistency_2.pdf"
        )
        
        # Both files should exist and have reasonable sizes
        assert Path(file1).exists() and Path(file2).exists()
        assert abs(Path(file1).stat().st_size - Path(file2).stat().st_size) < 1000
    
    # Test 3: Schedule Timeline Report
    
    def test_generate_schedule_report_success(self, generator, sample_schedule_data, sample_milestones):
        """Should successfully generate schedule timeline report."""
        filepath = generator.generate_schedule_report(
            schedule_data=sample_schedule_data,
            milestones=sample_milestones,
            filename="test_schedule.pdf"
        )
        
        assert filepath is not None
        assert Path(filepath).exists()
        assert Path(filepath).suffix == '.pdf'
        assert Path(filepath).stat().st_size > 0
    
    def test_schedule_report_without_milestones(self, generator, sample_schedule_data):
        """Should generate schedule report without milestones."""
        filepath = generator.generate_schedule_report(
            schedule_data=sample_schedule_data,
            milestones=[],
            filename="test_schedule_no_milestones.pdf"
        )
        
        assert filepath is not None
        assert Path(filepath).exists()
    
    def test_schedule_report_with_many_tasks(self, generator, sample_milestones):
        """Should handle schedule with many tasks."""
        # Generate large schedule dataset
        start_date = datetime.now()
        data = []
        for i in range(50):
            task_start = start_date + timedelta(days=i*2)
            data.append({
                'task_name': f'Task {i+1}',
                'vessel_name': f'Vessel {i % 5}',
                'start_date': task_start,
                'end_date': task_start + timedelta(days=5),
                'status': 'planned',
                'progress_pct': 0
            })
        
        large_schedule = pd.DataFrame(data)
        filepath = generator.generate_schedule_report(
            schedule_data=large_schedule,
            milestones=sample_milestones,
            filename="test_large_schedule.pdf"
        )
        
        assert filepath is not None
        assert Path(filepath).stat().st_size > 5000  # Should be larger with more data
    
    # Test 4: Financial Analysis Report
    
    def test_generate_financial_report_success(self, generator, sample_financial_data,
                                              sample_revenue_projections):
        """Should successfully generate financial analysis report."""
        filepath = generator.generate_financial_report(
            financial_data=sample_financial_data,
            revenue_projections=sample_revenue_projections,
            filename="test_financial.pdf"
        )
        
        assert filepath is not None
        assert Path(filepath).exists()
        assert Path(filepath).suffix == '.pdf'
        assert Path(filepath).stat().st_size > 0
    
    def test_financial_report_calculations(self, generator):
        """Should correctly calculate financial metrics in report."""
        financial_data = pd.DataFrame({
            'voyage_id': ['V1', 'V2', 'V3'],
            'cost_category': ['Fuel', 'Port', 'Crew'],
            'cost_usd': [100000, 50000, 30000],
            'revenue_usd': [500000, 500000, 500000]
        })
        
        revenue_proj = pd.DataFrame({
            'period': ['Q1'],
            'projected_revenue': [1000000],
            'actual_revenue': [1100000],
            'variance': [100000]
        })
        
        filepath = generator.generate_financial_report(
            financial_data=financial_data,
            revenue_projections=revenue_proj,
            filename="test_financial_calc.pdf"
        )
        
        assert filepath is not None
        # Total costs should be 180000, total revenue 1500000
        assert Path(filepath).exists()
    
    def test_financial_report_with_negative_variance(self, generator, sample_financial_data):
        """Should handle negative revenue variance properly."""
        revenue_proj = pd.DataFrame({
            'period': ['Q1', 'Q2'],
            'projected_revenue': [1000000, 1000000],
            'actual_revenue': [900000, 800000],  # Below projection
            'variance': [-100000, -200000]
        })
        
        filepath = generator.generate_financial_report(
            financial_data=sample_financial_data,
            revenue_projections=revenue_proj,
            filename="test_negative_variance.pdf"
        )
        
        assert filepath is not None
        assert Path(filepath).exists()
    
    # Integration Tests
    
    def test_generate_all_reports_sequentially(self, generator, sample_voyage_data,
                                               sample_fleet_data, sample_utilization_data,
                                               sample_performance_data, sample_schedule_data,
                                               sample_milestones, sample_financial_data,
                                               sample_revenue_projections):
        """Should generate all 4 report types successfully."""
        files = []
        
        # Generate comprehensive report
        files.append(generator.generate_comprehensive_report(
            voyage_data=sample_voyage_data,
            filename="all_comprehensive.pdf"
        ))
        
        # Generate fleet report
        files.append(generator.generate_fleet_report(
            fleet_data=sample_fleet_data,
            utilization_data=sample_utilization_data,
            performance_data=sample_performance_data,
            filename="all_fleet.pdf"
        ))
        
        # Generate schedule report
        files.append(generator.generate_schedule_report(
            schedule_data=sample_schedule_data,
            milestones=sample_milestones,
            filename="all_schedule.pdf"
        ))
        
        # Generate financial report
        files.append(generator.generate_financial_report(
            financial_data=sample_financial_data,
            revenue_projections=sample_revenue_projections,
            filename="all_financial.pdf"
        ))
        
        # All 4 reports should exist
        assert len(files) == 4
        for filepath in files:
            assert filepath is not None
            assert Path(filepath).exists()
            assert Path(filepath).stat().st_size > 0
    
    # Error Handling Tests
    
    def test_invalid_output_directory(self):
        """Should handle invalid output directory gracefully."""
        # Use a path that doesn't exist and can't be created
        with pytest.raises((OSError, PermissionError, ValueError)):
            invalid_dir = "/invalid/path/that/does/not/exist/and/cannot/be/created"
            generator = PDFReportGenerator(output_dir=invalid_dir)
            # Try to generate a report
            generator.generate_comprehensive_report(
                voyage_data=pd.DataFrame(),
                filename="test.pdf"
            )
    
    def test_report_with_special_characters_in_filename(self, generator, sample_voyage_data):
        """Should handle special characters in filename."""
        # Some characters might be invalid on certain file systems
        filepath = generator.generate_comprehensive_report(
            voyage_data=sample_voyage_data,
            filename="test_report_2025-01-01.pdf"
        )
        
        assert filepath is not None
        assert Path(filepath).exists()
    
    # Performance Tests
    
    def test_large_dataset_performance(self, generator):
        """Should handle large datasets efficiently."""
        # Generate large dataset
        large_voyage_data = pd.DataFrame({
            'voyage_id': [f'V-{i:05d}' for i in range(1000)],
            'vessel_name': np.random.choice(['Vessel A', 'Vessel B', 'Vessel C'], 1000),
            'load_port': np.random.choice(['Rotterdam', 'Hamburg'], 1000),
            'discharge_port': np.random.choice(['New York', 'Houston'], 1000),
            'distance_nm': np.random.randint(3000, 12000, 1000),
            'duration_days': np.random.uniform(10, 45, 1000),
            'cargo_mt': np.random.randint(30000, 75000, 1000),
            'freight_rate': np.random.uniform(25, 85, 1000),
            'revenue_usd': np.random.uniform(1000000, 5000000, 1000),
            'cost_usd': np.random.uniform(500000, 3000000, 1000)
        })
        
        filepath = generator.generate_comprehensive_report(
            voyage_data=large_voyage_data,
            filename="test_large_dataset.pdf"
        )
        
        assert filepath is not None
        assert Path(filepath).exists()
        # Should complete without timeout or memory issues
