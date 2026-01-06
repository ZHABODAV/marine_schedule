# Vessel Schedule UI Modules

Complete modular UI components for vessel scheduling system. Each module is standalone and can be manually integrated into your HTML vessel schedule.

##  Available Modules

### 1. Alerts Dashboard
**Path:** `ui_modules/alerts_dashboard/`

Real-time alert notifications and management.

**Features:**
- Real-time alert notifications
- Alert history table with filtering
- Alert configuration panel
- Severity indicators (Critical, High, Medium, Low)
- Sound notifications
- Acknowledgment and resolution tracking

**Usage:**
```html
<!-- Include files -->
<link rel="stylesheet" href="ui_modules/alerts_dashboard/alerts_dashboard.css">
<script src="ui_modules/alerts_dashboard/alerts_dashboard.js"></script>

<!-- Add container -->
<div id="alerts-dashboard"></div>

<!-- Initialize -->
<script>
const alertsDashboard = new AlertsDashboard({
    containerId: 'alerts-dashboard',
    apiEndpoint: '/api/alerts',
    refreshInterval: 30000,
    soundEnabled: true
});
alertsDashboard.init();
</script>
```

**API Endpoints Required:**
- `GET /api/alerts` - Get all alerts
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert
- `POST /api/alerts/{id}/resolve` - Resolve alert

---

### 2. Berth Management
**Path:** `ui_modules/berth_management/`

Comprehensive berth management with constraints and conflict detection.

**Features:**
- Berth utilization dashboard
- Constraints editor (max length, draft, beam, maintenance periods)
- Berth capacity planning tools
- Conflict visualization and resolution
- Overbooking warnings

**Usage:**
```html
<link rel="stylesheet" href="ui_modules/berth_management/berth_management.css">
<script src="ui_modules/berth_management/berth_management.js"></script>

<div id="berth-management"></div>

<script>
const berthMgmt = new BerthManagement({
    containerId: 'berth-management',
    apiEndpoint: '/api/berths'
});
berthMgmt.init();
</script>
```

**API Endpoints Required:**
- `GET /api/berths` - Get berth data
- `GET /api/berths/capacity?days=14` - Get capacity data
- `POST /api/berths/constraints` - Save constraint
- `DELETE /api/berths/constraints/{id}` - Delete constraint
- `POST /api/berths/conflicts/auto-resolve` - Auto-resolve conflicts
- `POST /api/berths/conflicts/{id}/resolve` - Resolve single conflict

---

### 3. Bunker Optimization Interface
**Path:** `ui_modules/bunker_optimization/`

Bunker cost optimization and route planning.

**Features:**
- Bunker cost calculator
- Optimization parameter configuration
- Route-based bunker planning
- Bunker port selection
- Cost comparison charts

**Usage:**
```html
<link rel="stylesheet" href="ui_modules/bunker_optimization/bunker_optimization.css">
<script src="ui_modules/bunker_optimization/bunker_optimization.js"></script>

<div id="bunker-optimization"></div>

<script>
const bunkerOpt = new BunkerOptimization({
    containerId: 'bunker-optimization',
    apiEndpoint: '/api/bunker'
});
bunkerOpt.init();
</script>
```

---

### 4. Weather Integration
**Path:** `ui_modules/weather_integration/`

Weather data visualization and warnings.

**Features:**
- Weather warnings overlay on Gantt charts
- Weather forecast display
- Route weather risk indicators
- Storm tracking
- Wind and wave condition analysis

**Usage:**
```html
<link rel="stylesheet" href="ui_modules/weather_integration/weather_integration.css">
<script src="ui_modules/weather_integration/weather_integration.js"></script>

<div id="weather-integration"></div>

<script>
const weather = new WeatherIntegration({
    containerId: 'weather-integration',
    apiEndpoint: '/api/weather',
    ganttElementId: 'gantt-chart' // For overlay
});
weather.init();
</script>
```

---

### 5. Vessel Tracking
**Path:** `ui_modules/vessel_tracking/`

Live vessel position tracking and status updates.

**Features:**
- Live vessel positions on map
- Vessel status updates
- AIS data integration support
- Route tracking
- ETA calculations

**Usage:**
```html
<link rel="stylesheet" href="ui_modules/vessel_tracking/vessel_tracking.css">
<script src="ui_modules/vessel_tracking/vessel_tracking.js"></script>

<div id="vessel-tracking"></div>

<script>
const tracking = new VesselTracking({
    containerId: 'vessel-tracking',
    apiEndpoint: '/api/vessels/tracking',
    mapProvider: 'leaflet' // or 'google', 'mapbox'
});
tracking.init();
</script>
```

