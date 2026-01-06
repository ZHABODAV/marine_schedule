# Unified Dashboard Documentation

## Overview

The Unified Dashboard is a comprehensive control center that integrates all major features of the Vessel Scheduler application into a single, user-friendly interface. It provides quick access to:

- **Import/Export** - Data export functionality
- **Trading Lanes** - Route management and optimization
- **Financial Calculator** - Cost analysis and bunker optimization
- **Network Visualization** - Port and route network views
- **Storage Manager** - Session and data persistence

## Features

### 1. Import/Export Manager

The Import/Export section provides one-click access to export various reports:

- **Gantt Chart Export** - Export voyage schedules as Excel Gantt charts
- **Fleet Overview** - Export complete vessel fleet data
- **Voyage Summary** - Export cargo and voyage commitments
- **Financial Report** - Export detailed financial analysis

**Usage:**
```javascript
// Export Gantt chart
window.unifiedDashboard.exportGantt();

// Export fleet overview
window.unifiedDashboard.exportFleet();

// Export voyage summary
window.unifiedDashboard.exportVoyages();

// Export financial report
window.unifiedDashboard.exportFinancial();
```

### 2. Trading Lanes Management

Manage trading routes and cargo lanes:

- **Create Lane** - Create new trading lanes with target volumes
- **View All** - View and manage all active trading lanes
- **Place Volume** - Distribute cargo volume across lanes

**Features:**
- Lane mini-list showing active lanes
- Volume and frequency tracking
- Quick access to lane operations

**Usage:**
```javascript
// Create new trading lane
window.unifiedDashboard.createTradingLane();

// View all trading lanes
window.unifiedDashboard.viewTradingLanes();

// Place volume into lanes
window.unifiedDashboard.placeVolume();
```

### 3. Financial Calculator

Real-time financial analysis and optimization:

- **Calculate** - Run financial analysis on all voyages
- **Optimize Bunker** - Optimize fuel costs across fleet

**Displays:**
- Total costs
- Bunker costs breakdown
- Hire costs summary

**Usage:**
```javascript
// Run financial calculations
window.unifiedDashboard.calculateFinancials();

// Optimize bunker strategy
window.unifiedDashboard.optimizeBunker();
```

### 4. Network Visualization

Visualize port and route networks:

- **Show Network** - Display interactive network graph
- **Export Snapshot** - Export network data to Excel

**Stats:**
- Total ports in network
- Total routes configured

**Usage:**
```javascript
// Show network visualization
window.unifiedDashboard.showNetwork();

// Export network snapshot
window.unifiedDashboard.exportNetwork();
```

### 5. Storage Manager

Manage application data persistence:

- **Save Session** - Save current state to localStorage
- **Load Session** - Restore previous session
- **Clear Storage** - Clear all saved data

**Displays:**
- Last save timestamp
- Storage size used

**Usage:**
```javascript
// Save current session
window.unifiedDashboard.saveSession();

// Load saved session
window.unifiedDashboard.loadSession();

// Clear all storage
window.unifiedDashboard.clearStorage();
```

## Dashboard Statistics

The dashboard displays real-time statistics:

- **Vessels** - Total number of vessels in fleet
- **Cargo Orders** - Total cargo commitments
- **Trading Lanes** - Active trading lanes
- **Total Costs** - Calculated total costs

## Quick Actions

The Quick Actions bar provides instant access to common operations:

- **Refresh All** - Refresh all dashboard components
- **Export All** - Export all available reports
- **View Reports** - Navigate to reports section
- **Switch Module** - Switch between Deep Sea, Balakovo, and Olya modules

## Recent Activity

The Recent Activity panel tracks:
- Export operations
- Financial calculations
- Session saves/loads
- Configuration changes

## Integration

### Adding to Main Application

The unified dashboard is automatically integrated in [`js/main.js`](../js/main.js):

```javascript
import UnifiedDashboard from './modules/unified-dashboard.js';

// In initModules()
this.modules.unifiedDashboard = UnifiedDashboard;

// In onTabChange()
case 'dashboard':
    this.modules.unifiedDashboard?.render();
    break;
```

### CSS Styling

Dashboard styles are defined in [`css/unified-dashboard.css`](../css/unified-dashboard.css) and include:

