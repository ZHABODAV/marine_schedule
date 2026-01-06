#!/usr/bin/env python3
"""
Olya Year Schedule Generator
=============================

Generates year-long schedules for Olya barge-sea vessel coordination
with winter restrictions (barges only operate April-November due to river ice)

Usage:
    python generate_olya_year_schedule.py
"""

import sys
import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path


def generate_olya_year_schedule(
    input_file: str = "input/olya/voyage_config.csv",
    output_file: str = "input/olya/voyage_config_year.csv",
    start_date: date = date(2026, 4, 1),  # Start in April (after ice)
    end_date: date = date(2026, 11  , 30)  # End in November (before ice)
):
    """
    Generate year schedule for Olya with seasonal restrictions
    
    Barges work only April-November (navigation season)
    Sea vessels work year-round
    """
    
    print("=" * 80)
    print("OLYA YEAR SCHEDULE GENERATOR WITH WINTER RESTRICTIONS")
    print("=" * 80)
    
    # Load base voyages
    print(f"\n>> Loading base voyage configs from: {input_file}")
    df = pd.read_csv(input_file, delimiter=';', comment='#', encoding='utf-8')
    print(f"   [OK] Loaded {len(df)} operations from {df['voyage_id'].nunique()} voyages")
    
    # Calculate turnaround time
    barge_ops = df[df['vessel_id'].str.startswith('BR')]
    sea_ops = df[df['vessel_id'].str.startswith('SV')]
    
    # Average cycle time  
    barge_cycle_days = 14  # ~2 weeks for BKO→OYA→BKO
    sea_cycle_days = 18    # ~2.5 weeks for OYA→IRN→OYA
    
    print(f"\n   [i] Barge cycle time: {barge_cycle_days} days")
    print(f"   [i] Sea vessel cycle time: {sea_cycle_days} days")
    
    # Calculate navigation season duration
    season_days = (end_date - start_date).days
    print(f"\n   [i] Navigation season: {start_date} to {end_date} ({season_days} days)")
    
    # Generate voyages
    all_voyages = []
    voyage_counter = 1
    
    # Group by vessel
    vessels = df['vessel_id'].unique()
    
    for vessel_id in sorted(vessels):
        vessel_ops = df[df['vessel_id'] == vessel_id].copy()
        is_barge = vessel_id.startswith('BR')
        
        # Determine cycle time and operation period
        if is_barge:
            cycle_days = barge_cycle_days
            period_start = start_date
            period_end = end_date
        else:
            cycle_days = sea_cycle_days
            # Sea vessels work year-round
            period_start = date(2026, 1, 1)
            period_end = date(2026, 12, 31)
        
        # Calculate number of cycles
        period_days = (period_end - period_start).days
        num_cycles = period_days // cycle_days
        
        print(f"\n>> Processing {vessel_id} ({'BARGE' if is_barge else 'SEA VESSEL'})")
        print(f"   Operating period: {period_start} to {period_end}")
        print(f"   Cycles per period: {num_cycles}")
        
        vessel_voyage_count = 0
        
        # Generate cycles
        for cycle in range(num_cycles):
            # Calculate offset
            days_offset = cycle * cycle_days
            voyage_start = period_start + timedelta(days=days_offset)
            
            # Skip if outside season for barges
            if is_barge and (voyage_start.month < 4 or voyage_start.month > 11):
                continue
            
            # Create new voyage
            voyage_id = f"VOY_Y2026_{voyage_counter:03d}_{'B' if is_barge else 'S'}"
            voyage_counter += 1
            vessel_voyage_count += 1
            
            # Copy and adjust operations
            for _, op in vessel_ops.iterrows():
                new_op = op.copy()
                new_op['voyage_id'] = voyage_id
                
                # Adjust start_date if present
                if pd.notna(op['start_date']) and str(op['start_date']).strip():
                    orig_date = pd.to_datetime(op['start_date']).date()
                    new_date = voyage_start + (orig_date - pd.to_datetime(df['start_date'].dropna().iloc[0]).date())
                    new_op['start_date'] = new_date.strftime('%Y-%m-%d')
                else:
                    new_op['start_date'] = voyage_start.strftime('%Y-%m-%d')
                
                all_voyages.append(new_op)
        
        print(f"   Generated {vessel_voyage_count} voyages")
    
    # Create output dataframe
    result_df = pd.DataFrame(all_voyages)
    
    # Save
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_path, sep=';', index=False, encoding='utf-8')
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_voyages = result_df['voyage_id'].nunique()
    total_operations = len(result_df)
    
    print(f"Total voyages generated: {total_voyages}")
    print(f"Total operations: {total_operations}")
    print(f"Time span: {start_date} to {end_date}")
    
    print("\nVoyages by vessel type:")
    barge_voyages = len([v for v in result_df['voyage_id'].unique() if '_B' in v])
    sea_voyages = len([v for v in result_df['voyage_id'].unique() if '_S' in v])
    print(f"  Barge voyages (Apr-Nov only): {barge_voyages}")
    print(f"  Sea vessel voyages (year-round): {sea_voyages}")
    
    print(f"\n[OK] Year schedule saved to: {output_file}")
    print("=" * 80)
    
    return str(output_path)


if __name__ == "__main__":
    generate_olya_year_schedule()
