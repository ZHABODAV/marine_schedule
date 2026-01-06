# Comprehensive Calculation Guide

## Maritime Vessel Scheduling System

This guide explains how to calculate various aspects of maritime vessel operations, including voyage planning, fuel optimization, berth utilization, and financial metrics.

---

## Table of Contents

1. [Voyage Time Calculations](#1-voyage-time-calculations)
2. [Distance Calculations](#2-distance-calculations)
3. [Speed Calculations](#3-speed-calculations)
4. [Fuel Consumption Calculations](#4-fuel-consumption-calculations)
5. [Bunker Optimization Calculations](#5-bunker-optimization-calculations)
6. [Port Operations Calculations](#6-port-operations-calculations)
7. [Canal Transit Calculations](#7-canal-transit-calculations)
8. [Berth Utilization Calculations](#8-berth-utilization-calculations)
9. [Financial Calculations](#9-financial-calculations)
10. [Schedule Optimization](#10-schedule-optimization)

---

## 1. Voyage Time Calculations

### 1.1 Basic Voyage Duration

**Formula:**

```
Duration (hours) = Distance (nautical miles) / Speed (knots)
```

**Example:**

```python
distance_nm = 1000
speed_kn = 14.5
duration_hours = distance_nm / speed_kn
# Result: 68.97 hours (~2.87 days)
```

### 1.2 Total Voyage Time Including Weather Margin

**Formula:**

```
Total Duration = Base Duration × (1 + Weather Margin %)
```

**Default Parameters:**

- Weather Margin: 10-15% (typically 10%)

**Example:**

```python
base_duration_hours = 68.97
weather_margin_pct = 10
total_duration = base_duration_hours * (1 + weather_margin_pct / 100)
# Result: 75.87 hours
```

### 1.3 Leg-by-Leg Time Calculation

For each voyage leg, calculate:

#### Loading Operation

```
Loading Time = (Cargo Quantity MT / Load Rate MT/day) × 24 + Port Overhead Hours
```

**Example:**

```python
cargo_qty_mt = 50000
load_rate_mt_day = 10000
port_overhead_hours = 6
loading_time_hours = (cargo_qty_mt / load_rate_mt_day) * 24 + port_overhead_hours
# Result: 126 hours (5.25 days)
```

#### Discharge Operation

```
Discharge Time = (Cargo Quantity MT / Discharge Rate MT/day) × 24 + Port Overhead Hours
```

#### Sea Leg

```
Sea Time = (Distance nm / Speed kn) × Weather Margin
```

#### Canal Transit

```
Canal Time = Transit Hours + Waiting Hours
```

#### Bunker Operation

```
Bunker Time = Fixed Duration (typically 12-24 hours)
```

---

## 2. Distance Calculations

### 2.1 Point-to-Point Distance

Distances are typically stored in a distance matrix or database. If calculating:

**Great Circle Distance Formula (simplified):**

```
Distance = ACOS(
    SIN(lat1) × SIN(lat2) + 
    COS(lat1) × COS(lat2) × COS(lon2 - lon1)
) × 60 × 180 / π
```

Where:

- lat1, lat2 = latitudes in radians
- lon1, lon2 = longitudes in radians
- Result in nautical miles

### 2.2 Route Distance with Waypoints

**Formula:**

```
Total Distance = Σ(Distance between consecutive waypoints)
```

**Example:**

```python
route_segments = [
    ("PORT_A", "WAYPOINT_1", 500),
    ("WAYPOINT_1", "WAYPOINT_2", 300),
    ("WAYPOINT_2", "PORT_B", 400)
]
total_distance = sum(segment[2] for segment in route_segments)
# Result: 1200 nm
```

### 2.3 ECA Zone Distance

Calculate separately for Emission Control Areas:

```python
total_distance_nm = 1000
eca_miles = 150  # Distance within ECA zones
open_sea_miles = total_distance_nm - eca_miles
# Result: 850 nm in open sea, 150 nm in ECA
```

---

## 3. Speed Calculations

### 3.1 Different Speed Conditions

#### Laden Speed

Speed when vessel is loaded with cargo:

```
Typical: 12-15 knots
```

#### Ballast Speed

Speed when vessel is empty:

```
Typical: 13-16 knots (slightly faster than laden)
```

#### Eco Speed

Fuel-efficient speed:

```
Eco Speed = Normal Speed × 0.8-0.85
Typical: 10-13 knots
```

### 3.2 Average Speed Calculation

**Formula:**

```
Average Speed = Total Distance / Total Sea Time
```

**Example:**

```python
total_distance_nm = 5000
total_sea_hours = 350
average_speed_kn = total_distance_nm / total_sea_hours
# Result: 14.29 knots
```

### 3.3 Speed Optimization

To find optimal speed for fuel efficiency:

**Cubic Law Approximation:**

```
Fuel Consumption ∝ Speed³
```

**Example:**

```python
base_speed = 15.0
base_consumption = 35.0  # MT/day

new_speed = 12.0
estimated_consumption = base_consumption * (new_speed / base_speed) ** 3
# Result: ~18.2 MT/day (48% reduction)
```

---

## 4. Fuel Consumption Calculations

### 4.1 Sea Consumption

**Formula:**

```
Sea Consumption (MT) = Consumption Rate (MT/day) × Sea Time (days)
```

**Example:**

```python
consumption_rate_laden = 35.0  # MT/day
sea_time_days = 10.5
fuel_consumed = consumption_rate_laden * sea_time_days
# Result: 367.5 MT
```

### 4.2 Port Consumption

**Formula:**

```
Port Consumption (MT) = Port Consumption Rate (MT/day) × Port Time (days)
```

**Example:**

```python
port_consumption_rate = 5.0  # MT/day
port_time_days = 3.0
port_fuel = port_consumption_rate * port_time_days
# Result: 15 MT
```

### 4.3 Total Voyage Consumption

**Formula:**

```
Total Fuel = Σ(Sea Legs Consumption) + Σ(Port Consumption) + Σ(Canal Consumption)
```

**Example:**

```python
sea_consumption = 367.5
port_consumption = 15.0
canal_consumption = 8.0
total_fuel_mt = sea_consumption + port_consumption + canal_consumption
# Result: 390.5 MT
```

### 4.4 ECA Zone Fuel Calculation

When in ECA zones, MGO (Marine Gas Oil) must be used instead of IFO:

**Formula:**

```
ECA Hours = ECA Distance (nm) / Speed (kn)
ECA Days = ECA Hours / 24
MGO Consumed = Consumption Rate × ECA Days × 0.8
IFO Consumed = Total Consumption - MGO Consumed
```

**Example:**

```python
eca_miles = 150
speed_kn = 14.5
consumption_rate = 35.0

eca_hours = eca_miles / speed_kn  # 10.34 hours
eca_days = eca_hours / 24  # 0.43 days
mgo_consumed = consumption_rate * eca_days * 0.8  # 12.04 MT
```

### 4.5 Fuel Savings Calculation

**Formula:**

```
Fuel Savings = Normal Consumption - Eco Consumption
Percentage Savings = (Fuel Savings / Normal Consumption) × 100
```

**Example:**

```python
normal_consumption = 367.5  # MT at 15 knots
eco_consumption = 262.5  # MT at 12 knots
fuel_savings = normal_consumption - eco_consumption
savings_percent = (fuel_savings / normal_consumption) * 100
# Result: 105 MT saved (28.6%)
```

---

## 5. Bunker Optimization Calculations

### 5.1 Bunker Cost Calculation

**Formula:**

```
Bunker Cost = Quantity (MT) × Price (USD/MT)
```

**Example:**

```python
ifo_consumed = 350  # MT
ifo_price = 650  # USD/MT
mgo_consumed = 40  # MT
mgo_price = 850  # USD/MT

ifo_cost = ifo_consumed * ifo_price  # $227,500
mgo_cost = mgo_consumed * mgo_price  # $34,000
total_bunker_cost = ifo_cost + mgo_cost
# Result: $261,500
```

### 5.2 Optimal Bunker Port Selection

**Criteria:**

1. Price per MT (lowest)
2. Availability (sufficient quantity)
3. Route deviation (minimal)

**Example:**

```python
ports_on_route = [
    {"port": "SINGAPORE", "price": 650, "available": 5000},
    {"port": "ROTTERDAM", "price": 620, "available": 4000},
    {"port": "GIBRALTAR", "price": 630, "available": 3000}
]

required_fuel = 400  # MT
cheapest_port = min(
    [p for p in ports_on_route if p["available"] >= required_fuel],
    key=lambda x: x["price"]
)
# Result: ROTTERDAM at $620/MT
```

### 5.3 Fuel Tank Capacity Planning

**Formula:**

```
Required Capacity = Total Voyage Consumption + Safety Margin
Safety Margin = 10-20% of Total Consumption
```

**Example:**

```python
voyage_consumption = 390.5  # MT
safety_margin_pct = 15
required_capacity = voyage_consumption * (1 + safety_margin_pct / 100)
# Result: 449.1 MT
```

### 5.4 Hedging Calculation

**Value at Risk (VaR) - 95% Confidence:**

```
VaR = 1.65 × Price Volatility (σ) × Hedge Volume
```

**Example:**

```python
import numpy as np

prices = [620, 650, 640, 630, 660, 645]
avg_price = np.mean(prices)  # 640.83
price_std = np.std(prices)  # 14.25
hedge_volume_mt = 300
hedge_percentage = 0.7

hedge_value = hedge_volume_mt * hedge_percentage * avg_price  # $134,574
var_95 = 1.65 * price_std * (hedge_volume_mt * hedge_percentage)
# Result: VaR = $2,993
```

---

## 6. Port Operations Calculations

### 6.1 Loading Rate Calculation

**Formula:**

```
Actual Load Rate = Berth Load Rate × Vessel Capability × Weather Factor
```

**Example:**

```python
berth_rate = 12000  # MT/day
vessel_capability = 1.0  # 100% of berth rate
weather_factor = 0.95  # 5% reduction due to weather

actual_rate = berth_rate * vessel_capability * weather_factor
# Result: 11,400 MT/day
```

### 6.2 Port Turnaround Time

**Formula:**

```
Turnaround Time = Berthing Time + Operations Time + Departure Time
```

**Typical Values:**

- Berthing: 2-4 hours
- Operations: Based on cargo quantity
- Departure: 1-2 hours

**Example:**

```python
berthing_hours = 3
cargo_qty = 50000
load_rate = 11400
operation_hours = (cargo_qty / load_rate) * 24  # 105.26 hours
departure_hours = 2

total_turnaround = berthing_hours + operation_hours + departure_hours
# Result: 110.26 hours (4.6 days)
```

### 6.3 Port Costs

**Formula:**

```
Total Port Cost = Base Port Charges + Berth Charges + Pilotage + Tugs + Agency Fees
```

**Example:**

```python
base_charges = 5000  # USD
berth_charges = 3000  # USD
pilotage = 2000  # USD
tugs = 1500  # USD
agency_fees = 800  # USD

total_port_cost = base_charges + berth_charges + pilotage + tugs + agency_fees
# Result: $12,300
```

---

## 7. Canal Transit Calculations

### 7.1 Canal Time Calculation

**Formula:**

```
Total Canal Time = Transit Time + Waiting Time + Buffer
```

**Example (Suez Canal):**

```python
transit_hours = 12  # Actual transit
avg_waiting_hours = 24  # Average queue time
buffer_hours = 6  # Safety buffer

total_canal_time = transit_hours + avg_waiting_hours + buffer_hours
# Result: 42 hours (1.75 days)
```

### 7.2 Canal Fee Calculation

**Formula:**

```
Canal Fee = Base Fee + (Fee per Ton × Vessel DWT)
```

**Example (Suez Canal):**

```python
base_fee_usd = 50000
fee_per_ton = 8.5
vessel_dwt = 75000

total_canal_fee = base_fee_usd + (fee_per_ton * vessel_dwt)
# Result: $687,500
```

### 7.3 Canal Restrictions Check

**Criteria:**

- Maximum LOA (Length Overall)
- Maximum Beam
- Maximum Draft
- Maximum DWT

**Example:**

```python
def can_transit_canal(vessel, canal):
    """Check if vessel can transit canal"""
    checks = [
        vessel.loa_m <= canal.max_loa_m,
        vessel.beam_m <= canal.max_beam_m,
        vessel.draft_m <= canal.max_draft_m,
        vessel.dwt_mt <= canal.max_dwt_mt
    ]
    return all(checks)

# Example vessel vs Suez Canal
vessel = {"loa_m": 225, "beam_m": 32, "draft_m": 12.5, "dwt_mt": 75000}
suez = {"max_loa_m": 400, "max_beam_m": 77.5, "max_draft_m": 20.1, "max_dwt_mt": 240000}
can_transit = can_transit_canal(vessel, suez)
# Result: True
```

---

## 8. Berth Utilization Calculations

### 8.1 Berth Utilization Rate

**Formula:**

```
Utilization Rate (%) = (Total Occupied Hours / Total Available Hours) × 100
```

**Example:**

```python
total_occupied_hours = 450
period_days = 30
hours_per_day = 24
total_available_hours = period_days * hours_per_day

utilization_rate = (total_occupied_hours / total_available_hours) * 100
# Result: 62.5%
```

### 8.2 Average Vessel Occupation Time

**Formula:**

```
Average Occupation = Total Occupation Hours / Number of Visits
```

**Example:**

```python
total_occupation_hours = 450
number_of_visits = 15

avg_occupation = total_occupation_hours / number_of_visits
# Result: 30 hours per visit
```

### 8.3 Peak Utilization Analysis

**Rolling Window Average:**

```
Rolling Average = Σ(Daily Utilization in Window) / Window Size
```

**Example:**

```python
daily_visits = [2, 3, 1, 4, 3, 2, 1]  # vessels per day
window_size = 7

rolling_avg = sum(daily_visits) / window_size
# Result: 2.29 vessels per day
```

### 8.4 Concurrent Vessel Capacity

**Formula:**

```
Concurrent Capacity = Number of Berths × Berth Efficiency
```

**Example:**

```python
number_of_berths = 4
berth_efficiency = 0.85  # 85% efficiency

effective_capacity = number_of_berths * berth_efficiency
# Result: 3.4 concurrent vessels
```

---

## 9. Financial Calculations

### 9.1 Freight Revenue

**Formula:**

```
Freight Revenue = Cargo Quantity (MT) × Freight Rate (USD/MT)
```

**Example:**

```python
cargo_qty_mt = 50000
freight_rate_mt = 45.00

freight_revenue = cargo_qty_mt * freight_rate_mt
# Result: $2,250,000
```

### 9.2 Time Charter Equivalent (TCE)

**Formula:**

```
TCE = (Freight Revenue - Voyage Costs) / Voyage Days
```

**Example:**

```python
freight_revenue = 2250000
bunker_cost = 261500
port_costs = 45000
canal_costs = 687500
total_voyage_costs = bunker_cost + port_costs + canal_costs  # $994,000

voyage_days = 35

tce = (freight_revenue - total_voyage_costs) / voyage_days
# Result: $35,886 per day
```

### 9.3 Daily Hire Cost

**Formula:**

```
Total Hire Cost = Daily Hire Rate × Voyage Duration (days)
```

**Example:**

```python
daily_hire_usd = 28000
voyage_days = 35

total_hire_cost = daily_hire_usd * voyage_days
# Result: $980,000
```

### 9.4 Voyage Profit/Loss

**Formula:**

```
Voyage Result = Freight Revenue - Total Costs
Total Costs = Hire Cost + Bunker Cost + Port Costs + Canal Costs + Other Costs
```

**Example:**

```python
freight_revenue = 2250000
hire_cost = 980000
bunker_cost = 261500
port_costs = 45000
canal_costs = 687500
other_costs = 20000

total_costs = hire_cost + bunker_cost + port_costs + canal_costs + other_costs
voyage_result = freight_revenue - total_costs
# Result: $256,000 profit
```

### 9.5 Break-Even Freight Rate

**Formula:**

```
Break-Even Rate = Total Costs / Cargo Quantity
```

**Example:**

```python
total_costs = 1994000
cargo_qty_mt = 50000

breakeven_rate = total_costs / cargo_qty_mt
# Result: $39.88 per MT
```

### 9.6 Net Present Value (NPV)

**Formula:**

```
NPV = Σ [Cash Flow_t / (1 + r)^t]
```

Where:

- r = discount rate
- t = time period

**Example:**

```python
cash_flows = [256000, 312000, 289000]  # 3 voyages
discount_rate = 0.08  # 8%

npv = sum(cf / (1 + discount_rate)**i for i, cf in enumerate(cash_flows, 1))
# Result: $789,743
```

---

## 10. Schedule Optimization

### 10.1 Earliest Arrival Time

**Formula:**

```
ETA = Departure Time + Sea Time + Canal Time + Buffer
```

**Example:**

```python
from datetime import datetime, timedelta

departure_time = datetime(2025, 1, 15, 8, 0)
sea_hours = 120
canal_hours = 42
buffer_hours = 12

eta = departure_time + timedelta(hours=sea_hours + canal_hours + buffer_hours)
# Result: 2025-01-22 14:00
```

### 10.2 Laycan Window Optimization

**Laycan** = Earliest (lay) and Latest Canceling (can) dates

**Formula:**

```
Optimal Departure = Laycan Start - Voyage Duration + Buffer
```

**Example:**

```python
laycan_start = datetime(2025, 2, 1)
laycan_end = datetime(2025, 2, 5)
voyage_duration_days = 7
buffer_days = 1

optimal_departure = laycan_start - timedelta(days=voyage_duration_days - buffer_days)
# Result: 2025-01-26 (arrives 2025-02-02)
```

### 10.3 Fleet Utilization

**Formula:**

```
Fleet Utilization (%) = (Total Active Days / Total Available Days) × 100
```

**Example:**

```python
fleet_size = 10
days_in_period = 30
total_available_days = fleet_size * days_in_period  # 300 days

active_days_per_vessel = [28, 30, 25, 29, 30, 27, 30, 26, 28, 29]
total_active_days = sum(active_days_per_vessel)  # 282 days

fleet_utilization = (total_active_days / total_available_days) * 100
# Result: 94%
```

### 10.4 Conflict Detection

Check for overlapping schedules:

**Formula:**

```
Conflict exists if: 
  (Start1 <= End2) AND (End1 >= Start2)
```

**Example:**

```python
def check_conflict(leg1, leg2):
    """Check if two legs conflict"""
    return (leg1['start_time'] <= leg2['end_time'] and 
            leg1['end_time'] >= leg2['start_time'])

leg_a = {'start_time': datetime(2025, 1, 15), 'end_time': datetime(2025, 1, 20)}
leg_b = {'start_time': datetime(2025, 1, 18), 'end_time': datetime(2025, 1, 25)}

has_conflict = check_conflict(leg_a, leg_b)
# Result: True (overlap from Jan 18-20)
```

---

## Quick Reference Formulas

### Time Calculations

| Calculation | Formula |
|------------|---------|
| Sea Time | Distance (nm) / Speed (kn) |
| Loading Time | (Quantity MT / Rate MT/day) × 24 + Overhead |
| Total Voyage | Σ(All Leg Times) |

### Fuel Calculations

| Calculation | Formula |
|------------|---------|
| Sea Consumption | Rate (MT/day) × Days |
| Total Fuel | Sea + Port + Canal Fuel |
| Fuel Savings | Normal - Eco Consumption |

### Financial Calculations

| Calculation | Formula |
|------------|---------|
| Freight Revenue | Quantity × Rate |
| TCE | (Revenue - Costs) / Days |
| Voyage Profit | Revenue - All Costs |

### Utilization Calculations

| Calculation | Formula |
|------------|---------|
| Berth Utilization | (Occupied / Available) × 100 |
| Fleet Utilization | (Active / Available) × 100 |
| Average Occupation | Total Hours / Visits |

---

## Typical Parameter Values

### Speed Parameters

- **Laden Speed:** 12-15 knots
- **Ballast Speed:** 13-16 knots
- **Eco Speed:** 10-13 knots

### Loading/Discharge Rates

- **Grain/Coal:** 8,000-15,000 MT/day
- **Containerized:** 20-30 moves/hour
- **Liquid Cargo:** 10,000-20,000 MT/day

### Port Times

- **Berthing:** 2-4 hours
- **Departure:** 1-2 hours
- **Port Overhead:** 6-12 hours

### Fuel Consumption

- **Handysize (30,000 DWT):** 15-25 MT/day
- **Panamax (70,000 DWT):** 25-35 MT/day
- **Capesize (180,000 DWT):** 40-60 MT/day
- **Port Consumption:** 10-20% of sea consumption

### Safety Margins

- **Weather Margin:** 10-15%
- **Fuel Buffer:** 15-20%
- **Schedule Buffer:** 1-2 days

---

## Implementation Examples

### Example 1: Complete Voyage Calculation

```python
from datetime import datetime, timedelta

# Input parameters
cargo_qty_mt = 50000
load_port = "SINGAPORE"
discharge_port = "ROTTERDAM"
distance_nm = 8500
vessel_speed_kn = 14.5
load_rate = 10000
discharge_rate = 8000
consumption_rate = 35.0
ifo_price = 650
mgo_price = 850

# Calculations
loading_time_hours = (cargo_qty_mt / load_rate) * 24 + 6
sea_time_hours = (distance_nm / vessel_speed_kn) * 1.1  # 10% weather margin
discharge_time_hours = (cargo_qty_mt / discharge_rate) * 24 + 6

total_hours = loading_time_hours + sea_time_hours + discharge_time_hours
total_days = total_hours / 24

# Fuel
sea_fuel_mt = consumption_rate * (sea_time_hours / 24)
port_fuel_mt = 5.0 * ((loading_time_hours + discharge_time_hours) / 24)
total_fuel_mt = sea_fuel_mt + port_fuel_mt

bunker_cost = total_fuel_mt * ifo_price

# Print results
print(f"Total Voyage Duration: {total_days:.2f} days")
print(f"Total Fuel Consumption: {total_fuel_mt:.2f} MT")
print(f"Total Bunker Cost: ${bunker_cost:,.2f}")
```

### Example 2: Berth Utilization Analysis

```python
import pandas as pd

# Sample data
visits = [
    {'start': datetime(2025, 1, 1, 8, 0), 'end': datetime(2025, 1, 3, 14, 0)},
    {'start': datetime(2025, 1, 5, 10, 0), 'end': datetime(2025, 1, 7, 16, 0)},
    {'start': datetime(2025, 1, 9, 9, 0), 'end': datetime(2025, 1, 11, 12, 0)},
]

# Calculate
total_occupied_hours = sum(
    (visit['end'] - visit['start']).total_seconds() / 3600 
    for visit in visits
)

analysis_start = datetime(2025, 1, 1)
analysis_end = datetime(2025, 1, 31)
total_hours = (analysis_end - analysis_start).total_seconds() / 3600

utilization_rate = (total_occupied_hours / total_hours) * 100

print(f"Total Visits: {len(visits)}")
print(f"Total Occupied: {total_occupied_hours:.2f} hours")
print(f"Utilization Rate: {utilization_rate:.2f}%")
```

---

## Related Documentation

- [`voyage_calculator.py`](../modules/voyage_calculator.py) - Basic voyage calculations
- [`deepsea_calculator.py`](../modules/deepsea_calculator.py) - Deep sea voyage calculations
- [`olya_calculator.py`](../modules/olya_calculator.py) - River/coastal calculations
- [`bunker_optimizer.py`](../modules/bunker_optimizer.py) - Bunker optimization algorithms
- [`berth_utilization.py`](../modules/berth_utilization.py) - Berth analysis tools

---

## Notes and Best Practices

1. **Always include safety margins** - 10-15% for weather, 15-20% for fuel
2. **Validate input data** - Check for realistic values before calculations
3. **Consider ECA zones** - Use correct fuel types and consumption rates
4. **Account for seasonality** - Different weather margins for different seasons
5. **Update prices regularly** - Bunker prices fluctuate daily
6. **Check canal restrictions** - Verify vessel can physically transit
7. **Monitor utilization** - Track berth and fleet utilization for optimization
8. **Document assumptions** - Record all assumptions made in calculations

---

**Last Updated:** December 19, 2025  
**Version:** 1.0
