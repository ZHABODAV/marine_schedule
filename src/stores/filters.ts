import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Module } from '@/types/calendar.types';

export interface DateRange {
  start: Date | null;
  end: Date | null;
}

export interface FilterState {
  module: Module;
  dateRange: DateRange;
  vessels: string[];
  ports: string[];
  routes: string[];
  cargoTypes: string[];
  statuses: string[];
  searchQuery: string;
}

export const useFiltersStore = defineStore('filters', () => {
  // Feature-specific filters
  const voyageFilters = ref<FilterState>({
    module: 'all',
    dateRange: { start: null, end: null },
    vessels: [],
    ports: [],
    routes: [],
    cargoTypes: [],
    statuses: [],
    searchQuery: '',
  });

  const scheduleFilters = ref<FilterState>({
    module: 'all',
    dateRange: { start: null, end: null },
    vessels: [],
    ports: [],
    routes: [],
    cargoTypes: [],
    statuses: [],
    searchQuery: '',
  });

  const reportFilters = ref<FilterState>({
    module: 'all',
    dateRange: { start: null, end: null },
    vessels: [],
    ports: [],
    routes: [],
    cargoTypes: [],
    statuses: [],
    searchQuery: '',
  });

  const calendarFilters = ref<FilterState>({
    module: 'all',
    dateRange: { start: null, end: null },
    vessels: [],
    ports: [],
    routes: [],
    cargoTypes: [],
    statuses: [],
    searchQuery: '',
  });

  // Global filter presets
  const presets = ref<Array<{ name: string; filters: Partial<FilterState> }>>([
    {
      name: 'This Month',
      filters: {
        dateRange: {
          start: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
          end: new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0),
        },
      },
    },
    {
      name: 'This Year',
      filters: {
        dateRange: {
          start: new Date(new Date().getFullYear(), 0, 1),
          end: new Date(new Date().getFullYear(), 11, 31),
        },
      },
    },
    {
      name: 'Last 30 Days',
      filters: {
        dateRange: {
          start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
          end: new Date(),
        },
      },
    },
  ]);

  // Getters
  const activeVoyageFiltersCount = computed(() => {
    let count = 0;
    if (voyageFilters.value.module !== 'all') count++;
    if (voyageFilters.value.dateRange.start || voyageFilters.value.dateRange.end) count++;
    if (voyageFilters.value.vessels.length > 0) count++;
    if (voyageFilters.value.ports.length > 0) count++;
    if (voyageFilters.value.routes.length > 0) count++;
    if (voyageFilters.value.cargoTypes.length > 0) count++;
    if (voyageFilters.value.statuses.length > 0) count++;
    if (voyageFilters.value.searchQuery) count++;
    return count;
  });

  const activeScheduleFiltersCount = computed(() => {
    let count = 0;
    if (scheduleFilters.value.module !== 'all') count++;
    if (scheduleFilters.value.dateRange.start || scheduleFilters.value.dateRange.end) count++;
    if (scheduleFilters.value.vessels.length > 0) count++;
    if (scheduleFilters.value.searchQuery) count++;
    return count;
  });

  const activeReportFiltersCount = computed(() => {
    let count = 0;
    if (reportFilters.value.module !== 'all') count++;
    if (reportFilters.value.dateRange.start || reportFilters.value.dateRange.end) count++;
    if (reportFilters.value.vessels.length > 0) count++;
    return count;
  });

  const activeCalendarFiltersCount = computed(() => {
    let count = 0;
    if (calendarFilters.value.module !== 'all') count++;
    if (calendarFilters.value.dateRange.start || calendarFilters.value.dateRange.end) count++;
    if (calendarFilters.value.vessels.length > 0) count++;
    if (calendarFilters.value.ports.length > 0) count++;
    return count;
  });

  const hasVoyageFilters = computed(() => activeVoyageFiltersCount.value > 0);
  const hasScheduleFilters = computed(() => activeScheduleFiltersCount.value > 0);
  const hasReportFilters = computed(() => activeReportFiltersCount.value > 0);
  const hasCalendarFilters = computed(() => activeCalendarFiltersCount.value > 0);

  // Actions
  function setVoyageFilter<K extends keyof FilterState>(key: K, value: FilterState[K]) {
    voyageFilters.value[key] = value;
  }

  function setScheduleFilter<K extends keyof FilterState>(key: K, value: FilterState[K]) {
    scheduleFilters.value[key] = value;
  }

  function setReportFilter<K extends keyof FilterState>(key: K, value: FilterState[K]) {
    reportFilters.value[key] = value;
  }

  function setCalendarFilter<K extends keyof FilterState>(key: K, value: FilterState[K]) {
    calendarFilters.value[key] = value;
  }

  function updateVoyageFilters(updates: Partial<FilterState>) {
    voyageFilters.value = { ...voyageFilters.value, ...updates };
  }

  function updateScheduleFilters(updates: Partial<FilterState>) {
    scheduleFilters.value = { ...scheduleFilters.value, ...updates };
  }

  function updateReportFilters(updates: Partial<FilterState>) {
    reportFilters.value = { ...reportFilters.value, ...updates };
  }

  function updateCalendarFilters(updates: Partial<FilterState>) {
    calendarFilters.value = { ...calendarFilters.value, ...updates };
  }

  function resetVoyageFilters() {
    voyageFilters.value = {
      module: 'all',
      dateRange: { start: null, end: null },
      vessels: [],
      ports: [],
      routes: [],
      cargoTypes: [],
      statuses: [],
      searchQuery: '',
    };
  }

  function resetScheduleFilters() {
    scheduleFilters.value = {
      module: 'all',
      dateRange: { start: null, end: null },
      vessels: [],
      ports: [],
      routes: [],
      cargoTypes: [],
      statuses: [],
      searchQuery: '',
    };
  }

  function resetReportFilters() {
    reportFilters.value = {
      module: 'all',
      dateRange: { start: null, end: null },
      vessels: [],
      ports: [],
      routes: [],
      cargoTypes: [],
      statuses: [],
      searchQuery: '',
    };
  }

  function resetCalendarFilters() {
    calendarFilters.value = {
      module: 'all',
      dateRange: { start: null, end: null },
      vessels: [],
      ports: [],
      routes: [],
      cargoTypes: [],
      statuses: [],
      searchQuery: '',
    };
  }

  function resetAllFilters() {
    resetVoyageFilters();
    resetScheduleFilters();
    resetReportFilters();
    resetCalendarFilters();
  }

  function applyPreset(presetName: string, context: 'voyage' | 'schedule' | 'report' | 'calendar') {
    const preset = presets.value.find(p => p.name === presetName);
    if (!preset) return;

    switch (context) {
      case 'voyage':
        updateVoyageFilters(preset.filters);
        break;
      case 'schedule':
        updateScheduleFilters(preset.filters);
        break;
      case 'report':
        updateReportFilters(preset.filters);
        break;
      case 'calendar':
        updateCalendarFilters(preset.filters);
        break;
    }
  }

  function addPreset(name: string, filters: Partial<FilterState>) {
    const existing = presets.value.find(p => p.name === name);
    if (existing) {
      existing.filters = filters;
    } else {
      presets.value.push({ name, filters });
    }
    savePresetsToLocalStorage();
  }

  function removePreset(name: string) {
    const index = presets.value.findIndex(p => p.name === name);
    if (index !== -1) {
      presets.value.splice(index, 1);
      savePresetsToLocalStorage();
    }
  }

  function savePresetsToLocalStorage() {
    try {
      localStorage.setItem('filterPresets', JSON.stringify(presets.value));
    } catch (e) {
      console.error('Failed to save filter presets to localStorage:', e);
    }
  }

  function loadPresetsFromLocalStorage() {
    try {
      const saved = localStorage.getItem('filterPresets');
      if (saved) {
        const parsed = JSON.parse(saved);
        // Merge with default presets
        const defaultPresetNames = presets.value.map(p => p.name);
        const customPresets = parsed.filter((p: any) => !defaultPresetNames.includes(p.name));
        presets.value = [...presets.value, ...customPresets];
      }
    } catch (e) {
      console.error('Failed to load filter presets from localStorage:', e);
    }
  }

  // Load presets on initialization
  loadPresetsFromLocalStorage();

  return {
    // State
    voyageFilters,
    scheduleFilters,
    reportFilters,
    calendarFilters,
    presets,
    // Getters
    activeVoyageFiltersCount,
    activeScheduleFiltersCount,
    activeReportFiltersCount,
    activeCalendarFiltersCount,
    hasVoyageFilters,
    hasScheduleFilters,
    hasReportFilters,
    hasCalendarFilters,
    // Actions
    setVoyageFilter,
    setScheduleFilter,
    setReportFilter,
    setCalendarFilter,
    updateVoyageFilters,
    updateScheduleFilters,
    updateReportFilters,
    updateCalendarFilters,
    resetVoyageFilters,
    resetScheduleFilters,
    resetReportFilters,
    resetCalendarFilters,
    resetAllFilters,
    applyPreset,
    addPreset,
    removePreset,
  };
});
