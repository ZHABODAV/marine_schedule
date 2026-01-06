/**
 * Combined UI Modules for Vessel Schedule
 * All modules in one file for easy deployment
 * Separate individual files can be found in their respective directories
 */

// ======================
// BUNKER OPTIMIZATION
// ======================

class BunkerOptimization {
    constructor(config = {}) {
        this.config = {
            apiEndpoint: config.apiEndpoint || '/api/bunker',
            containerId: config.containerId || 'bunker-optimization',
            ...config
        };
        this.routes = [];
        this.ports = [];
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        const container = document.getElementById(this.config.containerId);
        if (!container) return;
        
        this.render();
        await this.loadData();
        this.initialized = true;
    }

    render() {
        const container = document.getElementById(this.config.containerId);
        container.innerHTML = `
            <div class="bunker-optimization-wrapper">
                <h3>Bunker Optimization</h3>
                <div class="bunker-calculator">
                    <h4>Cost Calculator</h4>
                    <form id="bunker-calc-form">
                        <label>Voyage Distance (nm): <input type="number" id="bunker-distance" required></label>
                        <label>Vessel Speed (knots): <input type="number" id="bunker-speed" required></label>
                        <label>Consumption Rate (MT/day): <input type="number" id="bunker-consumption" required></label>
                        <label>Fuel Type:
                            <select id="bunker-fuel-type">
                                <option value="vlsfo">VLSFO</option>
                                <option value="hfo">HFO</option>
                                <option value="mgo">MGO</option>
                            </select>
                        </label>
                        <button type="submit" class="btn-primary">Calculate</button>
                    </form>
                    <div id="bunker-result"></div>
                </div>
                <div class="bunker-ports">
                    <h4>Recommended Bunker Ports</h4>
                    <div id="bunker-ports-list"></div>
                </div>
            </div>
        `;
        this.attachEventListeners();
    }

    attachEventListeners() {
        document.getElementById('bunker-calc-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateBunkerCost();
        });
    }

    async loadData() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            const data = await response.json();
            this.ports = data.ports || [];
            this.renderBunkerPorts();
        } catch (error) {
            console.error('Error loading bunker data:', error);
        }
    }

    calculateBunkerCost() {
        const distance = parseFloat(document.getElementById('bunker-distance').value);
        const speed = parseFloat(document.getElementById('bunker-speed').value);
        const consumption = parseFloat(document.getElementById('bunker-consumption').value);
        const fuelType = document.getElementById('bunker-fuel-type').value;

        const prices = { vlsfo: 450, hfo: 380, mgo: 550 };
        const days = distance / (speed * 24);
        const totalConsumption = days * consumption;
        const totalCost = totalConsumption * prices[fuelType];

        document.getElementById('bunker-result').innerHTML = `
            <div class="result-card">
                <p><strong>Voyage Duration:</strong> ${days.toFixed(2)} days</p>
                <p><strong>Total Consumption:</strong> ${totalConsumption.toFixed(2)} MT</p>
                <p><strong>Estimated Cost:</strong> $${totalCost.toFixed(2)}</p>
            </div>
        `;
    }

    renderBunkerPorts() {
        const container = document.getElementById('bunker-ports-list');
        container.innerHTML = this.ports.map(port => `
            <div class="port-card">
                <h5>${port.name}</h5>
                <p>VLSFO: $${port.prices.vlsfo}/MT</p>
                <p>HFO: $${port.prices.hfo}/MT</p>
                <p>MGO: $${port.prices.mgo}/MT</p>
            </div>
        `).join('');
    }

    destroy() {
        const container = document.getElementById(this.config.containerId);
        if (container) container.innerHTML = '';
        this.initialized = false;
    }
}

// ======================
// WEATHER INTEGRATION
// ======================

class WeatherIntegration {
    constructor(config = {}) {
        this.config = {
            apiEndpoint: config.apiEndpoint || '/api/weather',
            containerId: config.containerId || 'weather-integration',
            ganttElementId: config.ganttElementId || null,
            ...config
        };
        this.warnings = [];
        this.forecasts = [];
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        const container = document.getElementById(this.config.containerId);
        if (!container) return;
        
        this.render();
        await this.loadWeatherData();
        if (this.config.ganttElementId) this.overlayOnGantt();
        this.initialized = true;
    }

