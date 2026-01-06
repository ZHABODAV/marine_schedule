# Vessel Scheduler Enhanced - Tab Documentation

**File:** [`vessel_scheduler_enhanced.html`](../vessel_scheduler_enhanced.html)
**Version:** 4.0.0 Complete with UI Modules
**Last Updated:** 2025-12-19

This document provides a comprehensive overview of each tab in the vessel scheduling web interface, explaining its purpose, functionality, and backend Python module connections.

---

## Table of Contents

1. [Dashboard (Панель)](#1-dashboard-панель)
2. [Vessels (Суда)](#2-vessels-суда)
3. [Cargo (Грузы)](#3-cargo-грузы)
4. [Routes (Маршруты)](#4-routes-маршрутыy)
5. [Schedule (Расписание)](#5-schedule-расписание)
6. [Voyage Builder](#6-voyage-builder)
7. [Comparison (Сравнение)](#7-comparison-сравнение)
8. [Port Stock (Склады портов)](#8-port-stock-склады-портов)
9. [Sales Plan (План продаж)](#9-sales-plan-план-продаж)
10. [Network (Сеть)](#10-network-сеть)
11. [Alerts](#11-alerts)
12. [Berth Management](#12-berth-management)
13. [Bunker Optimization](#13-bunker-optimization)
14. [Weather](#14-weather)
15. [Vessel Tracking](#15-vessel-tracking)
16. [Scenarios](#16-scenarios)
17. [Templates](#17-templates)
18. [Capacity Planning](#18-capacity-planning)
19. [Reports (Отчеты)](#19-reports-отчеты)

---

## 1. Dashboard (Панель)

### Purpose

Provides a high-level overview of the vessel scheduling system with key performance indicators (KPIs) and real-time statistics.

### Features

- **Active Vessels:** Displays the number of vessels currently in operation
- **Pending Cargo:** Shows cargo awaiting vessel assignment
- **Total Distance:** Cumulative nautical miles across all planned voyages
- **Fleet Utilization:** Percentage showing how effectively the fleet is being used

### How It Works

1. Loads on page initiation
2. Fetches statistics from [`/api/dashboard/stats`](../api_server.py:902)
3. Updates metrics cards with real-time data
4. Auto-refreshes periodically

### Python Module Connections

- **Data Loader:** [`modules/deepsea_loader.py`](../modules/deepsea_loader.py) - DeepSeaLoader class
- **API Endpoint:** [`api_server.py`](../api_server.py:902) - `get_dashboard_stats()`
- **Data Sources:**
  - `input/Vessels.csv` - Vessel fleet information
  - `input/CargoCommitments.csv` - Cargo data
  - `input/Routes.csv` - Route information

### JavaScript Functions

- `updateDashboard()` - Fetches and updates dashboard statistics
- Called on tab activation and periodic refresh

---

## 2. Vessels (Суда)

### Purpose

Manages the vessel fleet database, allowing viewing, adding, editing, and removing vessels from the system.

### Features

- **Vessel List:** Tabular view of all vessels with specifications
- **Add Vessel:** Modal form to add new vessels
- **Edit Vessel:** Modify existing vessel details
- **Vessel Details:**
  - Vessel ID
  - Name
  - Class (vessel type)
  - DWT (Deadweight Tonnage in metric tons)
  - Speed (laden, in knots)
  - Status

### How It Works

1. Fetches vessel data from [`/api/vessels`](../api_server.py:160) (GET)
2. Displays vessels in a sortable table
3. "Add Vessel" button opens modal with input form
4. Form submission sends POST request to [`/api/vessels`](../api_server.py:160)
5. Updates `input/Vessels.csv` file on server

### Python Module Connections

- **Data Loader:** [`modules/deepsea_loader.py`](../modules/deepsea_loader.py) - DeepSeaLoader.load()
- **Data Structure:** [`modules/deepsea_data.py`](../modules/deepsea_data.py) - Vessel class
- **API Endpoint:** [`api_server.py`](../api_server.py:160) - `handle_vessels()`
- **CSV File:** `input/Vessels.csv`

### JavaScript Functions

- `loadVessels()` - Fetches vessel list from API
- `addVessel()` - Opens modal for adding new vessel
- `editVessel(vesselId)` - Opens modal with pre-filled vessel data
- `saveVessel()` - Submits vessel data to API

---

## 3. Cargo (Грузы)

### Purpose

Manages cargo commitments and shipment requirements, tracking what needs to be transported and when.

### Features

- **Cargo List:** All cargo commitments with details
- **Add Cargo:** Create new cargo shipment requirements
- **Cargo Information:**
  - Cargo ID
  - Commodity (product type)
  - Quantity (metric tons)
  - Load Port
  - Discharge Port
  - Laycan Start (earliest loading date)
  - Laycan End (latest loading date)
  - Status (Pending/Assigned/Completed)

### How It Works

1. Fetches cargo data from [`/api/cargo`](../api_server.py:210) (GET)
2. Displays in tabular format
3. "Add Cargo" opens modal form
4. Form sends POST request to [`/api/cargo`](../api_server.py:210)
5. Updates `input/CargoCommitments.csv`

### Python Module Connections

- **Data Loader:** [`modules/deepsea_loader.py`](../modules/deepsea_loader.py) - DeepSeaLoader.load()
- **Data Structure:** [`modules/deepsea_data.py`](../modules/deepsea_data.py) - VoyagePlan class
- **API Endpoint:** [`api_server.py`](../api_server.py:210) - `handle_cargo()`
- **CSV File:** `input/CargoCommitments.csv`

### JavaScript Functions

- `loadCargo()` - Fetches cargo list
- `addCargo()` - Opens cargo creation modal
- `saveCargo()` - Submits cargo data

---

## 4. Routes (Маршruты)

### Purpose

Defines and manages maritime routes between ports, including distances and canal transits.

### Features

- **Route Database:** List of all defined routes
- **Add Route:** Create new port-to-port routes
- **Route Details:**
  - Origin Port
  - Destination Port
  - Distance (nautical miles)
  - Canal Information (Suez, Panama, etc.)

### How It Works

1. Displays routes from `input/Routes.csv`
2. "Add Route" opens modal
3. User inputs route details
4. Data saved via API or direct CSV update

### Python Module Connections

- **Data Loader:** [`modules/deepsea_loader.py`](../modules/deepsea_loader.py) - Loads route data
- **Data Structure:** [`modules/deepsea_data.py`](../modules/deepsea_data.py) - RouteLeg class
- **CSV File:** `input/Routes.csv`
- **Port Data:** `input/Ports.csv`

### JavaScript Functions

- `loadRoutes()` - Fetches route data
- `addRoute()` - Opens route creation modal
- `saveRoute()` - Submits route data

---

## 5. Schedule (Расписание)

### Purpose

Generates and displays vessel schedules as Gantt charts, showing vessel activities over time.

### Features

- **Module Selection:** Switch between DeepSea, Balakovo, Olya
- **Operation Type Filters:** Filter by loading, discharge, transit, ballast, canal, bunker, waiting
- **Gantt Chart:** Visual timeline of vessel operations
- **Operation Legend:** Color-coded operation types

### How It Works

1. User selects module (DeepSea/Balakovo/Olya)
2. Clicks "Generate Schedule"
3. Sends POST to [`/api/calculate`](../api_server.py:478) with module type
4. Receives calculated voyage legs
5. Fetches Gantt data from [`/api/gantt-data`](../api_server.py:640)
6. Renders interactive Gantt chart

### Python Module Connections

#### DeepSea Module

- **Loader:** [`modules/deepsea_loader.py`](../modules/deepsea_loader.py) - DeepSeaLoader
- **Calculator:** [`modules/deepsea_calculator.py`](../modules/deepsea_calculator.py) - DeepSeaCalculator
- **Gantt:** [`modules/deepsea_gantt_excel.py`](../modules/deepsea_gantt_excel.py) - DeepSeaGanttExcel
- **Data:** [`modules/deepsea_data.py`](../modules/deepsea_data.py)

#### Olya Module

- **Loader:** [`modules/olya_loader.py`](../modules/olya_loader.py) - OlyaLoader
- **Coordinator:** [`modules/olya_coordinator.py`](../modules/olya_coordinator.py) - OlyaCoordinator
- **Gantt:** [`modules/olya_gantt_excel.py`](../modules/olya_gantt_excel.py) - OlyaGanttExcel
- **Data:** [`modules/olya_data.py`](../modules/olya_data.py)

#### Balakovo Module

- **Loader:** [`modules/balakovo_loader.py`](../modules/balakovo_loader.py) - BalakovoLoader
- **Planner:** [`modules/balakovo_planner.py`](../modules/balakovo_planner.py) - BalakovoPlanner
- **Gantt:** [`modules/balakovo_gantt.py`](../modules/balakovo_gantt.py) - BalakovoGanttExcel
- **Data:** [`modules/balakovo_data.py`](../modules/balakovo_data.py)

### JavaScript Functions

- `generateSchedule()` - Initiates schedule calculation
- `renderGanttChart(data)` - Renders Gantt visualization
- `applyOperationFilters()` - Filters displayed operations

---

## 6. Voyage Builder

### Purpose

Interactive tool for creating and validating multi-leg voyages with custom route planning.

### Features

- **Leg Builder:** Add multiple voyage legs
- **Leg Configuration:**
  - Port of call
  - Operation type (loading/discharge/transit)
  - Dates
  - Cargo information
- **Validation:** Checks voyage feasibility
- **Template Saving:** Save voyage as reusable template

### How It Works

1. User clicks "Add Leg" to add voyage segments
2. Fills in port, operation, dates for each leg
3. Clicks "Validate" to check voyage logic
4. Can save as template for future use
5. Data structured as sequential voyage legs

### Python Module Connections

- **Voyage Calculator:** [`modules/voyage_calculator.py`](../modules/voyage_calculator.py) - Voyage calculations
- **Distance Data:** Uses route database for distance calculations
- **Validation:** Checks dates, port sequences, cargo compatibility

### JavaScript Functions

- `addVoyageLeg()` - Adds new leg to builder
- `validateVoyage()` - Validates entire voyage
- `saveVoyageTemplate()` - Saves voyage as template
- `removeLeg(index)` - Removes a leg from builder

---

## 7. Comparison (Сравнение)

### Purpose

Compares multiple voyage scenarios or schedules side-by-side to support decision-making.

### Features

- **Scenario Selection:** Choose multiple scenarios to compare
- **Comparison Metrics:**
  - Total duration
  - Total distance
  - Fuel consumption
  - Estimated costs
  - Revenue projections
- **Visual Comparison:** Side-by-side metric display

### How It Works

1. User selects 2+ scenarios/voyages to compare
2. Clicks "Compare Selected"
3. System fetches calculated data for each scenario
4. Displays comparison grid with metrics
5. Highlights differences and optimal choices

### Python Module Connections

- **Scenario Data:** [`modules/deepsea_scenarios.py`](../modules/deepsea_scenarios.py) - Scenario management
- **Calculator:** Uses voyage calculators for metrics
- **Financial Analysis:** TCE, bunker costs, profit calculations

### JavaScript Functions

- `runComparison()` - Initiates comparison
- `renderComparisonResults(data)` - Displays comparison grid
- `highlightOptimal()` - Highlights best options

---

## 8. Port Stock (Склады портов)

### Purpose

Tracks cargo accumulation at ports, balancing rail inflows and vessel outflows.

### Features

- **Port Selection:** Choose port to analyze
- **Stock Timeline:** Daily cargo levels over time
- **Inflow/Outflow:** Rail arrivals vs vessel loadings
- **Capacity Warnings:** Alerts when approaching storage limits

### How It Works

1. User selects port from dropdown
2. Clicks "Calculate"
3. System analyzes:
   - Rail cargo arrivals (from `input/rail_cargo.csv`)
   - Vessel loading schedules
   - Daily stock accumulation/depletion
4. Renders timeline chart

### Python Module Connections

- **Data Sources:**
  - `input/rail_cargo.csv` - Rail input data
  - `input/cargo_movements.csv` - Vessel movements
- **Calculation Logic:** Custom stock balance calculations
- **No specific module** - Uses raw data analysis

### JavaScript Functions

- `calculatePortStock()` - Initiates stock calculation
- `updatePortStock()` - Updates display for selected port
- `renderStockTimeline(data)` - Renders timeline chart

---

## 9. Sales Plan (План продаж)

### Purpose

Calculates required shipping capacity to meet sales commitments and suggests voyage plans.

### Features

- **Required Shipments:** Total tonnage to ship
- **Suggested Trips:** Number of voyages needed
- **Capacity Gap:** Shortfall or excess capacity
- **Vessel Allocation:** Suggested vessel assignments

### How It Works

1. Reads cargo commitments from database
2. Calculates total tonnage requirements
3. Analyzes available vessel capacity
4. Suggests optimal number of trips
5. Identifies capacity gaps

### Python Module Connections

- **Data:** Cargo commitments, vessel fleet
- **Calculation:** Capacity planning algorithms
- **Could integrate with:** [`modules/balakovo_planner.py`](../modules/balakovo_planner.py) for optimization

### JavaScript Functions

- `calculateSalesPlan()` - Runs sales plan analysis
- `renderSalesPlanDetails(data)` - Displays results

---

## 10. Network (Сеть)

### Purpose

Visualizes the entire logistics network as an interactive graph showing ports, rail connections, and sea routes.

### Features

- **Network Graph:** Interactive visualization using vis-network
- **Node Types:**
  - Ports (size based on throughput)
  - Rail terminals
  - Transshipment points
- **Edge Types:**
  - Rail connections
  - Sea routes
  - Highlighted active voyages

### How It Works

1. Loads port, route, and rail data
2. Builds network graph structure
3. Uses vis-network library for rendering
4. Allows zooming, panning, node selection
5. Can export snapshot

### Python Module Connections

- **Data Sources:**
  - `input/Ports.csv`
  - `input/Routes.csv`
  - `input/rail_cargo.csv`
- **No dedicated module** - Uses data aggregation

### JavaScript Functions

- `renderNetwork()` - Generates network visualization
- `exportNetworkSnapshot()` - Exports network as image
- Uses **vis-network.js** library

---

## 11. Alerts

### Purpose

Centralized alert dashboard for monitoring critical events, conflicts, and warnings across the scheduling system.

### Features

- **Real-time Alerts:** Live notifications
- **Severity Levels:** Critical, High, Medium, Low
- **Alert Types:**
  - Berth conflicts
  - Weather warnings
  - Delays
  - Capacity issues
- **Alert Management:** Acknowledge and resolve alerts
- **Auto-refresh:** Updates every 30 seconds

### How It Works

1. AlertsDashboard class initializes
2. Fetches alerts from [`/api/alerts`](../api_extensions.py:18)
3. Displays in severity-coded cards
4. User can acknowledge or resolve alerts
5. Sends updates via POST requests

### Python Module Connections

- **API:** [`api_extensions.py`](../api_extensions.py:18) - `get_alerts()`
- **Alert Module:** [`modules/alerts.py`](../modules/alerts.py) - Alert generation logic
- **Data Sources:** System-wide monitoring (berths, weather, schedules)

### JavaScript Class

- **AlertsDashboard** (lines 2180-2443 in HTML)
- Methods:
  - `init()` - Initializes dashboard
  - `loadAlerts()` - Fetches alert data
  - `acknowledgeAlert(id)` - Acknowledges alert
  - `resolveAlert(id)` - Resolves alert
  - `playAlertSound()` - Audio notification

---

## 12. Berth Management

### Purpose

Manages berth allocation, constraints, utilization, and conflicts for efficient port operations.

### Features

- **Multiple Views:**
  - Dashboard: Overview and statistics
  - Constraints: Berth limitations
  - Capacity: Utilization planning
  - Conflicts: Scheduling conflicts
- **Berth Information:**
  - Max length, draft, beam
  - Current occupancy
  - Availability timeline
- **Conflict Resolution:** Auto-resolve conflicts

### How It Works

1. BerthManagement class loads berth data
2. Fetches from [`/api/berths`](../api_extensions.py:82)
3. Displays berth grid with status
4. Tracks utilization over time
5. Identifies and resolves conflicts

### Python Module Connections

- **API:** [`api_extensions.py`](../api_extensions.py:82) - `get_berths()`
- **Berth Module:** [`modules/berth_constraints.py`](../modules/berth_constraints.py) - Constraint checking
- **Utilization:** [`modules/berth_utilization.py`](../modules/berth_utilization.py) - Capacity tracking
- **Data Sources:**
  - `input/Berths.csv`
  - Vessel schedules

### JavaScript Class

- **BerthManagement** (lines 2449-2633)
- Views: Dashboard, Constraints, Capacity, Conflicts
- Methods:
  - `loadData()` - Fetches berth data
  - `switchView(view)` - Changes view
  - `renderBerthGrid()` - Displays berths
  - `calculateAverageUtilization()` - Calculates metrics

---

## 13. Bunker Optimization

### Purpose

Optimizes fuel procurement by comparing bunker prices across ports and calculating voyage fuel costs.

### Features

- **Cost Calculator:**
  - Voyage distance input
  - Vessel speed
  - Consumption rate
  - Fuel type selection
- **Bunker Ports:** List of ports with fuel prices
- **Fuel Types:** VLSFO, HFO, MGO
- **Cost Estimation:** Total fuel cost calculation

### How It Works

1. User inputs voyage parameters
2. Selects fuel type
3. System calculates:
   - Voyage duration
   - Fuel consumption
   - Total cost based on current prices
4. Displays recommended bunker ports

### Python Module Connections

- **API:** [`api_extensions.py`](../api_extensions.py:232) - `get_bunker_data()`
- **Bunker Module:** [`modules/bunker_optimizer.py`](../modules/bunker_optimizer.py) - Optimization logic
- **Price Data:** External or configured bunker prices

### JavaScript Class

- **BunkerOptimization** (lines 2639-2747)
- Methods:
  - `calculateBunkerCost()` - Calculates fuel costs
  - `renderBunkerPorts()` - Displays port prices

---

## 14. Weather

### Purpose

Integrates weather data into voyage planning, providing warnings and forecasts for maritime routes.

### Features

- **Active Warnings:** Storm, wind, fog alerts
- **5-Day Forecast:** Temperature, wind, wave conditions
- **Route Risk Assessment:** Weather impact on planned routes
- **Gantt Overlay:** Weather warnings overlaid on schedule

### How It Works

1. Fetches weather data from [`/api/weather`](../api_extensions.py:260)
2. Displays active warnings with severity
3. Shows 5-day forecast grid
4. Can overlay weather warnings on Gantt chart
5. Updates periodically

### Python Module Connections

- **API:** [`api_extensions.py`](../api_extensions.py:260) - `get_weather_data()`
- **Weather Data:** `input/WeatherWarnings.csv`
- **Integration:** Can overlay on schedule visualization

### JavaScript Class

- **WeatherIntegration** (lines 2753-2880)
- Methods:
  - `loadWeatherData()` - Fetches warnings and forecasts
  - `renderWarnings()` - Displays active warnings
  - `overlayOnGantt()` - Adds weather to Gantt chart
  - `getWeatherIcon(type)` - Returns weather icons

---

## 15. Vessel Tracking

### Purpose

Real-time vessel position tracking with interactive map visualization.

### Features

- **Live Map:** Interactive Leaflet.js map
- **Vessel Positions:** Current lat/long coordinates
- **Vessel Status:** Underway, at port, anchored
- **Vessel Details:**
  - Speed
  - Course
  - Destination
  - ETA
- **Search:** Filter vessels by name

### How It Works

1. VesselTracking class initializes Leaflet map
2. Fetches positions from [`/api/vessels/tracking`](../api_extensions.py:295)
3. Updates map markers with vessel locations
4. Displays vessel info on marker click
5. Auto-updates every 60 seconds

### Python Module Connections

- **API:** [`api_extensions.py`](../api_extensions.py:295) - `get_vessel_tracking()`
- **Position Data:** `input/VesselPositions.csv`
- **Live Integration:** Could integrate with AIS data

### JavaScript Class

- **VesselTracking** (lines 2886-3049)
- Uses **Leaflet.js** for mapping
- Methods:
  - `initMap()` - Initializes map
  - `loadVesselData()` - Fetches vessel positions
  - `updateMap()` - Updates markers
  - `renderVesselTable()` - Displays vessel list

---

## 16. Scenarios

### Purpose

Manages multiple planning scenarios for "what-if" analysis and scenario comparison.

### Features

- **Scenario List:** All saved scenarios
- **Create Scenario:** Save current planning state
- **Load Scenario:** Switch to different scenario
- **Base Scenarios:** Create variations from existing scenarios
- **Scenario Comparison:** Compare multiple scenarios

### How It Works

1. User creates new scenario or loads existing
2. Scenario stores:
   - Vessel assignments
   - Cargo allocations
   - Route selections
   - Timing decisions
3. Can switch between scenarios
4. Compare scenarios side-by-side

### Python Module Connections

- **API:** [`api_extensions.py`](../api_extensions.py:337) - `handle_scenarios()`
- **Scenario Module:** [`modules/deepsea_scenarios.py`](../modules/deepsea_scenarios.py) - Scenario management
- **Storage:** JSON or database storage

### JavaScript Class

- **ScenarioManagement** (lines 3121-3323)
- Methods:
  - `loadScenarios()` - Fetches all scenarios
  - `saveScenario()` - Creates new scenario
  - `loadScenario(id)` - Activates scenario
  - `deleteScenario(id)` - Removes scenario
  - `compareScenarios()` - Compares scenarios

---

## 17. Templates

### Purpose

Manages reusable voyage templates for common routes and vessel assignments.

### Features

- **Template Library:** Predefined voyage patterns
- **Template Categories:** Regional, Intercontinental, etc.
- **Template Details:**
  - Name and description
  - Port sequence
  - Estimated duration
  - Category
- **Apply Template:** Quickly create voyage from template
- **Edit/Delete:** Manage templates

### How It Works

1. Displays template library
2. User can filter by category
3. "Apply Template" populates Voyage Builder
4. Can edit existing templates
5. Create new templates from successful voyages

### Python Module Connections

- **API:** [`api_extensions.py`](../api_extensions.py:392) - `handle_voyage_templates()`
- **Template Storage:** Database or JSON files
- **Integration:** Works with Voyage Builder

### JavaScript Class

- **VoyageTemplates** (lines 3329-3597)
- Methods:
  - `loadTemplates()` - Fetches templates
  - `applyTemplate(id)` - Applies template to builder
  - `editTemplate(id)` - Opens editor
  - `deleteTemplate(id)` - Removes template
  - `filterByCategory(cat)` - Filters display

---

## 18. Capacity Planning

### Purpose

Analyzes berth capacity vs demand over time, forecasting utilization and identifying bottlenecks.

### Features

- **Time Range Selection:** 7, 14, 30, 90 days
- **Capacity vs Demand Chart:** Visual comparison
- **Utilization Forecast:** Predicted capacity usage
- **Recommendations:** Optimization suggestions
- **Peak Day Analysis:** Identifies highest demand periods
- **Overbooking Alerts:** Days exceeding capacity

### How It Works

1. User selects time range
2. Fetches capacity data from [`/api/capacity`](../api_extensions.py:442)
3. Compares berth capacity to vessel demand
4. Identifies overbooking days
5. Generates optimization recommendations
6. Can run auto-optimization

### Python Module Connections

- **API:** [`api_extensions.py`](../api_extensions.py:442) - `get_capacity_data()`
- **Planner:** [`modules/balakovo_planner.py`](../modules/balakovo_planner.py) - Capacity planning
- **Berth Data:** Uses berth schedules and constraints

### JavaScript Class

- **BerthCapacityPlanning** (lines 3603-3777)
- Methods:
  - `loadCapacityData()` - Fetches capacity data
  - `renderCapacityChart()` - Displays chart
  - `optimizeAllocation()` - Runs optimization
  - `getPeakDay()` - Identifies peak demand
  - `getOverbookingDays()` - Counts exceeded days

---

## 19. Reports (Отчеты)

### Purpose

Central hub for generating and exporting various reports and visualizations.

### Features

#### Available Reports

1. **Gantt Chart:** Visual schedule to Excel
2. **Fleet Overview:** Comprehensive fleet report
3. **Voyage Summary:** Detailed voyage statistics
4. **Scenario Comparison:** Multi-scenario analysis
5. **Financial Analysis (DeepSea):** TCE, profit, bunker costs
6. **Olya Coordination:** Barge-vessel coordination schedule
7. **Voyage Comparison:** KPI comparison across voyages
8. **Port Stock Timeline:** Historical stock levels

#### Data Import

- Upload CSV files for:
  - Ports
  - Routes
  - Vessels
  - Cargo
  - Commitments
  - Rail cargo
  - Movements
  - Voyage legs

### How It Works

#### Export Process

1. User selects report type
2. Clicks export button
3. System generates Excel file using appropriate module
4. File downloads to user's computer

#### Import Process

1. User selects file type
2. Uploads CSV file
3. System validates format
4. Updates corresponding `input/*.csv` file

### Python Module Connections

#### Export Modules

- **Gantt:**
  - [`modules/deepsea_gantt_excel.py`](../modules/deepsea_gantt_excel.py)
  - [`modules/olya_gantt_excel.py`](../modules/olya_gantt_excel.py)
  - [`modules/balakovo_gantt.py`](../modules/balakovo_gantt.py)
- **Excel Export:** [`modules/excel_exporter.py`](../modules/excel_exporter.py)
- **PDF Export:** Could use [`modules/pdf_reporter.py`](../modules/pdf_reporter.py)

#### API Endpoints

- `/api/export/gantt` - Gantt chart export
- `/api/export/fleet-overview` - Fleet overview
- `/api/export/voyage-summary` - Voyage summary
- `/api/upload/<type>` - CSV file upload

### JavaScript Functions

- `exportGantt()` - Exports Gantt chart
- `exportFleetOverview()` - Exports fleet data
- `exportVoyageSummary()` - Exports voyage details
- `handleFileUpload(file, type)` - Handles CSV uploads

---

## Global Features

### Module Selector

Located in the header, allows switching between:

- **DeepSea** - Ocean-going vessels, long voyages
- **Balakovo** - Terminal operations, berth scheduling
- **Olya** - River-sea operations, transshipment

Switching modules affects:

- Schedule generation
- Available data
- Report types
- Gantt chart rendering

### Global Filters

Available across most tabs:

- **Module:** Filter by DeepSea/Balakovo/Olya
- **Date Range:** Start and end dates
- **Product:** Filter by cargo type
- **Port:** Filter by loading/discharge port
- **Vessel:** Filter by specific vessel

### Auto-Refresh

Several tabs auto-refresh:

- **Alerts:** Every 30 seconds
- **Vessel Tracking:** Every 60 seconds
- **Dashboard:** Every 5 minutes

---

## Technical Architecture

### Frontend Technologies

- **HTML5** - Structure
- **CSS3** - Dark theme styling with CSS variables
- **JavaScript (ES6)** - Interactive functionality
- **Libraries:**
  - **SheetJS (xlsx)** - Excel file handling
  - **vis-network** - Network graph visualization
  - **Leaflet.js** - Map rendering
  - **html2pdf.js** - PDF export

### Backend Integration

- **Flask REST API** - Python backend ([`api_server.py`](../api_server.py))
- **API Extensions** - UI module endpoints ([`api_extensions.py`](../api_extensions.py))
- **Data Format:** JSON for API communication
- **File Format:** CSV (semicolon-separated) for data storage

### Data Flow

1. **User Action** → JavaScript event handler
2. **API Request** → Fetch data from Flask endpoint
3. **Python Processing** → Module calculates/loads data
4. **JSON Response** → Returns structured data
5. **UI Update** → JavaScript renders visualization

### Module Pattern

Each advanced tab uses a JavaScript class:

```javascript
class ModuleName {
    constructor(config) { /* Setup */ }
    async init() { /* Initialize */ }
    render() { /* Build HTML */ }
    async loadData() { /* Fetch from API */ }
    destroy() { /* Cleanup */ }
}
```

---

## API Endpoint Reference

### Core Endpoints

- `GET /api/health` - Health check
- `GET /api/vessels` - Get vessels
- `POST /api/vessels` - Update vessels
- `GET /api/cargo` - Get cargo
- `POST /api/cargo` - Update cargo
- `POST /api/calculate` - Calculate schedule
- `GET /api/gantt-data` - Get Gantt data
- `POST /api/export/excel` - Export Excel
- `GET /api/dashboard/stats` - Dashboard stats

### UI Module Endpoints

- `GET /api/alerts` - Get alerts
- `GET /api/berths` - Get berth data
- `GET /api/bunker` - Get bunker prices
- `GET /api/weather` - Get weather data
- `GET /api/vessels/tracking` - Get positions
- `GET /api/scenarios` - Get scenarios
- `GET /api/voyage-templates` - Get templates
- `GET /api/capacity` - Get capacity data

*Full API documentation: See [`api_server.py`](../api_server.py) and [`api_extensions.py`](../api_extensions.py)*

---

## File Dependencies

### Input Files (CSV)

- `input/Vessels.csv` - Vessel fleet
- `input/Cargo.csv` - Cargo types
- `input/CargoCommitments.csv` - Shipment requirements
- `input/Ports.csv` - Port database
- `input/Routes.csv` - Route distances
- `input/Berths.csv` - Berth specifications
- `input/rail_cargo.csv` - Rail inputs
- `input/cargo_movements.csv` - Movement tracking
- `input/voyage_legs.csv` - Voyage leg details
- `input/VesselPositions.csv` - Vessel positions
- `input/WeatherWarnings.csv` - Weather data

### Python Modules Used

See [`modules/`](../modules/) directory for all backend modules.

---

## Browser Compatibility

- **Chrome/Edge:** Fully supported
- **Firefox:** Fully supported
- **Safari:** Supported (test Leaflet.js)
- **Mobile:** Responsive design, limited features

---

## Version History

- **v4.0.0** - Complete UI modules integration
- **v3.0.0** - Added Voyage Builder, Comparison, Network
- **v2.0.0** - Multi-module support (DeepSea/Olya/Balakovo)
- **v1.0.0** - Initial release

---

## Related Documentation

- [API Reference](API_REFERENCE.md)
- [Quick Start Guide](QUICK_START.md)
- [Web Interfaces Overview](WEB_INTERFACES.md)
- [Berth Constraints](BERTH_CONSTRAINTS.md)

---

**Last Updated:** 2025-12-18  
**Document Version:** 1.0
