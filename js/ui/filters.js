// ===== FILTERS MODULE =====
// Global and operation-type filtering functionality

import { appState } from '../core/app-state.js';
import { showNotification } from '../core/utils.js';

/**
 * Initialize filter controls
 */
export function initializeFilters() {
    const filterModule = document.getElementById('filterModule');
    if (filterModule) {
        filterModule.value = appState.filters.module || '';
    }
}

/**
 * Initialize operation type filter checkboxes
 */
export function initializeOpTypeFilters() {
    const container = document.getElementById('opTypeFilters');
    if (!container) return;

    // Use CSS variables which are updated from config
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

/**
 * Update operation type filters based on checkbox state
 */
export function updateOpTypeFilters() {
    const checkboxes = document.querySelectorAll('#opTypeFilters input[type="checkbox"]');
    appState.filters.opTypes = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);
}

/**
 * Populate filter dropdown controls with current data
 */
export function populateFilterDropdowns() {
    // Product filter
    const productFilter = document.getElementById('filterProduct');
    if (productFilter) {
        const products = [...new Set(appState.cargo.map(c => c.commodity))].filter(Boolean);
        productFilter.innerHTML = '<option value="">Все продукты</option>' +
            products.map(p => `<option value="${p}">${p}</option>`).join('');
    }

    // Port filter
    const portFilter = document.getElementById('filterPort');
    if (portFilter) {
        const ports = [...new Set(appState.ports.map(p => p.name))].filter(Boolean);
        portFilter.innerHTML = '<option value="">Все порты</option>' +
            ports.map(p => `<option value="${p}">${p}</option>`).join('');
    }

    // Vessel filter
    const vesselFilter = document.getElementById('filterVessel');
    if (vesselFilter) {
        const vessels = appState.vessels.map(v => v.id).filter(Boolean);
        vesselFilter.innerHTML = '<option value="">Все суда</option>' +
            vessels.map(v => `<option value="${v}">${v}</option>`).join('');
    }

    // Port stock select
    const portStockSelect = document.getElementById('portStockSelect');
    if (portStockSelect) {
        const ports = [...new Set(appState.ports.map(p => p.name))].filter(Boolean);
        portStockSelect.innerHTML = '<option value="">Выберите порт...</option>' +
            ports.map(p => `<option value="${p}">${p}</option>`).join('');
    }
}

/**
 * Apply current filter settings and update views
 */
export function applyFilters() {
    appState.filters.module = document.getElementById('filterModule').value;
    appState.filters.dateStart = document.getElementById('filterDateStart').value;
    appState.filters.dateEnd = document.getElementById('filterDateEnd').value;
    appState.filters.product = document.getElementById('filterProduct').value;
    appState.filters.port = document.getElementById('filterPort').value;
    appState.filters.vesselId = document.getElementById('filterVessel').value;

    // Re-render all affected views (handled by calling code)
    showNotification('Фильтры применены', 'success');
}

/**
 * Reset all filters to default values
 */
export function resetFilters() {
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

    // Uncheck all operation type filters
    document.querySelectorAll('#opTypeFilters input[type="checkbox"]').forEach(cb => cb.checked = false);

    showNotification('Фильтры сброшены', 'info');
}

/**
 * Apply filters to a dataset
 * @param {Array} data - Array of items to filter
 * @returns {Array} Filtered array
 */
export function applyFiltersToData(data) {
    let filtered = [...data];

    if (appState.filters.dateStart) {
        const startDate = new Date(appState.filters.dateStart);
        filtered = filtered.filter(item => {
            const itemDate = new Date(item.laycanStart || item.date || item.start);
            return itemDate >= startDate;
        });
    }

    if (appState.filters.dateEnd) {
        const endDate = new Date(appState.filters.dateEnd);
        filtered = filtered.filter(item => {
            const itemDate = new Date(item.laycanEnd || item.date || item.end);
            return itemDate <= endDate;
        });
    }

    if (appState.filters.product) {
        filtered = filtered.filter(item => item.commodity === appState.filters.product);
    }

    if (appState.filters.port) {
        filtered = filtered.filter(item => 
            item.loadPort === appState.filters.port || item.dischPort === appState.filters.port
        );
    }

    if (appState.filters.vesselId) {
        filtered = filtered.filter(item => item.vesselId === appState.filters.vesselId || item.vessel === appState.filters.vesselId);
    }

    return filtered;
}
