<template>
  <div class="data-card" :class="[`variant-${variant}`, { 'is-clickable': clickable }]" @click="handleClick">
    <div v-if="icon" class="card-icon" :class="`icon-${iconColor}`">
      {{ icon }}
    </div>
    
    <div class="card-content">
      <div v-if="title" class="card-title">{{ title }}</div>
      <div class="card-value">
        <slot name="value">
          {{ formattedValue }}
        </slot>
      </div>
      <div v-if="subtitle || $slots.subtitle" class="card-subtitle">
        <slot name="subtitle">
          {{ subtitle }}
        </slot>
      </div>
      
      <div v-if="trend !== undefined" class="card-trend" :class="trendClass">
        <svg v-if="trend > 0" class="trend-icon" width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M2 10L6 6L10 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          <path d="M10 7V2H5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <svg v-else-if="trend < 0" class="trend-icon" width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M2 2L6 6L10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          <path d="M10 5V10H5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <svg v-else class="trend-icon" width="12" height="2" viewBox="0 0 12 2" fill="none">
          <path d="M1 1H11" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
        <span class="trend-value">{{ trendText }}</span>
      </div>
    </div>
    
    <div v-if="$slots.actions" class="card-actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  title?: string;
  value?: string | number;
  subtitle?: string;
  icon?: string;
  iconColor?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'gray';
  variant?: 'default' | 'bordered' | 'elevated';
  trend?: number;
  trendSuffix?: string;
  clickable?: boolean;
  formatValue?: (value: string | number) => string;
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: 'blue',
  variant: 'default',
  trendSuffix: '%',
  clickable: false,
});

const emit = defineEmits<{
  click: []
}>();

const formattedValue = computed(() => {
  if (props.value === undefined) return '';
  if (props.formatValue) return props.formatValue(props.value);
  
  // Default formatting for numbers
  if (typeof props.value === 'number') {
    return props.value.toLocaleString();
  }
  
  return String(props.value);
});

const trendClass = computed(() => {
  if (props.trend === undefined) return '';
  if (props.trend > 0) return 'trend-up';
  if (props.trend < 0) return 'trend-down';
  return 'trend-neutral';
});

const trendText = computed(() => {
  if (props.trend === undefined) return '';
  const abs = Math.abs(props.trend);
  return `${abs}${props.trendSuffix}`;
});

function handleClick() {
  if (props.clickable) {
    emit('click');
  }
}
</script>

<style scoped>
.data-card {
  position: relative;
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 8px;
  background: var(--color-background);
  transition: all 0.2s;
}

.variant-default {
  border: none;
}

.variant-bordered {
  border: 1px solid var(--color-border);
}

.variant-elevated {
  border: 1px solid var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.data-card.is-clickable {
  cursor: pointer;
}

.data-card.is-clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.card-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  font-size: 1.5rem;
  background: rgba(var(--color-primary-rgb), 0.1);
}

.icon-blue {
  background: #e3f2fd;
  color: #1976d2;
}

.icon-green {
  background: #e8f5e9;
  color: #388e3c;
}

.icon-yellow {
  background: #fffde7;
  color: #f57f17;
}

.icon-red {
  background: #ffebee;
  color: #d32f2f;
}

.icon-purple {
  background: #f3e5f5;
  color: #7b1fa2;
}

.icon-gray {
  background: #f5f5f5;
  color: #616161;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
}

.card-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.card-trend {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.trend-up {
  color: #388e 3c;
}

.trend-down {
  color: #d32f2f;
}

.trend-neutral {
  color: var(--color-text-secondary);
}

.trend-icon {
  flex-shrink: 0;
}

.trend-value {
  line-height: 1;
}

.card-actions {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
}

@media (max-width: 640px) {
  .data-card {
    flex-direction: column;
  }
  
  .card-icon {
    align-self: flex-start;
  }
}
</style>
