import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { vesselService } from '@/services';
import { handleApiError } from '@/services/api';
import type { Vessel, VesselFormData } from '@/types/vessel.types';
import { useAppStore } from './app';

export const useVesselStore = defineStore('vessel', () => {
  // State
  const vessels = ref<Vessel[]>([]);
  const selectedVessel = ref<Vessel | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters (computed)
  const totalVessels = computed(() => vessels.value.length);
  const activeVessels = computed(() =>
    vessels.value.filter(v => v.status === 'active')
  );
  const activeVoyages = computed(() => vessels.value.filter(v => v.status === 'active').length);
  const totalPorts = computed(() => {
    const ports = new Set<string>();
    vessels.value.forEach(v => {
      if (v.currentPort) ports.add(v.currentPort);
    });
    return ports.size;
  });
  const vesselsByType = computed(() => {
    const grouped: Record<string, Vessel[]> = {};
    vessels.value.forEach(vessel => {
      const type = vessel.class || 'unknown';  // Use 'class' property as type
      if (!grouped[type]) grouped[type] = [];
      grouped[type].push(vessel);
    });
    return grouped;
  });

  // Actions
  async function fetchVessels(module?: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      vessels.value = await vesselService.getAll(module);
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

  async function fetchVesselById(id: string | number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      selectedVessel.value = await vesselService.getById(id);
      return selectedVessel.value;
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

  async function createVessel(vesselData: VesselFormData) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const newVessel = await vesselService.create(vesselData);
      vessels.value.push(newVessel);
      appStore.addNotification({
        type: 'success',
        message: `Vessel "${newVessel.name}" created successfully`,
      });
      return newVessel;
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

  async function updateVessel(id: string | number, updates: Partial<VesselFormData>) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const updatedVessel = await vesselService.update(id, updates);
      const index = vessels.value.findIndex(v => v.id === id);
      if (index !== -1) {
        vessels.value[index] = updatedVessel;
      }
      appStore.addNotification({
        type: 'success',
        message: `Vessel updated successfully`,
      });
      return updatedVessel;
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

  async function deleteVessel(id: string | number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      await vesselService.delete(id);
      const index = vessels.value.findIndex(v => v.id === id);
      if (index !== -1) {
        vessels.value.splice(index, 1);
      }
      appStore.addNotification({
        type: 'success',
        message: 'Vessel deleted successfully',
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

  async function getVesselSchedule(vesselId: string | number, startDate?: string, endDate?: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      return await vesselService.getSchedule(vesselId, startDate, endDate);
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return [];
    } finally {
      loading.value = false;
    }
  }

  function clearError() {
    error.value = null;
  }

  function clearVessels() {
    vessels.value = [];
    selectedVessel.value = null;
  }

  return {
    // State
    vessels,
    selectedVessel,
    loading,
    error,
    // Getters
    totalVessels,
    activeVessels,
    activeVoyages,
    totalPorts,
    vesselsByType,
    // Actions
    fetchVessels,
    fetchVesselById,
    createVessel,
    updateVessel,
    deleteVessel,
    getVesselSchedule,
    clearError,
    clearVessels,
  };
});
