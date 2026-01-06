# JavaScript Module Extraction Guide

This document outlines the module splitting process from the monolithic `vessel_scheduler_enhanced.js` (5006 lines) into smaller, maintainable ES6 modules.

## Completed Modules

### Core Modules (`js/core/`)

#### 1. [`app-state.js`](core/app-state.js) - 151 lines

**Purpose:** Centralized application state management

**Exports:**

- `appConfig` - Application configuration object
- `appState` - Main application state with module-specific data
- `trading LanesState` - Trading lanes state
- `getCurrentData()` - Get current module's data

**Contains:**

- Module data structures (deepsea, balakovo, olya)
- Global filters and cross-filters
- Voyage builder state
- Port stocks and sales plan
- Legacy getters for backward compatibility

**Original Location:** Lines 4-120

---

#### 2. [`config.js`](core/config.js) - 48 lines

**Purpose:** Configuration loading and CSS variable management

**Exports:**

- `updateCSSVariables()` - Updates CSS custom properties for Gantt colors
- `loadConfigFromServer()` - Async function to load config from API

**Contains:**

- CSS variable updates for operation colors
- Server configuration loading

**Original Location:** Lines 126-140, 184-194

---

#### 3. [`utils.js`](core/utils.js) - 65 lines

**Purpose:** Common utility functions

**Exports:**

- `toNumber(v)` - Safe number conversion
- `formatDate(dateStr)` - Localized date formatting
- `showNotification(message, type)` - Notification popup system

**Contains:**

- Number parsing with comma/dot handling
- Russian locale date formatting
- Toast notification system with auto-dismiss

**Original Location:** Lines 142-179

---

### Service Modules (`js/services/`)

#### 4. [`storage-service.js`](services/storage-service.js) - 136 lines
**Purpose:** LocalStorage operations for state persistence

**Exports:**

- `saveToLocalStorage()` - Save app state to localStorage
- `loadFromLocalStorage()` - Load app state from localStorage
- `updateSessionInfo()` - Update session info display
- `saveTradingLanesToLocalStorage()` - Save trading lanes separately

**Contains:**

- Comprehensive state serialization
- Trading lanes Map serialization
- Session info with version tracking
- Auto-save mechanism (30-second interval)

**Original Location:** Lines 3656-3794

---

## Module Structure Overview

```
js/
├── core/                    # Core application modules
│   ├── app-state.js        #  State management (151 lines)
│   ├── config.js           #  Configuration(48 lines)
│   └── utils.js            #  Utilities (65 lines)
│
├── modules/                 # Feature modules
│   ├── vessel-management.js  #  Vessel operations (210 lines)
│   ├── cargo-management.js   # ⏳ Pending
│   ├── route-management.js   # ⏳ Pending
│   ├── voyage-builder.js     #  Voyage construction (186 lines)
│   ├── gantt-chart.js        #  Gantt visualization (325 lines)
│   ├── financial-analysis.js #  Financial calculations (111 lines)
│   ├── exports.js            #  Export functionality (372 lines)
│   └── network-viz.js        #  Network graphs (216 lines)
│
├── services/                # Service layer
│   ├── api-client.js       # ⏳ Pending
│   └── storage-service.js  #  Storage operations (136 lines)
│
└── ui/                      # UI components
    ├── dashboard.js         #  Dashboard & cross-filters (320 lines)
    ├── filters.js           #  Global filters (160 lines)
    └── modals.js            #  Modal dialogs (330 lines)
```

## Progress Statistics

- **Total Lines Extracted:** 2630+ lines
- **Original File Size:** 5006 lines
- **Modules Created:** 12 / ~18
- **Progress:** ~68% complete

## Benefits Achieved

### 1. Code Organization

- Clear separation of concerns
- Single Responsibility Principle
- Easier to locate and modify code

### 2. Maintainability

- Smaller files (~50-150 lines each)
- Focused functionality
- Easier code reviews

### 3. Reusability

- Functions can be imported where needed
- Reduces code duplication
- Enables tree-shaking

### 4. Modern JavaScript

- ES6 modules with import/export
- Async/await for API calls
- Arrow functions and template literals

