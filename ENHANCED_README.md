# Vessel Scheduler Enhanced - Version 3.0.0

## Overview

The **Vessel Scheduler Enhanced** is a comprehensive maritime logistics planning system that enables end-to-end management of vessel operations, cargo commitments, voyage planning, and network optimization. This enhanced version includes advanced features for multi-module operations, automated scheduling, voyage building, comparison analytics, and network visualization.

## Key Features

### 1. **Unified Global Filters**

- Filter data across all modules by:
  - Module (Deep Sea, Balakovo, Olya)
  - Date range (start/end)
  - Product/Commodity type
  - Port (loading/discharge)
  - Vessel ID
  - Operation types (Loading, Discharge, Transit, Ballast, Canal, Bunker, Waiting)

### 2. **Multi-Module Architecture**

- **Deep Sea Module**: International maritime cargo operations
- **Balakovo Module**: Regional river-sea operations
- **Olya Module**: Caspian Sea and river coordination

Each module maintains separate master and planning data with independent computed results.

### 3. **CSV Import Pipeline**

#### Master Data (Delimiter: `;`)

- **Ports.csv**: Port definitions with loading/discharge rates, coordinates, capabilities
- **Routes.csv**: Route definitions with distance, duration, canal transits, waypoints
- **Vessels.csv**: Vessel fleet with DWT, capacity, speed, daily hire rates
- **Cargo.csv**: Cargo type definitions (optional)

#### Planning Data (Delimiter: `;`)

- **CargoCommitments.csv**: Cargo obligations with laycan windows and delivery deadlines
- **rail_cargo.csv**: Rail shipments from plants to ports
- **cargo_movements.csv**: Actual/planned cargo movements
- **voyage_legs.csv**: Pre-defined voyage leg sequences

### 4. **localStorage Persistence**

All data is automatically saved to browser localStorage:

- Master data (ports, routes, vessels, cargo types)
- Planning data (commitments, rail cargo, movements, voyage legs)
- Computed data (voyages, voyage templates, scenarios, schedules)
- Port stock accumulators
- Sales plan inputs
- Filter states

Auto-save interval: 30 seconds

### 5. **RouteLeg Catalog**

Automatically builds a catalog of route legs from imported Routes.csv, including:

- Direct port-to-port legs
- Distance and duration
- Canal transits
- Waypoint sequences

### 6. **Auto-Schedule Generator**

Transforms cargo commitments into complete voyage schedules:

1. **Input**: Pending cargo commitments
2. **Process**:
   - Assigns vessels to commitments
   - Generates voyage legs (ballast → loading → laden transit → discharge)
   - Calculates durations based on port rates and vessel speeds
   - Applies laycan windows
3. **Output**: Complete voyage schedules with timeline

### 7. **Interactive Voyage Builder**

- **Add Legs**: Build voyages leg-by-leg
- **Leg Types**: Ballast, Loading, Transit, Discharge, Canal, Bunker, Waiting
- **Validation**: Real-time validation of leg sequences
- **Templates**: Save validated voyages as reusable templates

### 8. **Voyage Comparison Analytics**

- Select multiple voyages or scenarios
- Compare KPIs side-by-side:
  - Distance (nautical miles)
  - Duration (days)
  - Revenue ($)
  - Cost ($)
  - Profit ($)
  - TCE ($/day)
- Export comparison results to Excel

### 9. **Port Cargo Accumulation Engine**

Track daily stock levels at ports:

- **Rail Inflow**: Cargo arriving by rail from plants
- **Sea Outflow**: Cargo loaded onto vessels
- **Daily Stock**: Running balance with alerts (LOW/HIGH/OK status)
- 60-day forecast
- Export to Excel

### 10. **Sales Plan Calculator**

- **Required Shipments**: Total MT from commitments
- **Suggested Trips**: Calculated based on average vessel capacity
- **Capacity Gap**: Difference between demand and available capacity
- Breakdown by product type

