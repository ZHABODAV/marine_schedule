/**
 * Unified Dashboard Module
 * Integrates Import/Export, Trading Lanes, Financial Calculator, Network Visualization, and Storage Manager
 * @module modules/unified-dashboard
 */

import { appState, tradingLanesState, getCurrentData } from '../core/app-state.js';
import { showNotification, formatDate } from '../core/utils.js';
import { saveToLocalStorage, loadFromLocalStorage } from '../services/storage-service.js';
import * as exports from './exports.js';
import * as tradingLanes from './trading-lanes.js';
import * as financialAnalysis from './financial-analysis.js';
import * as networkViz from './network-viz.js';

/**
 * Render the unified dashboard
 */
export function renderUnifiedDashboard() {
    const container = document.getElementById('mainContent');
    if (!container) return;

    container.innerHTML = `
        <div class="unified-dashboard">
            <!-- Dashboard Header -->
            <div class="dashboard-header">
                <h2><i class="fas fa-th-large"></i> Unified Control Center</h2>
                <p class="subtitle">Integrated management of all planning features</p>
            </div>

            <!-- Quick Stats Overview -->
            <div class="stats-grid">
                <div class="stat-card stat-primary">
                    <i class="fas fa-ship"></i>
                    <div class="stat-content">
                        <h3 id="stat-vessels">0</h3>
                        <p>Vessels</p>
                    </div>
                </div>
                <div class="stat-card stat-success">
                    <i class="fas fa-boxes"></i>
                    <div class="stat-content">
                        <h3 id="stat-cargo">0</h3>
                        <p>Cargo Orders</p>
                    </div>
                </div>
                <div class="stat-card stat-info">
                    <i class="fas fa-route"></i>
                    <div class="stat-content">
                        <h3 id="stat-lanes">0</h3>
                        <p>Trading Lanes</p>
                    </div>
                </div>
                <div class="stat-card stat-warning">
                    <i class="fas fa-dollar-sign"></i>
                    <div class="stat-content">
                        <h3 id="stat-costs">$0</h3>
                        <p>Total Costs</p>
                    </div>
                </div>
            </div>

            <!-- Feature Cards Grid -->
            <div class="features-grid">
                <!-- Import/Export Card -->
                <div class="feature-card">
                    <div class="feature-header">
                        <h3><i class="fas fa-file-export"></i> Import/Export</h3>
                    </div>
                    <div class="feature-body">
                        <p class="feature-description">Export voyage data, fleet overview, and financial reports</p>
                        <div class="button-group">
                            <button class="btn-primary btn-small" onclick="window.unifiedDashboard.exportGantt()">
                                <i class="fas fa-chart-gantt"></i> Gantt Chart
                            </button>
                            <button class="btn-secondary btn-small" onclick="window.unifiedDashboard.exportFleet()">
                                <i class="fas fa-ship"></i> Fleet Overview
                            </button>
                            <button class="btn-secondary btn-small" onclick="window.unifiedDashboard.exportVoyages()">
                                <i class="fas fa-route"></i> Voyage Summary
                            </button>
                            <button class="btn-secondary btn-small" onclick="window.unifiedDashboard.exportFinancial()">
                                <i class="fas fa-dollar-sign"></i> Financial Report
                            </button>
                        </div>
                        <div class="feature-stats">
                            <span id="export-count">0 exports today</span>
                        </div>
                    </div>
                </div>

                <!-- Trading Lanes Card -->
                <div class="feature-card">
                    <div class="feature-header">
                        <h3><i class="fas fa-road"></i> Trading Lanes</h3>
                    </div>
                    <div class="feature-body">
                        <p class="feature-description">Manage and optimize trading routes</p>
                        <div class="button-group">
                            <button class="btn-primary btn-small" onclick="window.unifiedDashboard.createTradingLane()">
                                <i class="fas fa-plus"></i> Create Lane
                            </button>
                            <button class="btn-secondary btn-small" onclick="window.unifiedDashboard.viewTradingLanes()">
                                <i class="fas fa-eye"></i> View All
                            </button>
                            <button class="btn-secondary btn-small" onclick="window.unifiedDashboard.placeVolume()">
                                <i class="fas fa-boxes"></i> Place Volume
                            </button>
                        </div>
                        <div class="lanes-mini-list" id="lanes-mini-list">
                            Loading lanes...
                        </div>
                    </div>
                </div>

                <!-- Financial Calculator Card -->
                <div class="feature-card">
                    <div class="feature-header">
                        <h3><i class="fas fa-calculator"></i> Financial Calculator</h3>
                    </div>
                    <div class="feature-body">
                        <p class="feature-description">Analyze costs and optimize bunker strategy</p>
                        <div class="financial-summary">
                            <div class="financial-item">
                                <span>Total Costs:</span>
                                <strong id="fin-total-costs">$0</strong>
                            </div>
                            <div class="financial-item">
                                <span>Bunker Costs:</span>
                                <strong id="fin-bunker-costs">$0</strong>
                            </div>
                            <div class="financial-item">
                                <span>Hire Costs:</span>
                                <strong id="fin-hire-costs">$0</strong>
                            </div>
                        </div>
                        <div class="button-group">
                            <button class="btn-primary btn-small" onclick="window.unifiedDashboard.calculateFinancials()">
                                <i class="fas fa-calculator"></i> Calculate
                            </button>
                            <button class="btn-secondary btn-small" onclick="window.unifiedDashboard.optimizeBunker()">
                                <i class="fas fa-gas-pump"></i> Optimize Bunker
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Network Visualization Card -->
                <div class="feature-card">
                    <div class="feature-header">
                        <h3><i class="fas fa-project-diagram"></i> Network Visualization</h3>
                    </div>
                    <div class="feature-body">
                        <p class="feature-description">Visualize port and route networks</p>
                        <div class="network-stats">
                            <div class="network-stat-item">
                                <span>Ports:</span>
                                <strong id="net-ports">0</strong>
                            </div>
                            <div class="network-stat-item">
                                <span>Routes:</span>
                                <strong id="net-routes">0</strong>
                            </div>
                        </div>
                        <div class="button-group">
                            <button class="btn-primary btn-small" onclick="window.unifiedDashboard.showNetwork()">
                                <i class="fas fa-eye"></i> Show Network
                            </button>
                            <button class="btn-secondary btn-small" onclick="window.unifiedDashboard.exportNetwork()">
                                <i class="fas fa-download"></i> Export Snapshot
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Storage Manager Card -->
                <div class="feature-card">
                    <div class="feature-header">
                        <h3><i class="fas fa-database"></i> Storage Manager</h3>
                    </div>
                    <div class="feature-body">
                        <p class="feature-description">Manage local data and sessions</p>
                        <div class="storage-stats">
                            <div class="storage-item">
                                <span>Last Saved:</span>
                                <strong id="storage-last-saved">Never</strong>
                            </div>
                            <div class="storage-item">
                                <span>Storage Used:</span>
                                <strong id="storage-size">0 KB</strong>
                            </div>
                        </div>
                        <div class="button-group">
                            <button class="btn-primary btn-small" onclick="window.unifiedDashboard.saveSession()">
                                <i class="fas fa-save"></i> Save Session
                            </button>
                            <button class="btn-secondary btn-small" onclick="window.unifiedDashboard.loadSession()">
                                <i class="fas fa-folder-open"></i> Load Session
                            </button>
                            <button class="btn-danger btn-small" onclick="window.unifiedDashboard.clearStorage()">
                                <i class="fas fa-trash"></i> Clear Storage
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Recent Activity Card -->
                <div class="feature-card feature-card-wide">
                    <div class="feature-header">
                        <h3><i class="fas fa-history"></i> Recent Activity</h3>
                    </div>
                    <div class="feature-body">
                        <div class="activity-list" id="recent-activity">
                            <div class="activity-item">
                                <i class="fas fa-info-circle"></i>
                                <span>No recent activity</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions Bar -->
            <div class="quick-actions-bar">
                <h3>Quick Actions</h3>
                <div class="quick-actions-grid">
                    <button class="quick-action-btn" onclick="window.unifiedDashboard.refreshAll()">
                        <i class="fas fa-sync"></i>
                        <span>Refresh All</span>
                    </button>
                    <button class="quick-action-btn" onclick="window.unifiedDashboard.exportAll()">
                        <i class="fas fa-cloud-download-alt"></i>
                        <span>Export All</span>
                    </button>
                    <button class="quick-action-btn" onclick="window.unifiedDashboard.viewReports()">
                        <i class="fas fa-file-alt"></i>
                        <span>View Reports</span>
                    </button>
                    <button class="quick-action-btn" onclick="window.unifiedDashboard.switchModule()">
                        <i class="fas fa-exchange-alt"></i>
                        <span>Switch Module</span>
                    </button>
                </div>
            </div>
        </div>
    `;

    // Initialize the dashboard
    updateDashboardStats();
    updateLanesMiniList();
    updateFinancialSummary();
    updateNetworkStats();
    updateStorageInfo();
    updateRecentActivity();
}

