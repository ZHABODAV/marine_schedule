/**
 * Trading Lanes Management Module
 * Handles all trading lane operations: creation, rendering, vessel assignment, volume placement
 * Extracted from vessel_scheduler_enhanced.js (lines 3796-4463)
 */

import { appState, tradingLanesState, getCurrentData } from '../core/app-state.js';
import { showNotification, formatDate } from '../core/utils.js';
import { saveToLocalStorage } from '../services/storage-service.js';
import { apiClient } from '../services/api-client.js';

export class TradingLanes {
    constructor(state, storage) {
        this.state = state;
        this.storage = storage;
    }

    generateTradingLanes() {
        generateTradingLanes();
    }

    renderTradingLanes() {
        renderTradingLanes();
    }

    editTradingLane(laneId) {
        editTradingLane(laneId);
    }

    assignVesselsToLane(laneId) {
        assignVesselsToLane(laneId);
    }

    applyTemplateToLaneVoyages(laneId) {
        applyTemplateToLaneVoyages(laneId);
    }

    placeVolumeInTradingLanes() {
        placeVolumeInTradingLanes();
    }

    confirmVolumePlacement(targetVolume) {
        confirmVolumePlacement(targetVolume);
    }

    createShipmentsFromPlacement(placements) {
        createShipmentsFromPlacement(placements);
    }
}

/**
 * Generate trading lanes (shows creation modal)
 */
export function generateTradingLanes() {
    showCreateTradingLaneModal();
}

/**
 * Show modal for creating new trading lane
 */
