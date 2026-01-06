# Vessel Scheduler System

A comprehensive vessel scheduling and optimization system for maritime cargo operations, supporting deep-sea, river-sea (Olya), and terminal (Balakovo) operations with advanced features for berth management, bunker optimization, and real-time collaboration.

**Version**: 2.0.0  
**Last Updated**: 2025-12-18  
**Python Version**: 3.8+

---

##  Quick Start

### Web Interface (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Flask API server
python api_server.py

# 3. Open browser and navigate to
# http://localhost:5000
```

**Available Web Interfaces:**

- **[`vessel_scheduler_enhanced.html`](vessel_scheduler_enhanced.html)** - Complete vessel scheduling system with multi-module support
- **[`voyage_planner.html`](voyage_planner.html)** - Standalone voyage calculator (English)
- **[`voyage_planner_ru.html`](voyage_planner_ru.html)** - Standalone voyage calculator (Russian)

### Command Line Interface

```bash
# Generate CSV templates with sample data
python generate_templates.py

# Run Deep Sea scheduling
python main_deepsea.py

# Run Olya (river-sea) scheduling
python main_olya.py

# Run Balakovo terminal scheduling
python main_balakovo.py

# Run test suite (59 tests)
pytest tests/ -v
```

For detailed setup instructions, see [**Quick Start Guide**](docs/QUICK_START.md).

---

##  Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Web Interfaces](#web-interfaces)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Contributing](#contributing)

---

## Overview

The Vessel Scheduler System is an enterprise-grade maritime logistics platform designed for comprehensive vessel scheduling, route optimization, and berth management. It integrates three major operational modules with advanced features for financial optimization, security, and real-time collaboration.

### Supported Operations

- **Deep Sea Operations**: International ocean-going vessels with complex routing, canal transits, and laycan management
- **River-Sea Operations (Olya)**: Balakovo to Olya transshipment coordination for barges and river-sea vessels
- **Terminal Operations (Balakovo)**: Loading operations scheduling, berth capacity management, and constraint handling

---

##  Key Features

### Core Capabilities

 **Automated Voyage Calculation**

- Port-to-port distance calculation
- Speed-based transit time estimation
- Loading/unloading time calculations
- Canal transit handling (Suez, Panama, etc.)
- Weather margin considerations

 **Advanced Berth Management**

- Multi-berth coordination and scheduling
- Physical constraint validation (LOA, beam, draft)
- Time window restrictions
- Concurrent operations management
- Cargo segregation rules
- Priority-based allocation
- See [**Berth Constraints Documentation**](docs/BERTH_CONSTRAINTS.md)

 **Gantt Chart Visualization**

- Monthly and fleet overview charts
- Color-coded operation types
- Utilization statistics
- Excel export with professional formatting
- Interactive web-based visualization

 **Scenario Management**

- Compare different fleet compositions
- Evaluate routing alternatives
- Analyze capacity changes
- What-if scenario analysis

 **Bunker Optimization** 

- Price-based fuel procurement optimization
- Route-based bunker planning
- Speed optimization (eco-speed recommendations)
- Multi-fuel type support (VLSFO, MGO, LSMGO, HFO, LNG)
- ECA compliance
- See [**Phase 2 Enhancements**](docs/PHASE2_ENHANCEMENTS.md)

 **PDF Report Generation** 

- Professional vessel schedule reports
- Voyage summary with financial analysis
- Fleet overview with utilization metrics
- Berth utilization reports
- Customizable multi-section reports

 **Role-Based Access Control (RBAC)** 

- User authentication and authorization
- Fine-grained permissions system
- Predefined roles (Admin, Ops Manager, Scheduler, etc.)
- Comprehensive audit logging

 **Real-Time Collaboration** 

- WebSocket-based real-time updates
- Multi-user schedule editing
- User presence tracking
- Room-based collaboration

### Operation Types

| Type | Symbol | Description |
|------|--------|-------------|
| **Loading** | L | Cargo loading operations at port |
| **Discharge** | D | Cargo unloading operations at port |
| **Sea Transit** | → | Sea passage with cargo (laden) |
| **Ballast** | ⟶ | Sea passage without cargo |
| **Canal** | C | Canal transit (Suez, Panama, etc.) |
| **Bunker** | B | Fuel bunkering operations |
| **Waiting** | W | Port waiting/queue time |

---

##  System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Interface Layer                      │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ Vessel         │  │ Voyage         │  │ Enhanced       │ │
│  │ Scheduler      │  │ Planner        │  │ Scheduler      │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     REST API Layer (Flask)                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Vessels    │  │ Voyages    │  │ Schedule   │            │
│  │ Cargo      │  │ Routes     │  │ Export     │            │
│  │ Reports    │  │ Bunker     │  │ Auth       │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Deep Sea    │  │ Olya        │  │ Balakovo    │         │
│  │ Calculator  │  │ Coordinator │  │ Planner     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Bunker      │  │ PDF         │  │ RBAC        │         │
│  │ Optimizer   │  │ Reporter    │  │ Manager     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐│
│  │ CSV       │  │ Excel     │  │ JSON      │  │ Logs     ││
│  │ Input     │  │ Output    │  │ Config    │  │ Files    ││
│  └───────────┘  └───────────┘  └───────────┘  └──────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

##  Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Modern web browser (Chrome 90+, Firefox 88+, Edge 90+)

### Step 1: Clone or Download

```bash
cd c:/Users/Asus/Documents/project
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages

