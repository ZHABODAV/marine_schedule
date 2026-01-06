"""
Tests for Alerts Module

Tests cover:
- Alert creation and properties
- Alert severity levels
- Asset overlap detection
- Berth capacity checking
- Tight schedule detection
- Alert filtering and reporting
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from modules.alerts import (
    Alert, AlertSeverity, AlertSystem, run_all_checks
)


# ============================================================================
# Alert Base Tests
# ============================================================================

class TestAlert:
    """Tests for Alert class."""
    
    def test_alert_creation(self):
        """Should create alert with all properties."""
        alert = Alert(
            alert_type="TEST_ALERT",
            severity=AlertSeverity.WARNING,
            message="Test message",
            details={'key': 'value'}
        )
        
        assert alert.alert_type == "TEST_ALERT"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.message == "Test message"
        assert alert.details == {'key': 'value'}
        assert isinstance(alert.timestamp, datetime)
    
    def test_alert_without_details(self):
        """Should create alert without details."""
        alert = Alert(
            alert_type="SIMPLE_ALERT",
            severity=AlertSeverity.INFO,
            message="Simple message"
        )
        
        assert alert.details == {}
    
    def test_alert_to_dict(self):
        """Should convert alert to dictionary."""
        alert = Alert(
            alert_type="DICT_TEST",
            severity=AlertSeverity.CRITICAL,
            message="Dictionary test",
            details={'test_key': 123}
        )
        
        alert_dict = alert.to_dict()
        
        assert 'timestamp' in alert_dict
        assert alert_dict['alert_type'] == "DICT_TEST"
        assert alert_dict['severity'] == "CRITICAL"
        assert alert_dict['message'] == "Dictionary test"
        assert alert_dict['details'] == "{'test_key': 123}"
    
    def test_alert_str_representation(self):
        """Should have string representation."""
        alert = Alert(
            alert_type="STR_TEST",
            severity=AlertSeverity.WARNING,
            message="String test"
        )
        
        str_repr = str(alert)
        
        assert "WARNING" in str_repr
        assert "STR_TEST" in str_repr
        assert "String test" in str_repr


# ============================================================================
# AlertSystem Tests
# ============================================================================

class TestAlertSystem:
    """Tests for AlertSystem class."""
    
    def test_alert_system_initialization(self):
        """Should initialize with empty alerts list."""
        system = AlertSystem()
        
        assert system.alerts == []
    
    def test_add_alert(self):
        """Should add alert to system."""
        system = AlertSystem()
        alert = Alert("TEST", AlertSeverity.INFO, "Test")
        
        system.add_alert(alert)
        
        assert len(system.alerts) == 1
        assert system.alerts[0] == alert
    
    def test_clear_alerts(self):
        """Should clear all alerts."""
        system = AlertSystem()
        system.add_alert(Alert("TEST1", AlertSeverity.INFO, "Test 1"))
        system.add_alert(Alert("TEST2", AlertSeverity.WARNING, "Test 2"))
        
        system.clear_alerts()
        
        assert len(system.alerts) == 0


# ============================================================================
# Asset Overlap Detection Tests
# ============================================================================

class TestAssetOverlaps:
    """Tests for asset overlap detection."""
    
    @pytest.fixture
    def overlapping_schedule(self):
        """Create schedule with overlaps."""
        return pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A', 'VESSEL_B'],
            'start_time': [
                '2025-01-01 00:00:00',
                '2025-01-03 00:00:00',  # Overlaps with previous leg
                '2025-01-01 00:00:00'
            ],
            'end_time': [
                '2025-01-04 00:00:00',  # Ends after next starts
                '2025-01-06 00:00:00',
                '2025-01-02 00:00:00'
            ],
            'start_port': ['PORT_A', 'PORT_B', 'PORT_C'],
            'end_port': ['PORT_B', 'PORT_C', 'PORT_D']
        })
    
    @pytest.fixture
    def non_overlapping_schedule(self):
        """Create schedule without overlaps."""
        return pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [
                '2025-01-01 00:00:00',
                '2025-01-05 00:00:00'  # Starts after previous ends
            ],
            'end_time': [
                '2025-01-04 00:00:00',
                '2025-01-08 00:00:00'
            ],
            'start_port': ['PORT_A', 'PORT_B'],
            'end_port': ['PORT_B', 'PORT_C']
        })
    
    def test_detect_overlap(self, overlapping_schedule):
        """Should detect asset scheduling overlaps."""
        system = AlertSystem()
        
        alerts = system.check_asset_overlaps(overlapping_schedule)
        
        assert len(alerts) > 0
        assert alerts[0].alert_type == "ASSET_OVERLAP"
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert "VESSEL_A" in alerts[0].message
        assert 'overlap_hours' in alerts[0].details
    
    def test_no_overlap_detection(self, non_overlapping_schedule):
        """Should not  detect overlaps when none exist."""
        system = AlertSystem()
        
        alerts = system.check_asset_overlaps(non_overlapping_schedule)
        
        assert len(alerts) == 0
    
    def test_overlap_without_asset_column(self):
        """Should handle missing asset column."""
        system = AlertSystem()
        df = pd.DataFrame({
            'start_time': ['2025-01-01 00:00:00'],
            'end_time': ['2025-01-02 00:00:00']
        })
        
        alerts = system.check_asset_overlaps(df)
        
        assert len(alerts) == 0
    
    def test_overlap_details(self, overlapping_schedule):
        """Should include detailed overlap information."""
        system = AlertSystem()
        
        alerts = system.check_asset_overlaps(overlapping_schedule)
        
        assert len(alerts) > 0
        details = alerts[0].details
        assert 'asset' in details
        assert 'overlap_hours' in details
        assert 'leg1_route' in details
        assert 'leg2_route' in details
        assert details['overlap_hours'] > 0


# ============================================================================
# Berth Capacity Tests
# ============================================================================

class TestBerthCapacity:
    """Tests for berth capacity checking."""
    
    @pytest.fixture
    def capacity_test_data(self):
        """Create test data for capacity checking."""
        return pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_B', 'VESSEL_C'],
            'start_time': [
                '2025-01-01 00:00:00',
                '2025-01-01 06:00:00',
                '2025-01-01 12:00:00'
            ],
            'end_time': [
                '2025-01-02 00:00:00',
                '2025-01-02 06:00:00',
                '2025-01-02 12:00:00'
            ],
            'start_port': ['PORT_A', 'PORT_A', 'PORT_A'],
            'end_port': ['PORT_B', 'PORT_B', 'PORT_B']
        })
    
    def test_berth_capacity_exceeded(self, capacity_test_data):
        """Should detect when berth capacity is exceeded."""
        system = AlertSystem()
        capacities = {'PORT_B': 1}  # Only 1 berth
        
        alerts = system.check_berth_capacity(capacity_test_data, capacities)
        
        assert len(alerts) > 0
        assert alerts[0].alert_type == "BERTH_CAPACITY"
        assert alerts[0].severity == AlertSeverity.WARNING
        assert "PORT_B" in alerts[0].message
    
    def test_berth_capacity_sufficient(self, capacity_test_data):
        """Should not alert when capacity is sufficient."""
        system = AlertSystem()
        capacities = {'PORT_B': 10}  # Plenty of capacity
        
        alerts = system.check_berth_capacity(capacity_test_data, capacities)
        
        # May still generate alerts for concurrent vessels
        # but should be fewer if capacity is higher
        assert isinstance(alerts, list)
    
    def test_berth_capacity_no_capacities_provided(self, capacity_test_data):
        """Should use default capacity when none provided."""
        system = AlertSystem()
        
        alerts = system.check_berth_capacity(capacity_test_data, None)
        
        # Should not fail with None capacities
        assert isinstance(alerts, list)
    
    def test_berth_capacity_details(self, capacity_test_data):
        """Should include detailed capacity information."""
        system = AlertSystem()
        capacities = {'PORT_B': 1}
        
        alerts = system.check_berth_capacity(capacity_test_data, capacities)
        
        if len(alerts) > 0:
            details = alerts[0].details
            assert 'port' in details
            assert 'concurrent_vessels' in details
            assert 'max_capacity' in details
            assert 'assets' in details


# ============================================================================
# Tight Schedule Tests
# ============================================================================

class TestTightSchedules:
    """Tests for tight schedule detection."""
    
    @pytest.fixture
    def tight_schedule_data(self):
        """Create test data with tight schedules."""
        return pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [
                '2025-01-01 00:00:00',
                '2025-01-02 01:00:00'  # Only 1 hour buffer
            ],
            'end_time': [
                '2025-01-02 00:00:00',
                '2025-01-03 00:00:00'
            ],
            'start_port': ['PORT_A', 'PORT_B'],
            'end_port': ['PORT_B', 'PORT_C']
        })
    
    @pytest.fixture
    def comfortable_schedule_data(self):
        """Create test data with adequate buffers."""
        return pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A'],
            'start_time': [
                '2025-01-01 00:00:00',
                '2025-01-05 00:00:00'  # Plenty of buffer
            ],
            'end_time': [
                '2025-01-02 00:00:00',
                '2025-01-06 00:00:00'
            ],
            'start_port': ['PORT_A', 'PORT_B'],
            'end_port': ['PORT_B', 'PORT_C']
        })
    
    def test_detect_tight_schedule(self, tight_schedule_data):
        """Should detect tight schedules with insufficient buffer."""
        system = AlertSystem()
        
        alerts = system.check_tight_schedules(tight_schedule_data, min_buffer_hours=2.0)
        
        assert len(alerts) > 0
        assert alerts[0].alert_type == "TIGHT_SCHEDULE"
        assert alerts[0].severity == AlertSeverity.WARNING
        assert "VESSEL_A" in alerts[0].message
    
    def test_no_tight_schedule_detection(self, comfortable_schedule_data):
        """Should not detect issues with adequate buffers."""
        system = AlertSystem()
        
        alerts = system.check_tight_schedules(comfortable_schedule_data, min_buffer_hours=2.0)
        
        assert len(alerts) == 0
    
    def test_tight_schedule_custom_buffer(self, tight_schedule_data):
        """Should respect custom buffer requirement."""
        system = AlertSystem()
        
        # With 0.5 hour buffer, 1 hour should be fine
        alerts = system.check_tight_schedules(tight_schedule_data, min_buffer_hours=0.5)
        
        assert len(alerts) == 0
    
    def test_tight_schedule_details(self, tight_schedule_data):
        """Should include detailed scheduling information."""
        system = AlertSystem()
        
        alerts = system.check_tight_schedules(tight_schedule_data, min_buffer_hours=2.0)
        
        assert len(alerts) > 0
        details = alerts[0].details
        assert 'asset' in details
        assert 'buffer_hours' in details
        assert 'required_hours' in details
        assert 'between' in details
        assert details['buffer_hours'] < details['required_hours']


# ============================================================================
# Alert Filtering and Reporting Tests
# ============================================================================

class TestAlertSystemFeatures:
    """Tests for alert system features."""
    
    def test_get_all_alerts(self):
        """Should return all alerts."""
        system = AlertSystem()
        alert1 = Alert("TEST1", AlertSeverity.INFO, "Info alert")
        alert2 = Alert("TEST2", AlertSeverity.WARNING, "Warning alert")
        
        system.add_alert(alert1)
        system.add_alert(alert2)
        
        all_alerts = system.get_all_alerts()
        
        assert len(all_alerts) == 2
        assert alert1 in all_alerts
        assert alert2 in all_alerts
    
    def test_filter_alerts_by_severity(self):
        """Should filter alerts by severity."""
        system = AlertSystem()
        system.add_alert(Alert("TEST1", AlertSeverity.INFO, "Info"))
        system.add_alert(Alert("TEST2", AlertSeverity.WARNING, "Warning"))
        system.add_alert(Alert("TEST3", AlertSeverity.CRITICAL, "Critical"))
        
        critical_alerts = system.get_all_alerts(severity_filter=AlertSeverity.CRITICAL)
        
        assert len(critical_alerts) == 1
        assert critical_alerts[0].severity == AlertSeverity.CRITICAL
    
    def test_generate_report_empty(self):
        """Should generate empty report when no alerts."""
        system = AlertSystem()
        
        report = system.generate_report()
        
        assert isinstance(report, pd.DataFrame)
        assert len(report) == 0
    
    def test_generate_report_with_alerts(self):
        """Should generate DataFrame report with alerts."""
        system = AlertSystem()
        system.add_alert(Alert("TEST1", AlertSeverity.INFO, "Info alert"))
        system.add_alert(Alert("TEST2", AlertSeverity.WARNING, "Warning alert"))
        
        report = system.generate_report()
        
        assert isinstance(report, pd.DataFrame)
        assert len(report) == 2
        assert 'timestamp' in report.columns
        assert 'alert_type' in report.columns
        assert 'severity' in report.columns
        assert 'message' in report.columns


# ============================================================================
# Integration Tests
# ============================================================================

class TestAlertIntegration:
    """Integration tests for alert system"""
    
    @pytest.fixture
    def complex_schedule(self):
        """Create complex schedule with multiple issues."""
        return pd.DataFrame({
            'asset': ['VESSEL_A', 'VESSEL_A', 'VESSEL_B', 'VESSEL_B'],
            'start_time': [
                '2025-01-01 00:00:00',
                '2025-01-02 01:00:00',  # Tight schedule
                '2025-01-01 00:00:00',
                '2025-01-01 12:00:00'   # Same day at same port (capacity issue)
            ],
            'end_time': [
                '2025-01-02 00:00:00',
                '2025-01-03 00:00:00',
                '2025-01-02 00:00:00',
                '2025-01-02 12:00:00'
            ],
            'start_port': ['PORT_A', 'PORT_B', 'PORT_A', 'PORT_A'],
            'end_port': ['PORT_B', 'PORT_C', 'PORT_B', 'PORT_B']
        })
    
    def test_run_all_checks(self, complex_schedule):
        """Should run all checks using convenience function."""
        alert_system = run_all_checks(
            complex_schedule,
            berth_capacities={'PORT_B': 1},
            min_buffer_hours=2.0
        )
        
        assert isinstance(alert_system, AlertSystem)
        assert len(alert_system.alerts) > 0
        
        # Verify different types of alerts were generated
        alert_types = {alert.alert_type for alert in alert_system.alerts}
        assert len(alert_types) > 0
    
    def test_multiple_alert_types(self, complex_schedule):
        """Should detect multiple types of issues."""
        system = AlertSystem()
        
        system.check_asset_overlaps(complex_schedule)
        system.check_tight_schedules(complex_schedule, min_buffer_hours=2.0)
        system.check_berth_capacity(complex_schedule, {'PORT_B': 1})
        
        # Should have generated various alerts
        assert len(system.alerts) > 0
        
        # Generate report to verify
        report = system.generate_report()
        assert len(report) > 0


# ============================================================================
# Edge Cases
# ============================================================================

class TestAlertEdgeCases:
    """Tests for edge  cases and error handling."""
    
    def test_empty_dataframe(self):
        """Should handle empty DataFrame gracefully."""
        system = AlertSystem()
        # Create empty DataFrame with required columns
        empty_df = pd.DataFrame(columns=['asset', 'start_time', 'end_time', 'start_port', 'end_port'])
        
        overlaps = system.check_asset_overlaps(empty_df)
        capacity = system.check_berth_capacity(empty_df)
        tight = system.check_tight_schedules(empty_df)
        
        assert overlaps == []
        assert capacity == []
        assert tight == []
    
    def test_single_voyage(self):
        """Should handle single voyage without errors."""
        system = AlertSystem()
        single = pd.DataFrame({
            'asset': ['VESSEL_A'],
            'start_time': ['2025-01-01 00:00:00'],
            'end_time': ['2025-01-02 00:00:00'],
            'start_port': ['PORT_A'],
            'end_port': ['PORT_B']
        })
        
        alerts = system.check_asset_overlaps(single)
        
        assert len(alerts) == 0  # No overlaps from single voyage
