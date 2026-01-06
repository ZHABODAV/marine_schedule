// ===== VOYAGE BUILDER MODULE =====
// Purpose: Interactive voyage creation and leg management
// Lines extracted from vessel_scheduler_enhanced.js: 1935-2121

import { appState, getCurrentData } from '../core/app-state.js';
import { showNotification } from '../core/utils.js';
import { saveToLocalStorage } from '../services/storage-service.js';

export class VoyageBuilder {
  constructor(state, storage) {
    this.state = state;
    this.storage = storage;
  }

  addVoyageLeg() {
    addVoyageLeg();
  }

  moveLegUp(btn) {
    moveLegUp(btn);
  }

  moveLegDown(btn) {
    moveLegDown(btn);
  }

  removeVoyageLeg(legId) {
    removeVoyageLeg(legId);
  }

  validateVoyage() {
    validateVoyage();
  }

  saveVoyageTemplate() {
    saveVoyageTemplate();
  }

  populateVoyageVesselSelect() {
    populateVoyageVesselSelect();
  }

  setCargo(cargoId) {
    setCargo(cargoId);
  }
}

// ===== VOYAGE BUILDER =====
export function setCargo(cargoId) {
  appState.voyageBuilder.currentCargoId = cargoId;
  const cargo = appState.cargo.find(c => c.id === cargoId);
  if (cargo) {
    showNotification(`Груз ${cargo.commodity} (${cargo.quantity} MT) выбран для рейса`, 'info');
    // Update UI to show selected cargo
    const container = document.getElementById('voyageBuilderCargoInfo');
    if (container) {
      container.innerHTML = `
                <div class="info-box" style="margin-bottom: 1rem; border-left-color: var(--accent-primary);">
                    <strong>Выбранный груз:</strong> ${cargo.commodity}<br>
                    ${cargo.quantity} MT | ${cargo.loadPort} → ${cargo.dischPort}<br>
                    <button class="btn-sm btn-secondary" onclick="voyageBuilder.setCargo(null)">Отменить</button>
                </div>
            `;
    }
  } else {
    appState.voyageBuilder.currentCargoId = null;
    const container = document.getElementById('voyageBuilderCargoInfo');
    if (container) {container.innerHTML = '';}
  }
}

export function addVoyageLeg() {
  const container = document.getElementById('voyageLegsContainer');
  const legId = appState.voyageBuilder.currentLegs.length;
    
  const legDiv = document.createElement('div');
  legDiv.className = 'leg-item';
  legDiv.id = `leg-${legId}`;
  legDiv.innerHTML = `
        <div>
            <label style="font-size: 0.8rem; color: var(--text-muted);">Тип</label>
            <select id="leg-type-${legId}" name="leg-type-${legId}" class="leg-type" autocomplete="off">
                <option value="ballast">Балласт</option>
                <option value="loading">Погрузка</option>
                <option value="transit">Транзит (Груз)</option>
                <option value="discharge">Выгрузка</option>
                <option value="canal">Канал</option>
                <option value="bunker">Бункеровка</option>
                <option value="waiting">Ожидание</option>
            </select>
        </div>
        <div>
            <label style="font-size: 0.8rem; color: var(--text-muted);">Откуда</label>
            <input type="text" id="leg-from-${legId}" name="leg-from-${legId}" class="leg-from" placeholder="Порт/Место" autocomplete="off">
        </div>
        <div>
            <label style="font-size: 0.8rem; color: var(--text-muted);">Куда</label>
            <input type="text" id="leg-to-${legId}" name="leg-to-${legId}" class="leg-to" placeholder="Порт/Место" autocomplete="off">
        </div>
        <div>
            <label style="font-size: 0.8rem; color: var(--text-muted);">Дистанция (nm)</label>
            <input type="number" id="leg-distance-${legId}" name="leg-distance-${legId}" class="leg-distance" placeholder="0" autocomplete="off">
        </div>
        <div style="display: flex; gap: 0.25rem;">
            <button class="btn-secondary btn-small" onclick="voyageBuilder.moveLegUp(this)" title="Вверх">↑</button>
            <button class="btn-secondary btn-small" onclick="voyageBuilder.moveLegDown(this)" title="Вниз">↓</button>
            <button class="btn-danger btn-small" onclick="voyageBuilder.removeVoyageLeg(${legId})">✕</button>
        </div>
    `;
    
  container.appendChild(legDiv);
  appState.voyageBuilder.currentLegs.push({ id: legId });
}

export function moveLegUp(btn) {
  const row = btn.closest('.leg-item');
  const prev = row.previousElementSibling;
  if (prev) {
    row.parentNode.insertBefore(row, prev);
  }
}

export function moveLegDown(btn) {
  const row = btn.closest('.leg-item');
  const next = row.nextElementSibling;
  if (next) {
    row.parentNode.insertBefore(next, row);
  }
}

export function removeVoyageLeg(legId) {
  const legDiv = document.getElementById(`leg-${legId}`);
  if (legDiv) {
    legDiv.remove();
  }
  appState.voyageBuilder.currentLegs = appState.voyageBuilder.currentLegs.filter(l => l.id !== legId);
}

