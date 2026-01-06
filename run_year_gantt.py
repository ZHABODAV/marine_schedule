#!/usr/bin/env python3
"""
Run Year Schedule Gantt Generator
==================================

Generates Gantt charts for full year schedule (107 voyages in 2026)

Usage:
    python run_year_gantt.py
"""

import sys
import logging
from pathlib import Path

from modules.deepsea_loader import DeepSeaLoader
from modules.deepsea_calculator import DeepSeaCalculator
from modules.deepsea_gantt_excel import DeepSeaGanttExcel


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
    logger.info("YEAR SCHEDULE GANTT GENERATOR")
    logger.info("=" * 80)
    
    # 1. Load voyage plan year
    year_file = Path('input/deepsea/voyage_plan_year.csv')
    
    if not year_file.exists():
        logger.error(f"Year schedule not found: {year_file}")
        logger.error("Please run: python generate_year_schedule.py")
        return 1

    loader = DeepSeaLoader(input_dir='input/deepsea', voyage_plan_filename='voyage_plan_year.csv')
    
    try:
        logger.info("\n>> Loading year schedule (107 voyages)...")
        data = loader.load()
        
        logger.info(f"   Vessels: {len(data.vessels)}")
        logger.info(f"   Voyages: {len(data.voyage_plans)}")
        
        # 2. Calculate all voyages
        logger.info("\n>> Calculating voyages...")
        calculator = DeepSeaCalculator(data)
        data = calculator.calculate_all()
        
        logger.info(f"   Calculated: {len(data.calculated_voyages)} voyages")
        
        # 3. Generate Gantt charts
        logger.info("\n>> Generating Gantt charts...")
        gantt = DeepSeaGanttExcel(data, output_dir='output/deepsea')
        
        # Monthly Gantt charts
        logger.info("\n   Monthly Gantt charts:")
        files = gantt.generate_all_months(scenario_name="YEAR2026")
        
        logger.info(f"\n   Generated {len(files)} monthly Gantt charts")
        
        # Fleet overview
        logger.info("\n   Fleet Overview:")
        overview_file = gantt.generate_fleet_overview(scenario_name="YEAR2026")
        
        # 4. Statistics
        logger.info("\n" + "=" * 80)
        logger.info("STATISTICS")
        logger.info("=" * 80)
        
        total_cargo = sum(v.qty_mt for v in data.calculated_voyages.values())
        total_cost = sum(v.total_cost_usd for v in data.calculated_voyages.values())
        total_bunker = sum(v.total_bunker_cost_usd for v in data.calculated_voyages.values())
        total_hire = sum(v.hire_cost_usd for v in data.calculated_voyages.values())
        total_operational = sum(v.operational_cost_allocation for v in data.calculated_voyages.values())
        total_overhead = sum(v.overhead_cost_allocation for v in data.calculated_voyages.values())
        
        logger.info(f"  Voyages:            {len(data.calculated_voyages)}")
        logger.info(f"  Cargo:              {total_cargo:,.0f} MT")
        logger.info(f"  Total Costs:        ${total_cost:,.0f}")
        logger.info(f"    - Hire Costs:     ${total_hire:,.0f}")
        logger.info(f"    - Bunker:         ${total_bunker:,.0f}")
        logger.info(f"    - Operational:    ${total_operational:,.0f}")
        logger.info(f"    - Overhead:       ${total_overhead:,.0f}")
        
        logger.info("\n" + "=" * 80)
        logger.info("COMPLETED!")
        logger.info(f"  Monthly Gantt: output/deepsea/gantt_deepsea_2026_*.xlsx")
        logger.info(f"  Fleet Overview: {overview_file}")
        logger.info("=" * 80)
        
        return 0
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
