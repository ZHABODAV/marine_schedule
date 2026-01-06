/**
 * Vessel Management Module
 * Handles all vessel-related operations: CRUD, filtering, dashboard
 * Extracted from vessel_scheduler_enhanced.js
 */

import { appState, getCurrentData } from '../core/app-state.js';
import { showNotification } from '../core/utils.js';
import { saveToLocalStorage } from '../services/storage-service.js';
import { apiClient } from '../services/api-client.js';

export class VesselManager {
    constructor(state, storage) {
        this.state = state;
        this.storage = storage;
    }

    renderVesselsTable() {
        renderVesselsTable();
    }

    renderVesselDashboard() {
        renderVesselDashboard();
    }

    addVessel() {
        addVessel();
    }

    editVessel(id) {
        editVessel(id);
    }

    deleteVessel(id) {
        deleteVessel(id);
    }
}

/**
 * Render vessels table with current filters applied
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
 * Generate voyage for a specific vessel
 * @param {string} vesselId - ID of the vessel
 */
export function generateVoyageForVessel(vesselId) {
    // This will be implemented in voyage-builder module
    // For now, we'll just prepare the data
    if (window.switchTab) {
        window.switchTab('voyageBuilder');
    }
    
    // Set the selected vessel
    const select = document.getElementById('voyageVesselSelect');
    if (select) {
        select.value = vesselId;
    }

    // Clear existing legs
    appState.voyageBuilder.currentLegs = [];
    const container = document.getElementById('voyageLegsContainer');
    if (container) {
        container.innerHTML = '';
    }

    // Check if there's an existing voyage for this vessel to duplicate
    const voyages = appState[appState.currentModule].computed.voyages || [];
    const existingVoyage = voyages.find(voy => voy.vesselId === vesselId);

    if (existingVoyage && existingVoyage.legs && existingVoyage.legs.length > 0) {
        showNotification(`Дублирован существующий рейс для судна ${vesselId}`, 'success');
    } else {
        showNotification(`Планирование нового рейса для судна ${vesselId}`, 'info');
    }
}

/**
 * Open vessel modal for adding new vessel
 */
export function addVessel() {
    document.getElementById('vesselModalTitle').textContent = 'Добавить судно';
    document.getElementById('vesselEditId').value = '';
    const modal = document.getElementById('vesselModal');
    modal.style.display = 'flex';
    modal.classList.add('show');
}

/**
 * Open vessel modal for editing vessel
 * @param {string} id - Vessel ID to edit
 */
export function editVessel(id) {
    const vessel = appState.vessels.find(v => v.id === id);
    if (!vessel) {
        showNotification('Судно не найдено', 'error');
        return;
    }
    
    document.getElementById('vesselModalTitle').textContent = 'Редактировать судно';
    document.getElementById('vesselEditId').value = id;
    document.getElementById('vesselId').value = vessel.id;
    document.getElementById('vesselName').value = vessel.name;
    document.getElementById('vesselClass').value = vessel.class;
    document.getElementById('vesselDwt').value = vessel.dwt;
    document.getElementById('vesselSpeed').value = vessel.speed;
    
    const modal = document.getElementById('vesselModal');
    modal.style.display = 'flex';
    modal.classList.add('show');
}

/**
 * Delete vessel by ID
 * @param {string} id - Vessel ID to delete
 */
export async function deleteVessel(id) {
    if (!confirm(`Удалить судно ${id}? Это действие нельзя отменить.`)) return;
    
    try {
        // Call API to delete vessel
        const result = await apiClient.deleteVessel(id);
        
        if (result.success || result.status === 200) {
            const index = appState.vessels.findIndex(v => v.id === id);
            if (index !== -1) {
                // Check if vessel is assigned to any voyage
                const data = getCurrentData();
                const hasVoyages = data.computed.voyages.some(voy => voy.vesselId === id);
                
                if (hasVoyages) {
                    // Remove voyages for this vessel
                    data.computed.voyages = data.computed.voyages.filter(voy => voy.vesselId !== id);
                }
                
                appState.vessels.splice(index, 1);
                renderVesselsTable();
                renderVesselDashboard();
                saveToLocalStorage();
                showNotification('Судно удалено', 'success');
            }
        } else {
            showNotification('Ошибка удаления судна: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error deleting vessel:', error);
        showNotification('Ошибка удаления судна', 'error');
    }
}

/**
 * Close vessel modal
 */
export function closeVesselModal() {
    const modal = document.getElementById('vesselModal');
    if (modal) {
        modal.classList.remove('show');
        modal.style.display = 'none';
    }
    const form = document.getElementById('vesselForm');
    if (form) {
        form.reset();
    }
}

/**
 * Setup vessel form submission handler
 */
export function setupVesselFormHandler() {
    const form = document.getElementById('vesselForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const editId = document.getElementById('vesselEditId').value;
        const vesselData = {
            id: document.getElementById('vesselId').value,
            name: document.getElementById('vesselName').value,
            class: document.getElementById('vesselClass').value,
            dwt: parseInt(document.getElementById('vesselDwt').value),
            speed: parseFloat(document.getElementById('vesselSpeed').value),
            status: 'Active'
        };
        
        try {
            let result;
            if (editId) {
                // Update existing vessel
                result = await apiClient.updateVessel(editId, vesselData);
            } else {
                // Create new vessel
                result = await apiClient.createVessel(vesselData);
            }
            
            if (result.success || result.status === 200) {
                // Update local state
                if (editId) {
                    const index = appState.vessels.findIndex(v => v.id === editId);
                    if (index !== -1) {
                        appState.vessels[index] = vesselData;
                        showNotification('Судно обновлено', 'success');
                    }
                } else {
                    appState.vessels.push(vesselData);
                    showNotification('Судно добавлено', 'success');
                }
                
                renderVesselsTable();
                renderVesselDashboard();
                closeVesselModal();
                saveToLocalStorage();
            } else {
                showNotification('Ошибка сохранения: ' + (result.error || 'Unknown error'), 'error');
                if (result.errors && window.apiValidator) {
                    window.apiValidator.displayErrors(result.errors);
                }
            }
        } catch (error) {
            console.error('Error saving vessel:', error);
            showNotification('Ошибка сохранения судна', 'error');
        }
    });
}

/**
 * Helper function to apply filters (temporary, will be moved to utils)
 * @param {Array} data - Data to filter
 * @returns {Array} Filtered data
 */
function applyFiltersToData(data) {
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

    if (appState.filters.vesselId) {
        filtered = filtered.filter(item => item.vesselId === appState.filters.vesselId || item.vessel === appState.filters.vesselId || item.id === appState.filters.vesselId);
    }

    return filtered;
}

// Export functions to window for HTML onclick handlers
if (typeof window !== 'undefined') {
    window.addVessel = addVessel;
    window.editVessel = editVessel;
    window.deleteVessel = deleteVessel;
    window.closeVesselModal = closeVesselModal;
    window.generateVoyageForVessel = generateVoyageForVessel;
}