/**
 * Update dashboard statistics
 */
function updateDashboardStats() {
    const data = getCurrentData();
    
    document.getElementById('stat-vessels').textContent = appState.vessels.length;
    document.getElementById('stat-cargo').textContent = appState.cargo.length;
    document.getElementById('stat-lanes').textContent = tradingLanesState.lanes.length;
    
    // Calculate total costs
    const financial = calculateQuickFinancials();
    document.getElementById('stat-costs').textContent = '$' + financial.totalCosts.toLocaleString();
}

/**
 * Update lanes mini list
 */
function updateLanesMiniList() {
    const container = document.getElementById('lanes-mini-list');
    if (!container) return;

    if (tradingLanesState.lanes.length === 0) {
        container.innerHTML = '<div class="no-data-mini">No lanes created</div>';
        return;
    }

    const activeLanes = tradingLanesState.lanes.filter(l => l.active).slice(0, 3);
    container.innerHTML = activeLanes.map(lane => `
        <div class="lane-mini-item">
            <span class="lane-mini-name">${lane.name}</span>
            <span class="lane-mini-volume">${lane.totalVolume.toLocaleString()} MT</span>
        </div>
    `).join('') + (tradingLanesState.lanes.length > 3 ? 
        `<div class="lane-mini-more">+${tradingLanesState.lanes.length - 3} more</div>` : '');
}

