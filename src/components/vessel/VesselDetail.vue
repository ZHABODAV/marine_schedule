<template>
  <div class="vessel-detail">
    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <BaseButton @click="$emit('retry')" variant="primary">
        Retry
      </BaseButton>
    </div>

    <!-- Vessel Details -->
    <div v-else-if="vessel" class="detail-container">
      <!-- Header -->
      <div class="detail-header">
        <div class="header-content">
          <h2 class="vessel-name">{{ vessel.name }}</h2>
          <span :class="['status-badge', `status-${vessel.status.toLowerCase()}`]">
            {{ vessel.status }}
          </span>
        </div>
        <div class="header-actions">
          <BaseButton
            @click="$emit('edit', vessel)"
            variant="secondary"
          >
            Edit
          </BaseButton>
          <BaseButton
            @click="handleDelete"
            variant="danger"
          >
            Delete
          </BaseButton>
        </div>
      </div>

      <!-- Main Info -->
      <div class="detail-grid">
        <div class="detail-card">
          <h3 class="card-title">Basic Information</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Vessel ID</span>
              <span class="info-value">{{ vessel.id }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Type</span>
              <span class="info-value">{{ formatVesselType(vessel.type) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Class</span>
              <span class="info-value">{{ vessel.class }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Status</span>
              <span :class="['status-badge', `status-${vessel.status.toLowerCase()}`]">
                {{ vessel.status }}
              </span>
            </div>
          </div>
        </div>

        <div class="detail-card">
          <h3 class="card-title">Technical Specifications</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">DWT</span>
              <span class="info-value">{{ formatNumber(vessel.dwt) }} tons</span>
            </div>
            <div class="info-item">
              <span class="info-label">Speed</span>
              <span class="info-value">{{ vessel.speed }} knots</span>
            </div>
            <div class="info-item" v-if="vessel.draft">
              <span class="info-label">Draft</span>
              <span class="info-value">{{ vessel.draft }} m</span>
            </div>
            <div class="info-item" v-if="vessel.loa">
              <span class="info-label">LOA</span>
              <span class="info-value">{{ vessel.loa }} m</span>
            </div>
            <div class="info-item" v-if="vessel.fuelConsumption">
              <span class="info-label">Fuel Consumption</span>
              <span class="info-value">{{ vessel.fuelConsumption }} tons/day</span>
            </div>
          </div>
        </div>

        <!-- Notes -->
        <div v-if="vessel.notes" class="detail-card full-width">
          <h3 class="card-title">Notes</h3>
          <p class="notes-content">{{ vessel.notes }}</p>
        </div>

        <!-- Schedule Section -->
        <div class="detail-card full-width">
          <div class="card-header-with-action">
            <h3 class="card-title">Schedule</h3>
            <BaseButton
              @click="loadSchedule"
              variant="secondary"
              size="small"
              :disabled="loadingSchedule"
            >
              {{ loadingSchedule ? 'Loading...' : 'Refresh' }}
            </BaseButton>
          </div>

          <div v-if="loadingSchedule" class="schedule-loading">
            <LoadingSpinner />
          </div>

          <div v-else-if="schedule && schedule.length > 0" class="schedule-list">
            <div
              v-for="scheduleItem in schedule"
              :key="scheduleItem.id"
              class="schedule-item"
            >
              <div class="schedule-info">
                <strong>{{ scheduleItem.voyageId }}</strong>
                <span class="schedule-route">
                  {{ scheduleItem.from || scheduleItem.loadPort }} → 
                  {{ scheduleItem.to || scheduleItem.dischPort }}
                </span>
              </div>
              <div class="schedule-dates">
                <span class="schedule-date">
                  {{ formatDate(scheduleItem.startDate || scheduleItem.etd) }}
                </span>
                <span class="schedule-separator">-</span>
                <span class="schedule-date">
                  {{ formatDate(scheduleItem.endDate || scheduleItem.eta) }}
                </span>
              </div>
            </div>
          </div>

          <div v-else class="empty-schedule">
            <p>No scheduled voyages</p>
          </div>
        </div>

        <!-- Statistics -->
        <div class="detail-card full-width">
          <h3 class="card-title">Statistics</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ statistics.totalVoyages || 0 }}</span>
              <span class="stat-label">Total Voyages</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ formatNumber(statistics.totalDistance || 0) }}</span>
              <span class="stat-label">Total Distance (nm)</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ statistics.utilizationRate || 0 }}%</span>
              <span class="stat-label">Utilization Rate</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ formatNumber(statistics.cargoMoved || 0) }}</span>
              <span class="stat-label">Cargo Moved (tons)</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>No vessel data available</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Vessel } from '@/types/vessel.types';
