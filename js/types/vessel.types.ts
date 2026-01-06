/**
 * Vessel Type Definitions
 */

export interface Vessel {
    id: string;
    name: string;
    class: string;
    dwt: number;
    capacity?: number;
    speed: number;
    dailyHire?: number;
    contractType?: string;
    status: 'Active' | 'Pending' | 'Inactive';
}

export interface VesselFormData {
    id: string;
    name: string;
    class: string;
    dwt: number;
    speed: number;
}

export interface VesselDashboardFilter {
    status?: string;
    searchTerm?: string;
}
