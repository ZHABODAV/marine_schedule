"""
Voyage Tables Module
Creates formatted tables and reports for voyage data.
"""
from __future__ import annotations

import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict


class VoyageTableGenerator:
    """Generates formatted tables for voyage data."""
    
    def __init__(self, voyage_data: pd.DataFrame):
        """
        Initialize with voyage data.
        
        Args:
            voyage_data: DataFrame with voyage information
        """
        self.voyage_data = voyage_data
    
    def create_asset_table(self, asset: Optional[str] = None) -> pd.DataFrame:
        """
        Create a formatted table for asset schedules.
        
        Args:
            asset: Optional specific asset to filter
        
        Returns:
            Formatted DataFrame
        """
        df = self.voyage_data.copy()
        
        if asset:
            df = df[df['asset'] == asset]
        
        # Format datetime columns
        if 'start_time' in df.columns:
            df['start_time'] = pd.to_datetime(df['start_time'])
        if 'end_time' in df.columns:
            df['end_time'] = pd.to_datetime(df['end_time'])
        
        # Add calculated columns
        if 'start_time' in df.columns and 'end_time' in df.columns:
            df['duration_days'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 86400
        
        return df
    
    def create_port_summary(self) -> pd.DataFrame:
        """Create summary of port activities."""
        df = self.voyage_data.copy()
        
        # Summarize by port
        port_visits = []
        
        if 'start_port' in df.columns:
            start_ports = df.groupby('start_port').size().reset_index(name='departures')
            port_visits.append(start_ports.rename(columns={'start_port': 'port'}))
        
        if 'end_port' in df.columns:
            end_ports = df.groupby('end_port').size().reset_index(name='arrivals')
            if port_visits:
                port_visits[0] = port_visits[0].merge(end_ports.rename(columns={'end_port': 'port'}), 
                                                       on='port', how='outer')
            else:
                port_visits.append(end_ports.rename(columns={'end_port': 'port'}))
        
        if port_visits:
            result = port_visits[0].fillna(0)
            result['total_visits'] = result.get('departures', 0) + result.get('arrivals', 0)
            return result.sort_values('total_visits', ascending=False)
        
        return pd.DataFrame()
    
    def create_timeline_table(self, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Create a timeline table for a specific date range.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            Filtered and formatted DataFrame
        """
        df = self.voyage_data.copy()
        
        if 'start_time' in df.columns:
            df['start_time'] = pd.to_datetime(df['start_time'])
            
            if start_date:
                df = df[df['start_time'] >= pd.to_datetime(start_date)]
            
            if end_date:
                df = df[df['start_time'] <= pd.to_datetime(end_date)]
        
        return df.sort_values('start_time') if 'start_time' in df.columns else df
    
    def create_utilization_table(self) -> pd.DataFrame:
        """Create asset utilization summary table."""
        df = self.voyage_data.copy()
        
        if 'asset' not in df.columns:
            return pd.DataFrame()
        
        summary = []
        
        for asset in df['asset'].unique():
            asset_data = df[df['asset'] == asset]
            
            utilization = {
                'asset': asset,
                'total_legs': len(asset_data),
                'total_hours': asset_data['duration_hours'].sum() if 'duration_hours' in df.columns else 0
            }
            
            if 'leg_type' in df.columns:
                for leg_type in asset_data['leg_type'].unique():
                    type_data = asset_data[asset_data['leg_type'] == leg_type]
                    utilization[f'{leg_type}_hours'] = type_data['duration_hours'].sum() if 'duration_hours' in type_data.columns else 0
            
            summary.append(utilization)
        
        return pd.DataFrame(summary)
    
    def export_to_excel(self, output_file: str, include_summaries: bool = True) -> None:
        """
        Export all tables to Excel file with multiple sheets.
        
        Args:
            output_file: Path to output Excel file
            include_summaries: Whether to include summary sheets
        """
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main data
            self.voyage_data.to_excel(writer, sheet_name='Voyage Data', index=False)
            
            if include_summaries:
                # Port summary
                port_summary = self.create_port_summary()
                if not port_summary.empty:
                    port_summary.to_excel(writer, sheet_name='Port Summary', index=False)
                
                # Utilization
                utilization = self.create_utilization_table()
                if not utilization.empty:
                    utilization.to_excel(writer, sheet_name='Asset Utilization', index=False)
                
                # Per-asset sheets
                if 'asset' in self.voyage_data.columns:
                    for asset in self.voyage_data['asset'].unique():
                        asset_table = self.create_asset_table(asset)
                        sheet_name = f'Asset_{asset}'[:31]  # Excel sheet name limit
                        asset_table.to_excel(writer, sheet_name=sheet_name, index=False)


def create_voyage_tables(data: pd.DataFrame, output_file: Optional[str] = None) -> VoyageTableGenerator:
    """
    Create voyage tables from data.
    
    Args:
        data: Voyage data DataFrame
        output_file: Optional output Excel file path
    
    Returns:
        VoyageTableGenerator instance
    """
    generator = VoyageTableGenerator(data)
    
    if output_file:
        generator.export_to_excel(output_file)
    
    return generator
