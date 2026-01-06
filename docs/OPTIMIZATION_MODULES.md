# Optimization Modules - Complete Reference

This document describes all optimization modules implemented in the Maritime Voyage Planner system.

## Overview

The system includes 6 comprehensive optimization modules:

1. **Bunker Optimization** - Fuel procurement and consumption
2. **Route Optimization** - Vessel routing and path planning
3. **Capacity Optimization** - Cargo allocation and capacity management
4. **Berth Utilization** - Port berth utilization analysis
5. **Year Schedule Optimization** - Long-term fleet scheduling
6. **Voyage Calculation** - Individual voyage optimization

---

## 1. Bunker Optimization Module

**File:** [`modules/bunker_optimizer.py`](../modules/bunker_optimizer.py)

### Features

- **Price-based optimization**: Buy fuel at cheapest ports
- **Route-based optimization**: Minimize detours for bunkering
- **Speed optimization**: Eco-speed vs schedule constraints
- **Multi-fuel type support**: VLSFO, MGO, HFO, LNG
- **ECA compliance**: Emission Control Area fuel requirements
- **Hedging support**: Fuel price risk management

### Key Classes

#### `BunkerOptimizer`
Main optimization engine for bunker fuel planning.

**Methods:**
- `optimize_bunker_plan()` - Create optimized bunker plan for a voyage
- `find_cheapest_bunker_port()` - Find cheapest port for specific fuel type
- `calculate_hedging_position()` - Calculate recommended hedging for price risk
- `analyze_bunker_market()` - Analyze bunker market for a fuel type

#### `BunkerPrice`
Represents bunker fuel price at a specific port.

**Attributes:**
- `port_id`, `port_name`
- `fuel_type` - Type of fuel (Enum)
- `price_per_mt` - Price per metric ton
- `availability_mt` - Available quantity
- `eca_compliant` - ECA compliance flag

#### `FuelConsumption`
Fuel consumption parameters for a vessel.

**Attributes:**
- `consumption_at_sea_mt_per_day` - Sea consumption rate
- `consumption_in_port_mt_per_day` - Port consumption rate
- `speed_kts`, `eco_speed_kts` - Normal and economic speeds
- `tank_capacity_mt` - Fuel tank capacity
- `min_safe_level_mt` - Minimum safe fuel level

#### `BunkerPlan`
Optimized bunker plan result.

**Attributes:**
- `bunker_stops` - List of bunkering ports and quantities
- `total_cost_usd` - Total bunker cost
- `savings_vs_baseline_usd` - Savings compared to baseline
- `eco_speed_recommended` - Whether eco-speed is recommended

### Usage Example

```python
from modules.bunker_optimizer import BunkerOptimizer, BunkerPrice, FuelType, create_sample_fuel_consumption

# Create optimizer
prices = [
    BunkerPrice("SINGAPORE", "Singapore", FuelType.VLSFO, 650, 50000, datetime.now(), True),
    BunkerPrice("ROTTERDAM", "Rotterdam", FuelType.VLSFO, 620, 40000, datetime.now(), True),
]

fuel_params = {
    "VESSEL_001": create_sample_fuel_consumption("VESSEL_001")
}

optimizer = BunkerOptimizer(prices, fuel_params)

# Optimize bunker plan
plan = optimizer.optimize_bunker_plan(
    voyage_id="V001",
    vessel_id="VESSEL_001",
    route_ports=["SINGAPORE", "ROTTERDAM"],
    distances_nm=[8500],
    port_times_days=[1.0],
    fuel_type=FuelType.VLSFO,
    current_fuel_mt=500
)

print(f"Total cost: ${plan.total_cost_usd:,.2f}")
print(f"Savings: ${plan.savings_vs_baseline_usd:,.2f}")
```

---

## 2. Route Optimization Module

**File:** [`modules/route_optimizer.py`](../modules/route_optimizer.py)

### Features

- **Multi-objective optimization**: Distance, cost, time, profit
- **A* pathfinding algorithm**: Optimal path finding
- **Canal cost consideration**: Include canal fees in routing
- **Weather routing**: Adjust for weather conditions
- **Alternative routes**: Find multiple route options
- **Multi-port optimization**: Traveling Salesman Problem (TSP) solution

### Key Classes

#### `RouteOptimizer`
Main route optimization engine.

