<template>
  <div class="gantt-chart-container">
    <div class="gantt-controls">
      <div class="control-group">
        <label for="gantt-days">Timeline Days:</label>
        <input
          id="gantt-days"
          v-model.number="timelineDays"
          type="number"
          min="7"
          max="365"
          class="form-control"
        />
      </div>
      
      <div class="control-group">
        <label for="voyage-filter">Voyage Filter:</label>
        <select id="voyage-filter" v-model="voyageFilter" class="form-control">
          <option value="all">All Voyages</option>
          <option value="active">Active Only</option>
          <option value="planned">Planned Only</option>
          <option value="custom">Custom Selection</option>
        </select>
      </div>

      <div class="button-group">
        <button @click="refreshGantt" class="btn btn-primary">
          <span v-if="isLoading">Loading...</span>
          <span v-else>Refresh</span>
        </button>
        <button @click="exportGantt" class="btn btn-secondary">
          Export
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading-state">
      <LoadingSpinner />
      <p>Generating Gantt chart...</p>
    </div>

    <div v-else-if="ganttData.length === 0" class="empty-state">
      <p>No voyage data available. Generate a schedule first.</p>
    </div>

    <div v-else class="gantt-chart" ref="ganttContainer">
      <div class="gantt-legend">
        <span class="legend-item">
          <span class="legend-color op-loading"></span>
          П - Loading (Погрузка)
        </span>
        <span class="legend-item">
          <span class="legend-color op-discharge"></span>
          В - Discharge (Выгрузка)
        </span>
        <span class="legend-item">
          <span class="legend-color op-transit"></span>
          Т - Transit (Транзит)
        </span>
        <span class="legend-item">
          <span class="legend-color op-ballast"></span>
          Б - Ballast (Балласт)
        </span>
        <span class="legend-item">
          <span class="legend-color op-canal"></span>
          К - Canal (Канал)
        </span>
        <span class="legend-item">
          <span class="legend-color op-bunker"></span>
          Ф - Bunker (Бункеровка)
        </span>
      </div>

      <table class="gantt-table">
        <thead>
          <tr>
            <th class="vessel-header">Vessel</th>
            <th v-for="day in timelineDays" :key="day" class="day-header">
              {{ day }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in ganttData" :key="row.vessel">
            <th class="vessel-name">{{ row.vessel }}</th>
            <td
              v-for="(day, index) in row.days"
              :key="index"
              :class="['gantt-cell', day.class ? `op-${day.class}` : '']"
              :title="getCellTitle(row.vessel, index, day)"
            >
              {{ day.operation }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="ganttData.length > 0" class="gantt-stats">
      <div class="stat-card">
        <h4>Vessels</h4>
        <p class="stat-value">{{ ganttData.length }}</p>
      </div>
      <div class="stat-card">
        <h4>Timeline</h4>
        <p class="stat-value">{{ timelineDays }} days</p>
      </div>
      <div class="stat-card">
        <h4>Operations</h4>
        <p class="stat-value">{{ totalOperations }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useVoyageStore } from '@/stores/voyage'
import { useVesselStore } from '@/stores/vessel'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { generateGanttData, generateGanttFromVoyages, exportGantt as exportGanttXLS } from '@/services/gantt.service'

interface GanttDay {
  operation: string
  class: string
}

interface GanttRow {
  vessel: string
  days: GanttDay[]
}

const voyageStore = useVoyageStore()
const vesselStore = useVesselStore()

const ganttContainer = ref<HTMLElement | null>(null)
const timelineDays = ref(30)
const voyageFilter = ref('all')
const isLoading = ref(false)
const error = ref('')
const ganttData = ref<GanttRow[]>([])

const totalOperations = computed(() => {
  return ganttData.value.reduce((total, row) => {
    return total + row.days.filter(day => day.operation).length
  }, 0)
})

const refreshGantt = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    // Get voyages from store
    const voyages = voyageStore.voyages
    
    if (voyages.length > 0) {
      ganttData.value = await generateGanttFromVoyages(voyages, timelineDays.value)
    } else {
      // Fallback to generate from API
      ganttData.value = await generateGanttData(timelineDays.value)
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to generate Gantt chart'
    console.error('Gantt generation error:', err)
  } finally {
    isLoading.value = false
  }
}

const exportGantt = async () => {
  try {
    await exportGanttXLS()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to export Gantt chart'
  }
}

const getCellTitle = (vessel: string, dayIndex: number, day: GanttDay): string => {
  if (!day.operation) return ''
  
  const operationNames: Record<string, string> = {
    'loading': 'Loading Port',
    'discharge': 'Discharge Port',
    'transit': 'Sea Transit',
    'ballast': 'Ballast Voyage',
    'canal': 'Canal Transit',
    'bunker': 'Bunkering',
    'waiting': 'Waiting'
  }
  
  return `${vessel} - Day ${dayIndex + 1}: ${operationNames[day.class] || day.class}`
}

// Watch for changes in timeline days
watch(timelineDays, () => {
  refreshGantt()
})

// Initial load
onMounted(() => {
  refreshGantt()
})
</script>

<style scoped>
.gantt-chart-container {
  width: 100%;
  padding: 1.5rem;
  background: var(--bg-primary);
  border-radius: 8px;
}

.gantt-controls {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-group label {
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
}

.form-control {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  min-width: 100px;
}

.button-group {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-primary-dark);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-tertiary);
}

.alert {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.alert-error {
  background: var(--accent-danger-light);
  color: var(--accent-danger);
  border-left: 4px solid var(--accent-danger);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.gantt-legend {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  padding: 1rem;
  background: var(--bg-secondary);
  border-radius: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-primary);
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 3px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.gantt-chart {
  overflow-x: auto;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.gantt-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-secondary);
}

.gantt-table thead {
  position: sticky;
  top: 0;
  background: var(--bg-primary);
  z-index: 10;
}

.vessel-header {
  position: sticky;
  left: 0;
  background: var(--bg-primary);
  z-index: 11;
  padding: 0.75rem 1rem;
  text-align: left;
  border: 1px solid var(--border-color);
  min-width: 150px;
}

.day-header {
  padding: 0.5rem;
  text-align: center;
  border: 1px solid var(--border-color);
  min-width: 40px;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.vessel-name {
  position: sticky;
  left: 0;
  background: var(--bg-secondary);
  padding: 0.75rem 1rem;
  text-align: left;
  border: 1px solid var(--border-color);
  font-weight: 500;
  color: var(--text-primary);
  z-index: 5;
}

.gantt-cell {
  padding: 0.5rem;
  text-align: center;
  border: 1px solid var(--border-color);
  font-weight: 600;
  font-size: 0.875rem;
  min-width: 40px;
  transition: all 0.2s;
  cursor: default;
}

.gantt-cell:hover {
  transform: scale(1.1);
  z-index: 20;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.op-loading {
  background: #00b894;
  color: white;
}

.op-discharge {
  background: #0984e3;
  color: white;
}

.op-transit {
  background: #6c5ce7;
  color: white;
}

.op-ballast {
  background: #fdcb6e;
  color: #2d3436;
}

.op-canal {
  background: #e17055;
  color: white;
}

.op-bunker {
  background: #fd79a8;
  color: white;
}

.op-waiting {
  background: #b2bec3;
  color: #2d3436;
}

.gantt-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.stat-card {
  background: var(--bg-secondary);
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  border: 1px solid var(--border-color);
}

.stat-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
}

.stat-value {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent-primary);
}
</style>
