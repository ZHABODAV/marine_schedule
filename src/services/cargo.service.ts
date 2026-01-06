import apiClient, { ApiResponse, PaginatedResponse } from './api';
import type { CargoCommitment, CargoFormData } from '@/types/cargo.types';

export class CargoService {
  private readonly baseUrl = '/cargo';

  /**
   * Get all cargo commitments
   */
  async getAll(module?: string): Promise<CargoCommitment[]> {
    const params = module ? { module } : {};
    const response = await apiClient.get<ApiResponse<CargoCommitment[]>>(this.baseUrl, { params });
    return response.data.data;
  }

  /**
   * Get paginated cargo
   */
  async getPaginated(page: number = 1, perPage: number = 10, filters?: any): Promise<PaginatedResponse<CargoCommitment>> {
    const response = await apiClient.get<PaginatedResponse<CargoCommitment>>(this.baseUrl, {
      params: { page, per_page: perPage, ...filters },
    });
    return response.data;
  }

  /**
   * Get cargo by ID
   */
  async getById(id: string | number): Promise<CargoCommitment> {
    const response = await apiClient.get<ApiResponse<CargoCommitment>>(`${this.baseUrl}/${id}`);
    return response.data.data;
  }

  /**
   * Create a new cargo commitment
   */
  async create(cargo: CargoFormData): Promise<CargoCommitment> {
    const response = await apiClient.post<ApiResponse<CargoCommitment>>(this.baseUrl, cargo);
    return response.data.data;
  }

  /**
   * Update an existing cargo commitment
   */
  async update(id: string | number, cargo: Partial<CargoFormData>): Promise<CargoCommitment> {
    const response = await apiClient.put<ApiResponse<CargoCommitment>>(`${this.baseUrl}/${id}`, cargo);
    return response.data.data;
  }

  /**
   * Delete a cargo commitment
   */
  async delete(id: string | number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`);
  }

  /**
   * Get cargo by port
   */
  async getByPort(portId: string | number): Promise<CargoCommitment[]> {
    const response = await apiClient.get<ApiResponse<CargoCommitment[]>>(`${this.baseUrl}/port/${portId}`);
    return response.data.data;
  }

  /**
   * Get cargo statistics
   */
  async getStatistics(startDate?: string, endDate?: string, module?: string): Promise<any> {
    const params = { start_date: startDate, end_date: endDate, module };
    const response = await apiClient.get<ApiResponse<any>>(`${this.baseUrl}/statistics`, { params });
    return response.data.data;
  }

  /**
   * Import cargo from file
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
   * Export cargo to file
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
export const cargoService = new CargoService();
export default cargoService;
