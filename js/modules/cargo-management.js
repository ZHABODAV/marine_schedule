/**
 * Cargo Management Module
 * Handles all cargo-related operations: CRUD, filtering, assignment
 * Extracted from vessel_scheduler_enhanced.js
 */

import { appState } from '../core/app-state.js';
import { showNotification, formatDate } from '../core/utils.js';
import { saveToLocalStorage } from '../services/storage-service.js';
import { apiClient } from '../services/api-client.js';
import { voyageBuilder } from './voyage-builder.js';

export class CargoManager {
    constructor(state, storage) {
        this.state = state;
        this.storage = storage;
    }

    renderCargoTable() {
        renderCargoTable();
    }

    addCargo() {
        addCargo();
    }

    editCargo(id) {
        editCargo(id);
    }

    deleteCargo(id) {
        deleteCargo(id);
    }

    createVoyageFromCargo(id) {
        createVoyageFromCargo(id);
    }
}

/**
 * Render cargo table with current filters applied
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
 * Open cargo modal for adding new cargo
 */
export function addCargo() {
    const modal = document.getElementById('cargoModal');
    if (!modal) return;
    
    document.getElementById('cargoModalTitle').textContent = 'Добавить груз';
    document.getElementById('cargoEditId').value = '';
    document.getElementById('cargoForm').reset();
    modal.style.display = 'flex';
    modal.classList.add('show');
    
    // Populate port dropdowns
    populatePortDropdown('loadPort');
    populatePortDropdown('dischPort');
}

/**
 * Open cargo modal for editing cargo
 * @param {string} id - Cargo ID to edit
 */
export function editCargo(id) {
    const cargo = appState.cargo.find(c => c.id === id);
    if (!cargo) {
        showNotification('Груз не найден', 'error');
        return;
    }
    
    const modal = document.getElementById('cargoModal');
    if (!modal) return;
    
    document.getElementById('cargoModalTitle').textContent = 'Редактировать груз';
    document.getElementById('cargoEditId').value = id;
    
    // Populate port dropdowns first
    populatePortDropdown('loadPort');
    populatePortDropdown('dischPort');
    
    // Then set form values
    document.getElementById('cargoId').value = cargo.id;
    document.getElementById('commodity').value = cargo.commodity;
    document.getElementById('quantity').value = cargo.quantity;
    document.getElementById('loadPort').value = cargo.loadPort;
    document.getElementById('dischPort').value = cargo.dischPort;
    document.getElementById('laycanStart').value = cargo.laycanStart;
    document.getElementById('laycanEnd').value = cargo.laycanEnd;
    
    // Optional cost fields
    if (document.getElementById('operationalCost')) {
        document.getElementById('operationalCost').value = cargo.operationalCost || 0;
    }
    if (document.getElementById('overheadCost')) {
        document.getElementById('overheadCost').value = cargo.overheadCost || 0;
    }
    if (document.getElementById('otherCost')) {
        document.getElementById('otherCost').value = cargo.otherCost || 0;
    }
    
    modal.style.display = 'flex';
    modal.classList.add('show');
}

/**
 * Delete cargo by ID
 * @param {string} id - Cargo ID to delete
 */
