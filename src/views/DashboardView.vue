<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <div class="module-selector">
        <label for="module-select">Module:</label>
        <select id="module-select" v-model="selectedModule" @change="onModuleChange">
          <option value="all">All Modules</option>
          <option value="olya">Olya</option>
          <option value="balakovo">Balakovo</option>
          <option value="deepsea">Deep Sea</option>
        </select>
      </div>
    </div>
    
    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon vessel-icon"></div>
        <div class="stat-content">
          <h3>Total Vessels</h3>
          <p class="stat-value">{{ vesselStore.totalVessels }}</p>
          <span class="stat-label">Active: {{ vesselStore.activeVessels.length }}</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon voyage-icon"></div>
        <div class="stat-content">
          <h3>Active Voyages</h3>
          <p class="stat-value">{{ voyageStore.activeVoyages.length }}</p>
          <span class="stat-label">Planned: {{ voyageStore.plannedVoyages.length }}</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon cargo-icon"></div>
        <div class="stat-content">
          <h3>Cargo Operations</h3>
          <p class="stat-value">{{ cargoStore.totalCargo }}</p>
          <span class="stat-label">Pending: {{ cargoStore.pendingCargo.length }}</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon status-icon"></div>
        <div class="stat-content">
          <h3>System Status</h3>
          <p class="stat-value status-ok">Operational</p>
          <span class="stat-label">All systems running</span>
        </div>
      </div>
    </div>
    
    <!-- Charts Section -->
    <div class="charts-section">
      <div class="chart-card">
        <h3>Voyage Statistics</h3>
        <div class="chart-container">
          <canvas ref="voyageChartCanvas"></canvas>
        </div>
      </div>
      
      <div class="chart-card">
        <h3>Vessel Utilization</h3>
        <div class="chart-container">
          <canvas ref="utilizationChartCanvas"></canvas>
        </div>
      </div>
    </div>
    
    <!-- Recent Activity -->
    <div class="recent-activity">
      <h3>Recent Activity</h3>
      <div class="activity-list">
        <div v-if="loading" class="loading">
          <LoadingSpinner />
        </div>
        <div v-else-if="recentVoyages.length === 0" class="empty-state">
          <p>No recent activity</p>
        </div>
        <div v-else class="activity-items">
          <div v-for="voyage in recentVoyages" :key="voyage.id" class="activity-item">
            <div class="activity-icon">
              <span>{{ getStatusIcon(voyage.status) }}</span>
            </div>
            <div class="activity-content">
              <p class="activity-title">{{ voyage.vessel_name || 'Vessel' }} - {{ voyage.route_name || 'Route' }}</p>
              <p class="activity-meta">
                <span class="activity-status" :class="`status-${voyage.status}`">{{ voyage.status }}</span>
                <span class="activity-date">{{ formatDate(voyage.updated_at || voyage.created_at) }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useVesselStore } from '@/stores/vessel'
import { useVoyageStore } from '@/stores/voyage'
import { useCargoStore } from '@/stores/cargo'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const vesselStore = useVesselStore()
const voyageStore = useVoyageStore()
const cargoStore = useCargoStore()

const selectedModule = ref('all')
const loading = ref(false)
const voyageChartCanvas = ref<HTMLCanvasElement | null>(null)
const utilizationChartCanvas = ref<HTMLCanvasElement | null>(null)
let voyageChart: Chart | null = null
let utilizationChart: Chart | null = null

const recentVoyages = computed(() => {
  return voyageStore.voyages
    .slice()
    .sort((a, b) => {
      const dateA = new Date(a.updated_at || a.created_at || 0).getTime()
      const dateB = new Date(b.updated_at || b.created_at || 0).getTime()
      return dateB - dateA
    })
    .slice(0, 10)
})

function onModuleChange() {
  loadDashboardData()
}

async function loadDashboardData() {
  loading.value = true
  try {
    const module = selectedModule.value === 'all' ? undefined : selectedModule.value
    await Promise.all([
      vesselStore.fetchVessels(module),
      voyageStore.fetchVoyages(module),
      cargoStore.fetchCargo(module)
    ])
    updateCharts()
  } finally {
    loading.value = false
  }
}

function updateCharts() {
  createVoyageChart()
  createUtilizationChart()
}

function createVoyageChart() {
  if (!voyageChartCanvas.value) return
  
  if (voyageChart) {
    voyageChart.destroy()
  }
  
  const ctx = voyageChartCanvas.value.getContext('2d')
  if (!ctx) return
  
  voyageChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Planned', 'Active', 'Completed'],
      datasets: [{
        label: 'Voyages',
        data: [
          voyageStore.plannedVoyages.length,
          voyageStore.activeVoyages.length,
          voyageStore.completedVoyages.length
        ],
        backgroundColor: [
          'rgba(255, 206, 86, 0.7)',
          'rgba(54, 162, 235, 0.7)',
          'rgba(75, 192, 192, 0.7)'
        ],
        borderColor: [
          'rgba(255, 206, 86, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  })
}

function createUtilizationChart() {
  if (!utilizationChartCanvas.value) return
  
  if (utilizationChart) {
    utilizationChart.destroy()
  }
  
  const ctx = utilizationChartCanvas.value.getContext('2d')
  if (!ctx) return
  
  const vesselTypes = Object.keys(vesselStore.vesselsByType)
  const vesselCounts = vesselTypes.map(type => vesselStore.vesselsByType[type].length)
  
  utilizationChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: vesselTypes.length > 0 ? vesselTypes : ['No Data'],
      datasets: [{
        label: 'Vessels by Type',
        data: vesselCounts.length > 0 ? vesselCounts : [1],
        backgroundColor: [
          'rgba(255, 99, 132, 0.7)',
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 206, 86, 0.7)',
          'rgba(75, 192, 192, 0.7)',
          'rgba(153, 102, 255, 0.7)',
          'rgba(255, 159, 64, 0.7)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  })
}

function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    planned: '',
    active: '',
    completed: '',
    cancelled: ''
  }
  return icons[status] || ''
}

function formatDate(dateString: string | Date | undefined): string {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return 'N/A'
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  
  return date.toLocaleDateString()
}

onMounted(() => {
  loadDashboardData()
})

watch(() => [voyageStore.voyages, vesselStore.vessels], () => {
  updateCharts()
}, { deep: true })
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
}

.module-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.module-selector label {
  font-weight: 600;
  color: #64748b;
}

.module-selector select {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  font-size: 1rem;
  cursor: pointer;
  transition: border-color 0.2s;
}

.module-selector select:hover {
  border-color: #42b983;
}

.module-selector select:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.vessel-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.voyage-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.cargo-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.status-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-content h3 {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 2rem;
  color: #2c3e50;
  font-weight: bold;
  margin: 0 0 0.25rem 0;
}

.stat-label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.status-ok {
  color: #42b983;
  font-size: 1.5rem;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.chart-card h3 {
  font-size: 1.125rem;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  font-weight: 600;
}

.chart-container {
  height: 300px;
  position: relative;
}

.recent-activity {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.recent-activity h3 {
  font-size: 1.125rem;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  font-weight: 600;
}

.activity-list {
  max-height: 400px;
  overflow-y: auto;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #94a3b8;
}

.activity-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #f1f5f9;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.activity-item:hover {
  background-color: #f8fafc;
}

.activity-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  border-radius: 8px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.activity-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #64748b;
}

.activity-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.status-planned {
  background: #fef3c7;
  color: #92400e;
}

.status-active {
  background: #dbeafe;
  color: #1e40af;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.activity-date {
  color: #94a3b8;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
}
</style>
