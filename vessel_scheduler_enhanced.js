// ===== VESSEL SCHEDULER ENHANCED - MAIN ORCHESTRATOR =====
// Version 4.0.0 - Modular architecture with imports

// ===== MODULE IMPORTS =====
// Import all modular functionality
import { cargoManagement } from './js/modules/cargo-management.js';
import { vesselManagement } from './js/modules/vessel-management.js';
import { routeManagement } from './js/modules/route-management.js';
import { voyageBuilder } from './js/modules/voyage-builder.js';
import { scheduleGenerator } from './js/modules/schedule-generator.js';
import { ganttChart } from './js/modules/gantt-chart.js';
import { networkViz } from './js/modules/network-viz.js';
import { financialAnalysis } from './js/modules/financial-analysis.js';
import { operationalCalendar } from './js/modules/operational-calendar.js';
import { tradingLanes } from './js/modules/trading-lanes.js';
import { unifiedDashboard } from './js/modules/unified-dashboard.js';
import { tableRenderers } from './js/modules/table-renderers.js';
import { crudOperations } from './js/modules/crud-operations.js';
import { exportFunctions } from './js/modules/exports.js';

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
            routeLegs: []
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

// ===== MODULE ORCHESTRATOR =====
class ModuleOrchestrator {
    constructor() {
        this.modules = {
            cargo: cargoManagement,
            vessel: vesselManagement,
            route: routeManagement,
            voyage: voyageBuilder,
            schedule: scheduleGenerator,
            gantt: ganttChart,
            network: networkViz,
            financial: financialAnalysis,
            calendar: operationalCalendar,
            tradingLanes: tradingLanes,
            dashboard: unifiedDashboard,
            tables: tableRenderers,
            crud: crudOperations,
            exports: exportFunctions
        };

        this.initialized = false;
    }

    // Initialize all modules
    async initialize() {
        console.log(' Initializing Module Orchestrator...');

        try {
            // Initialize each module in sequence
            for (const [name, module] of Object.entries(this.modules)) {
                if (module && typeof module.init === 'function') {
                    console.log(`   Initializing ${name} module...`);
                    await module.init(appState, appConfig);
                }
            }

            this.initialized = true;
            console.log(' All modules initialized successfully');
            return true;
        } catch (error) {
            console.error(' Module initialization failed:', error);
            showNotification('Module initialization failed: ' + error.message, 'error');
            return false;
        }
    }

    // Get module by name
    getModule(moduleName) {
        return this.modules[moduleName];
    }

    // Execute module function
    async execute(moduleName, functionName, ...args) {
        const module = this.modules[moduleName];
        if (!module) {
            throw new Error(`Module "${moduleName}" not found`);
        }

        if (typeof module[functionName] !== 'function') {
            throw new Error(`Function "${functionName}" not found in module "${moduleName}"`);
        }

        return await module[functionName](...args);
    }

    // Reload specific module
    async reloadModule(moduleName) {
        const module = this.modules[moduleName];
        if (module && typeof module.reload === 'function') {
            await module.reload(appState, appConfig);
        }
    }
}

// Create global orchestrator instance
const orchestrator = new ModuleOrchestrator();

// ===== HELPER FUNCTIONS =====
function getCurrentData() {
    return appState[appState.currentModule];
}

function updateCSSVariables() {
    const colors = appConfig.gantt.colors;
    const root = document.documentElement;
    
    const fmt = (c) => c.startsWith('#') ? c : '#' + c;

    if (colors.loading) root.style.setProperty('--operation-loading', fmt(colors.loading));
    if (colors.discharge) root.style.setProperty('--operation-discharge', fmt(colors.discharge));
    if (colors.sea_laden) root.style.setProperty('--operation-transit', fmt(colors.sea_laden));
    if (colors.sea_ballast) root.style.setProperty('--operation-ballast', fmt(colors.sea_ballast));
    if (colors.canal) root.style.setProperty('--operation-canal', fmt(colors.canal));
    if (colors.bunker) root.style.setProperty('--operation-bunker', fmt(colors.bunker));
    if (colors.waiting) root.style.setProperty('--operation-waiting', fmt(colors.waiting));
}

