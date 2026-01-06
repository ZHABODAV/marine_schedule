import unittest
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.bunker_optimizer import BunkerOptimizer, BunkerPrice, FuelConsumption, FuelType

class TestBunkerLogic(unittest.TestCase):
    
    def setUp(self):
        # Setup basic prices
        self.prices = [
            BunkerPrice("PORT_A", "Port A", FuelType.VLSFO, 500.0, 10000, datetime.now(), True), # Cheap
            BunkerPrice("PORT_B", "Port B", FuelType.VLSFO, 800.0, 10000, datetime.now(), True), # Expensive
            BunkerPrice("PORT_C", "Port C", FuelType.VLSFO, 600.0, 10000, datetime.now(), True), # Moderate
        ]
        
        # Setup vessel consumption
        self.fuel_params = {
            "VESSEL_1": FuelConsumption(
                vessel_id="VESSEL_1",
                fuel_type=FuelType.VLSFO,
                consumption_at_sea_mt_per_day=20.0,
                consumption_in_port_mt_per_day=2.0,
                speed_kts=12.0,
                eco_speed_kts=10.0,
                eco_consumption_mt_per_day=15.0,
                tank_capacity_mt=1000.0,
                min_safe_level_mt=100.0
            )
        }
        
        self.optimizer = BunkerOptimizer(self.prices, self.fuel_params)

    def test_look_ahead_optimization(self):
        """
        Scenario:
        Route: Port A -> Port B -> Port C
        Distances: A->B (1000nm), B->C (1000nm)
        
        Logic:
        - Port A is cheap ($500)
        - Port B is expensive ($800)
        - Port C is moderate ($600)
        
        The vessel starts at Port A with low fuel.
        It should fill up at Port A enough to cover the leg to B AND the leg to C (or max capacity),
        avoiding purchase at Port B.
        """
        
        # 1000nm @ 12kts = ~3.5 days. 20mt/day = ~70mt consumption per leg.
        # Total needed A->C = ~140mt.
        
        plan = self.optimizer.optimize_bunker_plan(
            voyage_id="TEST_VOYAGE",
            vessel_id="VESSEL_1",
            route_ports=["PORT_A", "PORT_B", "PORT_C"],
            distances_nm=[1000.0, 1000.0],
            port_times_days=[1.0, 1.0, 1.0],
            fuel_type=FuelType.VLSFO,
            current_fuel_mt=150.0, # Just above reserve
            allow_eco_speed=False
        )
        
        # Check stops
        stops = plan.bunker_stops
        
        # Should bunker at Port A
        stop_a = next((s for s in stops if s['port_id'] == 'PORT_A'), None)
        self.assertIsNotNone(stop_a, "Should bunker at Port A")
        
        # Should NOT bunker at Port B (it's expensive and we should have bought enough at A)
        stop_b = next((s for s in stops if s['port_id'] == 'PORT_B'), None)
        self.assertIsNone(stop_b, "Should NOT bunker at Port B")
        
        # Verify quantity at A is substantial (more than just needed for A->B)
        # Needed for A->B is ~70mt. If it buys > 100mt, it's looking ahead.
        self.assertGreater(stop_a['quantity_mt'], 100.0, "Should buy extra fuel at cheap port A")

if __name__ == '__main__':
    unittest.main()
