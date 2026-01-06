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

export interface CostAllocation {
    operationalCost: number;
    overheadCost: number;
    otherCost: number;
    totalCost: number; // Computed field - sum of all costs
}

export interface CargoFormData {
    id: string;
    commodity: string;
    quantity: number;
    loadPort: string;
    dischPort: string;
    laycanStart: string;
    laycanEnd: string;
    status?: 'Pending' | 'Assigned' | 'Completed' | 'Cancelled';
    freightRate?: number;
    notes?: string;
    operationalCost?: number;
    overheadCost?: number;
    otherCost?: number;
    costAllocation?: CostAllocation;
}

export interface CargoTemplate {
    id: string;
    name: string;
    description?: string;
    commodity: string;
    quantity?: number;
    loadPort?: string;
    dischPort?: string;
    freightRate?: number;
    operationalCost?: number;
    overheadCost?: number;
    otherCost?: number;
    isDefault?: boolean;
    createdAt?: string | Date;
    updatedAt?: string | Date;
}

export interface CargoTemplateFormData {
    name: string;
    description?: string;
    commodity: string;
    quantity?: number;
    loadPort?: string;
    dischPort?: string;
    freightRate?: number;
    operationalCost?: number;
    overheadCost?: number;
    otherCost?: number;
    costAllocation?: CostAllocation;
    isDefault?: boolean;
}