/**
 * Update financial summary
 */
function updateFinancialSummary() {
    const financial = calculateQuickFinancials();
    
    document.getElementById('fin-total-costs').textContent = '$' + financial.totalCosts.toLocaleString();
    document.getElementById('fin-bunker-costs').textContent = '$' + financial.bunkerCosts.toLocaleString();
    document.getElementById('fin-hire-costs').textContent = '$' + financial.hireCosts.toLocaleString();
}

/**
 * Update network stats
 */
function updateNetworkStats() {
    const data = getCurrentData();
    
    document.getElementById('net-ports').textContent = data.masters.ports.length;
    document.getElementById('net-routes').textContent = data.masters.routes.length;
}

/**
 * Update storage info
 */
function updateStorageInfo() {
    try {
        const saved = localStorage.getItem('vesselSchedulerDataEnhanced');
        if (saved) {
            const data = JSON.parse(saved);
            const lastSaved = data.sessionInfo?.lastSaved;
            
            if (lastSaved) {
                const savedDate = new Date(lastSaved);
                document.getElementById('storage-last-saved').textContent = 
                    savedDate.toLocaleString('en-US', { hour: '2-digit', minute: '2-digit' });
            }
            
            const sizeKB = Math.round(new Blob([saved]).size / 1024);
            document.getElementById('storage-size').textContent = sizeKB + ' KB';
        }
    } catch (e) {
        console.error('Error reading storage info:', e);
    }
}

/**
 * Update recent activity
 */
function updateRecentActivity() {
    const container = document.getElementById('recent-activity');
    if (!container) return;

    // Get recent activity from storage or generate mock data
    const activities = [
        { icon: 'fa-ship', text: 'Fleet data loaded', time: '2 min ago' },
        { icon: 'fa-boxes', text: 'Cargo commitments updated', time: '5 min ago' },
        { icon: 'fa-calculator', text: 'Financial analysis completed', time: '10 min ago' }
    ];

    container.innerHTML = activities.map(a => `
        <div class="activity-item">
            <i class="fas ${a.icon}"></i>
            <span>${a.text}</span>
            <span class="activity-time">${a.time}</span>
        </div>
    `).join('');
}

/**
 * Calculate quick financials for dashboard
 */
function calculateQuickFinancials() {
    let totalCosts = 0;
    let bunkerCosts = 0;
    let hireCosts = 0;

    appState.cargo.forEach((cargo, idx) => {
        const vessel = appState.vessels[idx % appState.vessels.length];
        if (!vessel) return;

        const seaDays = 10; // Simplified
        const bunkerCost = 35 * 450 * seaDays; // consumption * price * days
        const hireCost = 15000 * seaDays;
        const portCost = 20000;

        bunkerCosts += bunkerCost;
        hireCosts += hireCost;
        totalCosts += bunkerCost + hireCost + portCost;
    });

    return {
        totalCosts: Math.round(totalCosts),
        bunkerCosts: Math.round(bunkerCosts),
        hireCosts: Math.round(hireCosts)
    };
}