## Newly Extracted Modules (Dec 25, 2025)

### Feature Modules (`js/modules/`)

#### 5. [`voyage-builder.js`](modules/voyage-builder.js) - 186 lines

**Purpose:** Interactive voyage creation and leg management

**Exports:**

- `addVoyageLeg()` - Add new leg to voyage
- `moveLegUp(btn)` - Move leg up in sequence
- `moveLegDown(btn)` - Move leg down in sequence
- `removeVoyageLeg(legId)` - Remove leg from voyage
- `validateVoyage()` - Validate voyage structure
- `saveVoyageTemplate()` - Save as reusable template
- `populateVoyageVesselSelect()` - Populate vessel dropdown

**Contains:**

- Interactive leg editor with drag/reorder
- Voyage validation logic
- Template creation and API integration
- Support for 7 operation types (ballast, loading, transit, discharge, canal, bunker, waiting)

**Original Location:** Lines 1935-2121

---

#### 6. [`gantt-chart.js`](modules/gantt-chart.js) - 325 lines

**Purpose:** Gantt chart generation and visualization

**Exports:**

- `generateGanttData(days)` - Generate Gantt data structure
- `generateGanttFromVoyages(voyages, days)` - Create Gantt from voyages
- `generateSchedule()` - Full schedule generation with API
- `exportGantt()` - Export to Excel

**Contains:**

- Multi-source Gantt generation (voyages, auto-schedule, random)
- 30-day timeline visualization
- Operation type filtering
- Color-coded operation cells
- API integration for calculation
- Vessel-centric timeline view

**Original Location:** Lines 1655-1933

---

#### 7. [`financial-analysis.js`](modules/financial-analysis.js) - 111 lines

**Purpose:** Financial calculations and cost analysis

**Exports:**

- `calculateFinancialAnalysis()` - Complete financial analysis
- `optimizeBunkerStrategy()` - Bunker cost optimization
- `calculateDeepSeaFinancials()` - Deep-sea voyage financials

**Contains:**

- Multi-factor cost calculation (bunker, hire, port)
- TCE (Time Charter Equivalent) calculation
- Profit/loss analysis
- 15% bunker optimization potential
- Detailed voyage-level breakdown
- API integration with fallback

**Original Location:** Lines 4893-5004

---

#### 8. [`exports.js`](modules/exports.js) - 372 lines

**Purpose:** Export functionality for various data formats

**Exports:**

- `exportGantt()` - Export Gantt chart to Excel
- `exportFleetOverview()` - Fleet summary export
- `exportVoyageSummary()` - Voyage summary export
- `exportScenarios()` - Scenario comparison export
- `exportDeepSeaFinancial()` - Financial analysis export
- `exportOlyaCoordination()` - Olya coordination export
- `exportVoyageComparison()` - Voyage comparison export
- `exportPortStockTimeline()` - Port stock history export

**Contains:**

- XLSX.js integration for Excel exports
- Multiple export templates
- Scenario comparison generator
- Deep Sea financial calculator
- Olya coordination calculator
- Multi-sheet workbook generation

**Original Location:** Lines 2903-3615

---

#### 9. [`network-viz.js`](modules/network-viz.js) - 216 lines

**Purpose:** Network graph visualization

**Exports:**

- `renderNetwork()` - Render interactive network graph
- `exportNetworkSnapshot()` - Export network to Excel

**Contains:**

- Vis.js network integration
- Two node types: ports (circles) and plants (squares)
- Two edge types: sea routes (solid blue) and rail (dashed green)
- Interactive graph with zoom/pan
- Aggregated flow calculations
- Multi-sheet export (nodes, edges, summary)

**Original Location:** Lines 2399-2615

---

### UI Modules (`js/ui/`)

#### 10. [`dashboard.js`](ui/dashboard.js) - 320 lines
**Purpose:** Dashboard display and cross-filtering functionality

**Exports:**
- `updateDashboard()` - Update dashboard summary statistics
- `populateCrossFilterDropdowns()` - Populate cross-filter controls
- `applyCrossFilters()` - Apply cross-filters and auto-populate related filters
- `clearCrossFilters()` - Clear all cross-filters
- `renderUnifiedPanel()` - Render unified information panel with cross-filtered data

