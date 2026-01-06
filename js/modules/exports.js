// ===== EXPORTS MODULE =====
// Purpose: Export functionality for various data formats (Excel, PDF, CSV)
// Lines extracted from vessel_scheduler_enhanced.js: 2903-3615

import { appState, getCurrentData } from '../core/app-state.js';
import { toNumber, formatDate, showNotification } from '../core/utils.js';

// ===== EXPORT FUNCTIONS =====
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

export function exportFleetOverview() {
    try {
        showNotification('Генерация обзора флота...', 'info');
        
        const wb = XLSX.utils.book_new();
        const fleetData = [];
        fleetData.push(['ID судна', 'Название', 'Класс', 'DWT (MT)', 'Скорость (узлы)', 'Статус']);
        
        appState.vessels.forEach(vessel => {
            fleetData.push([vessel.id, vessel.name, vessel.class, vessel.dwt, vessel.speed, vessel.status]);
        });
        
        const ws = XLSX.utils.aoa_to_sheet(fleetData);
        XLSX.utils.book_append_sheet(wb, ws, 'Обзор флота');
        
        const fileName = `fleet_overview_${new Date().toISOString().slice(0,10)}.xlsx`;
        XLSX.writeFile(wb, fileName);
        
        showNotification('Обзор флота успешно выгружен!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Ошибка при экспорте обзора флота', 'error');
    }
}

export function exportVoyageSummary() {
    try {
        showNotification('Генерация сводки рейсов...', 'info');
        
        const wb = XLSX.utils.book_new();
        
        const voyageData = [];
        voyageData.push(['ID груза', 'Товар', 'Количество (MT)', 'Порт погрузки', 'Порт выгрузки', 'Начало лейкэна', 'Конец лейкэна', 'Статус']);
        
        appState.cargo.forEach(cargo => {
            voyageData.push([cargo.id, cargo.commodity, cargo.quantity, cargo.loadPort, cargo.dischPort, cargo.laycanStart, cargo.laycanEnd, cargo.status]);
        });
        
        const ws = XLSX.utils.aoa_to_sheet(voyageData);
        XLSX.utils.book_append_sheet(wb, ws, 'Сводка рейсов');
        
        const fileName = `voyage_summary_${new Date().toISOString().slice(0,10)}.xlsx`;
        XLSX.writeFile(wb, fileName);
        
        showNotification('Сводка рейсов успешно выгружена!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Ошибка при экспорте сводки рейсов', 'error');
    }
}

export function exportScenarios() {
    try {
        showNotification('Генерация сравнения сценариев...', 'info');
        
        const wb = XLSX.utils.book_new();
       
        const scenarios = generateScenarioComparison();
        
        const scenarioData = [];
        scenarioData.push(['Сценарий', 'Рейсов', 'Затраты ($)', 'Дней', 'Утилизация (%)']);
        
        scenarios.forEach(s => {
            scenarioData.push([s.name, s.voyages, s.costs, s.days, s.utilization]);
        });
        
        const ws = XLSX.utils.aoa_to_sheet(scenarioData);
        XLSX.utils.book_append_sheet(wb, ws, 'Сценарии');
        
        const fileName = `scenarios_comparison_${new Date().toISOString().slice(0,10)}.xlsx`;
        XLSX.writeFile(wb, fileName);
        
        showNotification('Сравнение сценариев успешно выгружено!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Ошибка при экспорте сценариев', 'error');
    }
}