    render() {
        const container = document.getElementById(this.config.containerId);
        container.innerHTML = `
            <div class="weather-integration-wrapper">
                <h3>Weather Integration</h3>
                <div class="weather-warnings">
                    <h4>Active Warnings</h4>
                    <div id="weather-warnings-list"></div>
                </div>
                <div class="weather-forecast">
                    <h4>5-Day Forecast</h4>
                    <div id="weather-forecast-grid"></div>
                </div>
                <div class="weather-routes">
                    <h4>Route Risk Assessment</h4>
                    <div id="weather-route-risks"></div>
                </div>
            </div>
        `;
    }

    async loadWeatherData() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            const data = await response.json();
            this.warnings = data.warnings || [];
            this.forecasts = data.forecasts || [];
            this.renderWarnings();
            this.renderForecast();
        } catch (error) {
            console.error('Error loading weather data:', error);
        }
    }

    renderWarnings() {
        const container = document.getElementById('weather-warnings-list');
        if (this.warnings.length === 0) {
            container.innerHTML = '<p class="no-data">No active weather warnings</p>';
            return;
        }

        container.innerHTML = this.warnings.map(warning => `
            <div class="warning-card severity-${warning.severity}">
                <div class="warning-icon">${this.getWeatherIcon(warning.type)}</div>
                <div class="warning-content">
                    <h5>${warning.title}</h5>
                    <p>${warning.description}</p>
                    <p class="warning-location">${warning.location}</p>
                    <p class="warning-time">${new Date(warning.validUntil).toLocaleString()}</p>
                </div>
            </div>
        `).join('');
    }

    renderForecast() {
        const container = document.getElementById('weather-forecast-grid');
        container.innerHTML = this.forecasts.map(forecast => `
            <div class="forecast-day">
                <div class="forecast-date">${new Date(forecast.date).toLocaleDateString('en-US', {weekday: 'short', month: 'short', day: 'numeric'})}</div>
                <div class="forecast-icon">${this.getWeatherIcon(forecast.condition)}</div>
                <div class="forecast-temp">${forecast.temp}°C</div>
                <div class="forecast-wind">Wind: ${forecast.windSpeed} kt</div>
                <div class="forecast-waves">Waves: ${forecast.waveHeight} m</div>
            </div>
        `).join('');
    }

    overlayOnGantt() {
        const ganttElement = document.getElementById(this.config.ganttElementId);
        if (!ganttElement) return;

        this.warnings.forEach(warning => {
            const overlay = document.createElement('div');
            overlay.className = 'weather-overlay';
            overlay.style.cssText = `
                position: absolute;
                background: rgba(239, 68, 68, 0.2);
                border: 2px dashed #ef4444;
                pointer-events: none;
                z-index: 100;
            `;
            overlay.title = warning.title;
            ganttElement.appendChild(overlay);
        });
    }

    getWeatherIcon(type) {
        const icons = {
            storm: '',
            wind: '',
            fog: '',
            rain: '',
            clear: '',
            cloudy: ''
        };
        return icons[type] || '';
    }

    destroy() {
        const container = document.getElementById(this.config.containerId);
        if (container) container.innerHTML = '';
        this.initialized = false;
    }
}

// ======================
// VESSEL TRACKING
// ======================

class VesselTracking {
    constructor(config = {}) {
        this.config = {
            apiEndpoint: config.apiEndpoint || '/api/vessels/tracking',
            containerId: config.containerId || 'vessel-tracking',
            mapProvider: config.mapProvider || 'leaflet',
            updateInterval: config.updateInterval || 60000,
            ...config
        };
        this.vessels = [];
        this.map = null;
        this.markers = {};
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        const container = document.getElementById(this.config.containerId);
        if (!container) return;
        
        this.render();
        this.initMap();
        await this.loadVesselData();
        this.startTracking();
        this.initialized = true;
    }

