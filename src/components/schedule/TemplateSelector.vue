<template>
  <div class="template-selector">
    <div class="selector-header">
      <h4>Voyage Templates</h4>
      <button
        v-if="templates.length === 0"
        class="btn-load"
        @click="handleLoadTemplates"
      >
        <i class="icon-download"></i>
        Load Templates
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading templates...</p>
    </div>

    <div v-else-if="templates.length === 0" class="empty-state">
      <i class="icon-file-text"></i>
      <p>No templates available</p>
      <small>Click "Load Templates" to fetch available voyage patterns</small>
    </div>

    <div v-else class="templates-list">
      <!-- Select All / None -->
      <div class="bulk-actions">
        <button class="link-btn" @click="selectAll">Select All</button>
        <span class="separator">|</span>
        <button class="link-btn" @click="selectNone">Select None</button>
        <span class="selected-count">{{ selectedCount }} selected</span>
      </div>

      <!-- Templates -->
      <div class="templates-grid">
        <label
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
          :class="{ selected: isSelected(template.id) }"
        >
          <input
            type="checkbox"
            :value="template.id"
            :checked="isSelected(template.id)"
            @change="toggleTemplate(template.id)"
          />
          <div class="template-content">
            <div class="template-header">
              <span class="template-name">{{ template.name }}</span>
              <span class="pattern-badge">{{ formatPattern(template.pattern) }}</span>
            </div>
            <p v-if="template.description" class="template-description">
              {{ template.description }}
            </p>
            <div class="template-meta">
              <span class="meta-item">
                <i class="icon-clock"></i>
                {{ template.estimatedDays }} days
              </span>
              <span class="meta-item">
                <i class="icon-anchor"></i>
                {{ template.ports.length }} ports
              </span>
              <span v-if="template.cargoTypes.length > 0" class="meta-item">
                <i class="icon-box"></i>
                {{ template.cargoTypes.length }} cargo types
              </span>
            </div>
            <div class="ports-preview">
              <small>Ports: {{ template.ports.join(' → ') }}</small>
            </div>
          </div>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { ScheduleTemplate } from '@/types/schedule.types';

interface Props {
  templates: ScheduleTemplate[];
  module: string;
  selected?: string[];
}

interface Emits {
  (e: 'update:selected', templateIds: string[]): void;
  (e: 'load-templates'): void;
}

const props = withDefaults(defineProps<Props>(), {
  selected: () => [],
});

const emit = defineEmits<Emits>();

// State
const loading = ref(false);
const localSelected = ref<string[]>([...props.selected]);

// Computed
const filteredTemplates = computed(() => {
  return props.templates.filter(t => t.module === props.module);
});

const selectedCount = computed(() => localSelected.value.length);

// Methods
function isSelected(templateId: string): boolean {
  return localSelected.value.includes(templateId);
}

function toggleTemplate(templateId: string) {
  const index = localSelected.value.indexOf(templateId);
  if (index > -1) {
    localSelected.value.splice(index, 1);
  } else {
    localSelected.value.push(templateId);
  }
  emit('update:selected', [...localSelected.value]);
}

function selectAll() {
  localSelected.value = filteredTemplates.value.map(t => t.id);
  emit('update:selected', [...localSelected.value]);
}

function selectNone() {
  localSelected.value = [];
  emit('update:selected', []);
}

function handleLoadTemplates() {
  loading.value = true;
  emit('load-templates');
  // Loading state will be managed by parent
  setTimeout(() => {
    loading.value = false;
  }, 1000);
}

function formatPattern(pattern: string): string {
  return pattern
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
</script>

<style scoped>
.template-selector {
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 1rem;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.selector-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.btn-load {
  padding: 0.5rem 0.75rem;
  background: var(--primary-color, #3b82f6);
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  transition: background 0.2s;
}

.btn-load:hover {
  background: var(--primary-hover, #2563eb);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--text-secondary, #6b7280);
}

.loading-state .spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--border-color, #e5e7eb);
  border-top-color: var(--primary-color, #3b82f6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state i {
  font-size: 2.5rem;
  opacity: 0.3;
  margin-bottom: 0.75rem;
}

.empty-state small {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.75rem;
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--bg-secondary, #f9fafb);
  border-radius: 0.375rem;
}

.link-btn {
  background: none;
  border: none;
  color: var(--primary-color, #3b82f6);
  font-weight: 500;
  cursor: pointer;
  padding: 0;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.link-btn:hover {
  color: var(--primary-hover, #2563eb);
  text-decoration: underline;
}

.separator {
  color: var(--border-color, #e5e7eb);
}

.selected-count {
  margin-left: auto;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary, #6b7280);
}

.templates-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 400px;
  overflow-y: auto;
}

.template-card {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px solid var(--border-color, #e5e7eb);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  border-color: var(--primary-color, #3b82f6);
  background: rgba(59, 130, 246, 0.02);
}

.template-card.selected {
  border-color: var(--primary-color, #3b82f6);
  background: rgba(59, 130, 246, 0.05);
}

.template-card input[type="checkbox"] {
  flex-shrink: 0;
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
  margin-top: 0.125rem;
}

.template-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.template-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-primary, #111827);
}

.pattern-badge {
  padding: 0.25rem 0.5rem;
  background: var(--primary-color, #3b82f6);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  flex-shrink: 0;
}

.template-description {
  margin: 0;
  font-size: 0.75rem;
  color: var(--text-secondary, #6b7280);
  line-height: 1.4;
}

.template-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-secondary, #6b7280);
}

.meta-item i {
  font-size: 0.875rem;
}

.ports-preview {
  padding: 0.5rem;
  background: var(--bg-secondary, #f9fafb);
  border-radius: 0.25rem;
}

.ports-preview small {
  font-size: 0.75rem;
  color: var(--text-secondary, #6b7280);
  word-break: break-word;
}
</style>
