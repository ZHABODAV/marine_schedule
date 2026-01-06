# API Calculation Reference
## Maritime Vessel Scheduling System

Quick reference guide for using calculation modules via Python API.

---

## Table of Contents

1. [Voyage Calculator API](#voyage-calculator-api)
2. [Deep Sea Calculator API](#deep-sea-calculator-api)
3. [Olya Calculator API](#olya-calculator-api)
4. [Bunker Optimizer API](#bunker-optimizer-api)
5. [Berth Utilization API](#berth-utilization-api)
6. [Common Patterns](#common-patterns)

---

## Voyage Calculator API

### Module: [`voyage_calculator.py`](../modules/voyage_calculator.py:40)

#### Basic Usage

```python
from modules.voyage_calculator import VoyageCalculator, VoyageLeg
from datetime import datetime

# Create calculator
calculator = VoyageCalculator()

# Add a voyage leg
leg = VoyageLeg(
    leg_id="LEG_001",
    asset="VESSEL_A",
    start_port="SINGAPORE",
    end_port="ROTTERDAM",
    start_time=datetime(2025, 1, 15, 8, 0),
    duration_hours=586.0,
    leg_type="sailing"
)

calculator.add_leg(leg)
```

#### Calculate from DataFrame

```python
import pandas as pd

# Prepare data
df = pd.DataFrame([
    {
        'asset': 'VESSEL_A',
        'start_port': 'SINGAPORE',
        'end_port': 'ROTTERDAM',
        'start_time': '2025-01-15 08:00',
        'duration_hours': 586.0,
        'leg_type': 'sailing'
    }
])

# Calculate
result_df = calculator.calculate_voyage_from_df(df)
```

#### Get Asset Schedule

```python
# Get schedule for specific vessel
schedule = calculator.get_asset_schedule('VESSEL_A')
print(schedule)
```

#### Find Conflicts

```python
# Find scheduling conflicts
conflicts = calculator.find_conflicts(tolerance_hours=2)

for conflict in conflicts:
    print(f"Conflict: {conflict['asset']}")
    print(f"  Between: {conflict['leg1']} and {conflict['leg2']}")
    print(f"  Gap: {conflict['gap_hours']} hours")
```

#### Complete Example

```python
from modules.voyage_calculator import calculate_voyage_schedule

# Calculate from Excel file
result = calculate_voyage_schedule(
    input_file='input/voyage_legs.xlsx',
    output_file='output/calculated_schedule.xlsx'
)
```

---

## Deep Sea Calculator API

### Module: [`deepsea_calculator.py`](../modules/deepsea_calculator.py:21)

#### Basic Usage

```python
from modules.deepsea_calculator import DeepSeaCalculator
from modules.deepsea_data import DeepSeaData

# Load data
data = DeepSeaData()
data.load_all_csv('input/deepsea/')

# Create calculator
calculator = DeepSeaCalculator(data)

# Calculate all voyages
calculator.calculate_all()
```

#### Access Calculated Results

```python
# Get all calculated voyages
for voyage_id, voyage in data.calculated_voyages.items():
    print(f"{voyage_id}: {voyage.vessel_name}")
    print(f"  Route: {voyage.load_port} → {voyage.disch_port}")
    print(f"  Duration: {voyage.total_days:.1f} days")
    print(f"  Distance: {voyage.total_distance_nm:,.0f} nm")
    print(f"  TCE: ${voyage.tce_usd:,.0f}/day")
```

#### Export Results

```python
# Export to CSV
calculator.export_schedule_csv('output/schedule.csv')
calculator.export_summary_csv('output/summary.csv')

# Get as DataFrame
schedule_df = calculator.get_schedule_dataframe()
summary_df = calculator.get_voyage_summary_dataframe()
```

#### Leg-by-Leg Details

```python
# Access individual legs
for voyage in data.calculated_voyages.values():
    for leg in voyage.legs:
        print(f"{leg.leg_type}: {leg.from_port} → {leg.to_port}")
        print(f"  Duration: {leg.duration_hours:.1f} hours")
        print(f"  Distance: {leg.distance_nm:.0f} nm")
        print(f"  Bunker cost: ${leg.bunker_cost_usd:,.0f}")
```

---

## Olya Calculator API

### Module: [`olya_calculator.py`](../modules/olya_calculator.py:20)

#### Basic Usage

```python
from modules.olya_calculator import OlyaVoyageCalculator
from modules.olya_data import OlyaData

# Load data
data = OlyaData()
data.load_vessels('input/olya/vessels_olya.csv')
data.load_routes('input/olya/routes_olya.csv')
data.load_cargo_plan('input/olya/cargo_olya.csv')

# Create calculator
calculator = OlyaVoyageCalculator(data)

# Calculate all voyages
calculator.calculate_all()
```

#### Access Operations

```python
# Get calculated operations
for operation in data.calculated_operations:
    print(f"{operation.vessel_name}: {operation.operation}")
    print(f"  Port: {operation.port}")
    print(f"  Cargo: {operation.cargo} ({operation.qty_mt} MT)")
    print(f"  Time: {operation.start_time} → {operation.end_time}")
    print(f"  Duration: {operation.duration_hours:.1f} hours")
```

#### Export Schedule

```python
# Export to CSV
calculator.export_schedule_csv('output/olya/schedule.csv')

# Get as DataFrame
schedule_df = calculator.get_schedule_dataframe()
```

#### Voyage Summary

```python
# Get voyage summaries
for voyage_id, voyage in data.calculated_voyages.items():
    print(f"{voyage_id}: {voyage.vessel_name}")
    print(f"  Type: {voyage.vessel_type}")
    print(f"  Duration: {voyage.total_duration_days:.1f} days")
    print(f"  Operations: {len(voyage.operations)}")
```

---

## Bunker Optimizer API

### Module: [`bunker_optimizer.py`](../modules/bunker_optimizer.py:129)

#### Setup Optimizer

```python
from modules.bunker_optimizer import (
    BunkerOptimizer, BunkerPrice, FuelConsumption, FuelType
)
from datetime import datetime

# Define bunker prices
prices = [
    BunkerPrice("SINGAPORE", "Singapore", FuelType.VLSFO, 650, 50000, datetime.now(), True),
    BunkerPrice("ROTTERDAM", "Rotterdam", FuelType.VLSFO, 620, 40000, datetime.now(), True),
    BunkerPrice("GIBRALTAR", "Gibraltar", FuelType.VLSFO, 630, 20000, datetime.now(), True),
]

# Define vessel fuel consumption
fuel_params = {
    'VESSEL_A': FuelConsumption(
        vessel_id='VESSEL_A',
        fuel_type=FuelType.VLSFO,
        consumption_at_sea_mt_per_day=35.0,
        consumption_in_port_mt_per_day=5.0,
        speed_kts=14.5,
        eco_speed_kts=12.0,
        eco_consumption_mt_per_day=25.0,
        tank_capacity_mt=2000,
        min_safe_level_mt=200
    )
}

# Create optimizer
optimizer = BunkerOptimizer(prices, fuel_params)
```

#### Optimize Bunker Plan

```python
# Optimize for a voyage
bunker_plan = optimizer.optimize_bunker_plan(
    voyage_id='VOY_001',
    vessel_id='VESSEL_A',
    route_ports=['SINGAPORE', 'SUEZ', 'GIBRALTAR', 'ROTTERDAM'],
    distances_nm=[3500, 2800, 1800],
    port_times_days=[2, 0.5, 0.5, 2],
    fuel_type=FuelType.VLSFO,
    current_fuel_mt=500,
    allow_eco_speed=True
)

# View results
print(f"Total Consumption: {bunker_plan.total_consumption_mt:.2f} MT")
print(f"Total Cost: ${bunker_plan.total_cost_usd:,.2f}")
print(f"Savings: ${bunker_plan.savings_vs_baseline_usd:,.2f}")
print(f"Eco Speed Recommended: {bunker_plan.eco_speed_recommended}")

# View bunker stops
for stop in bunker_plan.bunker_stops:
    print(f"  {stop['port_name']}: {stop['quantity_mt']:.2f} MT @ ${stop['price_per_mt']:.2f}")
```

#### Find Cheapest Port

```python
# Find cheapest bunker port
cheapest = optimizer.find_cheapest_bunker_port(
    fuel_type=FuelType.VLSFO,
    quantity_mt=400,
    ports=['SINGAPORE', 'ROTTERDAM', 'GIBRALTAR']
)

if cheapest:
    print(f"Cheapest: {cheapest.port_name} @ ${cheapest.price_per_mt:.2f}/MT")
```

#### Market Analysis

```python
# Analyze bunker market
market_analysis = optimizer.analyze_bunker_market(FuelType.VLSFO)

print(f"Average Price: ${market_analysis['average_price']:.2f}")
print(f"Price Range: ${market_analysis['min_price']:.2f} - ${market_analysis['max_price']:.2f}")
print(f"Cheapest Port: {market_analysis['cheapest_port']}")
print(f"Most Expensive: {market_analysis['most_expensive_port']}")
```

#### Hedging Calculation

```python
# Calculate hedging position
hedging = optimizer.calculate_hedging_position(
    total_consumption_mt=1000,
    fuel_type=FuelType.VLSFO,
    hedge_percentage=0.7
)

print(f"Hedge Volume: {hedging['hedge_volume_mt']:.2f} MT")
print(f"Hedge Value: ${hedging['hedge_value_usd']:,.2f}")
print(f"Value at Risk (95%): ${hedging['value_at_risk_95_usd']:,.2f}")
```

---

## Berth Utilization API

### Module: [`berth_utilization.py`](../modules/berth_utilization.py:13)

#### Setup Analyzer

```python
from modules.berth_utilization import BerthUtilizationAnalyzer
import pandas as pd
from datetime import datetime

# Prepare voyage data
voyage_data = pd.DataFrame([
    {
        'asset': 'VESSEL_A',
        'start_port': 'SINGAPORE',
        'end_port': 'ROTTERDAM',
        'start_time': datetime(2025, 1, 1, 8, 0),
        'end_time': datetime(2025, 1, 3, 14, 0),
        'duration_hours': 54.0
    },
    # ... more data
])

# Create analyzer
analyzer = BerthUtilizationAnalyzer(voyage_data)
```

#### Port Utilization

```python
# Calculate for specific port
utilization = analyzer.calculate_port_utilization(
    port='SINGAPORE',
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31)
)

print(f"Port: {utilization['port']}")
print(f"Total Visits: {utilization['total_visits']}")
print(f"Utilization Rate: {utilization['utilization_rate_percent']:.2f}%")
print(f"Average Occupation: {utilization['avg_occupation_time_hours']:.2f} hours")
```

#### All Ports Analysis

```python
# Analyze all ports
all_ports_df = analyzer.calculate_all_ports_utilization()

# Sort by utilization
top_ports = all_ports_df.nlargest(5, 'utilization_rate_percent')
print(top_ports)
```

#### Peak Period Analysis

```python
# Identify peak periods
peak_periods = analyzer.identify_peak_periods(
    port='SINGAPORE',
    window_days=7
)

# Find highest utilization period
if not peak_periods.empty:
    max_period = peak_periods.loc[peak_periods['concurrent_vessels'].idxmax()]
    print(f"Peak Date: {max_period['date']}")
    print(f"Concurrent Vessels: {max_period['concurrent_vessels']}")
```

#### Occupancy Timeline

```python
# Get detailed timeline
timeline = analyzer.get_berth_occupancy_timeline('SINGAPORE')

# Show current occupancy at different times
for idx, event in timeline.iterrows():
    print(f"{event['datetime']}: {event['event_type']} - "
          f"{event['asset']} (occupancy: {event['occupancy']})")
```

#### Generate Report

```python
# Generate comprehensive report
report = analyzer.generate_utilization_report('output/berth_utilization.xlsx')
```

---

## Common Patterns

### Pattern 1: Complete Voyage Calculation Pipeline

```python
from modules.voyage_calculator import VoyageCalculator
import pandas as pd

def calculate_complete_voyage(vessel_id, route_data):
    """Complete voyage calculation with error handling"""
    try:
        calculator = VoyageCalculator()
        
        # Calculate from data
        result = calculator.calculate_voyage_from_df(route_data)
        
        # Check for conflicts
        conflicts = calculator.find_conflicts(tolerance_hours=2)
        if conflicts:
            print(f"Warning: {len(conflicts)} conflicts found")
            for c in conflicts:
                print(f"  - {c['conflict_type']} between {c['leg1']} and {c['leg2']}")
        
        # Get summary
        summary = calculator.get_schedule_summary()
        
        return {
            'schedule': result,
            'summary': summary,
            'conflicts': conflicts
        }
    
    except Exception as e:
        print(f"Error calculating voyage: {e}")
        return None
```

### Pattern 2: Bundled Financial Analysis

```python
def analyze_voyage_financials(voyage):
    """Calculate all financial metrics for a voyage"""
    
    # Revenue
    freight_revenue = voyage.qty_mt * voyage.freight_rate_mt
    
    # Costs
    bunker_cost = voyage.total_bunker_cost_usd
    port_cost = voyage.total_port_cost_usd
    canal_cost = voyage.total_canal_cost_usd
    hire_cost = voyage.hire_cost_usd
    
    total_cost = bunker_cost + port_cost + canal_cost + hire_cost
    
    # Profit
    voyage_result = freight_revenue - total_cost
    
    # TCE
    tce = (freight_revenue - (bunker_cost + port_cost + canal_cost)) / voyage.total_days
    
    # Break-even
    breakeven_rate = total_cost / voyage.qty_mt
    
    return {
        'freight_revenue': freight_revenue,
        'total_cost': total_cost,
        'bunker_cost': bunker_cost,
        'port_cost': port_cost,
        'canal_cost': canal_cost,
        'hire_cost': hire_cost,
        'voyage_result': voyage_result,
        'tce': tce,
        'breakeven_rate': breakeven_rate,
        'profit_margin': (voyage_result / freight_revenue * 100) if freight_revenue > 0 else 0
    }
```

### Pattern 3: Batch Processing

```python
def process_multiple_voyages(voyage_plans):
    """Process multiple voyages and aggregate results"""
    
    from modules.deepsea_calculator import DeepSeaCalculator
    from modules.deepsea_data import DeepSeaData
    
    # Load data
    data = DeepSeaData()
    data.load_all_csv('input/deepsea/')
    
    # Process
    calculator = DeepSeaCalculator(data)
    calculator.calculate_all()
    
    # Aggregate results
    total_revenue = sum(v.freight_revenue_usd for v in data.calculated_voyages.values())
    total_cost = sum(v.total_cost_usd for v in data.calculated_voyages.values())
    total_profit = total_revenue - total_cost
    
    avg_tce = sum(v.tce_usd for v in data.calculated_voyages.values()) / len(data.calculated_voyages)
    
    return {
        'voyage_count': len(data.calculated_voyages),
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'average_tce': avg_tce,
        'voyages': data.calculated_voyages
    }
```

### Pattern 4: Data Validation

```python
def validate_voyage_data(voyage_df):
    """Validate voyage data before processing"""
    
    errors = []
    
    # Required columns
    required = ['asset', 'start_port', 'end_port', 'start_time', 'duration_hours']
    missing = [col for col in required if col not in voyage_df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")
    
    # Data types
    try:
        voyage_df['start_time'] = pd.to_datetime(voyage_df['start_time'])
        voyage_df['duration_hours'] = pd.to_numeric(voyage_df['duration_hours'])
    except Exception as e:
        errors.append(f"Data type conversion error: {e}")
    
    # Logical checks
    if 'duration_hours' in voyage_df.columns:
        negative = voyage_df[voyage_df['duration_hours'] < 0]
        if not negative.empty:
            errors.append(f"Found {len(negative)} rows with negative duration")
    
    if errors:
        raise ValueError(f"Validation errors: {'; '.join(errors)}")
    
    return True
```

### Pattern 5: Export Multiple Formats

```python
def export_results_multi_format(calculator, base_path):
    """Export calculation results in multiple formats"""
    
    # CSV
    calculator.export_schedule_csv(f'{base_path}_schedule.csv')
    calculator.export_summary_csv(f'{base_path}_summary.csv')
    
    # Excel (multiple sheets)
    with pd.ExcelWriter(f'{base_path}.xlsx', engine='openpyxl') as writer:
        schedule_df = calculator.get_schedule_dataframe()
        summary_df = calculator.get_voyage_summary_dataframe()
        
        schedule_df.to_excel(writer, sheet_name='Schedule', index=False)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    # JSON (for API integration)
    import json
    schedule_df = calculator.get_schedule_dataframe()
    schedule_df['start_time'] = schedule_df['start_time'].astype(str)
    schedule_df['end_time'] = schedule_df['end_time'].astype(str)
    
    with open(f'{base_path}_schedule.json', 'w') as f:
        json.dump(schedule_df.to_dict('records'), f, indent=2)
    
    print(f"Exported to: {base_path}.*")
```

---

## Error Handling Best Practices

### Safe Data Loading

```python
from modules.deepsea_data import DeepSeaData

def safe_load_data(data_path):
    """Safely load data with error handling"""
    try:
        data = DeepSeaData()
        data.load_all_csv(data_path)
        
        # Validate
        if not data.vessels:
            raise ValueError("No vessels loaded")
        if not data.voyage_plans:
            raise ValueError("No voyage plans loaded")
        
        return data
    
    except FileNotFoundError as e:
        print(f"Data file not found: {e}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
```

### Graceful Calculation Failures

```python
def calculate_with_fallback(calculator, voyage_plan):
    """Calculate voyage with fallback on error"""
    try:
        result = calculator._calculate_voyage(voyage_plan)
        return result
    
    except Exception as e:
        print(f"Error calculating {voyage_plan.voyage_id}: {e}")
        
        # Return minimal result
        return {
            'voyage_id': voyage_plan.voyage_id,
            'status': 'error',
            'error_message': str(e),
            'timestamp': datetime.now()
        }
```

---

## Related Documentation

- [Comprehensive Calculation Guide](COMPREHENSIVE_CALCULATION_GUIDE.md) - Detailed formulas and examples
- [API Reference](API_REFERENCE.md) - Complete REST API documentation
- [Quick Start Guide](QUICK_START.md) - Getting started guide

---

**Last Updated:** December 19, 2025  
**Version:** 1.0