    render() {
        const container = document.getElementById(this.config.containerId);
        container.innerHTML = `
            <div class="vessel-tracking-wrapper">
                <h3>Vessel Tracking</h3>
                <div class="tracking-controls">
                    <button id="refresh-tracking-btn" class="btn-secondary">Refresh</button>
                    <input type="text" id="vessel-search" placeholder="Search vessel..." />
                </div>
                <div id="tracking-map" style="height: 500px; width: 100%;"></div>
                <div class="vessel-list">
                    <h4>Vessel List</h4>
                    <div id="vessel-status-table"></div>
                </div>
            </div>
        `;
        this.attachEventListeners();
    }

    attachEventListeners() {
        document.getElementById('refresh-tracking-btn')?.addEventListener('click', () => {
            this.loadVesselData();
        });
        
        document.getElementById('vessel-search')?.addEventListener('input', (e) => {
            this.filterVessels(e.target.value);
        });
    }

    initMap() {
        const mapDiv = document.getElementById('tracking-map');
        if (!mapDiv) return;

        if (typeof L !== 'undefined') {
            this.map = L.map('tracking-map').setView([0, 0], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);
        } else {
            mapDiv.innerHTML = '<div class="map-placeholder">Map library not loaded. Include Leaflet.js to enable mapping.</div>';
        }
    }

