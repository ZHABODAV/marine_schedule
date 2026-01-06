/**
 * Application State Management
 * Centralized state object for the Vessel Scheduler application
 * @module core/app-state
 */

// ===== APPLICATION STATE =====
let appConfig = {
    gantt: {
        colors: {
            loading: '#92D050',
            discharge: '#00B0F0',
            sea_laden: '#FFC000',
            sea_ballast: '#D9D9D9',
            canal: '#7030A0',
            bunker: '#833C0C',
            waiting: '#FF0000'
        }
    }
};

const appState = {
    currentModule: 'deepsea',
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
            routeLegs: [] // RouteLeg catalog
        }
    },
    balakovo: {
        masters: { ports: [], routes: [], vessels: [], cargoTypes: [] },
        planning: { commitments: [], railCargo: [], movements: [], voyageLegs: [] },
        computed: { voyages: [], voyageTemplates: [], scenarios: [], schedule: null, ganttData: [], routeLegs: [] }
    },
    olya: {
        masters: { ports: [], routes: [], vessels: [], cargoTypes: [] },
        planning: { commitments: [], railCargo: [], movements: [], voyageLegs: [] },
        computed: { voyages: [], voyageTemplates: [], scenarios: [], schedule: null, ganttData: [], routeLegs: [] }
    },

    // Global filters
    filters: {
        module: '',
        dateStart: null,
        dateEnd: null,
        product: null,
        port: null,
        vesselId: null,
        opTypes: []
    },

    // Cross-filters for unified panel
    crossFilters: {
        cargo: null,
        vessel: null,
        voyage: null,
        route: null
    },

    // Runtime state for voyage builder
    voyageBuilder: {
        currentLegs: [],
        lastValidation: null
    },

    // Port stock accumulators
    portStocks: {},

    // Sales plan inputs
    salesPlan: {
        targetShipments: 0,
        periodStart: null,
        periodEnd: null
    }
};

// ===== TRADING LANES STATE =====
const tradingLanesState = {
    lanes: [],
    assignments: new Map() // Map<cargoId, { vesselId, laneId, status }>
};

// Legacy getters for backward compatibility
Object.defineProperty(appState, 'vessels', {
    get() { return this[this.currentModule].masters.vessels; },
    set(val) { this[this.currentModule].masters.vessels = val; }
});

Object.defineProperty(appState, 'cargo', {
    get() { return this[this.currentModule].planning.commitments; },
    set(val) { this[this.currentModule].planning.commitments = val; }
});

Object.defineProperty(appState, 'routes', {
    get() { return this[this.currentModule].masters.routes; },
    set(val) { this[this.currentModule].masters.routes = val; }
});

Object.defineProperty(appState, 'ports', {
    get() { return this[this.currentModule].masters.ports; },
    set(val) { this[this.currentModule].masters.ports = val; }
});

Object.defineProperty(appState, 'schedule', {
    get() { return this[this.currentModule].computed.schedule; },
    set(val) { this[this.currentModule].computed.schedule = val; }
});

Object.defineProperty(appState, 'ganttData', {
    get() { return this[this.currentModule].computed.ganttData; },
    set(val) { this[this.currentModule].computed.ganttData = val; }
});

/**
 * Get current module data
 * @returns {Object} Current module's data object
 */
function getCurrentData() {
    return appState[appState.currentModule];
}

// Export state objects
export { appConfig, appState, tradingLanesState, getCurrentData };
