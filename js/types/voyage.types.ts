/**
 * Voyage Type Definitions
 */

export interface VoyageLeg {
    id?: number;
    type: 'ballast' | 'loading' | 'transit' | 'discharge' | 'canal' | 'bunker' | 'waiting';
    from?: string;
    to?: string;
    port?: string;
    distance?: number;
    duration?: number;
    cargo?: number;
}

export interface Voyage {
    id: string;
    vesselId: string | null;
    commitmentId?: string;
    laneId?: string;
    templateId?: string;
    legs: VoyageLeg[];
    startDate?: string;
    status: 'planned' | 'active' | 'completed';
    createdAt?: string;
}

export interface VoyageTemplate {
    id: string;
    name: string;
    description?: string;
    category: string;
    ports: string[];
    estimatedDays: number;
    legs?: VoyageLeg[];
    costAllocations?: {
        operationalCost: number;
        overheadCost: number;
        otherCost: number;
    };
    createdAt?: string;
}

export interface Scenario {
    id: string;
    name: string;
    description?: string;
    voyages?: Voyage[];
    parameters?: Record<string, any>;
}

export interface RouteLeg {
    id: string;
    from: string;
    to: string;
    distance: number;
    canal?: string;
    waypoints?: string[];
}
