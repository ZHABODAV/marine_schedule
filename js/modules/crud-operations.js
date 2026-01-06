/**
 * CRUD Operations Module
 * Handles Create, Read, Update, Delete operations for vessels, cargo, and routes
 * Extracted from vessel_scheduler_enhanced.js lines 1266-1548
 */

import { appState, getCurrentData } from '../core/app-state.js';
import { showNotification } from '../core/utilities.js';
import { renderVesselsTable, renderCargoTable, renderRoutesTable, renderVesselDashboard } from './table-renderers.js';
import { updateDashboard, populateFilterDropdowns } from '../ui/dashboard.js';
import { saveToLocalStorage } from '../services/storage-service.js';

/**
 * Add new vessel (opens modal)
 */
export function addVessel() {
    document.getElementById('vesselModalTitle').textContent = 'Добавить судно';
    document.getElementById('vesselEditId').value = '';
    const modal = document.getElementById('vesselModal');
    modal.style.display = 'flex';
    modal.classList.add('show');
}

/**
 * Edit existing vessel
 * @param {string} id - Vessel ID
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
 * Delete vessel
 * @param {string} id - Vessel ID
 */
export function deleteVessel(id) {
    if (!confirm(`Удалить судно ${id}? Это действие нельзя отменить.`)) return;
    
    const index = appState.vessels.findIndex(v => v.id === id);
    if (index !== -1) {
        // Check if vessel is assigned to any voyage
        const data = getCurrentData();
        const hasVoyages = data.computed.voyages.some(voy => voy.vesselId === id);
        
        if (hasVoyages) {
            if (!confirm(`Судно ${id} используется в рейсах. При удалении судна связанные рейсы будут отменены. Продолжить?`)) {
                return;
            }
            
            // Remove voyages for this vessel
            data.computed.voyages = data.computed.voyages.filter(voy => voy.vesselId !== id);
        }
        
        appState.vessels.splice(index, 1);
        renderVesselsTable();
        renderVesselDashboard();
        updateDashboard();
        populateFilterDropdowns();
        saveToLocalStorage();
        showNotification('Судно удалено', 'success');
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
 * Add new cargo (opens modal)
 */
export function addCargo() {
    const modal = document.getElementById('cargoModal');
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
 * Edit existing cargo
 * @param {string} id - Cargo ID
 */
export function editCargo(id) {
    const cargo = appState.cargo.find(c => c.id === id);
    if (!cargo) {
        showNotification('Груз не найден', 'error');
        return;
    }
    
    const modal = document.getElementById('cargoModal');
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
    
    modal.style.display = 'flex';
    modal.classList.add('show');
}

/**
 * Delete cargo
 * @param {string} id - Cargo ID
 */
export function deleteCargo(id) {
    if (!confirm(`Удалить груз ${id}?`)) return;
    
    const index = appState.cargo.findIndex(c => c.id === id);
    if (index !== -1) {
        appState.cargo.splice(index, 1);
        renderCargoTable();
        updateDashboard();
        saveToLocalStorage();
        showNotification('Груз удален', 'success');
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
 * Add new route (opens modal)
 */
export function addRoute() {
    const modal = document.getElementById('routeModal');
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
 * Delete route
 * @param {number} index - Route index
 */
export function deleteRoute(index) {
    if (confirm('Удалить этот маршрут?')) {
        appState.routes.splice(index, 1);
        renderRoutesTable();
        updateDashboard();
        saveToLocalStorage();
        showNotification('Маршрут удален', 'success');
    }
}

/**
 * Populate port dropdown
 * @param {string} elementId - Dropdown element ID
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
 * Setup form handlers for CRUD operations
 */
export function setupFormHandlers() {
    // Vessel form
    document.getElementById('vesselForm')?.addEventListener('submit', function(e) {
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
        
        // Validation
        if (window.apiValidator) {
            const validation = window.apiValidator.validateAndSanitize('vessel', vesselData);
            
            if (!validation.valid) {
                window.apiValidator.displayErrors(validation.errors);
                return;
            }
            
            // Use validation.data (sanitized) instead of vesselData
            if (editId) {
                const index = appState.vessels.findIndex(v => v.id === editId);
                if (index !== -1) {
                    appState.vessels[index] = validation.data;
                    showNotification('Судно обновлено', 'success');
                }
            } else {
                appState.vessels.push(validation.data);
                showNotification('Судно добавлено', 'success');
            }
        } else {
            // No validator, use data directly
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
        }
        
        renderVesselsTable();
        updateDashboard();
        populateFilterDropdowns();
        closeVesselModal();
        saveToLocalStorage();
    });
    
    // Cargo form
    document.getElementById('cargoForm')?.addEventListener('submit', function(e) {
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
            operationalCost: parseFloat(document.getElementById('operationalCost')?.value || 0),
            overheadCost: parseFloat(document.getElementById('overheadCost')?.value || 0),
            otherCost: parseFloat(document.getElementById('otherCost')?.value || 0),
            status: 'Pending'
        };
        
        // Validation
        if (window.apiValidator) {
            const validation = window.apiValidator.validateAndSanitize('cargo', cargoData);
            
            if (!validation.valid) {
                window.apiValidator.displayErrors(validation.errors, 'cargo-errors');
                return;
            }
            
            if (editId) {
                const index = appState.cargo.findIndex(c => c.id === editId);
                if (index !== -1) {
                    validation.data.status = appState.cargo[index].status;
                    appState.cargo[index] = validation.data;
                    showNotification('Груз обновлен', 'success');
                }
            } else {
                appState.cargo.push(validation.data);
                showNotification('Груз добавлен', 'success');
            }
        } else {
            if (editId) {
                const index = appState.cargo.findIndex(c => c.id === editId);
                if (index !== -1) {
                    cargoData.status = appState.cargo[index].status;
                    appState.cargo[index] = cargoData;
                    showNotification('Груз обновлен',  'success');
                }
            } else {
                appState.cargo.push(cargoData);
                showNotification('Груз добавлен', 'success');
            }
        }
        
        renderCargoTable();
        updateDashboard();
        populateFilterDropdowns();
        closeCargoModal();
        saveToLocalStorage();
    });
    
    // Route form
    document.getElementById('routeForm')?.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const routeData = {
            from: document.getElementById('routeFrom').value,
            to: document.getElementById('routeTo').value,
            distance: parseInt(document.getElementById('routeDistance').value),
            canal: document.getElementById('routeCanal')?.value || ''
        };
        
        appState.routes.push(routeData);
        renderRoutesTable();
        updateDashboard();
        closeRouteModal();
        saveToLocalStorage();
        showNotification('Маршрут добавлен', 'success');
    });
    
    // Modal close on background click
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('show');
        }
    });
}
