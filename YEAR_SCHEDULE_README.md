# Year Schedule Optimization System

## Quick Start

This system provides comprehensive year-long vessel schedule optimization with multiple strategies and conflict detection.

###  Features

 **Multi-Strategy Optimization**
- Max Revenue: Maximize total freight revenue
- Min Cost: Minimize operational expenses
- Balanced: Optimize profit margin and utilization

 **Conflict Detection**
- Automatic vessel overlap detection
- Schedule feasibility validation
- Resource conflict identification

 **Scenario Management**
- Save/load optimized schedules
- Compare multiple scenarios
- Track historical performance

 **Comprehensive KPIs**
- Financial metrics (revenue, cost, profit)
- Operational metrics (utilization, TCE)
- Quality indicators (conflicts, optimality score)

---

##  Files Created

### Core Module
- [`modules/year_schedule_optimizer.py`](modules/year_schedule_optimizer.py:1) - Main optimization engine
  - `YearScheduleOptimizer` - Optimization algorithms
  - `YearScheduleManager` - Scenario save/load
  - `YearScheduleConfig` - Configuration options
  - `OptimizationResult` - Results data structure

### API Endpoints
Added to [`api_server.py`](api_server.py:1):
- `GET /api/schedule/year` - Retrieve schedules
- `POST /api/schedule/year` - Generate optimized schedule
- `DELETE /api/schedule/year/<id>` - Delete schedule
- `POST /api/schedule/year/conflicts` - Detect conflicts
- `POST /api/schedule/year/compare` - Compare strategies

### Documentation
- [`docs/YEAR_SCHEDULE_API.md`](docs/YEAR_SCHEDULE_API.md:1) - Complete API reference
- [`YEAR_SCHEDULE_README.md`](YEAR_SCHEDULE_README.md:1) - This file

### Examples
- [`test_year_schedule_api.py`](test_year_schedule_api.py:1) - API endpoint tests
- [`examples/year_schedule_integration.py`](examples/year_schedule_integration.py:1) - Integration examples

---

##  Usage

### Start the Server

```bash
python api_server.py
```

Server runs on `http://localhost:5000`

### Test the Endpoints

```bash
python test_year_schedule_api.py
```

This runs comprehensive tests of all endpoints.

### Run Integration Examples

```bash
python examples/year_schedule_integration.py
```

Shows 6 different usage scenarios.

---

##  API Examples

### Generate Optimized Schedule

```bash
curl -X POST http://localhost:5000/api/schedule/year \
  -H "Content-Type: application/json" \
  -d '{
    "module": "deepsea",
    "strategy": "balance",
    "config": {
      "start_date": "2026-01-01",
      "end_date": "2026-12-31",
      "min_utilization_pct": 70.0,
      "max_utilization_pct": 95.0
    },
    "save_as": "annual_schedule_2026"
  }'
```

### List All Schedules

```bash
curl http://localhost:5000/api/schedule/year?list=true
```

### Compare Strategies

```bash
curl -X POST http://localhost:5000/api/schedule/year/compare \
  -H "Content-Type: application/json" \
  -d '{
    "module": "deepsea",
    "strategies": ["maxrevenue", "mincost", "balance"]
  }'
```

### Detect Conflicts

```bash
curl -X POST http://localhost:5000/api/schedule/year/conflicts \
  -H "Content-Type: application/json" \
  -d '{"module": "deepsea"}'
```

---

##  Optimization Strategies

### Max Revenue (`maxrevenue`)
**Goal:** Maximize total freight revenue

**Best for:**
- High freight rate markets
- Premium cargo focus
- Market share growth

**Key Metrics:**
- Total Revenue
- Average Freight Rate
- Revenue per Vessel Day

### Min Cost (`mincost`)
**Goal:** Minimize operational expenses

**Best for:**
- Tight margin markets
- Cost control focus
- Efficiency optimization

**Key Metrics:**
- Total Cost
- Cost per Ton-Mile
- Bunker Efficiency

### Balanced (`balance`)
**Goal:** Optimize profit margin and fleet utilization

**Best for:**
- Normal operations
- Long-term sustainability
- Multi-objective optimization

**Key Metrics:**
- Total Profit
- Profit Margin %
- Fleet Utilization
- Optimality Score

---

##  KPI Dashboard

The system calculates comprehensive KPIs:

### Financial Performance
- **Total Revenue:** Sum of freight revenues
- **Total Cost:** Operating expenses
- **Total Profit:** Revenue - Cost
- **Profit Margin:** (Profit / Revenue) × 100
- **Average TCE:** Time Charter Equivalent per day

### Operational Metrics
- **Total Voyages:** Number of completed voyages
- **Total Cargo:** Tons transported
- **Fleet Utilization:** % of vessel days in service
- **Average Speed:** Fleet average speed

