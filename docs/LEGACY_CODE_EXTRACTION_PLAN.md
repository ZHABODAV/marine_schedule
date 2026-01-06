# Legacy Code Extraction Plan

## Overview
This document outlines the strategy for extracting the 5000+ line `vessel_scheduler_enhanced.js` file into modular, maintainable components with TypeScript definitions.

## Current State
- **File**: `vessel_scheduler_enhanced.js`
- **Lines**: 5006
- **Issues**: 
  - Monolithic structure
  - Mixed concerns
  - No type safety
  - Difficult to maintain and test

## Module Extraction Strategy

### 1. Core State Management (`js/core/state-manager.js`)
**Lines**: 4-124
**Purpose**: Centralized application state
**Exports**:
- `appState`
- `appConfig`
- `getCurrentData()`
- `updateCSSVariables()`

### 2. Filter System (`js/modules/filter-system.js`)
**Lines**: 307-475
**Purpose**: Data filtering logic
**Exports**:
- `initializeFilters()`
- `applyFilters()`
- `resetFilters()`
- `populateFilterDropdowns()`

### 3. Table Renderers (`js/modules/table-renderers.js`)
**Lines**: 922-1123
**Purpose**: Table rendering functions
**Exports**:
- `renderVesselsTable()`
- `renderCargoTable()`
- `renderRoutesTable()`
- `renderVesselDashboard()`

### 4. CRUD Operations (`js/modules/crud-operations.js`)
**Lines**: 1266-1431
**Purpose**: Create, Read, Update, Delete operations
**Exports**:
- `addVessel()`, `editVessel()`, `deleteVessel()`
- `addCargo()`, `editCargo()`, `deleteCargo()`
- `addRoute()`, `deleteRoute()`

### 5. Voyage Builder (`js/modules/voyage-builder-core.js`)
**Lines**: 1935-2121
**Purpose**: Voyage construction and validation
**Exports**:
- `addVoyageLeg()`
- `validateVoyage()`
- `saveVoyageTemplate()`

### 6. Schedule Generator (`js/modules/schedule-generator.js`)
**Lines**: 1572-1892
**Purpose**: Schedule and Gantt generation
**Exports**:
- `generateSchedule()`
- `generateGanttData()`
- `generateAutoSchedule()`

### 7. Import/Export (`js/modules/data-exchange.js`)
**Lines**: 2617-2865, 2907-3067
**Purpose**: CSV import and Excel export
**Exports**:
- `handleFileUpload()`
- `exportGantt()`
- `exportFleetOverview()`
- `exportVoyageSummary()`

### 8. Trading Lanes (`js/modules/trading-lanes-manager.js`)
**Lines**: 3796-4463
**Purpose**: Trading lane management
**Exports**:
- `generateTradingLanes()`
- `renderTradingLanes()`
- `assignVesselsToLane()`

### 9. Financial Analysis (`js/modules/financial-calculator.js`)
**Lines**: 3120-3369, 4892-5004
**Purpose**: Financial calculations
**Exports**:
- `calculateDeepSeaFinancials()`
- `calculateFinancialAnalysis()`
- `optimizeBunkerStrategy()`

### 10. Network Visualization (`js/modules/network-builder.js`)
**Lines**: 2399-2615
**Purpose**: Network graph rendering
**Exports**:
- `renderNetwork()`
- `exportNetworkSnapshot()`

### 11. Storage Manager (`js/services/storage-manager.js`)
**Lines**: 3656-3794
**Purpose**: LocalStorage operations
**Exports**:
- `saveToLocalStorage()`
- `loadFromLocalStorage()`

### 12. Utilities (`js/core/utilities.js`)
**Lines**: 142-179
**Purpose**: Helper functions
**Exports**:
- `toNumber()`
- `formatDate()`
- `showNotification()`

## TypeScript Type Definitions

### Types File Structure
```
js/types/
├── state.types.ts       # Application state types
├── vessel.types.ts      # Vessel-related types
├── cargo.types.ts       # Cargo-related types
├── voyage.types.ts      # Voyage-related types
├── route.types.ts       # Route-related types
└── index.ts            # Barrel export
```

## Implementation Steps

1.  Create module directory structure
2. ⏳ Extract core utilities and state management
3. ⏳ Extract filter system
4. ⏳ Extract table renderers
5. ⏳ Extract CRUD operations
6. ⏳ Extract specialized modules (voyage builder, trading lanes, etc.)
7. ⏳ Create TypeScript definitions
8. ⏳ Update main file to import from modules
9. ⏳ Test all functionality

## Benefits

- **Maintainability**: Smaller, focused modules
- **Reusability**: Modules can be imported individually
- **Type Safety**: TypeScript definitions prevent errors
- **Testing**: Easier to unit test individual modules
- **Performance**: Potential for code splitting and lazy loading
- **Developer Experience**: Better IDE support and autocomplete

## Migration Notes

- All modules use ES6 module syntax (`export`/`import`)
- Backward compatibility maintained through barrel exports
- No breaking changes to existing functionality
- Gradual migration path supported