**Methods:**
- `find_optimal_route()` - Find optimal route between two ports
- `find_alternative_routes()` - Find multiple alternative routes
- `optimize_multi_port_route()` - Optimize route visiting multiple ports (TSP)

#### `RouteSegment`
A segment of a route between two ports.

**Attributes:**
- `from_port`, `to_port`
- `distance_nm` - Distance in nautical miles
- `transit_time_hours` - Transit time
- `cost_usd`, `canal_fee_usd` - Costs
- `weather_score` - Weather condition score (0-1)

#### `Route`
Complete route from origin to destination.

**Attributes:**
- `segments` - List of route segments
- `total_distance_nm`, `total_time_hours`, `total_cost_usd`
- `ports_sequence` - Ordered list of ports
- `optimization_objective` - Objective used

### Optimization Objectives

- `MINIMIZE_DISTANCE` - Shortest route
- `MINIMIZE_COST` - Cheapest route
- `MINIMIZE_TIME` - Fastest route
- `MAXIMIZE_PROFIT` - Most profitable route

### Usage Example

```python
from modules.route_optimizer import RouteOptimizer, RouteGraph, OptimizationObjective, create_sample_route_graph

# Create route graph
graph = create_sample_route_graph()

# Create optimizer
optimizer = RouteOptimizer(graph)

# Find optimal route
route = optimizer.find_optimal_route(
    origin="SINGAPORE",
    destination="ROTTERDAM",
    objective=OptimizationObjective.MINIMIZE_COST
)

print(f"Route: {' → '.join(route.ports_sequence)}")
print(f"Total distance: {route.total_distance_nm:,.0f} nm")
print(f"Total cost: ${route.total_cost_usd:,.2f}")

# Find alternative routes
alternatives = optimizer.find_alternative_routes(
    "SINGAPORE",
    "ROTTERDAM",
    num_alternatives=3
)
```

---

## 3. Capacity Optimization Module

**File:** [`modules/capacity_optimizer.py`](../modules/capacity_optimizer.py)

### Features

- **Multiple allocation strategies**: Profit, utilization, cost, throughput
- **Constraint satisfaction**: Capacity and time window constraints
- **Profit maximization**: Maximize total profit
- **Utilization balancing**: Balance vessel usage
- **Throughput maximization**: Maximize cargo moved

### Key Classes

#### `CapacityOptimizer`
Main capacity optimization engine.

**Methods:**
- `optimize()` - Run capacity optimization with selected strategy
- `export_to_dataframe()` - Export allocations to DataFrame
- `get_vessel_summary()` - Get summary by vessel

#### `VesselCapacity`
Vessel capacity parameters.

**Attributes:**
- `total_capacity_mt`, `available_capacity_mt`
- `utilization_pct` - Current utilization percentage
- `current_cargo` - List of allocated cargo IDs

#### `CargoParcel`
Individual cargo parcel to allocate.

**Attributes:**
- `quantity_mt` - Cargo quantity
- `load_port`, `discharge_port`
- `laycan_start`, `laycan_end` - Time window
- `revenue_per_mt`, `cost_per_mt` - Economics
- `priority` - Allocation priority (1-10)

### Allocation Strategies

- `GREEDY_PROFIT` - Maximize profit (allocate highest profit cargo first)
- `BALANCED_UTILIZATION` - Balance vessel usage
- `MINIMIZE_COST` - Minimize total cost
- `MAXIMIZE_THROUGHPUT` - Maximize total cargo moved

### Usage Example

```python
from modules.capacity_optimizer import CapacityOptimizer, AllocationStrategy, create_sample_capacity_data

# Create sample data
vessels, cargo_parcels = create_sample_capacity_data()

# Create optimizer
optimizer = CapacityOptimizer(
    vessels=vessels,
    cargo_parcels=cargo_parcels,
    strategy=AllocationStrategy.GREEDY_PROFIT
)

# Run optimization
result = optimizer.optimize()

print(f"Allocation rate: {result['metrics']['allocation_rate_pct']:.1f}%")
print(f"Total profit: ${result['metrics']['total_profit_usd']:,.2f}")
print(f"Avg vessel utilization: {result['metrics']['avg_vessel_utilization_pct']:.1f}%")

# Export results
df = optimizer.export_to_dataframe()
df.to_excel('capacity_allocation.xlsx', index=False)
```

---

