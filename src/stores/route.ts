import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { routeService, portService } from '@/services';
import { handleApiError } from '@/services/api';
import type { Route, Port } from '@/types/route.types';
import { useAppStore } from './app';

export const useRouteStore = defineStore('route', () => {
  // State
  const routes = ref<Route[]>([]);
  const ports = ref<Port[]>([]);
  const selectedRoute = ref<Route | null>(null);
  const selectedPort = ref<Port | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const totalRoutes = computed(() => routes.value.length);
  const totalPorts = computed(() => ports.value.length);
  const portsByCountry = computed(() => {
    const grouped: Record<string, Port[]> = {};
    ports.value.forEach(port => {
      const country = port.country || 'Unknown';
      if (!grouped[country]) grouped[country] = [];
      grouped[country].push(port);
    });
    return grouped;
  });

  // Actions
  async function fetchRoutes(module?: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      routes.value = await routeService.getAll(module);
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

  async function fetchPorts(module?: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      ports.value = await portService.getAll(module);
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

  async function fetchRouteById(id: string | number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      selectedRoute.value = await routeService.getById(id);
      return selectedRoute.value;
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

  async function fetchPortById(id: string | number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      selectedPort.value = await portService.getById(id);
      return selectedPort.value;
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

  async function createRoute(routeData: Partial<Route>) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const newRoute = await routeService.create(routeData);
      routes.value.push(newRoute);
      appStore.addNotification({
        type: 'success',
        message: 'Route created successfully',
      });
      return newRoute;
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

  async function updateRoute(id: string | number, updates: Partial<Route>) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      const updatedRoute = await routeService.update(id, updates);
      const index = routes.value.findIndex(r => r.id === id);
      if (index !== -1) {
        routes.value[index] = updatedRoute;
      }
      appStore.addNotification({
        type: 'success',
        message: 'Route updated successfully',
      });
      return updatedRoute;
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

  async function deleteRoute(id: string | number) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      await routeService.delete(id);
      const index = routes.value.findIndex(r => r.id === id);
      if (index !== -1) {
        routes.value.splice(index, 1);
      }
      appStore.addNotification({
        type: 'success',
        message: 'Route deleted successfully',
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

  async function calculateDistance(fromPort: string, toPort: string, viaCanals?: string[]) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      return await routeService.calculateDistance(fromPort, toPort, viaCanals);
    } catch (e: any) {
      error.value = handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message: error.value,
      });
      return 0;
    } finally {
      loading.value = false;
    }
  }

  async function getOptimalRoute(fromPort: string, toPort: string, vesselType?: string) {
    const appStore = useAppStore();
    loading.value = true;
    error.value = null;
    try {
      return await routeService.getOptimalRoute(fromPort, toPort, vesselType);
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
    routes.value = [];
    ports.value = [];
    selectedRoute.value = null;
    selectedPort.value = null;
  }

  return {
    // State
    routes,
    ports,
    selectedRoute,
    selectedPort,
    loading,
    error,
    // Getters
    totalRoutes,
    totalPorts,
    portsByCountry,
    // Actions
    fetchRoutes,
    fetchPorts,
    fetchRouteById,
    fetchPortById,
    createRoute,
    updateRoute,
    deleteRoute,
    calculateDistance,
    getOptimalRoute,
    clearError,
    clearData,
  };
});
