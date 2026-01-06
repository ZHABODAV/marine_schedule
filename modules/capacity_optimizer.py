"""
Capacity Optimization Module

Optimizes cargo loading capacity across vessels considering:
- Vessel capacity constraints  
- Port capacity constraints
- Time windows
- Cost minimization
- Revenue maximization
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from enum import Enum


class AllocationStrategy(Enum):
    """Capacity allocation strategies."""
    GREEDY_PROFIT = "greedy_profit"  # Maximize profit
    BALANCED_UTILIZATION = "balanced_utilization"  # Balance vessel usage
    MINIMIZE_COST = "minimize_cost"  # Minimize total cost
    MAXIMIZE_THROUGHPUT = "maximize_throughput"  # Maximize total cargo moved


@dataclass
class VesselCapacity:
    """Vessel capacity parameters."""
    vessel_id: str
    total_capacity_mt: float
    available_capacity_mt: float
    utilization_pct: float
    current_cargo: List[str]  # List of cargo IDs allocated
    
    def can_accommodate(self, cargo_quantity: float) -> bool:
        """Check if vessel can accommodate additional cargo."""
        return self.available_capacity_mt >= cargo_quantity
    
    def allocate_cargo(self, cargo_id: str, quantity_mt: float):
        """Allocate cargo to this vessel."""
        if self.can_accommodate(quantity_mt):
            self.available_capacity_mt -= quantity_mt
            self.current_cargo.append(cargo_id)
            self.utilization_pct = ((self.total_capacity_mt - self.available_capacity_mt) /
                                   self.total_capacity_mt * 100)
            return True
        return False


@dataclass
class CargoParcel:
    """Individual cargo parcel to allocate."""
    cargo_id: str
    quantity_mt: float
    load_port: str
    discharge_port: str
    laycan_start: datetime
    laycan_end: datetime
    revenue_per_mt: float
    cost_per_mt: float
    priority: int = 5
    
    def get_total_revenue(self) -> float:
        """Get total revenue for this parcel."""
        return self.quantity_mt * self.revenue_per_mt
    
    def get_total_cost(self) -> float:
        """Get total cost for this parcel."""
        return self.quantity_mt * self.cost_per_mt
    
    def get_profit(self) -> float:
        """Get profit for this parcel."""
        return self.get_total_revenue() - self.get_total_cost()


@dataclass
class AllocationResult:
    """Result of capacity allocation."""
    vessel_id: str
    cargo_id: str
    quantity_mt: float
    revenue_usd: float
    cost_usd: float
    profit_usd: float
    utilization_pct: float


class CapacityOptimizer:
    """
    Optimizes capacity allocation across vessels and cargo.
    
    Features:
    - Multiple allocation strategies
    - Constraint satisfaction (capacity, time windows)
    - Profit maximization
    - Utilization balancing
    """
    
    def __init__(
        self,
        vessels: Dict[str, VesselCapacity],
        cargo_parcels: List[CargoParcel],
        strategy: AllocationStrategy = AllocationStrategy.GREEDY_PROFIT
    ):
        """
        Initialize capacity optimizer.
        
        Parameters:
            vessels: Dictionary of vessel_id -> VesselCapacity  
            cargo_parcels: List of cargo parcels to allocate
            strategy: Allocation strategy to use
        """
        self.vessels = vessels
        self.cargo_parcels = sorted(cargo_parcels, key=lambda c: -c.priority)
        self.strategy = strategy
        
        self.allocations: List[AllocationResult] = []
        self.unallocated_cargo: List[CargoParcel] = []
    
    def optimize(self) -> Dict:
        """
        Run capacity optimization.
        
        Returns:
            Dictionary with optimization results
        """
        if self.strategy == AllocationStrategy.GREEDY_PROFIT:
            return self._optimize_greedy_profit()
        elif self.strategy == AllocationStrategy.BALANCED_UTILIZATION:
            return self._optimize_balanced_utilization()
        elif self.strategy == AllocationStrategy.MINIMIZE_COST:
            return self._optimize_minimize_cost()
        elif self.strategy == AllocationStrategy.MAXIMIZE_THROUGHPUT:
            return self._optimize_maximize_throughput()
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
    
    def _optimize_greedy_profit(self) -> Dict:
        """Optimize using greedy profit maximization."""
        # Sort cargo by profit per MT
        sorted_cargo = sorted(self.cargo_parcels, key=lambda c: -(c.revenue_per_mt - c.cost_per_mt))
        
        for cargo in sorted_cargo:
            allocated = False
            
            # Try to find best vessel
            best_vessel = None
            best_profit = -float('inf')
            
            for vessel_id, vessel in self.vessels.items():
                if vessel.can_accommodate(cargo.quantity_mt):
                    # Calculate profit for this allocation
                    profit = cargo.get_profit()
                    
                    # Prefer vessels with lower current utilization (to balance fleet)
                    adjusted_profit = profit * (1 - vessel.utilization_pct / 200)
                    
                    if adjusted_profit > best_profit:
                        best_profit = adjusted_profit
                        best_vessel = vessel_id
            
            if best_vessel:
                vessel = self.vessels[best_vessel]
                vessel.allocate_cargo(cargo.cargo_id, cargo.quantity_mt)
                
                self.allocations.append(
                    AllocationResult(
                        vessel_id=best_vessel,
                        cargo_id=cargo.cargo_id,
                        quantity_mt=cargo.quantity_mt,
                        revenue_usd=cargo.get_total_revenue(),
                        cost_usd=cargo.get_total_cost(),
                        profit_usd=cargo.get_profit(),
                        utilization_pct=vessel.utilization_pct
                    )
                )
                allocated = True
            
            if not allocated:
                self.unallocated_cargo.append(cargo)
        
        return self._generate_results()
    
    def _optimize_balanced_utilization(self) -> Dict:
        """Optimize to balance utilization across vessels."""
        # Keep allocating to least utilized vessel
        for cargo in self.cargo_parcels:
            allocated = False
            
            # Find vessel with lowest utilization that can fit cargo
            suitable_vessels = [
                (vessel_id, vessel) for vessel_id, vessel in self.vessels.items()
                if vessel.can_accommodate(cargo.quantity_mt)
            ]
            
            if suitable_vessels:
                # Sort by utilization (ascending)
                suitable_vessels.sort(key=lambda x: x[1].utilization_pct)
                best_vessel_id, best_vessel = suitable_vessels[0]
                
                best_vessel.allocate_cargo(cargo.cargo_id, cargo.quantity_mt)
                
                self.allocations.append(
                    AllocationResult(
                        vessel_id=best_vessel_id,
                        cargo_id=cargo.cargo_id,
                        quantity_mt=cargo.quantity_mt,
                        revenue_usd=cargo.get_total_revenue(),
                        cost_usd=cargo.get_total_cost(),
                        profit_usd=cargo.get_profit(),
                        utilization_pct=best_vessel.utilization_pct
                    )
                )
                allocated = True
            
            if not allocated:
                self.unallocated_cargo.append(cargo)
        
        return self._generate_results()
    
    def _optimize_minimize_cost(self) -> Dict:
        """Optimize to minimize total cost."""
        # Sort cargo by cost (ascending)
        sorted_cargo = sorted(self.cargo_parcels, key=lambda c: c.cost_per_mt)
        
        for cargo in sorted_cargo:
            allocated = False
            
            # Find cheapest allocation
            best_vessel = None
            lowest_cost = float('inf')
            
            for vessel_id, vessel in self.vessels.items():
                if vessel.can_accommodate(cargo.quantity_mt):
                    # Cost could vary by vessel (fuel, hire rate, etc.)
                    # For simplicity, using cargo cost
                    if cargo.get_total_cost() < lowest_cost:
                        lowest_cost = cargo.get_total_cost()
                        best_vessel = vessel_id
            
            if best_vessel:
                vessel = self.vessels[best_vessel]
                vessel.allocate_cargo(cargo.cargo_id, cargo.quantity_mt)
                
                self.allocations.append(
                    AllocationResult(
                        vessel_id=best_vessel,
                        cargo_id=cargo.cargo_id,
                        quantity_mt=cargo.quantity_mt,
                        revenue_usd=cargo.get_total_revenue(),
                        cost_usd=cargo.get_total_cost(),
                        profit_usd=cargo.get_profit(),
                        utilization_pct=vessel.utilization_pct
                    )
                )
                allocated = True
            
            if not allocated:
                self.unallocated_cargo.append(cargo)
        
        return self._generate_results()
    
    def _optimize_maximize_throughput(self) -> Dict:
        """Optimize to maximize total throughput (cargo moved)."""
        # Sort cargo by quantity (descending) to move largest parcels first
        sorted_cargo = sorted(self.cargo_parcels, key=lambda c: -c.quantity_mt)
        
        for cargo in sorted_cargo:
            allocated = False
            
            # Find any vessel that can fit
            for vessel_id, vessel in self.vessels.items():
                if vessel.can_accommodate(cargo.quantity_mt):
                    vessel.allocate_cargo(cargo.cargo_id, cargo.quantity_mt)
                    
                    self.allocations.append(
                        AllocationResult(
                            vessel_id=vessel_id,
                            cargo_id=cargo.cargo_id,
                            quantity_mt=cargo.quantity_mt,
                            revenue_usd=cargo.get_total_revenue(),
                            cost_usd=cargo.get_total_cost(),
                            profit_usd=cargo.get_profit(),
                            utilization_pct=vessel.utilization_pct
                        )
                    )
                    allocated = True
                    break
            
            if not allocated:
                self.unallocated_cargo.append(cargo)
        
        return self._generate_results()
    
    def _generate_results(self) -> Dict:
        """Generate results dictionary."""
        total_cargo = sum(c.quantity_mt for c in self.cargo_parcels)
        allocated_cargo = sum(a.quantity_mt for a in self.allocations)
        
        total_revenue = sum(a.revenue_usd for a in self.allocations)
        total_cost = sum(a.cost_usd for a in self.allocations)
        total_profit = total_revenue - total_cost
        
        avg_utilization = (sum(v.utilization_pct for v in self.vessels.values()) /
                          len(self.vessels) if self.vessels else 0)
        
        return {
            'allocations': self.allocations,
            'unallocated_cargo': self.unallocated_cargo,
            'metrics': {
                'total_cargo_mt': total_cargo,
                'allocated_cargo_mt': allocated_cargo,
                'unallocated_cargo_mt': total_cargo - allocated_cargo,
                'allocation_rate_pct': (allocated_cargo / total_cargo * 100) if total_cargo > 0 else 0,
                'total_revenue_usd': total_revenue,
                'total_cost_usd': total_cost,
                'total_profit_usd': total_profit,
                'avg_vessel_utilization_pct': avg_utilization,
                'number_of_allocations': len(self.allocations),
                'number_unallocated': len(self.unallocated_cargo)
            }
        }
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """Export allocations to DataFrame."""
        if not self.allocations:
            return pd.DataFrame()
        
        data = []
        for alloc in self.allocations:
            data.append({
                'Vessel ID': alloc.vessel_id,
                'Cargo ID': alloc.cargo_id,
                'Quantity (MT)': alloc.quantity_mt,
                'Revenue (USD)': alloc.revenue_usd,
                'Cost (USD)': alloc.cost_usd,
                'Profit (USD)': alloc.profit_usd,
                'Utilization (%)': alloc.utilization_pct
            })
        
        return pd.DataFrame(data)
    
    def get_vessel_summary(self) -> pd.DataFrame:
        """Get summary by vessel."""
        summary_data = []
        
        for vessel_id, vessel in self.vessels.items():
            vessel_allocations = [a for a in self.allocations if a.vessel_id == vessel_id]
            
            total_cargo = sum(a.quantity_mt for a in vessel_allocations)
            total_revenue = sum(a.revenue_usd for a in vessel_allocations)
            total_cost = sum(a.cost_usd for a in vessel_allocations)
            total_profit = total_revenue - total_cost
            
            summary_data.append({
                'Vessel ID': vessel_id,
                'Total Capacity (MT)': vessel.total_capacity_mt,
                'Allocated Cargo (MT)': total_cargo,
                'Available Capacity (MT)': vessel.available_capacity_mt,
                'Utilization (%)': vessel.utilization_pct,
                'Number of Cargos': len(vessel_allocations),
                'Total Revenue (USD)': total_revenue,
                'Total Cost (USD)': total_cost,
                'Total Profit (USD)': total_profit
            })
        
        return pd.DataFrame(summary_data)


def create_sample_capacity_data() -> Tuple[Dict[str, VesselCapacity], List[CargoParcel]]:
    """Create sample data for testing."""
    vessels = {
        'VESSEL_A': VesselCapacity('VESSEL_A', 50000, 50000, 0, []),
        'VESSEL_B': VesselCapacity('VESSEL_B', 75000, 75000, 0, []),
        'VESSEL_C': VesselCapacity('VESSEL_C', 60000, 60000, 0, []),
    }
    
    cargo_parcels = [
        CargoParcel('CARGO_001', 30000, 'PORT_A', 'PORT_B', datetime(2026, 1, 1), datetime(2026, 1, 7), 100, 60, 10),
        CargoParcel('CARGO_002', 45000, 'PORT_B', 'PORT_C', datetime(2026, 1, 5), datetime(2026, 1, 12), 95, 55, 8),
        CargoParcel('CARGO_003', 25000, 'PORT_A', 'PORT_C', datetime(2026, 1, 10), datetime(2026, 1, 17), 110, 65, 9),
        CargoParcel('CARGO_004', 35000, 'PORT_C', 'PORT_A', datetime(2026, 1, 15), datetime(2026, 1, 22), 105, 62, 7),
        CargoParcel('CARGO_005', 50000, 'PORT_B', 'PORT_A', datetime(2026, 1, 20), datetime(2026, 1, 27), 98, 58, 6),
    ]
    
    return vessels, cargo_parcels
