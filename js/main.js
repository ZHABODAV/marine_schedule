/**
 * Main Application Entry Point
 * Vessel Scheduler System
 * Version: 4.0.0
 */

import { CONFIG } from './core/config.js';
import { AppState } from './core/app-state.js';
import { showNotification } from './core/utils.js';

// Import UI modules
import { initDashboard } from './ui/dashboard.js';
import { initFilters } from './ui/filters.js';
import { initModals } from './ui/modals.js';

// Import feature modules
import { VesselManager } from './modules/vessel-management.js';
import { CargoManager } from './modules/cargo-management.js';
import { RouteManager } from './modules/route-management.js';
import { VoyageBuilder } from './modules/voyage-builder.js';
import { TradingLanes } from './modules/trading-lanes.js';
import { FinancialAnalysis } from './modules/financial-analysis.js';
import { GanttChart } from './modules/gantt-chart.js';
import { NetworkViz } from './modules/network-viz.js';
import { OperationalCalendar } from './modules/operational-calendar.js';
import { YearScheduleManager } from './modules/year-schedule.js';
import { VesselTracking } from './modules/vessel-tracking.js';
import UnifiedDashboard from './modules/unified-dashboard.js';

// Import services
import { StorageService } from './services/storage-service.js';
import { apiClient } from './services/api-client.js';

class VesselSchedulerApp {
    constructor() {
        this.version = '4.0.0';
        this.state = new AppState();
        this.storage = new StorageService();
        this.modules = {};
        this.initialized = false;
    }

    async init() {
        if (this.initialized) {
            console.warn('Application already initialized');
            return;
        }

        try {
            console.log(` Initializing Vessel Scheduler v${this.version}...`);

            // Check required libraries
            this.checkLibraries();

            // Initialize storage
            await this.storage.init();

            // Load application state
            await this.loadState();

            // Initialize UI components
            this.initUI();

            // Initialize modules
            this.initModules();

            // Setup tab navigation
            this.setupTabNavigation();

            // Setup event listeners
            this.setupEventListeners();

            // Load initial data
            await this.loadInitialData();

            this.initialized = true;
            console.log(' Application initialized successfully');

            // Dispatch ready event
            window.dispatchEvent(new CustomEvent('vesselSchedulerReady', {
                detail: { version: this.version, app: this }
            }));

        } catch (error) {
            console.error(' Failed to initialize application:', error);
            showNotification('Failed to initialize application', 'error');
        }
    }

    checkLibraries() {
        const required = [
            { name: 'XLSX', check: () => typeof XLSX !== 'undefined' },
            { name: 'vis-network', check: () => typeof vis !== 'undefined' }
        ];

        const optional = [
            { name: 'html2pdf', check: () => typeof html2pdf !== 'undefined' },
            { name: 'Leaflet', check: () => typeof L !== 'undefined' }
        ];

        const missing = required.filter(lib => !lib.check());
        if (missing.length > 0) {
            console.error(' Missing required libraries:', missing.map(l => l.name));
            throw new Error(`Missing required libraries: ${missing.map(l => l.name).join(', ')}`);
        }

        const missingOptional = optional.filter(lib => !lib.check());
        if (missingOptional.length > 0) {
            console.warn(' Missing optional libraries:', missingOptional.map(l => l.name));
        }

        console.log(' All required libraries loaded');
    }

    async loadState() {
        try {
            const savedState = await this.storage.getItem('appState');
            if (savedState) {
                this.state.restore(savedState);
                console.log(' Application state loaded from storage');
            }
        } catch (error) {
            console.warn('Could not load saved state:', error);
        }
    }

    initUI() {
        console.log(' Initializing UI components...');
        
        // Initialize dashboard
        if (document.getElementById('dashboard')) {
            initDashboard(this.state);
        }

        // Initialize filters
        initFilters(this.state);

        // Initialize modals
        initModals(this.state);

        console.log(' UI components initialized');
    }

    initModules() {
        console.log(' Initializing feature modules...');

        // Initialize unified dashboard
        this.modules.unifiedDashboard = UnifiedDashboard;

        // Initialize vessel management
        this.modules.vessels = new VesselManager(this.state, this.storage);

        // Initialize cargo management
        this.modules.cargo = new CargoManager(this.state, this.storage);

        // Initialize route management
        this.modules.routes = new RouteManager(this.state, this.storage);

        // Initialize voyage builder
        this.modules.voyageBuilder = new VoyageBuilder(this.state, this.storage);

        // Initialize trading lanes
        this.modules.tradingLanes = new TradingLanes(this.state, this.storage);

        // Initialize financial analysis
        this.modules.financial = new FinancialAnalysis(this.state, this.storage);

        // Initialize Gantt chart
        this.modules.gantt = new GanttChart(this.state);

        // Initialize network visualization
        this.modules.network = new NetworkViz(this.state);

        // Initialize operational calendar
        if (document.getElementById('operationalCalendar')) {
            this.modules.calendar = new OperationalCalendar(this.state, this.storage);
        }

        // Initialize year schedule
        this.modules.yearSchedule = new YearScheduleManager(this.state, this.storage);

        // Initialize vessel tracking
        if (document.getElementById('vessel-tracking')) {
            this.modules.tracking = new VesselTracking({
                containerId: 'vessel-tracking',
                apiEndpoint: '/api/vessels/tracking',
                mapProvider: 'leaflet',
                updateInterval: 60000
            });
        }

        console.log(' Feature modules initialized');
    }

    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.getAttribute('data-tab');
                
