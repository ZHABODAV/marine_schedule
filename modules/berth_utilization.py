"""
Berth Utilization Module
Calculates and reports berth utilization metrics.
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class BerthUtilizationAnalyzer:
    """Analyzes berth utilization from voyage data."""
    
    def __init__(self, voyage_data: pd.DataFrame):
        """
        Initialize with voyage data.
        
        Args:
            voyage_data: DataFrame with voyage schedules
        """
        self.voyage_data = voyage_data.copy()
        self._prepare_data()
    
    def _prepare_data(self) -> None:
        """Prepare data for analysis."""
        if 'start_time' in self.voyage_data.columns:
            self.voyage_data['start_time'] = pd.to_datetime(self.voyage_data['start_time'])
        if 'end_time' in self.voyage_data.columns:
            self.voyage_data['end_time'] = pd.to_datetime(self.voyage_data['end_time'])
    
    def calculate_port_utilization(self, port: str,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None,
                                   berth_count: int = 1) -> Dict:
        """
        Calculate utilization metrics for a specific port.
        
        Args:
            port: Port name
            start_date: Analysis start date
            end_date: Analysis end date
            berth_count: Number of berths at the port (default: 1)
        
        Returns:
            Dictionary with utilization metrics
        """
        df = self.voyage_data.copy()
        
        # Filter for this port
        port_data = df[(df.get('start_port') == port) | (df.get('end_port') == port)]
        
        if port_data.empty:
            return {
                'port': port,
                'total_visits': 0,
                'avg_occupation_time_hours': 0,
                'utilization_rate': 0
            }
        
        # Set date range
        if start_date is None:
            start_date = port_data['start_time'].min()
        if end_date is None:
            end_date = port_data['end_time'].max()
        
        # Ensure dates are valid (handle NaT from pandas)
        if pd.isna(start_date) or pd.isna(end_date):
            return {
                'port': port,
                'total_visits': 0,
                'avg_occupation_time_hours': 0,
                'utilization_rate': 0
            }
        
        # Filter by date range
        port_data = port_data[
            (port_data['start_time'] >= start_date) &
            (port_data['end_time'] <= end_date)
        ]
        
        # Calculate metrics
        total_visits = len(port_data)
        total_occupation_hours = port_data['duration_hours'].sum() if 'duration_hours' in port_data.columns else 0
        
        # Calculate period hours
        period_hours = (end_date - start_date).total_seconds() / 3600
        
        # Utilization rate (accounting for berth count)
        total_capacity_hours = period_hours * berth_count
        utilization_rate = (total_occupation_hours / total_capacity_hours * 100) if total_capacity_hours > 0 else 0
        
        return {
            'port': port,
            'analysis_start': start_date,
            'analysis_end': end_date,
            'berth_count': berth_count,
            'total_visits': total_visits,
            'total_occupation_hours': round(total_occupation_hours, 2),
            'avg_occupation_time_hours': round(total_occupation_hours / total_visits, 2) if total_visits > 0 else 0,
            'utilization_rate_percent': round(utilization_rate, 2),
            'period_hours': round(period_hours, 2)
        }
    
    def calculate_all_ports_utilization(self, 
                                        start_date: Optional[datetime] = None,
                                        end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Calculate utilization for all ports.
        
        Args:
            start_date: Analysis start date
            end_date: Analysis end date
        
        Returns:
            DataFrame with utilization metrics for all ports
        """
        # Get all unique ports
        ports = set()
        if 'start_port' in self.voyage_data.columns:
            ports.update(self.voyage_data['start_port'].dropna().unique())
        if 'end_port' in self.voyage_data.columns:
            ports.update(self.voyage_data['end_port'].dropna().unique())
        
        # Calculate for each port
        results = []
        for port in sorted(ports):
            metrics = self.calculate_port_utilization(port, start_date, end_date)
            results.append(metrics)
        
        return pd.DataFrame(results)
    
    def identify_peak_periods(self, port: str, window_days: int = 7) -> pd.DataFrame:
        """
        Identify peak utilization periods for a port.
        
        Args:
            port: Port name
            window_days: Rolling window size in days
        
        Returns:
            DataFrame with peak periods
        """
        df = self.voyage_data.copy()
        port_data = df[(df.get('start_port') == port) | (df.get('end_port') == port)]
        
        if port_data.empty:
            return pd.DataFrame()
        
        # Create daily utilization
        min_date = port_data['start_time'].min()
        max_date = port_data['end_time'].max()
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        
        daily_visits = []
        for date in date_range:
            # Count activities on this day
            day_activities = port_data[
                (port_data['start_time'].dt.date <= date) &
                (port_data['end_time'].dt.date >= date)
            ]
            daily_visits.append({
                'date': date,
                'concurrent_vessels': len(day_activities),
                'total_hours': day_activities['duration_hours'].sum() if 'duration_hours' in day_activities.columns else 0
            })
        
        daily_df = pd.DataFrame(daily_visits)
        
        if not daily_df.empty:
            # Calculate rolling average
            daily_df['rolling_avg_vessels'] = daily_df['concurrent_vessels'].rolling(window=window_days, min_periods=1).mean()
            daily_df['rolling_avg_hours'] = daily_df['total_hours'].rolling(window=window_days, min_periods=1).mean()
        
        return daily_df
    
    def get_berth_occupancy_timeline(self, port: str) -> pd.DataFrame:
        """
        Get detailed timeline of berth occupancy for a port.
        
        Args:
            port: Port name
        
        Returns:
            DataFrame with occupancy timeline
        """
        df = self.voyage_data.copy()
        port_data = df[(df.get('start_port') == port) | (df.get('end_port') == port)]
        
        if port_data.empty:
            return pd.DataFrame()
        
        # Create events for arrivals and departures
        events = []
        
        for _, row in port_data.iterrows():
            # Arrival event
            events.append({
                'datetime': row['start_time'],
                'event_type': 'arrival',
                'asset': row.get('asset', 'Unknown'),
                'change': +1
            })
            
            # Departure event
            events.append({
                'datetime': row['end_time'],
                'event_type': 'departure',
                'asset': row.get('asset', 'Unknown'),
                'change': -1
            })
        
        events_df = pd.DataFrame(events).sort_values('datetime')
        
        # Calculate cumulative occupancy
        events_df['occupancy'] = events_df['change'].cumsum()
        
        return events_df
    
    def generate_utilization_report(self, output_file: Optional[str] = None) -> pd.DataFrame:
        """
        Generate comprehensive utilization report.
        
        Args:
            output_file: Optional Excel file to save report
        
        Returns:
            DataFrame with report
        """
        report = self.calculate_all_ports_utilization()
        
        if output_file and not report.empty:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                report.to_excel(writer, sheet_name='Port Utilization', index=False)
                
                # Add detailed sheets for top ports
                top_ports = report.nlargest(5, 'total_visits')['port'].tolist()
                
                for port in top_ports:
                    timeline = self.get_berth_occupancy_timeline(port)
                    if not timeline.empty:
                        sheet_name = f"{port[:20]}_Timeline"
                        timeline.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return report


def analyze_berth_utilization(voyage_data: pd.DataFrame, 
                              output_file: Optional[str] = None) -> BerthUtilizationAnalyzer:
    """
    Analyze berth utilization from voyage data.
    
    Args:
        voyage_data: DataFrame with voyage schedules
        output_file: Optional output Excel file
    
    Returns:
        BerthUtilizationAnalyzer instance
    """
    analyzer = BerthUtilizationAnalyzer(voyage_data)
    
    if output_file:
        analyzer.generate_utilization_report(output_file)
    
    return analyzer
