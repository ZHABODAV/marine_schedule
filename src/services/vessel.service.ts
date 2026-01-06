import apiClient, { ApiResponse, PaginatedResponse } from './api';
import type { Vessel, VesselFormData } from '@/types/vessel.types';

export class VesselService {
  private readonly baseUrl = '/vessels';

  /**
   * Get all vessels
   */
  async getAll(module?: string): Promise<Vessel[]> {
    const params = module ? { module } : {};
    const response = await apiClient.get<ApiResponse<Vessel[]>>(this.baseUrl, { params });
    return response.data.data;
  }

  /**
   * Get paginated vessels
   */
  async getPaginated(page: number = 1, perPage: number = 10, filters?: any): Promise<PaginatedResponse<Vessel>> {
    const response = await apiClient.get<PaginatedResponse<Vessel>>(this.baseUrl, {
      params: { page, per_page: perPage, ...filters },
    });
    return response.data;
  }

  /**
   * Get vessel by ID
   */
  async getById(id: string | number): Promise<Vessel> {
    const response = await apiClient.get<ApiResponse<Vessel>>(`${this.baseUrl}/${id}`);
    return response.data.data;
  }

  /**
   * Create a new vessel
   */
  async create(vessel: VesselFormData): Promise<Vessel> {
    const response = await apiClient.post<ApiResponse<Vessel>>(this.baseUrl, vessel);
    return response.data.data;
  }

  /**
   * Update an existing vessel
   */
  async update(id: string | number, vessel: Partial<VesselFormData>): Promise<Vessel> {
    const response = await apiClient.put<ApiResponse<Vessel>>(`${this.baseUrl}/${id}`, vessel);
    return response.data.data;
  }

  /**
   * Delete a vessel
   */
  async delete(id: string | number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`);
  }

  /**
   * Get vessel positions
   */
  async getPositions(): Promise<any[]> {
    const response = await apiClient.get<ApiResponse<any[]>>(`${this.baseUrl}/positions`);
    return response.data.data;
  }

  /**
   * Get vessel schedule
   */
  async getSchedule(vesselId: string | number, startDate?: string, endDate?: string): Promise<any[]> {
    const params = { start_date: startDate, end_date: endDate };
    const response = await apiClient.get<ApiResponse<any[]>>(`${this.baseUrl}/${vesselId}/schedule`, { params });
    return response.data.data;
  }

  /**
   * Import vessels from file
   */
  async import(file: File): Promise<{ imported: number; errors?: string[] }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post<ApiResponse<{ imported: number; errors?: string[] }>>(
      `${this.baseUrl}/import`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.data;
  }

  /**
   * Export vessels to file
   */
  async export(format: 'csv' | 'excel' = 'excel'): Promise<Blob> {
    const response = await apiClient.get(`${this.baseUrl}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }
}

// Export singleton instance
export const vesselService = new VesselService();
export default vesselService;
