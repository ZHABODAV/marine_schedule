/**
 * Berth Management Module
 * Comprehensive berth constraints, utilization tracking, and conflict visualization
 */

class BerthManagement {
  constructor(config = {}) {
    this.config = {
      apiEndpoint: config.apiEndpoint || '/api/berths',
      containerId: config.containerId || 'berth-management',
      refreshInterval: config.refreshInterval || 60000, // 1 minute
      ...config
    };
        
    this.berths = [];
    this.constraints = [];
    this.utilization = [];
    this.conflicts = [];
    this.currentView = 'dashboard'; // dashboard, constraints, capacity, conflicts
    this.initialized = false;
  }

  /**
     * Initialize the berth management module
     */
  async init() {
    if (this.initialized) {return;}
        
    const container = document.getElementById(this.config.containerId);
    if (!container) {
      console.error(`Container #${this.config.containerId} not found`);
      return;
    }
        
    this.render();
    await this.loadData();
    this.initialized = true;
  }

  /**
     * Render the module HTML structure
     */
  render() {
    const container = document.getElementById(this.config.containerId);
    container.innerHTML = `
            <div class="berth-management-wrapper">
                <!-- Header with View Tabs -->
                <div class="berth-header">
                    <h3>Berth Management</h3>
                    <div class="view-tabs">
                        <button class="tab-btn active" data-view="dashboard">Dashboard</button>
                        <button class="tab-btn" data-view="constraints">Constraints</button>
                        <button class="tab-btn" data-view="capacity">Capacity Planning</button>
                        <button class="tab-btn" data-view="conflicts">Conflicts</button>
                    </div>
                </div>

                <!-- Dashboard View -->
                <div id="berth-dashboard" class="berth-view active">
                    <div class="dashboard-summary">
                        <div class="summary-card">
                            <div class="card-label">Total Berths</div>
                            <div class="card-value" id="total-berths">0</div>
                        </div>
                        <div class="summary-card">
                            <div class="card-label">Active Vessels</div>
                            <div class="card-value" id="active-vessels">0</div>
                        </div>
                        <div class="summary-card">
                            <div class="card-label">Avg Utilization</div>
                            <div class="card-value" id="avg-utilization">0%</div>
                        </div>
                        <div class="summary-card alert">
                            <div class="card-label">Conflicts</div>
                            <div class="card-value" id="conflict-count">0</div>
                        </div>
                    </div>

                    <div class="berth-utilization-chart">
                        <h4>Berth Utilization Timeline</h4>
                        <div id="utilization-timeline"></div>
                    </div>

                    <div class="berth-status-grid">
                        <h4>Berth Status</h4>
                        <div id="berth-grid"></div>
                    </div>
                </div>

                <!-- Constraints View -->
                <div id="berth-constraints" class="berth-view">
                    <div class="constraints-header">
                        <h4>Berth Constraints</h4>
                        <button id="add-constraint-btn" class="btn-primary">Add Constraint</button>
                    </div>
                    <div id="constraints-list"></div>
                </div>

                <!-- Capacity Planning View -->
                <div id="berth-capacity" class="berth-view">
                    <div class="capacity-controls">
                        <label>
                            Time Range:
                            <select id="capacity-timerange">
                                <option value="7">7 Days</option>
                                <option value="14" selected>14 Days</option>
                                <option value="30">30 Days</option>
                                <option value="90">90 Days</option>
                            </select>
                        </label>
                        <button id="refresh-capacity-btn" class="btn-secondary">Refresh</button>
                    </div>
                    
                    <div class="capacity-chart">
                        <h4>Capacity vs Demand</h4>
                        <canvas id="capacity-chart-canvas"></canvas>
                    </div>

                    <div class="overbooking-warnings" id="overbooking-warnings">
                        <h4>Overbooking Warnings</h4>
                        <div id="overbooking-list"></div>
                    </div>
                </div>

                <!-- Conflicts View -->
                <div id="berth-conflicts" class="berth-view">
                    <div class="conflicts-controls">
                        <select id="conflict-filter">
                            <option value="all">All Conflicts</option>
                            <option value="timing">Timing Conflicts</option>
                            <option value="size">Size Constraints</option>
                            <option value="draft">Draft Limitations</option>
                        </select>
                        <button id="resolve-all-btn" class="btn-primary">Auto-Resolve</button>
                    </div>

                    <div id="conflicts-visualization">
                        <h4>Conflict Timeline</h4>
                        <div id="conflicts-timeline"></div>
                    </div>

                    <div id="conflicts-details">
                        <h4>Conflict Details</h4>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Berth</th>
                                    <th>Vessels</th>
                                    <th>Type</th>
                                    <th>Severity</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="conflicts-table-body"></tbody>
                        </table>
                    </div>
                </div>

                <!-- Constraint Editor Modal (hidden by default) -->
                <div id="constraint-editor-modal" class="modal" style="display: none;">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h4>Edit Constraint</h4>
                            <button class="modal-close">&times;</button>
                        </div>
                        <div class="modal-body">
                            <form id="constraint-form">
                                <div class="form-group">
                                    <label>Berth:</label>
                                    <select id="constraint-berth" required></select>
                                </div>
                                <div class="form-group">
                                    <label>Constraint Type:</label>
                                    <select id="constraint-type" required>
                                        <option value="max_length">Max Length</option>
                                        <option value="max_draft">Max Draft</option>
                                        <option value="max_beam">Max Beam</option>
                                        <option value="min_gap">Min Gap Between Vessels</option>
                                        <option value="maintenance">Maintenance Period</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Value:</label>
                                    <input type="number" id="constraint-value" step="0.1" required>
                                </div>
                                <div class="form-group">
                                    <label>Start Date:</label>
                                    <input type="datetime-local" id="constraint-start">
                                </div>
                                <div class="form-group">
                                    <label>End Date:</label>
                                    <input type="datetime-local" id="constraint-end">
                                </div>
                                <div class="form-actions">
                                    <button type="submit" class="btn-primary">Save</button>
                                    <button type="button" class="btn-secondary cancel-btn">Cancel</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;

    this.attachEventListeners();
  }

  /**
     * Attach event listeners
     */
  attachEventListeners() {
    // View tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.switchView(e.target.dataset.view);
      });
    });

    // Add constraint button
    document.getElementById('add-constraint-btn')?.addEventListener('click', () => {
      this.showConstraintEditor();
    });

    // Constraint form
    document.getElementById('constraint-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.saveConstraint();
    });

    // Modal close
    document.querySelector('.modal-close')?.addEventListener('click', () => {
      this.hideConstraintEditor();
    });

    document.querySelector('.cancel-btn')?.addEventListener('click', () => {
      this.hideConstraintEditor();
    });

    // Capacity refresh
    document.getElementById('refresh-capacity-btn')?.addEventListener('click', () => {
      this.loadCapacityData();
    });

    // Auto-resolve conflicts
    document.getElementById('resolve-all-btn')?.addEventListener('click', () => {
      this.autoResolveConflicts();
    });

    // Conflict filter
    document.getElementById('conflict-filter')?.addEventListener('change', (e) => {
      this.filterConflicts(e.target.value);
    });
  }

  /**
     * Load all berth data
     */
  async loadData() {
    try {
      const response = await fetch(this.config.apiEndpoint);
      if (!response.ok) {throw new Error('Failed to fetch berth data');}
            
      const data = await response.json();
      this.berths = data.berths || [];
      this.constraints = data.constraints || [];
      this.utilization = data.utilization || [];
      this.conflicts = data.conflicts || [];
            
      this.updateAllViews();
    } catch (error) {
      console.error('Error loading berth data:', error);
      this.showError('Failed to load berth data');
    }
  }

  /**
     * Switch between views
     */
  switchView(viewName) {
    this.currentView = viewName;
        
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === viewName);
    });

    // Update views
    document.querySelectorAll('.berth-view').forEach(view => {
      view.classList.remove('active');
    });
    document.getElementById(`berth-${viewName}`)?.classList.add('active');

    // Load specific view data
    switch(viewName) {
      case 'dashboard':
        this.updateDashboard();
        break;
      case 'constraints':
        this.updateConstraintsView();
        break;
      case 'capacity':
        this.loadCapacityData();
        break;
      case 'conflicts':
        this.updateConflictsView();
        break;
    }
  }

  /**
     * Update all views with current data
     */
  updateAllViews() {
    if (this.currentView === 'dashboard') {
      this.updateDashboard();
    }
  }

  /**
     * Update dashboard view
     */
  updateDashboard() {
    // Update summary cards
    document.getElementById('total-berths').textContent = this.berths.length;
        
    const activeVessels = this.berths.filter(b => b.currentVessel).length;
    document.getElementById('active-vessels').textContent = activeVessels;
        
    const avgUtil = this.calculateAverageUtilization();
    document.getElementById('avg-utilization').textContent = `${avgUtil}%`;
        
    document.getElementById('conflict-count').textContent = this.conflicts.length;

    // Render berth grid
    this.renderBerthGrid();
        
    // Render utilization timeline
    this.renderUtilizationTimeline();
  }

  /**
     * Render berth status grid
     */
  renderBerthGrid() {
    const grid = document.getElementById('berth-grid');
        
    grid.innerHTML = this.berths.map(berth => `
            <div class="berth-card ${berth.currentVessel ? 'occupied' : 'available'}">
                <div class="berth-name">${berth.name}</div>
                <div class="berth-status">${berth.currentVessel ? 'Occupied' : 'Available'}</div>
                ${berth.currentVessel ? `
                    <div class="berth-vessel">${berth.currentVessel}</div>
                    <div class="berth-time">${this.formatTime(berth.occupiedUntil)}</div>
                ` : ''}
                <div class="berth-specs">
                    L: ${berth.maxLength}m | D: ${berth.maxDraft}m
                </div>
            </div>
        `).join('');
  }

  /**
     * Render utilization timeline
     */
  renderUtilizationTimeline() {
    const timeline = document.getElementById('utilization-timeline');
        
    // Simple timeline visualization
    const days = 14; // Show 14 days
    const today = new Date();
        
    const html = `
            <div class="timeline-grid">
                ${Array.from({ length: days }, (_, i) => {
    const date = new Date(today);
    date.setDate(date.getDate() + i);
    const utilization = this.getUtilizationForDate(date);
                    
    return `
                        <div class="timeline-day">
                            <div class="day-label">${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
                            <div class="util-bar-container">
                                <div class="util-bar" style="height: ${utilization}%">
                                    <span class="util-label">${utilization}%</span>
                                </div>
                            </div>
                        </div>
                    `;
  }).join('')}
            </div>
        `;
        
    timeline.innerHTML = html;
  }

  /**
     * Update constraints view
     */
  updateConstraintsView() {
    const container = document.getElementById('constraints-list');
        
    if (this.constraints.length === 0) {
      container.innerHTML = '<div class="no-data">No constraints defined</div>';
      return;
    }

    container.innerHTML = this.constraints.map(constraint => `
            <div class="constraint-item">
                <div class="constraint-header">
                    <span class="constraint-berth">${constraint.berth}</span>
                    <span class="constraint-type">${this.formatConstraintType(constraint.type)}</span>
                </div>
                <div class="constraint-details">
                    <span class="constraint-value">Value: ${constraint.value}</span>
                    ${constraint.startDate ? `<span class="constraint-date">From: ${this.formatDate(constraint.startDate)}</span>` : ''}
                    ${constraint.endDate ? `<span class="constraint-date">To: ${this.formatDate(constraint.endDate)}</span>` : ''}
                </div>
                <div class="constraint-actions">
                    <button class="btn-sm edit-constraint-btn" data-constraint-id="${constraint.id}">Edit</button>
                    <button class="btn-sm delete-constraint-btn" data-constraint-id="${constraint.id}">Delete</button>
                </div>
            </div>
        `).join('');

    // Attach action listeners
    container.querySelectorAll('.edit-constraint-btn').forEach(btn => {
      btn.addEventListener('click', (e) => this.editConstraint(e.target.dataset.constraintId));
    });
    container.querySelectorAll('.delete-constraint-btn').forEach(btn => {
      btn.addEventListener('click', (e) => this.deleteConstraint(e.target.dataset.constraintId));
    });
  }

  /**
     * Load and display capacity planning data
     */
  async loadCapacityData() {
    const timeRange = document.getElementById('capacity-timerange')?.value || 14;
        
    try {
      const response = await fetch(`${this.config.apiEndpoint}/capacity?days=${timeRange}`);
      if (!response.ok) {throw new Error('Failed to load capacity data');}
            
      const data = await response.json();
      this.renderCapacityChart(data.capacity);
      this.renderOverbookingWarnings(data.warnings);
    } catch (error) {
      console.error('Error loading capacity data:', error);
      this.showError('Failed to load capacity data');
    }
  }

  /**
     * Render capacity chart
     */
  renderCapacityChart(data) {
    const canvas = document.getElementById('capacity-chart-canvas');
    const ctx = canvas.getContext('2d');
        
    // Simple bar chart implementation
    // In production, use Chart.js or similar library
    const chartHTML = `
            <div class="simple-chart">
                ${data.map(item => `
                    <div class="chart-row">
                        <div class="chart-label">${item.date}</div>
                        <div class="chart-bars">
                            <div class="bar capacity" style="width: ${item.capacity}%">
                                <span>Capacity: ${item.capacity}%</span>
                            </div>
                            <div class="bar demand ${item.demand > 100 ? 'overbooked' : ''}" style="width: ${Math.min(item.demand, 150)}%">
                                <span>Demand: ${item.demand}%</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    canvas.parentElement.innerHTML = chartHTML;
  }

  /**
     * Render overbooking warnings
     */
  renderOverbookingWarnings(warnings) {
    const container = document.getElementById('overbooking-list');
        
    if (!warnings || warnings.length === 0) {
      container.innerHTML = '<div class="no-warnings">No overbooking detected</div>';
      return;
    }

    container.innerHTML = warnings.map(warning => `
            <div class="warning-item severity-${warning.severity}">
                <div class="warning-icon"></div>
                <div class="warning-content">
                    <div class="warning-date">${this.formatDate(warning.date)}</div>
                    <div class="warning-message">${warning.message}</div>
                    <div class="warning-details">
                        Capacity: ${warning.capacity} | Demand: ${warning.demand} | 
                        Overbooking: ${warning.overbooking}%
                    </div>
                </div>
            </div>
        `).join('');
  }

  /**
     * Update conflicts view
     */
  updateConflictsView() {
    this.renderConflictsTimeline();
    this.renderConflictsTable();
  }

  /**
     * Render conflicts timeline
     */
  renderConflictsTimeline() {
    const timeline = document.getElementById('conflicts-timeline');
        
    if (this.conflicts.length === 0) {
      timeline.innerHTML = '<div class="no-conflicts">No conflicts detected</div>';
      return;
    }

    // Group conflicts by date
    const groupedConflicts = this.groupConflictsByDate();
        
    timeline.innerHTML = `
            <div class="conflicts-timeline-grid">
                ${Object.entries(groupedConflicts).map(([date, conflicts]) => `
                    <div class="timeline-date-group">
                        <div class="date-header">${date}</div>
                        <div class="conflicts-for-date">
                            ${conflicts.map(conflict => `
                                <div class="conflict-marker severity-${conflict.severity}" 
                                     data-conflict-id="${conflict.id}"
                                     title="${conflict.message}">
                                    ${conflict.berth}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
  }

  /**
     * Render conflicts table
     */
  renderConflictsTable() {
    const tbody = document.getElementById('conflicts-table-body');
        
    if (this.conflicts.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="no-data">No conflicts</td></tr>';
      return;
    }

    tbody.innerHTML = this.conflicts.map(conflict => `
            <tr class="severity-${conflict.severity}">
                <td>${this.formatTime(conflict.time)}</td>
                <td>${conflict.berth}</td>
                <td>${conflict.vessels.join(', ')}</td>
                <td>${this.formatConflictType(conflict.type)}</td>
                <td><span class="severity-badge ${conflict.severity}">${conflict.severity}</span></td>
                <td>
                    <button class="btn-sm resolve-conflict-btn" data-conflict-id="${conflict.id}">Resolve</button>
                    <button class="btn-sm view-conflict-btn" data-conflict-id="${conflict.id}">Details</button>
                </td>
            </tr>
        `).join('');

    // Attach action listeners
    tbody.querySelectorAll('.resolve-conflict-btn').forEach(btn => {
      btn.addEventListener('click', (e) => this.resolveConflict(e.target.dataset.conflictId));
    });
    tbody.querySelectorAll('.view-conflict-btn').forEach(btn => {
      btn.addEventListener('click', (e) => this.viewConflictDetails(e.target.dataset.conflictId));
    });
  }

  /**
     * Show constraint editor modal
     */
  showConstraintEditor(constraintId = null) {
    const modal = document.getElementById('constraint-editor-modal');
        
    // Populate berth dropdown
    const berthSelect = document.getElementById('constraint-berth');
    berthSelect.innerHTML = this.berths.map(b => 
      `<option value="${b.id}">${b.name}</option>`
    ).join('');

    if (constraintId) {
      const constraint = this.constraints.find(c => c.id === constraintId);
      if (constraint) {
        document.getElementById('constraint-berth').value = constraint.berth;
        document.getElementById('constraint-type').value = constraint.type;
        document.getElementById('constraint-value').value = constraint.value;
        document.getElementById('constraint-start').value = constraint.startDate || '';
        document.getElementById('constraint-end').value = constraint.endDate || '';
      }
    }

    modal.style.display = 'block';
  }

  /**
     * Hide constraint editor modal
     */
  hideConstraintEditor() {
    document.getElementById('constraint-editor-modal').style.display = 'none';
    document.getElementById('constraint-form').reset();
  }

  /**
     * Save constraint
     */
  async saveConstraint() {
    const formData = {
      berth: document.getElementById('constraint-berth').value,
      type: document.getElementById('constraint-type').value,
      value: parseFloat(document.getElementById('constraint-value').value),
      startDate: document.getElementById('constraint-start').value,
      endDate: document.getElementById('constraint-end').value
    };

    try {
      const response = await fetch(`${this.config.apiEndpoint}/constraints`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {throw new Error('Failed to save constraint');}

      this.hideConstraintEditor();
      await this.loadData();
      this.showSuccess('Constraint saved successfully');
    } catch (error) {
      console.error('Error saving constraint:', error);
      this.showError('Failed to save constraint');
    }
  }

  /**
     * Edit constraint
     */
  editConstraint(constraintId) {
    this.showConstraintEditor(constraintId);
  }

  /**
     * Delete constraint
     */
  async deleteConstraint(constraintId) {
    if (!confirm('Are you sure you want to delete this constraint?')) {return;}

    try {
      const response = await fetch(`${this.config.apiEndpoint}/constraints/${constraintId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {throw new Error('Failed to delete constraint');}

      await this.loadData();
      this.showSuccess('Constraint deleted successfully');
    } catch (error) {
      console.error('Error deleting constraint:', error);
      this.showError('Failed to delete constraint');
    }
  }

  /**
     * Auto-resolve all conflicts
     */
  async autoResolveConflicts() {
    if (!confirm('Attempt to auto-resolve all conflicts? This may reschedule vessels.')) {return;}

    try {
      const response = await fetch(`${this.config.apiEndpoint}/conflicts/auto-resolve`, {
        method: 'POST'
      });

      if (!response.ok) {throw new Error('Failed to auto-resolve conflicts');}

      const result = await response.json();
      await this.loadData();
      this.showSuccess(`Resolved ${result.resolved} conflicts. ${result.unresolved} remain.`);
    } catch (error) {
      console.error('Error auto-resolving conflicts:', error);
      this.showError('Failed to auto-resolve conflicts');
    }
  }

  /**
     * Resolve single conflict
     */
  async resolveConflict(conflictId) {
    try {
      const response = await fetch(`${this.config.apiEndpoint}/conflicts/${conflictId}/resolve`, {
        method: 'POST'
      });

      if (!response.ok) {throw new Error('Failed to resolve conflict');}

      await this.loadData();
      this.showSuccess('Conflict resolved');
    } catch (error) {
      console.error('Error resolving conflict:', error);
      this.showError('Failed to resolve conflict');
    }
  }

  /**
     * View conflict details
     */
  viewConflictDetails(conflictId) {
    const conflict = this.conflicts.find(c => c.id === conflictId);
    if (!conflict) {return;}

    const modalContent = `
            <h3>Conflict Details</h3>
            <div class="conflict-details">
                <p><strong>Time:</strong> ${this.formatTime(conflict.time)}</p>
                <p><strong>Berth:</strong> ${conflict.berth}</p>
                <p><strong>Vessels:</strong> ${conflict.vessels.join(', ')}</p>
                <p><strong>Type:</strong> ${this.formatConflictType(conflict.type)}</p>
                <p><strong>Severity:</strong> ${conflict.severity}</p>
                <p><strong>Description:</strong> ${conflict.message}</p>
                ${conflict.suggestions ? `<p><strong>Suggestions:</strong> ${conflict.suggestions}</p>` : ''}
            </div>
        `;

    const event = new CustomEvent('showModal', { detail: { content: modalContent } });
    document.dispatchEvent(event);
  }

  /**
     * Filter conflicts
     */
  filterConflicts(filterType) {
    if (filterType === 'all') {
      this.updateConflictsView();
      return;
    }

    const filtered = this.conflicts.filter(c => c.type === filterType);
    const originalConflicts = this.conflicts;
    this.conflicts = filtered;
    this.updateConflictsView();
    this.conflicts = originalConflicts;
  }

  /**
     * Helper: Calculate average utilization
     */
  calculateAverageUtilization() {
    if (this.utilization.length === 0) {return 0;}
    const sum = this.utilization.reduce((acc, u) => acc + u.value, 0);
    return Math.round(sum / this.utilization.length);
  }

  /**
     * Helper: Get utilization for a specific date
     */
  getUtilizationForDate(date) {
    const dateStr = date.toISOString().split('T')[0];
    const util = this.utilization.find(u => u.date === dateStr);
    return util ? util.value : 0;
  }

  /**
     * Helper: Group conflicts by date
     */
  groupConflictsByDate() {
    const grouped = {};
    this.conflicts.forEach(conflict => {
      const date = new Date(conflict.time).toLocaleDateString();
      if (!grouped[date]) {grouped[date] = [];}
      grouped[date].push(conflict);
    });
    return grouped;
  }

  /**
     * Helper: Format constraint type
     */
  formatConstraintType(type) {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  /**
     * Helper: Format conflict type
     */
  formatConflictType(type) {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  /**
     * Helper: Format date
     */
  formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString();
  }

  /**
     * Helper: Format timestamp
     */
  formatTime(timestamp) {
    return new Date(timestamp).toLocaleString();
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
     * Destroy the module
     */
  destroy() {
    const container = document.getElementById(this.config.containerId);
    if (container) {container.innerHTML = '';}
    this.initialized = false;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BerthManagement;
}
