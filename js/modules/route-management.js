/**
 * Route Management Module
 * Handles all route-related operations: CRUD, selection, transfer to voyage builder
 * Extracted from vessel_scheduler_enhanced.js
 */

import { appState, getCurrentData } from '../core/app-state.js';
import { showNotification } from '../core/utils.js';
import { saveToLocalStorage } from '../services/storage-service.js';
import { apiClient } from '../services/api-client.js';

export class RouteManager {
    constructor(state, storage) {
        this.state = state;
        this.storage = storage;
    }

    renderRoutesTable() {
        renderRoutesTable();
    }

    addRoute() {
        addRoute();
    }

    deleteRoute(index) {
        deleteRoute(index);
    }

    transferRouteToBuilder(index) {
        transferRouteToBuilder(index);
    }

    transferSelectedRoutesToBuilder() {
        transferSelectedRoutesToBuilder();
    }
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
            <td>${route.from}</td>
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
 * @param {HTMLInputElement} checkbox - The select all checkbox
 */
export function toggleAllRoutes(checkbox) {
    const checkboxes = document.querySelectorAll('.route-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    updateRouteSelection();
}

/**
 * Update route selection count and show/hide bulk transfer button
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

/**
 * Transfer selected routes to voyage builder
 */
export function transferSelectedRoutesToBuilder() {
    const checkboxes = document.querySelectorAll('.route-checkbox:checked');
    const selectedIndices = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    if (selectedIndices.length === 0) {
        showNotification('Выберите хотя бы один маршрут', 'warning');
        return;
    }
    
    // Switch to builder tab
    if (window.switchTab) {
        window.switchTab('voyageBuilder');
    }
    
    // Clear existing legs
    appState.voyageBuilder.currentLegs = [];
    const container = document.getElementById('voyageLegsContainer');
    if (container) {
        container.innerHTML = '';
    }
    
    // Add legs for each selected route
    selectedIndices.forEach((index, legIndex) => {
        const route = appState.routes[index];
        if (!route) return;
        
        // Add loading at first port (only for first route)
        if (legIndex === 0 && window.addVoyageLeg) {
            window.addVoyageLeg();
            const leg = appState.voyageBuilder.currentLegs[appState.voyageBuilder.currentLegs.length - 1];
            const legDiv = document.getElementById(`leg-${leg.id}`);
            if (legDiv) {
                legDiv.querySelector('.leg-type').value = 'loading';
                legDiv.querySelector('.leg-from').value = route.from;
                legDiv.querySelector('.leg-to').value = route.from;
                legDiv.querySelector('.leg-distance').value = 0;
            }
        }
        
        // Add transit leg
        if (window.addVoyageLeg) {
            window.addVoyageLeg();
            let leg = appState.voyageBuilder.currentLegs[appState.voyageBuilder.currentLegs.length - 1];
            let legDiv = document.getElementById(`leg-${leg.id}`);
            if (legDiv) {
                legDiv.querySelector('.leg-type').value = 'transit';
                legDiv.querySelector('.leg-from').value = route.from;
                legDiv.querySelector('.leg-to').value = route.to;
                legDiv.querySelector('.leg-distance').value = route.distance;
            }
        }
        
        // Add canal leg if applicable
        if (route.canal && window.addVoyageLeg) {
            window.addVoyageLeg();
            const leg = appState.voyageBuilder.currentLegs[appState.voyageBuilder.currentLegs.length - 1];
            const legDiv = document.getElementById(`leg-${leg.id}`);
            if (legDiv) {
                legDiv.querySelector('.leg-type').value = 'canal';
                legDiv.querySelector('.leg-from').value = route.canal;
                legDiv.querySelector('.leg-to').value = route.canal;
                legDiv.querySelector('.leg-distance').value = 50; // Typical canal distance
            }
        }
        
        // Add discharge at last port (only for last route)
        if (legIndex === selectedIndices.length - 1 && window.addVoyageLeg) {
            window.addVoyageLeg();
            const leg = appState.voyageBuilder.currentLegs[appState.voyageBuilder.currentLegs.length - 1];
            const legDiv = document.getElementById(`leg-${leg.id}`);
            if (legDiv) {
                legDiv.querySelector('.leg-type').value = 'discharge';
                legDiv.querySelector('.leg-from').value = route.to;
                legDiv.querySelector('.leg-to').value = route.to;
                legDiv.querySelector('.leg-distance').value = 0;
            }
        }
    });
    
    // Uncheck all routes
    document.querySelectorAll('.route-checkbox').forEach(cb => cb.checked = false);
    const selectAll = document.getElementById('selectAllRoutes');
    if (selectAll) selectAll.checked = false;
    updateRouteSelection();
    
    showNotification(`Добавлено ${selectedIndices.length} маршрутов в конструктор рейса`, 'success');
}

/**
 * Transfer single route to voyage builder
 * @param {number} index - Route index in array
 */
export function transferRouteToBuilder(index) {
    const route = appState.routes[index];
    if (!route) return;

    // Switch to builder tab
    if (window.switchTab) {
        window.switchTab('voyageBuilder');
    }

    // Clear existing legs
    appState.voyageBuilder.currentLegs = [];
    const container = document.getElementById('voyageLegsContainer');
    if (container) {
        container.innerHTML = '';
    }

    // Add legs only if addVoyageLeg function is available
    if (!window.addVoyageLeg) {
        showNotification('Функция создания этапов недоступна', 'error');
        return;
    }

    // 1. Loading
    window.addVoyageLeg();
    let leg = appState.voyageBuilder.currentLegs[0];
    let legDiv = document.getElementById(`leg-${leg.id}`);
    if (legDiv) {
        legDiv.querySelector('.leg-type').value = 'loading';
        legDiv.querySelector('.leg-from').value = route.from;
        legDiv.querySelector('.leg-to').value = route.from;
        legDiv.querySelector('.leg-distance').value = 0;
    }

    // 2. Transit
    window.addVoyageLeg();
    leg = appState.voyageBuilder.currentLegs[1];
    legDiv = document.getElementById(`leg-${leg.id}`);
    if (legDiv) {
        legDiv.querySelector('.leg-type').value = 'transit';
        legDiv.querySelector('.leg-from').value = route.from;
        legDiv.querySelector('.leg-to').value = route.to;
        legDiv.querySelector('.leg-distance').value = route.distance;
    }

    // 3. Discharge
    window.addVoyageLeg();
    leg = appState.voyageBuilder.currentLegs[2];
    legDiv = document.getElementById(`leg-${leg.id}`);
    if (legDiv) {
        legDiv.querySelector('.leg-type').value = 'discharge';
        legDiv.querySelector('.leg-from').value = route.to;
        legDiv.querySelector('.leg-to').value = route.to;
        legDiv.querySelector('.leg-distance').value = 0;
    }

    showNotification(`Маршрут ${route.from} → ${route.to} перенесен в конструктор`, 'success');
}

/**
 * Open route modal for adding new route
 */
export function addRoute() {
    const modal = document.getElementById('routeModal');
    if (!modal) return;
    
    modal.classList.add('show');
    modal.style.display = 'flex';
    
    // Populate port dropdowns
    populatePortDropdown('routeFrom');
    populatePortDropdown('routeTo');
}

/**
 * Close route modal
 */
export function closeRouteModal() {
    const modal = document.getElementById('routeModal');
    if (modal) {
        modal.classList.remove('show');
        modal.style.display = 'none';
    }
    const form = document.getElementById('routeForm');
    if (form) {
        form.reset();
    }
}

/**
 * Delete route by index
 * @param {number} index - Route index in array
 */
export async function deleteRoute(index) {
    if (confirm('Удалить этот маршрут?')) {
        // Note: API might expect ID, but we have index.
        // Assuming routes have IDs or we just update the whole list via API if needed.
        // For now, we'll just update local state and assume sync happens later or via bulk update.
        // If API supports delete by index or ID, we should use it.
        // Let's assume we just update local state for now as routes might not have IDs in this version.
        
        appState.routes.splice(index, 1);
        renderRoutesTable();
        buildRouteLegCatalog();
        saveToLocalStorage();
        showNotification('Маршрут удален', 'success');
    }
}

/**
 * Setup route form submission handler
 */
export function setupRouteFormHandler() {
    const form = document.getElementById('routeForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const routeData = {
            from: document.getElementById('routeFrom').value,
            to: document.getElementById('routeTo').value,
            distance: parseInt(document.getElementById('routeDistance').value),
            canal: document.getElementById('routeCanal').value
        };
        
        try {
            const result = await apiClient.createRoute(routeData);
            
            if (result.success || result.status === 200) {
                appState.routes.push(routeData);
                renderRoutesTable();
                closeRouteModal();
                buildRouteLegCatalog();
                saveToLocalStorage();
                showNotification('Маршрут добавлен', 'success');
            } else {
                showNotification('Ошибка сохранения: ' + (result.error || 'Unknown error'), 'error');
                if (result.errors && window.apiValidator) {
                    window.apiValidator.displayErrors(result.errors);
                }
            }
        } catch (error) {
            console.error('Error saving route:', error);
            showNotification('Ошибка сохранения маршрута', 'error');
        }
    });
}

