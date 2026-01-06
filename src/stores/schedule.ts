import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { handleApiError } from '@/services/api';
import type {
  YearSchedule,
  YearScheduleConfig,
  ScheduleTemplate
} from '@/types/schedule.types';
import { useAppStore } from './app';

export const useScheduleStore = defineStore('schedule', () => {
  // State
  const currentSchedule = ref<YearSchedule | null>(null);
  const schedules = ref<YearSchedule[]>([]);
  const templates = ref<ScheduleTemplate[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const generating = ref(false);

  // Getters
  const totalSchedules = computed(() => schedules.value.length);
  const activeSchedules = computed(() => 
    schedules.value.filter(s => s.status !== 'archived')
  );
  const schedulesByYear = computed(() => {
    const grouped: Record<number, YearSchedule[]> = {};
    schedules.value.forEach(schedule => {
      const year = schedule.config.year;
      if (!grouped[year]) grouped[year] = [];
      grouped[year].push(schedule);
    });
    return grouped;
  });
  const conflicts = computed(() => currentSchedule.value?.conflicts || []);
  const criticalConflicts = computed(() => 
    conflicts.value.filter(c => c.severity === 'critical')
  );

  // Actions
  async function fetchSchedules(year?: number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const params = year ? { year } : {};
      const response = await fetch(`/api/schedules?${new URLSearchParams(params as any)}`);
      if (!response.ok) throw new Error('Failed to fetch schedules');
      schedules.value = await response.json();
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
    } finally {
      loading.value = false;
    }
  }

  async function fetchScheduleById(id: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/schedules/${id}`);
      if (!response.ok) throw new Error('Failed to fetch schedule');
      currentSchedule.value = await response.json();
      return currentSchedule.value;
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function generateSchedule(config: YearScheduleConfig) {
    const appStore = useAppStore();
    generating.value = true;
    error.value = null;
    try {
      const response = await fetch('/api/schedule/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (!response.ok) throw new Error('Failed to generate schedule');
      const newSchedule = await response.json();
      schedules.value.unshift(newSchedule);
      currentSchedule.value = newSchedule;
      appStore.addNotification({
        type: 'success',
        message: 'Schedule generated successfully',
      });
      return newSchedule;
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return null;
    } finally {
      generating.value = false;
    }
  }

  async function updateSchedule(id: string, updates: Partial<YearSchedule>) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/schedules/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      if (!response.ok) throw new Error('Failed to update schedule');
      const updatedSchedule = await response.json();
      const index = schedules.value.findIndex(s => s.id === id);
      if (index !== -1) {
        schedules.value[index] = updatedSchedule;
      }
      if (currentSchedule.value?.id === id) {
        currentSchedule.value = updatedSchedule;
      }
      appStore.addNotification({
        type: 'success',
        message: 'Schedule updated successfully',
      });
      return updatedSchedule;
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function finalizeSchedule(id: string) {
    return updateSchedule(id, { status: 'finalized' });
  }

  async function archiveSchedule(id: string) {
    return updateSchedule(id, { status: 'archived' });
  }

  async function deleteSchedule(id: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/schedules/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete schedule');
      const index = schedules.value.findIndex(s => s.id === id);
      if (index !== -1) {
        schedules.value.splice(index, 1);
      }
      if (currentSchedule.value?.id === id) {
        currentSchedule.value = null;
      }
      appStore.addNotification({
        type: 'success',
        message: 'Schedule deleted successfully',
      });
      return true;
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTemplates(module?: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const params = module ? { module } : {};
      const response = await fetch(`/api/schedules/templates?${new URLSearchParams(params as any)}`);
      if (!response.ok) throw new Error('Failed to fetch templates');
      templates.value = await response.json();
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
    } finally {
      loading.value = false;
    }
  }

  async function resolveConflict(scheduleId: string, conflictId: string, resolution: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/schedules/${scheduleId}/conflicts/${conflictId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolution }),
      });
      if (!response.ok) throw new Error('Failed to resolve conflict');
      const updatedSchedule = await response.json();
      if (currentSchedule.value?.id === scheduleId) {
        currentSchedule.value = updatedSchedule;
      }
      appStore.addNotification({
        type: 'success',
        message: 'Conflict resolved successfully',
      });
      return updatedSchedule;
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function exportToPDF(scheduleId: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/schedules/${scheduleId}/export/pdf`);
      if (!response.ok) throw new Error('Failed to export PDF');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const schedule = schedules.value.find(s => s.id === scheduleId);
      a.download = `schedule-${schedule?.config.year || 'export'}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      appStore.addNotification({
        type: 'success',
        message: 'PDF exported successfully',
      });
      return true;
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function exportToExcel(scheduleId: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/schedules/${scheduleId}/export/excel`);
      if (!response.ok) throw new Error('Failed to export Excel');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const schedule = schedules.value.find(s => s.id === scheduleId);
      a.download = `schedule-${schedule?.config.year || 'export'}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      appStore.addNotification({
        type: 'success',
        message: 'Excel exported successfully',
      });
      return true;
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function saveScenario(scheduleId: string, name: string, description?: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/schedules/${scheduleId}/scenario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description }),
      });
      if (!response.ok) throw new Error('Failed to save scenario');
      const savedSchedule = await response.json();
      const index = schedules.value.findIndex(s => s.id === scheduleId);
      if (index !== -1) {
        schedules.value[index] = savedSchedule;
      }
      if (currentSchedule.value?.id === scheduleId) {
        currentSchedule.value = savedSchedule;
      }
      appStore.addNotification({
        type: 'success',
        message: `Scenario "${name}" saved successfully`,
      });
      return savedSchedule;
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return null;
    } finally {
      loading.value = false;
    }
  }

  function clearError() {
    error.value = null;
  }

  function clearData() {
    schedules.value = [];
    templates.value = [];
    currentSchedule.value = null;
  }

  return {
    // State
    currentSchedule,
    schedules,
    templates,
    loading,
    error,
    generating,
    // Getters
    totalSchedules,
    activeSchedules,
    schedulesByYear,
    conflicts,
    criticalConflicts,
    // Actions
    fetchSchedules,
    fetchScheduleById,
    generateSchedule,
    updateSchedule,
    finalizeSchedule,
    archiveSchedule,
    deleteSchedule,
    fetchTemplates,
    resolveConflict,
    exportToPDF,
    exportToExcel,
    saveScenario,
    clearError,
    clearData,
  };
});
