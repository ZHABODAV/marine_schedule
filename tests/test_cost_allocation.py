"""
Comprehensive Tests for Cost Allocation Calculations

Tests include:
- Operational cost allocation
- Overhead cost allocation  
- Other cost allocation
- Total cost calculations
- Cost distribution accuracy
- Edge cases and boundary conditions
"""

import pytest
from dataclasses import dataclass
from typing import Optional
from modules.deepsea_data import CalculatedVoyage as DeepSeaVoyage
from modules.olya_data import CalculatedVoyage as OlyaVoyage


class TestCostAllocationDeepSea:
    """Test cost allocation for Deep Sea voyages."""
    
    def test_basic_cost_allocation(self):
        """Should correctly allocate basic costs."""
        voyage = DeepSeaVoyage(
            voyage_id="TEST_001",
            vessel_id="MV_TEST",
            cargo_type="Coal",
            qty_mt=50000,
            load_port="Rotterdam",
            discharge_port="Shanghai",
            laycan_start="2025-01-01",
            laycan_end="2025-01-10",
            distance_nm=10000,
            days_total=25.0,
            bunker_type="IFO380",
            bunker_price_usd_mt=500.0,
            total_bunker_mt=1200.0,
            bunker_cost_usd=600000.0,
            total_canal_cost_usd=100000.0,
            hire_cost_usd=250000.0,
            operational_cost_allocation=50000.0,
            overhead_cost_allocation=30000.0,
            other_cost_allocation=20000.0
        )
        
        total_cost = voyage.total_cost_usd
        expected_total = 600000 + 100000 + 250000 + 50000 + 30000 + 20000
        
        assert total_cost == expected_total, f"Expected {expected_total}, got {total_cost}"
        assert total_cost == 1050000.0
    
    def test_operational_cost_allocation_only(self):
        """Should correctly calculate when only operational costs are allocated."""
        voyage = DeepSeaVoyage(
            voyage_id="TEST_002",
            vessel_id="MV_TEST",
            cargo_type="Oil",
            qty_mt=75000,
            load_port="Dubai",
            discharge_port="Singapore",
            laycan_start="2025-02-01",
            laycan_end="2025-02-10",
            distance_nm=5000,
            days_total=15.0,
            bunker_type="IFO380",
            bunker_price_usd_mt=500.0,
            total_bunker_mt=800.0,
            bunker_cost_usd=400000.0,
            total_canal_cost_usd=50000.0,
            hire_cost_usd=150000.0,
            operational_cost_allocation=75000.0,
            overhead_cost_allocation=0.0,
            other_cost_allocation=0.0
        )
        
        total_cost = voyage.total_cost_usd
        expected_total = 400000 + 50000 + 150000 + 75000
        
        assert total_cost == expected_total
        assert total_cost == 675000.0
    
    def test_overhead_cost_allocation_only(self):
        """Should correctly calculate when only overhead costs are allocated."""
        voyage = DeepSeaVoyage(
            voyage_id="TEST_003",
            vessel_id="MV_TEST",
            cargo_type="Grain",
            qty_mt=60000,
            load_port="New York",
            discharge_port="Hamburg",
            laycan_start="2025-03-01",
            laycan_end="2025-03-10",
            distance_nm=6000,
            days_total=18.0,
            bunker_type="IFO380",
            bunker_price_usd_mt=500.0,
            total_bunker_mt=900.0,
            bunker_cost_usd=450000.0,
            total_canal_cost_usd=0.0,
            hire_cost_usd=180000.0,
            operational_cost_allocation=0.0,
            overhead_cost_allocation=45000.0,
            other_cost_allocation=0.0
        )
        
        total_cost = voyage.total_cost_usd
        expected_total = 450000 + 180000 + 45000
        
        assert total_cost == expected_total
        assert total_cost == 675000.0
    
    def test_all_cost_components(self):
        """Should correctly sum all cost components including allocations."""
        voyage = DeepSeaVoyage(
            voyage_id="TEST_004",
            vessel_id="MV_ALPHA",
            cargo_type="Iron Ore",
            qty_mt=80000,
            load_port="Port Hedland",
            discharge_port="Qingdao",
            laycan_start="2025-04-01",
            laycan_end="2025-04-15",
            distance_nm=4000,
            days_total=12.0,
            bunker_type="IFO380",
            bunker_price_usd_mt=450.0,
            total_bunker_mt=600.0,
            bunker_cost_usd=270000.0,
            total_canal_cost_usd=0.0,
            hire_cost_usd=120000.0,
            operational_cost_allocation=35000.0,
            overhead_cost_allocation=25000.0,
            other_cost_allocation=15000.0
        )
        
        # Verify each component
        assert voyage.bunker_cost_usd == 270000.0
        assert voyage.total_canal_cost_usd == 0.0
        assert voyage.hire_cost_usd == 120000.0
        assert voyage.operational_cost_allocation == 35000.0
        assert voyage.overhead_cost_allocation == 25000.0
        assert voyage.other_cost_allocation == 15000.0
        
        # Verify total
        assert voyage.total_cost_usd == 465000.0
    
    def test_zero_allocations(self):
        """Should correctly handle zero cost allocations."""
        voyage = DeepSeaVoyage(
            voyage_id="TEST_005",
            vessel_id="MV_BETA",
            cargo_type="Coal",
            qty_mt=50000,
            load_port="Newcastle",
            discharge_port="Mumbai",
            laycan_start="2025-05-01",
            laycan_end="2025-05-10",
            distance_nm=8000,
            days_total=22.0,
            bunker_type="IFO380",
            bunker_price_usd_mt=500.0,
            total_bunker_mt=1100.0,
            bunker_cost_usd=550000.0,
            total_canal_cost_usd=80000.0,
            hire_cost_usd=220000.0,
            operational_cost_allocation=0.0,
            overhead_cost_allocation=0.0,
            other_cost_allocation=0.0
        )
        
        total_cost = voyage.total_cost_usd
        expected_total = 550000 + 80000 + 220000
        
        assert total_cost == expected_total
        assert total_cost == 850000.0