/**
 * Build route leg catalog for efficient lookup
 * @returns {Array} Route legs catalog
 */
export function buildRouteLegCatalog() {
    const data = getCurrentData();
    const catalog = [];

    // Build legs from routes
    data.masters.routes.forEach(route => {
        catalog.push({
            id: `${route.from}-${route.to}`,
            from: route.from,
            to: route.to,
            distance: route.distance,
            canal: route.canal,
            waypoints: route.waypoints || []
        });
    });

    data.computed.routeLegs = catalog;
    return catalog;
}

/**
 * Populate port dropdown with available ports
 * @param {string} elementId - ID of the select element
 */
function populatePortDropdown(elementId) {
    const select = document.getElementById(elementId);
    if (!select) return;
    
    const ports = appState.ports || [];
    const uniquePorts = [...new Set(ports.map(p => p.name || p.id))].filter(Boolean);
    
    select.innerHTML = '<option value="">Выберите порт...</option>' +
        uniquePorts.map(port => `<option value="${port}">${port}</option>`).join('');
}

/**
 * Get route statistics for dashboard
 * @returns {Object} Route statistics
 */
export function getRouteStats() {
    const total = appState.routes.length;
    const totalDistance = appState.routes.reduce((sum, r) => sum + (r.distance || 0), 0);
    const avgDistance = total > 0 ? Math.round(totalDistance / total) : 0;
    const withCanal = appState.routes.filter(r => r.canal).length;
    
    return {
        total,
        totalDistance,
        avgDistance,
        withCanal
    };
}

/**
 * Find route between two ports
 * @param {string} from - Starting port
 * @param {string} to - Destination port
 * @returns {Object|null} Route object or null if not found
 */
export function findRoute(from, to) {
    return appState.routes.find(r => r.from === from && r.to === to) || null;
}

// Export functions to window for HTML onclick handlers
if (typeof window !== 'undefined') {
    window.addRoute = addRoute;
    window.closeRouteModal = closeRouteModal;
    window.deleteRoute = deleteRoute;
    window.transferRouteToBuilder = transferRouteToBuilder;
    window.transferSelectedRoutesToBuilder = transferSelectedRoutesToBuilder;
    window.toggleAllRoutes = toggleAllRoutes;
    window.updateRouteSelection = updateRouteSelection;
}