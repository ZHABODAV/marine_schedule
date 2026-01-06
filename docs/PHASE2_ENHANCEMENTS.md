# Phase 2+ Enhancements Documentation

**Version**: 2.0.0  
**Last Updated**: 2025-12-18  
**Status**:  Implemented

---

## Overview

Phase 2+ brings significant enhancements to the Vessel Scheduler System, transforming it from a basic planning tool into an enterprise-grade maritime logistics platform with advanced features for financial optimization, security, collaboration, and reporting.

## New Features

### 1. PDF Report Generation 

Professional PDF reports for vessel schedules, voyage summaries, fleet overviews, and berth utilization.

#### Module

[`modules/pdf_reporter.py`](../modules/pdf_reporter.py:1)

#### Key Classes

- [`PDFReportGenerator`](../modules/pdf_reporter.py:35) - Main PDF generation class

#### Features

-  Vessel schedule reports with custom styling
-  Voyage summary reports with financial analysis
-  Fleet overview reports with utilization metrics
-  Berth utilization reports by port
-  Custom multi-section reports
-  Professional headers, footers, and branding
-  Color-coded tables and charts

#### API Endpoints

```
POST /api/reports/pdf/vessel-schedule
POST /api/reports/pdf/voyage-summary
POST /api/reports/pdf/fleet-overview
POST /api/reports/pdf/berth-utilization
```

#### Usage Example

```python
from modules.pdf_reporter import PDFReportGenerator
import pandas as pd

# Initialize generator
pdf_gen = PDFReportGenerator(output_dir="output/reports")

# Generate vessel schedule report
vessel_df = pd.DataFrame({...})
filepath = pdf_gen.generate_vessel_schedule_report(
    vessel_data=vessel_df,
    filename="vessel_schedule_202512.pdf",
    title="December 2025 Vessel Schedule"
)
```

#### Request Example (API)

```bash
curl -X POST http://localhost:5000/api/reports/pdf/vessel-schedule \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type": "deepsea"}'
```

---

### 2.  Bunker Optimization 

Advanced fuel procurement and consumption optimization using price analysis and route optimization algorithms.

#### Module

[`modules/bunker_optimizer.py`](../modules/bunker_optimizer.py:1)

#### Key Classes

- [`BunkerOptimizer`](../modules/bunker_optimizer.py:120) - Main optimization engine
- [`BunkerPrice`](../modules/bunker_optimizer.py:23) - Fuel price data structure
- [`FuelConsumption`](../modules/bunker_optimizer.py:33) - Consumption parameters
- [`BunkerPlan`](../modules/bunker_optimizer.py:101) - Optimized bunker plan

#### Features

-  Price-based optimization (buy at cheapest ports)
-  Route-based optimization (minimize detours)
-  Speed optimization (eco-speed recommendations)
-  Multi-fuel type support (VLSFO, MGO, LSMGO, HFO, LNG)
-  ECA (Emission Control Area) compliance
-  Fuel hedging position calculator
-  Bunker market analysis

#### API Endpoints

```
POST /api/bunker/optimize
GET  /api/bunker/prices
GET  /api/bunker/market-analysis
```

#### Usage Example

```python
from modules.bunker_optimizer import BunkerOptimizer, FuelType

# Initialize optimizer
optimizer = BunkerOptimizer(bunker_prices, fuel_consumption_params)

# Optimize bunker plan
plan = optimizer.optimize_bunker_plan(
    voyage_id="V001",
    vessel_id="vessel_1",
    route_ports=["SINGAPORE", "ROTTERDAM", "HOUSTON"],
    distances_nm=[5000, 4800],
    port_times_days=[2, 1],
    fuel_type=FuelType.VLSFO,
    current_fuel_mt=1000,
    allow_eco_speed=True
)

# Get summary
summary = plan.get_summary()
print(f"Total Cost: ${summary['total_cost_usd']:,.2f}")
print(f"Savings: ${summary['savings_usd']:,.2f}")
```

#### Request Example (API)

```bash
curl -X POST http://localhost:5000/api/bunker/optimize \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "voyage_id": "V001",
    "vessel_id": "vessel_1",
    "route_ports": ["SINGAPORE", "ROTTERDAM"],
    "distances_nm": [5000],
    "port_times_days": [2],
    "fuel_type": "VLSFO",
    "current_fuel_mt": 1000,
    "allow_eco_speed": true
  }'
```

---

### 3. Role-Based Access Control (RBAC) 