class TestCostAllocationOlya:
    """Test cost allocation for Olya voyages."""
    
    def test_olya_basic_cost_allocation(self):
        """Should correctly allocate costs for Olya voyage."""
        voyage = OlyaVoyage(
            voyage_id="OLYA_001",
            vessel_name="Barge Alpha",
            cargo_name="Grain",
            qty_mt=3000,
            from_port="Balakovo",
            to_port="Olya",
            start_date="2025-01-15",
            end_date="2025-01-20",
            duration_hours=120.0,
            hire_cost_usd=15000.0,
            bunker_cost_usd=5000.0,
            port_cost_usd=2000.0,
            operational_cost_allocation=1000.0,
            overhead_cost_allocation=800.0,
            other_cost_allocation=500.0
        )
        
        total_cost = voyage.total_cost_usd
        expected_total = 15000 + 5000 + 2000 + 1000 + 800 + 500
        
        assert total_cost == expected_total
        assert total_cost == 24300.0
    
    def test_olya_with_transshipment_costs(self):
        """Should include transshipment-specific cost allocations."""
        voyage = OlyaVoyage(
            voyage_id="OLYA_002",
            vessel_name="Barge Beta",
            cargo_name="Wheat",
            qty_mt=2500,
            from_port="Nizhniy Novgorod",
            to_port="Olya",
            start_date="2025-02-01",
            end_date="2025-02-08",
            duration_hours=168.0,
            hire_cost_usd=21000.0,
            bunker_cost_usd=7000.0,
            port_cost_usd=3000.0,
            operational_cost_allocation=2500.0,  # Transshipment coordination
            overhead_cost_allocation=1500.0,  # Administrative overhead
            other_cost_allocation=1000.0  # Misc costs
        )
        
        assert voyage.total_cost_usd == 36000.0
        
        # Verify cost breakdown
        assert voyage.hire_cost_usd == 21000.0
        assert voyage.bunker_cost_usd == 7000.0
        assert voyage.port_cost_usd == 3000.0
        assert voyage.operational_cost_allocation == 2500.0
        assert voyage.overhead_cost_allocation == 1500.0
        assert voyage.other_cost_allocation == 1000.0
    
    def test_olya_zero_allocations(self):
        """Should handle zero cost allocations for Olya."""
        voyage = OlyaVoyage(
            voyage_id="OLYA_003",
            vessel_name="Barge Gamma",
            cargo_name="Barley",
            qty_mt=2000,
            from_port="Saratov",
            to_port="Olya",
            start_date="2025-03-01",
            end_date="2025-03-05",
            duration_hours=96.0,
            hire_cost_usd=12000.0,
            bunker_cost_usd=4000.0,
            port_cost_usd=1500.0,
            operational_cost_allocation=0.0,
            overhead_cost_allocation=0.0,
            other_cost_allocation=0.0
        )
        
        assert voyage.total_cost_usd == 17500.0


