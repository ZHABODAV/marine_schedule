#!/usr/bin/env python3
"""
Unified Scheduler System
========================

Single entry point for all scheduling modules:
- Olya Transshipment Planning
- Deep Sea Voyage Planning  
- Balakovo Berth Planning

Usage:
    python scheduler.py                    # Interactive menu
    python scheduler.py --olya            # Run Olya module
    python scheduler.py --deepsea         # Run Deep Sea module
    python scheduler.py --balakovo        # Run Balakovo module
    python scheduler.py --all             # Run all modules
"""

import argparse
import logging
import sys
from pathlib import Path

# Olya imports
try:
    from modules.olya_loader import OlyaLoader
    from modules.olya_calculator import OlyaVoyageCalculator
    from modules.olya_coordinator import OlyaCoordinator
    from modules.olya_gantt_excel import OlyaGanttExcel
    OLYA_AVAILABLE = True
except ImportError as e:
    OLYA_AVAILABLE = False
    OLYA_ERROR = str(e)

# Deep Sea imports
try:
    from modules.deepsea_loader import DeepSeaLoader
    from modules.deepsea_calculator import DeepSeaCalculator
    from modules.deepsea_gantt_excel import DeepSeaGanttExcel
    from modules.deepsea_scenarios import ScenarioManager
    DEEPSEA_AVAILABLE = True
except ImportError as e:
    DEEPSEA_AVAILABLE = False
    DEEPSEA_ERROR = str(e)

# Balakovo imports
try:
    from modules.balakovo_loader import BalakovoLoader
    from modules.balakovo_planner import BalakovoPlanner
    from modules.balakovo_gantt import BalakovoGanttExcel
    BALAKOVO_AVAILABLE = True
except ImportError as e:
    BALAKOVO_AVAILABLE = False
    BALAKOVO_ERROR = str(e)


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def print_banner():
    """Print application banner"""
    print("\n" + "=" * 70)
    print(" UNIFIED SCHEDULER SYSTEM")
    print("   Maritime Operations Planning Suite")
    print("=" * 70)


def print_menu():
    """Print interactive menu"""
    print("\nAvailable Modules:")
    print("=" * 70)
    
    if OLYA_AVAILABLE:
        print("  [1]  Olya Transshipment Planning")
        print("      Barge-to-vessel transshipment coordination")
    else:
        print(f"  [ ] Olya - Not Available ({OLYA_ERROR})")
    
    if DEEPSEA_AVAILABLE:
        print("\n  [2]  Deep Sea Voyage Planning")
        print("      Long-haul tanker voyage calculations")
    else:
        print(f"\n  [ ] Deep Sea - Not Available ({DEEPSEA_ERROR})")
    
    if BALAKOVO_AVAILABLE:
        print("\n  [3]  Balakovo Berth Planning")
        print("      River terminal berth scheduling")
    else:
        print(f"\n  [ ] Balakovo - Not Available ({BALAKOVO_ERROR})")
    
    print("\n  [4]  Run All Available Modules")
    print("  [0]  Exit")
    print("=" * 70)


