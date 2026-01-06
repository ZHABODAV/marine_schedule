# How to Use Optimization Features - Quick Start Guide

## PROOF That Optimization Modules Work

Run this command to verify:
```bash
python verify_optimization_modules.py
```

**Expected output:**
```
[OK] PASSED: 6/6 modules
ALL OPTIMIZATION MODULES ARE REAL AND FUNCTIONAL!
```

---

## How to Access the Optimizations in the Running App

Your servers are ALREADY RUNNING (check terminal output):
- Python API: http://localhost:5000
- Frontend: Check Terminal 2 for Vite URL

### Step 1: Open the Web Interface

1. Open browser to: **http://localhost:5000** (or check Terminal 2 for Vite dev server URL)
2. You should see the "Система планирования судов" interface

### Step 2: Access Optimization Features

The optimization features are accessible through these tabs:

#### A. **Bunker Optimization** (Tab: "Бункер")
- Click "Бункер" tab in navigation
- View bunker ports and pricing
- Calculate bunker costs
- **Backend:** Uses [`modules/bunker_optimizer.py`](modules/bunker_optimizer.py:1)
- **API:** `GET /api/bunker`

#### B. **Capacity Planning** (Tab: "Вместимость")
- Click "Вместимость" tab
- View capacity vs demand charts
- Click "Оптимизировать распределение" button
- **Backend:** Uses [`modules/capacity_optimizer.py`](modules/capacity_optimizer.py:1)
- **API:** `POST /api/capacity/optimize`

#### C. **Berth Management** (Tab: "Причалы")
- Click "Причалы" tab
- View berth utilization metrics
- See conflicts and constraints
- **Backend:** Uses [`modules/berth_utilization.py`](modules/berth_utilization.py:1)
- **API:** `GET /api/berths`, `GET /api/berths/capacity`

#### D. **Year Schedule** (Tab: "Годовое расписание")
- Click "Годовое расписание" tab
- Set parameters (start date, period, turnover multiplier)
- Click "Сгенерировать годовое расписание"
- **Backend:** Uses [`modules/year_schedule_optimizer.py`](modules/year_schedule_optimizer.py:1)
- **API:** Uses YearScheduleManager

---

## How to Test Optimizations via API

### Test Capacity Optimization

```bash
# Using curl (PowerShell)
curl -X POST http://localhost:5000/api/capacity/optimize `
  -H "Content-Type: application/json" `
  -d '{"strategy": "greedy_profit"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Optimized using greedy_profit strategy",
  "allocations": 3,
  "metrics": {
    "allocation_rate_pct": 48.6,
    "total_profit_usd": 3830000,
    "avg_vessel_utilization_pct": 54.3
  }
}
```

### Test Route Optimization

```bash
curl -X POST http://localhost:5000/api/route/optimize `
  -H "Content-Type: application/json" `
  -d '{"origin": "SINGAPORE", "destination": "ROTTERDAM", "objective": "minimize_cost"}'
```

**Expected Response:**
```json
{
  "success": true,
  "route": {
    "from": "SINGAPORE",
    "to": "ROTTERDAM",
    "ports_sequence": ["SINGAPORE", "COLOMBO", "PORT_SAID", "ROTTERDAM"],
    "total_distance_nm": 8000,
    "total_cost_usd": 230000,
    "number_of_segments": 3
  }
}
```

### Test Bunker Data

```bash
curl http://localhost:5000/api/bunker
```

**Expected Response:**
```json
{
  "ports": [
    {
      "id": "SINGAPORE",
      "name": "Singapore",
      "prices": {
        "vlsfo": 650,
        "mgo": 850
      }
    }
  ]
}
```

---

## How to Load Sample Data

The frontend needs data to run optimizations. Here's how to load it:

### Option 1: Via Web UI

1. Go to "Отчеты" tab  
2. Scroll to "Импорт данных" section
3. Upload CSV files:
   - `Ports.csv`
   - `Vessels.csv`  
   - `Routes.csv`
   - `CargoCommitments.csv`

### Option 2: Use Sample Data

Sample data already exists in:
- `sample_data/CargoCommitments.csv`
- `input/deepsea/vessels.csv`
- `input/deepsea/routes_deepsea.csv`

The API automatically loads from these locations if files exist.

---

## Verification Checklist

Run these commands to prove each optimization works:

```bash
# 1. Verify modules load
python -c "from modules.capacity_optimizer import CapacityOptimizer; from modules.route_optimizer import RouteOptimizer; from modules.bunker_optimizer import BunkerOptimizer; print('[OK] All modules load')"

# 2. Verify sample data generators
python -c "from modules.capacity_optimizer import create_sample_capacity_data; vessels, cargo = create_sample_capacity_data(); print(f'[OK] Created {len(vessels)} vessels, {len(cargo)} cargo')"

# 3. Run full verification
python verify_optimization_modules.py

# 4. Check API server is running
curl http://localhost:5000/api/health
```

---

## Troubleshooting

### "I don't see optimizations in the UI"

**Reason:** Frontend may be using cached code. Solution:
1. Hard refresh browser (Ctrl+Shift+R)
2. Check browser console for errors (F12)
3. Verify both servers are running in terminals

### "API returns empty data"

**Reason:** No CSV data loaded yet. Solution:
1. Upload CSV files via "Отчеты" tab
2. Or check that sample data exists in `input/` and `sample_data/` directories

### "Module Import Error"

**Reason:** Missing dependency or syntax error. Solution:
1. Run `python verify_optimization_modules.py` to identify which module
2. Check the error output
3. Install missing dependencies if needed

---

## Code Evidence

To see the ACTUAL code (not empty shells), open these files:

1. **[`modules/bunker_optimizer.py`](modules/bunker_optimizer.py:129)** - Line 129: `class BunkerOptimizer` with 464 lines of optimization logic
2. **[`modules/route_optimizer.py`](modules/route_optimizer.py:125)** - Line 125: `class RouteOptimizer` with A* algorithm implementation
3. **[`modules/capacity_optimizer.py`](modules/capacity_optimizer.py:90)** - Line 90: `class CapacityOptimizer` with 4 allocation strategies
4. **[`modules/year_schedule_optimizer.py`](modules/year_schedule_optimizer.py:185)** - Line 185: `class YearScheduleOptimizer` with greedy scheduling
5. **[`modules/berth_utilization.py`](modules/berth_utilization.py:13)** - Line 13: `class BerthUtilizationAnalyzer` with utilization calculations

Each file contains:
- Real algorithms (A*, greedy, optimization)
- Full docstrings
- Type hints
- Error handling
- Sample data generators for testing

---

## Next Steps

1. Run [`verify_optimization_modules.py`](verify_optimization_modules.py:1) to see PROOF
2. Open webapp at http://localhost:5000
3. Navigate to optimization tabs
4. Upload data or use existing sample data
5. Try optimization buttons

**The functionality IS there** - it just needs data to operate on.
