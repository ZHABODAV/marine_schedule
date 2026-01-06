"""
Bunker Optimization Module

Advanced financial modeling for bunker fuel optimization in maritime operations.
Calculates optimal bunker quantities, ports, and speeds to minimize costs while
meeting schedule constraints.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np


class FuelType(Enum):
    """Types of marine fuel."""
    VLSFO = "Very Low Sulfur Fuel Oil"  # <0.5% sulfur
    MGO = "Marine Gas Oil"  # Distillate fuel
    LSMGO = "Low Sulfur Marine Gas Oil"
    HFO ="Heavy Fuel Oil"  # High sulfur (restricted)
    LNG = "Liquefied Natural Gas"


@dataclass
class BunkerPrice:
    """Bunker fuel price at a specific port."""
    port_id: str
    port_name: str
    fuel_type: FuelType
    price_per_mt: float
    availability_mt: float
    last_updated: datetime
    eca_compliant: bool = True
    
    def get_total_cost(self, quantity_mt: float) -> float:
        """Calculate total cost for a quantity."""
        return quantity_mt * self.price_per_mt


@dataclass
class FuelConsumption:
    """Fuel consumption parameters for a vessel."""
    vessel_id: str
    fuel_type: FuelType
    consumption_at_sea_mt_per_day: float
    consumption_in_port_mt_per_day: float
    speed_kts: float
    eco_speed_kts: float  # Economic speed for fuel saving
    eco_consumption_mt_per_day: float  # Consumption at eco speed
    tank_capacity_mt: float
    min_safe_level_mt: float  # Minimum safe fuel level
    
    def calculate_voyage_consumption(
        self,
        distance_nm: float,
        speed_kts: float,
        port_time_days: float = 0
    ) -> float:
        """
        Calculate total fuel consumption for a voyage.
        
        Parameters:
            distance_nm: Distance in nautical miles
            speed_kts: Speed in knots
            port_time_days: Time spent in port
            
        Returns:
            Total fuel consumption in MT
        """
        sea_time_days = distance_nm / (speed_kts * 24)
        sea_consumption = sea_time_days * self.consumption_at_sea_mt_per_day
        port_consumption = port_time_days * self.consumption_in_port_mt_per_day
        return sea_consumption + port_consumption
    
    def calculate_fuel_savings(self, distance_nm: float) -> Dict[str, float]:
        """
        Calculate potential fuel savings by reducing speed.
        
        Parameters:
            distance_nm: Distance in nautical miles
            
        Returns:
            Dictionary with savings analysis
        """
        normal_time_days = distance_nm / (self.speed_kts * 24)
        normal_consumption = normal_time_days * self.consumption_at_sea_mt_per_day
        
        eco_time_days = distance_nm / (self.eco_speed_kts * 24)
        eco_consumption = eco_time_days * self.eco_consumption_mt_per_day
        
        return {
            'normal_consumption_mt': normal_consumption,
            'eco_consumption_mt': eco_consumption,
            'fuel_savings_mt': normal_consumption - eco_consumption,
            'time_difference_days': eco_time_days - normal_time_days,
            'normal_speed_kts': self.speed_kts,
            'eco_speed_kts': self.eco_speed_kts
        }


@dataclass
class BunkerPlan:
    """Optimized bunker plan for a voyage."""
    voyage_id: str
    vessel_id: str
    total_consumption_mt: float
    bunker_stops: List[Dict]  # List of {port, fuel_type, quantity_mt, cost}
    total_cost_usd: float
    fuel_remaining_mt: float
    optimization_method: str
    savings_vs_baseline_usd: float = 0
    eco_speed_recommended: bool = False
    
    def get_summary(self) -> Dict:
        """Get summary of bunker plan."""
        return {
            'voyage_id': self.voyage_id,
            'vessel_id': self.vessel_id,
            'total_consumption_mt': self.total_consumption_mt,
            'total_cost_usd': self.total_cost_usd,
            'number_of_bunker_stops': len(self.bunker_stops),
            'savings_usd': self.savings_vs_baseline_usd,
            'eco_speed_recommended': self.eco_speed_recommended
        }


class BunkerOptimizer:
    """
    Optimizes bunker fuel procurement and consumption.
    
    Features:
    - Price-based optimization (buy at cheapest ports)
    - Route-based optimization (minimize detours)
    - Speed optimization (eco-speed vs schedule constraints)
    - Multi-fuel type support
    - ECA (Emission Control Area) compliance
    """
    
    def __init__(
        self,
        bunker_prices: List[BunkerPrice],
        fuel_consumption_params: Dict[str, FuelConsumption]
    ):
        """
        Initialize bunker optimizer.
        
        Parameters:
            bunker_prices: List of bunker prices at various ports
            fuel_consumption_params: Fuel consumption data by vessel ID
        """
        self.bunker_prices = bunker_prices
        self.fuel_consumption_params = fuel_consumption_params
        self._build_price_index()
    
    def _build_price_index(self):
        """Build indexed structure for fast price lookups."""
        self.price_index: Dict[Tuple[str, FuelType], BunkerPrice] = {}
        for price in self.bunker_prices:
            key = (price.port_id, price.fuel_type)
            if key not in self.price_index or price.price_per_mt < self.price_index[key].price_per_mt:
                self.price_index[key] = price
    
    def optimize_bunker_plan(
        self,
        voyage_id: str,
        vessel_id: str,
        route_ports: List[str],
        distances_nm: List[float],
        port_times_days: List[float],
        fuel_type: FuelType,
        current_fuel_mt: float,
        allow_eco_speed: bool = True
    ) -> BunkerPlan:
        """
        Create optimized bunker plan for a voyage.
        
        Parameters:
            voyage_id: Voyage identifier
            vessel_id: Vessel identifier
            route_ports: List of ports in sequence
            distances_nm: Distances between consecutive ports
            port_times_days: Time spent at each port
            fuel_type: Type of fuel to use
            current_fuel_mt: Current fuel on board
            allow_eco_speed: Allow eco-speed recommendations
            
        Returns:
            Optimized bunker plan
        """
        if vessel_id not in self.fuel_consumption_params:
            raise ValueError(f"No fuel consumption data for vessel {vessel_id}")
        
        fuel_params = self.fuel_consumption_params[vessel_id]
        
        # Calculate total consumption
        total_consumption = 0
        for i, distance in enumerate(distances_nm):
            port_time = port_times_days[i] if i < len(port_times_days) else 0
            total_consumption += fuel_params.calculate_voyage_consumption(
                distance, fuel_params.speed_kts, port_time
            )
        
        # Check if eco-speed could save fuel
        eco_speed_recommended = False
        if allow_eco_speed:
            savings = fuel_params.calculate_fuel_savings(sum(distances_nm))
            if savings['fuel_savings_mt'] > 0:
                eco_speed_recommended = True
                total_consumption = sum(distances_nm) / (fuel_params.eco_speed_kts * 24) * \
                                  fuel_params.eco_consumption_mt_per_day
        
        # Find optimal bunker ports
        bunker_stops = []
        remaining_fuel = current_fuel_mt
        total_cost = 0
        
        # Pre-calculate prices for the route to enable look-ahead
        route_prices = []
        for port in route_ports:
            price_key = (port, fuel_type)
            price = self.price_index.get(price_key)
            route_prices.append(price)

        for i, port in enumerate(route_ports):
            # Calculate fuel needed to next port
            fuel_needed_to_next = 0
            if i < len(distances_nm):
                distance = distances_nm[i]
                port_time = port_times_days[i] if i < len(port_times_days) else 0
                fuel_needed_to_next = fuel_params.calculate_voyage_consumption(
                    distance,
                    fuel_params.eco_speed_kts if eco_speed_recommended else fuel_params.speed_kts,
                    port_time
                )
            
            # Determine strategy
            current_price = route_prices[i]
            
            # Look ahead for cheaper prices
            cheaper_port_ahead = False
            if current_price:
                for future_price in route_prices[i+1:]:
                    if future_price and future_price.price_per_mt < current_price.price_per_mt:
                        cheaper_port_ahead = True
                        break
            
            quantity_to_bunker = 0
            
            # Strategy 1: Must bunker if we can't reach next port with safety margin
            if remaining_fuel - fuel_needed_to_next < fuel_params.min_safe_level_mt:
                needed = (fuel_needed_to_next + fuel_params.min_safe_level_mt) - remaining_fuel
                quantity_to_bunker = max(quantity_to_bunker, needed)

            # Strategy 2: Opportunistic bunkering (if price is good and we have capacity)
            if current_price and not cheaper_port_ahead:
                # This is the cheapest port for the foreseeable future. Fill up!
                capacity_available = fuel_params.tank_capacity_mt - remaining_fuel
                quantity_to_bunker = max(quantity_to_bunker, capacity_available)
            
            # Execute bunker
            if quantity_to_bunker > 0 and current_price:
                # Cap at availability and tank capacity
                quantity_to_bunker = min(quantity_to_bunker, current_price.availability_mt)
                quantity_to_bunker = min(quantity_to_bunker, fuel_params.tank_capacity_mt - remaining_fuel)
                
                if quantity_to_bunker > 0:
                    cost = current_price.get_total_cost(quantity_to_bunker)
                    
                    bunker_stops.append({
                        'port_id': port,
                        'port_name': current_price.port_name,
                        'fuel_type': fuel_type.value,
                        'quantity_mt': quantity_to_bunker,
                        'price_per_mt': current_price.price_per_mt,
                        'total_cost_usd': cost,
                        'eca_compliant': current_price.eca_compliant
                    })
                    
                    remaining_fuel += quantity_to_bunker
                    total_cost += cost
            
            # Deduct fuel used for this leg
            remaining_fuel -= fuel_needed_to_next
        
        # Calculate savings vs baseline (not bunkering at cheapest ports)
        baseline_cost = self._calculate_baseline_cost(total_consumption, fuel_type)
        savings = baseline_cost - total_cost
        
        return BunkerPlan(
            voyage_id=voyage_id,
            vessel_id=vessel_id,
            total_consumption_mt=total_consumption,
            bunker_stops=bunker_stops,
            total_cost_usd=total_cost,
            fuel_remaining_mt=remaining_fuel,
            optimization_method="price_optimization",
            savings_vs_baseline_usd=savings,
            eco_speed_recommended=eco_speed_recommended
        )
    
    def _calculate_baseline_cost(self, total_consumption_mt: float, fuel_type: FuelType) -> float:
        """Calculate baseline cost using average price."""
        relevant_prices = [p.price_per_mt for p in self.bunker_prices if p.fuel_type == fuel_type]
        if not relevant_prices:
            return 0
        avg_price = sum(relevant_prices) / len(relevant_prices)
        return total_consumption_mt * avg_price
    
    def find_cheapest_bunker_port(
        self,
        fuel_type: FuelType,
        quantity_mt: float,
        ports: Optional[List[str]] = None
    ) -> Optional[BunkerPrice]:
        """
        Find cheapest port to bunker fuel.
        
        Parameters:
            fuel_type: Type of fuel needed
            quantity_mt: Quantity needed
            ports: Optional list of ports to consider (if None, all ports)
            
        Returns:
            BunkerPrice object for cheapest port, or None
        """
        candidates = [
            p for p in self.bunker_prices
            if p.fuel_type == fuel_type and p.availability_mt >= quantity_mt
        ]
        
        if ports:
            candidates = [p for p in candidates if p.port_id in ports]
        
        if not candidates:
            return None
        
        return min(candidates, key=lambda p: p.price_per_mt)
    
    def calculate_hedging_position(
        self,
        total_consumption_mt: float,
        fuel_type: FuelType,
        hedge_percentage: float = 0.7
    ) -> Dict[str, Any]:
        """
        Calculate recommended hedging position for fuel price risk.
        
        Parameters:
            total_consumption_mt: Total expected consumption
            fuel_type: Type of fuel
            hedge_percentage: Percentage to hedge (0-1)
            
        Returns:
            Dictionary with hedging recommendations
        """
        relevant_prices = [p.price_per_mt for p in self.bunker_prices if p.fuel_type == fuel_type]
        
        if not relevant_prices:
            return {}
        
        avg_price = np.mean(relevant_prices)
        price_std = np.std(relevant_prices)
        
        hedge_volume_mt = total_consumption_mt * hedge_percentage
        hedge_value_usd = hedge_volume_mt * avg_price
        
        # Simple VaR calculation (95% confidence)
        var_95 = 1.65 * price_std * hedge_volume_mt
        
        return {
            'hedge_volume_mt': float(hedge_volume_mt),
            'hedge_value_usd': float(hedge_value_usd),
            'average_price': float(avg_price),
            'price_volatility': float(price_std),
            'value_at_risk_95_usd': float(var_95),
            'recommended_hedge_instruments': ['Forward contracts', 'Fuel swaps', 'Options']
        }
    
    def analyze_bunker_market(self, fuel_type: FuelType) -> Dict[str, Any]:
        """
        Analyze bunker market for a fuel type.
        
        Parameters:
            fuel_type: Type of fuel to analyze
            
        Returns:
            Market analysis dictionary
        """
        relevant_prices = [p for p in self.bunker_prices if p.fuel_type == fuel_type]
        
        if not relevant_prices:
            return {}
        
        prices = [p.price_per_mt for p in relevant_prices]
        
        return {
            'fuel_type': fuel_type.value,
            'number_of_ports': len(relevant_prices),
            'average_price': np.mean(prices),
            'min_price': min(prices),
            'max_price': max(prices),
            'price_spread': max(prices) - min(prices),
            'std_deviation': np.std(prices),
            'cheapest_port': min(relevant_prices, key=lambda p: p.price_per_mt).port_name,
            'most_expensive_port': max(relevant_prices, key=lambda p: p.price_per_mt).port_name,
            'total_availability_mt': sum(p.availability_mt for p in relevant_prices)
        }
    
    def generate_bunker_report(self, bunker_plans: List[BunkerPlan]) -> pd.DataFrame:
        """
        Generate comprehensive bunker report from multiple plans.
        
        Parameters:
            bunker_plans: List of bunker plans
            
        Returns:
            DataFrame with bunker analysis
        """
        data = []
        for plan in bunker_plans:
            data.append({
                'Voyage ID': plan.voyage_id,
                'Vessel ID': plan.vessel_id,
                'Total Consumption (MT)': plan.total_consumption_mt,
                'Total Cost (USD)': plan.total_cost_usd,
                'Number of Bunker Stops': len(plan.bunker_stops),
                'Savings (USD)': plan.savings_vs_baseline_usd,
                'Eco Speed Recommended': plan.eco_speed_recommended,
                'Fuel Remaining (MT)': plan.fuel_remaining_mt,
                'Optimization Method': plan.optimization_method
            })
        
        return pd.DataFrame(data)


def create_sample_bunker_prices() -> List[BunkerPrice]:
    """Create sample bunker prices for testing."""
    prices = [
        BunkerPrice("SINGAPORE", "Singapore", FuelType.VLSFO, 650, 50000, datetime.now(), True),
        BunkerPrice("ROTTERDAM", "Rotterdam", FuelType.VLSFO, 620, 40000, datetime.now(), True),
        BunkerPrice("FUJAIRAH", "Fujairah", FuelType.VLSFO, 640, 35000, datetime.now(), True),
        BunkerPrice("HOUSTON", "Houston", FuelType.VLSFO, 670, 30000, datetime.now(), True),
        BunkerPrice("GIBRALTAR", "Gibraltar", FuelType.VLSFO, 630, 20000, datetime.now(), True),
        BunkerPrice("SINGAPORE", "Singapore", FuelType.MGO, 850, 30000, datetime.now(), True),
        BunkerPrice("ROTTERDAM", "Rotterdam", FuelType.MGO, 820, 25000, datetime.now(), True),
    ]
    return prices


def create_sample_fuel_consumption(vessel_id: str) -> FuelConsumption:
    """Create sample fuel consumption parameters."""
    return FuelConsumption(
        vessel_id=vessel_id,
        fuel_type=FuelType.VLSFO,
        consumption_at_sea_mt_per_day=35.0,
        consumption_in_port_mt_per_day=5.0,
        speed_kts=14.5,
        eco_speed_kts=12.0,
        eco_consumption_mt_per_day=25.0,
        tank_capacity_mt=2000,
        min_safe_level_mt=200
    )