    async loadVesselData() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            const data = await response.json();
            this.vessels = data.vessels || [];
            this.updateMap();
            this.renderVesselTable();
        } catch (error) {
            console.error('Error loading vessel data:', error);
        }
    }

    updateMap() {
        if (!this.map) return;

        Object.values(this.markers).forEach(marker => marker.remove());
        this.markers = {};

        this.vessels.forEach(vessel => {
            if (vessel.position && vessel.position.lat && vessel.position.lon) {
                if (typeof L !== 'undefined') {
                    const marker = L.marker([vessel.position.lat, vessel.position.lon])
                        .addTo(this.map)
                        .bindPopup(`
                            <b>${vessel.name}</b><br>
                            Status: ${vessel.status}<br>
                            Speed: ${vessel.speed} knots<br>
                            Course: ${vessel.course}°<br>
                            ETA: ${vessel.eta ? new Date(vessel.eta).toLocaleString() : 'N/A'}
                        `);
                    this.markers[vessel.id] = marker;
                }
            }
        });

        if (this.vessels.length > 0 && typeof L !== 'undefined') {
            const bounds = L.latLngBounds(
                this.vessels.filter(v => v.position).map(v => [v.position.lat, v.position.lon])
            );
            this.map.fitBounds(bounds, { padding: [50, 50] });
        }
    }

    renderVesselTable() {
        const container = document.getElementById('vessel-status-table');
        container.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Vessel</th>
                        <th>Status</th>
                        <th>Position</th>
                        <th>Speed</th>
                        <th>Destination</th>
                        <th>ETA</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.vessels.map(vessel => `
                        <tr>
                            <td><strong>${vessel.name}</strong></td>
                            <td><span class="status-badge ${vessel.status}">${vessel.status}</span></td>
                            <td>${vessel.position ? `${vessel.position.lat.toFixed(2)}°, ${vessel.position.lon.toFixed(2)}°` : 'N/A'}</td>
                            <td>${vessel.speed || 0} knots</td>
                            <td>${vessel.destination || 'N/A'}</td>
                            <td>${vessel.eta ? new Date(vessel.eta).toLocaleString() : 'N/A'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    filterVessels(searchTerm) {
        const rows = document.querySelectorAll('#vessel-status-table tbody tr');
        rows.forEach(row => {
            const vesselName = row.querySelector('td strong').textContent.toLowerCase();
            row.style.display = vesselName.includes(searchTerm.toLowerCase()) ? '' : 'none';
        });
    }

    startTracking() {
        setInterval(() => {
            this.loadVesselData();
        }, this.config.updateInterval);
    }

    destroy() {
        const container = document.getElementById(this.config.containerId);
        if (container) container.innerHTML = '';
        if (this.map) this.map.remove();
        this.initialized = false;
    }
}

// ======================
// PDF EXPORT
// ======================

class PDFExport {
    constructor(config = {}) {
        this.config = {
            apiEndpoint: config.apiEndpoint || '/api/export/pdf',
            reportTypes: config.reportTypes || ['schedule', 'berth', 'fleet'],
            ...config
        };
    }

    async generateReport(reportType, options = {}) {
        try {
            const response = await fetch(this.config.apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    reportType,
                    options
                })
            });

            if (!response.ok) throw new Error('Failed to generate PDF');

            const blob = await response.blob();
            this.downloadPDF(blob, `${reportType}_report_${new Date().toISOString().split('T')[0]}.pdf`);
        } catch (error) {
            console.error('Error generating PDF:', error);
            alert('Failed to generate PDF report');
        }
    }

    downloadPDF(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    async exportCurrentView(elementId, filename = 'export.pdf') {
        const element = document.getElementById(elementId);
        if (!element) return;

        if (typeof html2pdf !== 'undefined') {
            const opt = {
                margin: 10,
                filename: filename,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
            };

            html2pdf().set(opt).from(element).save();
        } else {
            console.error('html2pdf library not loaded');
            alert('PDF export library not available');
        }
    }
}

// ======================
// SCENARIO MANAGEMENT
// ======================

class ScenarioManagement {
    constructor(config = {}) {
        this.config = {
            apiEndpoint: config.apiEndpoint || '/api/scenarios',
            containerId: config.containerId || 'scenario-management',
            ...config
        };
        this.scenarios = [];
        this.currentScenario = null;
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        const container = document.getElementById(this.config.containerId);
        if (!container) return;
        
        this.render();
        await this.loadScenarios();
        this.initialized = true;
    }

    render() {
        const container = document.getElementById(this.config.containerId);
        container.innerHTML = `
            <div class="scenario-management-wrapper">
                <h3>Scenario Management</h3>
                <div class="scenario-header">
                    <button id="create-scenario-btn" class="btn-primary">Create New Scenario</button>
                    <button id="compare-scenarios-btn" class="btn-secondary">Compare Scenarios</button>
                </div>
                <div class="scenarios-list">
                    <h4>Available Scenarios</h4>
                    <div id="scenarios-grid"></div>
                </div>
                <div id="scenario-editor" style="display: none;">
                    <h4>Scenario Editor</h4>
                    <form id="scenario-form">
                        <label>Name: <input type="text" id="scenario-name" required></label>
                        <label>Description: <textarea id="scenario-description"></textarea></label>
                        <label>Based On:
                            <select id="scenario-base"></select>
                        </label>
                        <button type="submit" class="btn-primary">Save Scenario</button>
                        <button type="button" id="cancel-scenario-btn" class="btn-secondary">Cancel</button>
                    </form>
                </div>
            </div>
        `;
        this.attachEventListeners();
    }

    attachEventListeners() {
        document.getElementById('create-scenario-btn')?.addEventListener('click', () => {
            this.showScenarioEditor();
        });

        document.getElementById('cancel-scenario-btn')?.addEventListener('click', () => {
            this.hideScenarioEditor();
        });

        document.getElementById('scenario-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveScenario();
        });

        document.getElementById('compare-scenarios-btn')?.addEventListener('click', () => {
            this.compareScenarios();
        });
    }

    async loadScenarios() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            const data = await response.json();
            this.scenarios = data.scenarios || [];
            this.renderScenarios();
        } catch (error) {
            console.error('Error loading scenarios:', error);
        }
    }

    renderScenarios() {
        const container = document.getElementById('scenarios-grid');
        container.innerHTML = this.scenarios.map(scenario => `
            <div class="scenario-card ${scenario.id === this.currentScenario?.id ? 'active' : ''}">
                <h5>${scenario.name}</h5>
                <p>${scenario.description}</p>
                <p class="scenario-meta">Created: ${new Date(scenario.createdAt).toLocaleDateString()}</p>
                <div class="scenario-actions">
                    <button class="btn-sm load-scenario-btn" data-scenario-id="${scenario.id}">Load</button>
                    <button class="btn-sm edit-scenario-btn" data-scenario-id="${scenario.id}">Edit</button>
                    <button class="btn-sm delete-scenario-btn" data-scenario-id="${scenario.id}">Delete</button>
                </div>
            </div>
        `).join('');

        container.querySelectorAll('.load-scenario-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.loadScenario(e.target.dataset.scenarioId));
        });
        container.querySelectorAll('.edit-scenario-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.editScenario(e.target.dataset.scenarioId));
        });
        container.querySelectorAll('.delete-scenario-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.deleteScenario(e.target.dataset.scenarioId));
        });
    }

    showScenarioEditor() {
        document.getElementById('scenario-editor').style.display = 'block';
        const baseSelect = document.getElementById('scenario-base');
        baseSelect.innerHTML = `
            <option value="">None (Start Fresh)</option>
            ${this.scenarios.map(s => `<option value="${s.id}">${s.name}</option>`).join('')}
        `;
    }

    hideScenarioEditor() {
        document.getElementById('scenario-editor').style.display = 'none';
        document.getElementById('scenario-form').reset();
    }

    async saveScenario() {
        const formData = {
            name: document.getElementById('scenario-name').value,
            description: document.getElementById('scenario-description').value,
            baseScenarioId: document.getElementById('scenario-base').value || null
        };

        try {
            const response = await fetch(this.config.apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (!response.ok) throw new Error('Failed to save scenario');

            this.hideScenarioEditor();
            await this.loadScenarios();
            alert('Scenario saved successfully');
        } catch (error) {
            console.error('Error saving scenario:', error);
            alert('Failed to save scenario');
        }
    }

    async loadScenario(scenarioId) {
        try {
            const response = await fetch(`${this.config.apiEndpoint}/${scenarioId}/load`, {
                method: 'POST'
            });

            if (!response.ok) throw new Error('Failed to load scenario');

            const data = await response.json();
            this.currentScenario = this.scenarios.find(s => s.id === scenarioId);
            this.renderScenarios();
            
            const event = new CustomEvent('scenarioLoaded', { detail: data });
            document.dispatchEvent(event);
        } catch (error) {
            console.error('Error loading scenario:', error);
            alert('Failed to load scenario');
        }
    }

    async editScenario(scenarioId) {
        const scenario = this.scenarios.find(s => s.id === scenarioId);
        if (!scenario) return;

        this.showScenarioEditor();
        document.getElementById('scenario-name').value = scenario.name;
        document.getElementById('scenario-description').value = scenario.description;
    }

    async deleteScenario(scenarioId) {
        if (!confirm('Are you sure you want to delete this scenario?')) return;

        try {
            const response = await fetch(`${this.config.apiEndpoint}/${scenarioId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Failed to delete scenario');

            await this.loadScenarios();
        } catch (error) {
            console.error('Error deleting scenario:', error);
            alert('Failed to delete scenario');
        }
    }

    compareScenarios() {
        alert('Scenario comparison feature - implementation depends on your specific comparison metrics');
    }

    destroy() {
        const container = document.getElementById(this.config.containerId);
        if (container) container.innerHTML = '';
        this.initialized = false;
    }
}