// ===== DASHBOARD ACTION HANDLERS =====

const dashboardActions = {
    // Import/Export actions
    exportGantt() {
        exports.exportGantt();
        logActivity('Exported Gantt chart');
    },

    exportFleet() {
        exports.exportFleetOverview();
        logActivity('Exported fleet overview');
    },

    exportVoyages() {
        exports.exportVoyageSummary();
        logActivity('Exported voyage summary');
    },

    exportFinancial() {
        exports.exportDeepSeaFinancial();
        logActivity('Exported financial report');
    },

    // Trading Lanes actions
    createTradingLane() {
        tradingLanes.showCreateTradingLaneModal();
    },

    viewTradingLanes() {
        // Switch to trading lanes tab
        if (window.switchTab) {
            window.switchTab('tradingLanes');
        }
    },

    placeVolume() {
        tradingLanes.placeVolumeInTradingLanes();
    },

    // Financial Calculator actions
    calculateFinancials() {
        financialAnalysis.calculateFinancialAnalysis();
        updateFinancialSummary();
        logActivity('Calculated financial analysis');
    },

    optimizeBunker() {
        financialAnalysis.optimizeBunkerStrategy();
        logActivity('Optimized bunker strategy');
    },

    // Network Visualization actions
    showNetwork() {
        if (window.switchTab) {
            window.switchTab('network');
        }
        setTimeout(() => {
            networkViz.renderNetwork();
        }, 500);
    },

    exportNetwork() {
        networkViz.exportNetworkSnapshot();
        logActivity('Exported network snapshot');
    },

    // Storage Manager actions
    saveSession() {
        saveToLocalStorage();
        updateStorageInfo();
        showNotification('Session saved successfully', 'success');
        logActivity('Saved session');
    },

    loadSession() {
        const loaded = loadFromLocalStorage();
        if (loaded) {
            updateDashboardStats();
            updateLanesMiniList();
            updateFinancialSummary();
            showNotification('Session loaded successfully', 'success');
            logActivity('Loaded session');
        } else {
            showNotification('No saved session found', 'warning');
        }
    },

    clearStorage() {
        if (confirm('Are you sure you want to clear all stored data? This action cannot be undone.')) {
            localStorage.removeItem('vesselSchedulerDataEnhanced');
            updateStorageInfo();
            showNotification('Storage cleared', 'success');
            logActivity('Cleared storage');
        }
    },

    // Quick actions
    refreshAll() {
        updateDashboardStats();
        updateLanesMiniList();
        updateFinancialSummary();
        updateNetworkStats();
        updateStorageInfo();
        updateRecentActivity();
        showNotification('Dashboard refreshed', 'success');
    },

    exportAll() {
        showNotification('Exporting all data...', 'info');
        exports.exportFleetOverview();
        setTimeout(() => exports.exportVoyageSummary(), 1000);
        setTimeout(() => exports.exportDeepSeaFinancial(), 2000);
        setTimeout(() => networkViz.exportNetworkSnapshot(), 3000);
        logActivity('Exported all data');
    },

    viewReports() {
        if (window.switchTab) {
            window.switchTab('reports');
        }
    },

    switchModule() {
        const moduleSelector = document.getElementById('moduleSelector');
        if (moduleSelector) {
            moduleSelector.focus();
        }
    }
};

/**
 * Log activity to recent activity list
 */
function logActivity(text) {
    const container = document.getElementById('recent-activity');
    if (!container) return;

    const activityItem = document.createElement('div');
    activityItem.className = 'activity-item';
    activityItem.innerHTML = `
        <i class="fas fa-check-circle" style="color: var(--accent-success);"></i>
        <span>${text}</span>
        <span class="activity-time">Just now</span>
    `;

    container.insertBefore(activityItem, container.firstChild);

    // Keep only last 5 items
    while (container.children.length > 5) {
        container.removeChild(container.lastChild);
    }
}

// Expose dashboard actions globally
if (typeof window !== 'undefined') {
    window.unifiedDashboard = dashboardActions;
}

export default {
    render: renderUnifiedDashboard,
    actions: dashboardActions,
    updateStats: updateDashboardStats
};
