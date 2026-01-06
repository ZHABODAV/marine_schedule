/**
 * Cargo Type Definitions
 */

export interface CargoCommitment {
    id: string;
    commodity: string;
    quantity: number;
    loadPort: string;
    dischPort: string;
    laycanStart: string;
    laycanEnd: string;
    status: 'Pending' | 'Assigned' | 'Completed';
    deliveryDeadline?: string;
    operationalCost?: number;
    overheadCost?: number;
    otherCost?: number;
    laneId?: string;
    source?: string;
}

export interface RailCargo {
    origin_station?: string;
    origin?: string;
    destination_port?: string;
    destination?: string;
    qty_mt?: number;
    quantity?: number;
    [key: string]: any;
}

export interface CargoType {
    id: string;
    name: string;
    category?: string;
    properties?: Record<string, any>;
}

export interface CargoFormData {
    id: string;
    commodity: string;
    quantity: number;
    loadPort: string;
    dischPort: string;
    laycanStart: string;
    laycanEnd: string;
    operationalCost?: number;
    overheadCost?: number;
    otherCost?: number;
}
