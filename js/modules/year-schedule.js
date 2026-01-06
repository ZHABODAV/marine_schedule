/**
 * Year Schedule Module
 * Handles year schedule generation, visualization, and management
 */

import { appState } from '../core/app-state.js';
import { showNotification } from '../core/utils.js';
import { apiClient } from '../services/api-client.js';

export class YearScheduleManager {
    constructor(state, storage) {
        this.state = state;
        this.storage = storage;
    }

    async generateYearSchedule() {
        generateYearSchedule();
    }
}

/**
 * Generate year schedule based on parameters
 */
export async function generateYearSchedule() {
    const startDate = document.getElementById('yearScheduleStartDate').value;
    const period = parseInt(document.getElementById('yearSchedulePeriod').value);
    const turnaround = parseFloat(document.getElementById('yearScheduleTurnaround').value);
    const basePlan = document.getElementById('yearScheduleBasePlan').value;
    
    // Calculate end date based on period
    const start = new Date(startDate);
    const end = new Date(start);
    end.setMonth(end.getMonth() + period);
    const endDate = end.toISOString().split('T')[0];

    const config = {
        module: appState.currentModule,
        strategy: 'balance', // Default strategy
        config: {
            start_date: startDate,
            end_date: endDate,
            min_utilization_pct: 70.0,
            max_utilization_pct: 95.0,
            bunker_optimization: true
        },
        save_as: `schedule_${new Date().getTime()}`
    };

    showNotification('Генерация годового расписания...', 'info');
    
    const resultsContainer = document.getElementById('yearScheduleResults');
    resultsContainer.innerHTML = '<div class="loading">Генерация расписания... Это может занять некоторое время.</div>';

    try {
        const result = await apiClient.request('POST', '/api/schedule/year', config);
        
        if (result.success) {
            renderYearScheduleResults(result.data);
            showNotification('Годовое расписание сгенерировано', 'success');
        } else {
            resultsContainer.innerHTML = `<div class="error-message">Ошибка: ${result.error || 'Unknown error'}</div>`;
            showNotification('Ошибка генерации расписания', 'error');
        }
    } catch (error) {
        console.error('Error generating year schedule:', error);
        resultsContainer.innerHTML = `<div class="error-message">Ошибка: ${error.message}</div>`;
        showNotification('Ошибка генерации расписания', 'error');
    }
}

/**
 * Render year schedule results
 * @param {Object} data - Result data from API
 */
function renderYearScheduleResults(data) {
    const container = document.getElementById('yearScheduleResults');
    if (!container) return;

    const kpis = data.kpis || {};
    const conflicts = data.conflicts || { count: 0, details: [] };

    container.innerHTML = `
        <div class="section" style="background-color: var(--bg-tertiary);">
            <h3>Результаты оптимизации (${data.strategy})</h3>
            
            <div class="cards-grid">
                <div class="card">
                    <h3>Выручка</h3>
                    <div class="stat-value">$${(kpis.total_revenue_usd || 0).toLocaleString()}</div>
                </div>
                <div class="card">
                    <h3>Прибыль</h3>
                    <div class="stat-value" style="color: var(--accent-success);">$${(kpis.total_profit_usd || 0).toLocaleString()}</div>
                </div>
                <div class="card">
                    <h3>Рейсов</h3>
                    <div class="stat-value">${kpis.total_voyages || 0}</div>
                </div>
                <div class="card">
                    <h3>Утилизация</h3>
                    <div class="stat-value">${(kpis.fleet_utilization_pct || 0).toFixed(1)}%</div>
                </div>
            </div>

            <div style="margin-top: 2rem;">
                <h4>Конфликты (${conflicts.count})</h4>
                ${conflicts.count > 0 ? `
                    <ul style="color: var(--accent-danger);">
                        ${conflicts.details.map(c => `<li>${c.message || JSON.stringify(c)}</li>`).join('')}
                    </ul>
                ` : '<p style="color: var(--accent-success);">Конфликтов не обнаружено</p>'}
            </div>

            <div style="margin-top: 2rem; display: flex; gap: 1rem;">
                <button class="btn-primary" onclick="window.open('/api/export/gantt?schedule_id=${data.schedule_id}', '_blank')">Скачать Gantt (Excel)</button>
                <button class="btn-secondary" onclick="window.open('/api/export/report?schedule_id=${data.schedule_id}', '_blank')">Скачать отчет</button>
            </div>
        </div>
    `;
}

// Export functions to window for HTML onclick handlers
if (typeof window !== 'undefined') {
    window.generateYearSchedule = generateYearSchedule;
}