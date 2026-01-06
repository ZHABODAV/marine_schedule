"""
Generate Year-Long Vessel Schedule
==================================
Extends existing voyage plans to create a full year schedule by replicating 
voyages with appropriate time offsets based on vessel turnaround times.
"""

import pandas as pd
import sys
from datetime import datetime, timedelta
from pathlib import Path

def generate_year_schedule(input_file: str, output_file: str, start_date: str = "2026-01-01"):
    """
    Generate a year-long schedule from existing voyage plans.
    
    Args:
        input_file: Path to input voyage_plan.csv
        output_file: Path to output voyage_plan_year.csv
        start_date: Start date for the year schedule (YYYY-MM-DD)
    """
    print("=" * 80)
    print("YEAR-LONG SCHEDULE GENERATOR")
    print("=" * 80)
    
    # Load existing voyage plans
    print(f"\n>> Loading voyage plans from: {input_file}")
    df = pd.read_csv(input_file, sep=';', encoding='utf-8')
    print(f"   [OK] Loaded {len(df)} base voyages")
    
    # Parse dates
    df['laycan_start'] = pd.to_datetime(df['laycan_start'])
    df['laycan_end'] = pd.to_datetime(df['laycan_end'])
    
    # Calculate average voyage duration (laycan window)
    # Convert timedelta to days - using total_seconds to avoid dt accessor type issues
    df['laycan_days'] = (df['laycan_end'] - df['laycan_start']).apply(lambda x: x.days)
    avg_laycan_days = int(df['laycan_days'].mean())
    print(f"   [i] Average laycan window: {avg_laycan_days} days")
    
    # Estimate vessel turnaround time based on cargo type and route
    # Typical turnaround: voyage time + port time + positioning
    # Using simplified model: 2x laycan window as turnaround estimate
    turnaround_days = avg_laycan_days * 2
    print(f"   [i] Estimated vessel turnaround: {turnaround_days} days")
    
    # Start date for year schedule
    year_start = pd.to_datetime(start_date)
    year_end = year_start + timedelta(days=365)
    print(f"\n>> Generating schedule from {year_start.date()} to {year_end.date()}")
    
    # Generate voyages
    all_voyages = []
    
    # Group by vessel to ensure proper turnaround
    for vessel_id in df['vessel_id'].unique():
        vessel_voyages = df[df['vessel_id'] == vessel_id].copy()
        vessel_voyages = vessel_voyages.sort_values('laycan_start')
        
        print(f"\n>> Processing vessel: {vessel_id}")
        print(f"   Base voyages: {len(vessel_voyages)}")
        
        # Calculate how many cycles we can fit in a year
        base_cycle_duration = (vessel_voyages['laycan_start'].iloc[-1] - 
                              vessel_voyages['laycan_start'].iloc[0]).days + turnaround_days
        
        if base_cycle_duration == 0:
            base_cycle_duration = turnaround_days
            
        cycles_per_year = max(1, int(365 / base_cycle_duration))
        print(f"   Cycle duration: {base_cycle_duration} days")
        print(f"   Cycles per year: {cycles_per_year}")
        
        voyage_counter = 1
        current_date = year_start
        
        while current_date < year_end:
            for _, base_voyage in vessel_voyages.iterrows():
                # Calculate time offset from original voyage
                original_start = base_voyage['laycan_start']
                days_offset = (current_date - year_start).days
                
                # Create new voyage with offset dates
                new_voyage = base_voyage.copy()
                new_voyage['laycan_start'] = year_start + timedelta(days=days_offset)
                new_voyage['laycan_end'] = new_voyage['laycan_start'] + timedelta(days=int(base_voyage['laycan_days']))
                
                # Update voyage ID to be unique
                base_id = base_voyage['voyage_id'].split('_')[0]
                new_voyage['voyage_id'] = f"{base_id}_Y{year_start.year}_{voyage_counter:03d}"
                
                # Only add if within year boundary
                if new_voyage['laycan_start'] < year_end:
                    all_voyages.append(new_voyage)
                    voyage_counter += 1
                
                # Move to next voyage slot (with turnaround time)
                current_date += timedelta(days=turnaround_days)
                
                if current_date >= year_end:
                    break
            
            # If we ran through all vessel's voyages, continue the cycle
            current_date = new_voyage['laycan_end'] + timedelta(days=turnaround_days // len(vessel_voyages))
        
        print(f"   Generated {voyage_counter - 1} voyages for the year")
    
    # Create output dataframe
    df_year = pd.DataFrame(all_voyages)
    
    if len(df_year) == 0:
        print("\n[ERROR] No voyages generated!")
        return
    
    # Sort by date
    df_year = df_year.sort_values(['laycan_start', 'vessel_id'])
    
    # Format dates back to strings using apply (works with both datetime and Timestamp objects)
    df_year['laycan_start'] = df_year['laycan_start'].apply(
        lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else ''
    )
    df_year['laycan_end'] = df_year['laycan_end'].apply(
        lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else ''
    )
    
    # Drop temporary columns
    df_year = df_year.drop(columns=['laycan_days'], errors='ignore')
    
    # Save output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df_year.to_csv(output_file, sep=';', index=False, encoding='utf-8')
    
    print(f"\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total voyages generated: {len(df_year)}")
    print(f"Vessels utilized: {df_year['vessel_id'].nunique()}")
    print(f"Time span: {df_year['laycan_start'].min()} to {df_year['laycan_end'].max()}")
    print(f"\nVoyages by vessel:")
    for vessel in df_year['vessel_id'].unique():
        count = len(df_year[df_year['vessel_id'] == vessel])
        print(f"  {vessel}: {count} voyages")
    
    print(f"\n[OK] Year schedule saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    # Default paths
    input_file = "input/deepsea/voyage_plan.csv"
    output_file = "input/deepsea/voyage_plan_year.csv"
    start_date = "2026-01-01"
    
    # Command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        start_date = sys.argv[3]
    
    try:
        generate_year_schedule(input_file, output_file, start_date)
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
