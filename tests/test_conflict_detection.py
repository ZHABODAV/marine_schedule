"""
Comprehensive Tests for Schedule Conflict Detection Algorithm

Tests include:
- Asset scheduling overlaps
- Berth capacity violations
- Tight scheduling buffer times
- Multiple conflict scenarios
- Alert severity levels
- Edge cases and boundary conditions
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from modules.alerts import AlertSystem, Alert, AlertSeverity


class TestConflictDetection:
    """Test suite for schedule conflict detection."""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.alert_system = AlertSystem()
    
    # Asset Overlap Detection Tests
    
    def test_detect_simple_overlap(self):
        """Should detect basic asset scheduling overlap."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 14, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 18, 0)],
            'start_port': ['PortA', 'PortB'],
            'end_port': ['PortB', 'PortC']
        })
        
        alerts = self.alert_system.check_asset_overlaps(df)
        
        assert len(alerts) == 1, "Should detect one overlap"
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert alerts[0].alert_type == "ASSET_OVERLAP"
        assert 'VESSEL_A' in alerts[0].message
    
    def test_detect_exact_overlap(self):
        """Should detect when two schedules have identical times."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 10, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 16, 0)],
            'start_port': ['PortA', 'PortA'],
            'end_port': ['PortB', 'PortB']
        })
        
        alerts = self.alert_system.check_asset_overlaps(df)
        
        assert len(alerts) == 1, "Should detect exact overlap"
        assert alerts[0].details['overlap_hours'] == 6.0
    
    def test_no_overlap_sequential(self):
        """Should NOT detect conflict when schedules are sequential."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 16, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 20, 0)],
            'start_port': ['PortA', 'PortB'],
            'end_port': ['PortB', 'PortC']
        })
        
        alerts = self.alert_system.check_asset_overlaps(df)
        
        assert len(alerts) == 0, "Should not detect overlap for sequential schedules"
    
    def test_multiple_overlaps_same_asset(self):
        """Should detect multiple overlaps for the same asset."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A', 'VESSEL_A'],
            'start_time': [
                datetime(2025, 1, 1, 10, 0),
                datetime(2025, 1, 1, 14, 0),
                datetime(2025, 1, 1, 17, 0)
            ],
            'end_time': [
                datetime(2025, 1, 1, 16, 0),
                datetime(2025, 1, 1, 19, 0),
                datetime(2025, 1, 1, 21, 0)
            ],
            'start_port': ['PortA', 'PortB', 'PortC'],
            'end_port': ['PortB', 'PortC', 'PortD']
        })
        
        alerts = self.alert_system.check_asset_overlaps(df)
        
        assert len(alerts) == 2, "Should detect two overlaps"
    
    def test_no_overlap_different_assets(self):
        """Should NOT detect overlap when different assets have overlapping times."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_B'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 14, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 18, 0)],
            'start_port': ['PortA', 'PortC'],
            'end_port': ['PortB', 'PortD']
        })
        
        alerts = self.alert_system.check_asset_overlaps(df)
        
        assert len(alerts) == 0, "Different assets should not conflict"
    
    def test_overlap_details(self):
        """Should provide detailed overlap information."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 14, 0)],
            'end_time': [datetime(2025, 1, 1, 18, 0), datetime(2025, 1, 1, 20, 0)],
            'start_port': ['Rotterdam', 'Hamburg'],
            'end_port': ['Hamburg', 'Amsterdam']
        })
        
        alerts = self.alert_system.check_asset_overlaps(df)
        
        assert 'overlap_hours' in alerts[0].details
        assert 'leg1_route' in alerts[0].details
        assert 'leg2_route' in alerts[0].details
        assert alerts[0].details['overlap_hours'] == 4.0
        assert 'Rotterdam' in alerts[0].details['leg1_route']
        assert 'Hamburg' in alerts[0].details['leg2_route']
    
    def test_partial_overlap(self):
        """Should correctly calculate partial overlap duration."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 15, 30)],
            'end_time': [datetime(2025, 1, 1, 17, 0), datetime(2025, 1, 1, 20, 0)],
            'start_port': ['PortA', 'PortB'],
            'end_port': ['PortB', 'PortC']
        })
        
        alerts = self.alert_system.check_asset_overlaps(df)
        
        assert len(alerts) == 1
        assert alerts[0].details['overlap_hours'] == 1.5
    
    # Berth Capacity Tests
    
    def test_berth_capacity_exceeded(self):
        """Should detect when berth capacity is exceeded."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_B', 'VESSEL_C'],
            'start_time': [
                datetime(2025, 1, 1, 10, 0),
                datetime(2025, 1, 1, 11, 0),
                datetime(2025, 1, 1, 12, 0)
            ],
            'end_time': [
                datetime(2025, 1, 1, 16, 0),
                datetime(2025, 1, 1, 17, 0),
                datetime(2025, 1, 1, 18, 0)
            ],
            'start_port': ['PortX', 'PortX', 'PortX'],
            'end_port': ['PortA', 'PortA', 'PortA']
        })
        
        berth_capacities = {'PortA': 2}
        alerts = self.alert_system.check_berth_capacity(df, berth_capacities)
        
        assert len(alerts) > 0, "Should detect capacity violation"
        assert alerts[0].alert_type == "BERTH_CAPACITY"
        assert alerts[0].severity == AlertSeverity.WARNING
    
    def test_berth_capacity_within_limit(self):
        """Should NOT alert when capacity is not exceeded."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_B'],
            'start_time': [
                datetime(2025, 1, 1, 10, 0),
                datetime(2025, 1, 1, 11, 0)
            ],
            'end_time': [
                datetime(2025, 1, 1, 16, 0),
                datetime(2025, 1, 1, 17, 0)
            ],
            'start_port': ['PortX', 'PortX'],
            'end_port': ['PortA', 'PortA']
        })
        
        berth_capacities = {'PortA': 2}
        alerts = self.alert_system.check_berth_capacity(df, berth_capacities)
        
        assert len(alerts) == 0, "Should not alert when within capacity"
    
    def test_berth_sequential_arrival(self):
        """Should handle sequential arrivals correctly."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_B', 'VESSEL_C'],
            'start_time': [
                datetime(2025, 1, 1, 10, 0),
                datetime(2025, 1, 1, 16, 0),
                datetime(2025, 1, 1, 22, 0)
            ],
            'end_time': [
                datetime(2025, 1, 1, 16, 0),
                datetime(2025, 1, 1, 22, 0),
                datetime(2025, 1, 2, 4, 0)
            ],
            'start_port': ['PortX', 'PortY', 'PortZ'],
            'end_port': ['PortA', 'PortA', 'PortA']
        })
        
        berth_capacities = {'PortA': 1}
        alerts = self.alert_system.check_berth_capacity(df, berth_capacities)
        
        assert len(alerts) == 0, "Sequential arrivals should not violate capacity"
    
    def test_berth_default_capacity(self):
        """Should use default high capacity when not specified."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0)],
            'start_port': ['PortX'],
            'end_port': ['PortUnknown']
        })
        
        alerts = self.alert_system.check_berth_capacity(df, {})
        
        assert len(alerts) == 0, "Should not alert with default capacity"
    
    # Tight Schedule Tests
    
    def test_tight_schedule_detection(self):
        """Should detect insufficient buffer time between activities."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 17, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 20, 0)],
            'start_port': ['PortA', 'PortC'],
            'end_port': ['PortB', 'PortD']
        })
        
        alerts = self.alert_system.check_tight_schedules(df, min_buffer_hours=2.0)
        
        assert len(alerts) == 1, "Should detect tight schedule"
        assert alerts[0].alert_type == "TIGHT_SCHEDULE"
        assert alerts[0].severity == AlertSeverity.WARNING
        assert alerts[0].details['buffer_hours'] == 1.0
    
    def test_adequate_buffer_time(self):
        """Should NOT alert when buffer time is adequate."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 19, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 22, 0)],
            'start_port': ['PortA', 'PortC'],
            'end_port': ['PortB', 'PortD']
        })
        
        alerts = self.alert_system.check_tight_schedules(df, min_buffer_hours=2.0)
        
        assert len(alerts) == 0, "Should not alert with adequate buffer"
    
    def test_zero_buffer_time(self):
        """Should detect when there's exactly no buffer time."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 16, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 20, 0)],
            'start_port': ['PortA', 'PortB'],
            'end_port': ['PortB', 'PortC']
        })
        
        alerts = self.alert_system.check_tight_schedules(df, min_buffer_hours=2.0)
        
        assert len(alerts) == 1
        assert alerts[0].details['buffer_hours'] == 0.0
    
    def test_tight_schedule_details(self):
        """Should provide detailed tight schedule information."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 17, 30)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 20, 0)],
            'start_port': ['Rotterdam', 'Hamburg'],
            'end_port': ['Hamburg', 'Amsterdam']
        })
        
        alerts = self.alert_system.check_tight_schedules(df, min_buffer_hours=2.0)
        
        assert 'buffer_hours' in alerts[0].details
        assert 'required_hours' in alerts[0].details
        assert 'between' in alerts[0].details
        assert alerts[0].details['buffer_hours'] == 1.5
        assert 'Hamburg' in alerts[0].details['between']
    
    # Edge Cases
    
    def test_empty_dataframe(self):
        """Should handle empty DataFrame gracefully."""
        df = pd.DataFrame({
            'asset': [],
            'start_time': [],
            'end_time': [],
            'start_port': [],
            'end_port': []
        })
        
        overlap_alerts = self.alert_system.check_asset_overlaps(df)
        capacity_alerts = self.alert_system.check_berth_capacity(df)
        tight_alerts = self.alert_system.check_tight_schedules(df)
        
        assert len(overlap_alerts) == 0
        assert len(capacity_alerts) == 0
        assert len(tight_alerts) == 0
    
    def test_single_activity(self):
        """Should handle single activity without errors."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0)],
            'start_port': ['PortA'],
            'end_port': ['PortB']
        })
        
        overlap_alerts = self.alert_system.check_asset_overlaps(df)
        tight_alerts = self.alert_system.check_tight_schedules(df)
        
        assert len(overlap_alerts) == 0
        assert len(tight_alerts) == 0
    
    def test_missing_asset_column(self):
        """Should handle missing asset column gracefully."""
        df = pd.DataFrame({
            'start_time': [datetime(2025, 1, 1, 10, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0)]
        })
        
        alerts = self.alert_system.check_asset_overlaps(df)
        
        assert len(alerts) == 0
    
    def test_complex_multi_conflict_scenario(self):
        """Should handle complex scenario with multiple types of conflicts."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A', 'VESSEL_B', 'VESSEL_B'],
            'start_time': [
                datetime(2025, 1, 1, 10, 0),
                datetime(2025, 1, 1, 14, 0),  # Overlaps with first
                datetime(2025, 1, 1, 10, 0),
                datetime(2025, 1, 1, 17, 30)  # Tight schedule
            ],
            'end_time': [
                datetime(2025, 1, 1, 16, 0),
                datetime(2025, 1, 1, 20, 0),
                datetime(2025, 1, 1, 16, 0),
                datetime(2025, 1, 1, 22, 0)
            ],
            'start_port': ['PortX', 'PortY', 'PortX', 'PortZ'],
            'end_port': ['PortA', 'PortA', 'PortA', 'PortB']
        })
        
        berth_capacities = {'PortA': 2}
        
        overlap_alerts = self.alert_system.check_asset_overlaps(df)
        capacity_alerts = self.alert_system.check_berth_capacity(df, berth_capacities)
        tight_alerts = self.alert_system.check_tight_schedules(df, min_buffer_hours=2.0)
        
        # Should have overlap for VESSEL_A, capacity issue at PortA, and tight schedule for VESSEL_B
        assert len(overlap_alerts) > 0
        assert len(capacity_alerts) > 0  
        assert len(tight_alerts) > 0
    
    # Alert System Tests
    
    def test_get_all_alerts(self):
        """Should retrieve all alerts from the system."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 14, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 18, 0)],
            'start_port': ['PortA', 'PortB'],
            'end_port': ['PortB', 'PortC']
        })
        
        self.alert_system.check_asset_overlaps(df)
        all_alerts = self.alert_system.get_all_alerts()
        
        assert len(all_alerts) > 0
    
    def test_filter_alerts_by_severity(self):
        """Should filter alerts by severity level."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 14, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 18, 0)],
            'start_port': ['PortA', 'PortB'],
            'end_port': ['PortB', 'PortC']
        })
        
        self.alert_system.check_asset_overlaps(df)
        critical_alerts = self.alert_system.get_all_alerts(AlertSeverity.CRITICAL)
        
        assert all(alert.severity == AlertSeverity.CRITICAL for alert in critical_alerts)
    
    def test_generate_report(self):
        """Should generate DataFrame report of alerts."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 14, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 18, 0)],
            'start_port': ['PortA', 'PortB'],
            'end_port': ['PortB', 'PortC']
        })
        
        self.alert_system.check_asset_overlaps(df)
        report = self.alert_system.generate_report()
        
        assert isinstance(report, pd.DataFrame)
        assert len(report) > 0
        assert 'alert_type' in report.columns
        assert 'severity' in report.columns
        assert 'message' in report.columns
    
    def test_clear_alerts(self):
        """Should clear all alerts from the system."""
        df = pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [datetime(2025, 1, 1, 10, 0), datetime(2025, 1, 1, 14, 0)],
            'end_time': [datetime(2025, 1, 1, 16, 0), datetime(2025, 1, 1, 18, 0)],
            'start_port': ['PortA', 'PortB'],
            'end_port': ['PortB', 'PortC']
        })
        
        self.alert_system.check_asset_overlaps(df)
        assert len(self.alert_system.get_all_alerts()) > 0
        
        self.alert_system.clear_alerts()
        assert len(self.alert_system.get_all_alerts()) == 0
    
    # Performance Tests
    
    def test_large_dataset_performance(self):
        """Should handle large dataset efficiently."""
        # Generate large dataset
        n = 1000
        df = pd.DataFrame({
            'asset': [f'VESSEL_{i % 10}' for i in range(n)],
            'start_time': [datetime(2025, 1, 1) + timedelta(hours=i) for i in range(n)],
            'end_time': [datetime(2025, 1, 1) + timedelta(hours=i+2) for i in range(n)],
            'start_port': [f'Port{i % 5}' for i in range(n)],
            'end_port': [f'Port{(i+1) % 5}' for i in range(n)]
        })
        
        # Should complete without hanging
        alerts = self.alert_system.check_asset_overlaps(df)
        
        assert isinstance(alerts, list)
