"""
Year Schedule Integration Example
==================================
Demonstrates how to integrate year schedule optimization into workflows
"""

from modules.deepsea_loader import DeepSeaLoader
from modules.deepsea_calculator import DeepSeaCalculator
from modules.year_schedule_optimizer import (
    YearScheduleOptimizer,
    YearScheduleManager,
    YearScheduleConfig
)
from datetime import datetime


def example_1_basic_optimization():
    """Example 1: Basic year schedule optimization"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Year Schedule Optimization")
    print("="*80)
    
    # Load data
    print("\n>> Loading vessel and voyage data...")
    loader = DeepSeaLoader()
    data = loader.load()
    
    # Calculate base voyages
    print(">> Calculating base voyages...")
    calculator = DeepSeaCalculator(data)
    data = calculator.calculate_all()
    
    # Create optimizer
    print(">> Initializing optimizer...")
    optimizer = YearScheduleOptimizer(data)
    
    # Run optimization
    print(">> Running balanced optimization...")
    result = optimizer.optimize("balance")
    
    # Display results
    print(f"\n Optimization Complete!")
    print(f"  Strategy: {result.strategy}")
    print(f"  Total Revenue: ${result.total_revenue_usd:,.0f}")
    print(f"  Total Cost: ${result.total_cost_usd:,.0f}")
    print(f"  Total Profit: ${result.total_profit_usd:,.0f}")
    print(f"  Fleet Utilization: {result.fleet_utilization_pct:.1f}%")
    print(f"  Optimality Score: {result.optimality_score:.1f}/100")
    print(f"  Conflicts Detected: {result.conflicts_detected}")


def example_2_compare_strategies():
    """Example 2: Compare different optimization strategies"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Compare Optimization Strategies")
    print("="*80)
    
    # Load data
    loader = DeepSeaLoader()
    data = loader.load()
    calculator = DeepSeaCalculator(data)
    data = calculator.calculate_all()
    
    # Create optimizer
    optimizer = YearScheduleOptimizer(data)
    
    # Compare strategies
    strategies = ['maxrevenue', 'mincost', 'balance']
    results = {}
    
    for strategy in strategies:
        print(f"\n>> Optimizing with {strategy} strategy...")
        result = optimizer.optimize(strategy)
        results[strategy] = result
    
    # Display comparison
    print(f"\n{'='*80}")
    print("STRATEGY COMPARISON")
    print(f"{'='*80}")
    print(f"{'Strategy':<15} {'Revenue':>12} {'Cost':>12} {'Profit':>12} {'Utiliz%':>8} {'Score':>6}")
    print(f"{'-'*80}")
    
    for strategy, result in results.items():
        print(f"{strategy:<15} "
              f"${result.total_revenue_usd:>11,.0f} "
              f"${result.total_cost_usd:>11,.0f} "
              f"${result.total_profit_usd:>11,.0f} "
              f"{result.fleet_utilization_pct:>7.1f}% "
              f"{result.optimality_score:>5.1f}")
    
    # Find best
    best = max(results.items(), key=lambda x: x[1].optimality_score)
    print(f"\n Best Strategy: {best[0].upper()} (Score: {best[1].optimality_score:.1f})")


def example_3_conflict_detection():
    """Example 3: Detect and analyze conflicts"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Conflict Detection")
    print("="*80)
    
    # Load and optimize
    loader = DeepSeaLoader()
    data = loader.load()
    calculator = DeepSeaCalculator(data)
    data = calculator.calculate_all()
    
    optimizer = YearScheduleOptimizer(data)
    
    # Detect conflicts
    print("\n>> Detecting scheduling conflicts...")
    conflicts = optimizer.detect_conflicts()
    
    print(f"\n Conflict Analysis:")
    print(f"  Total Conflicts: {len(conflicts)}")
    
    # Categorize
    errors = [c for c in conflicts if c.get('severity') == 'error']
    warnings = [c for c in conflicts if c.get('severity') == 'warning']
    
    print(f"  - Errors (Critical): {len(errors)}")
    print(f"  - Warnings (Minor): {len(warnings)}")
    
    # Show critical conflicts
    if errors:
        print(f"\n  Critical Conflicts:")
        for i, conflict in enumerate(errors[:5], 1):
            print(f"    {i}. {conflict.get('description', 'Unknown conflict')}")
    
    # Show warnings
    if warnings:
        print(f"\n  Warnings:")
        for i, conflict in enumerate(warnings[:3], 1):
            print(f"    {i}. {conflict.get('description', 'Unknown warning')}")


def example_4_save_load_scenarios():
    """Example 4: Save and load schedule scenarios"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Save/Load Schedule Scenarios")
    print("="*80)
    
    # Load and optimize
    loader = DeepSeaLoader()
    data = loader.load()
    calculator = DeepSeaCalculator(data)
    data = calculator.calculate_all()
    
    # Create and run optimization
    optimizer = YearScheduleOptimizer(data)
    result = optimizer.optimize("balance")
    
    # Save schedule
    schedule_mgr = YearScheduleManager()
    schedule_id = f"annual_2026_{int(datetime.now().timestamp())}"
    
    print(f"\n>> Saving schedule as: {schedule_id}")
    success = schedule_mgr.save_schedule(
        schedule_id=schedule_id,
        optimization_result=result,
        data=data,
        metadata={
            'created_by': 'example_script',
            'purpose': 'demonstration',
            'timestamp': datetime.now().isoformat()
        }
    )
    
    if success:
        print(f" Schedule saved successfully")
    
    # List all schedules
    print(f"\n>> Listing all saved schedules:")
    schedules = schedule_mgr.list_schedules()
    print(f"  Found {len(schedules)} schedules")
    
    for s in schedules[:5]:
        print(f"  - {s['schedule_id']}: {s['strategy']} (Score: {s['optimality_score']:.1f})")
    
    # Load schedule
    print(f"\n>> Loading schedule: {schedule_id}")
    loaded = schedule_mgr.load_schedule(schedule_id)
    
    if loaded:
        print(f" Schedule loaded successfully")
        print(f"  Strategy: {loaded.get('strategy')}")
        print(f"  Created: {loaded.get('created_at')}")
        kpis = loaded.get('kpis', {})
        print(f"  Profit: ${kpis.get('total_profit_usd', 0):,.0f}")