### 11. **Network Visualization (vis-network)**

Interactive graph showing:

- **Ports** (blue circles): Maritime terminals
- **Plants** (green squares): Rail cargo origins
- **Sea Routes** (solid blue arrows): Maritime connections with distance
- **Rail Routes** (dashed green arrows): Rail connections

### 12. **Enhanced Export Modules**

All exports generate Excel files (.xlsx):

- Gantt Chart (30-day vessel schedule)
- Fleet Overview
- Voyage Summary
- Scenario Comparison
- Deep Sea Financial Analysis
- Olya Coordination
- **New**: Voyage Comparison Results
- **New**: Port Stock Timeline
- **New**: Network Snapshot (future)

### 13. **Schedule Tab Enhancements**

- **Operation Types Legend**: Moved from Dashboard to Schedule
- **Operation Type Filters**: Checkboxes to filter Gantt by operation type
- **Module-Specific Schedules**: Auto-switch based on active module

## File Structure

```
Scheduler/
├── vessel_scheduler_enhanced.html    # Main HTML file
├── vessel_scheduler_enhanced.js      # Complete JavaScript implementation
├── ENHANCED_README.md                # This documentation
└── sample_data/                      # Sample CSV files
    ├── Ports.csv
    ├── Routes.csv
    ├── Vessels.csv
    ├── CargoCommitments.csv
    └── rail_cargo.csv
```

## Getting Started

### 1. **Initial Setup**

1. Open [`vessel_scheduler_enhanced.html`](vessel_scheduler_enhanced.html) in a modern web browser
2. The app loads with sample data for immediate testing

### 2. **Import Master Data**

**Recommended order**:

1. Navigate to **Reports** tab → **Import Data** section
2. Import `Ports.csv`
3. Import `Routes.csv` (triggers RouteLeg catalog build)
4. Import `Vessels.csv`
5. (Optional) Import `Cargo.csv`

### 3. **Import Planning Data**

1. Import `CargoCommitments.csv`
2. (Optional for Balakovo/Olya modules) Import `rail_cargo.csv`
3. (Optional) Import `cargo_movements.csv`
4. (Optional) Import `voyage_legs.csv`

### 4. **Basic Workflow**

#### **Dashboard**

- View key metrics: Active vessels, Pending cargo, Total distance, Fleet utilization
- Metrics update based on global filters

#### **Vessels/Cargo/Routes Tabs**

- Browse and manage master data
- Add/edit entries via modal forms
- All changes are auto-saved

#### **Schedule Tab**

- Click "Generate Schedule" to create 30-day Gantt chart
- Use operation type checkboxes to filter displayed operations
- Export Gantt to Excel

#### **Voyage Builder Tab**

1. Click "Add Leg" to add voyage segments
2. Fill in leg details (type, from, to, distance)
3. Click "Validate" to check for errors
4. Click "Save Template" to store as reusable template

#### **Comparison Tab**

1. Checkboxes appear for all generated voyages and scenarios
2. Select items to compare
3. Click "Compare Selected"
4. View side-by-side KPI comparison
5. Export to Excel

#### **Port Stock Tab**

1. Select a port from dropdown
2. Click "Calculate"
3. View 60-day daily stock timeline
4. Export to Excel

#### **Sales Plan Tab**

1. Click "Calculate Plan"
2. View required shipments, suggested trips, capacity gap
3. Review breakdown by product

#### **Network Tab**

1. Click "Generate Network"
2. Interact with graph (zoom, drag nodes)
3. Export snapshot (future feature)

## Global Filters Usage

Access the global filter bar at the top of the page:

1. **Module**: Filter to specific module (or "All Modules")
2. **Date Range**: Set start/end dates
3. **Product**: Select commodity type
4. **Port**: Select specific port
5. **Vessel**: Select specific vessel
6. **Apply Filters**: Click to apply selections
7. **Reset**: Clear all filters

Filters affect:

