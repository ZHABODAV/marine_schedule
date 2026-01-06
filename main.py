"""
Main Entry Point for Maritime Voyage Calculation and Scheduling System
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

# Import modules
from modules.voyage_calculator import VoyageCalculator, calculate_voyage_schedule
from modules.voyage_tables import VoyageTableGenerator, create_voyage_tables
from modules.excel_gantt import create_gantt_charts
from modules.alerts import AlertSystem, run_all_checks
from modules.berth_utilization import BerthUtilizationAnalyzer, analyze_berth_utilization
from modules.balakovo_report import BalakovoReportGenerator, generate_balakovo_report
from tools.create_templates import create_all_templates


def main():
    """Main entry point for the application."""
    print("WARNING: main.py is deprecated and will be removed in a future version.")
    print("Please use scheduler.py instead for a unified interface.")
    print("Redirecting to scheduler.py logic where possible...\n")
    
    parser = argparse.ArgumentParser(
        description='Maritime Voyage Calculation and Scheduling System (DEPRECATED - use scheduler.py)'
    )
    
    parser.add_argument(
        'command',
        choices=['calculate', 'gantt', 'alerts', 'utilization', 'balakovo', 'templates'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='Input Excel file path'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path'
    )
    
    parser.add_argument(
        '--port',
        type=str,
        default='Balakovo',
        help='Port name for Balakovo reports'
    )
    
    parser.add_argument(
        '--capacity',
        type=str,
        help='Berth capacity config file (JSON format)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == 'templates':
            # Create templates
            print("Creating Excel templates...")
            output_dir = args.output if args.output else 'input'
            create_all_templates(output_dir)
            print(f"Templates created in '{output_dir}' directory")
            
        elif args.command == 'calculate':
            # Calculate voyage schedule
            if not args.input:
                print("Error: Input file required for calculate command")
                sys.exit(1)
            
            print(f"Calculating voyage schedule from {args.input}...")
            output_file = args.output if args.output else 'output/voyage_schedule.xlsx'
            
            result = calculate_voyage_schedule(args.input, output_file)
            print(f"Voyage schedule saved to {output_file}")
            print(f"Total legs calculated: {len(result)}")
            
        elif args.command == 'gantt':
            # Create Gantt charts
            if not args.input:
                print("Error: Input file required for gantt command")
                sys.exit(1)
            
            print(f"Creating Gantt charts from {args.input}...")
            output_file = args.output if args.output else 'output/gantt_charts.xlsx'
            
            voyage_data = pd.read_excel(args.input)
            create_gantt_charts(voyage_data, output_file)
            print(f"Gantt charts saved to {output_file}")
            
        elif args.command == 'alerts':
            # Run alert checks
            if not args.input:
                print("Error: Input file required for alerts command")
                sys.exit(1)
            
            print(f"Running alert checks on {args.input}...")
            voyage_data = pd.read_excel(args.input)
            
            # Load berth capacity if provided
            berth_capacity = None
            if args.capacity:
                import json
                with open(args.capacity) as f:
                    berth_capacity = json.load(f)
            
            alert_system = run_all_checks(voyage_data, berth_capacity)
            
            # Display alerts
            alerts = alert_system.get_all_alerts()
            print(f"\nFound {len(alerts)} alerts:")
            for alert in alerts:
                print(f"  {alert}")
            
            # Save report if output specified
            if args.output:
                report = alert_system.generate_report()
                report.to_excel(args.output, index=False)
                print(f"\nAlert report saved to {args.output}")
            
        elif args.command == 'utilization':
            # Analyze berth utilization
            if not args.input:
                print("Error: Input file required for utilization command")
                sys.exit(1)
            
            print(f"Analyzing berth utilization from {args.input}...")
            output_file = args.output if args.output else 'output/berth_utilization.xlsx'
            
            voyage_data = pd.read_excel(args.input)
            analyzer = analyze_berth_utilization(voyage_data, output_file)
            print(f"Berth utilization report saved to {output_file}")
            
        elif args.command == 'balakovo':
            # Generate Balakovo report
            if not args.input:
                print("Error: Input file required for balakovo command")
                sys.exit(1)
            
            print(f"Generating Balakovo report from {args.input}...")
            output_file = args.output if args.output else 'output/balakovo_report.xlsx'
            
            voyage_data = pd.read_excel(args.input)
            generator = generate_balakovo_report(voyage_data, output_file, args.port)
            
            # Display statistics
            stats = generator.get_operation_statistics(args.port)
            print(f"\nBalakovo Operations Statistics ({args.port}):")
            print(f"  Total operations: {stats.get('total_operations', 0)}")
            print(f"  Unique assets: {stats.get('unique_assets', 0)}")
            print(f"  Total cargo: {stats.get('total_cargo', 0)}")
            print(f"\nReport saved to {output_file}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_full_analysis(input_file: str, output_dir: str = 'output'):
    """
    Run full analysis pipeline on voyage data.
    
    Args:
        input_file: Path to input Excel file
        output_dir: Directory for output files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("MARITIME VOYAGE ANALYSIS - FULL PIPELINE")
    print("=" * 60)
    
    # Load data
    print(f"\n1. Loading data from {input_file}...")
    voyage_data = pd.read_excel(input_file)
    print(f"   Loaded {len(voyage_data)} voyage records")
    
    # Calculate schedules
    print("\n2. Calculating voyage schedules...")
    calculator = VoyageCalculator()
    schedule = calculator.calculate_voyage_from_df(voyage_data)
    schedule_file = output_path / 'voyage_schedule.xlsx'
    schedule.to_excel(schedule_file, index=False)
    print(f"   Schedule saved to {schedule_file}")
    
    # Create tables
    print("\n3. Generating voyage tables...")
    tables_file = output_path / 'voyage_tables.xlsx'
    create_voyage_tables(schedule, str(tables_file))
    print(f"   Tables saved to {tables_file}")
    
    # Create Gantt charts
    print("\n4. Creating Gantt charts...")
    gantt_file = output_path / 'gantt_charts.xlsx'
    create_gantt_charts(schedule, str(gantt_file))
    print(f"   Gantt charts saved to {gantt_file}")
    
    # Run alerts
    print("\n5. Running alert checks...")
    alert_system = run_all_checks(schedule)
    alerts = alert_system.get_all_alerts()
    print(f"   Found {len(alerts)} alerts")
    if alerts:
        alert_file = output_path / 'alerts.xlsx'
        alert_system.generate_report().to_excel(alert_file, index=False)
        print(f"   Alert report saved to {alert_file}")
    
    # Analyze utilization
    print("\n6. Analyzing berth utilization...")
    util_file = output_path / 'berth_utilization.xlsx'
    analyze_berth_utilization(schedule, str(util_file))
    print(f"   Utilization report saved to {util_file}")
    
    # Balakovo report
    print("\n7. Generating Balakovo report...")
    balakovo_file = output_path / 'balakovo_report.xlsx'
    generate_balakovo_report(schedule, str(balakovo_file))
    print(f"   Balakovo report saved to {balakovo_file}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print(f"All outputs saved to '{output_dir}' directory")
    print("=" * 60)


if __name__ == "__main__":
    # Check if running with command-line arguments
    if len(sys.argv) > 1:
        main()
    else:
        # Interactive mode or demo
        print("Maritime Voyage Calculation and Scheduling System")
        print("\nUsage:")
        print("  python main.py <command> [options]")
        print("\nCommands:")
        print("  templates    - Create Excel input templates")
        print("  calculate    - Calculate voyage schedules")
        print("  gantt        - Create Gantt charts")
        print("  alerts       - Run alert checks")
        print("  utilization  - Analyze berth utilization")
        print("  balakovo     - Generate Balakovo reports")
        print("\neFor detailed help:")
        print("  python main.py --help")
