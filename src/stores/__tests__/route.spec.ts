import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useRouteStore } from '../route';
import type { Route, Port } from '@/types/route.types';

// Mock services
const mockRoutes: Route[] = [
  {
    id: '1',
    name: 'Route 1',
    from: 'Port A',
    to: 'Port B',
    distance: 1000,
  },
  {
    id: '2',
    name: 'Route 2',
    from: 'Port C',
    to: 'Port D',
    distance: 1500,
    canalTransit: true,
    canal: 'Suez',
  },
];

const mockPorts: Port[] = [
  {
    id: '1',
    name: 'Port A',
    country: 'Country 1',
    latitude: 0,
    longitude: 0,
  },
  {
    id: '2',
    name: 'Port B',
    country: 'Country 1',
    latitude: 0,
    longitude: 0,
  },
  {
    id: '3',
    name: 'Port C',
    country: 'Country 2',
    latitude: 0,
    longitude: 0,
  },
];

vi.mock('@/services', () => ({
  routeService: {
    getAll: vi.fn(() => Promise.resolve(mockRoutes)),
    getById: vi.fn((id: string) => Promise.resolve(mockRoutes.find(r => r.id === id))),
    create: vi.fn((data: Partial<Route>) => Promise.resolve({ ...data, id: '3' } as Route)),
    update: vi.fn((id: string, data: Partial<Route>) => Promise.resolve({ ...mockRoutes.find(r => r.id === id), ...data } as Route)),
    delete: vi.fn(() => Promise.resolve()),
    calculateDistance: vi.fn(() => Promise.resolve(1200)),
    getOptimalRoute: vi.fn(() => Promise.resolve(mockRoutes[0])),
  },
  portService: {
    getAll: vi.fn(() => Promise.resolve(mockPorts)),
    getById: vi.fn((id: string) => Promise.resolve(mockPorts.find(p => p.id === id))),
  },
}));

vi.mock('../app', () => ({
  useAppStore: vi.fn(() => ({
    addNotification: vi.fn(),
  })),
}));