import BaseButton from '@/components/shared/BaseButton.vue';
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue';

// Props
interface Props {
  vessel: Vessel | null;
  loading?: boolean;
  error?: string | null;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: null,
});

// Emits
const emit = defineEmits<{
  edit: [vessel: Vessel];
  delete: [vessel: Vessel];
  retry: [];
  'load-schedule': [vesselId: string | number];
}>();

// State
const schedule = ref<any[]>([]);
const loadingSchedule = ref(false);
const statistics = ref({
  totalVoyages: 0,
  totalDistance: 0,
  utilizationRate: 0,
  cargoMoved: 0,
});

// Lifecycle
onMounted(() => {
  if (props.vessel) {
    loadSchedule();
    loadStatistics();
  }
});

// Methods
function formatNumber(value: number): string {
  return value.toLocaleString();
}

function formatVesselType(type: string): string {
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function formatDate(date: string | undefined): string {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

async function loadSchedule() {
  if (!props.vessel) return;
  
  loadingSchedule.value = true;
  emit('load-schedule', props.vessel.id);
  
  // This would be populated by the parent component
  // For now, we'll simulate after a delay
  setTimeout(() => {
    loadingSchedule.value = false;
  }, 500);
}

function loadStatistics() {
  // This would normally fetch from API or parent component
  // For now, using mock data
  statistics.value = {
    totalVoyages: 12,
    totalDistance: 45_320,
    utilizationRate: 87,
    cargoMoved: 156_800,
  };
}

function handleDelete() {
  if (!props.vessel) return;
  
  if (confirm(`Delete vessel ${props.vessel.name}? This action cannot be undone.`)) {
    emit('delete', props.vessel);
  }
}
</script>

<style scoped>
.vessel-detail {
  padding: 1.5rem;
}

.error-state {
  text-align: center;
  padding: 3rem;
}

.error-message {
  color: var(--danger-color, #dc2626);
  margin-bottom: 1rem;
}

.detail-container {
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid var(--border-color, #e5e7eb);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.vessel-name {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary, #1f2937);
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.status-badge {
  display: inline-block;
  padding: 0.35rem 0.85rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-active {
  background: #d1fae5;
  color: #065f46;
}

.status-inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-maintenance {
  background: #fef3c7;
  color: #92400e;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.detail-card {
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  padding: 1.5rem;
}

.detail-card.full-width {
  grid-column: 1 / -1;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: var(--text-primary, #1f2937);
}

.card-header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.875rem;
  color: var(--text-muted, #6b7280);
  font-weight: 500;
}

.info-value {
  font-size: 1rem;
  color: var(--text-primary, #1f2937);
}

.notes-content {
  color: var(--text-secondary, #4b5563);
  line-height: 1.6;
  margin: 0;
}

.schedule-loading {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.schedule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--bg-tertiary, #f9fafb);
  border-radius: 6px;
  border-left: 3px solid var(--primary-color, #2563eb);
}

.schedule-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.schedule-route {
  font-size: 0.875rem;
  color: var(--text-muted, #6b7280);
}

.schedule-dates {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary, #4b5563);
  font-size: 0.875rem;
}

.schedule-separator {
  color: var(--text-muted, #9ca3af);
}

.empty-schedule {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted, #6b7280);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: var(--bg-tertiary, #f9fafb);
  border-radius: 6px;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary-color, #2563eb);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted, #6b7280);
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted, #6b7280);
}

@media (max-width: 1024px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .schedule-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>
