# Financial System Changes - Cost Allocations & Revenue Removal

## Overview

The financial results logic has been updated to:

1. **Remove revenue/profit calculations** from all results
2. **Add cost allocation fields** to voyages and voyage templates

---

## 1. Backend Changes

### Data Structures Modified

#### DeepSea Module ([`modules/deepsea_data.py`](../modules/deepsea_data.py))

**`VoyagePlan` class** - Added cost allocation fields:

```python
operational_cost_allocation: float = 0  # Custom operational costs
overhead_cost_allocation: float = 0     # Overhead allocation  
other_cost_allocation: float = 0        # Other allocated costs
```

**`CalculatedVoyage` class** - Updated:

- **REMOVED**: `profit_usd` property, `tce_usd` property
- **KEPT** (for backward compatibility): `freight_revenue_usd` field (not used in calculations)
- **ADDED**: Same 3 cost allocation fields as VoyagePlan
- **UPDATED**: `total_cost_usd` property now includes all allocations:

  ```python
  total_cost_usd = (bunker_cost + port_cost + canal_cost + hire_cost +
                    operational_allocation + overhead_allocation + other_allocation)
  ```

#### Olya Module ([`modules/olya_data.py`](../modules/olya_data.py))

**`CalculatedVoyage` class** - Added:

```python
operational_cost_allocation: float = 0
overhead_cost_allocation: float = 0
other_cost_allocation: float = 0
hire_cost_usd: float = 0
bunker_cost_usd: float = 0
port_cost_usd: float = 0

@property
def total_cost_usd(self) -> float:
    return (hire_cost_usd + bunker_cost_usd + port_cost_usd +
            operational_allocation + overhead_allocation + other_allocation)
```

### Calculator Updates

#### [`modules/deepsea_calculator.py`](../modules/deepsea_calculator.py)

- **Line 54**: Changed log output from TCE to total cost
- **Line 80-95**: Added cost allocation fields when creating voyage
- **Line 134**: Removed `freight_revenue_usd` calculation
- **Line 397-405**: Updated CSV export to include allocation columns, removed revenue/profit/TCE columns

#### Main Scripts Updated

- [`main_deepsea.py`](../main_deepsea.py) - Lines 72-83: Show cost breakdown instead of revenue/profit
- [`run_year_gantt.py`](../run_year_gantt.py) - Lines 80-92: Show cost breakdown instead of revenue/profit
- [`examples/year_schedule_calculations.py`](../examples/year_schedule_calculations.py) - Multiple functions updated

---

## 2. Voyage Template Structure

### Template JSON Format ([`data/voyage_templates.json`](../data/voyage_templates.json))

Each template now includes:

```json
{
  "id": "template_xxx",
  "name": "Template Name",
  "description": "Description",
  "category": "Custom",
  "ports": ["Port1", "Port2"],
  "estimatedDays": 20,
  "legs": [ /* leg data */ ],
  "costAllocations": {
    "operationalCost": 0,
    "overheadCost": 0,
    "otherCost": 0
  },
  "createdAt": "2025-12-23T13:46:20.688947"
}
```

---

## 3. UI Updates Required

### Forms to Update

#### Cargo/Voyage Input Form

**Location**: `vessel_scheduler_complete.html` - Cargo Modal (around line 2348)

**Add these fields after existing cargo inputs**:

```html
<div class="input-group">
    <label for="operationalCost">Operational Cost Allocation (USD):</label>
    <input type="number" id="operationalCost" name="operationalCost" 
           value="0" min="0" step="1000">
</div>

<div class="input-group">
    <label for="overheadCost">Overhead Cost Allocation (USD):</label>
    <input type="number" id="overheadCost" name="overheadCost" 
           value="0" min="0" step="1000">
</div>

<div class="input-group">
    <label for="otherCost">Other Cost Allocation (USD):</label>
    <input type="number" id="otherCost" name="otherCost" 
           value="0" min="0" step="1000">
</div>
```

#### Voyage Template Builder

**Location**: Where templates are created/edited

**Add same 3 cost allocation fields** to template form

### JavaScript Updates Required

#### When saving cargo/voyage ([`vessel_scheduler_enhanced.js`](../vessel_scheduler_enhanced.js))

**Add to cargo object**:

```javascript
const cargoData = {
    // ... existing fields ...
    operationalCost: parseFloat(document.getElementById('operationalCost').value) || 0,
    overheadCost: parseFloat(document.getElementById('overheadCost').value) || 0,
    otherCost: parseFloat(document.getElementById('otherCost').value) || 0
};
```

#### When saving voyage template
**Add to template object**:

```javascript
const templateData = {
    // ... existing fields ...
    costAllocations: {
        operationalCost: parseFloat(document.getElementById('operationalCost').value) || 0,
        overheadCost: parseFloat(document.getElementById('overheadCost').value) || 0,
        otherCost: parseFloat(document.getElementById('otherCost').value) || 0
    }
};
```

### Display/Report Updates

#### Financial Summary Display

**REMOVE** these fields from all financial summaries:

- Revenue
- Profit
- Profit Margin %
- TCE (Time Charter Equivalent)

**SHOW** these instead:

- Total Costs (broken down by):
  - Hire Costs
  - Bunker Costs
  - Port Costs
  - Canal Costs (if applicable)
  - Operational Cost Allocation
  - Overhead Cost Allocation
  - Other Cost Allocation

#### Voyage Details Tables

**Update columns** (around line 4900 in `vessel_scheduler_enhanced.js`):

**REMOVE**:

```javascript
// Remove these columns:
<td style="color: var(--accent-success);">$${v.revenue.toLocaleString()}</td>
<td>$${v.profit.toLocaleString()}</td>
<td>$${v.tce.toFixed(0)}</td>
```

**ADD**:

```javascript
// Add these columns:
<td>$${v.bunkerCost.toLocaleString()}</td>
<td>$${v.hireCost.toLocaleString()}</td>
<td>$${v.operationalCost.toLocaleString()}</td>
<td>$${v.overheadCost.toLocaleString()}</td>
<td>$${v.otherCost.toLocaleString()}</td>
<td style="font-weight: 600;">$${v.totalCost.toLocaleString()}</td>
```

#### KPI Calculations ([`vessel_scheduler_enhanced.js`](../vessel_scheduler_enhanced.js) around line 2098)

**REMOVE**:

```javascript
revenue: Math.random() * 500000 + 100000,
profit: kpi.revenue - kpi.cost,
tce: kpi.profit / kpi.duration,
```

**UPDATE**:

```javascript
totalCost: Math.random() * 300000 + 50000,
costPerDay: kpi.totalCost / kpi.duration,
costPerNM: kpi.totalCost / kpi.distance,
```

---

## 4. API Updates  

### Endpoints Already Support Cost Allocations

The API endpoints in [`api_extensions.py`](../api_extensions.py ) will automatically handle the new `costAllocations` field in templates when:

- Creating templates: POST `/api/voyage-templates`
- Updating templates: PUT `/api/voyage-templates/<id>`
- Retrieving templates: GET `/api/voyage-templates`

The backend will store and retrieve the `costAllocations` object as part of the template JSON.

---

## 5. Summary of Changes by File

| File | Changes |
|------|---------|
| **Data Models** |
| `modules/deepsea_data.py` | Added cost allocations, removed profit/TCE properties |
| `modules/olya_data.py` | Added cost allocations and total_cost property |
| **Calculators** |
| `modules/deepsea_calculator.py` | Removed revenue calc, added allocation support, updated exports |
| **Main Scripts** |
| `main_deepsea.py` | Updated summary to show cost breakdown only |
| `run_year_gantt.py` | Updated statistics to show cost breakdown only |
| `examples/year_schedule_calculations.py` | Reworked all financial functions for costs only |
| **Data** |
| `data/voyage_templates.json` | Added costAllocations object to all templates |

---

## 6. Migration Notes

### Existing Data

- Existing templates will work but won't have cost allocations (defaults to 0)
- `freight_revenue_usd` field still exists in voyage plans for backward compatibility but is not used
- Old CSV exports may have revenue/profit columns - these should be ignored

### Testing Checklist

- [ ] Cargo form saves cost allocations correctly
- [ ] Template form saves cost allocations correctly
- [ ] Financial summaries show only costs (no revenue/profit)
- [ ] Voyage detail tables show cost breakdown
- [ ] Excel/CSV exports include allocation columns
- [ ] API correctly stores/retrieves cost allocations

---

## 7. Example Usage

### Creating a Voyage with Cost Allocations

```javascript
const voyageData = {
    vessel_id: "SHIP001",
    route_id: "ROUTE_123",
    cargo_type: "GRAIN",
    qty_mt: 75000,
    load_port: "HOUSTON",
    disch_port: "ROTTERDAM",
    laycan_start: "2026-01-15",
    laycan_end: "2026-01-20",
    charterer: "ABC_TRADING",
    freight_rate_mt: 0,  // Not used anymore
    operational_cost_allocation: 15000,  // NEW
    overhead_cost_allocation: 8000,      // NEW
    other_cost_allocation: 5000          // NEW
};
```

### Expected Cost Breakdown

```
Total Costs: $450,000
  - Hire Costs:        $180,000
  - Bunker Costs:      $120,000
  - Port Costs:        $90,000
  - Canal Costs:       $32,000
  - Operational:       $15,000
  - Overhead:          $8,000
  - Other:             $5,000
```