describe('Route Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have empty routes array initially', () => {
      const store = useRouteStore();
      expect(store.routes).toEqual([]);
    });

    it('should have empty ports array initially', () => {
      const store = useRouteStore();
      expect(store.ports).toEqual([]);
    });

    it('should have no selected route initially', () => {
      const store = useRouteStore();
      expect(store.selectedRoute).toBeNull();
    });

    it('should have no selected port initially', () => {
      const store = useRouteStore();
      expect(store.selectedPort).toBeNull();
    });

    it('should not be loading initially', () => {
      const store = useRouteStore();
      expect(store.loading).toBe(false);
    });

    it('should have no error initially', () => {
      const store = useRouteStore();
      expect(store.error).toBeNull();
    });
  });

  describe('Getters', () => {
    it('should calculate total routes correctly', async () => {
      const store = useRouteStore();
      await store.fetchRoutes();
      
      expect(store.totalRoutes).toBe(2);
    });

    it('should calculate total ports correctly', async () => {
      const store = useRouteStore();
      await store.fetchPorts();
      
      expect(store.totalPorts).toBe(3);
    });

    it('should group ports by country', async () => {
      const store = useRouteStore();
      await store.fetchPorts();
      
      const grouped = store.portsByCountry;
      expect(grouped['Country 1']).toHaveLength(2);
      expect(grouped['Country 2']).toHaveLength(1);
    });

    it('should handle ports without country', async () => {
      const portsWithoutCountry = [
        { ...mockPorts[0], country: undefined },
      ];
      
      const { portService } = await import('@/services');
      vi.mocked(portService.getAll).mockResolvedValueOnce(portsWithoutCountry as any);
      
      const store = useRouteStore();
      await store.fetchPorts();
      
      expect(store.portsByCountry['Unknown']).toBeDefined();
    });
  });

  describe('Fetch Routes', () => {
    it('should fetch routes successfully', async () => {
      const store = useRouteStore();
      await store.fetchRoutes();
      
      expect(store.routes).toEqual(mockRoutes);
      expect(store.loading).toBe(false);
      expect(store.error).toBeNull();
    });

    it('should set loading state during fetch', async () => {
      const store = useRouteStore();
      const fetchPromise = store.fetchRoutes();
      
      expect(store.loading).toBe(true);
      await fetchPromise;
      expect(store.loading).toBe(false);
    });

    it('should handle fetch error', async () => {
      const { routeService } = await import('@/services');
      const errorMessage = 'Network error';
      vi.mocked(routeService.getAll).mockRejectedValueOnce(new Error(errorMessage));
      
      const store = useRouteStore();
      await store.fetchRoutes();
      
      expect(store.error).toBeTruthy();
      expect(store.loading).toBe(false);
    });

    it('should pass module parameter to service', async () => {
      const { routeService } = await import('@/services');
      const store = useRouteStore();
      
      await store.fetchRoutes('olya');
      
      expect(routeService.getAll).toHaveBeenCalledWith('olya');
    });
  });

  describe('Fetch Ports', () => {
    it('should fetch ports successfully', async () => {
      const store = useRouteStore();
      await store.fetchPorts();
      
      expect(store.ports).toEqual(mockPorts);
      expect(store.loading).toBe(false);
      expect(store.error).toBeNull();
    });

    it('should handle fetch ports error', async () => {
      const { portService } = await import('@/services');
      vi.mocked(portService.getAll).mockRejectedValueOnce(new Error('Error'));
      
      const store = useRouteStore();
      await store.fetchPorts();
      
      expect(store.error).toBeTruthy();
    });
  });

  describe('Fetch Route by ID', () => {
    it('should fetch route by id successfully', async () => {
      const store = useRouteStore();
      const result = await store.fetchRouteById('1');
      
      expect(result).toEqual(mockRoutes[0]);
      expect(store.selectedRoute).toEqual(mockRoutes[0]);
    });

    it('should return null on error', async () => {
      const { routeService } = await import('@/services');
      vi.mocked(routeService.getById).mockRejectedValueOnce(new Error('Not found'));
      
      const store = useRouteStore();
      const result = await store.fetchRouteById('999');
      
      expect(result).toBeNull();
      expect(store.error).toBeTruthy();
    });
  });

  describe('Fetch Port by ID', () => {
    it('should fetch port by id successfully', async () => {
      const store = useRouteStore();
      const result = await store.fetchPortById('1');
      
      expect(result).toEqual(mockPorts[0]);
      expect(store.selectedPort).toEqual(mockPorts[0]);
    });

    it('should return null on error', async () => {
      const { portService } = await import('@/services');
      vi.mocked(portService.getById).mockRejectedValueOnce(new Error('Not found'));
      
      const store = useRouteStore();
      const result = await store.fetchPortById('999');
      
      expect(result).toBeNull();
    });
  });

  describe('Create Route', () => {
    it('should create route successfully', async () => {
      const store = useRouteStore();
      const newRoute: Partial<Route> = {
        name: 'New Route',
        from: 'Port E',
        to: 'Port F',
        distance: 2000,
      };
      
      const result = await store.createRoute(newRoute);
      
      expect(result).toBeDefined();
      expect(result?.id).toBe('3');
      expect(store.routes).toHaveLength(1);
    });

    it('should return null on create error', async () => {
      const { routeService } = await import('@/services');
      vi.mocked(routeService.create).mockRejectedValueOnce(new Error('Create failed'));
      
      const store = useRouteStore();
      const result = await store.createRoute({});
      
      expect(result).toBeNull();
      expect(store.error).toBeTruthy();
    });
  });

  describe('Update Route', () => {
    it('should update route successfully', async () => {
      const store = useRouteStore();
      await store.fetchRoutes();
      
      const updates = { distance: 1100 };
      const result = await store.updateRoute('1', updates);
      
      expect(result).toBeDefined();
      expect(store.routes[0]?.distance).toBe(1100);
    });

    it('should return null on update error', async () => {
      const { routeService } = await import('@/services');
      vi.mocked(routeService.update).mockRejectedValueOnce(new Error('Update failed'));
      
      const store = useRouteStore();
      const result = await store.updateRoute('1', {});
      
      expect(result).toBeNull();
      expect(store.error).toBeTruthy();
    });
  });

  describe('Delete Route', () => {
    it('should delete route successfully', async () => {
      const store = useRouteStore();
      await store.fetchRoutes();
      
      const initialLength = store.routes.length;
      const result = await store.deleteRoute('1');
      
      expect(result).toBe(true);
      expect(store.routes).toHaveLength(initialLength - 1);
    });

    it('should return false on delete error', async () => {
      const { routeService } = await import('@/services');
      vi.mocked(routeService.delete).mockRejectedValueOnce(new Error('Delete failed'));
      
      const store = useRouteStore();
      const result = await store.deleteRoute('1');
      
      expect(result).toBe(false);
      expect(store.error).toBeTruthy();
    });
  });

  describe('Calculate Distance', () => {
    it('should calculate distance successfully', async () => {
      const store = useRouteStore();
      const distance = await store.calculateDistance('Port A', 'Port B');
      
      expect(distance).toBe(1200);
    });

    it('should return 0 on calculation error', async () => {
      const { routeService } = await import('@/services');
      vi.mocked(routeService.calculateDistance).mockRejectedValueOnce(new Error('Calc failed'));
      
      const store = useRouteStore();
      const distance = await store.calculateDistance('Port A', 'Port B');
      
      expect(distance).toBe(0);
      expect(store.error).toBeTruthy();
    });

    it('should pass canal parameters', async () => {
      const { routeService } = await import('@/services');
      const store = useRouteStore();
      
      await store.calculateDistance('Port A', 'Port B', ['Suez', 'Panama']);
      
      expect(routeService.calculateDistance).toHaveBeenCalledWith(
        'Port A',
        'Port B',
        ['Suez', 'Panama']
      );
    });
  });

  describe('Get Optimal Route', () => {
    it('should get optimal route successfully', async () => {
      const store = useRouteStore();
      const route = await store.getOptimalRoute('Port A', 'Port B');
      
      expect(route).toEqual(mockRoutes[0]);
    });

    it('should return null on error', async () => {
      const { routeService } = await import('@/services');
      vi.mocked(routeService.getOptimalRoute).mockRejectedValueOnce(new Error('Error'));
      
      const store = useRouteStore();
      const route = await store.getOptimalRoute('Port A', 'Port B');
      
      expect(route).toBeNull();
    });

    it('should pass vessel type parameter', async () => {
      const { routeService } = await import('@/services');
      const store = useRouteStore();
      
      await store.getOptimalRoute('Port A', 'Port B', 'tanker');
      
      expect(routeService.getOptimalRoute).toHaveBeenCalledWith(
        'Port A',
        'Port B',
        'tanker'
      );
    });
  });

  describe('Clear Error', () => {
    it('should clear error state', async () => {
      const { routeService } = await import('@/services');
      vi.mocked(routeService.getAll).mockRejectedValueOnce(new Error('Error'));
      
      const store = useRouteStore();
      await store.fetchRoutes();
      expect(store.error).toBeTruthy();
      
      store.clearError();
      expect(store.error).toBeNull();
    });
  });

  describe('Clear Data', () => {
    it('should clear all data', async () => {
      const store = useRouteStore();
      await store.fetchRoutes();
      await store.fetchPorts();
      await store.fetchRouteById('1');
      await store.fetchPortById('1');
      
      store.clearData();
      
      expect(store.routes).toEqual([]);
      expect(store.ports).toEqual([]);
      expect(store.selectedRoute).toBeNull();
      expect(store.selectedPort).toBeNull();
    });
  });
});