Comprehensive authentication, authorization, and user management system.

#### Module

[`modules/rbac.py`](../modules/rbac.py:1)

#### Key Classes

- [`RBACManager`](../modules/rbac.py:169) - Main RBAC manager
- [`User`](../modules/rbac.py:72) - User entity
- [`Role`](../modules/rbac.py:58) - Role with permissions
- [`AuditLog`](../modules/rbac.py:149) - Audit trail

#### Predefined Roles

1. **Administrator** - Full system access
2. **Operations Manager** - Manage operations and schedules
3. **Scheduler** - Create and edit schedules
4. **Finance Manager** - Financial oversight
5. **Viewer** - Read-only access
6. **Port Agent** - Port-specific operations

#### Permissions

```python
class Permission(Enum):
    # Vessel permissions
    VIEW_VESSELS = "view_vessels"
    CREATE_VESSELS = "create_vessels"
    EDIT_VESSELS = "edit_vessels"
    DELETE_VESSELS = "delete_vessels"
    
    # Voyage permissions
    VIEW_VOYAGES = "view_voyages"
    CREATE_VOYAGES = "create_voyages"
    EDIT_VOYAGES = "edit_voyages"
    APPROVE_VOYAGES = "approve_voyages"
    
    # Schedule permissions
    VIEW_SCHEDULES = "view_schedules"
    CREATE_SCHEDULES = "create_schedules"
    PUBLISH_SCHEDULES = "publish_schedules"
    
    # Financial permissions
    VIEW_FINANCIALS = "view_financials"
    EDIT_FINANCIALS = "edit_financials"
    APPROVE_BUDGETS = "approve_budgets"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    SYSTEM_SETTINGS = "system_settings"
```

#### API Endpoints

```
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

#### Usage Example

```python
from modules.rbac import RBACManager, UserRole, Permission

# Initialize RBAC
rbac = RBACManager()

# Create user
user = rbac.create_user(
    username="john_doe",
    password="secure_password",
    email="john@example.com",
    full_name="John Doe",
    role_names=[UserRole.SCHEDULER.value],
    department="Operations"
)

# Authenticate
token = rbac.authenticate("john_doe", "secure_password")

# Check permission
has_perm = rbac.check_permission(token, Permission.CREATE_VOYAGES)
```

#### Request Example (API)

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token in subsequent requests
curl -X GET http://localhost:5000/api/vessels \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Default Admin Account

```
Username: admin
Password: admin123
 CHANGE IMMEDIATELY ON FIRST LOGIN
```

---

### 4. Real-Time Collaboration (WebSocket) 

Live updates and multi-user collaboration using WebSocket technology.

#### Implementation

[`api_server_enhanced.py`](../api_server_enhanced.py:1) with Flask-SocketIO

#### Features

-  Real-time schedule updates broadcast to all users
-  Room-based collaboration (per schedule)
-  User presence tracking (join/leave notifications)
-  Bidirectional communication
-  Auto-reconnection support

#### Events

```javascript
// Client-side events
socket.on('connected', (data) => {
    console.log(data.message);
});

socket.on('schedule_changed', (data) => {
    console.log('Schedule updated:', data.updates);
    // Update UI
});

socket.on('user_joined', (data) => {
    console.log('User joined schedule:', data.schedule_id);
});

// Emit events
socket.emit('join_schedule', {schedule_id: 'SCH001'});
socket.emit('schedule_update', {
    schedule_id: 'SCH001',
    updates: {...}
});
```

#### Server Events

- `connect` - Client connection established
- `join_schedule` - Join a schedule collaboration room
- `leave_schedule` - Leave a schedule room
- `schedule_update` - Broadcast schedule changes

---

### 5. Enhanced API Server 

Complete rewrite with improved error handling, authentication, and new endpoints.

#### File

[`api_server_enhanced.py`](../api_server_enhanced.py:1)

#### Improvements

-  Comprehensive error handling (400, 401, 403, 404, 500)
-  Authentication decorators (`@require_auth`, `@require_permission`)
-  Request validation and sanitization
-  Detailed error logging with stack traces
-  WebSocket integration
-  Modern HTML landing page
-  Backward compatibility with original API

#### Running the Enhanced Server

```bash
# Install new dependencies
pip install -r requirements.txt

# Run enhanced server
python api_server_enhanced.py
```

#### Server Output

```
============================================================
Starting Enhanced Vessel Scheduler API Server v2.0
============================================================
Server running on http://localhost:5000
WebSocket support enabled on same port