export async function deleteCargo(id) {
    if (!confirm(`Удалить груз ${id}?`)) return;
    
    try {
        const result = await apiClient.deleteCargo(id);
        
        if (result.success || result.status === 200) {
            const index = appState.cargo.findIndex(c => c.id === id);
            if (index !== -1) {
                appState.cargo.splice(index, 1);
                renderCargoTable();
                saveToLocalStorage();
                showNotification('Груз удален', 'success');
            }
        } else {
            showNotification('Ошибка удаления груза: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error deleting cargo:', error);
        showNotification('Ошибка удаления груза', 'error');
    }
}

/**
 * Close cargo modal
 */
export function closeCargoModal() {
    const modal = document.getElementById('cargoModal');
    if (modal) {
        modal.classList.remove('show');
        modal.style.display = 'none';
    }
    const form = document.getElementById('cargoForm');
    if (form) {
        form.reset();
    }
}

/**
 * Setup cargo form submission handler
 */
export function setupCargoFormHandler() {
    const form = document.getElementById('cargoForm');
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const editId = document.getElementById('cargoEditId').value;
        const cargoData = {
            id: document.getElementById('cargoId').value,
            commodity: document.getElementById('commodity').value,
            quantity: parseInt(document.getElementById('quantity').value),
            loadPort: document.getElementById('loadPort').value,
            dischPort: document.getElementById('dischPort').value,
            laycanStart: document.getElementById('laycanStart').value,
            laycanEnd: document.getElementById('laycanEnd').value,
            operationalCost: parseFloat(document.getElementById('operationalCost')?.value) || 0,
            overheadCost: parseFloat(document.getElementById('overheadCost')?.value) || 0,
            otherCost: parseFloat(document.getElementById('otherCost')?.value) || 0,
            status: 'Pending'
        };
        
        try {
            let result;
            if (editId) {
                result = await apiClient.updateCargo(editId, cargoData);
            } else {
                result = await apiClient.createCargo(cargoData);
            }
            
            if (result.success || result.status === 200) {
                if (editId) {
                    const index = appState.cargo.findIndex(c => c.id === editId);
                    if (index !== -1) {
                        // Preserve status if not returned by API
                        if (!cargoData.status) cargoData.status = appState.cargo[index].status;
                        appState.cargo[index] = cargoData;
                        showNotification('Груз обновлен', 'success');
                    }
                } else {
                    appState.cargo.push(cargoData);
                    showNotification('Груз добавлен', 'success');
                }
                
                renderCargoTable();
                closeCargoModal();
                saveToLocalStorage();
            } else {
                showNotification('Ошибка сохранения: ' + (result.error || 'Unknown error'), 'error');
                if (result.errors && window.apiValidator) {
                    window.apiValidator.displayErrors(result.errors, 'cargo-errors');
                }
            }
        } catch (error) {
            console.error('Error saving cargo:', error);
            showNotification('Ошибка сохранения груза', 'error');
        }
    });
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

    if (appState.filters.product) {
        filtered = filtered.filter(item => item.commodity === appState.filters.product);
    }

    if (appState.filters.port) {
        filtered = filtered.filter(item => 
            item.loadPort === appState.filters.port || item.dischPort === appState.filters.port
        );
    }

    return filtered;
}

/**
 * Create voyage from cargo
 * @param {string} cargoId - Cargo ID to create voyage for
 */
export function createVoyageFromCargo(cargoId) {
    const cargo = appState.cargo.find(c => c.id === cargoId);
    if (!cargo) return;
    
    // Switch to voyage builder and pre-populate
    if (window.switchTab) {
        window.switchTab('voyageBuilder');
    }
    
    // Set cargo in voyage builder
    if (voyageBuilder && voyageBuilder.setCargo) {
        voyageBuilder.setCargo(cargoId);
    }
    
    const route = appState.routes.find(r => r.from === cargo.loadPort && r.to === cargo.dischPort);
    if (route) {
        const routeIndex = appState.routes.indexOf(route);
        if (window.transferRouteToBuilder) {
            window.transferRouteToBuilder(routeIndex);
        }
        showNotification(`Создание рейса для груза ${cargoId}`, 'success');
    } else {
        showNotification(`Маршрут ${cargo.loadPort} → ${cargo.dischPort} не найден`, 'warning');
    }
}

/**
 * Get cargo statistics for dashboard
 * @returns {Object} Cargo statistics
 */
export function getCargoStats() {
    const total = appState.cargo.length;
    const pending = appState.cargo.filter(c => c.status === 'Pending').length;
    const assigned = appState.cargo.filter(c => c.status === 'Assigned').length;
    const completed = appState.cargo.filter(c => c.status === 'Completed').length;
    
    const totalQuantity = appState.cargo.reduce((sum, c) => sum + (c.quantity || 0), 0);
    
    return {
        total,
        pending,
        assigned,
        completed,
        totalQuantity
    };
}

// Export functions to window for HTML onclick handlers
if (typeof window !== 'undefined') {
    window.addCargo = addCargo;
    window.editCargo = editCargo;
    window.deleteCargo = deleteCargo;
    window.closeCargoModal = closeCargoModal;
    window.createVoyageFromCargo = createVoyageFromCargo;
}