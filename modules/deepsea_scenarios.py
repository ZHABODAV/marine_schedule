"""
Управление сценариями Deep Sea
==============================

Сценарий = набор рейсов для расчёта и сравнения
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging
import copy

from .deepsea_data import (
    DeepSeaData, VoyagePlan, CalculatedVoyage
)
from .deepsea_calculator import DeepSeaCalculator

logger = logging.getLogger(__name__)


@dataclass
class Scenario:
    """Сценарий - набор рейсов"""
    scenario_id: str
    scenario_name: str
    description: str
    voyage_ids: List[str]
    
    # Результаты расчёта
    calculated_voyages: Dict[str, CalculatedVoyage] = field(default_factory=dict)
    
    # Статистика
    total_cargo_mt: float = 0
    total_revenue_usd: float = 0
    total_cost_usd: float = 0
    avg_tce_usd: float = 0
    total_days: float = 0
    fleet_utilization_pct: float = 0


@dataclass
class ScenarioComparison:
    """Сравнение сценариев"""
    scenarios: List[Scenario]
    
    def get_comparison_table(self) -> pd.DataFrame:
        """Таблица сравнения"""
        rows = []
        for s in self.scenarios:
            rows.append({
                'Сценарий': s.scenario_name,
                'Описание': s.description,
                'Рейсов': len(s.calculated_voyages),
                'Груз (MT)': s.total_cargo_mt,
                'Выручка ($)': s.total_revenue_usd,
                'Затраты ($)': s.total_cost_usd,
                'TCE ($/день)': s.avg_tce_usd,
                'Дней': s.total_days,
                'Утилизация (%)': s.fleet_utilization_pct
            })
        return pd.DataFrame(rows)


class ScenarioManager:
    """Менеджер сценариев"""
    
    def __init__(self, data: DeepSeaData, input_dir: str = "input/deepsea"):
        self.base_data = data
        self.input_dir = Path(input_dir)
        self.scenarios: Dict[str, Scenario] = {}
    
    def load_scenarios(self) -> Dict[str, Scenario]:
        """Загрузка сценариев из CSV"""
        logger.info("\n Загрузка сценариев...")
        
        filepath = self.input_dir / "scenarios.csv"
        if not filepath.exists():
            logger.warning(f"  Файл сценариев не найден: {filepath}")
            return {}
        
        try:
            df = pd.read_csv(filepath, delimiter=';', comment='#', encoding='utf-8')
            
            for _, row in df.iterrows():
                voyage_ids_str = str(row['voyage_ids']).strip()
                voyage_ids = [v.strip() for v in voyage_ids_str.split(',') if v.strip()]
                
                scenario = Scenario(
                    scenario_id=str(row['scenario_id']).strip(),
                    scenario_name=str(row['scenario_name']).strip(),
                    description=str(row.get('description', '')).strip(),
                    voyage_ids=voyage_ids
                )
                
                self.scenarios[scenario.scenario_id] = scenario
                logger.info(f"   {scenario.scenario_id}: {scenario.scenario_name} ({len(voyage_ids)} рейсов)")
            
        except Exception as e:
            logger.error(f"  Ошибка загрузки сценариев: {e}")
        
        return self.scenarios
    
    def create_scenario(
        self,
        scenario_id: str,
        scenario_name: str,
        voyage_ids: List[str],
        description: str = ""
    ) -> Scenario:
        """Создание сценария программно"""
        scenario = Scenario(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            description=description,
            voyage_ids=voyage_ids
        )
        self.scenarios[scenario_id] = scenario
        return scenario
    
    def calculate_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Расчёт одного сценария"""
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            logger.error(f"Сценарий {scenario_id} не найден")
            return None
        
        logger.info(f"\nРасчёт сценария: {scenario.scenario_name}")
        logger.info(f"   Рейсы: {', '.join(scenario.voyage_ids)}")
        
        # Создаём копию данных для сценария
        scenario_data = self._create_scenario_data(scenario)
        
        if not scenario_data.voyage_plans:
            logger.warning(f"   Нет рейсов для расчёта")
            return scenario
        
        # Рассчитываем
        calculator = DeepSeaCalculator(scenario_data)
        scenario_data = calculator.calculate_all()
        
        # Сохраняем результаты в сценарий
        scenario.calculated_voyages = scenario_data.calculated_voyages
        
        # Считаем статистику
        self._calculate_scenario_stats(scenario)
        
        return scenario
    
    def calculate_all_scenarios(self) -> Dict[str, Scenario]:
        """Расчёт всех сценариев"""
        logger.info("\n" + "=" * 70)
        logger.info("РАСЧЁТ ВСЕХ СЦЕНАРИЕВ")
        logger.info("=" * 70)
        
        for scenario_id in self.scenarios:
            self.calculate_scenario(scenario_id)
        
        return self.scenarios
    
    def compare_scenarios(self, scenario_ids: Optional[List[str]] = None) -> ScenarioComparison:
        """Сравнение сценариев"""
        if scenario_ids is None:
            scenario_ids = list(self.scenarios.keys())
        
        scenarios_to_compare = [
            self.scenarios[sid] for sid in scenario_ids 
            if sid in self.scenarios
        ]
        
        return ScenarioComparison(scenarios=scenarios_to_compare)
    
    def _create_scenario_data(self, scenario: Scenario) -> DeepSeaData:
        """Создание данных для сценария (только нужные рейсы)"""
        # Глубокое копирование базовых данных
        scenario_data = DeepSeaData(
            params=self.base_data.params,
            ports=self.base_data.ports,
            distances=self.base_data.distances,
            canals=self.base_data.canals,
            vessels=self.base_data.vessels,
            route_legs=self.base_data.route_legs,
            voyage_plans=[]  # Будем заполнять
        )
        
        # Фильтруем только рейсы из сценария
        voyage_ids_set = set(scenario.voyage_ids)
        
        for plan in self.base_data.voyage_plans:
            if plan.voyage_id in voyage_ids_set:
                scenario_data.voyage_plans.append(plan)
        
        logger.info(f"   Найдено рейсов: {len(scenario_data.voyage_plans)} из {len(scenario.voyage_ids)}")
        
        # Предупреждаем о ненайденных
        found_ids = {p.voyage_id for p in scenario_data.voyage_plans}
        missing = voyage_ids_set - found_ids
        if missing:
            logger.warning(f"Не найдены рейсы: {', '.join(missing)}")
        
        return scenario_data
    
    def _calculate_scenario_stats(self, scenario: Scenario):
        """Расчёт статистики сценария"""
        if not scenario.calculated_voyages:
            return
        
        voyages = list(scenario.calculated_voyages.values())
        
        scenario.total_cargo_mt = sum(v.qty_mt for v in voyages)
        scenario.total_revenue_usd = sum(v.freight_revenue_usd for v in voyages)
        scenario.total_cost_usd = sum(v.total_cost_usd for v in voyages)
        scenario.total_days = sum(v.total_days for v in voyages)
        
        if voyages:
            scenario.avg_tce_usd = sum(v.tce_usd for v in voyages) / len(voyages)
        
        # Утилизация флота
        # Считаем дни работы каждого судна
        vessel_days = {}
        for voyage in voyages:
            vid = voyage.vessel_id
            if vid not in vessel_days:
                vessel_days[vid] = set()
            
            # Добавляем все дни рейса
            current = voyage.actual_start.date()
            while current <= voyage.actual_end.date():
                vessel_days[vid].add(current)
                current += timedelta(days=1)
        
        # Общий период
        if voyages:
            min_date = min(v.actual_start for v in voyages).date()
            max_date = max(v.actual_end for v in voyages).date()
            total_period_days = (max_date - min_date).days + 1
            
            # Средняя утилизация
            if vessel_days and total_period_days > 0:
                total_busy = sum(len(days) for days in vessel_days.values())
                total_available = len(vessel_days) * total_period_days
                scenario.fleet_utilization_pct = (total_busy / total_available) * 100
    
    def export_comparison(self, filepath: str, scenario_ids: Optional[List[str]] = None):
        """Экспорт сравнения в Excel"""
        comparison = self.compare_scenarios(scenario_ids)
        df = comparison.get_comparison_table()
        
        # Форматируем числа
        df['Груз (MT)'] = df['Груз (MT)'].apply(lambda x: f"{x:,.0f}")
        df['Выручка ($)'] = df['Выручка ($)'].apply(lambda x: f"${x:,.0f}")
        df['Затраты ($)'] = df['Затраты ($)'].apply(lambda x: f"${x:,.0f}")
        df['TCE ($/день)'] = df['TCE ($/день)'].apply(lambda x: f"${x:,.0f}")
        df['Дней'] = df['Дней'].apply(lambda x: f"{x:.1f}")
        df['Утилизация (%)'] = df['Утилизация (%)'].apply(lambda x: f"{x:.1f}%")
        
        df.to_excel(filepath, index=False, sheet_name='Сравнение')
        logger.info(f"   Сравнение сценариев: {filepath}")