function toNumber(v) {
    if (v === null || v === undefined) return 0;
    const s = String(v).trim();
    if (!s) return 0;
    const n = Number(s.replace(',', '.'));
    return Number.isFinite(n) ? n : 0;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {year: 'numeric', month: 'short', day: 'numeric'});
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        padding: 1rem 1.5rem;
        background-color: ${type === 'success' ? 'var(--accent-success)' : type === 'info' ? 'var(--accent-primary)' : 'var(--accent-danger)'};
        color: white;
        border-radius: 6px;
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
        font-weight: 500;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async function() {
    console.log(' Vessel Scheduler Enhanced v4.0.0 - Starting...');

    // Initialize orchestrator
    const success = await orchestrator.initialize();
    
    if (!success) {
        showNotification('Failed to initialize modules. Check console for details.', 'error');
        return;
    }

    // Load config from server
    fetch('/api/config')
        .then(r => r.json())
        .then(config => {
            if (config && config.gantt) {
                appConfig = config;
                updateCSSVariables();
                initializeOpTypeFilters();
            }
        })
        .catch(e => console.warn('Could not load config from server:', e));

    // Initialize UI components
    initializeTabs();
    initializeFilters();
    initializeOpTypeFilters();

    // Load data from local storage or sample
    const loaded = loadFromLocalStorage();
    if (!loaded) {
        loadSampleData();
    }
    
    updateSessionInfo();
    setInterval(updateSessionInfo, 60000);

    // Sync with server data
    syncServerData();

    // Setup form handlers
    setupFormHandlers();
    populateFilterDropdowns();

    // Update module display
    updateModuleDisplay();

    console.log(' Application initialized successfully');
});

// ===== SYNC WITH SERVER =====
async function syncServerData() {
    try {
        // Sync vessels
        const vesselsData = await fetch('/api/vessels').then(r => r.json());
        if (vesselsData.vessels && vesselsData.vessels.length > 0) {
            console.log('Loaded vessels from server:', vesselsData.vessels.length);
            appState.vessels = vesselsData.vessels;
            await orchestrator.execute('tables', 'renderVesselsTable', appState);
            await orchestrator.execute('vessel', 'renderVesselDashboard', appState);
        }

        // Sync cargo
        const cargoData = await fetch('/api/cargo').then(r => r.json());
        if (cargoData.cargo && cargoData.cargo.length > 0) {
            console.log('Loaded cargo from server:', cargoData.cargo.length);
            appState.cargo = cargoData.cargo;
            await orchestrator.execute('tables', 'renderCargoTable', appState);
        }

        updateDashboard();
        populateFilterDropdowns();
    } catch (error) {
        console.warn('Error syncing with server:', error);
    }
}

// ===== TAB NAVIGATION =====
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

async function switchTab(tabName) {
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName)?.classList.add('active');

    // Tab specific initialization using modules
    switch (tabName) {
        case 'dashboard':
            updateDashboard();
            await orchestrator.execute('dashboard', 'render', appState);
            break;
        case 'voyageBuilder':
            await orchestrator.execute('voyage', 'initialize', appState);
            break;
        case 'tradingLanes':
            await orchestrator.execute('tradingLanes', 'render', appState);
            break;
        case 'vesselCargoAssignment':
            await orchestrator.execute('vessel', 'renderCargoAssignments', appState);
            break;
        case 'yearSchedule':
            const startDateEl = document.getElementById('yearScheduleStartDate');
            if (startDateEl && !startDateEl.value) {
                startDateEl.value = '2026-01-01';
            }
            break;
        case 'operationalCalendar':
            await orchestrator.execute('calendar', 'render', appState);
            break;
        case 'financialAnalysis':
            if (appState.cargo.length > 0) {
                await orchestrator.execute('financial', 'calculate', appState);
            }
            break;
        case 'networkVisualization':
            await orchestrator.execute('network', 'render', appState);
            break;
    }
}

// ===== FILTERS =====
function initializeFilters() {
    const filterModule = document.getElementById('filterModule');
    if (filterModule) {
        filterModule.value = appState.filters.module || '';
    }
}

