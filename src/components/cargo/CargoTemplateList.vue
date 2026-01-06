<template>
  <div class="cargo-template-list">
    <div class="list-header">
      <h2 class="list-title">Cargo Templates</h2>
      <BaseButton
        variant="primary"
        @click="$emit('create')"
      >
        + New Template
      </BaseButton>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Loading templates..." />

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p class="error-message"> {{ error }}</p>
      <BaseButton variant="primary" @click="$emit('retry')">
        Retry
      </BaseButton>
    </div>

    <!-- Empty State -->
    <div v-else-if="templates.length === 0" class="empty-state">
      <div class="empty-icon"></div>
      <h3>No Templates Yet</h3>
      <p>Create your first cargo template to streamline cargo creation with predefined cost structures.</p>
      <BaseButton variant="primary" @click="$emit('create')">
        Create First Template
      </BaseButton>
    </div>

    <!-- Template Grid -->
    <div v-else class="template-grid">
      <div
        v-for="template in templates"
        :key="template.id"
        class="template-card"
        :class="{ 'is-default': template.isDefault }"
      >
        <div class="card-header">
          <div class="template-info">
            <h3 class="template-name">{{ template.name }}</h3>
            <span v-if="template.isDefault" class="default-badge">Default</span>
          </div>
          <div class="card-actions">
            <button
              class="icon-button"
              title="Edit template"
              @click="$emit('edit', template)"
            >
              
            </button>
            <button
              class="icon-button delete-button"
              title="Delete template"
              @click="$emit('delete', template)"
            >
              
            </button>
          </div>
        </div>

        <p v-if="template.description" class="template-description">
          {{ template.description }}
        </p>

        <div class="template-details">
          <div class="detail-item">
            <span class="detail-label">Commodity:</span>
            <span class="detail-value">{{ template.commodity }}</span>
          </div>

          <div v-if="template.quantity" class="detail-item">
            <span class="detail-label">Quantity:</span>
            <span class="detail-value">{{ formatNumber(template.quantity) }} MT</span>
          </div>

          <div v-if="template.freightRate" class="detail-item">
            <span class="detail-label">Freight Rate:</span>
            <span class="detail-value">${{ formatNumber(template.freightRate) }}/MT</span>
          </div>

          <div v-if="template.loadPort || template.dischPort" class="detail-item">
            <span class="detail-label">Route:</span>
            <span class="detail-value">
              {{ template.loadPort || 'Any' }} → {{ template.dischPort || 'Any' }}
            </span>
          </div>

          <div v-if="hasCostAllocation(template)" class="detail-item">
            <span class="detail-label">Total Cost:</span>
            <span class="detail-value cost-highlight">
              ${{ formatNumber(getTotalCost(template)) }}
            </span>
          </div>
        </div>

        <div class="card-footer">
          <BaseButton
            variant="secondary"
            size="small"
            @click="$emit('apply', template)"
          >
            Apply Template
          </BaseButton>
          <span class="card-meta">
            Created: {{ formatDate(template.createdAt) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { CargoTemplate } from '@/types/cargo.types';
import BaseButton from '@/components/shared/BaseButton.vue';
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue';

// Props
interface Props {
  templates: CargoTemplate[];
  loading?: boolean;
  error?: string | null;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: null,
});

// Emits
defineEmits<{
  create: [];
  edit: [template: CargoTemplate];
  delete: [template: CargoTemplate];
  apply: [template: CargoTemplate];
  retry: [];
}>();

// Methods
function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 2,
  }).format(value);
}

function formatDate(date: string | Date | undefined): string {
  if (!date) return 'N/A';
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function hasCostAllocation(template: CargoTemplate): boolean {
  return !!(template.operationalCost || template.overheadCost || template.otherCost);
}

function getTotalCost(template: CargoTemplate): number {
  return (template.operationalCost || 0) + 
         (template.overheadCost || 0) + 
         (template.otherCost || 0);
}
</script>

<style scoped>
.cargo-template-list {
  padding: 1.5rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.list-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary, #1f2937);
}

.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.error-message {
  color: var(--danger-color, #dc2626);
  font-size: 1.125rem;
  margin-bottom: 1rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.4;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  color: var(--text-primary, #1f2937);
}

.empty-state p {
  margin: 0 0 1.5rem 0;
  font-size: 1rem;
  color: var(--text-secondary, #6b7280);
  max-width: 500px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.template-card {
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.2s ease;
  position: relative;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.template-card.is-default {
  border-color: var(--primary-color, #2563eb);
  border-width: 2px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.template-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.template-name {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
}

.default-badge {
  padding: 0.25rem 0.75rem;
  background: var(--primary-color, #2563eb);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.icon-button {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.icon-button:hover {
  background: var(--bg-secondary, #f9fafb);
  transform: scale(1.05);
}

.delete-button:hover {
  background: var(--danger-color, #dc2626);
  border-color: var(--danger-color, #dc2626);
  color: white;
}

.template-description {
  margin: 0 0 1rem 0;
  color: var(--text-secondary, #6b7280);
  font-size: 0.95rem;
  line-height: 1.5;
}

.template-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--bg-secondary, #f9fafb);
  border-radius: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
}

.detail-label {
  font-weight: 500;
  color: var(--text-secondary, #6b7280);
}

.detail-value {
  font-weight: 600;
  color: var(--text-primary, #1f2937);
}

.cost-highlight {
  color: var(--success-color, #059669);
  font-size: 1.05rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color, #e5e7eb);
}

.card-meta {
  font-size: 0.85rem;
  color: var(--text-secondary, #6b7280);
}

@media (max-width: 1024px) {
  .template-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .cargo-template-list {
    padding: 1rem;
  }

  .list-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .template-grid {
    grid-template-columns: 1fr;
  }

  .card-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .card-meta {
    text-align: center;
  }
}
</style>
