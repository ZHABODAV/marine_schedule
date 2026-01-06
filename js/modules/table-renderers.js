/**
 * Table Rendering Module
 * Renders data tables for vessels, cargo, and routes
 * Extracted from vessel_scheduler_enhanced.js lines 922-1263
 */

import { appState, getCurrentData } from '../core/app-state.js';
import { applyFiltersToData, formatDate } from '../core/utilities.js';

/**
 * Render vessels table
 */
export function renderVesselsTable() {
    const tbody = document.getElementById('vesselsTableBody');
    if (!tbody) return;
    
    const filteredData = applyFiltersToData(appState.vessels);
    
    if (filteredData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="no-data">Нет данных о судах.</td></tr>';
        return;
    }
    
    tbody.innerHTML = filteredData.map(vessel => `
        <tr>
            <td>${vessel.id}</td>
            <td>${vessel.name}</td>
            <td>${vessel.class}</td>
            <td>${vessel.dwt.toLocaleString()}</td>
            <td>${vessel.speed}</td>
            <td><span class="status-badge status-${vessel.status.toLowerCase()}">${vessel.status}</span></td>
            <td>
                <button class="btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.9rem; margin-right: 0.5rem;" onclick="editVessel('${vessel.id}')">Изменить</button>
                <button class="btn-danger" style="padding: 0.5rem 1rem; font-size: 0.9rem;" onclick="deleteVessel('${vessel.id}')">Удалить</button>
            </td>
        </tr>
    `).join('');
}

/**
 * Render vessel dashboard grid view
 */
export function renderVesselDashboard() {
    const container = document.getElementById('vesselDashboardGrid');
    if (!container) return;

    const searchTerm = document.getElementById('vesselDashboardSearch')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('vesselDashboardFilter')?.value || '';

    let vessels = applyFiltersToData(appState.vessels);
    
    // Apply status filter
    if (statusFilter) {
        vessels = vessels.filter(v => v.status === statusFilter);
    }
    
    // Apply search filter
    vessels = vessels.filter(v =>
        v.name.toLowerCase().includes(searchTerm) ||
        v.id.toLowerCase().includes(searchTerm)
    );

    if (vessels.length === 0) {
        container.innerHTML = '<div class="no-data">Нет судов для отображения</div>';
        return;
    }

    container.innerHTML = vessels.map(vessel => {
        // Find active voyage
        const voyages = appState[appState.currentModule].computed.voyages || [];
        const activeVoyage = voyages.find(voy => voy.vesselId === vessel.id) || null;

        let itinerary = 'Нет активного рейса';
        let cargoInfo = 'Нет груза';

        if (activeVoyage) {
            if (activeVoyage.legs && activeVoyage.legs.length > 0) {
                const firstLeg = activeVoyage.legs[0];
                const lastLeg = activeVoyage.legs[activeVoyage.legs.length - 1];
                itinerary = `${firstLeg.from || firstLeg.port || '?'} → ${lastLeg.to || lastLeg.port || '?'}`;
            }

            // Try to find cargo info
            const commitment = appState.cargo.find(c => c.id === activeVoyage.commitmentId);
            if (commitment) {
                cargoInfo = `${commitment.commodity} (${commitment.quantity.toLocaleString()} MT)`;
            }
        }

        return `
            <div class="card" style="display: flex; flex-direction: column; gap: 1rem; border-left: 4px solid ${vessel.status === 'Active' ? 'var(--accent-success)' : 'var(--text-muted)'}">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin-bottom: 0.25rem; font-size: 1.2rem;">${vessel.name}</h3>
                        <span class="status-badge status-${vessel.status.toLowerCase()}">${vessel.status}</span>
                    </div>
                    <div style="text-align: right; font-size: 0.9rem; color: var(--text-muted);">
                        ${vessel.class}<br>
                        ${vessel.dwt.toLocaleString()} DWT
                    </div>
                </div>
                
                <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px;">
                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.25rem;">Текущий рейс</div>
                    <div style="font-weight: 600; color: var(--accent-primary);">${activeVoyage ? activeVoyage.id : '-'}</div>
                </div>

                <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px;">
                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.25rem;">Груз</div>
                    <div>${cargoInfo}</div>
                </div>

                <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px;">
                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.25rem;">Маршрут</div>
                    <div style="font-size: 0.95rem;">${itinerary}</div>
                </div>

                <div style="margin-top: auto; padding-top: 0.5rem;">
                    <button class="btn-primary" style="width: 100%;" onclick="generateVoyageForVessel('${vessel.id}')">Сгенерировать рейс</button>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Render cargo/commitments table
 */
export function renderCargoTable() {
    const tbody = document.getElementById('cargoTableBody');
    if (!tbody) return;
    
    const filteredData = applyFiltersToData(appState.cargo);
    
    if (filteredData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="no-data">Нет данных о грузах.</td></tr>';
        return;
    }
    
    tbody.innerHTML = filteredData.map(cargo => `
        <tr>
            <td>${cargo.id}</td>
            <td>${cargo.commodity}</td>
            <td>${cargo.quantity.toLocaleString()}</td>
            <td>${cargo.loadPort}</td>
            <td>${cargo.dischPort}</td>
            <td>${formatDate(cargo.laycanStart)}</td>
            <td>${formatDate(cargo.laycanEnd)}</td>
            <td><span class="status-badge status-${cargo.status.toLowerCase()}">${cargo.status}</span></td>
            <td>
                <button class="btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.9rem; margin-right: 0.5rem;" onclick="editCargo('${cargo.id}')">Изменить</button>
                <button class="btn-danger" style="padding: 0.5rem 1rem; font-size: 0.9rem;" onclick="deleteCargo('${cargo.id}')">Удалить</button>
            </td>
        </tr>
    `).join('');
}

/**
 * Render routes table
 */
export function renderRoutesTable() {
    const tbody = document.getElementById('routesTableBody');
    if (!tbody) return;
    
    if (appState.routes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">Нет данных о маршрутах.</td></tr>';
        return;
    }
    
    tbody.innerHTML = appState.routes.map((route, index) => `
        <tr>
            <td>
                <input type="checkbox" class="route-checkbox" value="${index}" onchange="updateRouteSelection()" style="cursor: pointer; width: 18px; height: 18px;">
            </td>
            <td>${route.from}< /td>
            <td>${route.to}</td>
            <td>${route.distance.toLocaleString()}</td>
            <td>${route.canal || '-'}</td>
            <td>
                <button class="btn-primary" style="padding: 0.5rem 1rem; font-size: 0.9rem; margin-right: 0.5rem;" onclick="transferRouteToBuilder(${index})">В конструктор</button>
                <button class="btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.9rem;" onclick="deleteRoute(${index})">Удалить</button>
            </td>
        </tr>
    `).join('');
}

/**
 * Toggle all routes selection
 * @param {HTMLInputElement} checkbox - Master checkbox
 */
export function toggleAllRoutes(checkbox) {
    const checkboxes = document.querySelectorAll('.route-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    updateRouteSelection();
}

/**
 * Update route selection count
 */
export function updateRouteSelection() {
    const checkboxes = document.querySelectorAll('.route-checkbox:checked');
    const count = checkboxes.length;
    
    const bulkBtn = document.getElementById('bulkTransferBtn');
    const countSpan = document.getElementById('selectedRoutesCount');
    
    if (bulkBtn && countSpan) {
        if (count > 0) {
            bulkBtn.style.display = 'inline-block';
            countSpan.textContent = count;
        } else {
            bulkBtn.style.display = 'none';
        }
    }
}
