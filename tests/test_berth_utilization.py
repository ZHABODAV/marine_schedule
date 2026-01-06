import unittest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.berth_utilization import BerthUtilizationAnalyzer

class TestBerthUtilization(unittest.TestCase):
    
    def setUp(self):
        # Create dummy voyage data
        # 3 vessels occupying the port for 24 hours each on the same day
        self.data = pd.DataFrame([
            {
                'start_port': 'TEST_PORT',
                'end_port': 'OTHER_PORT',
                'start_time': datetime(2025, 1, 1, 0, 0),
                'end_time': datetime(2025, 1, 1, 23, 59),
                'duration_hours': 24.0
            },
            {
                'start_port': 'TEST_PORT',
                'end_port': 'OTHER_PORT',
                'start_time': datetime(2025, 1, 1, 0, 0),
                'end_time': datetime(2025, 1, 1, 23, 59),
                'duration_hours': 24.0
            },
            {
                'start_port': 'TEST_PORT',
                'end_port': 'OTHER_PORT',
                'start_time': datetime(2025, 1, 1, 0, 0),
                'end_time': datetime(2025, 1, 1, 23, 59),
                'duration_hours': 24.0
            }
        ])
        
        self.analyzer = BerthUtilizationAnalyzer(self.data)

    def test_multi_berth_utilization(self):
        """
        Verify that utilization is calculated correctly for multi-berth ports.
        
        Scenario:
        - 3 vessels dock for 24 hours each on the same day.
        - Total occupation hours = 72.
        - Period hours = 24.
        
        If berth_count = 1, utilization should be 300%.
        If berth_count = 3, utilization should be 100%.
        If berth_count = 4, utilization should be 75%.
        """
        
        start = datetime(2025, 1, 1, 0, 0)
        end = datetime(2025, 1, 2, 0, 0)
        
        # Test with default (1 berth) - legacy behavior check
        metrics_1 = self.analyzer.calculate_port_utilization(
            'TEST_PORT', start_date=start, end_date=end, berth_count=1
        )
        self.assertAlmostEqual(metrics_1['utilization_rate_percent'], 300.0, delta=1.0)
        
        # Test with 3 berths
        metrics_3 = self.analyzer.calculate_port_utilization(
            'TEST_PORT', start_date=start, end_date=end, berth_count=3
        )
        self.assertAlmostEqual(metrics_3['utilization_rate_percent'], 100.0, delta=1.0)
        
        # Test with 4 berths
        metrics_4 = self.analyzer.calculate_port_utilization(
            'TEST_PORT', start_date=start, end_date=end, berth_count=4
        )
        self.assertAlmostEqual(metrics_4['utilization_rate_percent'], 75.0, delta=1.0)

if __name__ == '__main__':
    unittest.main()
