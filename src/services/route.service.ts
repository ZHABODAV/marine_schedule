import apiClient, { ApiResponse, PaginatedResponse } from './api';
import type { Route, Port } from '@/types/route.types';

export class RouteService {
  private readonly baseUrl = '/routes';

  /**
   * Get all routes
   */
  async getAll(module?: string): Promise<Route[]> {
    const params = module ? { module } : {};
    const response = await apiClient.get<ApiResponse<Route[]>>(this.baseUrl, { params });
    return response.data.data;
  }

  /**
   * Get paginated routes
   */
  async getPaginated(page: number = 1, perPage: number = 10, filters?: any): Promise<PaginatedResponse<Route>> {
    const response = await apiClient.get<PaginatedResponse<Route>>(this.baseUrl, {
      params: { page, per_page: perPage, ...filters },
    });
    return response.data;
  }

  /**
   * Get route by ID
   */
  async getById(id: string | number): Promise<Route> {
    const response = await apiClient.get<ApiResponse<Route>>(`${this.baseUrl}/${id}`);
    return response.data.data;
  }

  /**
   * Create a new route
   */
  async create(route: Partial<Route>): Promise<Route> {
    const response = await apiClient.post<ApiResponse<Route>>(this.baseUrl, route);
    return response.data.data;
  }

  /**
   * Update an existing route
   */
  async update(id: string | number, route: Partial<Route>): Promise<Route> {
    const response = await apiClient.put<ApiResponse<Route>>(`${this.baseUrl}/${id}`, route);
    return response.data.data;
  }

  /**
   * Delete a route
   */
  async delete(id: string | number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`);
  }

  /**
   * Calculate route distance
   */
  async calculateDistance(fromPort: string, toPort: string, viaCanals?: string[]): Promise<number> {
    const response = await apiClient.post<ApiResponse<{ distance: number }>>(`${this.baseUrl}/calculate-distance`, {
      from_port: fromPort,
      to_port: toPort,
      via_canals: viaCanals,
    });
    return response.data.data.distance;
  }

  /**
   * Get optimal route
   */
  async getOptimalRoute(fromPort: string, toPort: string, vesselType?: string): Promise<Route> {
    const response = await apiClient.get<ApiResponse<Route>>(`${this.baseUrl}/optimal`, {
      params: { from_port: fromPort, to_port: toPort, vessel_type: vesselType },
    });
    return response.data.data;
  }
}

export class PortService {
  private readonly baseUrl = '/ports';

  /**
   * Get all ports
   */
  async getAll(module?: string): Promise<Port[]> {
    const params = module ? { module } : {};
    const response = await apiClient.get<ApiResponse<Port[]>>(this.baseUrl, { params });
    return response.data.data;
  }

  /**
   * Get port by ID
   */
  async getById(id: string | number): Promise<Port> {
    const response = await apiClient.get<ApiResponse<Port>>(`${this.baseUrl}/${id}`);
    return response.data.data;
  }

  /**
   * Create a new port
   */
  async create(port: Partial<Port>): Promise<Port> {
    const response = await apiClient.post<ApiResponse<Port>>(this.baseUrl, port);
    return response.data.data;
  }

  /**
   * Update an existing port
   */
  async update(id: string | number, port: Partial<Port>): Promise<Port> {
    const response = await apiClient.put<ApiResponse<Port>>(`${this.baseUrl}/${id}`, port);
    return response.data.data;
  }

  /**
   * Delete a port
   */
  async delete(id: string | number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`);
  }

  /**
   * Get port schedule
   */
  async getSchedule(portId: string | number, startDate?: string, endDate?: string): Promise<any[]> {
    const params = { start_date: startDate, end_date: endDate };
    const response = await apiClient.get<ApiResponse<any[]>>(`${this.baseUrl}/${portId}/schedule`, { params });
    return response.data.data;
  }

  /**
   * Get berth availability
   */
  async getBerthAvailability(portId: string | number, date?: string): Promise<any[]> {
    const params = date ? { date } : {};
    const response = await apiClient.get<ApiResponse<any[]>>(`${this.baseUrl}/${portId}/berths`, { params });
    return response.data.data;
  }
}

// Export singleton instances
export const routeService = new RouteService();
export const portService = new PortService();
export default routeService;
