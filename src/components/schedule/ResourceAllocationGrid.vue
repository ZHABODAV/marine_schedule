<template>
  <div class="resource-allocation-grid">
    <div class="grid-header">
      <h3>Resource Allocation Timeline - {{ year }}</h3>
      <div class="view-controls">
        <button
          :class="['view-btn', { active: viewMode === 'month' }]"
          @click="viewMode = 'month'"
        >
          Monthly
        </button>
        <button
          :class="['view-btn', { active: viewMode === 'quarter' }]"
          @click="viewMode = 'quarter'"
        >
          Quarterly
        </button>
      </div>
    </div>

    <div class="grid-container">
      <!-- Timeline Header -->
      <div class="timeline-header">
        <div class="vessel-col-header">Vessel</div>
        <div class="months-row">
          <div
            v-for="month in displayMonths"
            :key="month.index"
            class="month-header"
            :style="{ width: month.width }"
          >
            {{ month.name }}
          </div>
        </div>
      </div>

      <!-- Vessel Rows -->
      <div class="vessel-rows">
        <div
          v-for="vessel in vesselAllocations"
          :key="vessel.vesselId"
          class="vessel-row"
        >
          <div class="vessel-info">
            <span class="vessel-name">{{ vessel.vesselName }}</span>
            <span class="utilization-badge" :class="getUtilizationClass(vessel.utilizationRate)">
              {{ vessel.utilizationRate.toFixed(0) }}%
            </span>
          </div>
          <div class="timeline-track">
            <div
              v-for="allocation in getVesselMonthlyData(vessel.vesselId)"
              :key="`${vessel.vesselId}-${allocation.month}`"
              class="month-cell"
              :class="{ 'has-voyages': allocation.voyages > 0 }"
              :title="`${getMonthName(allocation.month)}: ${allocation.voyages} voyage(s)`"
              @click="handleCellClick(vessel.vesselId, allocation.month)"
            >
              <div
                v-if="allocation.voyages > 0"
                class="allocation-bar"
                :style="{ height: `${Math.min(allocation.utilization, 100)}%` }"
              >
                <span class="voyage-count">{{ allocation.voyages }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="vesselAllocations.length === 0" class="empty-grid">
        <i class="icon-calendar"></i>
        <p>No resource allocations to display</p>
      </div>
    </div>

    <!-- Details Panel -->
    <div v-if="selectedCell" class="details-panel">
      <div class="details-header">
        <h4>{{ selectedCell.vesselName }} - {{ getMonthName(selectedCell.month) }}</h4>
        <button class="close-btn" @click="selectedCell = null">×</button>
      </div>
      <div class="details-content">
        <div class="detail-item">
          <span class="label">Voyages:</span>
          <span class="value">{{ selectedCell.voyages.length }}</span>
        </div>
        <div class="detail-item">
          <span class="label">Utilization:</span>
          <span class="value">{{ selectedCell.utilization.toFixed(1) }}%</span>
        </div>
        <div class="voyages-list">
          <h5>Scheduled Voyages</h5>
          <div
            v-for="voyage in selectedCell.voyages"
            :key="voyage"
            class="voyage-item"
          >
            <span>{{ voyage }}</span>
            <button class="btn-edit" @click="handleEditVoyage(voyage)">
              Edit
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { ResourceAllocation } from '@/types/schedule.types';

interface Props {
  allocations: ResourceAllocation[];
  year: number;
}

interface Emits {
  (e: 'adjust', data: { vesselId: string; month: number; adjustments: any }): void;
  (e: 'edit-voyage', voyageId: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// State
const viewMode = ref<'month' | 'quarter'>('month');
const selectedCell = ref<{
  vesselId: string;
  vesselName: string;
  month: number;
  voyages: string[];
  utilization: number;
} | null>(null);

// Computed
const vesselAllocations = computed(() => {
  const vesselMap = new Map();
  
  props.allocations.forEach(allocation => {
    allocation.vessels.forEach(vessel => {
      if (!vesselMap.has(vessel.vesselId)) {
        vesselMap.set(vessel.vesselId, {
          vesselId: vessel.vesselId,
          vesselName: vessel.vesselName,
          utilizationRate: 0,
          totalVoyages: 0,
        });
      }
      const v = vesselMap.get(vessel.vesselId);
      v.utilizationRate += vessel.utilizationRate;
      v.totalVoyages += vessel.assignedVoyages.length;
    });
  });

  return Array.from(vesselMap.values()).map(v => ({
    ...v,
    utilizationRate: v.utilizationRate / 12, // Average across year
  }));
});

const displayMonths = computed(() => {
  if (viewMode.value === 'quarter') {
    return [
      { index: 1, name: 'Q1', width: '25%' },
      { index: 2, name: 'Q2', width: '25%' },
      { index: 3, name: 'Q3', width: '25%' },
      { index: 4, name: 'Q4', width: '25%' },
    ];
  }
  return Array.from({ length: 12 }, (_, i) => ({
    index: i + 1,
    name: getMonthShortName(i + 1),
    width: `${100 / 12}%`,
  }));
});

// Methods
function getVesselMonthlyData(vesselId: string) {
  const monthlyData = [];
  
  for (let month = 1; month <= 12; month++) {
    const allocation = props.allocations.find(a => a.month === month);
    const vessel = allocation?.vessels.find(v => v.vesselId === vesselId);
    
    monthlyData.push({
      month,
      voyages: vessel?.assignedVoyages.length || 0,
      utilization: vessel?.utilizationRate || 0,
      voyageIds: vessel?.assignedVoyages || [],
    });
  }
  
  return monthlyData;
}

function handleCellClick(vesselId: string, month: number) {
  const allocation = props.allocations.find(a => a.month === month);
  const vessel = allocation?.vessels.find(v => v.vesselId === vesselId);
  
  if (vessel && vessel.assignedVoyages.length > 0) {
    const vesselInfo = vesselAllocations.value.find(v => v.vesselId === vesselId);
    selectedCell.value = {
      vesselId,
      vesselName: vesselInfo?.vesselName || '',
      month,
      voyages: vessel.assignedVoyages,
      utilization: vessel.utilizationRate,
    };
  }
}

function handleEditVoyage(voyageId: string) {
  emit('edit-voyage', voyageId);
}

function getUtilizationClass(rate: number): string {
  if (rate >= 90) return 'high';
  if (rate >= 70) return 'medium';
  if (rate >= 50) return 'low';
  return 'very-low';
}

function getMonthName(month: number): string {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  return months[month - 1];
}

function getMonthShortName(month: number): string {
  return getMonthName(month).substring(0, 3);
}
</script>

<style scoped>
.resource-allocation-grid {
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.5rem;
  overflow: hidden;
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  background: var(--bg-secondary, #f9fafb);
}

.grid-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.view-controls {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color, #e5e7eb);
  background: white;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.view-btn:hover {
  background: var(--bg-secondary, #f9fafb);
}

.view-btn.active {
  background: var(--primary-color, #3b82f6);
  color: white;
  border-color: var(--primary-color, #3b82f6);
}

.grid-container {
  padding: 1rem;
}

.timeline-header {
  display: flex;
  margin-bottom: 0.5rem;
}

.vessel-col-header {
  width: 200px;
  flex-shrink: 0;
  font-weight: 600;
  padding: 0.5rem;
  color: var(--text-secondary, #6b7280);
  font-size: 0.875rem;
}

.months-row {
  flex: 1;
  display: flex;
}

.month-header {
  text-align: center;
  font-weight: 500;
  font-size: 0.75rem;
  color: var(--text-secondary, #6b7280);
  padding: 0.5rem 0.25rem;
  border-left: 1px solid var(--border-color, #e5e7eb);
}

.vessel-rows {
  max-height: 500px;
  overflow-y: auto;
}

.vessel-row {
  display: flex;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  min-height: 60px;
}

.vessel-row:hover {
  background: var(--bg-secondary, #f9fafb);
}

.vessel-info {
  width: 200px;
  flex-shrink: 0;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.vessel-name {
  font-weight: 500;
  font-size: 0.875rem;
}

.utilization-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  width: fit-content;
}

.utilization-badge.high {
  background: #dcfce7;
  color: #166534;
}

.utilization-badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.utilization-badge.low {
  background: #fee2e2;
  color: #991b1b;
}

.utilization-badge.very-low {
  background: #f3f4f6;
  color: #6b7280;
}

.timeline-track {
  flex: 1;
  display: flex;
  align-items: stretch;
}

.month-cell {
  flex: 1;
  border-left: 1px solid var(--border-color, #e5e7eb);
  position: relative;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: flex-end;
  padding: 0.25rem;
}

.month-cell:hover {
  background: rgba(59, 130, 246, 0.05);
}

.month-cell.has-voyages {
  background: rgba(59, 130, 246, 0.02);
}

.allocation-bar {
  width: 100%;
  background: linear-gradient(to top, var(--primary-color, #3b82f6), rgba(59, 130, 246, 0.7));
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 20px;
  position: relative;
  transition: all 0.2s;
}

.month-cell:hover .allocation-bar {
  background: var(--primary-color, #3b82f6);
}

.voyage-count {
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.empty-grid {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-secondary, #6b7280);
}

.empty-grid i {
  font-size: 3rem;
  opacity: 0.3;
  margin-bottom: 1rem;
}

.details-panel {
  border-top: 1px solid var(--border-color, #e5e7eb);
  background: var(--bg-secondary, #f9fafb);
  padding: 1rem;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.details-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary, #6b7280);
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: var(--text-primary, #111827);
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  background: white;
  border-radius: 0.375rem;
}

.detail-item .label {
  font-weight: 500;
  color: var(--text-secondary, #6b7280);
}

.detail-item .value {
  font-weight: 600;
}

.voyages-list h5 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.voyage-item {
  background: white;
  padding: 0.75rem;
  border-radius: 0.375rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.btn-edit {
  padding: 0.25rem 0.75rem;
  background: var(--primary-color, #3b82f6);
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
  transition: background 0.2s;
}

.btn-edit:hover {
  background: var(--primary-hover, #2563eb);
}
</style>