- Dashboard metrics
- Vessel/Cargo table displays
- Schedule generation
- All computed results

## Data Model

### Application State Structure

```javascript
appState = {
    currentModule: 'deepsea',  // or 'balakovo', 'olya'
    deepsea: {
        masters: {
            ports: [],
            routes: [],
            vessels: [],
            cargoTypes: []
        },
        planning: {
            commitments: [],
            railCargo: [],
            movements: [],
            voyageLegs: []
        },
        computed: {
            voyages: [],
            voyageTemplates: [],
            scenarios: [],
            schedule: null,
            ganttData: [],
            routeLegs: []
        }
    },
    // balakovo, olya have same structure
    filters: { ... },
    voyageBuilder: { ... },
    portStocks: { ... },
    salesPlan: { ... }
}
```

## CSV Format Specifications

### Ports.csv

```
port_id;port_name;country;basin;unlocode;latitude;longitude;can_handle_liquid;can_handle_dry;avg_loading_rate_tph;avg_discharge_rate_tph;typical_waiting_hours;congestion_level
P001;Houston;USA;Gulf of Mexico;USHOU;29.7604;-95.3698;yes;yes;400;500;12;Low
```

### Routes.csv

```
route_id;route_name;port_start_id;port_end_id;distance_nm;typical_duration_days;canal_transit;canal_name;eca_pct;waypoints;typical_weather_risk
R001;Houston-Rotterdam;Houston;Rotterdam;4800;14.5;no;;25;Gibraltar;Low
```

### Vessels.csv

```
vessel_id;vessel_name;vessel_class;type;dwt_mt;capacity_mt;speed_kn;tc_daily_hire_usd;contract_type
V001;Atlantic Star;Handysize;Dry Bulk;35000;33000;14.0;15000;Time Charter
```

### CargoCommitments.csv

```
commitment_id;product_name;qty_mt;load_port_id;discharge_port_id;load_date_window_start;load_date_window_end;delivery_deadline;status
C001;Grain;50000;Houston;Rotterdam;2025-01-15;2025-01-20;2025-02-15;Pending
```

### rail_cargo.csv

```
rail_shipment_id;origin_station;destination_port;product_type;qty_mt;shipment_date;arrival_date
RC001;Balakovo Plant;Olya;Fertilizer;2500;2025-01-10;2025-01-12
```

## API Reference

### Key Functions

#### Data Management

- [`loadFromLocalStorage()`](vessel_scheduler_enhanced.js:2066): Load persisted state
- [`saveToLocalStorage()`](vessel_scheduler_enhanced.js:2048): Save current state
- [`getCurrentData()`](vessel_scheduler_enhanced.js:87): Get active module data

#### Filtering

- [`applyFilters()`](vessel_scheduler_enhanced.js:380): Apply global filters
- [`resetFilters()`](vessel_scheduler_enhanced.js:390): Clear all filters
- [`applyFiltersToData(data)`](vessel_scheduler_enhanced.js:410): Filter dataset

#### Import

- [`handleFileUpload(input, type)`](vessel_scheduler_enhanced.js:1462): Handle file selection
- [`parseCSV(content, type)`](vessel_scheduler_enhanced.js:1530): Parse CSV content

#### Voyage Building

- [`addVoyageLeg()`](vessel_scheduler_enhanced.js:1180): Add leg to builder
- [`validateVoyage()`](vessel_scheduler_enhanced.js:1206): Validate leg sequence
- [`saveVoyageTemplate()`](vessel_scheduler_enhanced.js:1259): Save as template

#### Auto-Scheduling

- [`generateAutoSchedule()`](vessel_scheduler_enhanced.js:1106): Generate from commitments
- [`buildRouteLegCatalog()`](vessel_scheduler_enhanced.js:1088): Build route catalog

#### Analytics