class TestCostAllocationEdgeCases:
    """Test edge cases and boundary conditions for cost allocation."""
    
    def test_very_large_cost_values(self):
        """Should handle very large cost values correctly."""
        voyage = DeepSeaVoyage(
            voyage_id="TEST_LARGE",
            vessel_id="MV_ULTRA",
            cargo_type="LNG",
            qty_mt=100000,
            load_port="Qatar",
            discharge_port="Tokyo",
            laycan_start="2025-06-01",
            laycan_end="2025-06-20",
            distance_nm=12000,
            days_total=30.0,
            bunker_type="LNG",
            bunker_price_usd_mt=800.0,
            total_bunker_mt=2000.0,
            bunker_cost_usd=1600000.0,
            total_canal_cost_usd=250000.0,
            hire_cost_usd=750000.0,
            operational_cost_allocation=150000.0,
            overhead_cost_allocation=100000.0,
            other_cost_allocation=50000.0
        )
        
        assert voyage.total_cost_usd == 2900000.0
    
    def test_very_small_cost_values(self):
        """Should handle very small cost values correctly."""
        voyage = OlyaVoyage(
            voyage_id="OLYA_SMALL",
            vessel_name="Small Barge",
            cargo_name="Test Cargo",
            qty_mt=100,
            from_port="Port A",
            to_port="Port B",
            start_date="2025-07-01",
            end_date="2025-07-02",
            duration_hours=24.0,
            hire_cost_usd=500.0,
            bunker_cost_usd=100.0,
            port_cost_usd=50.0,
            operational_cost_allocation=25.0,
            overhead_cost_allocation=15.0,
            other_cost_allocation=10.0
        )
        
        assert voyage.total_cost_usd == 700.0
    
    def test_cost_precision(self):
        """Should maintain precision in cost calculations."""
        voyage = DeepSeaVoyage(
            voyage_id="TEST_PRECISION",
            vessel_id="MV_PRECISE",
            cargo_type="Chemicals",
            qty_mt=25000,
            load_port="Houston",
            discharge_port="Rotterdam",
            laycan_start="2025-08-01",
            laycan_end="2025-08-15",
            distance_nm=7500,
            days_total=20.0,
            bunker_type="MGO",
            bunker_price_usd_mt=750.50,
            total_bunker_mt=500.5,
            bunker_cost_usd=375625.25,
            total_canal_cost_usd=125000.75,
            hire_cost_usd=200000.50,
            operational_cost_allocation=37500.33,
            overhead_cost_allocation=25000.22,
            other_cost_allocation=12500.11
        )
        
        expected = 375625.25 + 125000.75 + 200000.50 + 37500.33 + 25000.22 + 12500.11
        assert abs(voyage.total_cost_usd - expected) < 0.01
    
    def test_default_zero_values(self):
        """Should use default zero values when allocations not specified."""
        # This tests the default parameter values in dataclass
        voyage = DeepSeaVoyage(
            voyage_id="TEST_DEFAULTS",
            vessel_id="MV_DEFAULT",
            cargo_type="Coal",
            qty_mt=40000,
            load_port="Richards Bay",
            discharge_port="Paradip",
            laycan_start="2025-09-01",
            laycan_end="2025-09-10",
            distance_nm=6500,
            days_total=18.0,
            bunker_type="IFO380",
            bunker_price_usd_mt=500.0,
            total_bunker_mt=900.0,
            bunker_cost_usd=450000.0,
            total_canal_cost_usd=0.0,
            hire_cost_usd=180000.0
            # Not specifying allocations - should default to 0
        )
        
        # Should only include bunker, canal, and hire costs
        assert voyage.operational_cost_allocation == 0.0
        assert voyage.overhead_cost_allocation == 0.0
        assert voyage.other_cost_allocation == 0.0
        assert voyage.total_cost_usd == 630000.0


