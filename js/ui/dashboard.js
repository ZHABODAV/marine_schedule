// ===== DASHBOARD MODULE =====
// Dashboard display and cross-filtering functionality

import { appState, getCurrentData } from '../core/app-state.js';
import { applyFiltersToData } from './filters.js';
import { formatDate } from '../core/utils.js';

/**
 * Update dashboard summary statistics
 */
export function updateDashboard() {
    const filteredVessels = applyFiltersToData(appState.vessels);
    const filteredCargo = applyFiltersToData(appState.cargo);
    const data = getCurrentData();
    
    const activeVessels = filteredVessels.filter(v => v.status === 'Active').length;
    const pendingCargo = filteredCargo.filter(c => c.status === 'Pending').length;
    const activeVoyages = (data.computed.voyages || []).filter(v => v.status === 'active' || v.status === 'planned').length;
    const utilization = Math.round((activeVessels / Math.max(filteredVessels.length, 1)) * 100);
    
    document.getElementById('activeVessels').textContent = activeVessels;
    document.getElementById('pendingCargo').textContent = pendingCargo;
    const activeVoyagesEl = document.getElementById('activeVoyages');
    if (activeVoyagesEl) activeVoyagesEl.textContent = activeVoyages;
    document.getElementById('utilization').textContent = utilization + '%';
    
    // Update cross-filter dropdowns
    populateCrossFilterDropdowns();
    
    // Render unified panel if on dashboard
    if (document.getElementById('dashboard')?.classList.contains('active')) {
        renderUnifiedPanel();
    }
}

/**
 * Populate cross-filter dropdown controls
 */
export function populateCrossFilterDropdowns() {
    const data = getCurrentData();
    
    // Cargo filter
    const cargoFilter = document.getElementById('crossFilterCargo');
    if (cargoFilter) {
        const cargos = appState.cargo;
        cargoFilter.innerHTML = '<option value="">Все грузы</option>' +
            cargos.map(c => `<option value="${c.id}">${c.id} - ${c.commodity} (${c.quantity} MT)</option>`).join('');
        if (appState.crossFilters.cargo) {
            cargoFilter.value = appState.crossFilters.cargo;
        }
    }
    
    // Vessel filter
    const vesselFilter = document.getElementById('crossFilterVessel');
    if (vesselFilter) {
        const vessels = appState.vessels;
        vesselFilter.innerHTML = '<option value="">Все суда</option>' +
            vessels.map(v => `<option value="${v.id}">${v.name} (${v.class})</option>`).join('');
        if (appState.crossFilters.vessel) {
            vesselFilter.value = appState.crossFilters.vessel;
        }
    }
    
    // Voyage filter
    const voyageFilter = document.getElementById('crossFilterVoyage');
    if (voyageFilter) {
        const voyages = data.computed.voyages || [];
        voyageFilter.innerHTML = '<option value="">Все рейсы</option>' +
            voyages.map(v => `<option value="${v.id}">${v.id}</option>`).join('');
        if (appState.crossFilters.voyage) {
            voyageFilter.value = appState.crossFilters.voyage;
        }
    }
    
    // Route filter
    const routeFilter = document.getElementById('crossFilterRoute');
    if (routeFilter) {
        const routes = appState.routes;
        routeFilter.innerHTML = '<option value="">Все маршруты</option>' +
            routes.map((r, idx) => `<option value="${idx}">${r.from} → ${r.to}</option>`).join('');
        if (appState.crossFilters.route) {
            routeFilter.value = appState.crossFilters.route;
        }
    }
}

/**
 * Apply cross-filters and update related dropdowns
 */