def run_olya(input_dir: str = "input/olya", output_dir: str = "output/olya"):
    """Run Olya transshipment planning"""
    logger = logging.getLogger(__name__)
    
    if not OLYA_AVAILABLE:
        logger.error(f" Olya module not available: {OLYA_ERROR}")
        return False
    
    logger.info("\n" + "=" * 70)
    logger.info(" OLYA TRANSSHIPMENT PLANNING")
    logger.info("=" * 70)
    
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 1. Load data
        loader = OlyaLoader(input_dir=input_dir)
        data = loader.load()
        
        if not data.voyage_configs:
            logger.error(" No voyage configuration found!")
            return False
        
        # 2. Calculate voyages
        calculator = OlyaVoyageCalculator(data)
        data = calculator.calculate_all()
        
        # 3. Coordinate operations
        coordinator = OlyaCoordinator(data)
        analysis = coordinator.analyze()
        
        # 4. Generate reports
        gantt = OlyaGanttExcel(data, output_dir)
        gantt.generate_schedule()
        
        logger.info("\n" + "=" * 70)
        logger.info(" OLYA PLANNING COMPLETE!")
        logger.info(f"   Results: {output_dir}/")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f" Error in Olya module: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_deepsea(input_dir: str = "input/deepsea", output_dir: str = "output/deepsea"):
    """Run Deep Sea voyage planning"""
    logger = logging.getLogger(__name__)
    
    if not DEEPSEA_AVAILABLE:
        logger.error(f"Deep Sea module not available: {DEEPSEA_ERROR}")
        return False
    
    logger.info("\n" + "=" * 70)
    logger.info(" DEEP SEA VOYAGE PLANNING")
    logger.info("=" * 70)
    
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 1. Load data
        loader = DeepSeaLoader(input_dir=input_dir)
        data = loader.load()
        
        if not data.voyage_plans:
            logger.error(" No voyage plans found!")
            return False
        
        # 2. Calculate voyages
        calculator = DeepSeaCalculator(data)
        data = calculator.calculate_all()
        
        # 3. Run scenarios (if scenarios file exists)
        from modules.deepsea_scenarios import ScenarioManager
        manager = ScenarioManager(data, input_dir=input_dir)
        scenarios = manager.load_scenarios()
        
        if scenarios:
            manager.calculate_all_scenarios()
            
            # Export scenario comparison
            comparison_path = Path(output_dir) / "scenario_comparison.xlsx"
            manager.export_comparison(str(comparison_path))
        
        # 4. Generate reports
        gantt = DeepSeaGanttExcel(data, output_dir)
        gantt.generate_schedule()
        
        logger.info("\n" + "=" * 70)
        logger.info(" DEEP SEA PLANNING COMPLETE!")
        logger.info(f"   Results: {output_dir}/")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f" Error in Deep Sea module: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_balakovo(input_dir: str = "input/balakovo", output_dir: str = "output/balakovo"):
    """Run Balakovo berth planning"""
    logger = logging.getLogger(__name__)
    
    if not BALAKOVO_AVAILABLE:
        logger.error(f" Balakovo module not available: {BALAKOVO_ERROR}")
        return False
    
    logger.info("\n" + "=" * 70)
    logger.info(" BALAKOVO BERTH PLANNING")
    logger.info("=" * 70)
    
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 1. Load data
        loader = BalakovoLoader(input_dir=input_dir)
        data = loader.load()
        
        if not data.cargo_plans:
            logger.error(" No cargo plans found!")
            return False
        
        # 2. Plan berth schedule
        planner = BalakovoPlanner(data)
        data = planner.plan()
        
        # 3. Generate reports
        gantt = BalakovoGanttExcel(data, output_dir)
        gantt.generate_schedule()
        
        # 4. Export CSV
        import pandas as pd
        
        slots_data = []
        for schedule in data.schedules.values():
            for slot in schedule.slots:
                slots_data.append({
                    'slot_id': slot.slot_id,
                    'berth_id': slot.berth_id,
                    'vessel_id': slot.vessel_id,
                    'vessel_name': slot.vessel_name,
                    'cargo_id': slot.cargo_id,
                    'cargo_type': slot.cargo_type,
                    'qty_mt': slot.qty_mt,
                    'destination': slot.destination,
                    'eta': slot.eta,
                    'berthing_start': slot.berthing_start,
                    'departure': slot.departure,
                    'waiting_hours': slot.waiting_hours,
                    'loading_hours': slot.loading_hours,
                    'status': slot.status.value
                })
        
        if slots_data:
            df = pd.DataFrame(slots_data)
            csv_path = Path(output_dir) / "berth_schedule.csv"
            df.to_csv(csv_path, index=False, sep=';')
        
        logger.info("\n" + "=" * 70)
        logger.info(" BALAKOVO PLANNING COMPLETE!")
        logger.info(f"   Results: {output_dir}/")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f" Error in Balakovo module: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_modules():
    """Run all available modules"""
    logger = logging.getLogger(__name__)
    
    results = {}
    
    if OLYA_AVAILABLE:
        logger.info("\n" + "  Running Olya module...")
        results['olya'] = run_olya()
    
    if DEEPSEA_AVAILABLE:
        logger.info("\n" + "  Running Deep Sea module...")
        results['deepsea'] = run_deepsea()
    
    if BALAKOVO_AVAILABLE:
        logger.info("\n" + "  Running Balakovo module...")
        results['balakovo'] = run_balakovo()
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info(" EXECUTION SUMMARY")
    logger.info("=" * 70)
    
    for module, success in results.items():
        status = " Success" if success else " Failed"
        logger.info(f"  {module.upper():12} {status}")
    
    logger.info("=" * 70)
    
    return all(results.values())


def interactive_mode():
    """Run in interactive menu mode"""
    logger = logging.getLogger(__name__)
    
    while True:
        print_menu()
        
        try:
            choice = input("\nSelect module [0-4]: ").strip()
            
            if choice == '0':
                logger.info("\n Goodbye!")
                return 0
            
            elif choice == '1' and OLYA_AVAILABLE:
                run_olya()
                input("\nPress Enter to continue...")
            
            elif choice == '2' and DEEPSEA_AVAILABLE:
                run_deepsea()
                input("\nPress Enter to continue...")
            
            elif choice == '3' and BALAKOVO_AVAILABLE:
                run_balakovo()
                input("\nPress Enter to continue...")
            
            elif choice == '4':
                run_all_modules()
                input("\nPress Enter to continue...")
            
            else:
                logger.warning(" Invalid choice or module not available")
                input("\nPress Enter to continue...")
        
        except KeyboardInterrupt:
            logger.info("\n\n Goodbye!")
            return 0
        except Exception as e:
            logger.error(f"\n Error: {e}")
            input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Unified Scheduler System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--olya', action='store_true', help='Run Olya transshipment planning')
    parser.add_argument('--deepsea', action='store_true', help='Run Deep Sea voyage planning')
    parser.add_argument('--balakovo', action='store_true', help='Run Balakovo berth planning')
    parser.add_argument('--all', action='store_true', help='Run all modules')
    parser.add_argument('--input-olya', default='input/olya', help='Olya input directory')
    parser.add_argument('--input-deepsea', default='input/deepsea', help='Deep Sea input directory')
    parser.add_argument('--input-balakovo', default='input/balakovo', help='Balakovo input directory')
    parser.add_argument('--output-olya', default='output/olya', help='Olya output directory')
    parser.add_argument('--output-deepsea', default='output/deepsea', help='Deep Sea output directory')
    parser.add_argument('--output-balakovo', default='output/balakovo', help='Balakovo output directory')
    
    args = parser.parse_args()
    
    setup_logging()
    print_banner()
    
    # Command line mode
    if args.all:
        return 0 if run_all_modules() else 1
    
    if args.olya:
        return 0 if run_olya(args.input_olya, args.output_olya) else 1
    
    if args.deepsea:
        return 0 if run_deepsea(args.input_deepsea, args.output_deepsea) else 1
    
    if args.balakovo:
        return 0 if run_balakovo(args.input_balakovo, args.output_balakovo) else 1
    
    # Interactive mode (default)
    return interactive_mode()


if __name__ == "__main__":
    sys.exit(main())
