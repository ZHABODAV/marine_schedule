/**
 * Application State Type Definitions
 * Extracted from vessel_scheduler_enhanced.js
 */

// Import types from other type files
import type { Vessel } from './vessel.types';
import type { CargoCommitment, RailCargo, CargoType } from './cargo.types';
import type { Voyage, VoyageLeg, VoyageTemplate, Scenario, RouteLeg } from './voyage.types';
import type { Route, Port, Movement } from './route.types';

export interface GanttColors {
    loading: string;
    discharge: string;
    sea_laden: string;
    sea_ballast: string;
    canal: string;
    bunker: string;
    waiting: string;
}

export interface AppConfig {
    gantt: {
        colors: GanttColors;
    };
}

export interface Masters {
    ports: Port[];
    routes: Route[];
    vessels: Vessel[];
    cargoTypes: CargoType[];
}

export interface Planning {
    commitments: CargoCommitment[];
    railCargo: RailCargo[];
    movements: Movement[];
    voyageLegs: VoyageLeg[];
}

export interface Computed {
    voyages: Voyage[];
    voyageTemplates: VoyageTemplate[];
    scenarios: Scenario[];
    schedule: Schedule | null;
    ganttData: GanttRow[];
    routeLegs: RouteLeg[];
}

export interface ModuleData {
    masters: Masters;
    planning: Planning;
    computed: Computed;
}

export interface Filters {
    module: string;
    dateStart: string | null;
    dateEnd: string | null;
    product: string | null;
    port: string | null;
    vesselId: string | null;
    opTypes: string[];
    selectedVoyages?: string[];
}

export interface CrossFilters {
    cargo: string | null;
    vessel: string | null;
    voyage: string | null;
    route: string | null;
}

export interface VoyageBuilderState {
    currentLegs: VoyageLeg[];
    lastValidation: ValidationResult | null;
}

export interface SalesPlan {
    targetShipments: number;
    periodStart: string | null;
    periodEnd: string | null;
}

export interface AppState {
    currentModule: 'deepsea' | 'balakovo' | 'olya';
    deepsea: ModuleData;
    balakovo: ModuleData;
    olya: ModuleData;
    filters: Filters;
    crossFilters: CrossFilters;
    voyageBuilder: VoyageBuilderState;
    portStocks: Record<string, PortStockDay[]>;
    salesPlan: SalesPlan;
    
    // Legacy getters (for backward compatibility)
    vessels: Vessel[];
    cargo: CargoCommitment[];
    routes: Route[];
    ports: Port[];
    schedule: Schedule | null;
    ganttData: GanttRow[];
}

export interface ValidationResult {
    valid: boolean;
    legs?: VoyageLeg[];
    errors?: string[];
}

export interface PortStockDay {
    date: string;
    railInflow: string;
    seaOutflow: string;
    stock: string;
}

export interface GanttRow {
    vessel: string;
    days: GanttDay[];
}

export interface GanttDay {
    operation: string;
    class: string;
}

export interface Schedule {
    type: string;
    generatedAt: string;
    summary: {
        totalVessels: number;
        totalCargo: number;
        totalDistance: number;
        estimatedDuration: number;
    };
    selectedVoyages?: string[];
}

// Re-export imported types for convenience
export type {
    Vessel,
    CargoCommitment,
    RailCargo,
    CargoType,
    Voyage,
    VoyageLeg,
    VoyageTemplate,
    Scenario,
    RouteLeg,
    Route,
    Port,
    Movement
};
