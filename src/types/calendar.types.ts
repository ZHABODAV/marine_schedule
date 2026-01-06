/**
 * Calendar Type Definitions
 * For Operational Calendar views and events
 */

export type CalendarViewType = 'month' | 'week' | 'year' | 'timeline';

export type EventStatus = 'planned' | 'in-progress' | 'completed' | 'cancelled';

export type Module = 'all' | 'olya' | 'balakovo' | 'deepsea';

export interface CalendarEvent {
  id: string;
  title: string;
  module: Exclude<Module, 'all'>;
  vessel: string;
  start: Date;
  end: Date;
  status: EventStatus;
  cargo?: number; // in MT
  cost?: number; // in USD
  route?: string;
  details?: Record<string, any>; // Additional voyage-specific data
}

export interface FilterOptions {
  module: Module;
  vessel: string | 'all';
  status: EventStatus | 'all';
  dateRange?: {
    start: Date;
    end: Date;
  };
  searchQuery?: string;
}

export interface CalendarStatistics {
  totalVoyages: number;
  activeVessels: number;
  totalCargo: number;
  totalCost: number;
}

export interface CalendarState {
  currentDate: Date;
  viewType: CalendarViewType;
  events: CalendarEvent[];
  filters: FilterOptions;
  loading: boolean;
  error: string | null;
}
