<template>
  <div class="conflict-detector">
    <div class="detector-header">
      <h3>
        <i class="icon-alert-triangle"></i>
        Conflicts & Issues
      </h3>
      <div class="conflict-summary">
        <span v-if="conflicts.length === 0" class="no-conflicts">
          <i class="icon-check-circle"></i>
          No conflicts detected
        </span>
        <template v-else>
          <span class="conflict-badge critical">{{ criticalCount }} Critical</span>
          <span class="conflict-badge high">{{ highCount }} High</span>
          <span class="conflict-badge medium">{{ mediumCount }} Medium</span>
          <span class="conflict-badge low">{{ lowCount }} Low</span>
        </template>
      </div>
    </div>

    <div v-if="conflicts.length > 0" class="conflicts-container">
      <!-- Filter Controls -->
      <div class="filter-bar">
        <select v-model="filterSeverity" class="filter-select">
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select v-model="filterType" class="filter-select">
          <option value="">All Types</option>
          <option value="vessel-overlap">Vessel Overlap</option>
          <option value="port-capacity">Port Capacity</option>
          <option value="cargo-timing">Cargo Timing</option>
          <option value="resource-shortage">Resource Shortage</option>
        </select>
      </div>

      <!-- Conflicts List -->
      <div class="conflicts-list">
        <div
          v-for="conflict in filteredConflicts"
          :key="conflict.id"
          :class="['conflict-card', `severity-${conflict.severity}`]"
        >
          <div class="conflict-header">
            <div class="conflict-title">
              <i :class="getConflictIcon(conflict.type)"></i>
              <span class="conflict-type">{{ formatType(conflict.type) }}</span>
              <span :class="['severity-tag', conflict.severity]">
                {{ conflict.severity.toUpperCase() }}
              </span>
            </div>
            <button
              v-if="!conflict.resolved"
              class="resolve-btn"
              @click="handleResolve(conflict)"
            >
              Resolve
            </button>
          </div>

          <p class="conflict-description">{{ conflict.description }}</p>

          <div class="affected-entities">
            <span class="label">Affected:</span>
            <div class="entities-list">
              <span
                v-for="entity in conflict.affectedEntities"
                :key="entity"
                class="entity-tag"
              >
                {{ entity }}
              </span>
            </div>
          </div>

          <div v-if="conflict.suggestedResolution" class="suggested-resolution">
            <i class="icon-lightbulb"></i>
            <span>{{ conflict.suggestedResolution }}</span>
          </div>

          <!-- Resolution Options -->
          <div v-if="resolvingConflict === conflict.id" class="resolution-panel">
            <h5>Resolution Options</h5>
            <div class="resolution-options">
              <button
                class="resolution-option"
                @click="applyResolution(conflict.id, 'auto')"
              >
                <i class="icon-wand"></i>
                Auto-resolve
              </button>
              <button
                class="resolution-option"
                @click="applyResolution(conflict.id, 'manual')"
              >
                <i class="icon-edit"></i>
                Manual adjustment
              </button>
              <button
                class="resolution-option"
                @click="applyResolution(conflict.id, 'ignore')"
              >
                <i class="icon-eye-off"></i>
                Ignore
              </button>
            </div>
            <button class="cancel-btn" @click="resolvingConflict = null">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-conflicts-state">
      <i class="icon-check-circle"></i>
      <h4>All Clear!</h4>
      <p>No scheduling conflicts detected. Your schedule is optimized.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { ScheduleConflict } from '@/types/schedule.types';

interface Props {
  conflicts: ScheduleConflict[];
  scheduleId: string;
}

