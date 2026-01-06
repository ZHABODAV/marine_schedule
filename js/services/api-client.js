/**
 * API Client Service
 * Centralized service for making HTTP requests to the backend API
 * with built-in validation, error handling, and authentication
 */

class APIClient {
    constructor(baseURL = 'http://localhost:5000', validator = null) {
        this.baseURL = baseURL;
        this.validator = validator;
        this.token = this.getStoredToken();
        this.requestInterceptors = [];
        this.responseInterceptors = [];
    }

    /**
     * Get stored authentication token
     * @returns {string|null}
     */
    getStoredToken() {
        return localStorage.getItem('auth_token');
    }

    /**
     * Set authentication token
     * @param {string} token
     */
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('auth_token', token);
        } else {
            localStorage.removeItem('auth_token');
        }
    }

    /**
     * Get default headers
     * @returns {object}
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    /**
     * Add request interceptor
     * @param {function} interceptor
     */
    addRequestInterceptor(interceptor) {
        this.requestInterceptors.push(interceptor);
    }

    /**
     * Add response interceptor
     * @param {function} interceptor
     */
    addResponseInterceptor(interceptor) {
        this.responseInterceptors.push(interceptor);
    }

    /**
     * Apply request interceptors
     * @param {object} config
     * @returns {object}
     */
    applyRequestInterceptors(config) {
        let modifiedConfig = { ...config };
        for (const interceptor of this.requestInterceptors) {
            modifiedConfig = interceptor(modifiedConfig);
        }
        return modifiedConfig;
    }

    /**
     * Apply response interceptors
     * @param {Response} response
     * @returns {Response}
     */
    async applyResponseInterceptors(response) {
        let modifiedResponse = response;
        for (const interceptor of this.responseInterceptors) {
            modifiedResponse = await interceptor(modifiedResponse);
        }
        return modifiedResponse;
    }

    /**
     * Make HTTP request
     * @param {string} method - HTTP method
     * @param {string} endpoint - API endpoint
     * @param {object} data - Request data
     * @param {object} options - Additional options
     * @returns {Promise<object>}
     */
    async request(method, endpoint, data = null, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        let config = {
            method: method.toUpperCase(),
            headers: { ...this.getHeaders(), ...options.headers },
            ...options
        };

        // Add body for non-GET requests
        if (data && method.toUpperCase() !== 'GET') {
            config.body = JSON.stringify(data);
        }

        // Apply request interceptors
        config = this.applyRequestInterceptors(config);

        try {
            let response = await fetch(url, config);
            
            // Apply response interceptors
            response = await this.applyResponseInterceptors(response);

            // Handle response
            if (!response.ok) {
                return this.handleErrorResponse(response);
            }

            // Check if response has content
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const result = await response.json();
                return { success: true, data: result, status: response.status };
            }

            // For non-JSON responses (like file downloads)
            return { success: true, response: response, status: response.status };

        } catch (error) {
            console.error('API Request Error:', error);
            return {
                success: false,
                error: error.message || 'Network error occurred',
                status: 0
            };
        }
    }

    /**
     * Handle error response
     * @param {Response} response
     * @returns {Promise<object>}
     */
    async handleErrorResponse(response) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        let errorDetails = null;

        try {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                errorMessage = errorData.error || errorData.message || errorMessage;
                errorDetails = errorData.details || null;
            }
        } catch (e) {
            // Unable to parse error response
        }

        // Handle 401 Unauthorized
        if (response.status === 401) {
            this.setToken(null);
            this.onUnauthorized();
        }

        return {
            success: false,
            error: errorMessage,
            details: errorDetails,
            status: response.status
        };
    }

    /**
     * Override this method to handle unauthorized access
     */
    onUnauthorized() {
        console.warn('Unauthorized access. Token cleared.');
        // Optionally redirect to login page
        // window.location.href = '/login';
    }

    /**
     * Validate data before making request
     * @param {string} entityType
     * @param {object} data
     * @returns {object}
     */
    validateData(entityType, data) {
        if (this.validator) {
            return this.validator.validate(entityType, data);
        }
        return { valid: true, errors: [] };
    }

    // ==================== AUTH ENDPOINTS ====================

    /**
     * Login
     * @param {string} username
     * @param {string} password
     * @returns {Promise<object>}
     */
    async login(username, password) {
        const result = await this.request('POST', '/api/auth/login', {
            username,
            password
        });

        if (result.success && result.data.token) {
            this.setToken(result.data.token);
        }

        return result;
    }

    /**
     * Logout
     * @returns {Promise<object>}
     */
    async logout() {
        const result = await this.request('POST', '/api/auth/logout');
        this.setToken(null);
        return result;
    }

    /**
     * Get current user
     * @returns {Promise<object>}
     */
    async getCurrentUser() {
        return this.request('GET', '/api/auth/me');
    }

    // ==================== HEALTH ENDPOINTS ====================

    /**
     * Health check
     * @returns {Promise<object>}
     */
    async healthCheck() {
        return this.request('GET', '/api/health');
    }

    // ==================== VESSEL ENDPOINTS ====================

    /**
     * Get all vessels
     * @param {object} filters - Query parameters
     * @returns {Promise<object>}
     */
    async getVessels(filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const endpoint = `/api/vessels${queryString ? '?' + queryString : ''}`;
        return this.request('GET', endpoint);
    }

    /**
     * Get single vessel
     * @param {string} vesselId
     * @returns {Promise<object>}
     */
    async getVessel(vesselId) {
        return this.request('GET', `/api/vessels/${vesselId}`);
    }

    /**
     * Create vessel
     * @param {object} vesselData
     * @returns {Promise<object>}
     */
    async createVessel(vesselData) {
        const validation = this.validateData('vessel', vesselData);
        if (!validation.valid) {
            return {
                success: false,
                error: 'Validation failed',
                errors: validation.errors
            };
        }

        return this.request('POST', '/api/vessels', vesselData);
    }

    /**
     * Update vessel
     * @param {string} vesselId
     * @param {object} vesselData
     * @returns {Promise<object>}
     */
    async updateVessel(vesselId, vesselData) {
        return this.request('PUT', `/api/vessels/${vesselId}`, vesselData);
    }

    /**
     * Delete vessel
     * @param {string} vesselId
     * @returns {Promise<object>}
     */
    async deleteVessel(vesselId) {
        return this.request('DELETE', `/api/vessels/${vesselId}`);
    }

    // ==================== CARGO ENDPOINTS ====================

    /**
     * Get all cargo
     * @param {object} filters - Query parameters
     * @returns {Promise<object>}
     */
    async getCargo(filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const endpoint = `/api/cargo${queryString ? '?' + queryString : ''}`;
        return this.request('GET', endpoint);
    }

    /**
     * Create cargo
     * @param {object} cargoData
     * @returns {Promise<object>}
     */
    async createCargo(cargoData) {
        const validation = this.validateData('cargo', cargoData);
        if (!validation.valid) {
            return {
                success: false,
                error: 'Validation failed',
                errors: validation.errors
            };
        }

        return this.request('POST', '/api/cargo', cargoData);
    }

    /**
     * Update cargo
     * @param {string} cargoId
     * @param {object} cargoData
     * @returns {Promise<object>}
     */
    async updateCargo(cargoId, cargoData) {
        return this.request('PUT', `/api/cargo/${cargoId}`, cargoData);
    }

    /**
     * Delete cargo
     * @param {string} cargoId
     * @returns {Promise<object>}
     */
    async deleteCargo(cargoId) {
        return this.request('DELETE', `/api/cargo/${cargoId}`);
    }

    // ==================== ROUTE ENDPOINTS ====================

    /**
     * Get all routes
     * @returns {Promise<object>}
     */
    async getRoutes() {
        return this.request('GET', '/api/routes');
    }

    /**
     * Create route
     * @param {object} routeData
     * @returns {Promise<object>}
     */
    async createRoute(routeData) {
        const validation = this.validateData('route', routeData);
        if (!validation.valid) {
            return {
                success: false,
                error: 'Validation failed',
                errors: validation.errors
            };
        }

        return this.request('POST', '/api/routes', routeData);
    }

    // ==================== PORT ENDPOINTS ====================

    /**
     * Get all ports
     * @returns {Promise<object>}
     */
    async getPorts() {
        return this.request('GET', '/api/ports');
    }

    // ==================== SCHEDULE ENDPOINTS ====================

    /**
     * Generate schedule
     * @param {object} scheduleConfig
     * @returns {Promise<object>}
     */
    async generateSchedule(scheduleConfig) {
        return this.request('POST', '/api/schedule/generate', scheduleConfig);
    }

    /**
     * Get schedule
     * @param {string} type - Schedule type (deepsea, olya, balakovo)
     * @param {object} filters - Query parameters
     * @returns {Promise<object>}
     */
    async getSchedule(type, filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const endpoint = `/api/schedule/${type}${queryString ? '?' + queryString : ''}`;
        return this.request('GET', endpoint);
    }

    // ==================== VOYAGE ENDPOINTS ====================

    /**
     * Calculate voyage
     * @param {object} voyageData
     * @returns {Promise<object>}
     */
    async calculateVoyage(voyageData) {
        const validation = this.validateData('voyage', voyageData);
        if (!validation.valid) {
            return {
                success: false,
                error: 'Validation failed',
                errors: validation.errors
            };
        }

        return this.request('POST', '/api/voyage/calculate', voyageData);
    }

    // ==================== EXPORT ENDPOINTS ====================

    /**
     * Export Gantt chart
     * @param {object} exportConfig
     * @returns {Promise<object>}
     */
    async exportGantt(exportConfig) {
        return this.request('POST', '/api/export/gantt', exportConfig);
    }

    /**
     * Export fleet overview
     * @param {object} exportConfig
     * @returns {Promise<object>}
     */
    async exportFleetOverview(exportConfig) {
        return this.request('POST', '/api/export/fleet-overview', exportConfig);
    }

    /**
     * Export voyage summary
     * @param {object} exportConfig
     * @returns {Promise<object>}
     */
    async exportVoyageSummary(exportConfig) {
        return this.request('POST', '/api/export/voyage-summary', exportConfig);
    }

    // ==================== BUNKER ENDPOINTS ====================

    /**
     * Optimize bunker plan
     * @param {object} bunkerConfig
     * @returns {Promise<object>}
     */
    async optimizeBunker(bunkerConfig) {
        return this.request('POST', '/api/bunker/optimize', bunkerConfig);
    }

    /**
     * Get bunker prices
     * @param {object} filters
     * @returns {Promise<object>}
     */
    async getBunkerPrices(filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const endpoint = `/api/bunker/prices${queryString ? '?' + queryString : ''}`;
        return this.request('GET', endpoint);
    }

    /**
     * Get bunker market analysis
     * @returns {Promise<object>}
     */
    async getBunkerMarketAnalysis() {
        return this.request('GET', '/api/bunker/market-analysis');
    }

    // ==================== REPORT ENDPOINTS ====================

    /**
     * Generate vessel schedule PDF
     * @param {object} reportConfig
     * @returns {Promise<object>}
     */
    async generateVesselSchedulePDF(reportConfig) {
        return this.request('POST', '/api/reports/pdf/vessel-schedule', reportConfig);
    }

    /**
     * Generate fleet overview PDF
     * @param {object} reportConfig
     * @returns {Promise<object>}
     */
    async generateFleetOverviewPDF(reportConfig) {
        return this.request('POST', '/api/reports/pdf/fleet-overview', reportConfig);
    }

    /**
     * Generate berth utilization PDF
     * @param {object} reportConfig
     * @returns {Promise<object>}
     */
    async generateBerthUtilizationPDF(reportConfig) {
        return this.request('POST', '/api/reports/pdf/berth-utilization', reportConfig);
    }

    // ==================== FILE UPLOAD ENDPOINTS ====================

    /**
     * Upload CSV file
     * @param {File} file
     * @param {string} type
     * @param {string} module
     * @returns {Promise<object>}
     */
    async uploadCSV(file, type, module) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);
        formData.append('module', module);

        const headers = this.getHeaders();
        delete headers['Content-Type']; // Let browser set multipart boundary

        return this.request('POST', '/api/upload/csv', null, {
            body: formData,
            headers
        });
    }

    /**
     * Upload Excel file
     * @param {File} file
     * @param {string} type
     * @param {string} sheet
     * @returns {Promise<object>}
     */
    async uploadExcel(file, type, sheet = null) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);
        if (sheet) {
            formData.append('sheet', sheet);
        }

        const headers = this.getHeaders();
        delete headers['Content-Type'];

        return this.request('POST', '/api/upload/excel', null, {
            body: formData,
            headers
        });
    }

    // ==================== STATISTICS ENDPOINTS ====================

    /**
     * Get dashboard statistics
     * @param {object} filters
     * @returns {Promise<object>}
     */
    async getDashboardStats(filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const endpoint = `/api/dashboard/stats${queryString ? '?' + queryString : ''}`;
        return this.request('GET', endpoint);
    }

    /**
     * Get berth utilization
     * @param {object} filters
     * @returns {Promise<object>}
     */
    async getBerthUtilization(filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const endpoint = `/api/berths/utilization${queryString ? '?' + queryString : ''}`;
        return this.request('GET', endpoint);
    }

    // ==================== CALENDAR EVENTS ====================

    /**
     * Get calendar events from all modules
     * @param {object} filters - Query parameters
     * @returns {Promise<object>}
     */
    async getCalendarEvents(filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const endpoint = `/api/calendar/events${queryString ? '?' + queryString : ''}`;
        return this.request('GET', endpoint);
    }

    // ==================== BERTH CONSTRAINTS ====================

    /**
     * Create berth constraint
     * @param {object} constraintData
     * @returns {Promise<object>}
     */
    async createBerthConstraint(constraintData) {
        const validation = this.validateData('berthConstraint', constraintData);
        if (!validation.valid) {
            return {
                success: false,
                error: 'Validation failed',
                errors: validation.errors
            };
        }

        return this.request('POST', '/api/berths/constraints', constraintData);
    }

    /**
     * Get berth constraints
     * @param {object} filters
     * @returns {Promise<object>}
     */
    async getBerthConstraints(filters = {}) {
        const queryString = new URLSearchParams(filters).toString();
        const endpoint = `/api/berths/constraints${queryString ? '?' + queryString : ''}`;
        return this.request('GET', endpoint);
    }
}

// Create global API client instance
let apiClient;

// Initialize with validator if available
if (typeof apiValidator !== 'undefined') {
    apiClient = new APIClient('http://localhost:5000', apiValidator);
} else {
    apiClient = new APIClient('http://localhost:5000');
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, apiClient };
}

console.log(' API Client service loaded successfully');
