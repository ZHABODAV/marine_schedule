/**
 * Year Schedule Generator Type Definitions
 * For annual planning and resource allocation
 */

import type { Module } from './calendar.types';

export type OptimizationGoal = 'maximize-revenue' | 'minimize-cost' | 'balance-utilization';

export interface VesselAllocation {
  vesselId: string;
  vesselName: string;
  allocatedDays: number;
  utilizationRate: number; // 0-100%
  assignedVoyages: string[]; // Voyage IDs
}

export interface ResourceAllocation {
  month: number; // 1-12
  year: number;
  vessels: VesselAllocation[];
  totalVoyages: number;
  totalCargo: number;
  totalRevenue: number;
  totalCost: number;
}

export interface ScheduleConflict {
  id: string;
  type: 'vessel-overlap' | 'port-capacity' | 'cargo-timing' | 'resource-shortage';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affectedEntities: string[]; // Vessel IDs, Port IDs, etc.
  suggestedResolution?: string;
}

export interface YearScheduleConfig {
  year: number;
  module: Exclude<Module, 'all'>;
  vessels: string[]; // Vessel IDs to include
  optimizationGoal: OptimizationGoal;
  loadCargoCommitments: boolean;
  useTemplates: boolean;
  selectedTemplateIds?: string[];
}

export interface YearSchedule {
  id: string;
  name: string;
  config: YearScheduleConfig;
  monthlyAllocations: ResourceAllocation[];
  conflicts: ScheduleConflict[];
  statistics: {
    totalVoyages: number;
    totalCargo: number;
    totalRevenue: number;
    totalCost: number;
    netProfit: number;
    averageUtilization: number;
  };
  createdAt: string;
  updatedAt: string;
  status: 'draft' | 'finalized' | 'archived';
}

export interface ScheduleTemplate {
  id: string;
  name: string;
  description?: string;
  module: Exclude<Module, 'all'>;
  pattern: 'weekly' | 'bi-weekly' | 'monthly' | 'custom';
  estimatedDays: number;
  ports: string[];
  cargoTypes: string[];
}

export interface ScheduleState {
  currentSchedule: YearSchedule | null;
  schedules: YearSchedule[];
  templates: ScheduleTemplate[];
  loading: boolean;
  error: string | null;
  generating: boolean;
}
