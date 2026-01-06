/**
 * Alerts Dashboard Module
 * Real-time alert notifications and management for vessel scheduling
 */

class AlertsDashboard {
    constructor(config = {}) {
        this.config = {
            apiEndpoint: config.apiEndpoint || '/api/alerts',
            containerId: config.containerId || 'alerts-dashboard',
            refreshInterval: config.refreshInterval || 30000, // 30 seconds
            maxAlerts: config.maxAlerts || 100,
            soundEnabled: config.soundEnabled !== false,
            ...config
        };
        
        this.alerts = [];
        this.alertHistory = [];
        this.filters = {
            severity: 'all',
            type: 'all',
            status: 'active'
        };
        this.refreshTimer = null;
        this.initialized = false;
    }

    /**
     * Initialize the alerts dashboard
     */
    async init() {
        if (this.initialized) return;
        
        const container = document.getElementById(this.config.containerId);
        if (!container) {
            console.error(`Container #${this.config.containerId} not found`);
            return;
        }
        
        this.render();
        await this.loadAlerts();
        this.startAutoRefresh();
        this.initialized = true;
    }

    /**
     * Render the dashboard HTML structure
     */
    render() {
        const container = document.getElementById(this.config.containerId);
        container.innerHTML = `
            <div class="alerts-dashboard-wrapper">
                <!-- Header -->
                <div class="alerts-header">
                    <h3>Alerts Dashboard</h3>
                    <div class="alerts-actions">
                        <button id="alerts-refresh-btn" class="btn-icon" title="Refresh">
                            <span class="icon"></span>
                        </button>
                        <button id="alerts-config-btn" class="btn-icon" title="Configuration">
                            <span class="icon"></span>
                        </button>
                    </div>
                </div>

                <!-- Filters -->
                <div class="alerts-filters">
                    <select id="alerts-severity-filter" class="filter-select">
                        <option value="all">All Severities</option>
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                    
                    <select id="alerts-type-filter" class="filter-select">
                        <option value="all">All Types</option>
                        <option value="berth_conflict">Berth Conflict</option>
                        <option value="weather_warning">Weather Warning</option>
                        <option value="delay">Delay</option>
                        <option value="cargo_issue">Cargo Issue</option>
                        <option value="bunker_alert">Bunker Alert</option>
                    </select>
                    
                    <select id="alerts-status-filter" class="filter-select">
                        <option value="active">Active Only</option>
                        <option value="acknowledged">Acknowledged</option>
                        <option value="resolved">Resolved</option>
                        <option value="all">All Statuses</option>
                    </select>
                </div>

                <!-- Summary Stats -->
                <div class="alerts-summary">
                    <div class="stat-card critical">
                        <div class="stat-label">Critical</div>
                        <div class="stat-value" id="critical-count">0</div>
                    </div>
                    <div class="stat-card high">
                        <div class="stat-label">High</div>
                        <div class="stat-value" id="high-count">0</div>
                    </div>
                    <div class="stat-card medium">
                        <div class="stat-label">Medium</div>
                        <div class="stat-value" id="medium-count">0</div>
                    </div>
                    <div class="stat-card low">
                        <div class="stat-label">Low</div>
                        <div class="stat-value" id="low-count">0</div>
                    </div>
                </div>

                <!-- Active Alerts -->
                <div class="alerts-list-container">
                    <h4>Active Alerts</h4>
                    <div id="alerts-list" class="alerts-list"></div>
                </div>

                <!-- Alert History -->
                <div class="alerts-history-container">
                    <h4>Alert History</h4>
                    <div id="alerts-history-table-wrapper">
                        <table id="alerts-history-table" class="data-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Severity</th>
                                    <th>Type</th>
                                    <th>Message</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="alerts-history-body"></tbody>
                        </table>
                    </div>
                </div>

                <!-- Configuration Panel (initially hidden) -->
                <div id="alerts-config-panel" class="config-panel" style="display: none;">
                    <h4>Alert Configuration</h4>
                    <div class="config-options">
                        <label>
                            <input type="checkbox" id="alerts-sound-toggle" ${this.config.soundEnabled ? 'checked' : ''}>
                            Sound Notifications
                        </label>
                        <label>
                            Auto-refresh interval (seconds):
                            <input type="number" id="alerts-refresh-interval" value="${this.config.refreshInterval / 1000}" min="5" max="300">
                        </label>
                        <label>
                            Max alerts to display:
                            <input type="number" id="alerts-max-display" value="${this.config.maxAlerts}" min="10" max="500">
                        </label>
                    </div>
                    <button id="alerts-config-save" class="btn-primary">Save Configuration</button>
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    /**
     * Attach event listeners to UI elements
     */
    attachEventListeners() {
        // Refresh button
        document.getElementById('alerts-refresh-btn')?.addEventListener('click', () => {
            this.loadAlerts();
        });

        // Configuration button
        document.getElementById('alerts-config-btn')?.addEventListener('click', () => {
            const panel = document.getElementById('alerts-config-panel');
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        });

        // Save configuration
        document.getElementById('alerts-config-save')?.addEventListener('click', () => {
            this.saveConfiguration();
        });

        // Filters
        document.getElementById('alerts-severity-filter')?.addEventListener('change', (e) => {
            this.filters.severity = e.target.value;
            this.applyFilters();
        });

        document.getElementById('alerts-type-filter')?.addEventListener('change', (e) => {
            this.filters.type = e.target.value;
            this.applyFilters();
        });

        document.getElementById('alerts-status-filter')?.addEventListener('change', (e) => {
            this.filters.status = e.target.value;
            this.applyFilters();
        });
    }

    /**
     * Load alerts from API
     */
    async loadAlerts() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            if (!response.ok) throw new Error('Failed to fetch alerts');
            
            const data = await response.json();
            this.processAlerts(data.alerts || []);
            this.updateUI();
        } catch (error) {
            console.error('Error loading alerts:', error);
            this.showError('Failed to load alerts');
        }
    }

    /**
     * Process incoming alerts data
     */
    processAlerts(newAlerts) {
        const existingIds = new Set(this.alerts.map(a => a.id));
        
        newAlerts.forEach(alert => {
            if (!existingIds.has(alert.id)) {
                // New alert - add to history and potentially play sound
                this.alertHistory.unshift(alert);
                if (this.config.soundEnabled && alert.severity === 'critical') {
                    this.playAlertSound();
                }
            }
        });

        this.alerts = newAlerts;
        
        // Limit history size
        if (this.alertHistory.length > this.config.maxAlerts) {
            this.alertHistory = this.alertHistory.slice(0, this.config.maxAlerts);
        }
    }

    /**
     * Update the UI with current alerts
     */
    updateUI() {
        this.updateSummaryStats();
        this.renderAlertsList();
        this.renderAlertsHistory();
    }

    /**
     * Update summary statistics
     */
    updateSummaryStats() {
        const counts = {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
        };

        this.alerts.forEach(alert => {
            if (alert.status === 'active') {
                counts[alert.severity] = (counts[alert.severity] || 0) + 1;
            }
        });

        document.getElementById('critical-count').textContent = counts.critical;
        document.getElementById('high-count').textContent = counts.high;
        document.getElementById('medium-count').textContent = counts.medium;
        document.getElementById('low-count').textContent = counts.low;
    }

    /**
     * Render active alerts list
     */
    renderAlertsList() {
        const container = document.getElementById('alerts-list');
        const activeAlerts = this.getFilteredAlerts().filter(a => a.status === 'active');

        if (activeAlerts.length === 0) {
            container.innerHTML = '<div class="no-alerts">No active alerts</div>';
            return;
        }

        container.innerHTML = activeAlerts.map(alert => `
            <div class="alert-card severity-${alert.severity}" data-alert-id="${alert.id}">
                <div class="alert-header">
                    <span class="alert-severity">${this.getSeverityIcon(alert.severity)} ${alert.severity.toUpperCase()}</span>
                    <span class="alert-time">${this.formatTime(alert.timestamp)}</span>
                </div>
                <div class="alert-type">${this.formatAlertType(alert.type)}</div>
                <div class="alert-message">${alert.message}</div>
                ${alert.vessel ? `<div class="alert-vessel">Vessel: ${alert.vessel}</div>` : ''}
                <div class="alert-actions">
                    <button class="btn-sm acknowledge-btn" data-alert-id="${alert.id}">Acknowledge</button>
                    <button class="btn-sm resolve-btn" data-alert-id="${alert.id}">Resolve</button>
                    <button class="btn-sm details-btn" data-alert-id="${alert.id}">Details</button>
                </div>
            </div>
        `).join('');

        // Attach action handlers
        container.querySelectorAll('.acknowledge-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.acknowledgeAlert(e.target.dataset.alertId));
        });
        container.querySelectorAll('.resolve-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.resolveAlert(e.target.dataset.alertId));
        });
        container.querySelectorAll('.details-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.showAlertDetails(e.target.dataset.alertId));
        });
    }

    /**
     * Render alerts history table
     */
    renderAlertsHistory() {
        const tbody = document.getElementById('alerts-history-body');
        const filteredHistory = this.getFilteredHistory();

        if (filteredHistory.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-data">No alerts in history</td></tr>';
            return;
        }

        tbody.innerHTML = filteredHistory.map(alert => `
            <tr class="severity-${alert.severity}">
                <td>${this.formatTime(alert.timestamp)}</td>
                <td><span class="severity-badge ${alert.severity}">${alert.severity}</span></td>
                <td>${this.formatAlertType(alert.type)}</td>
                <td>${alert.message}</td>
                <td><span class="status-badge ${alert.status}">${alert.status}</span></td>
                <td>
                    <button class="btn-sm view-btn" data-alert-id="${alert.id}">View</button>
                </td>
            </tr>
        `).join('');

        tbody.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.showAlertDetails(e.target.dataset.alertId));
        });
    }

    /**
     * Apply current filters to alerts
     */
    applyFilters() {
        this.updateUI();
    }

    /**
     * Get filtered alerts based on current filters
     */
    getFilteredAlerts() {
        return this.alerts.filter(alert => {
            if (this.filters.severity !== 'all' && alert.severity !== this.filters.severity) return false;
            if (this.filters.type !== 'all' && alert.type !== this.filters.type) return false;
            if (this.filters.status !== 'all' && alert.status !== this.filters.status) return false;
            return true;
        });
    }

    /**
     * Get filtered alert history
     */
    getFilteredHistory() {
        return this.alertHistory.filter(alert => {
            if (this.filters.severity !== 'all' && alert.severity !== this.filters.severity) return false;
            if (this.filters.type !== 'all' && alert.type !== this.filters.type) return false;
            if (this.filters.status !== 'all' && alert.status !== this.filters.status) return false;
            return true;
        });
    }

    /**
     * Acknowledge an alert
     */
    async acknowledgeAlert(alertId) {
        try {
            const response = await fetch(`${this.config.apiEndpoint}/${alertId}/acknowledge`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error('Failed to acknowledge alert');
            
            const alert = this.alerts.find(a => a.id === alertId);
            if (alert) alert.status = 'acknowledged';
            
            this.updateUI();
        } catch (error) {
            console.error('Error acknowledging alert:', error);
            this.showError('Failed to acknowledge alert');
        }
    }

    /**
     * Resolve an alert
     */
    async resolveAlert(alertId) {
        try {
            const response = await fetch(`${this.config.apiEndpoint}/${alertId}/resolve`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error('Failed to resolve alert');
            
            const alert = this.alerts.find(a => a.id === alertId);
            if (alert) alert.status = 'resolved';
            
            this.updateUI();
        } catch (error) {
            console.error('Error resolving alert:', error);
            this.showError('Failed to resolve alert');
        }
    }

    /**
     * Show alert details in a modal
     */
    showAlertDetails(alertId) {
        const alert = [...this.alerts, ...this.alertHistory].find(a => a.id === alertId);
        if (!alert) return;

        // Create modal (assuming a modal system exists)
        const modalContent = `
            <h3>Alert Details</h3>
            <div class="alert-details">
                <p><strong>ID:</strong> ${alert.id}</p>
                <p><strong>Time:</strong> ${this.formatTime(alert.timestamp)}</p>
                <p><strong>Severity:</strong> ${alert.severity}</p>
                <p><strong>Type:</strong> ${this.formatAlertType(alert.type)}</p>
                <p><strong>Status:</strong> ${alert.status}</p>
                <p><strong>Message:</strong> ${alert.message}</p>
                ${alert.vessel ? `<p><strong>Vessel:</strong> ${alert.vessel}</p>` : ''}
                ${alert.details ? `<p><strong>Details:</strong> ${alert.details}</p>` : ''}
            </div>
        `;
        
        // Trigger custom event for modal display
        const event = new CustomEvent('showModal', { detail: { content: modalContent } });
        document.dispatchEvent(event);
    }

    /**
     * Save configuration settings
     */
    saveConfiguration() {
        const soundEnabled = document.getElementById('alerts-sound-toggle').checked;
        const refreshInterval = parseInt(document.getElementById('alerts-refresh-interval').value) * 1000;
        const maxAlerts = parseInt(document.getElementById('alerts-max-display').value);

        this.config.soundEnabled = soundEnabled;
        this.config.refreshInterval = refreshInterval;
        this.config.maxAlerts = maxAlerts;

        // Restart auto-refresh with new interval
        this.startAutoRefresh();

        // Hide config panel
        document.getElementById('alerts-config-panel').style.display = 'none';

        this.showSuccess('Configuration saved');
    }

    /**
     * Start auto-refresh timer
     */
    startAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
        
        this.refreshTimer = setInterval(() => {
            this.loadAlerts();
        }, this.config.refreshInterval);
    }

    /**
     * Stop auto-refresh timer
     */
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    /**
     * Play alert sound
     */
    playAlertSound() {
        // Simple beep using Web Audio API
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    }

    /**
     * Helper: Get severity icon
     */
    getSeverityIcon(severity) {
        const icons = {
            critical: '',
            high: '',
            medium: '',
            low: ''
        };
        return icons[severity] || '';
    }

    /**
     * Helper: Format alert type
     */
    formatAlertType(type) {
        return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    /**
     * Helper: Format timestamp
     */
    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }

    /**
     * Show error message
     */
    showError(message) {
        const event = new CustomEvent('showNotification', {
            detail: { type: 'error', message }
        });
        document.dispatchEvent(event);
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        const event = new CustomEvent('showNotification', {
            detail: { type: 'success', message }
        });
        document.dispatchEvent(event);
    }

    /**
     * Destroy the dashboard and clean up
     */
    destroy() {
        this.stopAutoRefresh();
        const container = document.getElementById(this.config.containerId);
        if (container) container.innerHTML = '';
        this.initialized = false;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AlertsDashboard;
}
