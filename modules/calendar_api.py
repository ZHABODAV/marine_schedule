"""
Operational Calendar API Module
Provides endpoints for calendar data aggregation
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
from pathlib import Path


class CalendarAPI:
    """API for operational calendar data"""
    
    def __init__(self, deepsea_data=None, olya_data=None, balakovo_data=None):
        self.deepsea_data = deepsea_data
        self.olya_data = olya_data
        self.balakovo_data = balakovo_data
    
    def get_all_events(self, start_date: str = None, end_date: str = None, 
                      module: str = 'all', vessel: str = 'all') -> Dict[str, Any]:
        """
        Get all calendar events from all modules
        
        Args:
            start_date: Filter start date (YYYY-MM-DD)
            end_date: Filter end date (YYYY-MM-DD)
            module: Filter by module (all/deepsea/olya/balakovo)
            vessel: Filter by vessel ID
            
        Returns:
            Dictionary with events and metadata
        """
        events = []
        
        # Collect from all modules
        if module in ['all', 'deepsea'] and self.deepsea_data:
            events.extend(self._get_deepsea_events())
        
        if module in ['all', 'olya'] and self.olya_data:
            events.extend(self._get_olya_events())
        
        if module in ['all', 'balakovo'] and self.balakovo_data:
            events.extend(self._get_balakovo_events())
        
        # Apply filters
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            events = [e for e in events if datetime.fromisoformat(e['end'].replace('Z', '')) >= start]
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            events = [e for e in events if datetime.fromisoformat(e['start'].replace('Z', '')) <= end]
        
        if vessel != 'all':
            events = [e for e in events if e['vessel'] == vessel]
        
        return {
            'events': events,
            'total_count': len(events),
            'modules': list(set(e['module'] for e in events)),
            'vessels': list(set(e['vessel'] for e in events)),
            'date_range': {
                'start': min((e['start'] for e in events)) if events else None,
                'end': max((e['end'] for e in events)) if events else None
            }
        }
    
    def _get_deepsea_events(self) -> List[Dict[str, Any]]:
        """Extract events from Deep Sea data"""
        events = []
        
        if not self.deepsea_data or not hasattr(self.deepsea_data, 'calculated_voyages'):
            return events
        
        for voyage_id, voyage in self.deepsea_data.calculated_voyages.items():
            events.append({
                'id': voyage_id,
                'title': f"{voyage.vessel_id}: {voyage.cargo_type}",
                'module': 'deepsea',
                'vessel': voyage.vessel_id,
                'start': voyage.laycan_start.isoformat() if hasattr(voyage.laycan_start, 'isoformat') else str(voyage.laycan_start),
                'end': voyage.laycan_end.isoformat() if hasattr(voyage.laycan_end, 'isoformat') else str(voyage.laycan_end),
                'status': self._determine_status(voyage.laycan_start, voyage.laycan_end),
                'cargo': voyage.qty_mt,
                'cost': voyage.total_cost_usd,
                'route': f"{voyage.load_port} → {voyage.discharge_port}",
                'details': {
                    'cargo_type': voyage.cargo_type,
                    'distance_nm': voyage.total_distance_nm,
                    'duration_days': voyage.voyage_duration_days,
                    'bunker_cost': voyage.total_bunker_cost_usd,
                    'hire_cost': voyage.hire_cost_usd
                }
            })
        
        return events
    
    def _get_olya_events(self) -> List[Dict[str, Any]]:
        """Extract events from Olya data"""
        events = []
        
        if not self.olya_data:
            return events
        
        # Check if we have voyage configs
        if hasattr(self.olya_data, 'voyage_configs'):
            for config in self.olya_data.voyage_configs:
                events.append({
                    'id': f"OLYA_{config.get('id', len(events))}",
                    'title': f"{config.get('vessel_name', 'Unknown')}: {config.get('cargo_name', 'Cargo')}",
                    'module': 'olya',
                    'vessel': config.get('vessel_name', 'Unknown'),
                    'start': config.get('start_date', datetime.now().isoformat()),
                    'end': config.get('end_date', (datetime.now() + timedelta(days=7)).isoformat()),
                    'status': 'planned',
                    'cargo': config.get('cargo_qty', 0),
                    'cost': config.get('total_cost', 0),
                    'route': f"{config.get('from_port', 'Origin')} → {config.get('to_port', 'Destination')}",
                    'details': config
                })
        
        return events
    
    def _get_balakovo_events(self) -> List[Dict[str, Any]]:
        """Extract events from Balakovo data"""
        events = []
        
        if not self.balakovo_data:
            return events
        
        # Placeholder for Balakovo events extraction
        # Implementation depends on Balakovo data structure
        
        return events
    
    def _determine_status(self, start_date, end_date) -> str:
        """Determine voyage status based on dates"""
        now = datetime.now()
        
        # Convert to datetime if string
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', ''))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', ''))
        
        if now < start_date:
            return 'planned'
        elif now > end_date:
            return 'completed'
        else:
            return 'in-progress'
    
    def get_statistics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Get calendar statistics
        
        Returns:
            Dictionary with aggregated statistics
        """
        all_events = self.get_all_events(start_date, end_date)['events']
        
        return {
            'total_voyages': len(all_events),
            'total_vessels': len(set(e['vessel'] for e in all_events)),
            'total_cargo_mt': sum(e.get('cargo', 0) for e in all_events),
            'total_cost_usd': sum(e.get('cost', 0) for e in all_events),
            'by_module': self._stats_by_module(all_events),
            'by_status': self._stats_by_status(all_events),
            'by_vessel': self._stats_by_vessel(all_events)
        }
    
    def _stats_by_module(self, events: List[Dict]) -> Dict[str, int]:
        """Count events by module"""
        stats = {}
        for event in events:
            module = event['module']
            stats[module] = stats.get(module, 0) + 1
        return stats
    
    def _stats_by_status(self, events: List[Dict]) -> Dict[str, int]:
        """Count events by status"""
        stats = {}
        for event in events:
            status = event['status']
            stats[status] = stats.get(status, 0) + 1
        return stats
    
    def _stats_by_vessel(self, events: List[Dict]) -> Dict[str, int]:
        """Count events by vessel"""
        stats = {}
        for event in events:
            vessel = event['vessel']
            stats[vessel] = stats.get(vessel, 0) + 1
        return stats
    
    def get_upcoming_events(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get upcoming events
        
        Args:
            days: Number of days to look ahead
            limit: Maximum number of events to return
            
        Returns:
            List of upcoming events sorted by date
        """
        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        all_events = self.get_all_events(end_date=end_date)['events']
        
        # Filter to future events only
        now = datetime.now()
        upcoming = [
            e for e in all_events 
            if datetime.fromisoformat(e['start'].replace('Z', '')) > now
        ]
        
        # Sort by start date
        upcoming.sort(key=lambda e: e['start'])
        
        return upcoming[:limit]
    
    def export_to_csv(self, filename: str = None, **filters) -> str:
        """
        Export calendar events to CSV
        
        Args:
            filename: Output filename (optional)
            **filters: Filter parameters
            
        Returns:
            Path to exported file
        """
        events = self.get_all_events(**filters)['events']
        
        # Convert to DataFrame
        df = pd.DataFrame(events)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"calendar_export_{timestamp}.csv"
        
        # Ensure output directory exists
        output_path = Path('output') / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export
        df.to_csv(output_path, index=False)
        
        return str(output_path)
    
    def export_to_excel(self, filename: str = None, **filters) -> str:
        """
        Export calendar events to Excel with multiple sheets
        
        Args:
            filename: Output filename (optional)
            **filters: Filter parameters
            
        Returns:
            Path to exported file
        """
        events = self.get_all_events(**filters)['events']
        stats = self.get_statistics()
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"calendar_export_{timestamp}.xlsx"
        
        # Ensure output directory exists
        output_path = Path('output') / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # All events sheet
            df_events = pd.DataFrame(events)
            if not df_events.empty and 'details' in df_events.columns:
                df_events = df_events.drop('details', axis=1)
            df_events.to_excel(writer, sheet_name='All Events', index=False)
            
            # Statistics sheet
            df_stats = pd.DataFrame([stats])
            df_stats.to_excel(writer, sheet_name='Statistics', index=False)
            
            # By Module sheet
            module_events = {}
            for event in events:
                module = event['module']
                if module not in module_events:
                    module_events[module] = []
                module_events[module].append(event)
            
            for module, mod_events in module_events.items():
                df_module = pd.DataFrame(mod_events)
                if not df_module.empty and 'details' in df_module.columns:
                    df_module = df_module.drop('details', axis=1)
                sheet_name = f"{module.capitalize()}"[:31]  # Excel sheet name limit
                df_module.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return str(output_path)
