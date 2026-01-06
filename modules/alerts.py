"""
Alerts Module
Handles alert system for overlaps and berth capacity issues.
"""
from __future__ import annotations

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Alert:
    """Represents a single alert."""
    
    def __init__(self, alert_type: str, severity: AlertSeverity, 
                 message: str, details: Optional[Dict] = None):
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'alert_type': self.alert_type,
            'severity': self.severity.value,
            'message': self.message,
            'details': str(self.details)
        }
    
    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.alert_type}: {self.message}"


class AlertSystem:
    """Main alert system for voyage scheduling."""
    
    def __init__(self):
        self.alerts: List[Alert] = []
    
    def add_alert(self, alert: Alert) -> None:
        """Add an alert to the system."""
        self.alerts.append(alert)
    
    def check_asset_overlaps(self, voyage_data: pd.DataFrame) -> List[Alert]:
        """
        Check for asset scheduling overlaps.
        
        Args:
            voyage_data: DataFrame with voyage schedules
        
        Returns:
            List of overlap alerts
        """
        overlap_alerts = []
        
        if 'asset' not in voyage_data.columns:
            return overlap_alerts
        
        df = voyage_data.copy()
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        
        # Check each asset
        for asset in df['asset'].unique():
            asset_data = df[df['asset'] == asset].sort_values('start_time')
            
            for i in range(len(asset_data) - 1):
                current = asset_data.iloc[i]
                next_leg = asset_data.iloc[i + 1]
                
                # Check if there's an overlap
                if current['end_time'] > next_leg['start_time']:
                    overlap_hours = (current['end_time'] - next_leg['start_time']).total_seconds() / 3600
                    
                    alert = Alert(
                        alert_type="ASSET_OVERLAP",
                        severity=AlertSeverity.CRITICAL,
                        message=f"Asset {asset} has overlapping schedules",
                        details={
                            'asset': asset,
                            'leg1_end': current['end_time'],
                            'leg2_start': next_leg['start_time'],
                            'overlap_hours': round(overlap_hours, 2),
                            'leg1_route': f"{current.get('start_port', 'N/A')} → {current.get('end_port', 'N/A')}",
                            'leg2_route': f"{next_leg.get('start_port', 'N/A')} → {next_leg.get('end_port', 'N/A')}"
                        }
                    )
                    overlap_alerts.append(alert)
                    self.add_alert(alert)
        
        return overlap_alerts
    
    def check_berth_capacity(self, voyage_data: pd.DataFrame, 
                           berth_capacities: Optional[Dict[str, int]] = None) -> List[Alert]:
        """
        Check for berth capacity issues.
        
        Args:
            voyage_data: DataFrame with voyage schedules
            berth_capacities: Dictionary of port -> max capacity
        
        Returns:
            List of capacity alerts
        """
        capacity_alerts = []
        
        if berth_capacities is None:
            berth_capacities = {}
        
        df = voyage_data.copy()
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        
        # Get all ports
        ports = set()
        if 'start_port' in df.columns:
            ports.update(df['start_port'].unique())
        if 'end_port' in df.columns:
            ports.update(df['end_port'].unique())
        
        # Check each port
        for port in ports:
            # Get all activities at this port
            port_activities = []
            
            for _, row in df.iterrows():
                if row.get('end_port') == port:
                    port_activities.append({
                        'start': row['start_time'],
                        'end': row['end_time'],
                        'asset': row['asset'],
                        'activity': 'arrival'
                    })
            
            # Sort by start time
            port_activities.sort(key=lambda x: x['start'])
            
            # Check against capacity
            max_capacity = berth_capacities.get(port, 999)  # Default high capacity
            
            # Optimized sweep-line algorithm O(N log N)
            events = []
            for activity in port_activities:
                events.append((activity['start'], 1, activity['asset'], activity['end']))
                events.append((activity['end'], -1, activity['asset'], None))
            
            # Sort by time
            events.sort(key=lambda x: x[0])
            
            current_assets = set()
            
            for time, change, asset, end_time in events:
                if change == 1:
                    current_assets.add(asset)
                    
                    if len(current_assets) > max_capacity:
                        # Found a violation
                        alert = Alert(
                            alert_type="BERTH_CAPACITY",
                            severity=AlertSeverity.WARNING,
                            message=f"Port {port} exceeds capacity",
                            details={
                                'port': port,
                                'concurrent_vessels': len(current_assets),
                                'max_capacity': max_capacity,
                                'assets': list(current_assets),
                                'time_period': f"At {time}"
                            }
                        )
                        # Avoid duplicate alerts for the same peak
                        if not capacity_alerts or capacity_alerts[-1].details['time_period'] != f"At {time}":
                            capacity_alerts.append(alert)
                            self.add_alert(alert)
                else:
                    current_assets.discard(asset)
        
        return capacity_alerts
    
    def check_tight_schedules(self, voyage_data: pd.DataFrame, 
                             min_buffer_hours: float = 2.0) -> List[Alert]:
        """
        Check for tight scheduling (insufficient buffer time).
        
        Args:
            voyage_data: DataFrame with voyage schedules
            min_buffer_hours: Minimum buffer time required in hours
        
        Returns:
            List of tight schedule alerts
        """
        tight_alerts = []
        
        df = voyage_data.copy()
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        
        for asset in df['asset'].unique():
            asset_data = df[df['asset'] == asset].sort_values('start_time')
            
            for i in range(len(asset_data) - 1):
                current = asset_data.iloc[i]
                next_leg = asset_data.iloc[i + 1]
                
                buffer_hours = (next_leg['start_time'] - current['end_time']).total_seconds() / 3600
                
                if 0 <= buffer_hours < min_buffer_hours:
                    alert = Alert(
                        alert_type="TIGHT_SCHEDULE",
                        severity=AlertSeverity.WARNING,
                        message=f"Asset {asset} has insufficient buffer time",
                        details={
                            'asset': asset,
                            'buffer_hours': round(buffer_hours, 2),
                            'required_hours': min_buffer_hours,
                            'between': f"{current.get('end_port', 'N/A')} and {next_leg.get('start_port', 'N/A')}"
                        }
                    )
                    tight_alerts.append(alert)
                    self.add_alert(alert)
        
        return tight_alerts
    
    def get_all_alerts(self, severity_filter: Optional[AlertSeverity] = None) -> List[Alert]:
        """
        Get all alerts, optionally filtered by severity.
        
        Args:
            severity_filter: Optional severity level to filter
        
        Returns:
            List of alerts
        """
        if severity_filter:
            return [a for a in self.alerts if a.severity == severity_filter]
        return self.alerts
    
    def generate_report(self) -> pd.DataFrame:
        """Generate a report of all alerts as DataFrame."""
        if not self.alerts:
            return pd.DataFrame()
        
        return pd.DataFrame([alert.to_dict() for alert in self.alerts])
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()


def run_all_checks(voyage_data: pd.DataFrame, 
                  berth_capacities: Optional[Dict[str, int]] = None,
                  min_buffer_hours: float = 2.0) -> AlertSystem:
    """
    Run all alert checks on voyage data.
    
    Args:
        voyage_data: DataFrame with voyage schedules
        berth_capacities: Optional dictionary of port capacities
        min_buffer_hours: Minimum buffer time in hours
    
    Returns:
        AlertSystem with all detected alerts
    """
    alert_system = AlertSystem()
    
    alert_system.check_asset_overlaps(voyage_data)
    alert_system.check_berth_capacity(voyage_data, berth_capacities)
    alert_system.check_tight_schedules(voyage_data, min_buffer_hours)
    
    return alert_system