export function applyCrossFilters() {
    appState.crossFilters.cargo = document.getElementById('crossFilterCargo')?.value || null;
    appState.crossFilters.vessel = document.getElementById('crossFilterVessel')?.value || null;
    appState.crossFilters.voyage = document.getElementById('crossFilterVoyage')?.value || null;
    appState.crossFilters.route = document.getElementById('crossFilterRoute')?.value || null;
    
    // Auto-populate related filters
    if (appState.crossFilters.cargo) {
        const cargo = appState.cargo.find(c => c.id === appState.crossFilters.cargo);
        if (cargo) {
            // Find route matching this cargo
            const routeIdx = appState.routes.findIndex(r =>
                r.from === cargo.loadPort && r.to === cargo.dischPort
            );
            if (routeIdx >= 0) {
                appState.crossFilters.route = routeIdx.toString();
                document.getElementById('crossFilterRoute').value = routeIdx.toString();
            }
            
            // Find voyage for this cargo
            const data = getCurrentData();
            const voyage = data.computed.voyages.find(v => v.commitmentId === cargo.id);
            if (voyage) {
                appState.crossFilters.voyage = voyage.id;
                appState.crossFilters.vessel = voyage.vesselId;
                document.getElementById('crossFilterVoyage').value = voyage.id;
                document.getElementById('crossFilterVessel').value = voyage.vesselId;
            }
        }
    }
    
    if (appState.crossFilters.vessel) {
        const data = getCurrentData();
        const voyage = data.computed.voyages.find(v => v.vesselId === appState.crossFilters.vessel);
        if (voyage && !appState.crossFilters.voyage) {
            appState.crossFilters.voyage = voyage.id;
            document.getElementById('crossFilterVoyage').value = voyage.id;
        }
    }
    
    if (appState.crossFilters.voyage) {
        const data = getCurrentData();
        const voyage = data.computed.voyages.find(v => v.id === appState.crossFilters.voyage);
        if (voyage) {
            if (!appState.crossFilters.vessel) {
                appState.crossFilters.vessel = voyage.vesselId;
                document.getElementById('crossFilterVessel').value = voyage.vesselId;
            }
            if (!appState.crossFilters.cargo && voyage.commitmentId) {
                appState.crossFilters.cargo = voyage.commitmentId;
                document.getElementById('crossFilterCargo').value = voyage.commitmentId;
            }
        }
    }
    
    if (appState.crossFilters.route) {
        const route = appState.routes[parseInt(appState.crossFilters.route)];
        if (route && !appState.crossFilters.cargo) {
            // Find cargo matching this route
            const cargo = appState.cargo.find(c =>
                c.loadPort === route.from && c.dischPort === route.to
            );
            if (cargo) {
                appState.crossFilters.cargo = cargo.id;
                document.getElementById('crossFilterCargo').value = cargo.id;
            }
        }
    }
    
    renderUnifiedPanel();
    showNotification('Кроссфильтры применены', 'success');
}

/**
 * Clear all cross-filters
 */
export function clearCrossFilters() {
    appState.crossFilters = {
        cargo: null,
        vessel: null,
        voyage: null,
        route: null
    };
    
    document.getElementById('crossFilterCargo').value = '';
    document.getElementById('crossFilterVessel').value = '';
    document.getElementById('crossFilterVoyage').value = '';
    document.getElementById('crossFilterRoute').value = '';
    
    renderUnifiedPanel();
    showNotification('Фильтры очищены', 'info');
}

/**
 * Render unified information panel with cross-filtered data
 */
export function renderUnifiedPanel() {
    const container = document.getElementById('unifiedInfoPanelGrid');
    if (!container) return;
    
    const searchTerm = document.getElementById('unifiedPanelSearch')?.value.toLowerCase() || '';
    const data = getCurrentData();
    
    // Get filtered data
    let cargos = appState.cargo;
    let vessels = appState.vessels;
    let voyages = data.computed.voyages || [];
    let routes = appState.routes;
    
    // Apply cross-filters
    if (appState.crossFilters.cargo) {
        cargos = cargos.filter(c => c.id === appState.crossFilters.cargo);
    }
    if (appState.crossFilters.vessel) {
        vessels = vessels.filter(v => v.id === appState.crossFilters.vessel);
        voyages = voyages.filter(voy => voy.vesselId === appState.crossFilters.vessel);
    }
    if (appState.crossFilters.voyage) {
        voyages = voyages.filter(voy => voy.id === appState.crossFilters.voyage);
    }
    if (appState.crossFilters.route) {
        const route = routes[parseInt(appState.crossFilters.route)];
        if (route) {
            cargos = cargos.filter(c => c.loadPort === route.from && c.dischPort === route.to);
        }
    }
    
    // Apply search filter
    if (searchTerm) {
        cargos = cargos.filter(c =>
            c.id.toLowerCase().includes(searchTerm) ||
            c.commodity.toLowerCase().includes(searchTerm)
        );
        vessels = vessels.filter(v =>
            v.name.toLowerCase().includes(searchTerm) ||
            v.id.toLowerCase().includes(searchTerm)
        );
        voyages = voyages.filter(voy =>
            voy.id.toLowerCase().includes(searchTerm)
        );
    }
    
    // Build unified cards
    const unifiedItems = [];
    
    // Create unified items from cargo
    cargos.forEach(cargo => {
        const voyage = voyages.find(v => v.commitmentId === cargo.id);
        const vessel = voyage ? vessels.find(v => v.id === voyage.vesselId) : null;
        const route = routes.find(r => r.from === cargo.loadPort && r.to === cargo.dischPort);
        
        unifiedItems.push({
            type: 'cargo-based',
            cargo: cargo,
            vessel: vessel,
            voyage: voyage,
            route: route
        });
    });
    
    // Add voyages that don't have cargo yet
    voyages.forEach(voyage => {
        if (!cargos.find(c => c.id === voyage.commitmentId)) {
            const vessel = vessels.find(v => v.id === voyage.vesselId);
            unifiedItems.push({
                type: 'voyage-based',
                cargo: null,
                vessel: vessel,
                voyage: voyage,
                route: null
            });
        }
    });
    
    if (unifiedItems.length === 0) {
        container.innerHTML = '<div class="no-data">Нет данных для отображения. Измените фильтры или добавьте данные.</div>';
        return;
    }
    
    container.innerHTML = unifiedItems.map(item => renderUnifiedCard(item)).join('');
}

