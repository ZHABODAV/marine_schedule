import apiClient, { ApiResponse, PaginatedResponse } from './api';
import type { Voyage, VoyageTemplate, Scenario } from '@/types/voyage.types';

export class VoyageService {
  private readonly baseUrl = '/voyages';

  /**
   * Get all voyages
   */
  async getAll(module?: string): Promise<Voyage[]> {
    const params = module ? { module } : {};
    const response = await apiClient.get<ApiResponse<Voyage[]>>(this.baseUrl, { params });
    return response.data.data;
  }

  /**
   * Get paginated voyages
   */
  async getPaginated(page: number = 1, perPage: number = 10, filters?: any): Promise<PaginatedResponse<Voyage>> {
    const response = await apiClient.get<PaginatedResponse<Voyage>>(this.baseUrl, {
      params: { page, per_page: perPage, ...filters },
    });
    return response.data;
  }

  /**
   * Get voyage by ID
   */
  async getById(id: string | number): Promise<Voyage> {
    const response = await apiClient.get<ApiResponse<Voyage>>(`${this.baseUrl}/${id}`);
    return response.data.data;
  }

  /**
   * Create a new voyage
   */
  async create(voyage: Partial<Voyage>): Promise<Voyage> {
    const response = await apiClient.post<ApiResponse<Voyage>>(this.baseUrl, voyage);
    return response.data.data;
  }

  /**
   * Update an existing voyage
   */
  async update(id: string | number, voyage: Partial<Voyage>): Promise<Voyage> {
    const response = await apiClient.put<ApiResponse<Voyage>>(`${this.baseUrl}/${id}`, voyage);
    return response.data.data;
  }

  /**
   * Delete a voyage
   */
  async delete(id: string | number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`);
  }

  /**
   * Calculate voyage
   */
  async calculate(voyageData: any): Promise<any> {
    const response = await apiClient.post<ApiResponse<any>>(`${this.baseUrl}/calculate`, voyageData);
    return response.data.data;
  }

  /**
   * Optimize voyage
   */
  async optimize(voyageId: string | number, options?: any): Promise<Voyage> {
    const response = await apiClient.post<ApiResponse<Voyage>>(`${this.baseUrl}/${voyageId}/optimize`, options);
    return response.data.data;
  }

  /**
   * Get voyage financials
   */
  async getFinancials(voyageId: string | number): Promise<any> {
    const response = await apiClient.get<ApiResponse<any>>(`${this.baseUrl}/${voyageId}/financials`);
    return response.data.data;
  }

  /**
   * Export voyage to file
   */
  async export(voyageId: string | number, format: 'pdf' | 'excel' = 'excel'): Promise<Blob> {
    const response = await apiClient.get(`${this.baseUrl}/${voyageId}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  }

  /**
   * Generate voyage schedule
   */
  async generateSchedule(params: any): Promise<any> {
    const response = await apiClient.post<ApiResponse<any>>(`${this.baseUrl}/generate-schedule`, params);
    return response.data.data;
  }
}

export class VoyageTemplateService {
  private readonly baseUrl = '/voyage-templates';

  /**
   * Get all voyage templates
   */
  async getAll(): Promise<VoyageTemplate[]> {
    const response = await apiClient.get<ApiResponse<VoyageTemplate[]>>(this.baseUrl);
    return response.data.data;
  }

  /**
   * Get template by ID
   */
  async getById(id: string | number): Promise<VoyageTemplate> {
    const response = await apiClient.get<ApiResponse<VoyageTemplate>>(`${this.baseUrl}/${id}`);
    return response.data.data;
  }

  /**
   * Create a new template
   */
  async create(template: Partial<VoyageTemplate>): Promise<VoyageTemplate> {
    const response = await apiClient.post<ApiResponse<VoyageTemplate>>(this.baseUrl, template);
    return response.data.data;
  }

  /**
   * Update an existing template
   */
  async update(id: string | number, template: Partial<VoyageTemplate>): Promise<VoyageTemplate> {
    const response = await apiClient.put<ApiResponse<VoyageTemplate>>(`${this.baseUrl}/${id}`, template);
    return response.data.data;
  }

  /**
   * Delete a template
   */
  async delete(id: string | number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`);
  }

  /**
   * Apply template to voyage
   */
  async apply(templateId: string | number, voyageData: any): Promise<Voyage> {
    const response = await apiClient.post<ApiResponse<Voyage>>(`${this.baseUrl}/${templateId}/apply`, voyageData);
    return response.data.data;
  }
}

export class ScenarioService {
  private readonly baseUrl = '/scenarios';

  /**
   * Get all scenarios
   */
  async getAll(): Promise<Scenario[]> {
    const response = await apiClient.get<ApiResponse<Scenario[]>>(this.baseUrl);
    return response.data.data;
  }

  /**
   * Get scenario by ID
   */
  async getById(id: string | number): Promise<Scenario> {
    const response = await apiClient.get<ApiResponse<Scenario>>(`${this.baseUrl}/${id}`);
    return response.data.data;
  }

  /**
   * Create a new scenario
   */
  async create(scenario: Partial<Scenario>): Promise<Scenario> {
    const response = await apiClient.post<ApiResponse<Scenario>>(this.baseUrl, scenario);
    return response.data.data;
  }

  /**
   * Update an existing scenario
   */
  async update(id: string | number, scenario: Partial<Scenario>): Promise<Scenario> {
    const response = await apiClient.put<ApiResponse<Scenario>>(`${this.baseUrl}/${id}`, scenario);
    return response.data.data;
  }

  /**
   * Delete a scenario
   */
  async delete(id: string | number): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`);
  }

  /**
   * Compare scenarios
   */
  async compare(scenarioIds: (string | number)[]): Promise<any> {
    const response = await apiClient.post<ApiResponse<any>>(`${this.baseUrl}/compare`, { scenario_ids: scenarioIds });
    return response.data.data;
  }
}

// Export singleton instances
export const voyageService = new VoyageService();
export const voyageTemplateService = new VoyageTemplateService();
export const scenarioService = new ScenarioService();
export default voyageService;