function initializeOpTypeFilters() {
    const container = document.getElementById('opTypeFilters');
    if (!container) return;

    const opTypes = [
        { id: 'loading', label: 'П', color: 'var(--operation-loading)' },
        { id: 'discharge', label: 'В', color: 'var(--operation-discharge)' },
        { id: 'transit', label: 'Т', color: 'var(--operation-transit)' },
        { id: 'ballast', label: 'Б', color: 'var(--operation-ballast)' },
        { id: 'canal', label: 'К', color: 'var(--operation-canal)' },
        { id: 'bunker', label: 'Ф', color: 'var(--operation-bunker)' },
        { id: 'waiting', label: 'О', color: 'var(--operation-waiting)' }
    ];

    container.innerHTML = opTypes.map(op => `
        <label style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; background-color: var(--bg-tertiary); border-radius: 4px; cursor: pointer;">
            <input type="checkbox" value="${op.id}" onchange="updateOpTypeFilters()" style="cursor: pointer;">
            <span style="display: inline-block; width: 1.5rem; height: 1.5rem; background-color: ${op.color}; border-radius: 4px; text-align: center; color: white; line-height: 1.5rem; font-weight: 700;">${op.label}</span>
        </label>
    `).join('');
}

function updateOpTypeFilters() {
    const checkboxes = document.querySelectorAll('#opTypeFilters input[type="checkbox"]');
    appState.filters.opTypes = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);
}

function populateFilterDropdowns() {
    // Delegate to modules
    orchestrator.execute('tables', 'populateFilterDropdowns', appState).catch(console.error);
}

function applyFilters() {
    appState.filters.module = document.getElementById('filterModule').value;
    appState.filters.dateStart = document.getElementById('filterDateStart').value;
    appState.filters.dateEnd = document.getElementById('filterDateEnd').value;
    appState.filters.product = document.getElementById('filterProduct').value;
    appState.filters.port = document.getElementById('filterPort').value;
    appState.filters.vesselId = document.getElementById('filterVessel').value;

    // Re-render all affected views
    orchestrator.execute('tables', 'renderVesselsTable', appState);
    orchestrator.execute('tables', 'renderCargoTable', appState);
    orchestrator.execute('tables', 'renderRoutesTable', appState);
    updateDashboard();
    
    showNotification('Фильтры применены', 'success');
}

function resetFilters() {
    appState.filters = {
        module: '',
        dateStart: null,
        dateEnd: null,
        product: null,
        port: null,
        vesselId: null,
        opTypes: []
    };

    document.getElementById('filterModule').value = '';
    document.getElementById('filterDateStart').value = '';
    document.getElementById('filterDateEnd').value = '';
    document.getElementById('filterProduct').value = '';
    document.getElementById('filterPort').value = '';
    document.getElementById('filterVessel').value = '';

    document.querySelectorAll('#opTypeFilters input[type="checkbox"]').forEach(cb => cb.checked = false);

    applyFilters();
    showNotification('Фильтры сброшены', 'info');
}

// ===== MODULE SWITCHING =====
function switchModule() {
    const selector = document.getElementById('moduleSelector');
    appState.currentModule = selector.value;
    updateModuleDisplay();
    
    orchestrator.execute('tables', 'renderVesselsTable', appState);
    orchestrator.execute('tables', 'renderCargoTable', appState);
    orchestrator.execute('tables', 'renderRoutesTable', appState);
    updateDashboard();
    populateFilterDropdowns();
    
    showNotification(`Переключено на модуль: ${selector.options[selector.selectedIndex].text}`, 'success');
}

function updateModuleDisplay() {
    const selector = document.getElementById('moduleSelector');
    const moduleName = selector.options[selector.selectedIndex].text;
    
    const scheduleModuleEl = document.getElementById('scheduleModule');
    const currentModuleNameEl = document.getElementById('currentModuleName');
    if (scheduleModuleEl) scheduleModuleEl.textContent = moduleName;
    if (currentModuleNameEl) currentModuleNameEl.textContent = moduleName;
}

// ===== DASHBOARD =====
async function updateDashboard() {
    try {
        await orchestrator.execute('dashboard', 'update', appState);
    } catch (error) {
        console.error('Dashboard update failed:', error);
    }
}

// ===== FORM HANDLERS =====
function setupFormHandlers() {
    orchestrator.execute('crud', 'setupFormHandlers', appState).catch(console.error);
}

// ===== WRAPPER FUNCTIONS FOR GLOBAL ACCESS =====
// These functions delegate to modules while maintaining backward compatibility