```
# Core dependencies
openpyxl>=3.0.0          # Excel file manipulation
pandas>=1.3.0            # Data processing
pyyaml>=5.4.0            # Configuration management
flask>=2.0.0             # Web framework

# Phase 2+ enhancements
flask-socketio>=5.3.0    # WebSocket support
reportlab>=4.0.0         # PDF generation
python-socketio>=5.9.0   # WebSocket client

# Optional but recommended
pytest>=7.0.0            # Testing framework
pytest-cov>=3.0.0        # Code coverage
```

### Step 3: Initialize Directory Structure

```bash
# Create necessary directories (auto-created by system)
mkdir -p input output/reports logs data/rbac
```

---

##  Usage

### 1. Web Interface Usage

Start the API server:

```bash
python api_server.py
```

Open browser to <http://localhost:5000> and choose an interface:

- **Vessel Scheduler Enhanced** - Full-featured multi-module system
- **Voyage Planner** - Quick voyage calculations

See [**Web Interfaces Guide**](docs/WEB_INTERFACES.md) for detailed usage.

### 2. Deep Sea Scheduling

```python
from modules.deepsea_loader import DeepSeaLoader
from modules.deepsea_calculator import DeepSeaCalculator
from modules.deepsea_gantt_excel import DeepSeaGanttExcel

# Load data from CSV
loader = DeepSeaLoader()
data = loader.load_all()

# Calculate voyages
calculator = DeepSeaCalculator(data)
calculator.calculate_all_voyages()

# Generate Gantt charts
gantt = DeepSeaGanttExcel(data)
gantt.generate_all_months()
gantt.generate_fleet_overview()
```

**Output**: `output/deepsea/gantt_deepsea_2025_01.xlsx`

### 3. River-Sea (Olya) Scheduling

```python
from modules.olya_loader import OlyaLoader
from modules.olya_coordinator import OlyaCoordinator
from modules.olya_gantt_excel import OlyaGanttExcel

# Load data
loader = OlyaLoader()
data = loader.load_all()

# Coordinate berth operations
coordinator = OlyaCoordinator(data)
coordinator.run_simulation()

# Generate Gantt
gantt = OlyaGanttExcel(data)
gantt.generate_all_months()
```

**Output**: `output/olya/gantt_olya_2025_01.xlsx`

### 4. Balakovo Terminal Planning

```python
from modules.balakovo_loader import BalakovoLoader
from modules.balakovo_planner import BalakovoPlanner

# Load terminal data
loader = BalakovoLoader()
data = loader.load_all()

# Plan berth operations with advanced constraints
planner = BalakovoPlanner(data)
result = planner.plan()

# Check for conflicts
if result.conflicts:
    print(f"Conflicts detected: {len(result.conflicts)}")
```

See [**Berth Constraints Guide**](docs/BERTH_CONSTRAINTS.md) for advanced constraint configuration.

---

##  Web Interfaces

### Vessel Scheduler Enhanced

**File**: [`vessel_scheduler_enhanced.html`](vessel_scheduler_enhanced.html)

**Features**:

- Multi-module support (Deep Sea, Balakovo, Olya)
- Global filtering system
- CSV import/export
- Voyage builder
- Scenario comparison
- Port stock management
- Sales plan calculator
- Network visualization

### Voyage Planner