/**
 * Render a single unified info card
 * @param {Object} item - Contains cargo, vessel, voyage, route data
 * @returns {string} HTML string for card
 */
function renderUnifiedCard(item) {
    const { cargo, vessel, voyage, route } = item;
    
    return `
        <div class="card" style="border-left: 4px solid ${voyage ? 'var(--accent-success)' : 'var(--accent-warning)'};">
            <!-- Cargo Section -->
            <div style="background: var(--bg-primary); padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <div style="font-size: 0.85rem; color: var(--text-muted);"> ГРУЗ</div>
                    ${cargo ? `<span class="status-badge status-${cargo.status.toLowerCase()}">${cargo.status}</span>` : '<span class="status-badge status-pending">Нет груза</span>'}
                </div>
                ${cargo ? `
                    <div style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary); margin-bottom: 0.5rem;">${cargo.id}</div>
                    <div style="color: var(--text-secondary); margin-bottom: 0.25rem;">${cargo.commodity}</div>
                    <div style="color: var(--accent-primary); font-weight: 600;">${cargo.quantity.toLocaleString()} MT</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
                        Лейкэн: ${formatDate(cargo.laycanStart)} - ${formatDate(cargo.laycanEnd)}
                    </div>
                ` : '<div style="color: var(--text-muted); font-style: italic;">Груз не назначен</div>'}
            </div>
            
            <!-- Vessel Section -->
            <div style="background: var(--bg-primary); padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;"> СУДНО</div>
                ${vessel ? `
                    <div style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary); margin-bottom: 0.25rem;">${vessel.name}</div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem;">
                        ${vessel.class} | ${vessel.dwt.toLocaleString()} DWT | ${vessel.speed} узлов
                    </div>
                ` : '<div style="color: var(--text-muted); font-style: italic;">Судно не назначено</div>'}
            </div>
            
            <!-- Voyage Section -->
            <div style="background: var(--bg-primary); padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;"> РЕЙС</div>
                ${voyage ? `
                    <div style="font-weight: 700; color: var(--accent-primary); margin-bottom: 0.25rem;">${voyage.id}</div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem;">
                        Этапов: ${voyage.legs ? voyage.legs.length : 0}
                        ${voyage.startDate ? ` | Старт: ${formatDate(voyage.startDate)}` : ''}
                    </div>
                ` : '<div style="color: var(--text-muted); font-style: italic;">Рейс не создан</div>'}
            </div>
            
            <!-- Route Section -->
            <div style="background: var(--bg-primary); padding: 1rem; border-radius: 6px;">
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;"> МАРШРУТ</div>
                ${route ? `
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem;">
                        ${route.from} → ${route.to}
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem;">
                        ${route.distance.toLocaleString()} nm
                        ${route.canal ? ` | Канал: ${route.canal}` : ''}
                    </div>
                ` : (cargo ? `
                    <div style="color: var(--text-secondary);">
                        ${cargo.loadPort} → ${cargo.dischPort}
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-muted);">Маршрут не определен</div>
                ` : '<div style="color: var(--text-muted); font-style: italic;">Маршрут не определен</div>')}
            </div>
            
            <!-- Action Buttons -->
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color); display: flex; gap: 0.5rem;">
                ${cargo && !voyage ? `
                    <button class="btn-primary" style="flex: 1; padding: 0.5rem; font-size: 0.9rem;" onclick="createVoyageFromCargo('${cargo.id}')">Создать рейс</button>
                ` : ''}
                ${voyage ? `
                    <button class="btn-secondary" style="flex: 1; padding: 0.5rem; font-size: 0.9rem;" onclick="viewVoyageDetails('${voyage.id}')">Детали рейса</button>
                ` : ''}
                ${cargo ? `
                    <button class="btn-secondary" style="padding: 0.5rem; font-size: 0.9rem;" onclick="editCargo('${cargo.id}')"></button>
                ` : ''}
            </div>
        </div>
    `;
}
