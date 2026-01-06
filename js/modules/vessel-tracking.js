/* global L */
/**
 * Vessel Tracking Module
 * Handles vessel tracking visualization on map and list
 * Extracted from vessel_scheduler_enhanced.html
 */

export class VesselTracking {
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
    this.intervalId = null;
  }

  async init() {
    if (this.initialized) {
      return;
    }
    const container = document.getElementById(this.config.containerId);
    if (!container) {
      return;
    }
    
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
        <h3>Трекинг судов</h3>
        <div class="tracking-controls">
          <button id="refresh-tracking-btn" class="btn-secondary">Обновить</button>
          <input type="text" id="vessel-search" placeholder="Поиск судна..." />
        </div>
        <div id="tracking-map" style="height: 500px; width: 100%;"></div>
        <div class="vessel-list">
          <h4>Список судов</h4>
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
    if (!mapDiv) {
      return;
    }

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
    if (!this.map) {
      return;
    }

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
            <th>Судно</th>
            <th>Статус</th>
            <th>Позиция</th>
            <th>Скорость</th>
            <th>Назначение</th>
            <th>ETA</th>
          </tr>
        </thead>
        <tbody>
          ${this.vessels.map(vessel => `
            <tr>
              <td><strong>${vessel.name}</strong></td>
              <td><span class="status-badge ${vessel.status}">${vessel.status}</span></td>
              <td>${vessel.position ? `${vessel.position.lat.toFixed(2)}°, ${vessel.position.lon.toFixed(2)}°` : 'Н/Д'}</td>
              <td>${vessel.speed || 0} узлов</td>
              <td>${vessel.destination || 'Н/Д'}</td>
              <td>${vessel.eta ? new Date(vessel.eta).toLocaleString() : 'Н/Д'}</td>
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
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    this.intervalId = setInterval(() => {
      this.loadVesselData();
    }, this.config.updateInterval);
  }

  destroy() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    const container = document.getElementById(this.config.containerId);
    if (container) {
      container.innerHTML = '';
    }
    if (this.map) {
      this.map.remove();
    }
    this.initialized = false;
  }
}
