# Year Schedule API Documentation

## Overview

The Year Schedule API provides comprehensive endpoints for generating, optimizing, and managing annual vessel schedules with multiple optimization strategies.

## Features

- **Multi-Strategy Optimization**: Max Revenue, Min Cost, and Balanced approaches
- **Conflict Detection**: Automatic detection of vessel scheduling conflicts
- **Scenario Management**: Save, load, and compare schedule scenarios
- **KPI Analytics**: Comprehensive financial and operational metrics
- **Strategy Comparison**: Side-by-side comparison of optimization approaches

## Endpoints

### 1. GET /api/schedule/year

Retrieve saved year schedules.

**Query Parameters:**
- `list=true` - List all saved schedules
- `schedule_id=<id>` - Get specific schedule by ID

**Example Request:**
```bash
# List all schedules
curl http://localhost:5000/api/schedule/year?list=true

# Get specific schedule
curl http://localhost:5000/api/schedule/year?schedule_id=test_maxrev_1234567890
```

**Example Response:**
```json
{
  "success": true,
  "schedules": [
    {
      "schedule_id": "test_maxrev_1234567890",
      "created_at": "2026-01-15T10:30:00",
      "strategy": "maxrevenue",
      "optimality_score": 85.3
    }
  ],
  "count": 1
}
```

---

### 2. POST /api/schedule/year

Generate optimized year schedule with specified strategy.

**Request Body:**
```json
{
  "module": "deepsea",
  "strategy": "balance",
  "config": {
    "start_date": "2026-01-01",
    "end_date": "2026-12-31",
    "min_utilization_pct": 70.0,
    "max_utilization_pct": 95.0,
    "bunker_optimization": true
  },
  "save_as": "annual_schedule_2026"
}
```

**Parameters:**
- `module` (string): Module to use - `deepsea` or `olya`
- `strategy` (string): Optimization strategy
  - `maxrevenue` - Maximize total freight revenue
  - `mincost` - Minimize operational costs
  - `balance` - Balanced profit and utilization
- `config` (object): Configuration options
  - `start_date` - Schedule start date (YYYY-MM-DD)
  - `end_date` - Schedule end date (YYYY-MM-DD)
  - `min_utilization_pct` - Minimum fleet utilization target
  - `max_utilization_pct` - Maximum fleet utilization target
  - `bunker_optimization` - Enable bunker optimization
- `save_as` (string, optional): Save schedule with this ID

**Example Response:**
```json
{
  "success": true,
  "strategy": "balance",
  "kpis": {
    "total_revenue_usd": 15000000.0,
    "total_cost_usd": 9500000.0,
    "total_profit_usd": 5500000.0,
    "total_voyages": 48,
    "total_cargo_mt": 480000,
    "fleet_utilization_pct": 82.5,
    "avg_tce_usd": 18500.0,
    "optimality_score": 87.3
  },
  "conflicts": {
    "count": 2,
    "details": [
      {
        "type": "vessel_overlap",
        "severity": "warning",
        "vessel_id": "V001",
        "description": "Tight turnaround: 18 hours gap"
      }
    ]
  },
  "saved": true,
  "schedule_id": "annual_schedule_2026"
}
```

---

### 3. DELETE /api/schedule/year/<schedule_id>

Delete a saved schedule.

**Example Request:**
```bash
curl -X DELETE http://localhost:5000/api/schedule/year/annual_schedule_2026
```

**Example Response:**
```json
{
  "success": true,
  "message": "Schedule annual_schedule_2026 deleted"
}
```

---

### 4. POST /api/schedule/year/conflicts

Detect scheduling conflicts in current or saved schedule.

**Request Body:**
```json
{
  "module": "deepsea",
  "schedule_id": "annual_schedule_2026"
}
```

**Example Response:**
```json
{
  "success": true,
  "total_conflicts": 3,
  "errors": 1,
  "warnings": 2,
  "summary": {
    "critical": 1,
    "minor": 2,
    "vessel_overlaps": 1
  },
  "conflicts": [
    {
      "type": "vessel_overlap",
      "severity": "error",
      "vessel_id": "MAERSK_LINE_1",
      "voyage1": "VOY001",
      "voyage2": "VOY002",
      "gap_hours": -12.0,
      "description": "Vessel MAERSK_LINE_1 has overlapping voyages"
    },
    {
      "type": "tight_schedule",
      "severity": "warning",
      "vessel_id": "MSC_VESSEL_2",
      "gap_hours": 18.0,
      "description": "Tight turnaround time"
    }
  ]
}
```

