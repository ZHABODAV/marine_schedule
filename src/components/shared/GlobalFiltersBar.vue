<template>
  <div class="global-filters-bar">
    <div class="filters-container">
      <!-- Module Filter -->
      <div class="filter-group">
        <label class="filter-label">Module</label>
        <BaseSelect
          v-model="localFilters.module"
          :options="moduleOptions"
          placeholder="All Modules"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Date Range Filter -->
      <div class="filter-group">
        <label class="filter-label">Date Range</label>
        <DateRangePicker
          v-model="localFilters.dateRange"
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Vessels Filter (Multi-select) -->
      <div v-if="showVessels" class="filter-group">
        <label class="filter-label">Vessels</label>
        <MultiSelect
          v-model="localFilters.vessels"
          :options="vesselOptions"
          placeholder="Select vessels..."
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Ports Filter (Multi-select) -->
      <div v-if="showPorts" class="filter-group">
        <label class="filter-label">Ports</label>
        <MultiSelect
          v-model="localFilters.ports"
          :options="portOptions"
          placeholder="Select ports..."
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Routes Filter (Multi-select) -->
      <div v-if="showRoutes" class="filter-group">
        <label class="filter-label">Routes</label>
        <MultiSelect
          v-model="localFilters.routes"
          :options="routeOptions"
          placeholder="Select routes..."
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Cargo Types Filter (Multi-select) -->
      <div v-if="showCargoTypes" class="filter-group">
        <label class="filter-label">Cargo Types</label>
        <MultiSelect
          v-model="localFilters.cargoTypes"
          :options="cargoTypeOptions"
          placeholder="Select cargo types..."
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Status Filter (Multi-select) -->
      <div v-if="showStatuses" class="filter-group">
        <label class="filter-label">Status</label>
        <MultiSelect
          v-model="localFilters.statuses"
          :options="statusOptions"
          placeholder="Select statuses..."
          @update:modelValue="emitFilters"
        />
      </div>

      <!-- Search Query -->
      <div v-if="showSearch" class="filter-group filter-search">
        <label class="filter-label">Search</label>
        <BaseInput
          v-model="localFilters.searchQuery"
          type="text"
          placeholder="Search..."
          clearable
          @update:modelValue="emitFilters"
        />
      </div>
    </div>

    <!-- Filter Actions -->
    <div class="filters-actions">
      <div class="filter-presets">
        <BaseSelect
          v-model="selectedPreset"
          :options="presetOptions"
          placeholder="Presets..."
          clearable
          @update:modelValue="applyPreset"
        />
      </div>
      
      <div class="filter-buttons">
        <BaseButton
          v-if="activeFiltersCount > 0"
          variant="text"
          size="small"
          @click="resetFilters"
        >
          Clear All ({{ activeFiltersCount }})
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useFiltersStore, type FilterState } from '@/stores/filters';
import type { Module } from '@/types/calendar.types';
import BaseSelect from './BaseSelect.vue';
import BaseInput from './BaseInput.vue';
import BaseButton from './BaseButton.vue';
import DateRangePicker from './DateRangePicker.vue';
import MultiSelect from './MultiSelect.vue';

interface Props {
  context: 'voyage' | 'schedule' | 'report' | 'calendar';
  showVessels?: boolean;
  showPorts?: boolean;
  showRoutes?: boolean;
  showCargoTypes?: boolean;
  showStatuses?: boolean;
  showSearch?: boolean;
  vesselOptions?: Array<{ value: string; label: string }>;
  portOptions?: Array<{ value: string; label: string }>;
  routeOptions?: Array<{ value: string; label: string }>;
  cargoTypeOptions?: Array<{ value: string; label: string }>;
  statusOptions?: Array<{ value: string; label: string }>;
}

const props = withDefaults(defineProps<Props>(), {
  showVessels: true,
  showPorts: true,
  showRoutes: true,
  showCargoTypes: true,
  showStatuses: true,
  showSearch: true,
  vesselOptions: () => [],
  portOptions: () => [],
  routeOptions: () => [],
  cargoTypeOptions: () => [],
  statusOptions: () => [],
});

const emit = defineEmits<{
  filtersChanged: [filters: FilterState];
}>();

const filtersStore = useFiltersStore();
const selectedPreset = ref<string>('');

// Get the appropriate filters based on context
const contextFilters = computed(() => {
  switch (props.context) {
    case 'voyage':
      return filtersStore.voyageFilters;
    case 'schedule':
      return filtersStore.scheduleFilters;
    case 'report':
      return filtersStore.reportFilters;
    case 'calendar':
      return filtersStore.calendarFilters;
  }
});

const activeFiltersCount = computed(() => {
  switch (props.context) {
    case 'voyage':
      return filtersStore.activeVoyageFiltersCount;
    case 'schedule':
      return filtersStore.activeScheduleFiltersCount;
    case 'report':
      return filtersStore.activeReportFiltersCount;
    case 'calendar':
      return filtersStore.activeCalendarFiltersCount;
  }
});

// Local filters for two-way binding
const localFilters = ref<FilterState>({ ...contextFilters.value });

// Watch context filters from store
watch(contextFilters, (newFilters) => {
  localFilters.value = { ...newFilters };
}, { deep: true });

const moduleOptions = computed(() => [
  { value: 'all', label: 'All Modules' },
  { value: 'olya', label: 'Olya' },
  { value: 'deep-sea', label: 'Deep Sea' },
  { value: 'balakovo', label: 'Balakovo' },
]);

const presetOptions = computed(() =>
  filtersStore.presets.map(p => ({ value: p.name, label: p.name }))
);

function emitFilters() {
  // Update store based on context
  switch (props.context) {
    case 'voyage':
      filtersStore.updateVoyageFilters(localFilters.value);
      break;
    case 'schedule':
      filtersStore.updateScheduleFilters(localFilters.value);
      break;
    case 'report':
      filtersStore.updateReportFilters(localFilters.value);
      break;
    case 'calendar':
      filtersStore.updateCalendarFilters(localFilters.value);
      break;
  }
  
  emit('filtersChanged', localFilters.value);
}

function resetFilters() {
  switch (props.context) {
    case 'voyage':
      filtersStore.resetVoyageFilters();
      break;
    case 'schedule':
      filtersStore.resetScheduleFilters();
      break;
    case 'report':
      filtersStore.resetReportFilters();
      break;
    case 'calendar':
      filtersStore.resetCalendarFilters();
      break;
  }
  selectedPreset.value = '';
}

function applyPreset(presetName: string) {
  if (!presetName) return;
  filtersStore.applyPreset(presetName, props.context);
}
</script>

<style scoped>
.global-filters-bar {
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.filters-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-search {
  grid-column: span 2;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.filters-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.filter-presets {
  min-width: 200px;
}

.filter-buttons {
  display: flex;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .filters-container {
    grid-template-columns: 1fr;
  }
  
  .filter-search {
    grid-column: span 1;
  }
  
  .filters-actions {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .filter-presets {
    min-width: auto;
  }
}
</style>
