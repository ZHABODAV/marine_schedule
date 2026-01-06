// ===== FINANCIAL ANALYSIS MODULE =====
// Purpose: Financial calculations and cost analysis for voyages
// Lines extracted from vessel_scheduler_enhanced.js: 4893-5004

import { appState, getCurrentData } from '../core/app-state.js';
import { toNumber, showNotification } from '../core/utils.js';


// ===== FINANCIAL ANALYSIS =====
export function calculateFinancialAnalysis() {
    showNotification('Расчет финансового анализа...', 'info');
    
    const financial = calculateDeepSeaFinancials();
    
    // Calculate totals
    const totalBunkerCost = financial.voyages.reduce((sum, v) => sum + v.bunkerCost, 0);
    const totalHireCost = financial.voyages.reduce((sum, v) => sum + v.hireCost, 0);
    const totalOtherCost = financial.totalCosts - totalBunkerCost - totalHireCost;

    // Update summary cards
    document.getElementById('totalCosts').textContent = '$' + financial.totalCosts.toLocaleString();
    document.getElementById('totalHireCosts').textContent = '$' + totalHireCost.toLocaleString();
    document.getElementById('totalBunkerCosts').textContent = '$' + totalBunkerCost.toLocaleString();
    document.getElementById('totalOtherCosts').textContent = '$' + totalOtherCost.toLocaleString();
    
    // Calculate bunker details
    const potentialSavings = Math.round(totalBunkerCost * 0.15); // 15% optimization potential
    const avgConsumption = financial.voyages.length > 0 ?
        financial.voyages.reduce((sum, v) => sum + 35, 0) / financial.voyages.length : 0;
    
    document.getElementById('bunkerCosts').textContent = '$' + Math.round(totalBunkerCost).toLocaleString();
    document.getElementById('bunkerSavings').textContent = '$' + potentialSavings.toLocaleString();
    document.getElementById('avgConsumption').textContent = Math.round(avgConsumption);
    
    // Detailed financial table
    const tableContainer = document.getElementById('financialDetailsTable');
    const html = `
        <div class="section">
            <h3>Детальный анализ затрат по рейсам</h3>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Рейс</th>
                            <th>Судно</th>
                            <th>Груз (MT)</th>
                            <th>Bunker ($)</th>
                            <th>Hire ($)</th>
                            <th>Port ($)</th>
                            <th>Allocations ($)</th>
                            <th>Total ($)</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${financial.voyages.map(v => {
                            const allocations = (v.operationalCost || 0) + (v.overheadCost || 0) + (v.otherCost || 0);
                            return `
                            <tr>
                                <td>${v.id}</td>
                                <td>${v.vessel}</td>
                                <td>${v.cargo.toLocaleString()}</td>
                                <td style="color: var(--accent-warning);">$${v.bunkerCost.toLocaleString()}</td>
                                <td>$${v.hireCost.toLocaleString()}</td>
                                <td>$${v.portCost.toLocaleString()}</td>
                                <td>$${allocations.toLocaleString()}</td>
                                <td><strong>$${(v.bunkerCost + v.hireCost + v.portCost + allocations).toLocaleString()}</strong></td>
                            </tr>
                        `}).join('')}
                    </tbody>
                    <tfoot style="background: var(--bg-secondary); font-weight: 700;">
                        <tr>
                            <td colspan="3">ИТОГО</td>
                            <td style="color: var(--accent-warning);">$${Math.round(totalBunkerCost).toLocaleString()}</td>
                            <td>$${Math.round(totalHireCost).toLocaleString()}</td>
                            <td>-</td>
                            <td>-</td>
                            <td><strong>$${financial.totalCosts.toLocaleString()}</strong></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    `;
    
    tableContainer.innerHTML = html;
    
    showNotification('Финансовый анализ завершен', 'success');
}

export function optimizeBunkerStrategy() {
    showNotification('Оптимизация стратегии бункеровки...', 'info');
    
    // This would call backend optimization algorithm
    fetch('/api/bunker/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            module: appState.currentModule,
            vessels: appState.vessels,
            routes: appState.routes
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification(`Оптимизация завершена. Потенциал экономии: $${result.savings.toLocaleString()}`, 'success');
            calculateFinancialAnalysis(); // Refresh analysis
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Bunker optimization error:', error);
        // Client-side fallback
        const current = parseInt(document.getElementById('bunkerCosts').textContent.replace(/[$,]/g, '')) || 0;
        const savings = Math.round(current * 0.15);
        document.getElementById('bunkerSavings').textContent = '$' + savings.toLocaleString();
        showNotification(`Оптимизация (клиент): потенциал экономии ~$${savings.toLocaleString()}`, 'info');
    });
}

// ===== DEEP SEA CALCULATOR =====
function calculateDeepSeaFinancials() {
    const voyages = [];
    let totalCosts = 0;
    let totalDistance = 0;
    let totalDays = 0;
    let totalRevenue = 0;
    
    const params = {
        speedLaden: 13.5,
        speedBallast: 14.5,
        bunkerIFO: 450,
        bunkerMGO: 650,
        consumptionLaden: 35,
        consumptionBallast: 28,
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
        
        const freightRate = 25;
        const revenue = cargo.quantity * freightRate;
        
        const totalCost = bunkerCost + hireCost + portCost;
        const netRevenue = revenue - bunkerCost - portCost;
        const tce = netRevenue / totalVoyageDays;
        const profit = revenue - totalCost;
        
        const voyageData = {
            id: cargo.id,
            vessel: vessel.name,
            cargo: cargo.quantity,
            distance: route.distance,
            seaDays: seaDays,
            revenue: revenue,
            bunkerCost: Math.round(bunkerCost),
            hireCost: Math.round(hireCost),
            portCost: portCost,
            totalCost: Math.round(totalCost),
            tce: tce,
            profit: Math.round(profit)
        };
        
        voyages.push(voyageData);
        totalRevenue += revenue;
        totalCosts += totalCost;
        totalDistance += route.distance;
        totalDays += totalVoyageDays;
    });
    
    const avgTCE = voyages.length > 0 ? voyages.reduce((sum, v) => sum + v.tce, 0) / voyages.length : 0;
    
    return {
        voyages: voyages,
        totalVoyages: voyages.length,
        totalRevenue: Math.round(totalRevenue),
        totalCosts: Math.round(totalCosts),
        totalProfit: Math.round(totalRevenue - totalCosts),
        avgTCE: avgTCE,
        totalDistance: totalDistance,
        totalDays: totalDays
    };
}

// Export all functions
export const financialAnalysis = {
    calculateFinancialAnalysis,
    optimizeBunkerStrategy,
    calculateDeepSeaFinancials
};