// Vessel functions
window.addVessel = () => orchestrator.execute('vessel', 'add', appState);
window.editVessel = (id) => orchestrator.execute('vessel', 'edit', appState, id);
window.deleteVessel = (id) => orchestrator.execute('vessel', 'delete', appState, id);

// Cargo functions
window.addCargo = () => orchestrator.execute('cargo', 'add', appState);
window.editCargo = (id) => orchestrator.execute('cargo', 'edit', appState, id);
window.deleteCargo = (id) => orchestrator.execute('cargo', 'delete', appState, id);

// Route functions
window.addRoute = () => orchestrator.execute('route', 'add', appState);
window.deleteRoute = (idx) => orchestrator.execute('route', 'delete', appState, idx);
window.transferRouteToBuilder = (idx) => orchestrator.execute('route', 'transferToBuilder', appState, idx);

// Schedule functions
window.generateSchedule = () => orchestrator.execute('schedule', 'generate', appState);
window.generateYearSchedule = () => orchestrator.execute('schedule', 'generateYear', appState);

// Gantt functions
window.exportGantt = () => orchestrator.execute('exports', 'gantt', appState);
window.exportFleetOverview = () => orchestrator.execute('exports', 'fleetOverview', appState);

// Network functions
window.renderNetwork = () => orchestrator.execute('network', 'render', appState);
window.exportNetworkSnapshot = () => orchestrator.execute('exports', 'networkSnapshot', appState);

// Financial functions
window.calculateFinancialAnalysis = () => orchestrator.execute('financial', 'calculate', appState);
window.optimizeBunkerStrategy = () => orchestrator.execute('financial', 'optimizeBunker', appState);

// Operational Calendar
window.renderOperationalCalendar = () => orchestrator.execute('calendar', 'render', appState);

// Trading Lanes
window.generateTradingLanes = () => orchestrator.execute('tradingLanes', 'generate', appState);
window.renderTradingLanes = () => orchestrator.execute('tradingLanes', 'render', appState);

// Voyage Builder
window.addVoyageLeg = () => orchestrator.execute('voyage', 'addLeg', appState);
window.validateVoyage = () => orchestrator.execute('voyage', 'validate', appState);
window.saveVoyageTemplate = () => orchestrator.execute('voyage', 'saveTemplate', appState);

// Global utility functions
window.switchModule = switchModule;
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;
window.switchTab = switchTab;
window.showNotification = showNotification;
window.getCurrentData = getCurrentData;
window.toNumber = toNumber;
window.formatDate = formatDate;

// ===== LOCAL STORAGE =====
function saveToLocalStorage() {
    const storageData = {
        ...appState,
        sessionInfo: {
            lastSaved: new Date().toISOString(),
            version: '4.0.0'
        }
    };
    
    try {
        localStorage.setItem('vesselSchedulerDataEnhanced', JSON.stringify(storageData));
        console.log('Session saved successfully:', new Date().toISOString());
        updateSessionInfo();
    } catch (error) {
        console.error('Error saving to localStorage:', error);
        showNotification('Ошибка сохранения сессии', 'error');
    }
}

function loadFromLocalStorage() {
    const data = localStorage.getItem('vesselSchedulerDataEnhanced');
    if (!data) return false;

    try {
        const loaded = JSON.parse(data);
        
        appState.currentModule = loaded.currentModule || 'deepsea';
        appState.deepsea = loaded.deepsea || appState.deepsea;
        appState.balakovo = loaded.balakovo || appState.balakovo;
        appState.olya = loaded.olya || appState.olya;
        appState.filters = loaded.filters || appState.filters;
        appState.voyageBuilder = loaded.voyageBuilder || appState.voyageBuilder;
        appState.portStocks = loaded.portStocks || {};
        appState.salesPlan = loaded.salesPlan || appState.salesPlan;

        orchestrator.execute('tables', 'renderVesselsTable', appState);
        orchestrator.execute('tables', 'renderCargoTable', appState);
        orchestrator.execute('tables', 'renderRoutesTable', appState);
        updateDashboard();

        return true;
    } catch (e) {
        console.error('Failed to load local storage state', e);
        return false;
    }
}