**Files**: [`voyage_planner.html`](voyage_planner.html), [`voyage_planner_ru.html`](voyage_planner_ru.html)

**Features**:

- Offline autonomous calculator
- Berth constraint management
- Excel template import/export
- Detailed voyage cost analysis

See [**Web Interfaces Documentation**](docs/WEB_INTERFACES.md) for complete guide.

---

##  API Documentation

### REST API Endpoints

The Flask API server provides comprehensive endpoints:

#### Health & Authentication

```
GET  /api/health                    # Health check
POST /api/auth/login                # User login
POST /api/auth/logout               # User logout
GET  /api/auth/me                   # Current user info
```

#### Vessels Management

```
GET  /api/vessels                   # Get all vessels
POST /api/vessels                   # Create vessel
GET  /api/vessels/{id}              # Get specific vessel
PUT  /api/vessels/{id}              # Update vessel
DELETE /api/vessels/{id}            # Delete vessel
```

#### Cargo Management

```
GET  /api/cargo                     # Get all cargo
POST /api/cargo                     # Create cargo
GET  /api/cargo/{id}                # Get specific cargo
PUT  /api/cargo/{id}                # Update cargo
DELETE /api/cargo/{id}              # Delete cargo
```

#### Schedule & Planning

```
POST /api/schedule/generate         # Generate schedule
GET  /api/schedule/{type}           # Get schedule (deepsea/olya/balakovo)
POST /api/voyage/calculate          # Calculate voyage metrics
```

#### Export Functions

```
POST /api/export/gantt              # Export Gantt chart (Excel)
POST /api/export/fleet-overview     # Export fleet overview (Excel)
POST /api/export/voyage-summary     # Export voyage summary (Excel)
POST /api/reports/pdf/vessel-schedule  # Generate vessel schedule PDF
POST /api/reports/pdf/fleet-overview   # Generate fleet overview PDF
```

#### Bunker Optimization

```
POST /api/bunker/optimize           # Optimize bunker plan
GET  /api/bunker/prices             # Get bunker prices
GET  /api/bunker/market-analysis    # Get market analysis
```

#### File Upload

```
POST /api/upload/csv                # Upload CSV files
POST /api/upload/excel              # Upload Excel files
```

#### Statistics & Monitoring

```
GET  /api/dashboard/stats           # Get dashboard statistics
GET  /api/berths/utilization        # Get berth utilization
```

### WebSocket Events

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Listen for events
socket.on('connected', (data) => {
    console.log('Connected:', data.message);
});

socket.on('schedule_changed', (data) => {
    console.log('Schedule updated:', data);
});

// Join schedule room
socket.emit('join_schedule', {schedule_id: 'SCH001'});

