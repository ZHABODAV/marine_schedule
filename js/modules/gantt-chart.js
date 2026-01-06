// ===== GANTT CHART MODULE =====
// Purpose: Gantt chart generation and visualization
// Lines extracted from vessel_scheduler_enhanced.js: 1655-1933

import { appState, getCurrentData, appConfig } from '../core/app-state.js';
import { toNumber, formatDate, showNotification } from '../core/utils.js';
import { saveToLocalStorage } from '../services/storage-service.js';

// ===== GANTT GENERATION =====
export function generateGanttData(days = 30) {
    const data = getCurrentData();
    
    // First, try to use generated voyages from auto-schedule
    if (data.computed.voyages && data.computed.voyages.length > 0) {
        return generateGanttFromVoyages(data.computed.voyages, days);
    }
    
    //Otherwise, generate from commitments
    if (data.planning.commitments && data.planning.commitments.length > 0) {
        const voyages = generateAutoSchedule(); // This creates voyages
        if (voyages && voyages.length > 0) {
            return generateGanttFromVoyages(voyages, days);
        }
    }
    
    // Fallback: random generation for demo
    return generateRandomGantt(days);
}

export function generateGanttFromVoyages(voyages, days = 30) {
    const gantt = [];
    const operationMap = {
        'ballast': { label: 'Б', class: 'ballast' },
        'loading': { label: 'П', class: 'loading' },
        'transit': { label: 'Т', class: 'transit' },
        'discharge': { label: 'В', class: 'discharge' },
        'canal': { label: 'К', class: 'canal' },
        'bunker': { label: 'Ф', class: 'bunker' },
        'waiting': { label: 'О', class: 'waiting' }
    };
    
    const filteredVessels = applyFiltersToData(appState.vessels);
    const startDate = new Date();
    
    filteredVessels.forEach(vessel => {
        const row = { vessel: vessel.name, days: [] };
        
        // Initialize all days as empty
        for (let i = 0; i < days; i++) {
            row.days.push({ operation: '', class: '' });
        }
        
        // Find voyages for this vessel
        const vesselVoyages = voyages.filter(v => v.vesselId === vessel.id);
        
        vesselVoyages.forEach(voyage => {
            let currentDay = 0;
            const voyageStart = new Date(voyage.startDate);
            const dayOffset = Math.floor((voyageStart - startDate) / (1000 * 60 * 60 * 24));
            
            if (dayOffset < 0 || dayOffset >= days) return; // Voyage outside timeline
            
            currentDay = dayOffset;
            
            // Plot each leg on the timeline
            voyage.legs.forEach(leg => {
                const durationDays = Math.ceil((leg.duration || 0) / 24); // Convert hours to days
                const opInfo = operationMap[leg.type] || { label: '?', class: 'waiting' };
                
                // Apply operation type filter
                const shouldShow = appState.filters.opTypes.length === 0 ||
                                 appState.filters.opTypes.includes(opInfo.class);
                
                for (let i = 0; i < durationDays && currentDay < days; i++) {
                    if (currentDay >= 0) {
                        row.days[currentDay] = shouldShow
                            ? { operation: opInfo.label, class: opInfo.class }
                            : { operation: '', class: '' };
                    }
                    currentDay++;
                }
            });
        });
        
        gantt.push(row);
    });
    
    return gantt;
}

function generateRandomGantt(days = 30) {
    const operations = ['П', 'В', 'Т', 'Б', 'К'];
    const opClasses = ['loading', 'discharge', 'transit', 'ballast', 'canal'];
    const gantt = [];
    
    const filteredVessels = applyFiltersToData(appState.vessels);
    
    filteredVessels.forEach(vessel => {
        const row = {vessel: vessel.name, days: []};
        for (let i = 0; i < days; i++) {
            const opIndex = Math.floor(Math.random() * operations.length);
            
            // Apply operation type filter
            if (appState.filters.opTypes.length > 0 && !appState.filters.opTypes.includes(opClasses[opIndex])) {
                row.days.push({ operation: '', class: '' });
            } else {
                row.days.push({
                    operation: operations[opIndex],
                    class: opClasses[opIndex]
                });
            }
        }
        gantt.push(row);
    });
    
    return gantt;
}