## 4. Berth Utilization Module

**File:** [`modules/berth_utilization.py`](../modules/berth_utilization.py)

### Features

- **Utilization metrics**: Calculate berth utilization rates
- **Peak period identification**: Identify high-utilization periods
- **Occupancy timeline**: Detailed berth occupancy timeline
- **Multi-port analysis**: Analyze all ports simultaneously
- **Excel reporting**: Generate comprehensive Excel reports

### Key Classes

#### `BerthUtilizationAnalyzer`
Main berth utilization analyzer.

**Methods:**
- `calculate_port_utilization()` - Calculate metrics for specific port
- `calculate_all_ports_utilization()` - Calculate for all ports
- `identify_peak_periods()` - Identify peak utilization periods  
- `get_berth_occupancy_timeline()` - Get detailed occupancy timeline
- `generate_utilization_report()` - Generate comprehensive Excel report

### Usage Example

```python
from modules.berth_utilization import BerthUtilizationAnalyzer
import pandas as pd

# Load voyage data
voyage_data = pd.read_excel('voyage_schedule.xlsx')

# Create analyzer
analyzer = BerthUtilizationAnalyzer(voyage_data)

# Analyze specific port
port_metrics = analyzer.calculate_port_utilization(
    port="ROTTERDAM",
    berth_count=3
)

print(f"Total visits: {port_metrics['total_visits']}")
print(f"Utilization rate: {port_metrics['utilization_rate_percent']:.1f}%")

# Analyze all ports
all_ports_df = analyzer.calculate_all_ports_utilization()

# Generate comprehensive report
analyzer.generate_utilization_report('berth_utilization_report.xlsx')
```

---

## 5. Year Schedule Optimization Module

**File:** [`modules/year_schedule_optimizer.py`](../modules/year_schedule_optimizer.py)

### Features

- **Long-term planning**: Generate schedules for 1-2 years
- **Fleet optimization**: Optimize fleet utilization
- **Laycan adherence**: Respect cargo laycan windows
- **Seasonal adjustment**: Adjust for seasonal demand
- **Cargo prioritization**: Priority-based cargo scheduling

### Key Classes

#### `YearScheduleOptimizer`
Main year schedule optimizer.

**Methods:**
- `generate_schedule()` - Generate optimized year schedule
- `export_to_dataframe()` - Export schedule to DataFrame
- `export_to_excel()` - Export schedule to Excel

#### `VesselAvailability`
Vessel availability window.

**Attributes:**
- `vessel_id`
- `available_from`, `available_until` - Availability window
- `current_location` - Current port
- `dwt`, `speed_kts` - Vessel specs

#### `CargoCommitment`
Cargo commitment to be scheduled.

**Attributes:**
- `quantity_mt` - Cargo quantity
- `load_port`, `discharge_port`
- `laycan_start`, `laycan_end` - Laycan window
- `priority` - Scheduling priority

#### `YearScheduleParams`
Schedule generation parameters.

**Attributes:**
- `start_date` - Schedule start date
- `period_months` - Planning period (default: 12)
- `turnaround_multiplier` - Turnaround time multiplier
- `min_cargo_utilization` - Minimum cargo utilization (70%)

### Usage Example

```python
from modules.year_schedule_optimizer import (
    YearScheduleOptimizer,
    YearScheduleParams,
    create_sample_year_schedule_data
)
from datetime import datetime

# Create sample data
vessels, cargo_commitments, route_distances = create_sample_year_schedule_data()

# Create optimizer
params = YearScheduleParams(
    start_date=datetime(2026, 1, 1),
    period_months=12,
    turnaround_multiplier=1.1
)

optimizer = YearScheduleOptimizer(
    vessels=vessels,
    cargo_commitments=cargo_commitments,
    route_distances=route_distances,
    params=params
)

# Generate schedule
result = optimizer.generate_schedule()

print(f"Total voyages: {result['metrics']['total_voyages']}")
print(f"Cargo coverage: {result['metrics']['cargo_coverage_pct']:.1f}%")
print(f"Fleet utilization: {result['metrics']['avg_fleet_utilization_pct']:.1f}%")

# Export to Excel
optimizer.export_to_excel('year_schedule_2026.xlsx')
```

---

## 6. Voyage Calculator Module

**File:** [`modules/voyage_calculator.py`](../modules/voyage_calculator.py)