// Emit schedule update
socket.emit('schedule_update', {
    schedule_id: 'SCH001',
    updates: {...}
});
```

### Authentication

All endpoints (except `/api/health` and `/api/auth/login`) require authentication:

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token in subsequent requests
curl -X GET http://localhost:5000/api/vessels \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Default Admin Account**:

- Username: `admin`
- Password: `admin123`
-  **CHANGE IMMEDIATELY ON FIRST LOGIN**

See [**Phase 2 Enhancements**](docs/PHASE2_ENHANCEMENTS.md) for complete API documentation.

---

##  Project Structure

```
project/
├── modules/                          # Core Python modules
│   ├── __init__.py
│   ├── deepsea_data.py              # Deep sea data structures
│   ├── deepsea_loader.py            # Deep sea data loader
│   ├── deepsea_calculator.py        # Deep sea voyage calculation
│   ├── deepsea_gantt_excel.py       # Deep sea Gantt generation
│   ├── deepsea_scenarios.py         # Deep sea scenario management
│   ├── olya_data.py                 # Olya data structures
│   ├── olya_loader.py               # Olya data loader
│   ├── olya_calculator.py           # Olya calculations
│   ├── olya_coordinator.py          # Olya coordination logic
│   ├── olya_gantt_excel.py          # Olya Gantt generation
│   ├── balakovo_data.py             # Balakovo data structures
│   ├── balakovo_loader.py           # Balakovo data loader
│   ├── balakovo_planner.py          # Balakovo berth planning
│   ├── balakovo_gantt.py            # Balakovo Gantt generation
│   ├── berth_constraints.py         # Advanced berth constraints
│   ├── bunker_optimizer.py          # Bunker optimization engine
│   ├── pdf_reporter.py              # PDF report generation
│   ├── rbac.py                      # Role-based access control
│   └── template_generator.py        # CSV template generation
├── input/                           # Input CSV files
│   ├── Vessels.csv
│   ├── Cargo.csv
│   ├── Routes.csv
│   ├── Ports.csv
│   ├── VesselPositions.csv
│   └── ...
├── output/                          # Generated outputs
│   ├── deepsea/                     # Deep sea outputs
│   ├── olya/                        # Olya outputs
│   ├── balakovo/                    # Balakovo outputs
│   ├── reports/                     # PDF reports
│   └── templates/                   # Generated CSV templates
├── tests/                           # Test suite (59 tests)
│   ├── test_berth_constraints.py
│   ├── test_template_generator.py
│   ├── test_test_data_generator.py
│   └── ...
├── docs/                            # Documentation
│   ├── QUICK_START.md
│   ├── WEB_INTERFACES.md
│   ├── BERTH_CONSTRAINTS.md
│   ├── PHASE2_ENHANCEMENTS.md
│   ├── UI_ENHANCEMENT_GUIDE.md
│   └── EXCEL_GANTT_FIX.md
├── ui_modules/                      # Modular UI components
│   ├── alerts_dashboard/
│   ├── berth_management/
│   └── ...
├── logs/                            # Application logs
│   ├── app_YYYYMMDD.log
│   └── errors_YYYYMMDD.log
├── data/rbac/                       # RBAC data storage
│   ├── users.json
│   └── audit_logs.jsonl
├── api_server.py                    # Flask API server
├── api_server_enhanced.py           # Enhanced API (Phase 2+)
├── main_deepsea.py                  # Deep sea entry point
├── main_olya.py                     # Olya entry point
├── main_balakovo.py                 # Balakovo entry point
├── generate_templates.py            # Template generator script
├── config.yaml                      # System configuration
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

##  Configuration

### config.yaml Structure

```yaml
deepsea:
  default_speed_kts: 14
  loading_rate_mt_per_day: 5000
  discharge_rate_mt_per_day: 7000
  canal_transit_days:
    suez: 1.5
    panama: 1.0
  
olya:
  default_speed_kph: 15
  num_berths: 2
  berth_capacity_mt: 10000
  loading_rate_mt_per_day: 2500
  
balakovo:
  default_load_rate: 2500
  berth_capacity_mt: 10000
  max_concurrent_loading: 2
  cleaning_time_hours: 4.0
  
output:
  directory: "output"
  excel_format: "xlsx"
  reports_directory: "output/reports"
  
logging:
  level: "INFO"
  app_log_file: "logs/app_{date}.log"
  error_log_file: "logs/errors_{date}.log"
```

### Input CSV Format

All CSV files use:

- **Delimiter**: `;` (semicolon)
- **Encoding**: UTF-8
- **Date Format**: YYYY-MM-DD
- **Comments**: Start with `#`

**Example - Vessels.csv**:

```csv
vessel_id;vessel_name;vessel_class;dwt_mt;speed_kts
V001;Atlantic Star;Handysize;35000;14
V002;Pacific Dawn;Panamax;75000;15
```

**Example - Cargo.csv**:

```csv
cargo_id;commodity;quantity_mt;load_port;disch_port;laycan_start;laycan_end
C001;Grain;50000;Houston;Rotterdam;2025-01-15;2025-01-20
```

Generate templates with sample data:

```bash
python generate_templates.py
```

---

##  Testing

### Run All Tests

```bash
pytest tests/ -v
```

**Expected Output**: `59 passed` 

### Run Specific Test Suites

```bash
# Test berth constraints
pytest tests/test_berth_constraints.py -v

# Test template generation
pytest tests/test_template_generator.py -v

# Test with coverage
pytest tests/ --cov=modules --cov-report=html
```

### Test Coverage

Current test coverage includes:

-  Berth constraint validation (27 tests)
-  Template generation (18 tests)
-  Test data generation (14 tests)
-  Bunker optimization
-  PDF report generation
-  RBAC authentication/authorization

See [**Test Documentation**](tests/README.md) for details.

---

##  Troubleshooting

### Common Issues

#### Issue: Tests Not Running

**Symptom**: `ModuleNotFoundError: No module named 'modules'`

**Solution**:

```bash
# Ensure you're in the project root directory
cd c:/Users/Asus/Documents/project
pytest tests/ -v
```

#### Issue: Excel Files Won't Open

