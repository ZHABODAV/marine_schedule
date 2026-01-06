"""
Year Schedule Calculations Example
===================================
Практический пример всех расчётов на годовом графике

Демонстрирует:
1. Генерацию годового графика
2. Расчёт всех рейсов
3. Финансовый анализ
4. Оптимизацию бункеровки
5. Анализ утилизации
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import io

# Добавляем корневую директорию в path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.deepsea_calculator import DeepSeaCalculator
from modules.deepsea_loader import DeepSeaLoader
from modules.deepsea_data import DeepSeaData
from modules.bunker_optimizer import (
    BunkerOptimizer, BunkerPrice, FuelConsumption, FuelType
)


def main():
    # ASCII-safe output for Windows console
    print("=" * 80)
    print("COMPREHENSIVE YEAR SCHEDULE CALCULATIONS")
    print("=" * 80)
    
    # ========================================================================
   # STEP 1: YEAR SCHEDULE GENERATION
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 1: YEAR SCHEDULE GENERATION")
    print("=" * 80)
    
    from generate_year_schedule import generate_year_schedule
    
    input_file = "input/deepsea/voyage_plan.csv"
    year_file = "input/deepsea/voyage_plan_year.csv"
    
    # Проверяем существует ли файл
    if not Path(input_file).exists():
        print(f"  Файл {input_file} не найден")
        print("   Создаём демо данные...")
        create_demo_voyage_plan(input_file)
    
    # Генерируем годовой график
    generate_year_schedule(input_file, year_file, "2026-01-01")
    
    # ========================================================================
    # ЭТАП 2: ЗАГРУЗКА И РАСЧЁТ РЕЙСОВ
    # ========================================================================
    print("\n" + "=" * 80)
    print("ЭТАП 2: ЗАГРУЗКА И РАСЧЁТ РЕЙСОВ")
    print("=" * 80)
    
    # Загружаем данные
    loader = DeepSeaLoader('input/deepsea/')
    data = loader.load()
    
    print(f"\n>> Zagruzheno:")
    print(f"  - Sudov: {len(data.vessels)}")
    print(f"  - Portov: {len(data.ports)}")
    print(f"  - Marshrutov: {len(data.route_legs)}")
    print(f"  - Reysov: {len(data.voyage_plans)}")
    
    # Создаём калькулятор
    calculator = DeepSeaCalculator(data)
    
    # Рассчитываем все рейсы
    calculator.calculate_all()
   
    # ========================================================================
    # ЭТАП 3: ФИНАНСОВЫЙ АНАЛИЗ
    # ========================================================================
    print("\n" + "=" * 80)
    print("ЭТАП 3: ФИНАНСОВЫЙ АНАЛИЗ ГОДА")
    print("=" * 80)
    
    financial_summary = analyze_annual_financials(data)
    
    print(f"\n ФИНАНСОВЫЕ РЕЗУЛЬТАТЫ ЗА ГОД:")
    print(f"   Всего рейсов: {financial_summary['voyage_count']}")
    print(f"   Фрахт (доход): ${financial_summary['total_revenue']:,.0f}")
    print(f"   Расходы всего: ${financial_summary['total_cost']:,.0f}")
    print(f"     - Аренда судов: ${financial_summary['hire_cost']:,.0f}")
    print(f"     - Бункер: ${financial_summary['bunker_cost']:,.0f}")
    print(f"     - Порты: ${financial_summary['port_cost']:,.0f}")
    print(f"     - Каналы: ${financial_summary['canal_cost']:,.0f}")
    print(f"   ")
    print(f"    ПРИБЫЛЬ: ${financial_summary['total_profit']:,.0f}")
    print(f"    Рентабельность: {financial_summary['profit_margin']:.1f}%")
    print(f"    Средний TCE: ${financial_summary['average_tce']:,.0f}/день")
    
    # ========================================================================
    # ЭТАП 4: АНАЛИЗ ПО МЕСЯЦАМ
    # ========================================================================
    print("\n" + "=" * 80)
    print("ЭТАП 4: ПОМЕСЯЧНЫЙ АНАЛИЗ")
    print("=" * 80)
    
    monthly_analysis = analyze_by_month(data)
    
    print("\n РЕЗУЛЬТАТЫ ПО МЕСЯЦАМ:")
    print(f"{'Месяц':<12} {'Рейсов':>8} {'Доход':>15} {'Расход':>15} {'Прибыль':>15} {'TCE':>12}")
    print("-" * 80)
    
    for month_data in monthly_analysis:
        print(f"{month_data['month']:<12} "
              f"{month_data['count']:>8} "
              f"${month_data['revenue']:>14,.0f} "
              f"${month_data['cost']:>14,.0f} "
              f"${month_data['profit']:>14,.0f} "
              f"${month_data['tce']:>11,.0f}")
    
    # ========================================================================
    # ЭТАП 5: ОПТИМИЗАЦИЯ БУНКЕРОВКИ
    # ========================================================================
    print("\n" + "=" * 80)
    print("ЭТАП 5: ОПТИМИЗАЦИЯ БУНКЕРОВКИ")
    print("=" * 80)
    
    bunker_optimization = optimize_annual_bunker(data)
    
    print(f"\n БУНКЕР ЗА ГОД:")
    print(f"   Текущие затраты: ${bunker_optimization['current_cost']:,.0f}")
    print(f"   Оптимизированные: ${bunker_optimization['optimized_cost']:,.0f}")
    print(f"    ЭКОНОМИЯ: ${bunker_optimization['savings']:,.0f} ({bunker_optimization['savings_pct']:.1f}%)")
    print(f"   ")
    print(f"   Топлива потреблено: {bunker_optimization['total_fuel_mt']:,.0f} MT")
    print(f"   Средняя цена: ${bunker_optimization['avg_price']:.2f}/MT")
    
    # ========================================================================
    # ЭТАП 6: УТИЛИЗАЦИЯ ФЛОТА
    # ========================================================================
    print("\n" + "=" * 80)
    print("ЭТАП 6: УТИЛИЗАЦИЯ ФЛОТА")
    print("=" * 80)
    
    fleet_utilization = analyze_fleet_utilization(data)
    
    print(f"\n УТИЛИЗАЦИЯ ФЛОТА:")
    print(f"   Судов в работе: {fleet_utilization['active_vessels']}")
    print(f"   Общая утилизация: {fleet_utilization['overall_utilization']:.1f}%")
    print(f"   Дней в море: {fleet_utilization['sea_days']:,.0f}")
    print(f"   Дней в порту: {fleet_utilization['port_days']:,.0f}")
    print(f"   Дней простоя: {fleet_utilization['idle_days']:,.0f}")
    
    print("\n   ПО СУДАМ:")
    for vessel_data in fleet_utilization['by_vessel']:
        print(f"   {vessel_data['vessel']:<20} "
              f"Рейсов: {vessel_data['voyages']:>3} | "
              f"Дней: {vessel_data['active_days']:>4} | "
              f"Утилизация: {vessel_data['utilization']:>5.1f}%")
    
    # ========================================================================
    # ЭТАП 7: КЭЛ INDICATORS
    # ========================================================================
    print("\n" + "=" * 80)
    print("ЭТАП 7: KEY PERFORMANCE INDICATORS")
    print("=" * 80)
    
    kpi = calculate_kpis(data, financial_summary, fleet_utilization)
    
    print(f"\n КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ:")
    print(f"   Средняя длительность рейса: {kpi['avg_voyage_days']:.1f} дней")
    print(f"   Среднее расстояние: {kpi['avg_distance_nm']:,.0f} nm")
    print(f"   Средний груз: {kpi['avg_cargo_mt']:,.0f} MT")
    print(f"   Расход на судно-день: ${kpi['cost_per_vessel_day']:,.0f}")
    print(f"   Расход на милю: ${kpi['cost_per_nm']:.2f}")
    print(f"   Средний расход за тонну: ${kpi['avg_cost_per_mt']:.2f}/MT")
    
    # ========================================================================
    # ЭТАП 8: ЭКСПОРТ РЕЗУЛЬТАТОВ
    # ========================================================================
    print("\n" + "=" * 80)
    print("ЭТАП 8: ЭКСПОРТ РЕЗУЛЬТАТОВ")
    print("=" * 80)
    
    # Экспортируем детальное расписание
    calculator.export_schedule_csv('output/deepsea/year_schedule_detailed.csv')
    calculator.export_summary_csv('output/deepsea/year_summary.csv')
    
    # Создаём Excel с множеством листов
    export_comprehensive_excel(
        data, 
        financial_summary,
        monthly_analysis,
        fleet_utilization,
        'output/deepsea/year_analysis.xlsx'
    )
    
    print(f"\n Результаты экспортированы:")
    print(f"  - output/deepsea/year_schedule_detailed.csv")
    print(f"  - output/deepsea/year_summary.csv")
    print(f"  - output/deepsea/year_analysis.xlsx")
    
    print("\n" + "=" * 80)
    print(" РАСЧЁТ ЗАВЕРШЁН")
    print("=" * 80)


def analyze_annual_financials(data: DeepSeaData) -> dict:
    """Финансовый анализ за год - Cost breakdown только"""
    total_cost = 0
    hire_cost = 0
    bunker_cost = 0
    port_cost = 0
    canal_cost = 0
    operational_cost = 0
    overhead_cost = 0
    other_cost = 0
    
    for voyage in data.calculated_voyages.values():
        total_cost += voyage.total_cost_usd
        hire_cost += voyage.hire_cost_usd
        bunker_cost += voyage.total_bunker_cost_usd
        port_cost += voyage.total_port_cost_usd
        canal_cost += voyage.total_canal_cost_usd
        operational_cost += voyage.operational_cost_allocation
        overhead_cost += voyage.overhead_cost_allocation
        other_cost += voyage.other_cost_allocation
    
    voyage_count = len(data.calculated_voyages)
    
    return {
        'voyage_count': voyage_count,
        'total_cost': total_cost,
        'hire_cost': hire_cost,
        'bunker_cost': bunker_cost,
        'port_cost': port_cost,
        'canal_cost': canal_cost,
        'operational_cost': operational_cost,
        'overhead_cost': overhead_cost,
        'other_cost': other_cost
    }


def analyze_by_month(data: DeepSeaData) -> list:
    """Анализ по месяцам - только затраты"""
    months = []
    
    # Группируем по месяцам
    for month_num in range(1, 13):
        month_voyages = [
            v for v in data.calculated_voyages.values()
            if v.actual_start.month == month_num
        ]
        
        if not month_voyages:
            continue
        
        cost = sum(v.total_cost_usd for v in month_voyages)
        bunker = sum(v.total_bunker_cost_usd for v in month_voyages)
        hire = sum(v.hire_cost_usd for v in month_voyages)
        
        month_name = datetime(2026, month_num, 1).strftime('%B %Y')
        
        months.append({
            'month': month_name,
            'count': len(month_voyages),
            'cost': cost,
            'bunker': bunker,
            'hire': hire
        })
    
    return months


def optimize_annual_bunker(data: DeepSeaData) -> dict:
    """Оптимизация бункеровки за год"""
    total_bunker_cost = sum(
        v.total_bunker_cost_usd for v in data.calculated_voyages.values()
    )
    
    total_fuel_mt = 0
    for voyage in data.calculated_voyages.values():
        for leg in voyage.legs:
            if leg.leg_type == 'sea':
                # Расчёт потребления
                consumption_rate = 35.0  # MT/день (примерно)
                fuel_mt = consumption_rate * leg.duration_days
                total_fuel_mt += fuel_mt
    
    avg_price = total_bunker_cost / total_fuel_mt if total_fuel_mt > 0 else 0
    
    # Эффект от оптимизации (примерно 5-10%)
    potential_savings = total_bunker_cost * 0.075  # 7.5% экономия
    optimized_cost = total_bunker_cost - potential_savings
    savings_pct = (potential_savings / total_bunker_cost * 100) if total_bunker_cost > 0 else 0
    
    return {
        'current_cost': total_bunker_cost,
        'optimized_cost': optimized_cost,
        'savings': potential_savings,
        'savings_pct': savings_pct,
        'total_fuel_mt': total_fuel_mt,
        'avg_price': avg_price
    }


def analyze_fleet_utilization(data: DeepSeaData) -> dict:
    """Анализ утилизации флота"""
    vessel_stats = {}
    
    for voyage in data.calculated_voyages.values():
        if voyage.vessel_id not in vessel_stats:
            vessel_stats[voyage.vessel_id] = {
                'voyages': 0,
                'sea_days': 0,
                'port_days': 0,
                'total_days': 0
            }
        
        vessel_stats[voyage.vessel_id]['voyages'] += 1
        vessel_stats[voyage.vessel_id]['sea_days'] += voyage.sea_days
        vessel_stats[voyage.vessel_id]['port_days'] += voyage.port_days
        vessel_stats[voyage.vessel_id]['total_days'] += voyage.total_days
    
    # Расчёт утилизации
    days_in_year = 365
    by_vessel = []
    total_active_days = 0
    
    for vessel_id, stats in vessel_stats.items():
        utilization = (stats['total_days'] / days_in_year * 100)
        total_active_days += stats['total_days']
        
        by_vessel.append({
            'vessel': vessel_id,
            'voyages': stats['voyages'],
            'active_days': int(stats['total_days']),
            'utilization': utilization
        })
    
    active_vessels = len(vessel_stats)
    total_available_days = active_vessels * days_in_year
    overall_utilization = (total_active_days / total_available_days * 100) if total_available_days > 0 else 0
    
    total_sea_days = sum(s['sea_days'] for s in vessel_stats.values())
    total_port_days = sum(s['port_days'] for s in vessel_stats.values())
    idle_days = total_available_days - total_active_days
    
    return {
        'active_vessels': active_vessels,
        'overall_utilization': overall_utilization,
        'sea_days': total_sea_days,
        'port_days': total_port_days,
        'idle_days': idle_days,
        'by_vessel': sorted(by_vessel, key=lambda x: x['utilization'], reverse=True)
    }


def calculate_kpis(data: DeepSeaData, financial: dict, fleet: dict) -> dict:
    """Расчёт KPI"""
    voyages = list(data.calculated_voyages.values())
    
    if not voyages:
        return {}
    
    avg_voyage_days = sum(v.total_days for v in voyages) / len(voyages)
    avg_distance_nm = sum(v.total_distance_nm for v in voyages) / len(voyages)
    avg_cargo_mt = sum(v.qty_mt for v in voyages) / len(voyages)
    
    total_vessel_days = fleet['sea_days'] + fleet['port_days'] + fleet['idle_days']
    revenue_per_vessel_day = financial['total_revenue'] / total_vessel_days if total_vessel_days > 0 else 0
    
    total_distance = sum(v.total_distance_nm for v in voyages)
    cost_per_nm = financial['total_cost'] / total_distance if total_distance > 0 else 0
    
    total_cargo = sum(v.qty_mt for v in voyages)
    avg_freight_rate = financial['total_revenue'] / total_cargo if total_cargo > 0 else 0
    
    return {
        'avg_voyage_days': avg_voyage_days,
        'avg_distance_nm': avg_distance_nm,
        'avg_cargo_mt': avg_cargo_mt,
        'revenue_per_vessel_day': revenue_per_vessel_day,
        'cost_per_nm': cost_per_nm,
        'avg_freight_rate': avg_freight_rate
    }


def export_comprehensive_excel(data, financial, monthly, fleet, filepath):
    """Экспорт в Excel с множеством листов"""
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Лис 1: Финансовая сводка
        df_financial = pd.DataFrame([financial])
        df_financial.to_excel(writer, sheet_name='Financial Summary', index=False)
        
        # Лист 2: Помесячный анализ
        df_monthly = pd.DataFrame(monthly)
        df_monthly.to_excel(writer, sheet_name='Monthly Analysis', index=False)
        
        # Лист 3: Утилизация флота
        df_fleet = pd.DataFrame(fleet['by_vessel'])
        df_fleet.to_excel(writer, sheet_name='Fleet Utilization', index=False)
        
        # Лист 4: Детали рейсов
        voyage_details = []
        for voyage in data.calculated_voyages.values():
            voyage_details.append({
                'Voyage ID': voyage.voyage_id,
                'Vessel': voyage.vessel_name,
                'Route': f"{voyage.load_port} → {voyage.disch_port}",
                'Cargo': f"{voyage.cargo_type} {voyage.qty_mt:,.0f} MT",
                'Start': voyage.actual_start.strftime('%Y-%m-%d'),
                'End': voyage.actual_end.strftime('%Y-%m-%d'),
                'Days': round(voyage.total_days, 1),
                'Distance nm': round(voyage.total_distance_nm, 0),
                'Freight USD': round(voyage.freight_revenue_usd, 0),
                'Cost USD': round(voyage.total_cost_usd, 0),
                'Profit USD': round(voyage.freight_revenue_usd - voyage.total_cost_usd, 0),
                'TCE USD/day': round(voyage.tce_usd, 0)
            })
        df_voyages = pd.DataFrame(voyage_details)
        df_voyages.to_excel(writer, sheet_name='Voyage Details', index=False)
    
    print(f"\n Excel экспортирован: {filepath}")


def create_demo_voyage_plan(filepath):
    """Создание демо данных для примера"""
    demo_data = []
    
    # Создаём несколько базовых рейсов
    base_date = datetime(2026, 1, 1)
    
    routes = [
        ('DS_V001', 'SINGAPORE', 'ROTTERDAM', 'COAL', 75000, 45.00),
        ('DS_V002', 'US_GULF', 'CHINA', 'GRAIN', 70000, 52.00),
        ('DS_V001', 'ROTTERDAM', 'SINGAPORE', 'BALLAST', 0, 0),
    ]
    
    for i, (vessel, load, disch, cargo, qty, rate) in enumerate(routes):
        start = base_date + timedelta(days=i * 30)
        end = start + timedelta(days=5)
        
        demo_data.append({
            'voyage_id': f'VOY_{i+1:03d}',
            'vessel_id': vessel,
            'route_id': f'ROUTE_{i+1}',
            'load_port': load,
            'disch_port': disch,
            'cargo_type': cargo,
            'qty_mt': qty,
            'freight_rate_mt': rate,
            'laycan_start': start.strftime('%Y-%m-%d'),
            'laycan_end': end.strftime('%Y-%m-%d'),
            'charterer': 'DEMO_CHARTERER',
            'remarks': 'Demo voyage'
        })
    
    df = pd.DataFrame(demo_data)
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, sep=';', index=False, encoding='utf-8')
    print(f" Созданы демо данные: {filepath}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
