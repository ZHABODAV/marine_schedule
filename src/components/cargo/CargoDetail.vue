<template>
  <div class="cargo-detail">
    <LoadingSpinner v-if="loading" />

    <div v-else-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <BaseButton @click="$emit('retry')" variant="primary">Retry</BaseButton>
    </div>

    <div v-else-if="cargo" class="detail-container">
      <div class="detail-header">
        <div class="header-content">
          <h2 class="cargo-title">{{ cargo.commodity }}</h2>
          <span :class="['status-badge', `status-${cargo.status.toLowerCase()}`]">
            {{ cargo.status }}
          </span>
        </div>
        <div class="header-actions">
          <BaseButton @click="$emit('edit', cargo)" variant="secondary">
            Edit
          </BaseButton>
          <BaseButton @click="handleDelete" variant="danger">
            Delete
          </BaseButton>
        </div>
      </div>

      <div class="detail-grid">
        <div class="detail-card">
          <h3 class="card-title">Basic Information</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Cargo ID</span>
              <span class="info-value">{{ cargo.id }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Commodity</span>
              <span class="info-value">{{ cargo.commodity }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Quantity</span>
              <span class="info-value">{{ formatNumber(cargo.quantity) }} MT</span>
            </div>
            <div class="info-item">
              <span class="info-label">Status</span>
              <span :class="['status-badge', `status-${cargo.status.toLowerCase()}`]">
                {{ cargo.status }}
              </span>
            </div>
          </div>
        </div>

        <div class="detail-card">
          <h3 class="card-title">Route Information</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Load Port</span>
              <span class="info-value">{{ cargo.loadPort }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Discharge Port</span>
              <span class="info-value">{{ cargo.dischPort }}</span>
            </div>
          </div>
          <div class="route-visual">
            <span class="port-label">{{ cargo.loadPort }}</span>
            <span class="route-arrow">→</span>
            <span class="port-label">{{ cargo.dischPort }}</span>
          </div>
        </div>

        <div class="detail-card full-width">
          <h3 class="card-title">Laycan</h3>
          <div class="laycan-info">
            <div class="laycan-item">
              <span class="laycan-label">Start</span>
              <span class="laycan-date">{{ formatDate(cargo.laycanStart) }}</span>
            </div>
            <div class="laycan-separator">-</div>
            <div class="laycan-item">
              <span class="laycan-label">End</span>
              <span class="laycan-date">{{ formatDate(cargo.laycanEnd) }}</span>
            </div>
            <div class="laycan-duration">
              <span class="duration-label">Duration:</span>
              <span class="duration-value">{{ calculateLaycanDays(cargo) }} days</span>
            </div>
          </div>
        </div>

        <div class="detail-card" v-if="cargo.freightRate">
          <h3 class="card-title">Financial</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Freight Rate</span>
              <span class="info-value">${{ cargo.freightRate.toFixed(2) }}/MT</span>
            </div>
            <div class="info-item">
              <span class="info-label">Total Freight</span>
              <span class="info-value">
                ${{ formatNumber((cargo.freightRate * cargo.quantity).toFixed(0)) }}
              </span>
            </div>
          </div>
        </div>

        <div class="detail-card full-width" v-if="cargo.notes">
          <h3 class="card-title">Notes</h3>
          <p class="notes-content">{{ cargo.notes }}</p>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>No cargo data available</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CargoCommitment } from '@/types/cargo.types';
import BaseButton from '@/components/shared/BaseButton.vue';
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue';

interface Props {
  cargo: CargoCommitment | null;
  loading?: boolean;
  error?: string | null;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: null,
});

const emit = defineEmits<{
  edit: [cargo: CargoCommitment];
  delete: [cargo: CargoCommitment];
  retry: [];
}>();

function formatNumber(value: number | string): string {
  return Number(value).toLocaleString();
}

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function calculateLaycanDays(cargo: CargoCommitment): number {
  const start = new Date(cargo.laycanStart);
  const end = new Date(cargo.laycanEnd);
  const diff = end.getTime() - start.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

function handleDelete() {
  if (!props.cargo) return;
  if (confirm(`Delete cargo commitment ${props.cargo.id}? This action cannot be undone.`)) {
    emit('delete', props.cargo);
  }
}
</script>

<style scoped>
.cargo-detail {
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

.cargo-title {
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

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-assigned {
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

.route-visual {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem;
  background: var(--bg-tertiary, #f9fafb);
  border-radius: 6px;
}

.port-label {
  font-weight: 600;
  color: var(--primary-color, #2563eb);
}

.route-arrow {
  font-size: 1.5rem;
  color: var(--text-muted, #9ca3af);
}

.laycan-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem;
  background: var(--bg-tertiary, #f9fafb);
  border-radius: 6px;
}

.laycan-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.laycan-label {
  font-size: 0.875rem;
  color: var(--text-muted, #6b7280);
  font-weight: 500;
}

.laycan-date {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
}

.laycan-separator {
  font-size: 1.25rem;
  color: var(--text-muted, #9ca3af);
}

.laycan-duration {
  margin-left: auto;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.duration-label {
  font-size: 0.875rem;
  color: var(--text-muted, #6b7280);
}

.duration-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color, #2563eb);
}

.notes-content {
  color: var(--text-secondary, #4b5563);
  line-height: 1.6;
  margin: 0;
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

  .laycan-info {
    flex-direction: column;
    align-items: flex-start;
  }

  .laycan-duration {
    margin-left: 0;
    align-items: flex-start;
  }
}
</style>
