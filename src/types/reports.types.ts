/**
 * PDF Reports Type Definitions
 * For export and reporting functionality
 */

import type { Module } from './calendar.types';

export type ReportType = 'comprehensive' | 'fleet' | 'schedule' | 'financial';

export type ExportFormat = 'pdf' | 'excel' | 'csv';

export interface ReportConfig {
  type: ReportType;
  format: ExportFormat;
  module: Module;
  dateRange: {
    start: Date;
    end: Date;
  };
  vessels?: string[]; // Specific vessels to include
  includeCharts?: boolean;
  includeSummary?: boolean;
  includeDetails?: boolean;
}

export interface ComprehensiveReportData {
  voyages: Array<{
    id: string;
    vesselName: string;
    module: string;
    startDate: string;
    endDate: string;
    route: string;
    cargo: number;
    cost: number;
    revenue: number;
    legs: Array<{
      type: string;
      from: string;
      to: string;
      distance: number;
      duration: number;
    }>;
  }>;
  totalVoyages: number;
  totalCargo: number;
  totalCost: number;
  totalRevenue: number;
}

export interface FleetReportData {
  vessels: Array<{
    id: string;
    name: string;
    type: string;
    dwt: number;
    utilizationRate: number;
    totalVoyages: number;
    totalDistance: number;
    totalCargo: number;
    operatingDays: number;
    idleDays: number;
  }>;
  fleetStatistics: {
    totalVessels: number;
    averageUtilization: number;
    totalOperatingDays: number;
    totalIdleDays: number;
  };
}

export interface ScheduleReportData {
  timeline: Array<{
    date: string;
    events: Array<{
      vesselName: string;
      eventType: string;
      location: string;
      status: string;
    }>;
  }>;
  monthlyBreakdown: Array<{
    month: string;
    voyagesCount: number;
    cargoMoved: number;
    vesselsActive: number;
  }>;
}

export interface FinancialReportData {
  summary: {
    totalRevenue: number;
    totalCost: number;
    netProfit: number;
    profitMargin: number;
  };
  costBreakdown: {
    operationalCost: number;
    fuelCost: number;
    portCost: number;
    canalCost: number;
    overheadCost: number;
    otherCost: number;
  };
  revenueStreams: Array<{
    source: string;
    amount: number;
    percentage: number;
  }>;
  voyageFinancials: Array<{
    voyageId: string;
    revenue: number;
    cost: number;
    profit: number;
    margin: number;
  }>;
}

export interface ReportGenerationStatus {
  id: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  progress: number; // 0-100
  downloadUrl?: string;
  error?: string;
  createdAt: string;
}

export interface ReportsState {
  activeReports: ReportGenerationStatus[];
  history: ReportGenerationStatus[];
  loading: boolean;
  error: string | null;
}