export function generateSchedule() {
    const moduleType = appState.currentModule;
    const scheduleContent = document.getElementById('scheduleContent');
    const voyageSelection = document.getElementById('voyageSelectionForGantt')?.value || 'all';

    // Handle custom voyage selection
    if (voyageSelection === 'custom') {
        showCustomVoyageSelectionModal();
        return;
    }

    scheduleContent.innerHTML = '<div class="info-box"><p>Генерация расписания...</p></div>';

    // Call Flask API for calculation
    fetch('/api/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            module: moduleType,
            voyageFilter: voyageSelection
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            const filteredVessels = applyFiltersToData(appState.vessels);
            const filteredCargo = applyFiltersToData(appState.cargo);

            const totalVessels = filteredVessels.length;
            const totalCargo = filteredCargo.length;
            const totalDistance = appState.routes.reduce((sum, r) => sum + (r.distance || 0), 0);
            const activeVessels = filteredVessels.filter(v => v.status === 'Active').length;
            const estimatedDuration = Math.ceil(totalDistance / (14 * 24));

            // Generate Gantt from API data
            fetch('/api/gantt-data')
            .then(response => response.json())
            .then(ganttResult => {
                const ganttData = generateGanttFromAPI(ganttResult.assets || {});

                let ganttHTML = '<div class="gantt-chart"><table class="gantt-table"><thead><tr><th>Судно</th>';
                for (let i = 1; i <= 30; i++) {
                    ganttHTML += `<th>${i}</th>`;
                }
                ganttHTML += '</tr></thead><tbody>';

                ganttData.forEach(row => {
                    ganttHTML += `<tr><th>${row.vessel}</th>`;
                    row.days.forEach(day => {
                        if (day.operation) {
                            ganttHTML += `<td class="gantt-cell op-${day.class}">${day.operation}</td>`;
                        } else {
                            ganttHTML += `<td class="gantt-cell"></td>`;
                        }
                    });
                    ganttHTML += '</tr>';
                });
                ganttHTML += '</tbody></table></div>';

                const moduleNames = {
                    deepsea: 'Deep Sea (Морские)',
                    balakovo: 'Balakovo (Балаково)',
                    olya: 'Olya (Оля)'
                };
                const moduleColors = {
                    deepsea: '#4a9eff',
                    balakovo: '#00b894',
                    olya: '#6c5ce7'
                };

                scheduleContent.innerHTML = `
                    <div class="info-box" style="border-left-color: ${moduleColors[moduleType] || '#4a9eff'}">
                        <h3>Расписание сгенерировано: ${moduleNames[moduleType] || moduleType}</h3>
                        <p>Расписание успешно сгенерировано на основе текущих данных судов и грузов модуля ${moduleNames[moduleType]}.</p>

                        <div style="margin-top: 1.5rem;">
                            <h4 style="color: var(--text-primary); margin-bottom: 1rem;">Сводка:</h4>
                            <ul>
                                <li>Всего судов: ${totalVessels}</li>
                                <li>Активных судов: ${activeVessels}</li>
                                <li>Грузовых отправлений: ${totalCargo}</li>
                                <li>Активных маршрутов: ${appState.routes.length}</li>
                                <li>Общая дистанция: ${totalDistance.toLocaleString()} морских миль</li>
                                <li>Примерная длительность: ${estimatedDuration} дней</li>
                                <li>Обработано этапов: ${result.legs_count}</li>
                                <li>Найдено предупреждений: ${result.alerts_count}</li>
                            </ul>
                        </div>

                        <div style="margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
                            <button class="btn-primary" onclick="ganttChart.exportGantt()">Скачать диаграмму Ганта</button>
                            <button class="btn-secondary" onclick="exports.exportFleetOverview()">Скачать обзор флота</button>
                        </div>
                    </div>

                    <div class="section" style="margin-top: 1.5rem;">
                        <h3>Диаграмма Ганта</h3>
                        ${ganttHTML}
                    </div>
                `;

                appState.schedule = {
                    type: moduleType,
                    generatedAt: new Date().toISOString(),
                    summary: {totalVessels, totalCargo, totalDistance, estimatedDuration}
                };

                saveToLocalStorage();
                showNotification('Расписание успешно сгенерировано!', 'success');
            })
            .catch(error => {
                console.error('Error getting Gantt data:', error);
                showNotification('Ошибка при получении данных диаграммы', 'error');
            });
        } else {
            throw new Error(result.error);
        }
    })
    .catch(error => {
        scheduleContent.innerHTML = `
            <div class="info-box" style="border-left-color: var(--accent-danger);">
                <h3>Ошибка генерации расписания</h3>
                <p>${error.message}</p>
            </div>
        `;
        showNotification('Ошибка генерации расписания: ' + error.message, 'error');
    });
}

function generateGanttFromAPI(assets) {
    const gantt = [];
    const operationMap = {
        'ballast': { label: 'Б', class: 'ballast' },
        'loading': { label: 'П', class: 'loading' },
        'transit': { label: 'Т', class: 'transit' },
        'discharge': { label: 'В', class: 'discharge' },
        'canal': { label: 'К', class: 'canal' },
        'bunker': { label: 'Ф', class: 'bunker' },
        'waiting': { label: 'О', class: 'waiting' }
    };

    Object.keys(assets).forEach(assetName => {
        const legs = assets[assetName];
        const row = { vessel: assetName, days: [] };

        // Initialize all days as empty
        for (let i = 0; i < 30; i++) {
            row.days.push({ operation: '', class: '' });
        }

        legs.forEach(leg => {
            const startDate = new Date(leg.start_time);
            const endDate = new Date(leg.end_time);
            const duration = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));

            // Simplified: place operation on first day
            const dayIndex = Math.floor((startDate - new Date()) / (1000 * 60 * 60 * 24));
            if (dayIndex >= 0 && dayIndex < 30) {
                const opInfo = operationMap[leg.leg_type] || { label: '?', class: 'waiting' };
                row.days[dayIndex] = { operation: opInfo.label, class: opInfo.class };
            }
        });

        gantt.push(row);
    });

    return gantt;
}

export function exportGantt() {
    // Get current year-month for export
    const now = new Date();
    const yearMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    
    fetch('/api/export/excel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            type: 'gantt',
            year_month: yearMonth
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            return response.json().then(err => { throw new Error(err.error || 'No voyages found for this month'); });
        }
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gantt_chart_${yearMonth}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        showNotification('Диаграмма Ганта успешно выгружена!', 'success');
    })
    .catch(error => {
        console.error('Export error:', error);
        showNotification('Ошибка при экспорте диаграммы Ганта: ' + error.message, 'error');
    });
}

// Helper function for filters (note: moved from original location)
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

    if (appState.filters.vesselId) {
        filtered = filtered.filter(item => item.vesselId === appState.filters.vesselId || item.vessel === appState.filters.vesselId);
    }

    return filtered;
}

// Import required from auto-schedule generator (stub here)
function generateAutoSchedule() {
    // This function exists in the main file - would need to be imported or extracted
    // For now, return empty to prevent errors
    return [];
}

// Export all functions as namespace
export const ganttChart = {
    generateGanttData,
    generateGanttFromVoyages,
    generateSchedule,
    exportGantt
};
