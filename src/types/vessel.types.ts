/**
 * Vessel Type Definitions
 */

export interface Vessel {
  id: string | number;
  name: string;
  imo?: string;
  type: string;
  dwt: number;
  capacity?: number;
  speed?: number;
  consumption?: number;
  current_port?: string;
  status?: 'active' | 'inactive' | 'maintenance';
  owner?: string;
  flag?: string;
  built?: number;
  loa?: number; // Length overall
  beam?: number;
  draft?: number;
  module?: 'deepsea' | 'olya' | 'balakovo';
  [key: string]: any;
}

export interface VesselFormData {
  name: string;
  imo?: string;
  type: string;
  dwt: number;
  capacity?: number;
  speed?: number;
  consumption?: number;
  owner?: string;
  flag?: string;
  built?: number;
  loa?: number;
  beam?: number;
  draft?: number;
  module?: string;
}

export interface VesselDashboardFilter {
  type?: string;
  status?: string;
  owner?: string;
  module?: string;
  search?: string;
}