def example_5_custom_config():
    """Example 5: Custom optimization configuration"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Custom Optimization Configuration")
    print("="*80)
    
    # Load data
    loader = DeepSeaLoader()
    data = loader.load()
    calculator = DeepSeaCalculator(data)
    data = calculator.calculate_all()
    
    # Custom configuration
    config = YearScheduleConfig(
        start_date="2026-01-01",
        end_date="2026-12-31",
        optimization_strategy="balance",
        min_utilization_pct=75.0,  # Higher minimum
        max_utilization_pct=92.0,  # Tighter band
        min_tce_usd=15000.0,  # Minimum TCE threshold
        bunker_optimization=True,
        conflict_resolution="auto"
    )
    
    print(f"\n>> Running optimization with custom config:")
    print(f"  Utilization Target: {config.min_utilization_pct:.0f}% - {config.max_utilization_pct:.0f}%")
    print(f"  Minimum TCE: ${config.min_tce_usd:,.0f}")
    print(f"  Bunker Optimization: {config.bunker_optimization}")
    
    # Create optimizer with config
    optimizer = YearScheduleOptimizer(data, config)
    result = optimizer.optimize("balance")
    
    # Check if meets targets
    print(f"\n Results:")
    print(f"  Fleet Utilization: {result.fleet_utilization_pct:.1f}%", end="")
    if config.min_utilization_pct <= result.fleet_utilization_pct <= config.max_utilization_pct:
        print("  Within target")
    else:
        print("  Outside target")
    
    print(f"  Average TCE: ${result.avg_tce_usd:,.0f}", end="")
    if result.avg_tce_usd >= config.min_tce_usd:
        print("  Above minimum")
    else:
        print("  Below minimum")


def example_6_real_time_monitoring():
    """Example 6: Real-time schedule monitoring"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Real-Time Schedule Monitoring")
    print("="*80)
    
    # Load data
    loader = DeepSeaLoader()
    data = loader.load()
    calculator = DeepSeaCalculator(data)
    data = calculator.calculate_all()
    
    # Create optimizer
    optimizer = YearScheduleOptimizer(data)
    
    # Optimize
    print("\n>> Generating initial schedule...")
    result = optimizer.optimize("balance")
    
    # Monitor KPIs
    print(f"\n>> Real-Time KPI Dashboard:")
    print(f"{'='*80}")
    print(f"  FINANCIAL PERFORMANCE")
    print(f"  Revenue:  ${result.total_revenue_usd:>15,.0f}")
    print(f"  Cost:     ${result.total_cost_usd:>15,.0f}")
    print(f"  Profit:   ${result.total_profit_usd:>15,.0f}")
    margin = (result.total_profit_usd / result.total_revenue_usd * 100) if result.total_revenue_usd > 0 else 0
    print(f"  Margin:    {margin:>14.1f}%")
    
    print(f"\n  OPERATIONAL METRICS")
    print(f"  Voyages:     {result.total_voyages:>12}")
    print(f"  Cargo (MT):  {result.total_cargo_mt:>12,}")
    print(f"  Avg TCE:    ${result.avg_tce_usd:>12,.0f}")
    print(f"  Utilization: {result.fleet_utilization_pct:>11.1f}%")
    
    print(f"\n  QUALITY INDICATORS")
    print(f"  Conflicts:   {result.conflicts_detected:>12}")
    print(f"  Optimality:  {result.optimality_score:>11.1f}/100")
    print(f"{'='*80}")
    
    # Alert on issues
    if result.conflicts_detected > 0:
        print(f"\n  ALERT: {result.conflicts_detected} conflicts detected")
    
    if result.optimality_score < 70:
        print(f"\n  ALERT: Low optimality score ({result.optimality_score:.1f})")
    
    if margin < 15:
        print(f"\n  ALERT: Low profit margin ({margin:.1f}%)")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("YEAR SCHEDULE OPTIMIZATION - INTEGRATION EXAMPLES")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        example_1_basic_optimization()
        example_2_compare_strategies()
        example_3_conflict_detection()
        example_4_save_load_scenarios()
        example_5_custom_config()
        example_6_real_time_monitoring()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