---

### 5. POST /api/schedule/year/compare

Compare multiple optimization strategies side-by-side.

**Request Body:**
```json
{
  "module": "deepsea",
  "strategies": ["maxrevenue", "mincost", "balance"]
}
```

**Example Response:**
```json
{
  "success": true,
  "best_strategy": "balance",
  "recommendation": "Based on optimality score, balance is recommended",
  "comparison": {
    "maxrevenue": {
      "total_revenue_usd": 16500000.0,
      "total_cost_usd": 10200000.0,
      "total_profit_usd": 6300000.0,
      "total_voyages": 52,
      "fleet_utilization_pct": 88.5,
      "avg_tce_usd": 19200.0,
      "conflicts_detected": 5,
      "optimality_score": 78.5
    },
    "mincost": {
      "total_revenue_usd": 14200000.0,
      "total_cost_usd": 8700000.0,
      "total_profit_usd": 5500000.0,
      "total_voyages": 45,
      "fleet_utilization_pct": 75.0,
      "avg_tce_usd": 17800.0,
      "conflicts_detected": 2,
      "optimality_score": 82.3
    },
    "balance": {
      "total_revenue_usd": 15000000.0,
      "total_cost_usd": 9500000.0,
      "total_profit_usd": 5500000.0,
      "total_voyages": 48,
      "fleet_utilization_pct": 82.5,
      "avg_tce_usd": 18500.0,
      "conflicts_detected": 2,
      "optimality_score": 87.3
    }
  }
}
```

---

## Optimization Strategies

### Max Revenue (`maxrevenue`)

**Goal:** Maximize total freight revenue

**Approach:**
- Prioritizes high-paying cargoes
- Allocates best vessels to premium routes
- May result in higher costs but maximum revenue

**Use When:**
- Market conditions favor high freight rates
- Commercial strategy prioritizes market share
- Capacity exceeds demand

**KPIs to Watch:**
- Total Revenue
- Average Freight Rate
- Revenue per Vessel Day

---

### Min Cost (`mincost`)

**Goal:** Minimize operational expenses

**Approach:**
- Optimizes vessel allocation for cost efficiency
- Minimizes ballast legs and repositioning
- Prioritizes fuel-efficient vessels and routes

**Use When:**
- Operating in tight margin environment
- Cost control is paramount
- Market rates are compressed

**KPIs to Watch:**
- Total Cost
- Cost per Ton-Mile
- Bunker Consumption

---

### Balanced (`balance`)

**Goal:** Optimize profit margin while maintaining utilization

**Approach:**
- Balances revenue and cost considerations
- Targets optimal fleet utilization (70-95%)
- Considers service quality and reliability

**Use When:**
- Normal market conditions
- Long-term sustainability is goal
- Multiple optimization objectives

**KPIs to Watch:**
- Total Profit
- Profit Margin %
- Fleet Utilization
- Optimality Score

---

## Conflict Types

### Vessel Overlap (Error)
- **Severity:** Critical
- **Description:** Vessel assigned to multiple voyages at the same time
- **Resolution:** Adjust voyage dates or reallocate vessel

### Tight Schedule (Warning)
- **Severity:** Minor
- **Description:** Insufficient turnaround time between voyages (<24 hours)
- **Resolution:** Add buffer time or review port operations

### Capacity Exceeded (Error)
- **Severity:** Critical
- **Description:** Cargo quantity exceeds vessel capacity
- **Resolution:** Split cargo or allocate larger vessel

---

## KPI Definitions

### Financial Metrics

- **Total Revenue:** Sum of all freight revenues
- **Total Cost:** Sum of all voyage costs (fuel, port, canal, crew, etc.)
- **Total Profit:** Total Revenue - Total Cost
- **Average TCE:** Time Charter Equivalent per vessel per day

### Operational Metrics