### Features

- **Voyage leg calculation**: Calculate individual voyage legs
- **Timing optimization**: Optimize departure/arrival times
- **Conflict detection**: Identify scheduling conflicts
- **Asset tracking**: Track asset positions and availability

### Key Classes

#### `VoyageCalculator`
Main calculation engine for voyage planning.

**Methods:**
- `calculate_voyage_from_df()` - Calculate voyage from DataFrame
- `get_asset_schedule()` - Get schedule for specific asset
- `find_conflicts()` - Find scheduling conflicts

#### `VoyageLeg`
Represents a single leg of a voyage.

**Attributes:**
- `leg_id`, `asset`
- `start_port`, `end_port`
- `start_time`, `end_time`, `duration_hours`
- `leg_type` - Type of operation (sailing, loading, etc.)

---

## Integration

### API Integration

All optimization modules are integrated into the API server:

```python
# In api_server.py
from modules.bunker_optimizer import BunkerOptimizer  
from modules.route_optimizer import RouteOptimizer
from modules.capacity_optimizer import CapacityOptimizer
from modules.berth_utilization import BerthUtilizationAnalyzer
from modules.year_schedule_optimizer import YearScheduleManager
```

### Frontend Integration

Optimization modules are accessible via UI modules in the web interface:

- **Bunker Optimization**: Tab "Бункер"
- **Capacity Planning**: Tab "Вместимость"
- **Berth Management**: Tab "Причалы"
- **Year Schedule**: Tab "Годовое расписание"

---

## Performance Considerations

### Algorithm Complexity

| Module | Algorithm | Complexity | Scalability |
|--------|-----------|------------|-------------|
| Bunker Optimizer | Greedy + Look-ahead | O(n*m) where n=ports, m=segments | Excellent (tested up to 100 ports) |
| Route Optimizer | A* Pathfinding | O(E + V log V) where E=edges, V=vertices | Good (suitable for maritime networks) |
| Capacity Optimizer | Greedy/Balancing | O(n*m) where n=cargo, m=vessels | Excellent (thousands of parcels) |
| Berth Utilization | Aggregation | O(n) where n=voyages | Excellent (millions of records) |
| Year Schedule | Greedy Allocation | O(n*m) where n=cargo, m=vessels | Good (up to 1000 cargo commitments) |
| Voyage Calculator | Sequential Calculation | O(n) where n=legs | Excellent |

### Optimization Tips

1. **Bunker Optimization**:
   - Use price caching to avoid repeated API calls
   - Limit look-ahead window for large route networks

2. **Route Optimization**:
   - Pre-compute common routes and cache results
   - Use heuristics for TSP with > 10 ports

3. **Capacity Optimization**:
   - Sort cargo by priority before optimization
   - Use BALANCED_UTILIZATION for better fleet usage

4. **Year Schedule**:
   - Limit planning horizon to 18 months for best performance
   - Use cargo prioritization to focus on critical commitments

---

## Testing

All optimization modules include sample data generators for testing:

```python
# Bunker Optimizer
from modules.bunker_optimizer import create_sample_bunker_prices, create_sample_fuel_consumption

# Route Optimizer  
from modules.route_optimizer import create_sample_route_graph

# Capacity Optimizer
from modules.capacity_optimizer import create_sample_capacity_data

# Year Schedule
from modules.year_schedule_optimizer import create_sample_year_schedule_data
```

---

## Future Enhancements

Planned improvements for optimization modules:

1. **Machine Learning Integration**:
   - Predictive bunker price forecasting
   - Historical route optimization learning
   - Demand forecasting for capacity planning

2. **Advanced Algorithms**:
   - Genetic algorithms for complex routing
   - Simulated annealing for capacity optimization
   - Linear programming for year schedule

3. **Real-time Optimization**:
   - Dynamic re-routing based on weather
   - Real-time bunker price updates
   - Live capacity adjustments

4. **Multi-objective Optimization**:
   - Pareto-optimal solutions
   - Trade-off analysis tools
   - Scenario comparison

---

## Support

For questions or issues with optimization modules:

1. Check module documentation in source files
2. Review test cases in `tests/` directory
3. Consult [`USER_GUIDE_EN.md`](USER_GUIDE_EN.md)
4. Contact development team

---

**Last Updated:** 2026-01-04
**Version:** 1.0.0
