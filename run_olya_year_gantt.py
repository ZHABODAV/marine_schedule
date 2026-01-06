#!/usr/bin/env python3
"""
Run Olya Year Schedule Gantt Generator
=======================================

Generates Gantt charts for full year Olya schedule (111 voyages in 2026)
with winter restrictions for barges (Apr-Nov only)

Usage:
    python run_olya_year_gantt.py
"""

import sys
import logging
from pathlib import Path

from modules.olya_loader import OlyaLoader
from modules.olya_calculator import OlyaVoyageCalculator
from modules.olya_gantt_excel import OlyaGanttExcel
from modules.olya_coordinator import OlyaCoordinator


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("\n" + "=" * 80)
    logger.info("OLYA YEAR SCHEDULE GANTT GENERATOR (WITH WINTER RESTRICTIONS)")
    logger.info("=" * 80)
    
    # 1. Load voyage config year
    loader = OlyaLoader(input_dir='input/olya')
    
    # Temporarily point to year schedule
    original_file = Path('input/olya/voyage_config.csv')
    year_file = Path('input/olya/voyage_config_year.csv')
    backup_file = Path('input/olya/voyage_config_backup.csv')
    
    if not year_file.exists():
        logger.error(f"Year schedule not found: {year_file}")
        logger.error("Please run: python generate_olya_year_schedule.py")
        return 1
    
    # Backup original and use year plan
    if original_file.exists():
        original_file.rename(backup_file)
    year_file.rename(original_file)
    
    try:
        logger.info("\n>> Loading year schedule (111 voyages, Apr-Nov for barges)...")
        data = loader.load()
        
        logger.info(f"   Vessels: {len(data.vessels)}")
        logger.info(f"   Barges: {len(data.barges)}")
        logger.info(f"   Sea Vessels: {len(data.sea_vessels)}")
        logger.info(f"   Voyages: {len(set(c.voyage_id for c in data.voyage_configs))}")
        
        # 2. Calculate all voyages
        logger.info("\n>> Calculating voyages...")
        calculator = OlyaVoyageCalculator(data)
        data = calculator.calculate_all()
        
        logger.info(f"   Calculated: {len(data.calculated_voyages)} voyages")
        logger.info(f"   Total operations: {len([op for v in data.calculated_voyages.values() for op in v.operations])}")
        
        # 3. Coordination analysis
        logger.info("\n>> Analyzing barge-sea vessel coordination at Olya...")
        coordinator = OlyaCoordinator(data)
        analysis = coordinator.analyze()
        
        # 4. Generate Gantt charts
        logger.info("\n>> Generating Gantt charts...")
        gantt = OlyaGanttExcel(data, output_dir='output/olya')
        
        # Monthly Gantt charts
        logger.info("\n   Monthly Gantt charts:")
        gantt.generate_all_months()
        
        # Summary Gantt
        logger.info("\n   Summary Gantt (all months):")
        gantt.generate_summary_gantt()
        
        # 5. Statistics
        logger.info("\n" + "=" * 80)
        logger.info("STATISTICS")
        logger.info("=" * 80)
        
        total_ops = sum(len(v.operations) for v in data.calculated_voyages.values())
        barge_voyages = [v for v in data.calculated_voyages.values() if v.vessel_type == 'barge']
        sea_voyages = [v for v in data.calculated_voyages.values() if v.vessel_type == 'sea_vessel']
        
        total_cargo = sum(
            sum(op.qty_mt for op in v.operations if op.operation == 'loading')
            for v in data.calculated_voyages.values()
        )
        
        logger.info(f"  Total Voyages:      {len(data.calculated_voyages)}")
        logger.info(f"    Barge voyages:    {len(barge_voyages)} (Apr-Nov only)")
        logger.info(f"    Sea voyages:      {len(sea_voyages)} (year-round)")
        logger.info(f"  Total Operations:   {total_ops}")
        logger.info(f"  Total Cargo:        {total_cargo:,.0f} MT")
        
        # Coordination stats
        logger.info(f"\n  Olya Coordination:")
        logger.info(f"    Barge arrivals:   {analysis.get('barge_arrivals', 0)}")
        logger.info(f"    Sea departures:   {analysis.get('sea_departures', 0)}")
        logger.info(f"    Conflicts:        {len(analysis.get('conflicts', []))}")
        logger.info(f"    Demurrage hours:  {analysis.get('total_demurrage_hours', 0):.1f}h")
        
        logger.info("\n" + "=" * 80)
        logger.info("COMPLETED!")
        logger.info(f"  Monthly Gantt: output/olya/gantt_2026_*.xlsx")
        logger.info(f"  Summary Gantt: output/olya/gantt_all_months.xlsx")
        logger.info(f"  Schedule CSV:  output/olya/schedule_calculated.csv")
        logger.info("=" * 80)
        
        return 0
        
    finally:
        # Restore original files
        if original_file.exists():
            original_file.rename(year_file)
        if backup_file.exists():
            backup_file.rename(original_file)


if __name__ == "__main__":
    sys.exit(main())