### Quality Indicators
- **Conflicts Detected:** Number of scheduling issues
- **Optimality Score:** 0-100 composite score
- **Service Level:** % of commitments met

---

##  Optimality Score

Composite score calculation (0-100):

```
Score = (Profit Margin × 40%) + 
        (Utilization Match × 30%) + 
        (Conflict Free × 30%)
```

**Components:**
- **Profit Margin (40%):** Revenue efficiency
- **Utilization Match (30%):** Target utilization adherence
- **Conflict Free (30%):** Schedule feasibility

**Interpretation:**
- 90-100: Excellent optimization
- 80-89: Good optimization
- 70-79: Fair optimization
- <70: Needs improvement

---

##  Conflict Types

### Critical Errors
- **Vessel Overlap:** Same vessel assigned to multiple voyages
- **Capacity Exceeded:** Cargo exceeds vessel capacity
- **Port Unavailable:** Port closed during planned arrival

### Warnings
- **Tight Schedule:** Insufficient turnaround time (<24h)
- **Weather Risk:** High weather disruption probability
- **Bunker Risk:** Low fuel margin

---

##  Scenario Management

### Save Schedule

```python
from modules.year_schedule_optimizer import YearScheduleManager

mgr = YearScheduleManager()
mgr.save_schedule(
    schedule_id="annual_2026",
    optimization_result=result,
    data=data,
    metadata={'purpose': 'annual planning'}
)
```

### Load Schedule

```python
schedule = mgr.load_schedule("annual_2026")
print(f"Strategy: {schedule['strategy']}")
print(f"Profit: ${schedule['kpis']['total_profit_usd']:,.0f}")
```

### List Schedules

```python
schedules = mgr.list_schedules()
for s in schedules:
    print(f"{s['schedule_id']}: Score {s['optimality_score']:.1f}")
```

---

##  Integration Example

```python
from modules.deepsea_loader import DeepSeaLoader
from modules.deepsea_calculator import DeepSeaCalculator
from modules.year_schedule_optimizer import YearScheduleOptimizer

# Load data
loader = DeepSeaLoader()
data = loader.load()

# Calculate voyages
calculator = DeepSeaCalculator(data)
data = calculator.calculate_all()

# Optimize
optimizer = YearScheduleOptimizer(data)
result = optimizer.optimize("balance")

# Display results
print(f"Revenue: ${result.total_revenue_usd:,.0f}")
print(f"Profit: ${result.total_profit_usd:,.0f}")
print(f"Score: {result.optimality_score:.1f}/100")
```

---

##  Documentation

| Document | Description |
|----------|-------------|
| [`docs/YEAR_SCHEDULE_API.md`](docs/YEAR_SCHEDULE_API.md:1) | Complete API reference with examples |
| [`test_year_schedule_api.py`](test_year_schedule_api.py:1) | API endpoint tests |
| [`examples/year_schedule_integration.py`](examples/year_schedule_integration.py:1) | 6 integration examples |

---

##  Testing

### Run API Tests
```bash
# Start server first
python api_server.py

# In another terminal
python test_year_schedule_api.py
```

### Test Coverage
-  Schedule generation (all strategies)
-  Schedule retrieval (list and specific)
-  Conflict detection
-  Strategy comparison
-  Save/load scenarios
-  Delete schedules

---

##  System Requirements

- Python 3.8+
- Flask (for API server)
- Existing modules:
  - `modules/deepsea_loader`
  - `modules/deepsea_calculator`
  - `modules/voyage_calculator`

---

##  Performance

Expected processing times:

| Fleet Size | Optimization Time |
|------------|------------------|
| 5-10 vessels | 1-3 seconds |
| 10-30 vessels | 3-10 seconds |
| 30+ vessels | 10-30 seconds |

Strategy comparison runs 3× longer (sequential optimization).

---

##  Future Enhancements

Potential improvements:
- Machine learning-based demand forecasting
- Weather routing integration
- Port congestion modeling
- Multi-objective Pareto optimization
- Real-time schedule adjustment
- What-if scenario analysis

---

##  Troubleshooting

### Server won't start
Check logs in `logs/` directory for errors.

### Type errors with Olya module
Currently optimized for DeepSea module. Use `module: "deepsea"` in requests.

### No conflicts detected
This is good! Means schedule is feasible.

### Low optimality score
Try different strategies or adjust configuration targets.

---

##  Support

For issues:
1. Check server logs
2. Review [`docs/YEAR_SCHEDULE_API.md`](docs/YEAR_SCHEDULE_API.md:1)
3. Run test suite for diagnostics
4. Check example integrations

---

##  License

Part of the Vessel Scheduler System project.

---

**Last Updated:** 2025-12-28  
**Version:** 1.0  
**Status:** Production Ready 
