<template>
  <div class="date-range-picker">
    <div class="date-inputs">
      <div class="date-input-group">
        <input
          ref="startInput"
          v-model="startDateString"
          type="date"
          class="date-input"
          placeholder="Start Date"
          @change="handleStartDateChange"
        />
      </div>
      <span class="date-separator">to</span>
      <div class="date-input-group">
        <input
          ref="endInput"
          v-model="endDateString"
          type="date"
          class="date-input"
          placeholder="End Date"
          @change="handleEndDateChange"
        />
      </div>
      <button
        v-if="hasValue"
        class="clear-button"
        type="button"
        @click="clearDates"
        title="Clear dates"
      >
        
      </button>
    </div>

    <!-- Quick presets -->
    <div v-if="showPresets" class="date-presets">
      <button
        v-for="preset in datePresets"
        :key="preset.label"
        class="preset-button"
        type="button"
        @click="applyPreset(preset)"
      >
        {{ preset.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { DateRange } from '@/stores/filters';

interface Props {
  modelValue: DateRange;
  showPresets?: boolean;
  minDate?: Date;
  maxDate?: Date;
}

const props = withDefaults(defineProps<Props>(), {
  showPresets: true,
});

const emit = defineEmits<{
  'update:modelValue': [value: DateRange];
}>();

const startInput = ref<HTMLInputElement>();
const endInput = ref<HTMLInputElement>();

const startDateString = ref('');
const endDateString = ref('');

// Formatters
function dateToString(date: Date | null): string {
  if (!date) return '';
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function stringToDate(str: string): Date | null {
  if (!str) return null;
  const date = new Date(str);
  return isNaN(date.getTime()) ? null : date;
}

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  startDateString.value = dateToString(newValue.start);
  endDateString.value = dateToString(newValue.end);
}, { immediate: true, deep: true });

const hasValue = computed(() => 
  props.modelValue.start !== null || props.modelValue.end !== null
);

// Date presets
interface DatePreset {
  label: string;
  getRange: () => DateRange;
}

const datePresets = ref<DatePreset[]>([
  {
    label: 'Today',
    getRange: () => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return { start: today, end: today };
    },
  },
  {
    label: 'This Week',
    getRange: () => {
      const today = new Date();
      const dayOfWeek = today.getDay();
      const start = new Date(today);
      start.setDate(today.getDate() - dayOfWeek);
      start.setHours(0, 0, 0, 0);
      const end = new Date(start);
      end.setDate(start.getDate() + 6);
      return { start, end };
    },
  },
  {
    label: 'This Month',
    getRange: () => {
      const today = new Date();
      const start = new Date(today.getFullYear(), today.getMonth(), 1);
      const end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
      return { start, end };
    },
  },
  {
    label: 'This Quarter',
    getRange: () => {
      const today = new Date();
      const quarter = Math.floor(today.getMonth() / 3);
      const start = new Date(today.getFullYear(), quarter * 3, 1);
      const end = new Date(today.getFullYear(), quarter * 3 + 3, 0);
      return { start, end };
    },
  },
  {
    label: 'This Year',
    getRange: () => {
      const today = new Date();
      const start = new Date(today.getFullYear(), 0, 1);
      const end = new Date(today.getFullYear(), 11, 31);
      return { start, end };
    },
  },
  {
    label: 'Last 7 Days',
    getRange: () => {
      const end = new Date();
      end.setHours(23, 59, 59, 999);
      const start = new Date(end);
      start.setDate(end.getDate() - 6);
      start.setHours(0, 0, 0, 0);
      return { start, end };
    },
  },
  {
    label: 'Last 30 Days',
    getRange: () => {
      const end = new Date();
      end.setHours(23, 59, 59, 999);
      const start = new Date(end);
      start.setDate(end.getDate() - 29);
      start.setHours(0, 0, 0, 0);
      return { start, end };
    },
  },
  {
    label: 'Last 90 Days',
    getRange: () => {
      const end = new Date();
      end.setHours(23, 59, 59, 999);
      const start = new Date(end);
      start.setDate(end.getDate() - 89);
      start.setHours(0, 0, 0, 0);
      return { start, end };
    },
  },
]);

function handleStartDateChange() {
  const start = stringToDate(startDateString.value);
  emit('update:modelValue', {
    start,
    end: props.modelValue.end,
  });
}

function handleEndDateChange() {
  const end = stringToDate(endDateString.value);
  emit('update:modelValue', {
    start: props.modelValue.start,
    end,
  });
}

function clearDates() {
  startDateString.value = '';
  endDateString.value = '';
  emit('update:modelValue', {
    start: null,
    end: null,
  });
}

function applyPreset(preset: DatePreset) {
  const range = preset.getRange();
  emit('update:modelValue', range);
}
</script>

<style scoped>
.date-range-picker {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.date-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
}

.date-input-group {
  flex: 1;
}

.date-input {
  width: 100%;
  padding: 0.375rem 0.5rem;
  font-size: 0.875rem;
  border: none;
  background: transparent;
  color: var(--color-text);
  font-family: inherit;
}

.date-input:focus {
  outline: none;
}

.date-input::-webkit-calendar-picker-indicator {
  cursor: pointer;
  opacity: 0.6;
}

.date-input::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}

.date-separator {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.clear-button {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: 3px;
  font-size: 0.875rem;
  line-height: 1;
  transition: all 0.2s;
}

.clear-button:hover {
  background: var(--color-background-soft);
  color: var(--color-text);
}

.date-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.preset-button {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid var(--color-border);
  background: var(--color-background);
  color: var(--color-text);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.preset-button:hover {
  background: var(--color-background-soft);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

@media (max-width: 640px) {
  .date-inputs {
    flex-wrap: wrap;
  }
  
  .date-input-group {
    flex-basis: calc(50% - 0.25rem);
  }
  
  .date-separator {
    display: none;
  }
}
</style>