- Responsive grid layouts
- Feature cards with hover effects
- Statistical widgets
- Quick action buttons
- Activity timeline

### HTML Template

The dashboard HTML is dynamically generated in [`js/modules/unified-dashboard.js`](../js/modules/unified-dashboard.js) using the `renderUnifiedDashboard()` function.

## API Reference

### Main Functions

#### `renderUnifiedDashboard()`
Renders the complete dashboard interface into the main content area.

#### `updateDashboardStats()`
Updates all statistical counters in real-time.

#### `updateLanesMiniList()`
Refreshes the trading lanes mini-list display.

#### `updateFinancialSummary()`
Updates the financial summary cards.

#### `updateNetworkStats()`
Updates network visualization statistics.

#### `updateStorageInfo()`
Updates storage manager information.

#### `updateRecentActivity()`
Refreshes the recent activity timeline.

### Dashboard Actions

All dashboard actions are exposed via `window.unifiedDashboard`:

```javascript
window.unifiedDashboard = {
    // Import/Export
    exportGantt,
    exportFleet,
    exportVoyages,
    exportFinancial,
    
    // Trading Lanes
    createTradingLane,
    viewTradingLanes,
    placeVolume,
    
    // Financial
    calculateFinancials,
    optimizeBunker,
    
    // Network
    showNetwork,
    exportNetwork,
    
    // Storage
    saveSession,
    loadSession,
    clearStorage,
    
    // Quick Actions
    refreshAll,
    exportAll,
    viewReports,
    switchModule
}
```

## Customization

### Adding New Features

To add a new feature card to the dashboard:

1. Add the feature card HTML in `renderUnifiedDashboard()`
2. Create action handler functions
3. Add the handler to `dashboardActions` object
4. Expose via `window.unifiedDashboard`

Example:
```javascript
// In renderUnifiedDashboard()
<div class="feature-card">
    <div class="feature-header">
        <h3><i class="fas fa-icon"></i> New Feature</h3>
    </div>
    <div class="feature-body">
        <button onclick="window.unifiedDashboard.newFeature()">
            Action
        </button>
    </div>
</div>

// In dashboardActions
const dashboardActions = {
    newFeature() {
        // Implementation
    }
};
```

### Styling

Customize dashboard appearance in [`css/unified-dashboard.css`](../css/unified-dashboard.css):

```css
.feature-card {
    background: var(--bg-secondary);
    border-radius: 12px;
    /* Custom styles */
}
```

## Responsive Design

The dashboard is fully responsive:

- **Desktop (>1024px)**: Multi-column grid layout
- **Tablet (641-1024px)**: Two-column layout
- **Mobile (<640px)**: Single column layout

## Accessibility

- Keyboard navigation support
- Screen reader friendly
- High contrast mode compatible
- ARIA labels on interactive elements

## Performance

- Lazy loading of statistics
- Debounced update functions
- Efficient DOM manipulation
- Minimal re-renders

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

### Dashboard Not Showing

Check that the CSS file is loaded:
```html
<link rel="stylesheet" href="css/unified-dashboard.css">
```

### Actions Not Working

Verify that the module is properly initialized:
```javascript
console.log(window.unifiedDashboard);
// Should show object with all action functions
```

### Statistics Not Updating

Manually refresh the dashboard:
```javascript
window.unifiedDashboard.refreshAll();
```

## Related Documentation

- [Module System Setup](./MODULE_SYSTEM_SETUP.md)
- [JavaScript Modernization Plan](./JAVASCRIPT_MODERNIZATION_PLAN.md)
- [API Reference](./API_REFERENCE.md)
- [Financial Analysis](./COMPREHENSIVE_CALCULATION_GUIDE.md)

## Version History

- **v1.0.0** (2025-12-26) - Initial release
  - Import/Export integration
  - Trading Lanes management
  - Financial Calculator
  - Network Visualization
  - Storage Manager
  - Quick Actions
  - Recent Activity tracking

## Future Enhancements

- [ ] Real-time notifications
- [ ] Customizable widget layout
- [ ] Dashboard themes
- [ ] Export dashboard configuration
- [ ] Widget drag-and-drop
- [ ] Advanced analytics widgets
- [ ] Integration with external APIs
- [ ] Multi-user collaboration features
