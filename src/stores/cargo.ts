import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { cargoService } from '@/services';
import { handleApiError } from '@/services/api';
import type { CargoCommitment, CargoFormData } from '@/types/cargo.types';
import { useAppStore } from './app';

export const useCargoStore = defineStore('cargo', () => {
  // State
  const cargoList = ref<CargoCommitment[]>([]);
  const templates = ref<any[]>([]);
  const selectedCargo = ref<CargoCommitment | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const totalCargo = computed(() => cargoList.value.length);
  const pendingCargo = computed(() => 
    cargoList.value.filter(c => c.status === 'Pending')
  );
  const assignedCargo = computed(() => 
    cargoList.value.filter(c => c.status === 'Assigned')
  );
  const completedCargo = computed(() => 
    cargoList.value.filter(c => c.status === 'Completed')
  );
  const totalQuantity = computed(() =>
    cargoList.value.reduce((sum, c) => sum + c.quantity, 0)
  );
  const totalOperationalCost = computed(() =>
    cargoList.value.reduce((sum, c) => sum + (c.operationalCost || 0), 0)
  );
  const totalOverheadCost = computed(() =>
    cargoList.value.reduce((sum, c) => sum + (c.overheadCost || 0), 0)
  );
  const totalOtherCost = computed(() =>
    cargoList.value.reduce((sum, c) => sum + (c.otherCost || 0), 0)
  );
  const totalAllCosts = computed(() =>
    totalOperationalCost.value + totalOverheadCost.value + totalOtherCost.value
  );

  // Actions
  async function fetchCargo(module?: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      cargoList.value = await cargoService.getAll(module);
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

  async function fetchCargoById(id: string | number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      selectedCargo.value = await cargoService.getById(id);
      return selectedCargo.value;
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

  async function createCargo(cargoData: CargoFormData) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const newCargo = await cargoService.create(cargoData);
      cargoList.value.push(newCargo);
      appStore.addNotification({
        type: 'success',
        message: 'Cargo commitment created successfully',
      });
      return newCargo;
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

  async function updateCargo(id: string | number, updates: Partial<CargoFormData>) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const updatedCargo = await cargoService.update(id, updates);
      const index = cargoList.value.findIndex(c => c.id === id);
      if (index !== -1) {
        cargoList.value[index] = updatedCargo;
      }
      appStore.addNotification({
        type: 'success',
        message: 'Cargo commitment updated successfully',
      });
      return updatedCargo;
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

  async function deleteCargo(id: string | number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      await cargoService.delete(id);
      const index = cargoList.value.findIndex(c => c.id === id);
      if (index !== -1) {
        cargoList.value.splice(index, 1);
      }
      appStore.addNotification({
        type: 'success',
        message: 'Cargo commitment deleted successfully',
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

  async function getCargoStatistics(startDate?: string, endDate?: string, module?: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      return await cargoService.getStatistics(startDate, endDate, module);
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

  // Template Actions
  async function fetchTemplates() {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('/api/voyage-templates');
      if (!response.ok) throw new Error('Failed to fetch templates');
      const data = await response.json();
      templates.value = data.templates || [];
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

  async function createTemplate(templateData: any) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('/api/voyage-templates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(templateData),
      });
      if (!response.ok) throw new Error('Failed to create template');
      
      await fetchTemplates(); // Refresh list
      
      appStore.addNotification({
        type: 'success',
        message: 'Template created successfully',
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

  async function updateTemplate(id: string, templateData: any) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/voyage-templates/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(templateData),
      });
      if (!response.ok) throw new Error('Failed to update template');
      
      await fetchTemplates(); // Refresh list
      
      appStore.addNotification({
        type: 'success',
        message: 'Template updated successfully',
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

  async function deleteTemplate(id: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch(`/api/voyage-templates/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete template');
      
      templates.value = templates.value.filter(t => t.id !== id);
      
      appStore.addNotification({
        type: 'success',
        message: 'Template deleted successfully',
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

  function clearError() {
    error.value = null;
  }

  function clearCargo() {
    cargoList.value = [];
    selectedCargo.value = null;
  }

  return {
    // State
    cargoList,
    templates,
    selectedCargo,
    loading,
    error,
    // Getters
    totalCargo,
    pendingCargo,
    assignedCargo,
    completedCargo,
    totalQuantity,
    totalOperationalCost,
    totalOverheadCost,
    totalOtherCost,
    totalAllCosts,
    // Actions
    fetchCargo,
    fetchCargoById,
    createCargo,
    updateCargo,
    deleteCargo,
    getCargoStatistics,
    fetchTemplates,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    clearError,
    clearCargo,
  };
});