interface Emits {
  (e: 'resolve', conflictId: string, resolution: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// State
const filterSeverity = ref<string>('');
const filterType = ref<string>('');
const resolvingConflict = ref<string | null>(null);

// Computed
const filteredConflicts = computed(() => {
  return props.conflicts.filter(conflict => {
    if (filterSeverity.value && conflict.severity !== filterSeverity.value) {
      return false;
    }
    if (filterType.value && conflict.type !== filterType.value) {
      return false;
    }
    return true;
  });
});

const criticalCount = computed(() => 
  props.conflicts.filter(c => c.severity === 'critical').length
);

const highCount = computed(() => 
  props.conflicts.filter(c => c.severity === 'high').length
);

const mediumCount = computed(() => 
  props.conflicts.filter(c => c.severity === 'medium').length
);

const lowCount = computed(() => 
  props.conflicts.filter(c => c.severity === 'low').length
);

// Methods
function handleResolve(conflict: ScheduleConflict) {
  resolvingConflict.value = conflict.id;
}

function applyResolution(conflictId: string, resolution: string) {
  emit('resolve', conflictId, resolution);
  resolvingConflict.value = null;
}

function formatType(type: string): string {
  return type
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function getConflictIcon(type: string): string {
  const icons: Record<string, string> = {
    'vessel-overlap': 'icon-anchor',
    'port-capacity': 'icon-box',
    'cargo-timing': 'icon-clock',
    'resource-shortage': 'icon-alert-circle',
  };
  return icons[type] || 'icon-alert-triangle';
}
</script>

<style scoped>
.conflict-detector {
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.5rem;
  overflow: hidden;
}

.detector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--bg-secondary, #f9fafb);
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.detector-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.conflict-summary {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.no-conflicts {
  color: var(--success-color, #10b981);
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-weight: 500;
}

.conflict-badge {
  padding: 0.25rem 0.625rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.conflict-badge.critical {
  background: #fee2e2;
  color: #991b1b;
}

.conflict-badge.high {
  background: #fed7aa;
  color: #9a3412;
}

.conflict-badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.conflict-badge.low {
  background: #dbeafe;
  color: #1e40af;
}

.conflicts-container {
  padding: 1rem;
}

.filter-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  min-width: 150px;
}

.conflicts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 500px;
  overflow-y: auto;
}

.conflict-card {
  border: 2px solid;
  border-radius: 0.5rem;
  padding: 1rem;
  transition: all 0.2s;
}

.conflict-card.severity-critical {
  border-color: #fca5a5;
  background: #fef2f2;
}

.conflict-card.severity-high {
  border-color: #fdba74;
  background: #fff7ed;
}

.conflict-card.severity-medium {
  border-color: #fcd34d;
  background: #fefce8;
}

.conflict-card.severity-low {
  border-color: #93c5fd;
  background: #eff6ff;
}

.conflict-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.conflict-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.conflict-type {
  font-weight: 600;
  font-size: 0.875rem;
}

.severity-tag {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.severity-tag.critical {
  background: #dc2626;
  color: white;
}

.severity-tag.high {
  background: #ea580c;
  color: white;
}

.severity-tag.medium {
  background: #f59e0b;
  color: white;
}

.severity-tag.low {
  background: #3b82f6;
  color: white;
}

.resolve-btn {
  padding: 0.375rem 0.75rem;
  background: var(--primary-color, #3b82f6);
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background 0.2s;
}

.resolve-btn:hover {
  background: var(--primary-hover, #2563eb);
}

.conflict-description {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary, #374151);
  line-height: 1.5;
}

.affected-entities {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.75rem;
}

.affected-entities .label {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-secondary, #6b7280);
}

.entities-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.entity-tag {
  padding: 0.125rem 0.5rem;
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.suggested-resolution {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: var(--primary-color, #3b82f6);
}

.resolution-panel {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color, #e5e7eb);
}

.resolution-panel h5 {
  margin: 0 0 0.75rem 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.resolution-options {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.resolution-option {
  flex: 1;
  padding: 0.75rem;
  background: white;
  border: 2px solid var(--border-color, #e5e7eb);
  border-radius: 0.375rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.375rem;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.resolution-option:hover {
  border-color: var(--primary-color, #3b82f6);
  background: rgba(59, 130, 246, 0.05);
}

.cancel-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.cancel-btn:hover {
  background: var(--bg-secondary, #f9fafb);
}

.no-conflicts-state {
  padding: 3rem 1rem;
  text-align: center;
  color: var(--success-color, #10b981);
}

.no-conflicts-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.no-conflicts-state h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary, #111827);
  font-size: 1.25rem;
}

.no-conflicts-state p {
  margin: 0;
  color: var(--text-secondary, #6b7280);
}
</style>
