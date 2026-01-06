# JavaScript Feature Modules

This directory contains extracted feature modules from the monolithic [`vessel_scheduler_enhanced.js`](../../vessel_scheduler_enhanced.js) file.

##  Extracted Modules

### 1. **Vessel Management** (`vessel-management.js`) - 210 lines
**Purpose:** Vessel CRUD operations and dashboard rendering

**Key Functions:**
- `renderVesselsTable()` - Render vessel list table
- `renderVesselDashboard()` - Render vessel grid cards
- `addVessel()`, `editVessel()`, `deleteVessel()` - CRUD operations
- `generateVoyageForVessel()` - Create voyage for specific vessel

**Original Lines:** 922-1131

---

### 2. **Cargo Management** (`cargo-management.js`) - 311 lines
**Purpose:** Cargo CRUD operations and assignment management

**Key Functions:**
- `renderCargoTable()` - Render cargo list table
- `addCargo()`, `editCargo()`, `deleteCargo()` - CRUD operations
- `assignVesselToCargo()` - Assign vessel to cargo
- `createVoyageFromCargo()` - Create voyage for specific cargo
- `getCargoStats()` - Get cargo statistics

**Original Lines:** 1072-1098 (table), 1335-1387 (CRUD), 1475-1522 (forms)

---

### 3. **Route Management** (`route-management.js`) - 371 lines
**Purpose:** Route catalog and transfer to voyage builder

**Key Functions:**
- `renderRoutesTable()` - Render routes table
- `addRoute()`, `deleteRoute()` - Route CRUD operations
- `transferRouteToBuilder()` - Transfer single route to builder
- `transferSelectedRoutesToBuilder()` - Bulk transfer
- `buildRouteLegCatalog()` - Build route leg catalog
- `getRouteStats()`, `findRoute()` - Route utilities

**Original Lines:** 1100-1264

---

### 4. **Trading Lanes** (`trading-lanes.js`) - 668 lines
**Purpose:** Trading lane management and volume placement

**Key Functions:**
- `generateTradingLanes()` - Show lane creation modal
- `renderTradingLanes()` - Render trading lanes grid
- `editTradingLane()` - Edit lane settings
- `assignVesselsToLane()` - Assign vessels to lane
- `applyTemplateToLaneVoyages()` - Apply template to voyages
- `placeVolumeInTradingLanes()` - Reverse sales planning
- `createShipmentsFromPlacement()` - Create shipments from volume

**Features:**
- Lane creation with route and volume targets
- Vessel suitability matching
- Voyage template integration
- Volume-to-shipment conversion
- Auto-assignment of suitable vessels

**Original Lines:** 3796-4463

---

### 5. **Voyage Builder** (`voyage-builder.js`) - 186 lines
**Purpose:** Interactive voyage creation with visual leg editor

**Key Functions:**
- `addVoyageLeg()` - Add new voyage leg
- `moveLegUp()`, `moveLegDown()` - Reorder legs
- `validateVoyage()` - Validate voyage structure
- `saveVoyageTemplate()` - Save as reusable template

**Features:**
- 7 operation types: ballast, loading, transit, discharge, canal, bunker, waiting
- Real-time validation
- Template system with API integration

**Original Lines:** 1935-2121

---

### 6. **Gantt Chart** (`gantt-chart.js`) - 325 lines
**Purpose:** Gantt chart generation and visualization

**Key Functions:**
- `generateGanttData()` - Generate timeline data
- `generateGanttFromVoyages()` - Create Gantt from voyages
- `generateSchedule()` - Full schedule generation
- `exportGantt()` - Export to Excel

**Features:**
- 30-day timeline view
- Color-coded operations
- Operation type filtering
- API integration for calculations
- Multi-source data (voyages, auto-schedule, demo)

**Original Lines:** 1655-1933

---

### 6. **Financial Analysis** (`financial-analysis.js`) - 111 lines
**Purpose:** Financial calculations and voyage economics

**Key Functions:**
- `calculateFinancialAnalysis()` - Full financial analysis
- `optimizeBunkerStrategy()` - Bunker cost optimization
- `calculateDeepSeaFinancials()` - Deep-sea voyage economics

**Calculations:**
- Bunker costs (fuel consumption × price)
- Hire costs (daily rate × voyage duration)
- Port costs (fixed fees)
- TCE (Time Charter Equivalent)
- Profit/loss analysis

**Original Lines:** 4893-5004

---

### 7. **Exports** (`exports.js`) - 372 lines
**Purpose:** Multi-format export functionality

**Key Functions:**
- `exportGantt()` - Gantt chart to Excel
- `exportFleetOverview()` - Fleet summary
- `exportVoyageSummary()` - Voyage summary
- `exportScenarios()` - Scenario comparison
- `exportDeepSeaFinancial()` - Financial analysis
- `exportOlyaCoordination()` - Olya coordination
- `exportPortStockTimeline()` - Port stock history

**Features:**
- XLSX.js integration
- Multi-sheet workbooks
- Automated calculations
- Multiple export templates

**Original Lines:** 2903-3615

---

### 8. **Network Visualization** (`network-viz.js`) - 216 lines
**Purpose:** Interactive network graph for ports and routes

**Key Functions:**
- `renderNetwork()` - Render interactive graph
- `exportNetworkSnapshot()` - Export network to Excel

**Features:**
- Vis.js integration
- Two node types: ports (circles), plants (squares)
- Two edge types: sea routes (blue solid), rail (green dashed)
- Interactive zoom/pan
- Aggregated flow calculations

**Original Lines:** 2399-2615

---

##  Integration Pattern

All modules follow ES6 module pattern:

```javascript
// Import dependencies
import { appState, getCurrentData } from '../core/app-state.js';
import { showNotification } from '../core/utils.js';

// Export individual functions
export function myFunction() {
    // Implementation
}

// Export namespace for global access
export const moduleName = {
    myFunction,
    anotherFunction
};
```

##  Progress Statistics

- **Total Lines Extracted:** 1,820+ lines
- **Original File Size:** 5,006 lines
- **Modules Created:** 9 / ~18 planned
- **Completion:** ~50%

##  Next Steps

### Remaining Modules to Extract:
1. **Cargo Management** - Cargo CRUD and assignment
2. **Route Management** - Route catalog and selection
3. **Trading Lanes** - Trading lane configuration
4. **Year Schedule** - Annual schedule generation
5. **Operational Calendar** - Monthly calendar views
6. **UI Components** - Dashboard, filters, modals

### Integration Tasks:
1. Create main entry point (`index.js`)
2. Update HTML to load ES6 modules
3. Add global namespace for legacy compatibility
4. Write unit tests for each module
5. Update documentation

##  Related Documentation

- [`MODULE_EXTRACTION_GUIDE.md`](../MODULE_EXTRACTION_GUIDE.md) - Full extraction guide
- [`../README.md`](../README.md) - JavaScript directory overview
- [`../../docs/JAVASCRIPT_MODERNIZATION_PLAN.md`](../../docs/JAVASCRIPT_MODERNIZATION_PLAN.md) - Modernization plan

##  Notes

- All modules maintain backward compatibility
- Russian localization preserved
- API integration points maintained
- State management centralized in `core/app-state.js`