# === ИНТЕРАКТИВНЫЙ БИЛДЕР СЦЕНАРИЕВ ===

class ScenarioBuilder:
    """
    Интерактивный построитель сценариев
    Позволяет добавлять/удалять рейсы и сразу видеть результат
    """
    
    def __init__(self, data: DeepSeaData):
        self.data = data
        self.current_voyages: List[str] = []
        self.calculated_data: Optional[DeepSeaData] = None
    
    def add_voyage(self, voyage_id: str) -> bool:
        """Добавить рейс"""
        # Проверяем что рейс существует
        exists = any(p.voyage_id == voyage_id for p in self.data.voyage_plans)
        if not exists:
            logger.warning(f"Рейс {voyage_id} не найден в планах")
            return False
        
        if voyage_id in self.current_voyages:
            logger.info(f"Рейс {voyage_id} уже добавлен")
            return False
        
        # Проверяем конфликты (одно судно в одно время)
        conflict = self._check_conflicts(voyage_id)
        if conflict:
            logger.warning(f"Конфликт: {conflict}")
            return False
        
        self.current_voyages.append(voyage_id)
        logger.info(f" Добавлен рейс: {voyage_id}")
        return True
    
    def remove_voyage(self, voyage_id: str) -> bool:
        """Удалить рейс"""
        if voyage_id not in self.current_voyages:
            logger.warning(f"Рейс {voyage_id} не в списке")
            return False
        
        self.current_voyages.remove(voyage_id)
        logger.info(f" Удалён рейс: {voyage_id}")
        return True
    
    def clear(self):
        """Очистить сценарий"""
        self.current_voyages = []
        self.calculated_data = None
        logger.info(" Сценарий очищен")
    
    def calculate(self) -> Optional[DeepSeaData]:
        """Рассчитать текущий сценарий"""
        if not self.current_voyages:
            logger.warning("Нет рейсов для расчёта")
            return None
        
        # Создаём данные с выбранными рейсами
        scenario_data = DeepSeaData(
            params=self.data.params,
            ports=self.data.ports,
            distances=self.data.distances,
            canals=self.data.canals,
            vessels=self.data.vessels,
            route_legs=self.data.route_legs,
            voyage_plans=[]
        )
        
        voyage_ids_set = set(self.current_voyages)
        for plan in self.data.voyage_plans:
            if plan.voyage_id in voyage_ids_set:
                scenario_data.voyage_plans.append(plan)
        
        # Рассчитываем
        calculator = DeepSeaCalculator(scenario_data)
        self.calculated_data = calculator.calculate_all()
        
        return self.calculated_data
    
    def get_summary(self) -> Dict:
        """Получить сводку"""
        if not self.calculated_data or not self.calculated_data.calculated_voyages:
            return {}
        
        voyages = list(self.calculated_data.calculated_voyages.values())
        
        return {
            'voyages': len(voyages),
            'cargo_mt': sum(v.qty_mt for v in voyages),
            'revenue_usd': sum(v.freight_revenue_usd for v in voyages),
            'cost_usd': sum(v.total_cost_usd for v in voyages),
            'avg_tce_usd': sum(v.tce_usd for v in voyages) / len(voyages) if voyages else 0,
            'total_days': sum(v.total_days for v in voyages),
        }
    
    def print_summary(self):
        """Печать сводки"""
        summary = self.get_summary()
        if not summary:
            print("Сначала выполните calculate()")
            return
        
        print("\n" + "=" * 50)
        print("СВОДКА СЦЕНАРИЯ")
        print("=" * 50)
        print(f"Рейсов:    {summary['voyages']}")
        print(f"Груз:      {summary['cargo_mt']:,.0f} MT")
        print(f"Выручка:   ${summary['revenue_usd']:,.0f}")
        print(f"Затраты:   ${summary['cost_usd']:,.0f}")
        print(f"TCE:       ${summary['avg_tce_usd']:,.0f}/день")
        print(f"Дней:      {summary['total_days']:.1f}")
        print("=" * 50)
    
    def get_available_voyages(self) -> List[Dict]:
        """Список доступных рейсов"""
        available = []
        for plan in self.data.voyage_plans:
            if plan.voyage_id not in self.current_voyages:
                vessel = self.data.vessels.get(plan.vessel_id)
                available.append({
                    'voyage_id': plan.voyage_id,
                    'vessel': vessel.vessel_name if vessel else plan.vessel_id,
                    'route': f"{plan.load_port} → {plan.disch_port}",
                    'cargo': plan.cargo_type,
                    'qty_mt': plan.qty_mt,
                    'laycan': f"{plan.laycan_start.strftime('%d.%m')} - {plan.laycan_end.strftime('%d.%m')}"
                })
        return available
    
    def _check_conflicts(self, voyage_id: str) -> Optional[str]:
        """Проверка конфликтов расписания"""
        # Получаем план нового рейса
        new_plan = None
        for plan in self.data.voyage_plans:
            if plan.voyage_id == voyage_id:
                new_plan = plan
                break
        
        if not new_plan:
            return None
        
        # Проверяем пересечение с существующими рейсами того же судна
        for existing_id in self.current_voyages:
            for plan in self.data.voyage_plans:
                if plan.voyage_id == existing_id and plan.vessel_id == new_plan.vessel_id:
                    # Простая проверка по laycan (можно уточнить после расчёта)
                    if (new_plan.laycan_start <= plan.laycan_end and 
                        new_plan.laycan_end >= plan.laycan_start):
                        return f"Судно {new_plan.vessel_id} уже занято рейсом {existing_id}"
        
        return None
    
    def save_as_scenario(self, scenario_id: str, scenario_name: str, description: str = "") -> Scenario:
        """Сохранить как сценарий"""
        return Scenario(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            description=description,
            voyage_ids=self.current_voyages.copy(),
            calculated_voyages=self.calculated_data.calculated_voyages if self.calculated_data else {}
        )