---

### 6. PDF Export
**Path:** `ui_modules/pdf_export/`

Generate PDF reports and export functionality.

**Features:**
- PDF report generation
- Customizable templates
- Schedule export
- Multi-page reports
- Chart/table embedding

**Usage:**
```html
<script src="ui_modules/pdf_export/pdf_export.js"></script>

<button id="export-pdf-btn">Export PDF</button>

<script>
const pdfExporter = new PDFExport({
    apiEndpoint: '/api/export/pdf',
    reportTypes: ['schedule', 'berth', 'fleet']
});

document.getElementById('export-pdf-btn').addEventListener('click', async () => {
    await pdfExporter.generateReport('schedule', {
        dateRange: { start: '2025-01-01', end: '2025-01-31' }
    });
});
</script>
```

---

### 7. Advanced Scenario Management
**Path:** `ui_modules/scenario_management/`

Create and manage multiple scheduling scenarios.

**Features:**
- Scenario creation wizard
- Scenario editing interface
- What-if analysis tools
- Scenario comparison
- Version control

**Usage:**
```html
<link rel="stylesheet" href="ui_modules/scenario_management/scenario_management.css">
<script src="ui_modules/scenario_management/scenario_management.js"></script>

<div id="scenario-management"></div>

<script>
const scenarios = new ScenarioManagement({
    containerId: 'scenario-management',
    apiEndpoint: '/api/scenarios'
});
scenarios.init();
</script>
```

---

### 8. Voyage Templates
**Path:** `ui_modules/voyage_templates/`

Template library for common voyages.

**Features:**
- Template library browser
- Template creation and editing
- Apply templates to new voyages
- Template categorization
- Parameter customization

**Usage:**
```html
<link rel="stylesheet" href="ui_modules/voyage_templates/voyage_templates.css">
<script src="ui_modules/voyage_templates/voyage_templates.js"></script>

<div id="voyage-templates"></div>

<script>
const templates = new VoyageTemplates({
    containerId: 'voyage-templates',
    apiEndpoint: '/api/voyage-templates'
});
templates.init();
</script>
```

---

### 9. Berth Capacity Planning
**Path:** `ui_modules/berth_capacity_planning/`

Advanced capacity planning and allocation.

**Features:**
- Capacity vs demand charts
- Overbooking warnings
- Capacity allocation optimization
- Multi-berth planning
- Resource utilization forecasting

**Usage:**
```html
<link rel="stylesheet" href="ui_modules/berth_capacity_planning/berth_capacity_planning.css">
<script src="ui_modules/berth_capacity_planning/berth_capacity_planning.js"></script>

<div id="capacity-planning"></div>

<script>
const capacityPlanning = new BerthCapacityPlanning({
    containerId: 'capacity-planning',
    apiEndpoint: '/api/capacity'
});
capacityPlanning.init();
</script>
```

---

##  Shared Styles

Common CSS variables and utilities used across modules:

```css
:root {
    /* Colors */
    --primary-color: #3b82f6;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --info-color: #06b6d4;
    
    /* Severity Colors */
    --critical-color: #ef4444;
    --high-color: #f59e0b;
    --medium-color: #eab308;
    --low-color: #10b981;
    
    /* Neutral Colors */
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    
    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    
    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 6px;
    --radius-lg: 8px;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

---

##  Integration Guide

### Step 1: Include Module Files

Add CSS and JS files to your HTML:

```html
<!-- In <head> -->
<link rel="stylesheet" href="ui_modules/[module-name]/[module-name].css">

<!-- Before </body> -->
<script src="ui_modules/[module-name]/[module-name].js"></script>
```

### Step 2: Add HTML Container

Place the container where you want the module to appear:

```html
<div id="[module-container-id]"></div>
```

### Step 3: Initialize Module

Initialize the module with configuration:

```javascript
const moduleInstance = new ModuleClass({
    containerId: '[module-container-id]',
    apiEndpoint: '/api/[endpoint]',
    // Additional options...
});

moduleInstance.init();
```

### Step 4: Implement Backend API

Each module requires specific API endpoints (see module documentation above).

Example API response format for Alerts:

```json
{
    "alerts": [
        {
            "id": "alert_001",
            "timestamp": "2025-01-15T10:30:00Z",
            "severity": "high",
            "type": "berth_conflict",
            "status": "active",
            "message": "Berth overlap detected",
            "vessel": "MV Atlantica",
            "details": "Vessel scheduled during maintenance window"
        }
    ]
}
```

---

##  Events and Notifications

Modules dispatch custom events that you can listen for:

```javascript
// Notification events
document.addEventListener('showNotification', (e) => {
    const { type, message } = e.detail;
    // Display notification: type can be 'success', 'error', 'warning', 'info'
    console.log(`[${type}] ${message}`);
});