Phase 2+ Features Active:
   PDF Report Generation
   Bunker Optimization
   Role-Based Access Control (RBAC)
   Real-time Collaboration (WebSocket)
   Enhanced Error Handling

Default Admin Account:
  Username: admin
  Password: admin123 (please change immediately)
============================================================
```

---

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### New Dependencies Added

```
flask-socketio>=5.3.0      # WebSocket support
reportlab>=4.0.0          # PDF generation
python-socketio>=5.9.0     # WebSocket client
```

### 2. Initialize RBAC

The RBAC system automatically initializes with a default admin account on first run. Data is stored in `data/rbac/`.

### 3. Start Enhanced Server

```bash
python api_server_enhanced.py
```

---

## API Authentication

All API endpoints (except `/api/auth/login` and `/api/health`) require authentication.

### Getting a Token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Using the Token

```bash
curl -X GET http://localhost:5000/api/vessels \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Token Expiration

Tokens expire after 8 hours. Refresh by logging in again.

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run tests for specific modules
pytest tests/test_pdf_reporter.py -v
pytest tests/test_bunker_optimizer.py -v
pytest tests/test_rbac.py -v
```

### Test Coverage

Tests cover:

-  PDF generation for all report types
-  Bunker optimization algorithms
-  RBAC authentication and authorization
-  Permission checks
-  Audit logging

---

## Security Considerations

### Authentication

-  Password hashing using SHA-256
-  Secure session token generation
-  Token expiration (8 hours)
-  Audit logging of all authentication events

### Authorization

-  Fine-grained permission system
-  Role-based access control
-  Permission decorators on API endpoints
-  403 Forbidden responses for unauthorized access

### Best Practices

1. **Change Default Password**: Immediately change the default admin password
2. **Use HTTPS**: In production, use HTTPS for all API communication
3. **Secure Secret Key**: Change the Flask secret key in production
4. **Regular Audits**: Review audit logs regularly
5. **Principle of Least Privilege**: Assign minimum necessary permissions

---

## Future Enhancements (Phase 3)

### Planned Features

- [ ] Weather Routing Integration
- [ ] AIS Vessel Tracking
- [ ] Mobile-Responsive UI  
- [ ] Multi-Language Support (i18n)
- [ ] Advanced Analytics Dashboard
- [ ] Email Notifications
- [ ] Calendar Integration
- [ ] REST API Documentation (Swagger/OpenAPI)

### Potential Integrations

- [ ] External Weather Services (NOAA, MeteoGroup)
- [ ] AIS Data Providers (MarineTraffic, VesselFinder)
- [ ] Port Authorities APIs
- [ ] Fuel Price Indices (Port Bunker Price Index)
- [ ] Insurance and Risk Management Systems

---

## Migration Guide

### From v1.x to v2.0

1. **Update Dependencies**

   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Switch to Enhanced Server**

   ```bash
   # Old
   python api_server.py
   
   # New
   python api_server_enhanced.py
   ```

3. **Add Authentication to API Calls**
   - All API calls now require authentication token
   - Login to get token, include in `Authorization` header

4. **Update Frontend (if custom)**
   - Add authentication flow
   - Handle 401/403 responses
   - Integrate WebSocket for real-time updates

---

## Troubleshooting

### PDF Generation Issues

**Problem**: ImportError for reportlab  
**Solution**: `pip install reportlab>=4.0.0`

**Problem**: PDF file won't open  
**Solution**: Check write permissions for `output/reports/` directory

### RBAC Issues

**Problem**: Can't login with admin account  
**Solution**: Delete `data/rbac/users.json`, restart server to recreate default admin

**Problem**: Permission denied errors  
**Solution**: Check user roles and permissions in `data/rbac/users.json`

### WebSocket Issues

**Problem**: Real-time updates not working  
**Solution**: Ensure `flask-socketio` is installed, check browser console for connection errors

**Problem**: CORS errors with WebSocket  
**Solution**: Add your domain to `cors_allowed_origins` in SocketIO initialization

---

## Contact & Support

For questions, issues, or feature requests regarding Phase 2+ enhancements:

- **GitHub Issues**: [Project Issues](https://github.com/your-repo/issues)
- **Documentation**: [`docs/`](.) directory
- **Examples**: [`examples/phase2/`](../examples/phase2/)

---

**Phase 2+ Implementation Team**  
Maritime Logistics Development Division  
Version 2.0.0 - December 2025