**Symptom**: Excel cannot open the generated file

**Solution**:

1. Update openpyxl: `pip install --upgrade openpyxl`
2. Use Excel's "Open and Repair" function
3. See [**Excel Gantt Fix Documentation**](docs/EXCEL_GANTT_FIX.md)

#### Issue: Web Interface Not Loading

**Symptom**: Cannot connect to <http://localhost:5000>

**Solution**:

```bash
# Check if server is running
python api_server.py

# Check if port 5000 is already in use
# Windows: netstat -ano | findstr :5000
# Linux/Mac: lsof -i :5000
```

#### Issue: Authentication Fails

**Symptom**: 401 Unauthorized responses

**Solution**:

1. Delete `data/rbac/users.json`
2. Restart server to recreate default admin account
3. Login with username: `admin`, password: `admin123`
4. Change password immediately

#### Issue: Missing CSV Files

**Symptom**: No output files generated

**Solution**:

1. Generate templates: `python generate_templates.py`
2. Check `input/` directory for CSV files
3. Verify CSV format (semicolon delimiter, UTF-8 encoding)
4. Check file permissions for `output/` directory

For more troubleshooting, see [**Quick Start Guide**](docs/QUICK_START.md).

---

##  Documentation

### Core Documentation

- [**Quick Start Guide**](docs/QUICK_START.md) - Get started quickly
- [**Web Interfaces**](docs/WEB_INTERFACES.md) - Web interface usage guide
- [**Berth Constraints**](docs/BERTH_CONSTRAINTS.md) - Advanced berth management
- [**Phase 2 Enhancements**](docs/PHASE2_ENHANCEMENTS.md) - Advanced features (PDF, Bunker, RBAC, WebSocket)

### Technical Documentation

- [**Excel Gantt Fix**](docs/EXCEL_GANTT_FIX.md) - MergedCell type handling
- [**UI Enhancement Guide**](docs/UI_ENHANCEMENT_GUIDE.md) - UI integration guide
- [**Test Documentation**](tests/README.md) - Test suite documentation
- [**UI Modules**](ui_modules/README.md) - Modular UI components

### Reference

- [**Project Rules**](.kilocode/rules/rules.md) - Coding standards and guidelines
- [**API Endpoints**](#api-documentation) - Complete API reference

---

##  Contributing

### Code Quality Standards

- **Language**: All code documentation must be in English
- **Style**: Follow PEP 8 guidelines
- **Type Hints**: Use type hints for function signatures
- **Documentation**: Complete docstrings for all classes and methods
- **Testing**: All new features must include tests
- **No Incomplete Code**: No placeholder comments or stub implementations

### Development Workflow

1. Create feature branch: `feature/your-feature-name`
2. Implement feature with tests
3. Run full test suite: `pytest tests/ -v`
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

### Code Review Checklist

- [ ] Code follows PEP 8 guidelines
- [ ] All functions have type hints
- [ ] Docstrings are clear and complete
- [ ] Tests cover happy path and edge cases
- [ ] No Pylance/type checker warnings
- [ ] Documentation updated
- [ ] All tests pass

---

##  Recent Updates

### Version 2.0.0 (2025-12-18)

-  Advanced berth constraints with validation
-  Bunker optimization engine
-  PDF report generation
-  Role-based access control (RBAC)
-  Real-time WebSocket collaboration
-  Enhanced API server with authentication
-  Comprehensive test suite (59 tests)
-  Updated all documentation

### Version 1.1.0 (2025-12-16)

-  Fixed MergedCell type error in Excel generation
-  Added comprehensive documentation
-  Improved error handling in Gantt charts
-  Enhanced type safety with openpyxl

### Version 1.0.0 (Initial)

- Initial release
- Deep sea scheduling
- Olya river scheduling
- Excel Gantt charts
- Scenario management

---

##  License

This project is proprietary software. All rights reserved.

---

##  Contact

For questions, issues, or support:

- **Email**: Contact the Maritime Logistics Team
- **Documentation**: See [`docs/`](docs/) directory
- **Issue Tracker**: Project issue management system

---

##  Acknowledgments

- Maritime logistics domain expertise
- Python maritime scheduling community
- openpyxl library contributors
- Flask framework team

---

**Last Updated**: 2025-12-18  
**Maintained By**: Maritime Logistics Development Team  
**Python Version**: 3.8+  
**Status**: Production Ready 