class TestCostAllocationIntegration:
    """Integration tests for cost allocation across multiple voyages."""
    
    def test_total_fleet_cost_allocation(self):
        """Should correctly aggregate costs across multiple voyages."""
        voyages = [
            DeepSeaVoyage(
                voyage_id=f"VOY_{i:03d}",
                vessel_id=f"MV_{i}",
                cargo_type="Coal",
                qty_mt=50000,
                load_port="Port A",
                discharge_port="Port B",
                laycan_start="2025-01-01",
                laycan_end="2025-01-10",
                distance_nm=5000,
                days_total=15.0,
                bunker_type="IFO380",
                bunker_price_usd_mt=500.0,
                total_bunker_mt=750.0,
                bunker_cost_usd=375000.0,
                total_canal_cost_usd=50000.0,
                hire_cost_usd=150000.0,
                operational_cost_allocation=25000.0,
                overhead_cost_allocation=15000.0,
                other_cost_allocation=10000.0
            )
            for i in range(5)
        ]
        
        total_cost = sum(voy.total_cost_usd for voy in voyages)
        expected_cost_per_voyage = 375000 + 50000 + 150000 + 25000 + 15000 + 10000
        expected_total = expected_cost_per_voyage * 5
        
        assert total_cost == expected_total
        assert total_cost == 3125000.0
    
    def test_cost_allocation_distribution(self):
        """Should properly distribute overhead costs proportionally."""
        # Simulate allocating overhead based on voyage duration
        total_overhead = 100000.0
        voyages_data = [
            {'id': 'V1', 'days': 10},
            {'id': 'V2', 'days': 20},
            {'id': 'V3', 'days': 30}
        ]
        
        total_days = sum(v['days'] for v in voyages_data)
        
        voyages = []
        for v in voyages_data:
            overhead_allocation = (v['days'] / total_days) * total_overhead
            
            voyage = DeepSeaVoyage(
                voyage_id=v['id'],
                vessel_id="MV_TEST",
                cargo_type="Coal",
                qty_mt=50000,
                load_port="Port A",
                discharge_port="Port B",
                laycan_start="2025-01-01",
                laycan_end="2025-01-10",
                distance_nm=5000,
                days_total=v['days'],
                bunker_type="IFO380",
                bunker_price_usd_mt=500.0,
                total_bunker_mt=750.0,
                bunker_cost_usd=375000.0,
                total_canal_cost_usd=0.0,
                hire_cost_usd=150000.0,
                operational_cost_allocation=0.0,
                overhead_cost_allocation=overhead_allocation,
                other_cost_allocation=0.0
            )
            voyages.append(voyage)
        
        # Check that overhead is distributed proportionally
        assert abs(voyages[0].overhead_cost_allocation - 16666.67) < 0.01
        assert abs(voyages[1].overhead_cost_allocation - 33333.33) < 0.01
        assert abs(voyages[2].overhead_cost_allocation - 50000.00) < 0.01
        
        # Check that total overhead equals original
        total_allocated = sum(v.overhead_cost_allocation for v in voyages)
        assert abs(total_allocated - total_overhead) < 0.01
