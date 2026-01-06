"""
Year Schedule Optimizer Module

Generates and optimizes year-long vessel schedules considering:
- Vessel turnaround times
- Seasonal demand
- Cargo commitments
- Fleet availability
- Port constraints
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


@dataclass
class YearScheduleParams:
    """Parameters for year schedule generation."""
    start_date: datetime
    period_months: int = 12
    turnaround_multiplier: float = 1.0  # Multiplier for vessel turnaround time
    min_cargo_utilization: float = 0.7  # Minimum cargo utilization (70%)
    max_demurrage_days: int = 3  # Maximum allowed demurrage
    seasonal_adjustment: bool = True  # Apply seasonal demand adjustments
    
    def get_end_date(self) -> datetime:
        """Calculate end date based on period."""
        return self.start_date + timedelta(days=30 * self.period_months)


@dataclass
class VesselAvailability:
    """Vessel availability window."""
    vessel_id: str
    available_from: datetime
    available_until: datetime
    current_location: str
    dwt: float
    speed_kts: float
    
    def is_available_on(self, date: datetime) -> bool:
        """Check if vessel is available on a date."""
        return self.available_from <= date <= self.available_until


@dataclass
class CargoCommitment:
    """Cargo commitment to be scheduled."""
    commitment_id: str
    commodity: str
    quantity_mt: float
    load_port: str
    discharge_port: str
    laycan_start: datetime
    laycan_end: datetime
    priority: int = 5  # 1-10, 10 is highest
    
    def is_within_laycan(self, date: datetime) -> bool:
        """Check if date is within laycan period."""
        return self.laycan_start <= date <= self.laycan_end


@dataclass
class ScheduledVoyage:
    """A voyage in the year schedule."""
    voyage_id: str
    vessel_id: str
    commitment_id: str
    load_port: str
    discharge_port: str
    load_date: datetime
    discharge_date: datetime
    cargo_mt: float
    revenue_usd: float = 0
    cost_usd: float = 0
    profit_usd: float = 0
    
    def get_voyage_days(self) -> float:
        """Get duration of voyage in days."""
        return (self.discharge_date - self.load_date).days


class YearScheduleOptimizer:
    """
    Optimizes year-long vessel schedules.
    
    Features:
    - Greedy cargo allocation
    - Fleet utilization maximization
    - Laycan adherence
    - Seasonal demand adjustment
    - Multi-objective optimization
    """
    
    def __init__(
        self,
        vessels: List[VesselAvailability],
        cargo_commitments: List[CargoCommitment],
        route_distances: Dict[Tuple[str, str], float],
        params: YearScheduleParams
    ):
        """
        Initialize year schedule optimizer.
        
        Parameters:
            vessels: List of available vessels
            cargo_commitments: List of cargo commitments to schedule
            route_distances: Dictionary mapping (from_port, to_port) to distance in nm
            params: Schedule generation parameters
        """
        self.vessels = vessels
        self.cargo_commitments = sorted(cargo_commitments, key=lambda c: -c.priority)
        self.route_distances = route_distances
        self.params = params
        
        self.scheduled_voyages: List[ScheduledVoyage] = []
        self.unscheduled_cargo: List[CargoCommitment] = []
        self.vessel_positions: Dict[str, str] = {v.vessel_id: v.current_location for v in vessels}
        self.vessel_availability_dates: Dict[str, datetime] = {v.vessel_id: v.available_from for v in vessels}
    
    def generate_schedule(self) -> Dict:
        """
        Generate optimized year schedule.
        
        Returns:
            Dictionary with schedule results
        """
        print(f"Generating year schedule from {self.params.start_date} for {self.params.period_months} months...")
        
        # Sort cargo by laycan start date and priority
        sorted_cargo = sorted(
            self.cargo_commitments,
            key=lambda c: (c.laycan_start, -c.priority)
        )
        
        # Try to schedule each cargo
        for cargo in sorted_cargo:
            scheduled = self._try_schedule_cargo(cargo)
            if not scheduled:
                self.unscheduled_cargo.append(cargo)
        
        # Calculate metrics
        total_cargo_quantity = sum(c.quantity_mt for c in self.cargo_commitments)
        scheduled_cargo_quantity = sum(v.cargo_mt for v in self.scheduled_voyages)
        cargo_coverage = (scheduled_cargo_quantity / total_cargo_quantity * 100) if total_cargo_quantity > 0 else 0
        
        total_revenue = sum(v.revenue_usd for v in self.scheduled_voyages)
        total_cost = sum(v.cost_usd for v in self.scheduled_voyages)
        total_profit = total_revenue - total_cost
        
        avg_vessel_utilization = self._calculate_fleet_utilization()
        
        return {
            'schedule': self.scheduled_voyages,
            'unscheduled_cargo': self.unscheduled_cargo,
            'metrics': {
                'total_voyages': len(self.scheduled_voyages),
                'total_cargo_mt': total_cargo_quantity,
                'scheduled_cargo_mt': scheduled_cargo_quantity,
                'cargo_coverage_pct': round(cargo_coverage, 2),
                'unscheduled_commitments': len(self.unscheduled_cargo),
                'total_revenue_usd': round(total_revenue, 2),
                'total_cost_usd': round(total_cost, 2),
                'total_profit_usd': round(total_profit, 2),
                'avg_fleet_utilization_pct': round(avg_vessel_utilization, 2)
            }
        }
    
    def _try_schedule_cargo(self, cargo: CargoCommitment) -> bool:
        """
        Try to schedule a cargo commitment.
        
        Parameters:
            cargo: Cargo to schedule
            
        Returns:
            True if successfully scheduled
        """
        # Find suitable vessels
        suitable_vessels = [
            v for v in self.vessels
            if v.dwt >= cargo.quantity_mt
        ]
        
        if not suitable_vessels:
            return False
        
        # Try each vessel
        best_vessel = None
        best_load_date = None
        best_score = -1
        
        for vessel in suitable_vessels:
            # Check if vessel is available during laycan
            vessel_available_date = self.vessel_availability_dates.get(vessel.vessel_id, vessel.available_from)
            
            # Calculate earliest possible load date
            current_position = self.vessel_positions.get(vessel.vessel_id, vessel.current_location)
            
            # Time to reposition to load port
            reposition_time_days = 0
            if current_position != cargo.load_port:
                distance = self.route_distances.get((current_position, cargo.load_port), 0)
                if distance > 0:
                    reposition_time_days = (distance / (vessel.speed_kts * 24)) + 0.5  # Add 0.5 day buffer
            
            earliest_load = max(
                vessel_available_date + timedelta(days=reposition_time_days),
                cargo.laycan_start
            )
            
            # Check if within laycan
            if earliest_load > cargo.laycan_end:
                continue
            
            # Calculate voyage time
            voyage_distance = self.route_distances.get((cargo.load_port, cargo.discharge_port), 0)
            if voyage_distance == 0:
                continue
            
            voyage_time_days = (voyage_distance / (vessel.speed_kts * 24)) + 1.0  # Add 1 day for port ops
            voyage_time_days *= self.params.turnaround_multiplier
            
            discharge_date = earliest_load + timedelta(days=voyage_time_days)
            
            # Score this option (prefer earlier dates, less repositioning)
            score = 1000 - reposition_time_days * 10 - (earliest_load - cargo.laycan_start).days
            
            if score > best_score:
                best_score = score
                best_vessel = vessel
                best_load_date = earliest_load
        
        if best_vessel and best_load_date:
            # Schedule this cargo
            voyage_distance = self.route_distances.get((cargo.load_port, cargo.discharge_port), 0)
            voyage_time_days = (voyage_distance / (best_vessel.speed_kts * 24)) + 1.0
            voyage_time_days *= self.params.turnaround_multiplier
            
            discharge_date = best_load_date + timedelta(days=voyage_time_days)
            
            # Estimate financials
            revenue = cargo.quantity_mt * 50  # Simple estimate: $50/MT
            cost = voyage_distance * 0.5 + cargo.quantity_mt * 10  # Simple cost model
            profit = revenue - cost
            
            voyage = ScheduledVoyage(
                voyage_id=f"V_{len(self.scheduled_voyages) + 1:04d}",
                vessel_id=best_vessel.vessel_id,
                commitment_id=cargo.commitment_id,
                load_port=cargo.load_port,
                discharge_port=cargo.discharge_port,
                load_date=best_load_date,
                discharge_date=discharge_date,
                cargo_mt=cargo.quantity_mt,
                revenue_usd=revenue,
                cost_usd=cost,
                profit_usd=profit
            )
            
            self.scheduled_voyages.append(voyage)
            
            # Update vessel position and availability
            self.vessel_positions[best_vessel.vessel_id] = cargo.discharge_port
            self.vessel_availability_dates[best_vessel.vessel_id] = discharge_date + timedelta(days=0.5)  # 0.5 day turnaround
            
            return True
        
        return False
    
    def _calculate_fleet_utilization(self) -> float:
        """Calculate average fleet utilization over the period."""
        if not self.vessels:
            return 0
        
        total_days = (self.params.get_end_date() - self.params.start_date).days
        
        utilizations = []
        for vessel in self.vessels:
            vessel_voyages = [v for v in self.scheduled_voyages if v.vessel_id == vessel.vessel_id]
            busy_days = sum(v.get_voyage_days() for v in vessel_voyages)
            utilization = (busy_days / total_days * 100) if total_days > 0 else 0
            utilizations.append(min(utilization, 100))  # Cap at 100%
        
        return sum(utilizations) / len(utilizations) if utilizations else 0
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """Export scheduled voyages to DataFrame."""
        if not self.scheduled_voyages:
            return pd.DataFrame()
        
        data = []
        for voyage in self.scheduled_voyages:
            data.append({
                'Voyage ID': voyage.voyage_id,
                'Vessel ID': voyage.vessel_id,
                'Commitment ID': voyage.commitment_id,
                'Load Port': voyage.load_port,
                'Discharge Port': voyage.discharge_port,
                'Load Date': voyage.load_date,
                'Discharge Date': voyage.discharge_date,
                'Cargo (MT)': voyage.cargo_mt,
                'Duration (days)': voyage.get_voyage_days(),
                'Revenue (USD)': voyage.revenue_usd,
                'Cost (USD)': voyage.cost_usd,
                'Profit (USD)': voyage.profit_usd
            })
        
        return pd.DataFrame(data)
    
    def export_to_excel(self, filename: str):
        """Export schedule to Excel file."""
        df = self.export_to_dataframe()
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Year Schedule', index=False)
            
            # Add unscheduled cargo sheet
            if self.unscheduled_cargo:
                unscheduled_data = []
                for cargo in self.unscheduled_cargo:
                    unscheduled_data.append({
                        'Commitment ID': cargo.commitment_id,
                        'Commodity': cargo.commodity,
                        'Quantity (MT)': cargo.quantity_mt,
                        'Load Port': cargo.load_port,
                        'Discharge Port': cargo.discharge_port,
                        'Laycan Start': cargo.laycan_start,
                        'Laycan End': cargo.laycan_end,
                        'Priority': cargo.priority
                    })
                
                unscheduled_df = pd.DataFrame(unscheduled_data)
                unscheduled_df.to_excel(writer, sheet_name='Unscheduled Cargo', index=False)
            
            # Add summary sheet
            result = self.generate_schedule()
            metrics_data = []
            for key, value in result['metrics'].items():
                metrics_data.append({'Metric': key.replace('_', ' ').title(), 'Value': value})
            
            metrics_df = pd.DataFrame(metrics_data)
            metrics_df.to_excel(writer, sheet_name='Summary', index=False)


class YearScheduleManager:
    """
    Simple wrapper for year schedule management in API.
    Provides easy access to YearScheduleOptimizer functionality.
    """
    
    def __init__(self):
        self.current_schedule: Optional[YearScheduleOptimizer] = None
        self.schedule_result: Optional[Dict] = None
    
    def generate_from_dataframes(
        self,
        vessels_df: pd.DataFrame,
        cargo_df: pd.DataFrame,
        routes_df: pd.DataFrame,
        start_date: datetime,
        period_months: int = 12
    ) -> Dict:
        """
        Generate year schedule from DataFrames.
        
        Parameters:
            vessels_df: DataFrame with vessel data
            cargo_df: DataFrame with cargo commitments
            routes_df: DataFrame with route distances
            start_date: Schedule start date
            period_months: Planning period in months
            
        Returns:
            Schedule result dictionary
        """
        # Convert DataFrames to objects
        vessels = []
        for _, row in vessels_df.iterrows():
            vessels.append(
                VesselAvailability(
                    vessel_id=row['vessel_id'],
                    available_from=pd.to_datetime(row.get('available_from', start_date)),
                    available_until=pd.to_datetime(row.get('available_until', start_date + timedelta(days=365))),
                    current_location=row.get('current_location', row.get('home_port', 'SINGAPORE')),
                    dwt=float(row['dwt']),
                    speed_kts=float(row.get('speed', 14.0))
                )
            )
        
        cargo_commitments = []
        for _, row in cargo_df.iterrows():
            cargo_commitments.append(
                CargoCommitment(
                    commitment_id=row.get('id', row.get('cargo_id', f"CARGO_{len(cargo_commitments)+1}")),
                    commodity=row.get('commodity', 'General'),
                    quantity_mt=float(row.get('quantity', 50000)),
                    load_port=row['loadPort'] if 'loadPort' in row else row.get('load_port', ''),
                    discharge_port=row['dischPort'] if 'dischPort' in row else row.get('discharge_port', ''),
                    laycan_start=pd.to_datetime(row.get('laycanStart', row.get('laycan_start', start_date))),
                    laycan_end=pd.to_datetime(row.get('laycanEnd', row.get('laycan_end', start_date + timedelta(days=7)))),
                    priority=int(row.get('priority', 5))
                )
            )
        
        #  Build route distances dictionary
        route_distances = {}
        for _, row in routes_df.iterrows():
            from_port = row['from'] if 'from' in row else row.get('from_port', '')
            to_port = row['to'] if 'to' in row else row.get('to_port', '')
            distance = float(row.get('distance', row.get('distance_nm', 0)))
            
            route_distances[(from_port, to_port)] = distance
        
        # Create optimizer
        params = YearScheduleParams(
            start_date=start_date,
            period_months=period_months
        )
        
        self.current_schedule = YearScheduleOptimizer(
            vessels=vessels,
            cargo_commitments=cargo_commitments,
            route_distances=route_distances,
            params=params
        )
        
        self.schedule_result = self.current_schedule.generate_schedule()
        return self.schedule_result
    
    def export_to_excel(self, filename: str):
        """Export current schedule to Excel."""
        if self.current_schedule:
            self.current_schedule.export_to_excel(filename)
    
    def get_schedule_dataframe(self) -> pd.DataFrame:
        """Get schedule as DataFrame."""
        if self.current_schedule:
            return self.current_schedule.export_to_dataframe()
        return pd.DataFrame()


def create_sample_year_schedule_data() -> Tuple[List[VesselAvailability], List[CargoCommitment], Dict]:
    """Create sample data for testing."""
    start_date = datetime(2026, 1, 1)
    
    vessels = [
        VesselAvailability("VESSEL_001", start_date, start_date + timedelta(days=365), "SINGAPORE", 50000, 14.0),
        VesselAvailability("VESSEL_002", start_date, start_date + timedelta(days=365), "ROTTERDAM", 75000, 13.5),
        VesselAvailability("VESSEL_003", start_date, start_date + timedelta(days=365), "HOUSTON", 60000, 14.5),
    ]
    
    cargo_commitments = []
    for i in range(12):
        month_start = start_date + timedelta(days=30 * i)
        cargo_commitments.append(
            CargoCommitment(
                commitment_id=f"CARGO_{i+1:03d}",
                commodity="Grain",
                quantity_mt=45000,
                load_port="SINGAPORE",
                discharge_port="ROTTERDAM",
                laycan_start=month_start,
                laycan_end=month_start + timedelta(days=7),
                priority=5
            )
        )
    
    route_distances = {
        ("SINGAPORE", "ROTTERDAM"): 8500,
        ("ROTTERDAM", "HOUSTON"): 4800,
        ("HOUSTON", "SINGAPORE"): 9200,
        ("SINGAPORE", "HOUSTON"): 9200,
        ("ROTTERDAM", "SINGAPORE"): 8500,
        ("HOUSTON", "ROTTERDAM"): 4800,
    }
    
    return vessels, cargo_commitments, route_distances