export function exportDeepSeaFinancial() {
    try {
        showNotification('Генерация финансового анализа Deep Sea...', 'info');
        
        const wb = XLSX.utils.book_new();
        
        const financial = calculateDeepSeaFinancials();
        
        const financialData = [];
        financialData.push(['Рейс', 'Судно', 'Груз (MT)', 'Расстояние (nm)', 'Дней в море', 'Bunker ($)', 'Hire ($)', 'Port ($)', 'Allocations ($)', 'Total ($)']);
        
        financial.voyages.forEach(v => {
            const allocations = (v.operationalCost || 0) + (v.overheadCost || 0) + (v.otherCost || 0);
            financialData.push([
                v.id, v.vessel, v.cargo, v.distance, v.seaDays.toFixed(1),
                v.bunkerCost, v.hireCost, v.portCost, allocations, v.totalCost
            ]);
        });
        
        const ws = XLSX.utils.aoa_to_sheet(financialData);
        XLSX.utils.book_append_sheet(wb, ws, 'Финансы');
        
        const summaryData = [
            ['Показатель', 'Значение'],
            ['Всего рейсов', financial.totalVoyages],
            ['Общие затраты ($)', financial.totalCosts],
            ['Общее расстояние (nm)', financial.totalDistance],
            ['Всего дней', financial.totalDays.toFixed(1)]
        ];
        
        const summaryWs = XLSX.utils.aoa_to_sheet(summaryData);
        XLSX.utils.book_append_sheet(wb, summaryWs, 'Сводка');
        
        const fileName = `deepsea_financial_${new Date().toISOString().slice(0,10)}.xlsx`;
        XLSX.writeFile(wb, fileName);
        
        showNotification('Финансовый анализ Deep Sea успешно выгружен!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Ошибка при экспорте финансового анализа', 'error');
    }
}

export function exportOlyaCoordination() {
    try {
        showNotification('Генерация координации Olya...', 'info');
        
        const wb = XLSX.utils.book_new();
        
        const olya = calculateOlyaCoordination();
        
        const matchesData = [];
        matchesData.push(['Статус', 'Баржа', 'Судно', 'Груз', 'Кол-во (MT)', 'Разгрузка баржи', 'Загрузка судна', 'Буфер (ч)', 'Примечания']);
        
        olya.matches.forEach(m => {
            matchesData.push([
                m.status, m.barge, m.vessel, m.cargo, m.quantity,
                m.bargeDischarge, m.vesselLoading, m.bufferHours.toFixed(1), m.notes
            ]);
        });
        
        const matchesWs = XLSX.utils.aoa_to_sheet(matchesData);
        XLSX.utils.book_append_sheet(wb, matchesWs, 'Стыковки');
        
        const bargesData = [];
        bargesData.push(['Судно', 'Рейс', 'Груз (MT)', 'Начало', 'Окончание', 'Длит. (ч)']);
        
        olya.barges.forEach(b => {
            bargesData.push([b.name, b.voyage, b.cargo, b.start, b.end, b.duration.toFixed(1)]);
        });
        
        const bargesWs = XLSX.utils.aoa_to_sheet(bargesData);
        XLSX.utils.book_append_sheet(wb, bargesWs, 'Баржи');
        
        const vesselsData = [];
        vesselsData.push(['Судно', 'Рейс', 'Груз (MT)', 'Начало', 'Окончание', 'Длит. (ч)']);
        
        olya.vessels.forEach(v => {
            vesselsData.push([v.name, v.voyage, v.cargo, v.start, v.end, v.duration.toFixed(1)]);
        });
        
        const vesselsWs = XLSX.utils.aoa_to_sheet(vesselsData);
        XLSX.utils.book_append_sheet(wb, vesselsWs, 'Суда');
        
        const fileName = `olya_coordination_${new Date().toISOString().slice(0,10)}.xlsx`;
        XLSX.writeFile(wb, fileName);
        
        showNotification('Координация Olya успешно выгружена!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Ошибка при экспорте координации Olya', 'error');
    }
}

export function exportVoyageComparison() {
    showNotification('Экспорт сравнения рейсов...', 'info');
    // Implementation would export the comparison results table
}

export function exportPortStockTimeline() {
    const portName = document.getElementById('portStockSelect').value;
    if (!portName || !appState.portStocks[portName]) {
        showNotification('Пожалуйста, сначала рассчитайте сток порта', 'warning');
        return;
    }

    try {
        showNotification('Экспорт истории стока порта...', 'info');
        
        const wb = XLSX.utils.book_new();
        const stockData = [];
        stockData.push(['Дата', 'ЖД Вход (MT)', 'Море Выход (MT)', 'Сток (MT)']);
        
        appState.portStocks[portName].forEach(day => {
            stockData.push([day.date, day.railInflow, day.seaOutflow, day.stock]);
        });
        
        const ws = XLSX.utils.aoa_to_sheet(stockData);
        XLSX.utils.book_append_sheet(wb, ws, 'Сток порта');
        
        const fileName = `port_stock_${portName}_${new Date().toISOString().slice(0,10)}.xlsx`;
        XLSX.writeFile(wb, fileName);
        
        showNotification('История стока порта успешно выгружена!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Ошибка при экспорте стока порта', 'error');
    }
}

