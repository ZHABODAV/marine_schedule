<template>
  <div class="financial-container">
    <div class="financial-controls">
      <div class="button-group">
        <button @click="calculateAnalysis" class="btn btn-primary">
          <span v-if="isCalculating">Calculating...</span>
          <span v-else>Calculate Analysis</span>
        </button>
        <button @click="optimizeBunker" class="btn btn-secondary">
          Optimize Bunker
        </button>
        <button @click="exportAnalysis" class="btn btn-secondary">
          Export Report
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <div v-if="isCalculating" class="loading-state">
      <LoadingSpinner />
      <p>Calculating financial analysis...</p>
    </div>

    <div v-else-if="!financialData" class="empty-state">
      <p>Click "Calculate Analysis" to generate financial report</p>
    </div>

    <template v-else>
      <!-- Summary Cards -->
      <div class="summary-cards">
        <div class="stat-card highlight">
          <h4>Total Costs</h4>
          <p class="stat-value">${{ formatNumber(financialData.totalCosts) }}</p>
        </div>
        <div class="stat-card">
          <h4>Total Revenue</h4>
          <p class="stat-value success">${{ formatNumber(financialData.totalRevenue) }}</p>
        </div>
        <div class="stat-card">
          <h4>Total Profit</h4>
          <p :class="['stat-value', financialData.totalProfit >= 0 ? 'success' : 'danger']">
            ${{ formatNumber(financialData.totalProfit) }}
          </p>
        </div>
        <div class="stat-card">
          <h4>Average TCE</h4>
          <p class="stat-value">${{ formatNumber(financialData.avgTCE) }}/day</p>
        </div>
      </div>

      <!-- Cost Breakdown -->
      <div class="section">
        <h3>Cost Breakdown</h3>
        <div class="cost-breakdown">
          <div class="breakdown-card">
            <div class="breakdown-header">
              <h4>Bunker Costs</h4>
              <span class="cost-value warning">${{ formatNumber(totalBunkerCost) }}</span>
            </div>
            <div class="breakdown-details">
              <div class="detail-item">
                <span>Potential Savings</span>
                <span class="success">${{ formatNumber(potentialSavings) }}</span>
              </div>
              <div class="detail-item">
                <span>Avg Consumption</span>
                <span>{{ avgConsumption.toFixed(1) }} MT/day</span>
              </div>
            </div>
            <div class="breakdown-bar">
              <div
                class="bar-fill warning"
                :style="{ width: `${(totalBunkerCost / financialData.totalCosts) * 100}%` }"
              ></div>
            </div>
          </div>

          <div class="breakdown-card">
            <div class="breakdown-header">
              <h4>Hire Costs</h4>
              <span class="cost-value primary">${{ formatNumber(totalHireCost) }}</span>
            </div>
            <div class="breakdown-details">
              <div class="detail-item">
                <span>Total Days</span>
                <span>{{ financialData.totalDays.toFixed(1) }}</span>
              </div>
            </div>
            <div class="breakdown-bar">
              <div
                class="bar-fill primary"
                :style="{ width: `${(totalHireCost / financialData.totalCosts) * 100}%` }"
              ></div>
            </div>
          </div>

          <div class="breakdown-card">
            <div class="breakdown-header">
              <h4>Other Costs</h4>
              <span class="cost-value">${{ formatNumber(totalOtherCost) }}</span>
            </div>
            <div class="breakdown-details">
              <div class="detail-item">
                <span>Port Fees, etc.</span>
                <span>{{ ((totalOtherCost / financialData.totalCosts) * 100).toFixed(1) }}%</span>
              </div>
            </div>
            <div class="breakdown-bar">
              <div
                class="bar-fill"
                :style="{ width: `${(totalOtherCost / financialData.totalCosts) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Cost Distribution Chart -->
      <div class="section">
        <h3>Cost Distribution</h3>
        <div class="chart-container">
          <canvas ref="costChartCanvas"></canvas>
        </div>
      </div>

      <!-- Detailed Voyage Analysis Table -->
      <div class="section">
        <h3>Detailed Voyage Analysis</h3>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Voyage</th>
                <th>Vessel</th>
                <th>Cargo (MT)</th>
                <th>Distance (nm)</th>
                <th>Days</th>
                <th>Bunker Cost</th>
                <th>Hire Cost</th>
                <th>Port Cost</th>
                <th>Total Cost</th>
                <th>Revenue</th>
                <th>Profit</th>
                <th>TCE</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="voyage in financialData.voyages" :key="voyage.id">
                <td>{{ voyage.id }}</td>
                <td>{{ voyage.vessel }}</td>
                <td>{{ formatNumber(voyage.cargo) }}</td>
                <td>{{ formatNumber(voyage.distance) }}</td>
                <td>{{ voyage.seaDays.toFixed(1) }}</td>
                <td class="cost-cell warning">${{ formatNumber(voyage.bunkerCost) }}</td>
                <td class="cost-cell">${{ formatNumber(voyage.hireCost) }}</td>
                <td class="cost-cell">${{ formatNumber(voyage.portCost) }}</td>
                <td class="cost-cell"><strong>${{ formatNumber(voyage.totalCost) }}</strong></td>
                <td class="cost-cell success">${{ formatNumber(voyage.revenue) }}</td>
                <td :class="['cost-cell', voyage.profit >= 0 ? 'success' : 'danger']">
                  ${{ formatNumber(voyage.profit) }}
                </td>
                <td class="cost-cell">${{ formatNumber(voyage.tce) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="total-row">
                <td colspan="2"><strong>TOTAL</strong></td>
                <td><strong>{{ formatNumber(totalCargo) }}</strong></td>
                <td><strong>{{ formatNumber(financialData.totalDistance) }}</strong></td>
                <td><strong>{{ financialData.totalDays.toFixed(1) }}</strong></td>
                <td class="cost-cell warning"><strong>${{ formatNumber(totalBunkerCost) }}</strong></td>
                <td class="cost-cell"><strong>${{ formatNumber(totalHireCost) }}</strong></td>
                <td>-</td>
                <td class="cost-cell"><strong>${{ formatNumber(financialData.totalCosts) }}</strong></td>
                <td class="cost-cell success"><strong>${{ formatNumber(financialData.totalRevenue) }}</strong></td>
                <td :class="['cost-cell', financialData.totalProfit >= 0 ? 'success' : 'danger']">
                  <strong>${{ formatNumber(financialData.totalProfit) }}</strong>
                </td>
                <td class="cost-cell"><strong>${{ formatNumber(financialData.avgTCE) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import { useVoyageStore } from '@/stores/voyage'
import { useCargoStore } from '@/stores/cargo'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import {
  calculateFinancialAnalysis,
  optimizeBunkerStrategy,
  type FinancialData,
} from '@/services/financial.service'

Chart.register(...registerables)

const voyageStore = useVoyageStore()
const cargoStore = useCargoStore()

const costChartCanvas = ref<HTMLCanvasElement | null>(null)
const isCalculating = ref(false)
const error = ref('')
const financialData = ref<FinancialData | null>(null)

let costChart: Chart | null = null

const totalBunkerCost = computed(() => {
  if (!financialData.value) return 0
  return financialData.value.voyages.reduce((sum, v) => sum + v.bunkerCost, 0)
})

const totalHireCost = computed(() => {
  if (!financialData.value) return 0
  return financialData.value.voyages.reduce((sum, v) => sum + v.hireCost, 0)
})

const totalOtherCost = computed(() => {
  if (!financialData.value) return 0
  return financialData.value.totalCosts - totalBunkerCost.value - totalHireCost.value
})

const totalCargo = computed(() => {
  if (!financialData.value) return 0
  return financialData.value.voyages.reduce((sum, v) => sum + v.cargo, 0)
})

const potentialSavings = computed(() => {
  return Math.round(totalBunkerCost.value * 0.15) // 15% optimization potential
})

const avgConsumption = computed(() => {
  if (!financialData.value || financialData.value.voyages.length === 0) return 0
  return 35 // Simplified - should calculate from actual data
})

const formatNumber = (num: number): string => {
  return Math.round(num).toLocaleString()
}

const calculateAnalysis = async () => {
  isCalculating.value = true
  error.value = ''

  try {
    financialData.value = await calculateFinancialAnalysis()
    await nextTick()
    renderCostChart()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to calculate financial analysis'
    console.error('Financial analysis error:', err)
  } finally {
    isCalculating.value = false
  }
}

const optimizeBunker = async () => {
  try {
    await optimizeBunkerStrategy()
    await calculateAnalysis() // Refresh after optimization
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to optimize bunker strategy'
  }
}

const exportAnalysis = () => {
  if (!financialData.value) return

  // Simple CSV export
  let csv = 'Voyage,Vessel,Cargo,Distance,Days,Bunker Cost,Hire Cost,Port Cost,Total Cost,Revenue,Profit,TCE\n'
  
  financialData.value.voyages.forEach(v => {
    csv += `${v.id},${v.vessel},${v.cargo},${v.distance},${v.seaDays.toFixed(1)},${v.bunkerCost},${v.hireCost},${v.portCost},${v.totalCost},${v.revenue},${v.profit},${v.tce}\n`
  })

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `financial_analysis_${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

const renderCostChart = () => {
  if (!costChartCanvas.value || !financialData.value) return

  if (costChart) {
    costChart.destroy()
  }

  const ctx = costChartCanvas.value.getContext('2d')
  if (!ctx) return

  costChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Bunker Costs', 'Hire Costs', 'Other Costs'],
      datasets: [
        {
          data: [totalBunkerCost.value, totalHireCost.value, totalOtherCost.value],
          backgroundColor: ['#fdcb6e', '#4a9eff', '#b2bec3'],
          borderColor: ['#f39c12', '#0984e3', '#95a5a6'],
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#e4e6eb',
            font: {
              size: 14,
            },
          },
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || ''
              const value = context.parsed || 0
              const total = financialData.value?.totalCosts || 1
              const percentage = ((value / total) * 100).toFixed(1)
              return `${label}: $${formatNumber(value)} (${percentage}%)`
            },
          },
        },
      },
    },
  })
}

onMounted(async () => {
  // Auto-calculate on mount if data is available
  if (voyageStore.voyages.length > 0 || cargoStore.cargo.length > 0) {
    await calculateAnalysis()
  }
})
</script>

<style scoped>
.financial-container {
  width: 100%;
  padding: 1.5rem;
  background: var(--bg-primary);
  border-radius: 8px;
}

.financial-controls {
  margin-bottom: 1.5rem;
}

.button-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
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

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bg-secondary);
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  border: 1px solid var(--border-color);
}

.stat-card.highlight {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 1px var(--accent-primary);
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
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-value.success {
  color: #00b894;
}

.stat-value.danger {
  color: #d63031;
}

.stat-value.warning {
  color: #fdcb6e;
}

.stat-value.primary {
  color: var(--accent-primary);
}

.section {
  margin-bottom: 2rem;
}

.section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: 1.25rem;
}

.cost-breakdown {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.breakdown-card {
  background: var(--bg-secondary);
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.breakdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.breakdown-header h4 {
  margin: 0;
  font-size: 1rem;
  color: var(--text-primary);
}

.cost-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.breakdown-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.breakdown-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: var(--text-secondary);
  transition: width 0.3s ease;
}

.bar-fill.warning {
  background: #fdcb6e;
}

.bar-fill.primary {
  background: var(--accent-primary);
}

.chart-container {
  height: 400px;
  background: var(--bg-secondary);
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.table-container {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-secondary);
  font-size: 0.875rem;
}

.data-table thead {
  background: var(--bg-primary);
  position: sticky;
  top: 0;
}

.data-table th {
  padding: 0.75rem;
  text-align: left;
  border: 1px solid var(--border-color);
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}

.data-table td {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.cost-cell {
  text-align: right;
  font-family: 'Courier New', monospace;
}

.cost-cell.success {
  color: #00b894;
}

.cost-cell.danger {
  color: #d63031;
}

.cost-cell.warning {
  color: #fdcb6e;
}

.total-row {
  background: var(--bg-primary);
  font-weight: 700;
}

.total-row td {
  border-top: 2px solid var(--border-color);
}
</style>