                // Update active tab button
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                // Update active tab content
                tabContents.forEach(content => content.classList.remove('active'));
                const targetContent = document.getElementById(tabId);
                if (targetContent) {
                    targetContent.classList.add('active');
                    
                    // Trigger module initialization if needed
                    this.onTabChange(tabId);
                }
            });
        });
    }

    onTabChange(tabId) {
        // Initialize module-specific components when tab is activated
        switch(tabId) {
            case 'dashboard':
                this.modules.unifiedDashboard?.render();
                break;
            case 'schedule':
                this.modules.gantt?.refresh();
                break;
            case 'network':
                this.modules.network?.render();
                break;
            case 'operationalCalendar':
                this.modules.calendar?.render();
                break;
            case 'financialAnalysis':
                this.modules.financial?.refresh();
                break;
            case 'tracking':
                this.modules.tracking?.init();
                break;
        }
    }

    setupEventListeners() {
        // Global event listeners
        
        // Module selector change
        const moduleSelector = document.getElementById('moduleSelector');
        if (moduleSelector) {
            moduleSelector.addEventListener('change', (e) => {
                this.state.setCurrentModule(e.target.value);
                this.refreshActiveModule();
            });
        }

        // Save state periodically
        setInterval(() => {
            this.saveState();
        }, 30000); // Every 30 seconds

        // Save state before page unload
        window.addEventListener('beforeunload', () => {
            this.saveState();
        });
    }

    async loadInitialData() {
        console.log(' Loading initial data...');

        try {
            // Try to load from API first
            try {
                const [vesselsRes, cargoRes, routesRes] = await Promise.all([
                    apiClient.getVessels(),
                    apiClient.getCargo(),
                    apiClient.getRoutes()
                ]);

                if (vesselsRes.success) {
                    this.state.setVessels(vesselsRes.data.vessels || []);
                } else {
                    // Fallback to storage
                    const vessels = await this.storage.getItem('vessels') || [];
                    this.state.setVessels(vessels);
                }

                if (cargoRes.success) {
                    this.state.setCargo(cargoRes.data.cargo || []);
                } else {
                    const cargo = await this.storage.getItem('cargo') || [];
                    this.state.setCargo(cargo);
                }

                if (routesRes.success) {
                    this.state.setRoutes(routesRes.data.routes || []);
                } else {
                    const routes = await this.storage.getItem('routes') || [];
                    this.state.setRoutes(routes);
                }

            } catch (apiError) {
                console.warn('API load failed, falling back to storage:', apiError);
                
                // Fallback to storage
                const vessels = await this.storage.getItem('vessels') || [];
                this.state.setVessels(vessels);

                const cargo = await this.storage.getItem('cargo') || [];
                this.state.setCargo(cargo);

                const routes = await this.storage.getItem('routes') || [];
                this.state.setRoutes(routes);
            }

            console.log(` Loaded: ${this.state.vessels.length} vessels, ${this.state.cargo.length} cargo, ${this.state.routes.length} routes`);
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    async saveState() {
        try {
            await this.storage.setItem('appState', this.state.export());
        } catch (error) {
            console.error('Failed to save state:', error);
        }
    }

    refreshActiveModule() {
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab) {
            this.onTabChange(activeTab.id);
        }
    }

    // Public API methods
    getModule(name) {
        return this.modules[name];
    }

    getState() {
        return this.state;
    }

    getStorage() {
        return this.storage;
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    const app = new VesselSchedulerApp();
    await app.init();
    
    // Make app globally accessible
    window.vesselSchedulerApp = app;
    
    // Expose useful globals for console debugging
    window.vesselScheduler = {
        version: app.version,
        app: app,
        state: app.state,
        storage: app.storage,
        modules: app.modules,
        
        info() {
            console.log(`
═══════════════════════════════════════════════
    Vessel Scheduler v${app.version}
═══════════════════════════════════════════════

Available Commands:
  vesselScheduler.info()              - Show this info
  vesselScheduler.state               - Access application state
  vesselScheduler.modules             - Access feature modules
  vesselScheduler.storage             - Access storage service
  
Loaded Modules:
  ${Object.keys(app.modules).map(m => ` ${m}`).join('\n  ')}

═══════════════════════════════════════════════
            `);
        }
    };
    
    console.log(' Type `vesselScheduler.info()` in console for available commands');
});

// Handle errors
window.addEventListener('error', (event) => {
    console.error('Application error:', event.error);
    showNotification('An error occurred. Check console for details.', 'error');
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showNotification('An error occurred. Check console for details.', 'error');
});

export default VesselSchedulerApp;