// ======================
// VOYAGE TEMPLATES
// ======================

class VoyageTemplates {
    constructor(config = {}) {
        this.config = {
            apiEndpoint: config.apiEndpoint || '/api/voyage-templates',
            containerId: config.containerId || 'voyage-templates',
            ...config
        };
        this.templates = [];
        this.categories = [];
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        const container = document.getElementById(this.config.containerId);
        if (!container) return;
        
        this.render();
        await this.loadTemplates();
        this.initialized = true;
    }

    render() {
        const container = document.getElementById(this.config.containerId);
        container.innerHTML = `
            <div class="voyage-templates-wrapper">
                <h3>Voyage Templates</h3>
                <div class="templates-header">
                    <button id="create-template-btn" class="btn-primary">Create Template</button>
                    <select id="template-category-filter">
                        <option value="all">All Categories</option>
                    </select>
                </div>
                <div class="templates-grid" id="templates-grid"></div>
            </div>
        `;
        this.attachEventListeners();
    }

    attachEventListeners() {
        document.getElementById('create-template-btn')?.addEventListener('click', () => {
            this.createTemplate();
        });

        document.getElementById('template-category-filter')?.addEventListener('change', (e) => {
            this.filterByCategory(e.target.value);
        });
    }

    async loadTemplates() {
        try {
            const response = await fetch(this.config.apiEndpoint);
            const data = await response.json();
            this.templates = data.templates || [];
            this.categories = data.categories || [];
            this.populateCategoryFilter();
            this.renderTemplates();
        } catch (error) {
            console.error('Error loading templates:', error);
        }
    }

