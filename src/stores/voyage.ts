import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { voyageService, voyageTemplateService, scenarioService } from '@/services';
import { handleApiError } from '@/services/api';
import type { Voyage, VoyageTemplate, Scenario } from '@/types/voyage.types';
import { useAppStore } from './app';

export const useVoyageStore = defineStore('voyage', () => {
  // State
  const voyages = ref<Voyage[]>([]);
  const templates = ref<VoyageTemplate[]>([]);
  const scenarios = ref<Scenario[]>([]);
  const selectedVoyage = ref<Voyage | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const totalVoyages = computed(() => voyages.value.length);
  const plannedVoyages = computed(() => 
    voyages.value.filter(v => v.status === 'planned')
  );
  const activeVoyages = computed(() => 
    voyages.value.filter(v => v.status === 'active')
  );
  const completedVoyages = computed(() => 
    voyages.value.filter(v => v.status === 'completed')
  );

  // Actions
  async function fetchVoyages(module?: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      voyages.value = await voyageService.getAll(module);
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

  async function fetchTemplates() {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      templates.value = await voyageTemplateService.getAll();
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

  async function fetchScenarios() {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      scenarios.value = await scenarioService.getAll();
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

  async function fetchVoyageById(id: string | number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      selectedVoyage.value = await voyageService.getById(id);
      return selectedVoyage.value;
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

  async function createVoyage(voyageData: Partial<Voyage>) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const newVoyage = await voyageService.create(voyageData);
      voyages.value.push(newVoyage);
      appStore.addNotification({
        type: 'success',
        message: 'Voyage created successfully',
      });
      return newVoyage;
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

  async function updateVoyage(id: string | number, updates: Partial<Voyage>) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const updatedVoyage = await voyageService.update(id, updates);
      const index = voyages.value.findIndex(v => v.id === id);
      if (index !== -1) {
        voyages.value[index] = updatedVoyage;
      }
      appStore.addNotification({
        type: 'success',
        message: 'Voyage updated successfully',
      });
      return updatedVoyage;
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

  async function deleteVoyage(id: string | number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      await voyageService.delete(id);
      const index = voyages.value.findIndex(v => v.id === id);
      if (index !== -1) {
        voyages.value.splice(index, 1);
      }
      appStore.addNotification({
        type: 'success',
        message: 'Voyage deleted successfully',
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

  async function calculateVoyage(voyageData: any) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const result = await voyageService.calculate(voyageData);
      appStore.addNotification({
        type: 'success',
        message: 'Voyage calculated successfully',
      });
      return result;
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

  async function optimizeVoyage(voyageId: string | number, options?: any) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const optimizedVoyage = await voyageService.optimize(voyageId, options);
      const index = voyages.value.findIndex(v => v.id === voyageId);
      if (index !== -1) {
        voyages.value[index] = optimizedVoyage;
      }
      appStore.addNotification({
        type: 'success',
        message: 'Voyage optimized successfully',
      });
      return optimizedVoyage;
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

  async function getVoyageFinancials(voyageId: string | number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      return await voyageService.getFinancials(voyageId);
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

  async function generateSchedule(params: any) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const result = await voyageService.generateSchedule(params);
      appStore.addNotification({
        type: 'success',
        message: 'Schedule generated successfully',
      });
      return result;
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
    voyages.value = [];
    templates.value = [];
    scenarios.value = [];
    selectedVoyage.value = null;
  }

  return {
    // State
    voyages,
    templates,
    scenarios,
    selectedVoyage,
    loading,
    error,
    // Getters
    totalVoyages,
    plannedVoyages,
    activeVoyages,
    completedVoyages,
    // Actions
    fetchVoyages,
    fetchTemplates,
    fetchScenarios,
    fetchVoyageById,
    createVoyage,
    updateVoyage,
    deleteVoyage,
    calculateVoyage,
    optimizeVoyage,
    getVoyageFinancials,
    generateSchedule,
    clearError,
    clearData,
  };
});