export function validateVoyage() {
  const container = document.getElementById('voyageLegsContainer');
  const legItems = container.querySelectorAll('.leg-item');
    
  if (legItems.length === 0) {
    showNotification('Нет этапов для проверки. Добавьте хотя бы один этап.', 'warning');
    return;
  }

  const legs = [];
  let isValid = true;
  const errors = [];

  legItems.forEach((item, idx) => {
    const type = item.querySelector('.leg-type').value;
    const from = item.querySelector('.leg-from').value;
    const to = item.querySelector('.leg-to').value;
    const distance = parseInt(item.querySelector('.leg-distance').value) || 0;

    if (!from || !to) {
      errors.push(`Этап ${idx + 1}: Порты Откуда/Куда обязательны`);
      isValid = false;
    }

    if (distance <= 0 && ['ballast', 'transit', 'canal'].includes(type)) {
      errors.push(`Этап ${idx + 1}: Дистанция должна быть > 0 для ${type}`);
      isValid = false;
    }

    legs.push({ type, from, to, distance });
  });

  const validationDiv = document.getElementById('voyageValidation');
    
  if (isValid) {
    validationDiv.innerHTML = `
            <div class="info-box" style="border-left-color: var(--accent-success);">
                <h3 style="color: var(--accent-success);">✓ Проверка пройдена</h3>
                <p>Все ${legs.length} этапов корректны. Вы можете сохранить этот рейс как шаблон.</p>
            </div>
        `;
    appState.voyageBuilder.lastValidation = { valid: true, legs };
  } else {
    validationDiv.innerHTML = `
            <div class="info-box" style="border-left-color: var(--accent-danger);">
                <h3 style="color: var(--accent-danger);">✗ Ошибка проверки</h3>
                <ul>${errors.map(e => `<li>${e}</li>`).join('')}</ul>
            </div>
        `;
    appState.voyageBuilder.lastValidation = { valid: false, errors };
  }
}

export function saveVoyageTemplate() {
  if (!appState.voyageBuilder.lastValidation || !appState.voyageBuilder.lastValidation.valid) {
    showNotification('Пожалуйста, сначала проверьте рейс', 'warning');
    return;
  }

  const templateName = prompt('Введите название шаблона:');
  if (!templateName) {return;}

  // Construct template object matching backend schema
  const legs = appState.voyageBuilder.lastValidation.legs;
  const ports = [...new Set(legs.map(l => l.from).concat(legs.map(l => l.to)))];
  const totalDistance = legs.reduce((sum, l) => sum + (l.distance || 0), 0);
  const estDays = Math.ceil(totalDistance / (12 * 24)) + legs.length; // Rough estimate: 12kn + 1 day per leg port time

  const template = {
    name: templateName,
    description: 'Created via Voyage Builder',
    category: 'Custom',
    ports: ports,
    estimatedDays: estDays,
    legs: legs, // Extra field, backend might ignore but useful if we extend schema
    cargoId: appState.voyageBuilder.currentCargoId || null,
    costAllocations: {
      operationalCost: 0,
      overheadCost: 0,
      otherCost: 0
    }
  };

  // Save to backend
  fetch('/api/voyage-templates', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(template)
  })
    .then(response => response.json())
    .then(result => {
      if (result.success) {
        // Also save locally for immediate UI update
        const data = getCurrentData();
        data.computed.voyageTemplates.push({
          ...template,
          id: result.template_id,
          createdAt: new Date().toISOString()
        });
        saveToLocalStorage();
        showNotification(`Шаблон рейса "${templateName}" сохранен на сервере`, 'success');
      } else {
        throw new Error(result.error || 'Unknown error');
      }
    })
    .catch(error => {
      console.error('Error saving template:', error);
      showNotification('Ошибка сохранения шаблона: ' + error.message, 'error');
        
      // Fallback to local save if server fails
      const data = getCurrentData();
      data.computed.voyageTemplates.push({
        ...template,
        id: 'local_' + Date.now(),
        createdAt: new Date().toISOString()
      });
      saveToLocalStorage();
      showNotification('Шаблон сохранен локально (ошибка сервера)', 'warning');
    });
}

export function populateVoyageVesselSelect() {
  const select = document.getElementById('voyageVesselSelect');
  if (!select) {return;}

  const vessels = appState.vessels.filter(v => v.status === 'Active');
  select.innerHTML = '<option value="">Выберите судно...</option>' +
        vessels.map(v => `<option value="${v.id}">${v.name} (${v.class}, ${v.dwt} DWT)</option>`).join('');
}

// Export all functions as a namespace for global access
export const voyageBuilder = {
  addVoyageLeg,
  moveLegUp,
  moveLegDown,
  removeVoyageLeg,
  validateVoyage,
  saveVoyageTemplate,
  populateVoyageVesselSelect
};

// Also attach to window for onclick handlers
if (typeof window !== 'undefined') {
  window.voyageBuilder = voyageBuilder;
  window.addVoyageLeg = addVoyageLeg;
  window.validateVoyage = validateVoyage;
  window.saveVoyageTemplate = saveVoyageTemplate;
  // Add setCargo to window.voyageBuilder for the onclick handler in the info box
  window.voyageBuilder.setCargo = setCargo;
}