- [`runComparison()`](vessel_scheduler_enhanced.js:1275): Compare voyages/scenarios
- [`calculatePortStock()`](vessel_scheduler_enhanced.js:1333): Calculate port stocks
- [`calculateSalesPlan()`](vessel_scheduler_enhanced.js:1407): Calculate sales plan

#### Visualization

- [`renderNetwork()`](vessel_scheduler_enhanced.js:1450): Render network graph
- [`generateSchedule()`](vessel_scheduler_enhanced.js:935): Generate Gantt schedule

## Browser Compatibility

- **Recommended**: Chrome 90+, Firefox 88+, Edge 90+
- **Required Features**: ES6, localStorage, FileReader API, vis-network support
- **Offline Capable**: Yes (after initial load, uses localStorage)

## Performance Considerations

- **LocalStorage Limit**: ~5-10 MB per origin
- **Large Datasets**: For >1000 vessels or >5000 commitments, consider backend integration
- **Network Graph**: Performance degrades with >500 nodes
- **Auto-Save**: Runs every 30 seconds; disable for large datasets

## Troubleshooting

### Data Not Persisting

- Check browser localStorage quota
- Verify that JavaScript is enabled
- Check browser console for errors

### Import Fails

- Verify CSV uses `;` delimiter
- Check for UTF-8 encoding (BOM optional)
- Ensure required columns are present
- Validate date formats (YYYY-MM-DD)

### Network Graph Not Rendering

- Ensure vis-network CDN is accessible
- Check that ports/routes are imported
- Verify browser console for errors

### Gantt Chart Empty

- Import vessels and commitments first
- Click "Generate Schedule"
- Check that vessels have status 'Active'

## Future Enhancements

- [ ] Backend API integration (REST/GraphQL)
- [ ] Real-time collaboration (WebSocket)
- [ ] Advanced financial modeling (bunker optimization, freight derivatives)
- [ ] Weather routing integration
- [ ] AIS vessel tracking
- [ ] PDF report generation
- [ ] Mobile-responsive UI
- [ ] Multi-language support
- [x] Role-based access control
- [x] Centralized Configuration & Logging
- [x] Security Hardening (Path validation, Backups)
- [x] Comprehensive Error Handling

## Backend Architecture (New in v3.1)

### 1. Configuration System

- Centralized configuration via `config.yaml`
- Typed interface via `modules/config.py`
- Supports environment-specific settings for logging, paths, and algorithm parameters

### 2. Logging System

- Standardized logging via `modules/logger.py`
- Rotating file logs (app.log, errors.log)
- Console output for development
- Configurable log levels

### 3. Security Enhancements

- **Path Validation**: `modules/security_utils.py` prevents directory traversal attacks
- **File Backups**: Automatic backups before overwriting critical files
- **RBAC**: Role-Based Access Control for API endpoints

### 4. Error Handling

- Centralized exception handling via `modules/error_handling.py`
- Standardized JSON error responses
- Custom exception hierarchy (`AppError`, `ValidationError`, `NotFoundError`, etc.)

## Technical Stack

- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Charting**: Custom Gantt implementation
- **Network Viz**: vis-network 9.1.2
- **Excel Export**: SheetJS (xlsx) 0.20.1
- **Storage**: Browser localStorage
- **Architecture**: Single-page application (SPA)

## License

© 2025 Maritime Logistics Team. All rights reserved.

## Version History

### v3.0.0  - Enhanced Edition

-  Unified global filters across all modules
-  Multi-module architecture (Deep Sea, Balakovo, Olya)
-  CSV import pipeline with `;` delimiter support
-  localStorage persistence for all data types
-  RouteLeg catalog generator
-  Auto-schedule generator
-  Interactive Voyage Builder
-  Voyage Comparison analytics
-  Port cargo accumulation engine
-  Sales Plan calculator
-  Network visualization with vis-network
-  Enhanced export modules
-  Operation type filters in Schedule tab
-  Operation types legend moved to Schedule

### For contact
Go fuck yourself and don't contact me. 