function updateSessionInfo() {
    const sessionInfoEl = document.getElementById('sessionInfo');
    if (!sessionInfoEl) return;
    
    const saved = localStorage.getItem('vesselSchedulerDataEnhanced');
    if (!saved) {
        sessionInfoEl.innerHTML = ' Нет сохраненной сессии';
        return;
    }
    
    try {
        const data = JSON.parse(saved);
        const lastSaved = data.sessionInfo?.lastSaved;
        
        if (lastSaved) {
            const savedDate = new Date(lastSaved);
            const now = new Date();
            const diffMinutes = Math.floor((now - savedDate) / (1000 * 60));
            
            let timeText = '';
            if (diffMinutes < 1) {
                timeText = 'только что';
            } else if (diffMinutes < 60) {
                timeText = `${diffMinutes} мин. назад`;
            } else if (diffMinutes < 1440) {
                const hours = Math.floor(diffMinutes / 60);
                timeText = `${hours} ч. назад`;
            } else {
                timeText = savedDate.toLocaleDateString('ru-RU');
            }
            
            sessionInfoEl.innerHTML = ` Сессия сохранена: ${timeText} | Модуль: ${data.currentModule || 'deepsea'}`;
        } else {
            sessionInfoEl.innerHTML = ' Сессия сохранена';
        }
    } catch (e) {
        sessionInfoEl.innerHTML = ' Ошибка чтения сессии';
    }
}

// ===== SAMPLE DATA =====
function loadSampleData() {
    appState.vessels = [
        {id: 'V001', name: 'Atlantic Star', class: 'Handysize', dwt: 35000, speed: 14, status: 'Active'},
        {id: 'V002', name: 'Pacific Dawn', class: 'Panamax', dwt: 75000, speed: 15, status: 'Active'},
        {id: 'V003', name: 'Baltic Voyager', class: 'Handymax', dwt: 52000, speed: 14, status: 'Active'},
        {id: 'V004', name: 'Mediterranean Queen', class: 'Supramax', dwt: 58000, speed: 14.5, status: 'Pending'}
    ];

    appState.cargo = [
        {id: 'C001', commodity: 'Grain', quantity: 50000, loadPort: 'Houston', dischPort: 'Rotterdam', laycanStart: '2025-01-15', laycanEnd: '2025-01-20', status: 'Pending'},
        {id: 'C002', commodity: 'Coal', quantity: 70000, loadPort: 'Newcastle', dischPort: 'Singapore', laycanStart: '2025-01-18', laycanEnd: '2025-01-22', status: 'Assigned'},
        {id: 'C003', commodity: 'Iron Ore', quantity: 60000, loadPort: 'Port Hedland', dischPort: 'Qingdao', laycanStart: '2025-01-20', laycanEnd: '2025-01-25', status: 'Pending'},
        {id: 'C004', commodity: 'Wheat', quantity: 45000, loadPort: 'Vancouver', dischPort: 'Yokohama', laycanStart: '2025-01-22', laycanEnd: '2025-01-27', status: 'Completed'}
    ];

    appState.routes = [
        {from: 'Houston', to: 'Rotterdam', distance: 4800, canal: ''},
        {from: 'Newcastle', to: 'Singapore', distance: 3900, canal: ''},
        {from: 'Port Hedland', to: 'Qingdao', distance: 2800, canal: ''},
        {from: 'Vancouver', to: 'Yokohama', distance: 4200, canal: ''}
    ];

    appState.ports = [
        {name: 'Houston', country: 'USA', loadRate: 5000, dischRate: 7000},
        {name: 'Rotterdam', country: 'Netherlands', loadRate: 6000, dischRate: 8000},
        {name: 'Singapore', country: 'Singapore', loadRate: 7000, dischRate: 9000},
        {name: 'Qingdao', country: 'China', loadRate: 8000, dischRate: 10000}
    ];

    orchestrator.execute('tables', 'renderVesselsTable', appState);
    orchestrator.execute('tables', 'renderCargoTable', appState);
    orchestrator.execute('tables', 'renderRoutesTable', appState);
    orchestrator.execute('vessel', 'renderVesselDashboard', appState);
    populateFilterDropdowns();
}

// Auto-save every 30 seconds
setInterval(saveToLocalStorage, 30000);

// Export orchestrator for debugging
window.orchestrator = orchestrator;
window.appState = appState;
window.appConfig = appConfig;