// Modal events
document.addEventListener('showModal', (e) => {
    const { content } = e.detail;
    // Display modal with content
    console.log('Show modal:', content);
});

// Data update events
document.addEventListener('dataUpdated', (e) => {
    const { module, data } = e.detail;
    // Handle data updates
    console.log(`${module} data updated:`, data);
});
```

---

##  Security Considerations

1. **API Authentication**: Implement proper authentication for all API endpoints
2. **Input Validation**: Validate all user inputs on backend
3. **CSRF Protection**: Use CSRF tokens for state-changing operations
4. **Rate Limiting**: Implement rate limiting on API endpoints
5. **Data Sanitization**: Sanitize data before displaying in UI

---

##  Responsive Design

All modules are designed to be responsive and work on:
- Desktop (1920x1080 and above)
- Laptop (1366x768)
- Tablet (768x1024)
- Mobile (320x568 and above)

---

##  Testing

### Unit Testing

Each module can be tested independently:

```javascript
// Example test
describe('AlertsDashboard', () => {
    let dashboard;
    
    beforeEach(() => {
        document.body.innerHTML = '<div id="test-container"></div>';
        dashboard = new AlertsDashboard({
            containerId: 'test-container',
            apiEndpoint: '/api/alerts'
        });
    });
    
    test('should initialize correctly', () => {
        expect(dashboard.initialized).toBe(false);
        dashboard.init();
        expect(dashboard.initialized).toBe(true);
    });
});
```

### Integration Testing

Test modules together:

```javascript
// Initialize multiple modules and test interactions
const alerts = new AlertsDashboard({ containerId: 'alerts-dashboard' });
const berths = new BerthManagement({ containerId: 'berth-management' });

alerts.init();
berths.init();

// Test cross-module event handling
document.addEventListener('dataUpdated', (e) => {
    if (e.detail.module === 'berths') {
        alerts.loadAlerts(); // Refresh alerts when berth data changes
    }
});
```

---

##  Performance Optimization

### Lazy Loading

Load modules only when needed:

```javascript
async function loadModule(moduleName) {
    const css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = `ui_modules/${moduleName}/${moduleName}.css`;
    document.head.appendChild(css);
    
    const js = await import(`./ui_modules/${moduleName}/${moduleName}.js`);
    return js.default;
}

// Usage
document.getElementById('show-alerts-btn').addEventListener('click', async () => {
    const AlertsDashboard = await loadModule('alerts_dashboard');
    const dashboard = new AlertsDashboard({ containerId: 'alerts-dashboard' });
    dashboard.init();
});
```

### Data Caching

Implement caching to reduce API calls:

```javascript
class AlertsDashboard {
    constructor(config) {
        this.cache = {
            data: null,
            timestamp: null,
            ttl: 60000 // 1 minute
        };
    }
    
    async loadAlerts() {
        const now = Date.now();
        if (this.cache.data && (now - this.cache.timestamp) < this.cache.ttl) {
            this.processAlerts(this.cache.data);
            return;
        }
        
        const response = await fetch(this.config.apiEndpoint);
        const data = await response.json();
        
        this.cache.data = data.alerts;
        this.cache.timestamp = now;
        this.processAlerts(data.alerts);
    }
}
```

---

##  Troubleshooting

### Common Issues

**Module not rendering:**
- Check container ID matches configuration
- Ensure CSS/JS files are loaded
- Check browser console for errors

**API errors:**
- Verify API endpoints are accessible
- Check network tab for failed requests
- Validate API response format

**Performance issues:**
- Reduce refresh intervals
- Implement data pagination
- Enable caching

---

##  License

These modules are part of the Vessel Scheduling System. 
All code must follow project coding standards:
- English comments and documentation
- No incomplete implementations
- Comprehensive error handling
- Complete, working code

---

##  Contributing

When adding new modules:
1. Follow the existing module structure
2. Include complete JS, HTML, CSS files
3. Document API requirements
4. Add usage examples
5. Update this README

---

##  Support

For issues or questions:
- Check module-specific documentation
- Review API endpoint requirements
- Verify integration steps
- Check browser console for errors
