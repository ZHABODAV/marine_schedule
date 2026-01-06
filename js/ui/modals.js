// ===== MODALS MODULE =====
// Modal dialogs for vessel, cargo, and route management

import { appState } from '../core/app-state.js';
import { showNotification, formatDate } from '../core/utils.js';

/**
 * Open vessel add/edit modal
 * @param {string|null} id - Vessel ID for editing, null for adding new
 */
export function openVesselModal(id = null) {
    const modal = document.getElementById('vesselModal');
    if (!modal) return;

    if (id) {
        // Edit mode
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
    } else {
        // Add mode
        document.getElementById('vesselModalTitle').textContent = 'Добавить судно';
        document.getElementById('vesselEditId').value = '';
        document.getElementById('vesselForm').reset();
    }
    
    modal.style.display = 'flex';
    modal.classList.add('show');
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
 * Open cargo add/edit modal
 * @param {string|null} id - Cargo ID for editing, null for adding new
 */
export function openCargoModal(id = null) {
    const modal = document.getElementById('cargoModal');
    if (!modal) return;

    // Populate port dropdowns
    populatePortDropdown('loadPort');
    populatePortDropdown('dischPort');

    if (id) {
        // Edit mode
        const cargo = appState.cargo.find(c => c.id === id);
        if (!cargo) {
            showNotification('Груз не найден', 'error');
            return;
        }
        
        document.getElementById('cargoModalTitle').textContent = 'Редактировать груз';
        document.getElementById('cargoEditId').value = id;
        document.getElementById('cargoId').value = cargo.id;
        document.getElementById('commodity').value = cargo.commodity;
        document.getElementById('quantity').value = cargo.quantity;
        document.getElementById('loadPort').value = cargo.loadPort;
        document.getElementById('dischPort').value = cargo.dischPort;
        document.getElementById('laycanStart').value = cargo.laycanStart;
        document.getElementById('laycanEnd').value = cargo.laycanEnd;
    } else {
        // Add mode
        document.getElementById('cargoModalTitle').textContent = 'Добавить груз';
        document.getElementById('cargoEditId').value = '';
        document.getElementById('cargoForm').reset();
    }
    
    modal.style.display = 'flex';
    modal.classList.add('show');
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
 * Open route add modal
 */
export function openRouteModal() {
    const modal = document.getElementById('routeModal');
    if (!modal) return;

    // Populate port dropdowns
    populatePortDropdown('routeFrom');
    populatePortDropdown('routeTo');
    
    modal.classList.add('show');
    modal.style.display = 'flex';
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
 * Display voyage details in a modal
 * @param {string} voyageId - Voyage ID to display
 */
export function showVoyageDetailsModal(voyageId) {
    const data = appState[appState.currentModule];
    const voyage = data.computed.voyages.find(v => v.id === voyageId);
    if (!voyage) return;
    
    // Create modal with voyage details
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 700px;">
            <h2>Детали рейса: ${voyage.id}</h2>
            <div class="info-box">
                <h3>Основная информация</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">Судно:</div>
                        <div style="font-weight: 600;">${voyage.vesselId || 'Не назначено'}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">Груз:</div>
                        <div style="font-weight: 600;">${voyage.commitmentId || 'Не назначен'}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">Статус:</div>
                        <div style="font-weight: 600;">${voyage.status || 'N/A'}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">Дата старта:</div>
                        <div style="font-weight: 600;">${voyage.startDate ? formatDate(voyage.startDate) : 'Не установлена'}</div>
                    </div>
                </div>
            </div>
            ${voyage.legs && voyage.legs.length > 0 ? `
                <div class="info-box" style="margin-top: 1rem;">
                    <h3>Этапы рейса (${voyage.legs.length})</h3>
                    <div class="table-container" style="margin-top: 1rem;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>№</th>
                                    <th>Тип</th>
                                    <th>Откуда</th>
                                    <th>Куда</th>
                                    <th>Дистанция</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${voyage.legs.map((leg, idx) => `
                                    <tr>
                                        <td>${idx + 1}</td>
                                        <td>${leg.type || 'N/A'}</td>
                                        <td>${leg.from || leg.port || '-'}</td>
                                        <td>${leg.to || leg.port || '-'}</td>
                                        <td>${leg.distance ? leg.distance.toLocaleString() + ' nm' : '-'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            ` : ''}
            <div class="modal-buttons" style="margin-top: 2rem;">
                <button class="btn-secondary" onclick="this.closest('.modal').remove()">Закрыть</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

/**
 * Show custom voyage selection modal for Gantt chart generation
 */
export function showCustomVoyageSelectionModal() {
    const data = appState[appState.currentModule];
    const voyages = data.computed.voyages || [];
    
    if (voyages.length === 0) {
        showNotification('Нет доступных рейсов для выбора', 'warning');
        // Reset selection to 'all'
        const selector = document.getElementById('voyageSelectionForGantt');
        if (selector) selector.value = 'all';
        return;
    }
    
    // Create modal for custom voyage selection
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <h2>Выберите рейсы для диаграммы Ганта</h2>
            <div style="margin-bottom: 1rem;">
                <button class="btn-secondary btn-small" onclick="selectAllVoyages(true)">Выбрать все</button>
                <button class="btn-secondary btn-small" onclick="selectAllVoyages(false)">Снять все</button>
            </div>
            <div style="max-height: 400px; overflow-y: auto; border: 1px solid var(--border-color); border-radius: 6px; padding: 1rem;">
                <div id="voyageCheckboxList">
                    ${voyages.map(voy => `
                        <label style="display: flex; gap: 0.75rem; padding: 0.5rem; background: var(--bg-tertiary); margin-bottom: 0.5rem; border-radius: 4px; cursor: pointer;">
                            <input type="checkbox" class="voyage-checkbox" value="${voy.id}" checked>
                            <div style="flex: 1;">
                                <div style="font-weight: 600;">${voy.id}</div>
                                <div style="font-size: 0.85rem; color: var(--text-muted);">
                                    Судно: ${voy.vesselId || 'Не назначено'} |
                                    Статус: ${voy.status || 'N/A'}
                                    ${voy.commitmentId ? `| Груз: ${voy.commitmentId}` : ''}
                                </div>
                            </div>
                        </label>
                    `).join('')}
                </div>
            </div>
            <div class="modal-buttons" style="margin-top: 1.5rem;">
                <button class="btn-primary" onclick="applyCustomVoyageSelection(); this.closest('.modal').remove();">Применить</button>
                <button class="btn-secondary" onclick="cancelCustomVoyageSelection(); this.closest('.modal').remove();">Отмена</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            cancelCustomVoyageSelection();
            modal.remove();
        }
    });
}

/**
 * Show trading lane creation modal
 */
export function showCreateTradingLaneModal() {
    const data = appState[appState.currentModule];
    
    // Get unique ports
    const uniquePorts = [...new Set(appState.ports.map(p => p.name || p.id))].filter(Boolean);
    
    // Create modal for manual lane creation
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <h2>Создать торговую линию</h2>
            <form id="createLaneForm">
                <div class="form-group">
                    <label>Название линии:</label>
                    <input type="text" id="laneName" placeholder="например: Балаково-Астрахань" required>
                </div>
                <div class="form-group">
                    <label>Порт погрузки:</label>
                    <select id="laneLoadPort" required>
                        <option value="">Выберите порт...</option>
                        ${uniquePorts.map(port => `<option value="${port}">${port}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>Порт выгрузки:</label>
                    <select id="laneDischargePort" required>
                        <option value="">Выберите порт...</option>
                        ${uniquePorts.map(port => `<option value="${port}">${port}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>Целевой объем (MT/месяц):</label>
                    <input type="number" id="laneTargetVolume" placeholder="50000" min="0" required>
                </div>
                <div class="form-group">
                    <label>Целевая частота (рейсов/месяц):</label>
                    <input type="number" id="laneTargetFrequency" placeholder="4" min="1" required>
                </div>
                <div class="form-group">
                    <label>Категория линии:</label>
                    <select id="laneCategory">
                        <option value="regular">Регулярная</option>
                        <option value="seasonal">Сезонная</option>
                        <option value="spot">Разовая</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Шаблон рейса (опционально):</label>
                    <select id="laneTemplate">
                        <option value="">Без шаблона</option>
                    </select>
                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
                        Шаблон будет загружен из доступных шаблонов
                    </div>
                </div>
                <div class="modal-buttons">
                    <button type="submit" class="btn-primary">Создать линию</button>
                    <button type="button" class="btn-secondary" onclick="this.closest('.modal').remove()">Отмена</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Load available templates
    fetch('/api/voyage-templates')
        .then(r => r.json())
        .then(templateData => {
            const templates = templateData.templates || [];
            const templateSelect = modal.querySelector('#laneTemplate');
            templateSelect.innerHTML = '<option value="">Без шаблона</option>' +
                templates.map(t => `<option value="${t.id}">${t.name} (${t.category})</option>`).join('');
        })
        .catch(error => {
            console.error('Error loading templates:', error);
        });
    
    // Handle form submission (requires trading lanes module)
    modal.querySelector('#createLaneForm').addEventListener('submit', (e) => {
        e.preventDefault();
        // This will be handled by the trading lanes module
        if (typeof window.handleCreateTradingLane === 'function') {
            window.handleCreateTradingLane(modal);
        }
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

/**
 * Helper: Populate port dropdown
 * @param {string} elementId - ID of select element
 */
function populatePortDropdown(elementId) {
    const select = document.getElementById(elementId);
    if (!select) return;
    
    const ports = appState.ports || [];
    const uniquePorts = [...new Set(ports.map(p => p.name || p.id))].filter(Boolean);
    
    select.innerHTML = '<option value="">Выберите порт...</option>' +
        uniquePorts.map(port => `<option value="${port}">${port}</option>`).join('');
}