- **Total Voyages:** Number of completed voyage cycles
- **Total Cargo:** Total tons transported
- **Fleet Utilization:** Percentage of vessel days in revenue service
- **Optimality Score:** Composite score (0-100) measuring overall optimization quality

### Optimality Score Calculation

Score = (Profit Margin × 40%) + (Utilization Match × 30%) + (Conflict Free × 30%)

Where:
- **Profit Margin:** (Total Profit / Total Revenue) × 100
- **Utilization Match:** How close to target utilization band (70-95%)
- **Conflict Free:** Penalty for detected conflicts

---

## Usage Examples

### Example 1: Generate Optimal Annual Schedule

```python
import requests

response = requests.post(
    'http://localhost:5000/api/schedule/year',
    json={
        'module': 'deepsea',
        'strategy': 'balance',
        'config': {
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'min_utilization_pct': 75.0,
            'max_utilization_pct': 90.0
        },
        'save_as': 'annual_2026_balanced'
    }
)

result = response.json()
print(f"Profit: ${result['kpis']['total_profit_usd']:,.0f}")
print(f"Optimality: {result['kpis']['optimality_score']:.1f}/100")
```

### Example 2: Compare All Strategies

```python
response = requests.post(
    'http://localhost:5000/api/schedule/year/compare',
    json={
        'module': 'deepsea',
        'strategies': ['maxrevenue', 'mincost', 'balance']
    }
)

comparison = response.json()
print(f"Best Strategy: {comparison['best_strategy']}")

for strategy, metrics in comparison['comparison'].items():
    print(f"\n{strategy.upper()}:")
    print(f"  Profit: ${metrics['total_profit_usd']:,.0f}")
    print(f"  Score: {metrics['optimality_score']:.1f}")
```

### Example 3: Detect and Analyze Conflicts

```python
response = requests.post(
    'http://localhost:5000/api/schedule/year/conflicts',
    json={'module': 'deepsea'}
)

conflicts = response.json()
print(f"Total Conflicts: {conflicts['total_conflicts']}")
print(f"Critical: {conflicts['errors']}")
print(f"Warnings: {conflicts['warnings']}")

for conflict in conflicts['conflicts']:
    if conflict['severity'] == 'error':
        print(f" {conflict['description']}")
```

---

## Best Practices

1. **Start with Balanced Strategy**
   - Provides good starting point for most scenarios
   - Balances multiple objectives

2. **Use Compare Endpoint**
   - Evaluate all strategies before committing
   - Understand tradeoffs between approaches

3. **Monitor Conflicts**
   - Run conflict detection regularly
   - Address critical errors before execution

4. **Save Scenarios**
   - Use `save_as` parameter to preserve good schedules
   - Compare current vs. historical performance

5. **Review KPIs Holistically**
   - Don't optimize single metric in isolation
   - Consider optimality score as overall health indicator

---

## Error Handling

All endpoints return consistent error format:

```json
{
  "success": false,
  "error": "Error description",
  "details": "Additional technical details"
}
```

Common HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (schedule doesn't exist)
- `500` - Internal Server Error

---

## Performance Considerations

- **Large Fleets:** Processing time increases with fleet size
- **Long Periods:** Year-long schedules take more time than monthly
- **Strategy Comparison:** Runs multiple optimizations sequentially

Expected Processing Times:
- Small fleet (5-10 vessels): 1-3 seconds
- Medium fleet (10-30 vessels): 3-10 seconds  
- Large fleet (30+ vessels): 10-30 seconds

---

## Integration Notes

### With Existing Modules

- Compatible with DeepSea module schedules
- Can integrate with Olya module (River operations)
- Works with existing vessel/cargo data structures

### Data Requirements

Minimum required data:
- Vessel fleet definitions
- Voyage plans or cargo commitments
- Route/distance information
- Cost/revenue parameters

---

## Future Enhancements

Planned features:
- Multi-objective Pareto optimization
- Machine learning-based demand forecasting
- Real-time schedule adjustment
- Weather routing integration
- Port congestion modeling

---

## Support

For issues or questions:
- Review logs in `logs/` directory
- Check server console for detailed error messages
- Run test suite: `python test_year_schedule_api.py`

---

**Last Updated:** 2025-12-28  
**API Version:** 1.0  
**Module:** modules/year_schedule_optimizer.py
