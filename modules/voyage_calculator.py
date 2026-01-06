"""
Voyage Calculator Module
Handles voyage leg calculations with time intervals and schedules.
"""
from __future__ import annotations

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class VoyageLeg:
    """Represents a single leg of a voyage with timing information."""
    
    def __init__(self, leg_id: str, asset: str, start_port: str, end_port: str,
                 start_time: datetime, duration_hours: float, leg_type: str = "sailing"):
        self.leg_id = leg_id
        self.asset = asset
        self.start_port = start_port
        self.end_port = end_port
        self.start_time = start_time
        self.duration_hours = duration_hours
        self.leg_type = leg_type
        self.end_time = start_time + timedelta(hours=duration_hours)
    
    def to_dict(self) -> Dict:
        """Convert leg to dictionary representation."""
        return {
            'leg_id': self.leg_id,
            'asset': self.asset,
            'start_port': self.start_port,
            'end_port': self.end_port,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_hours': self.duration_hours,
            'leg_type': self.leg_type
        }


class VoyageCalculator:
    """Main calculation engine for voyage planning and scheduling."""
    
    def __init__(self):
        self.legs: List[VoyageLeg] = []
        self.assets: Dict[str, List[VoyageLeg]] = {}
    
    def add_leg(self, leg: VoyageLeg) -> None:
        """Add a voyage leg to the calculation."""
        self.legs.append(leg)
        if leg.asset not in self.assets:
            self.assets[leg.asset] = []
        self.assets[leg.asset].append(leg)
    
    def calculate_voyage_from_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate voyage details from input DataFrame.
        
        Expected columns: asset, start_port, end_port, start_time, duration_hours, leg_type
        """
        results = []
        
        for idx, row in df.iterrows():
            leg = VoyageLeg(
                leg_id=f"LEG_{idx:04d}",
                asset=row['asset'],
                start_port=row['start_port'],
                end_port=row['end_port'],
                start_time=pd.to_datetime(row['start_time']),
                duration_hours=float(row['duration_hours']),
                leg_type=row.get('leg_type', 'sailing')
            )
            self.add_leg(leg)
            results.append(leg.to_dict())
        
        return pd.DataFrame(results)
    
    def get_asset_schedule(self, asset: str) -> pd.DataFrame:
        """Get all legs for a specific asset sorted by time."""
        if asset not in self.assets:
            return pd.DataFrame()
        
        legs_data = [leg.to_dict() for leg in self.assets[asset]]
        df = pd.DataFrame(legs_data)
        return df.sort_values('start_time').reset_index(drop=True)
    
    def get_schedule_summary(self) -> pd.DataFrame:
        """Get summary of all voyages."""
        if not self.legs:
            return pd.DataFrame()
        
        data = [leg.to_dict() for leg in self.legs]
        return pd.DataFrame(data).sort_values(['asset', 'start_time']).reset_index(drop=True)
    
    def find_conflicts(self, tolerance_hours: float = 0) -> List[Dict]:
        """Find potential scheduling conflicts for assets."""
        conflicts = []
        
        for asset, legs in self.assets.items():
            sorted_legs = sorted(legs, key=lambda x: x.start_time)
            for i in range(len(sorted_legs) - 1):
                current = sorted_legs[i]
                next_leg = sorted_legs[i + 1]
                
                gap_hours = (next_leg.start_time - current.end_time).total_seconds() / 3600
                
                if gap_hours < tolerance_hours:
                    conflicts.append({
                        'asset': asset,
                        'leg1': current.leg_id,
                        'leg2': next_leg.leg_id,
                        'gap_hours': gap_hours,
                        'conflict_type': 'overlap' if gap_hours < 0 else 'tight_schedule'
                    })
        
        return conflicts


def calculate_voyage_schedule(input_file: str, output_file: Optional[str] = None) -> pd.DataFrame:
    """
    Main function to calculate voyage schedule from Excel file.
    
    Args:
        input_file: Path to input Excel file
        output_file: Optional path to save results
    
    Returns:
        DataFrame with calculated voyage schedule
    """
    df = pd.read_excel(input_file)
    calculator = VoyageCalculator()
    result = calculator.calculate_voyage_from_df(df)
    
    if output_file:
        result.to_excel(output_file, index=False)
    
    return result
