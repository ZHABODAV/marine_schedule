<template>
  <span
    class="status-badge"
    :class="[
      `status-${status}`,
      `variant-${variant}`,
      { 'with-icon': showIcon }
    ]"
  >
    <span v-if="showIcon" class="status-icon">{{ icon }}</span>
    <span class="status-text">{{ label || status }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  status: string;
  label?: string;
  variant?: 'default' | 'outlined' | 'minimal';
  showIcon?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  showIcon: false,
});

const statusConfig: Record<string, { icon: string; color: string }> = {
  // Voyage statuses
  draft: { icon: '', color: 'gray' },
  planned: { icon: '', color: 'blue' },
  'in-progress': { icon: '', color: 'blue' },
  active: { icon: '', color: 'green' },
  completed: { icon: '', color: 'green' },
  cancelled: { icon: '', color: 'red' },
  delayed: { icon: '', color: 'yellow' },
  
  // Report statuses
  pending: { icon: '', color: 'gray' },
  generating: { icon: '', color: 'blue' },
  failed: { icon: '', color: 'red' },
  
  // Schedule statuses
  finalized: { icon: '', color: 'green' },
  archived: { icon: '', color: 'gray' },
  
  // Conflict severity
  low: { icon: '', color: 'blue' },
  medium: { icon: '', color: 'yellow' },
  high: { icon: '', color: 'orange' },
  critical: { icon: '', color: 'red' },
  
  // Generic statuses
  success: { icon: '', color: 'green' },
  warning: { icon: '', color: 'yellow' },
  error: { icon: '', color: 'red' },
  info: { icon: '', color: 'blue' },
};

const config = computed(() => 
  statusConfig[props.status.toLowerCase()] || { icon: '•', color: 'gray' }
);

const icon = computed(() => config.value.icon);
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  transition: all 0.2s;
}

/* Status colors - Default variant */
.variant-default.status-draft,
.variant-default.status-pending,
.variant-default.status-archived,
.variant-default.status-gray {
  background: #e0e0e0;
  color: #616161;
}

.variant-default.status-planned,
.variant-default.status-in-progress,
.variant-default.status-generating,
.variant-default.status-low,
.variant-default.status-info,
.variant-default.status-blue {
  background: #bbdefb;
  color: #1565c0;
}

.variant-default.status-active,
.variant-default.status-completed,
.variant-default.status-finalized,
.variant-default.status-success,
.variant-default.status-green {
  background: #c8e6c9;
  color: #2e7d32;
}

.variant-default.status-delayed,
.variant-default.status-medium,
.variant-default.status-warning,
.variant-default.status-yellow {
  background: #fff9c4;
  color: #f57f17;
}

.variant-default.status-high,
.variant-default.status-orange {
  background: #ffe0b2;
  color: #e65100;
}

.variant-default.status-cancelled,
.variant-default.status-failed,
.variant-default.status-critical,
.variant-default.status-error,
.variant-default.status-red {
  background: #ffcdd2;
  color: #c62828;
}

/* Outlined variant */
.variant-outlined {
  background: transparent;
  border: 1.5px solid currentColor;
}

.variant-outlined.status-draft,
.variant-outlined.status-pending,
.variant-outlined.status-archived,
.variant-outlined.status-gray {
  color: #616161;
}

.variant-outlined.status-planned,
.variant-outlined.status-in-progress,
.variant-outlined.status-generating,
.variant-outlined.status-low,
.variant-outlined.status-info,
.variant-outlined.status-blue {
  color: #1565c0;
}

.variant-outlined.status-active,
.variant-outlined.status-completed,
.variant-outlined.status-finalized,
.variant-outlined.status-success,
.variant-outlined.status-green {
  color: #2e7d32;
}

.variant-outlined.status-delayed,
.variant-outlined.status-medium,
.variant-outlined.status-warning,
.variant-outlined.status-yellow {
  color: #f57f17;
}

.variant-outlined.status-high,
.variant-outlined.status-orange {
  color: #e65100;
}

.variant-outlined.status-cancelled,
.variant-outlined.status-failed,
.variant-outlined.status-critical,
.variant-outlined.status-error,
.variant-outlined.status-red {
  color: #c62828;
}

/* Minimal variant */
.variant-minimal {
  background: transparent;
  padding: 0;
}

.variant-minimal.status-draft,
.variant-minimal.status-pending,
.variant-minimal.status-archived,
.variant-minimal.status-gray {
  color: #616161;
}

.variant-minimal.status-planned,
.variant-minimal.status-in-progress,
.variant-minimal.status-generating,
.variant-minimal.status-low,
.variant-minimal.status-info,
.variant-minimal.status-blue {
  color: #1565c0;
}

.variant-minimal.status-active,
.variant-minimal.status-completed,
.variant-minimal.status-finalized,
.variant-minimal.status-success,
.variant-minimal.status-green {
  color: #2e7d32;
}

.variant-minimal.status-delayed,
.variant-minimal.status-medium,
.variant-minimal.status-warning,
.variant-minimal.status-yellow {
  color: #f57f17;
}

.variant-minimal.status-high,
.variant-minimal.status-orange {
  color: #e65100;
}

.variant-minimal.status-cancelled,
.variant-minimal.status-failed,
.variant-minimal.status-critical,
.variant-minimal.status-error,
.variant-minimal.status-red {
  color: #c62828;
}

.status-icon {
  display: inline-flex;
  font-size: 0.875rem;
}

.status-text {
  line-height: 1;
}
</style>