// Helper functions (stubs - would need to import from other modules)
function generateScenarioComparison() {
    const scenarios = [];
    
    const scenario1 = {
        name: 'Базовый сценарий',
        voyages: appState.cargo.length,
        costs: 0,
        days: 0,
        utilization: 0
    };
    
    const financial = calculateDeepSeaFinancials();
    scenario1.costs = financial.totalCosts;
    scenario1.days = Math.round(financial.totalDays);
    scenario1.utilization = Math.round((financial.totalVoyages / Math.max(appState.vessels.length, 1)) * 100);
    
    scenarios.push(scenario1);
    
    const scenario2 = {
        name: 'Высокий приоритет',
        voyages: Math.ceil(appState.cargo.length * 0.6),
        costs: Math.round(scenario1.costs * 0.6),
        days: Math.round(scenario1.days * 0.6),
        utilization: Math.round(scenario1.utilization * 0.6)
    };
    
    scenarios.push(scenario2);
    
    const scenario3 = {
        name: 'Оптимизированные маршруты',
        voyages: appState.cargo.length,
        costs: Math.round(scenario1.costs * 0.85),
        days: Math.round(scenario1.days * 0.9),
        utilization: Math.round(scenario1.utilization * 0.95)
    };
    
    scenarios.push(scenario3);
    
    return scenarios;
}

function calculateDeepSeaFinancials() {
    const voyages = [];
    let totalCosts = 0;
    let totalDistance = 0;
    let totalDays = 0;
    let totalRevenue = 0;
    
    const params = {
        speedLaden: 13.5,
        bunkerIFO: 450,
        consumptionLaden: 35,
        loadRate: 5000,
        dischRate: 5000,
        portWaitingHours: 12,
        weatherMargin: 1.05
    };
    
    appState.cargo.forEach((cargo, idx) => {
        const vessel = appState.vessels[idx % appState.vessels.length];
        const route = appState.routes.find(r => r.from === cargo.loadPort && r.to === cargo.dischPort) || appState.routes[0];
        
        if (!vessel || !route) return;
        
        const seaHours = (route.distance / params.speedLaden) * params.weatherMargin;
        const seaDays = seaHours / 24;
        
        const loadDays = cargo.quantity / params.loadRate;
        const dischDays = cargo.quantity / params.dischRate;
        const portDays = loadDays + dischDays + (params.portWaitingHours / 24) * 2;
        
        const totalVoyageDays = seaDays + portDays;
        
        const bunkerConsumed = params.consumptionLaden * seaDays;
        const bunkerCost = bunkerConsumed * params.bunkerIFO;
        
        const dailyHire = 15000;
        const hireCost = dailyHire * totalVoyageDays;
        
        const portCost = 10000 * 2;
        
        const totalCost = bunkerCost + hireCost + portCost;
        
        voyages.push({
            id: cargo.id,
            vessel: vessel.name,
            cargo: cargo.quantity,
            distance: route.distance,
            seaDays: seaDays,
            bunkerCost: Math.round(bunkerCost),
            hireCost: Math.round(hireCost),
            portCost: portCost,
            totalCost: Math.round(totalCost)
        });
        
        totalCosts += totalCost;
        totalDistance += route.distance;
        totalDays += totalVoyageDays;
    });
    
    return {
        voyages: voyages,
        totalVoyages: voyages.length,
        totalCosts: Math.round(totalCosts),
        totalDistance: totalDistance,
        totalDays: totalDays
    };
}

function calculateOlyaCoordination() {
    // Stub for Olya coordination calculation
    return {
        matches: [],
        barges: [],
        vessels: []
    };
}

// Export all functions
export const exports = {
    exportGantt,
    exportFleetOverview,
    exportVoyageSummary,
    exportScenarios,
    exportDeepSeaFinancial,
    exportOlyaCoordination,
    exportVoyageComparison,
    exportPortStockTimeline
};
