# Module Loading System

## Overview

The Vessel Scheduler application uses a **modern ES6 module system** for better code organization, maintainability, and performance. This document explains how the module system works and how to use it.

## Architecture

### Entry Points

The application has multiple entry points depending on how you want to use it:

1. **`index.html`** - Main application entry point with full UI
   - Loads all core modules
   - Provides complete application interface
   - Includes loading screen and error handling
   - Best for production use

2. **`vessel_scheduler_complete.html`** - Complete scheduler interface
   - Legacy-compatible version
   - Includes both modern modules and legacy code
   - Transitional version during modernization

3. **`operational_calendar.html`** - Standalone calendar module
   - Lightweight, focused on calendar functionality
   - Can be embedded in other applications
   - Perfect for specific use cases

## Module Structure

```
js/
├── main.js                    # Main application entry point
├── index.js                   # Legacy loader (being phased out)
├── core/
│   ├── config.js             # Application configuration
│   ├── app-state.js          # Global state management
│   └── utils.js              # Utility functions
├── modules/                   # Feature modules
│   ├── vessel-management.js  # Vessel operations
│   ├── cargo-management.js   # Cargo handling
│   ├── route-management.js   # Route planning
│   ├── voyage-builder.js     # Voyage construction
│   ├── trading-lanes.js      # Trading lane management
│   ├── financial-analysis.js # Financial calculations
│   ├── gantt-chart.js        # Gantt chart visualization
│   ├── network-viz.js        # Network visualization
│   └── operational-calendar.js # Calendar operations
├── services/
│   └── storage-service.js    # Data persistence
└── ui/
    ├── dashboard.js          # Dashboard UI
    ├── filters.js            # Filter components
    └── modals.js             # Modal dialogs
```

## How It Works

### 1. HTML Entry Point

Each HTML file loads the application using ES6 module syntax:

```html
<!-- External libraries first -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
<script src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>

<!-- Then load modules -->
<script type="module">
    import VesselSchedulerApp from './js/main.js';
    
    document.addEventListener('DOMContentLoaded', async () => {
        const app = new VesselSchedulerApp();
        await app.init();
        window.vesselSchedulerApp = app;
    });
</script>
```

### 2. Main Application ([`main.js`](main.js:1))

The main application:
- Imports all necessary modules
- Creates application instance
- Initializes state management
- Sets up UI components
- Manages module lifecycle

```javascript
import { CONFIG } from './core/config.js';
import { AppState } from './core/app-state.js';
import { VesselManager } from './modules/vessel-management.js';
// ... other imports

class VesselSchedulerApp {
    constructor() {
        this.state = new AppState();
        this.modules = {};
    }
    
    async init() {
        // Initialize modules
        this.modules.vessels = new VesselManager(this.state);
        // ... initialize other modules
    }
}
```

### 3. Module Pattern

Each module follows a consistent pattern:

```javascript
// modules/example-module.js
export class ExampleModule {
    constructor(state, storage) {
        this.state = state;
        this.storage = storage;
    }
    
    async init() {
        // Module initialization
    }
    
    // Module methods...
}
```

## Loading Sequence

1. **Browser loads HTML** - Parses HTML, loads external libraries
2. **DOMContentLoaded fires** - DOM is ready
3. **Module import** - Browser fetches and parses [`main.js`](main.js:1)
4. **Dependency resolution** - Browser fetches all imported modules
5. **Application initialization** - Main app creates instances
6. **Module initialization** - Each module initializes in order
7. **Ready** - Application dispatches ready event

## Benefits

### Code Splitting
- Modules are loaded on-demand
- Smaller initial bundle size
- Faster page loads

### Dependency Management
- Clear dependency tree
- No global namespace pollution
- Automatic dependency resolution

### Maintainability
- Each module is self-contained
- Easy to test in isolation
- Clear separation of concerns

### Performance
- Native browser module support
- Parallel module loading
- Efficient caching

## Browser Compatibility

Modern browsers support ES6 modules natively:
- Chrome 61+
- Firefox 60+
- Safari 11+
- Edge 16+

For older browsers, consider using a build tool like Webpack or Rollup.

## Migration Path

The application is transitioning from legacy code to modern modules:

### Current State
-  Module structure created
-  Main application converted
-  Core modules implemented
- ⏳ Legacy functions being extracted
- ⏳ UI modules being modernized

### Phase 1: Dual Mode (Current)
Both systems run in parallel:
- Modern modules for new features
- Legacy code for compatibility
- Gradual migration of features

### Phase 2: Module-First
Modern modules primary:
- Most features use modules
- Legacy code minimal
- Better performance

### Phase 3: Full Modern
Complete modernization:
- All code in modules
- Legacy code removed
- Optimal performance

## Usage Examples

### Basic Application

```javascript
// Import and initialize
import VesselSchedulerApp from './js/main.js';

const app = new VesselSchedulerApp();
await app.init();

// Access modules
const vesselManager = app.getModule('vessels');
vesselManager.addVessel({ ... });
```

### Standalone Module

```javascript
// Use a specific module
import { OperationalCalendar } from './js/modules/operational-calendar.js';
import { AppState } from './js/core/app-state.js';

const state = new AppState();
const calendar = new OperationalCalendar(state);
await calendar.init();
```

### Extending Modules

```javascript
// Create custom module
import { VesselManager } from './js/modules/vessel-management.js';

class CustomVesselManager extends VesselManager {
    constructor(state, storage) {
        super(state, storage);
    }
    
    // Add custom functionality
    customMethod() {
        // Your code
    }
}
```

## Development

### Adding a New Module

1. Create module file in appropriate directory
2. Export class or functions
3. Import in [`main.js`](main.js:1)
4. Initialize in app init sequence
5. Add to module registry

Example:

```javascript
// js/modules/new-feature.js
export class NewFeature {
    constructor(state, storage) {
        this.state = state;
        this.storage = storage;
    }
    
    async init() {
        console.log('NewFeature initialized');
    }
}

// js/main.js
import { NewFeature } from './modules/new-feature.js';

initModules() {
    this.modules.newFeature = new NewFeature(this.state, this.storage);
}
```

### Debugging

The application exposes helpful debugging tools:

```javascript
// In browser console
vesselScheduler.info()           // Show info
vesselScheduler.state            // Access state
vesselScheduler.modules          // Access modules
vesselScheduler.storage          // Access storage
```

## Best Practices

1. **One module per file** - Keep modules focused and small
2. **Clear exports** - Export only what's needed
3. **Async initialization** - Use async/await for setup
4. **Error handling** - Always handle errors gracefully
5. **Documentation** - Document public APIs
6. **Testing** - Write unit tests for modules
7. **Naming** - Use descriptive, consistent names

## Troubleshooting

### Module not found
- Check file path is correct
- Ensure `.js` extension is included
- Verify file exists

### Module errors
- Check browser console for details
- Verify all dependencies are loaded
- Check for circular dependencies

### Performance issues
- Use browser DevTools Performance tab
- Check network tab for slow modules
- Consider code splitting

## Resources

- [MDN: JavaScript Modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [ES6 Modules Guide](https://exploringjs.com/es6/ch_modules.html)
- [Module Best Practices](https://developers.google.com/web/fundamentals/primers/modules)

## Future Enhancements

- [ ] TypeScript support
- [ ] Hot module replacement
- [ ] Service worker caching
- [ ] Build optimization
- [ ] Tree shaking
- [ ] Dynamic imports for large modules
