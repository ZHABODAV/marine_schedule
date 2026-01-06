<template>
  <BaseModal
    :show="true"
    title="Voyage Details"
    size="large"
    @close="$emit('close')"
  >
    <div class="event-modal-content">
      <!-- Header Section -->
      <div class="event-header">
        <div class="event-title-section">
          <h2 class="event-title">{{ event.title }}</h2>
          <StatusBadge :status="event.status" />
        </div>
        <div class="event-module-badge" :class="`module-${event.module}`">
          {{ moduleLabel }}
        </div>
      </div>

      <!-- Key Information Grid -->
      <div class="info-grid">
        <div class="info-item">
          <div class="info-label"> Vessel</div>
          <div class="info-value">{{ event.vessel }}</div>
        </div>

        <div class="info-item">
          <div class="info-label"> Route</div>
          <div class="info-value">{{ event.route || 'N/A' }}</div>
        </div>

        <div class="info-item">
          <div class="info-label"> Start Date</div>
          <div class="info-value">{{ formatDateTime(event.start) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label"> End Date</div>
          <div class="info-value">{{ formatDateTime(event.end) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">⏱ Duration</div>
          <div class="info-value">{{ calculateDuration() }} days</div>
        </div>

        <div class="info-item">
          <div class="info-label"> Cargo</div>
          <div class="info-value">{{ formatNumber(event.cargo || 0) }} MT</div>
        </div>

        <div class="info-item">
          <div class="info-label"> Cost</div>
          <div class="info-value">${{ formatNumber(event.cost || 0) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label"> Module</div>
          <div class="info-value">{{ moduleLabel }}</div>
        </div>
      </div>

      <!-- Additional Details -->
      <div v-if="hasAdditionalDetails" class="additional-details">
        <h3 class="section-title">Additional Details</h3>
        <div class="details-grid">
          <div
            v-for="(value, key) in filteredDetails"
            :key="key"
            class="detail-item"
          >
            <span class="detail-label">{{ formatKey(key) }}:</span>
            <span class="detail-value">{{ formatValue(value) }}</span>
          </div>
        </div>
      </div>

      <!-- Timeline Visualization -->
      <div class="timeline-visualization">
        <h3 class="section-title">Timeline</h3>
        <div class="timeline-bar-container">
          <div class="timeline-bar-wrapper">
            <div
              :class="['timeline-bar', `module-${event.module}`, `status-${event.status}`]"
            >
              <span class="timeline-start">{{ formatDate(event.start) }}</span>
              <span class="timeline-duration">{{ calculateDuration() }} days</span>
              <span class="timeline-end">{{ formatDate(event.end) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="modal-actions">
        <BaseButton variant="secondary" @click="exportEventDetails">
           Export Details
        </BaseButton>
        <BaseButton variant="primary" @click="$emit('close')">
          Close
        </BaseButton>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { CalendarEvent } from '@/types/calendar.types';
import BaseModal from '@/components/shared/BaseModal.vue';
import BaseButton from '@/components/shared/BaseButton.vue';
import StatusBadge from '@/components/shared/StatusBadge.vue';

interface Props {
  event: CalendarEvent;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
}>();

const moduleLabel = computed(() => {
  const labels: Record<string, string> = {
    deepsea: 'Deep Sea',
    olya: 'Olya',
    balakovo: 'Balakovo'
  };
  return labels[props.event.module] || props.event.module;
});

const hasAdditionalDetails = computed(() => {
  return props.event.details && Object.keys(props.event.details).length > 0;
});

const filteredDetails = computed(() => {
  if (!props.event.details) return {};
  
  // Filter out common fields already displayed
  const excludeKeys = [
    'id', 'voyage_id', 'vessel_id', 'vessel_name',
    'start_date', 'end_date', 'laycan_start', 'laycan_end',
    'qty_mt', 'total_cost_usd', 'cargo_type', 'cargo_name'
  ];
  
  const filtered: Record<string, any> = {};
  Object.entries(props.event.details).forEach(([key, value]) => {
    if (!excludeKeys.includes(key) && value != null && value !== '') {
      filtered[key] = value;
    }
  });
  
  return filtered;
});

function formatDateTime(date: Date): string {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function formatDate(date: Date): string {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 2
  }).format(value);
}

function calculateDuration(): number {
  const start = new Date(props.event.start);
  const end = new Date(props.event.end);
  const diffTime = Math.abs(end.getTime() - start.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}

function formatKey(key: string): string {
  // Convert snake_case to Title Case
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function formatValue(value: any): string {
  if (typeof value === 'number') {
    return formatNumber(value);
  }
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }
  if (value instanceof Date) {
    return formatDateTime(value);
  }
  return String(value);
}

function exportEventDetails() {
  const details = {
    'Voyage ID': props.event.id,
    'Title': props.event.title,
    'Vessel': props.event.vessel,
    'Module': moduleLabel.value,
    'Route': props.event.route || 'N/A',
    'Status': props.event.status,
    'Start Date': formatDateTime(props.event.start),
    'End Date': formatDateTime(props.event.end),
    'Duration': `${calculateDuration()} days`,
    'Cargo (MT)': props.event.cargo || 0,
    'Cost (USD)': props.event.cost || 0,
    ...filteredDetails.value
  };

  const content = Object.entries(details)
    .map(([key, value]) => `${key}: ${value}`)
    .join('\n');

  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `voyage-${props.event.id}-details.txt`;
  a.click();
  URL.revokeObjectURL(url);
}
</script>

<style scoped>
.event-modal-content {
  padding: 1.5rem;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--color-border);
}

.event-title-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.event-title {
  margin: 0;
  font-size: 1.5rem;
  color: var(--color-heading);
}

.event-module-badge {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.event-module-badge.module-deepsea {
  background: #e3f2fd;
  color: #1976d2;
}

.event-module-badge.module-olya {
  background: #f3e5f5;
  color: #7b1fa2;
}

.event-module-badge.module-balakovo {
  background: #e8f5e9;
  color: #388e3c;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
}

.section-title {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-heading);
}

.additional-details {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--color-background-soft);
  border-radius: 8px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  padding: 0.5rem;
  background: var(--color-background);
  border-radius: 4px;
}

.detail-label {
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 140px;
}

.detail-value {
  color: var(--color-text);
  flex: 1;
}

.timeline-visualization {
  margin-bottom: 2rem;
}

.timeline-bar-container {
  padding: 1.5rem;
  background: var(--color-background-soft);
  border-radius: 8px;
}

.timeline-bar-wrapper {
  position: relative;
  height: 80px;
  display: flex;
  align-items: center;
}

.timeline-bar {
  width: 100%;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  font-weight: 600;
  font-size: 0.875rem;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.timeline-bar.module-deepsea {
  background: linear-gradient(135deg, #e3f2fd 0%, #90caf9 100%);
  color: #1976d2;
}

.timeline-bar.module-olya {
  background: linear-gradient(135deg, #f3e5f5 0%, #ce93d8 100%);
  color: #7b1fa2;
}

.timeline-bar.module-balakovo {
  background: linear-gradient(135deg, #e8f5e9 0%, #a5d6a7 100%);
  color: #388e3c;
}

.timeline-duration {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 1rem;
  font-weight: 700;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

@media (max-width: 768px) {
  .event-modal-content {
    padding: 1rem;
  }

  .event-header {
    flex-direction: column;
    gap: 1rem;
  }

  .event-title {
    font-size: 1.25rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .timeline-bar {
    font-size: 0.75rem;
    padding: 0 0.5rem;
  }

  .timeline-start,
  .timeline-end {
    display: none;
  }
}
</style>