export function showCreateTradingLaneModal() {
    const data = getCurrentData();
    
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
                    <input type="text" id="laneName" name="laneName" placeholder="например: Балаково-Астрахань" autocomplete="off" required>
                </div>
                <div class="form-group">
                    <label>Порт погрузки:</label>
                    <select id="laneLoadPort" name="laneLoadPort" autocomplete="off" required>
                        <option value="">Выберите порт...</option>
                        ${uniquePorts.map(port => `<option value="${port}">${port}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>Порт выгрузки:</label>
                    <select id="laneDischargePort" name="laneDischargePort" autocomplete="off" required>
                        <option value="">Выберите порт...</option>
                        ${uniquePorts.map(port => `<option value="${port}">${port}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>Целевой объем (MT/месяц):</label>
                    <input type="number" id="laneTargetVolume" name="laneTargetVolume" placeholder="50000" min="0" autocomplete="off" required>
                </div>
                <div class="form-group">
                    <label>Целевая частота (рейсов/месяц):</label>
                    <input type="number" id="laneTargetFrequency" name="laneTargetFrequency" placeholder="4" min="1" autocomplete="off" required>
                </div>
                <div class="form-group">
                    <label>Категория линии:</label>
                    <select id="laneCategory" name="laneCategory" autocomplete="off">
                        <option value="regular">Регулярная</option>
                        <option value="seasonal">Сезонная</option>
                        <option value="spot">Разовая</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Шаблон рейса (опционально):</label>
                    <select id="laneTemplate" name="laneTemplate" autocomplete="off">
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
    
    modal.querySelector('#createLaneForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const laneData = {
            id: `LANE-${Date.now()}`,
            name: document.getElementById('laneName').value,
            loadPort: document.getElementById('laneLoadPort').value,
            dischPort: document.getElementById('laneDischargePort').value,
            totalVolume: parseInt(document.getElementById('laneTargetVolume').value),
            frequency: parseInt(document.getElementById('laneTargetFrequency').value),
            avgCargoSize: Math.round(parseInt(document.getElementById('laneTargetVolume').value) / parseInt(document.getElementById('laneTargetFrequency').value)),
            category: document.getElementById('laneCategory').value,
            voyageTemplateId: document.getElementById('laneTemplate').value || null,
            cargoIds: [],
            suitableVessels: [],
            assignedVessels: [],
            shipments: [],
            active: true,
            createdAt: new Date().toISOString()
        };
        
        // Find suitable vessels based on avg cargo size
        data.masters.vessels.forEach(v => {
            const vesselDWT = parseFloat(v.dwt) || 0;
            if (vesselDWT >= laneData.avgCargoSize * 0.7 && vesselDWT <= laneData.avgCargoSize * 1.5) {
                laneData.suitableVessels.push(v.id);
            }
        });
        
        // Save to API if endpoint exists, otherwise local
        // Assuming we might add API support later, for now local + sync
        tradingLanesState.lanes.push(laneData);
        renderTradingLanes();
        saveTradingLanesToLocalStorage();
        modal.remove();
        
        showNotification(`Торговая линия "${laneData.name}" создана`, 'success');
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

/**
 * Render trading lanes grid
 */
export function renderTradingLanes() {
    const container = document.getElementById('tradingLanesGrid');
    if (!container) return;
    
    if (tradingLanesState.lanes.length === 0) {
        container.innerHTML = '<div class="no-data">Нажмите "Генерировать линии" для создания торговых линий</div>';
        return;
    }
    
    container.innerHTML = tradingLanesState.lanes.map(lane => `
        <div class="card" style="border-left: 4px solid ${lane.active ? 'var(--accent-success)' : 'var(--text-muted)'};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin-bottom: 0.25rem; font-size: 1.2rem;">${lane.name}</h3>
                    <span class="status-badge status-${lane.active ? 'active' : 'pending'}">${lane.active ? 'Активна' : 'Неактивна'}</span>
                </div>
                <button class="btn-secondary btn-small" onclick="window.editTradingLane('${lane.id}')">Настроить</button>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1rem;">
                <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px;">
                    <div style="font-size: 0.85rem; color: var(--text-muted);">Общий объем</div>
                    <div style="font-weight: 600; color: var(--accent-primary);">${lane.totalVolume.toLocaleString()} MT</div>
                </div>
                <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px;">
                    <div style="font-size: 0.85rem; color: var(--text-muted);">Частота</div>
                    <div style="font-weight: 600;">${lane.frequency} грузов</div>
                </div>
            </div>
            
            <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem;">
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Подходящие суда</div>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    ${lane.suitableVessels.slice(0, 5).map(vId => {
                        const vessel = appState.vessels.find(v => v.id === vId);
                        return vessel ? `<span style="padding: 0.25rem 0.75rem; background: var(--bg-secondary); border-radius: 12px; font-size: 0.85rem;">${vessel.name}</span>` : '';
                    }).join('')}
                    ${lane.suitableVessels.length > 5 ? `<span style="color: var(--text-muted); font-size: 0.85rem;">+${lane.suitableVessels.length - 5} еще</span>` : ''}
                </div>
            </div>
            
            ${lane.voyageTemplateId ? `
                <div style="background: var(--bg-tertiary); padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; border-left: 3px solid var(--accent-primary);">
                    <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.25rem;"> Шаблон рейса</div>
                    <div style="font-weight: 600; color: var(--accent-primary);">${getTemplateNameById(lane.voyageTemplateId)}</div>
                </div>
            ` : ''}
            
            <button class="btn-primary" style="width: 100%; margin-bottom: 0.5rem;" onclick="window.assignVesselsToLane('${lane.id}')">Назначить суда на линию</button>
            ${lane.voyageTemplateId ? `
                <button class="btn-secondary" style="width: 100%;" onclick="window.applyTemplateToLaneVoyages('${lane.id}')">Применить шаблон к рейсам</button>
            ` : ''}
        </div>
    `).join('');
}

/**
 * Edit trading lane settings
 * @param {string} laneId - Lane ID to edit
 */
export function editTradingLane(laneId) {
    const lane = tradingLanesState.lanes.find(l => l.id === laneId);
    if (!lane) return;
    
    // Get available templates from API
    fetch('/api/voyage-templates')
        .then(r => r.json())
        .then(templateData => {
            const templates = templateData.templates || [];
            
            // Create modal for editing
            const modal = document.createElement('div');
            modal.className = 'modal show';
            modal.innerHTML = `
                <div class="modal-content">
                    <h2>Настройка торговой линии: ${lane.name}</h2>
                    <form id="editLaneForm">
                        <div class="form-group">
                            <label>Название линии:</label>
                            <input type="text" id="laneName" name="laneName" value="${lane.name}" autocomplete="off" required>
                        </div>
                        <div class="form-group">
                            <label>Целевой объем (MT/месяц):</label>
                            <input type="number" id="laneTargetVolume" name="laneTargetVolume" value="${lane.totalVolume}" min="0" autocomplete="off">
                        </div>
                        <div class="form-group">
                            <label>Целевая частота (рейсов/месяц):</label>
                            <input type="number" id="laneFrequency" name="laneFrequency" value="${lane.frequency}" min="1" autocomplete="off">
                        </div>
                        <div class="form-group">
                            <label>Шаблон рейса:</label>
                            <select id="laneVoyageTemplate" name="laneVoyageTemplate" autocomplete="off">
                                <option value="">Без шаблона</option>
                                ${templates.map(t => `
                                    <option value="${t.id}" ${lane.voyageTemplateId === t.id ? 'selected' : ''}>${t.name} (${t.category})</option>
                                `).join('')}
                            </select>
                            <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
                                Шаблон определяет стандартную последовательность этапов для рейсов на этой линии
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Статус:</label>
                            <select id="laneActive" name="laneActive" autocomplete="off">
                                <option value="true" ${lane.active ? 'selected' : ''}>Активна</option>
                                <option value="false" ${!lane.active ? 'selected' : ''}>Неактивна</option>
                            </select>
                        </div>
                        <div class="modal-buttons">
                            <button type="submit" class="btn-primary">Сохранить</button>
                            <button type="button" class="btn-secondary" onclick="this.closest('.modal').remove()">Отмена</button>
                        </div>
                    </form>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            modal.querySelector('#editLaneForm').addEventListener('submit', (e) => {
                e.preventDefault();
                
                lane.name = document.getElementById('laneName').value;
                lane.totalVolume = parseInt(document.getElementById('laneTargetVolume').value);
                lane.frequency = parseInt(document.getElementById('laneFrequency').value);
                lane.voyageTemplateId = document.getElementById('laneVoyageTemplate').value || null;
                lane.active = document.getElementById('laneActive').value === 'true';
                
                renderTradingLanes();
                saveTradingLanesToLocalStorage();
                modal.remove();
                
                showNotification('Торговая линия обновлена', 'success');
            });
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) modal.remove();
            });
        })
        .catch(error => {
            console.error('Error loading templates:', error);
            showNotification('Ошибка загрузки шаблонов', 'error');
        });
}

/**
 * Assign vessels to a trading lane
 * @param {string} laneId - Lane ID to assign vessels to
 */
export function assignVesselsToLane(laneId) {
    const lane = tradingLanesState.lanes.find(l => l.id === laneId);
    if (!lane) return;
    
    // Get cargos for this lane
    const laneCargos = appState.cargo.filter(c => lane.cargoIds.includes(c.id));
    
    if (laneCargos.length === 0) {
        // Switch to assignment tab for manual assignment
        if (window.switchTab) {
            window.switchTab('vesselCargoAssignment');
        }
        showNotification(`Назначение судов для линии ${lane.name}`, 'info');
        return;
    }
    
    // Auto-assign suitable vessels
    lane.suitableVessels.forEach((vesselId, idx) => {
        if (idx < laneCargos.length) {
            const cargo = laneCargos[idx];
            tradingLanesState.assignments.set(cargo.id, {
                vesselId: vesselId,
                laneId: laneId,
                status: 'assigned',
                assignedAt: new Date().toISOString()
            });
            cargo.status = 'Assigned';
        }
    });
    
    lane.assignedVessels = lane.suitableVessels.slice(0, laneCargos.length);
    
    renderTradingLanes();
    if (window.renderVesselCargoAssignments) {
        window.renderVesselCargoAssignments();
    }
    if (window.updateDashboard) {
        window.updateDashboard();
    }
    saveTradingLanesToLocalStorage();
    
    showNotification(`Назначено ${lane.assignedVessels.length} судов на линию ${lane.name}`, 'success');
}

/**
 * Apply voyage template to all voyages in a lane
 * @param {string} laneId - Lane ID to apply template to
 */
export function applyTemplateToLaneVoyages(laneId) {
    const lane = tradingLanesState.lanes.find(l => l.id === laneId);
    if (!lane || !lane.voyageTemplateId) {
        showNotification('Нет шаблона для применения', 'warning');
        return;
    }
    
    // Load template from API or local storage
    fetch('/api/voyage-templates')
        .then(r => r.json())
        .then(templateData => {
            const template = templateData.templates.find(t => t.id === lane.voyageTemplateId);
            
            if (!template) {
                showNotification('Шаблон не найден', 'error');
                return;
            }
            
            // Apply template to all cargos in this lane
            const laneCargos = appState.cargo.filter(c => lane.cargoIds.includes(c.id));
            let applied = 0;
            
            laneCargos.forEach(cargo => {
                // Create voyage from template for this cargo
                const voyageId = `VOY-${Date.now()}-${cargo.id}`;
                const data = getCurrentData();
                
                // Find or create voyage structure
                const voyage = {
                    id: voyageId,
                    vesselId: null, // Will be assigned separately
                    commitmentId: cargo.id,
                    laneId: laneId,
                    templateId: template.id,
                    legs: template.legs || [],
                    status: 'planned',
                    createdAt: new Date().toISOString()
                };
                
                data.computed.voyages.push(voyage);
                applied++;
            });
            
            saveToLocalStorage();
            showNotification(`Шаблон "${template.name}" применен к ${applied} рейсам линии ${lane.name}`, 'success');
        })
        .catch(error => {
            console.error('Error applying template:', error);
            showNotification('Ошибка применения шаблона', 'error');
        });
}

/**
 * Place volume into trading lanes (reverse sales planning)
 */
export function placeVolumeInTradingLanes() {
    const targetVolume = parseInt(prompt('Введите целевой объем для размещения (MT):'));
    if (!targetVolume || targetVolume <= 0) return;
    
    if (tradingLanesState.lanes.length === 0) {
        showNotification('Сначала сгенерируйте торговые линии', 'warning');
        return;
    }
    
    // Show lane selection modal
    const activeLanes = tradingLanesState.lanes.filter(l => l.active);
    
    if (activeLanes.length === 0) {
        showNotification('Нет активных линий', 'error');
        return;
    }
    
    // Create modal for lane selection
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Выберите линию для размещения ${targetVolume.toLocaleString()} MT</h2>
            <div class="form-group">
                <label>Торговая линия:</label>
                <select id="targetLaneSelect" name="targetLaneSelect" class="select-input" style="width: 100%;" autocomplete="off">
                    ${activeLanes.map(lane => `
                        <option value="${lane.id}">${lane.name} (${lane.totalVolume.toLocaleString()} MT, ${lane.frequency} рейсов)</option>
                    `).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Средний размер отгрузки (MT):</label>
                <input type="number" id="avgShipmentSize" name="avgShipmentSize" value="${Math.round(targetVolume / 10)}" min="1000" step="1000" autocomplete="off">
            </div>
            <div class="modal-buttons">
                <button class="btn-primary" onclick="window.confirmVolumePlacement(${targetVolume}); this.closest('.modal').remove();">Разместить</button>
                <button class="btn-secondary" onclick="this.closest('.modal').remove()">Отмена</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

/**
 * Confirm volume placement and create shipments
 * @param {number} targetVolume - Target volume to place
 */
export function confirmVolumePlacement(targetVolume) {
    const laneId = document.getElementById('targetLaneSelect')?.value;
    const avgShipmentSize = parseInt(document.getElementById('avgShipmentSize')?.value || targetVolume / 10);
    
    const lane = tradingLanesState.lanes.find(l => l.id === laneId);
    if (!lane) {
        showNotification('Линия не найдена', 'error');
        return;
    }
    
    const shipments = Math.ceil(targetVolume / avgShipmentSize);
    
    const placement = [{
        laneId: lane.id,
        laneName: lane.name,
        allocatedVolume: targetVolume,
        shipments: shipments,
        avgShipmentSize: avgShipmentSize
    }];
    
    displayVolumePlacement(targetVolume, placement);
}

/**
 * Display volume placement results
 * @param {number} targetVolume - Target volume
 * @param {Array} placements - Placement results
 */
function displayVolumePlacement(targetVolume, placements) {
    // Create modal to show results
    const modal = document.createElement('div');
    modal.className = 'modal show';
    const placementsJson = JSON.stringify(placements).replace(/"/g, '"');
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Размещение объема ${targetVolume.toLocaleString()} MT</h2>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Линия</th>
                            <th>Объем (MT)</th>
                            <th>Рейсов</th>
                            <th>Средний груз (MT)</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${placements.map(p => `
                            <tr>
                                <td>${p.laneName}</td>
                                <td>${p.allocatedVolume.toLocaleString()}</td>
                                <td>${p.shipments}</td>
                                <td>${p.avgShipmentSize.toLocaleString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <div class="modal-buttons" style="margin-top: 1.5rem;">
                <button class="btn-primary" onclick='window.createShipmentsFromPlacement(${placementsJson}); this.closest(".modal").remove();'>Создать отгрузки</button>
                <button class="btn-secondary" onclick="this.closest('.modal').remove()">Отмена</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

/**
 * Create shipments from volume placement
 * @param {Array} placements - Placement data
 */
export function createShipmentsFromPlacement(placements) {
    const data = getCurrentData();
    let createdCount = 0;
    
    placements.forEach(placement => {
        const lane = tradingLanesState.lanes.find(l => l.id === placement.laneId);
        if (!lane) return;
        
        // Create shipments for this lane
        for (let i = 0; i < placement.shipments; i++) {
            const shipmentId = `SHIP-${Date.now()}-${i}`;
            const shipment = {
                id: shipmentId,
                commodity: 'General Cargo', // Default, should be customizable
                quantity: placement.avgShipmentSize,
                loadPort: lane.loadPort,
                dischPort: lane.dischPort,
                laycanStart: new Date(Date.now() + i * 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10), // Weekly intervals
                laycanEnd: new Date(Date.now() + (i * 7 + 3) * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
                status: 'Pending',
                laneId: lane.id,
                source: 'volume_placement'
            };
            
            // Add to local state
            appState.cargo.push(shipment);
            lane.shipments.push(shipmentId);
            createdCount++;
            
            // Try to save to API
            apiClient.createCargo(shipment).catch(err => console.error('Failed to sync shipment to API', err));
        }
    });
    
    if (window.renderCargoTable) {
        window.renderCargoTable();
    }
    if (window.updateDashboard) {
        window.updateDashboard();
    }
    saveTradingLanesToLocalStorage();
    
    showNotification(`Создано ${createdCount} новых отгрузок`, 'success');
}

/**
 * Save trading lanes to localStorage
 */
function saveTradingLanesToLocalStorage() {
    // Save trading lanes state with serializable Map
    const tradingLanesData = {
        lanes: tradingLanesState.lanes,
        assignmentsArray: Array.from(tradingLanesState.assignments.entries())
    };
    
    const storageData = JSON.parse(localStorage.getItem('vesselSchedulerDataEnhanced') || '{}');
    storageData.tradingLanes = tradingLanesData;
    localStorage.setItem('vesselSchedulerDataEnhanced', JSON.stringify(storageData));
}

/**
 * Get template name by ID
 * @param {string} templateId - Template ID
 * @returns {string} Template name
 */
function getTemplateNameById(templateId) {
    // Try to get from local computed templates first
    const data = getCurrentData();
    const localTemplate = data.computed.voyageTemplates.find(t => t.id === templateId);
    if (localTemplate) {
        return localTemplate.name;
    }
    
    // Return template ID if not found (will be replaced when templates load)
    return templateId || 'Unknown Template';
}

// Export functions to window for HTML onclick handlers
if (typeof window !== 'undefined') {
    window.generateTradingLanes = generateTradingLanes;
    window.renderTradingLanes = renderTradingLanes;
    window.editTradingLane = editTradingLane;
    window.assignVesselsToLane = assignVesselsToLane;
    window.applyTemplateToLaneVoyages = applyTemplateToLaneVoyages;
    window.placeVolumeInTradingLanes = placeVolumeInTradingLanes;
    window.confirmVolumePlacement = confirmVolumePlacement;
    window.createShipmentsFromPlacement = createShipmentsFromPlacement;
}