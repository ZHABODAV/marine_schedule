/**
 * Route and Port Type Definitions
 */

export interface Route {
    id?: string;
    name?: string;
    from: string;
    to: string;
    distance: number;
    durationDays?: number;
    canalTransit?: boolean;
    canal?: string;
    ecaPct?: number;
    waypoints?: string[];
    weatherRisk?: string;
}

export interface Port {
    id?: string;
    name: string;
    country?: string;
    basin?: string;
    unlocode?: string;
    latitude?: number;
    longitude?: number;
    canHandleLiquid?: boolean;
    canHandleDry?: boolean;
    loadRate?: number;
    dischRate?: number;
    waitingHours?: number;
    congestionLevel?: string;
}

export interface Movement {
    loading_port?: string;
    port_from?: string;
    loadPort?: string;
    qty_mt?: number;
    quantity?: number;
    [key: string]: any;
}