**Contains:**
- Summary KPIs (active vessels, pending cargo, voyages, utilization)
- Cross-filter system (cargo ↔ vessel ↔ voyage ↔ route)
- Unified info panel with integrated cargo-vessel-voyage-route cards
- Smart filter auto-population
- Real-time dashboard updates

**Original Location:** Lines 497-829

---

#### 11. [`filters.js`](ui/filters.js) - 160 lines
**Purpose:** Global and operation-type filtering functionality

**Exports:**
- `initializeFilters()` - Initialize filter controls
- `initializeOpTypeFilters()` - Initialize operation type checkboxes
- `updateOpTypeFilters()` - Update operation type filter state
- `populateFilterDropdowns()` - Populate filter dropdowns with data
- `applyFilters()` - Apply current filter settings
- `resetFilters()` - Reset all filters to defaults
- `applyFiltersToData(data)` - Apply filters to a dataset

**Contains:**
- Date range filtering (laycan start/end)
- Product/commodity filtering
- Port filtering (load/discharge)
- Vessel filtering
- Operation type filtering (7 types: loading, discharge, transit, ballast, canal, bunker, waiting)
- Filter state management in appState

**Original Location:** Lines 307-475

---

#### 12. [`modals.js`](ui/modals.js) - 330 lines
**Purpose:** Modal dialogs for vessel, cargo, and route management

**Exports:**
- `openVesselModal(id)` - Open vessel add/edit modal
- `closeVesselModal()` - Close vessel modal
- `openCargoModal(id)` - Open cargo add/edit modal
- `closeCargoModal()` - Close cargo modal
- `openRouteModal()` - Open route add modal
- `closeRouteModal()` - Close route modal
- `showVoyageDetailsModal(voyageId)` - Display voyage details
- `showCustomVoyageSelectionModal()` - Custom voyage selection for Gantt
- `showCreateTradingLaneModal()` - Trading lane creation modal

**Contains:**
- Add/edit modals for vessels, cargo, routes
- Port dropdown population
- Voyage details viewer with leg breakdown
- Custom voyage selection with checkboxes
- Trading lane creation form
- Template integration
- Modal state management

**Original Location:** Lines 1267-1421, 3807-3925, 4466-4548

---

## Integration Steps

### 1. HTML Updates Required

```html
<!-- Add type="module" to enable ES6 modules -->
<script type="module" src="js/core/app-state.js"></script>
<script type="module" src="js/core/config.js"></script>
<script type="module" src="js/core/utils.js"></script>
<script type="module" src="js/services/storage-service.js"></script>
```

### 2. Import Examples

```javascript
// In a new module
import { appState, getCurrentData } from './core/app-state.js';
import { showNotification } from './core/utils.js';
import { saveToLocalStorage } from './services/storage-service.js';

// Use imported functions
const data = getCurrentData();
showNotification('Data loaded', 'success');
saveToLocalStorage();
```

## Next Steps

### Immediate (Week 1-2)

1.  Extract core modules (state, config, utils)
2.  Extract storage service
3. ⏳ Extract vessel management module
4. ⏳ Extract cargo management module
5. ⏳ Extract route management module

### Short-term (Month 1)

6. Extract UI modules (dashboard, filters, modals)
2. Extract gantt chart module
3. Extract export functionality
4. Create main application entry point
5. Update HTML to load modules

### Testing

11. Unit tests for utility functions
2. Integration tests for modules
3. End-to-end testing
4. Browser compatibility testing

## Notes

- All modules use ES6 import/export syntax
- Modules maintain backward compatibility where needed
- State management remains centralized
- Auto-save functionality preserved
- Russian localization maintained

## Related Documentation

- [`docs/JAVASCRIPT_MODERNIZATION_PLAN.md`](../docs/JAVASCRIPT_MODERNIZATION_PLAN.md) - Full modernization plan
- [`js/README.md`](README.md) - JavaScript modules overview
- [`js/api-validation.js`](api-validation.js) - Validation module (already modular)
- [`js/api-documentation-generator.js`](api-documentation-generator.js) - Documentation generator (already modular)