    populateCategoryFilter() {
        const select = document.getElementById('template-category-filter');
        const categoriesHtml = this.categories.map(cat => 
            `<option value="${cat}">${cat}</option>`
        ).join('');
        select.innerHTML = `<option value="all">All Categories</option>${categoriesHtml}`;
    }

    renderTemplates() {
        const container = document.getElementById('templates-grid');
        container.innerHTML = this.templates.map(template => `
            <div class="template-card">
                <h5>${template.name}</h5>
                <p class="template-category">${template.category}</p>
                <p class="template-description">${template.description}</p>
                <div class="template-details">
                    <span>Ports: ${template.ports.length}</span>
                    <span>Duration: ~${template.estimatedDays} days</span>
                </div>
                <div class="template-actions">
                    <button class="btn-sm apply-template-btn" data-template-id="${template.id}">Apply</button>
                    <button class="btn-sm edit-template-btn" data-template-id="${template.id}">Edit</button>
                    <button class="btn-sm delete-template-btn" data-template-id="${template.id}">Delete</button>
                </div>
            </div>
        `).join('');

        container.querySelectorAll('.apply-template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.applyTemplate(e.target.dataset.templateId));
        });
        container.querySelectorAll('.edit-template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.editTemplate(e.target.dataset.templateId));
        });
        container.querySelectorAll('.delete-template-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.deleteTemplate(e.target.dataset.templateId));
        });
    }

    filterByCategory(category) {
        if (category === 'all') {
            this.renderTemplates();
            return;
        }

        const filtered = this.templates.filter(t => t.category === category);
        const original = this.templates;
        this.templates = filtered;
        this.renderTemplates();
        this.templates = original;
    }

    applyTemplate(templateId) {
        const template = this.templates.find(t => t.id === templateId);
        if (!template) return;

        const event = new CustomEvent('applyVoyageTemplate', { detail: template });
        document.dispatchEvent(event);
    }

    createTemplate() {
        alert('Template creation wizard - collect voyage parameters and save');
    }

    editTemplate(templateId) {
        alert(`Edit template ${templateId}`);
    }

    async deleteTemplate(templateId) {
        if (!confirm('Delete this template?')) return;

        try {
            const response = await fetch(`${this.config.apiEndpoint}/${templateId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Failed to delete template');

            await this.loadTemplates();
        } catch (error) {
            console.error('Error deleting template:', error);
        }
    }

    destroy() {
        const container = document.getElementById(this.config.containerId);
        if (container) container.innerHTML = '';
        this.initialized = false;
    }
}

// ======================
// BERTH CAPACITY PLANNING
// ======================

class BerthCapacityPlanning {
    constructor(config = {}) {
        this.config = {
            apiEndpoint: config.apiEndpoint || '/api/capacity',
            containerId: config.containerId || 'berth-capacity-planning',
            ...config
        };
        this.capacityData = [];
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        const container = document.getElementById(this.config.containerId);
        if (!container) return;
        
        this.render();
        await this.loadCapacityData();
        this.initialized = true;
    }

    render() {
        const container = document.getElementById(this.config.containerId);
        container.innerHTML = `
            <div class="capacity-planning-wrapper">
                <h3>Berth Capacity Planning</h3>
                <div class="capacity-controls">
                    <label>Time Range:
                        <select id="capacity-timerange">
                            <option value="7">7 Days</option>
                            <option value="14" selected>14 Days</option>
                            <option value="30">30 Days</option>
                            <option value="90">90 Days</option>
                        </select>
                    </label>
                    <button id="optimize-allocation-btn" class="btn-primary">Optimize Allocation</button>
                </div>
                <div class="capacity-vs-demand">
                    <h4>Capacity vs Demand</h4>
                    <div id="capacity-chart"></div>
                </div>
                <div class="utilization-forecast">
                    <h4>Utilization Forecast</h4>
                    <div id="utilization-forecast"></div>
                </div>
                <div class="allocation-recommendations">
                    <h4>Recommendations</h4>
                    <div id="recommendations-list"></div>
                </div>
            </div>
        `;
        this.attachEventListeners();
    }

    attachEventListeners() {
        document.getElementById('capacity-timerange')?.addEventListener('change', () => {
            this.loadCapacityData();
        });

        document.getElementById('optimize-allocation-btn')?.addEventListener('click', () => {
            this.optimizeAllocation();
        });
    }

    async loadCapacityData() {
        const days = document.getElementById('capacity-timerange')?.value || 14;

        try {
            const response = await fetch(`${this.config.apiEndpoint}?days=${days}`);
            const data = await response.json();
            this.capacityData = data.capacity || [];
            this.renderCapacityChart();
            this.renderForecast();
            this.renderRecommendations(data.recommendations || []);
        } catch (error) {
            console.error('Error loading capacity data:', error);
        }
    }

    renderCapacityChart() {
        const container = document.getElementById('capacity-chart');
        container.innerHTML = `
            <div class="simple-bar-chart">
                ${this.capacityData.map(item => `
                    <div class="chart-day">
                        <div class="day-label">${new Date(item.date).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})}</div>
                        <div class="bars">
                            <div class="bar capacity-bar" style="height: ${item.capacity}%" title="Capacity: ${item.capacity}%">
                                <span>${item.capacity}%</span>
                            </div>
                            <div class="bar demand-bar ${item.demand > 100 ? 'overbooked' : ''}" style="height: ${Math.min(item.demand, 150)}%" title="Demand: ${item.demand}%">
                                <span>${item.demand}%</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderForecast() {
        const container = document.getElementById('utilization-forecast');
        const avgUtilization = this.capacityData.reduce((sum, item) => sum + (item.demand / item.capacity) * 100, 0) / this.capacityData.length;
        
        container.innerHTML = `
            <div class="forecast-summary">
                <div class="forecast-metric">
                    <span class="metric-label">Average Utilization:</span>
                    <span class="metric-value">${avgUtilization.toFixed(1)}%</span>
                </div>
                <div class="forecast-metric">
                    <span class="metric-label">Peak Day:</span>
                    <span class="metric-value">${this.getPeakDay()}</span>
                </div>
                <div class="forecast-metric">
                    <span class="metric-label">Overbooking Days:</span>
                    <span class="metric-value">${this.getOverbookingDays()}</span>
                </div>
            </div>
        `;
    }

    renderRecommendations(recommendations) {
        const container = document.getElementById('recommendations-list');
        
        if (recommendations.length === 0) {
            container.innerHTML = '<p class="no-data">No recommendations at this time</p>';
            return;
        }

        container.innerHTML = recommendations.map(rec => `
            <div class="recommendation-item priority-${rec.priority}">
                <div class="rec-icon">${rec.priority === 'high' ? '' : 'ℹ'}</div>
                <div class="rec-content">
                    <h5>${rec.title}</h5>
                    <p>${rec.description}</p>
                    ${rec.action ? `<button class="btn-sm apply-rec-btn" data-action="${rec.action}">Apply</button>` : ''}
                </div>
            </div>
        `).join('');
    }

    getPeakDay() {
        if (this.capacityData.length === 0) return 'N/A';
        const peak = this.capacityData.reduce((max, item) => item.demand > max.demand ? item : max, this.capacityData[0]);
        return new Date(peak.date).toLocaleDateString();
    }

    getOverbookingDays() {
        return this.capacityData.filter(item => (item.demand / item.capacity) > 1).length;
    }

    async optimizeAllocation() {
        try {
            const response = await fetch(`${this.config.apiEndpoint}/optimize`, {
                method: 'POST'
            });

            if (!response.ok) throw new Error('Failed to optimize');

            const result = await response.json();
            alert(`Optimization complete. ${result.improvements} improvements suggested.`);
            await this.loadCapacityData();
        } catch (error) {
            console.error('Error optimizing allocation:', error);
            alert('Failed to optimize allocation');
        }
    }

    destroy() {
        const container = document.getElementById(this.config.containerId);
        if (container) container.innerHTML = '';
        this.initialized = false;
    }
}

// Export all modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        BunkerOptimization,
        WeatherIntegration,
        VesselTracking,
        PDFExport,
        ScenarioManagement,
        VoyageTemplates,
        BerthCapacityPlanning
    };
}
