"""
Калькулятор расписания
======================

Автоматический расчёт дат операций на основе конфигурации рейсов
"""

from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
import logging

from modules.olya_data import (
    OlyaData, OlyaParams, Vessel, VoyageConfig,
    CalculatedOperation, CalculatedVoyage
)

logger = logging.getLogger(__name__)


class OlyaVoyageCalculator:
    """
    Калькулятор рейсов
    
    Принцип:
    1. Берём конфигурацию рейса (последовательность операций)
    2. Для первой операции берём start_date из конфига
    3. Для остальных рассчитываем: start = end предыдущей + turnaround
    4. Duration рассчитывается по типу операции
    """
    
    def __init__(self, data: OlyaData):
        self.data = data
        self.params = data.params
    
    def calculate_all(self) -> OlyaData:
        """Рассчитать все рейсы"""
        logger.info("\n" + "=" * 70)
        logger.info("РАСЧЁТ РАСПИСАНИЯ")
        logger.info("=" * 70)
        
        # Группируем конфиги по voyage_id
        configs_by_voyage: Dict[str, List[VoyageConfig]] = {}
        for config in self.data.voyage_configs:
            if config.voyage_id not in configs_by_voyage:
                configs_by_voyage[config.voyage_id] = []
            configs_by_voyage[config.voyage_id].append(config)
        
        # Сортируем операции в каждом рейсе
        for voyage_id in configs_by_voyage:
            configs_by_voyage[voyage_id].sort(key=lambda x: x.seq)
        
        # Рассчитываем каждый рейс
        all_operations = []
        
        for voyage_id, configs in configs_by_voyage.items():
            voyage = self._calculate_voyage(voyage_id, configs)
            if voyage:
                self.data.calculated_voyages[voyage_id] = voyage
                all_operations.extend(voyage.operations)
                
                logger.info(f"   {voyage_id}: {voyage.vessel_name} | "
                           f"{voyage.start_time.strftime('%d.%m') if voyage.start_time else 'N/A'} - "
                           f"{voyage.end_time.strftime('%d.%m') if voyage.end_time else 'N/A'} | "
                           f"{voyage.total_duration_days:.1f} дней")
        
        # Сортируем все операции по времени
        all_operations.sort(key=lambda x: x.start_time)
        self.data.calculated_operations = all_operations
        
        logger.info(f"\n  Рассчитано рейсов: {len(self.data.calculated_voyages)}")
        logger.info(f"  Всего операций: {len(all_operations)}")
        
        return self.data
    
    def _calculate_voyage(
        self, 
        voyage_id: str, 
        configs: List[VoyageConfig]
    ) -> Optional[CalculatedVoyage]:
        """Расчёт одного рейса"""
        if not configs:
            return None
        
        # Получаем судно
        vessel_id = configs[0].vessel_id
        vessel = self.data.get_vessel(vessel_id)
        if not vessel:
            logger.warning(f"   Судно {vessel_id} не найдено")
            return None
        
        # Получаем start_date первой операции
        first_config = configs[0]
        if not first_config.start_date:
            logger.warning(f"   {voyage_id}: не указана start_date для первой операции")
            return None
        
        # Создаём рейс
        voyage = CalculatedVoyage(
            voyage_id=voyage_id,
            vessel_id=vessel_id,
            vessel_name=vessel.vessel_name,
            vessel_type=vessel.vessel_type
        )
        
        # Рассчитываем каждую операцию
        current_time = datetime.combine(first_config.start_date, datetime.min.time())
        current_time = current_time.replace(hour=8)  # Начинаем в 08:00
        
        for config in configs:
            # Рассчитываем длительность
            duration_hours = self._calculate_duration(config, vessel)
            
            # Создаём операцию
            operation = CalculatedOperation(
                voyage_id=voyage_id,
                vessel_id=vessel_id,
                vessel_name=vessel.vessel_name,
                seq=config.seq,
                operation=config.operation,
                port=config.port,
                cargo=config.cargo,
                qty_mt=config.qty_mt,
                start_time=current_time,
                end_time=current_time + timedelta(hours=duration_hours),
                duration_hours=duration_hours,
                can_optimize=(config.operation == 'waiting'),
                remarks=config.remarks
            )
            
            voyage.operations.append(operation)
            
            # Следующая операция начинается после окончания текущей + turnaround
            current_time = operation.end_time + timedelta(hours=self.params.port_turnaround)
        
        return voyage
    
    def _calculate_duration(self, config: VoyageConfig, vessel: Vessel) -> float:
        """
        Расчёт длительности операции (в часах)
        
        Типы:
        - loading: qty / load_rate * 24
        - discharge: qty / discharge_rate * 24
        - transit: distance / speed
        - waiting: фиксированное время (из конфига или дефолт)
        """
        operation = config.operation.lower()
        qty = config.qty_mt
        
        if operation == 'loading':
            # Определяем норму загрузки по порту
            port = config.port.upper()
            if port == 'BKO':
                rate = self.params.load_rate_bko
            elif port == 'OYA':
                rate = self.params.load_rate_oya
            else:
                rate = self.params.load_rate_oya  # Default
            
            if qty > 0 and rate > 0:
                return (qty / rate) * 24
            return 48  # Default 2 дня
        
        elif operation == 'discharge':
            port = config.port.upper()
            if port == 'OYA':
                rate = self.params.discharge_rate_oya
            elif port in ['AMI', 'ANZ']:
                rate = self.params.discharge_rate_iran
            else:
                rate = self.params.discharge_rate_oya
            
            if qty > 0 and rate > 0:
                return (qty / rate) * 24
            return 48
        
        elif operation == 'transit':
            # Получаем расстояние
            distance = self.data.get_distance(config.port, config.port)
            
            # Если port = "BKO-OYA", извлекаем расстояние
            if '-' in config.port:
                parts = config.port.split('-')
                if len(parts) == 2:
                    distance = self.data.get_distance(parts[0], parts[1])
            
            if distance is None:
                logger.warning(f"   Расстояние не найдено для {config.port}")
                distance = 500  # Default
            
            # Скорость судна
            speed = vessel.speed_kn if vessel.speed_kn > 0 else (
                self.params.speed_barge if vessel.is_barge else self.params.speed_vessel
            )
            
            return distance / speed
        
        elif operation == 'waiting':
            # Ожидание - берём из qty_mt если указано (как часы), иначе дефолт
            if qty > 0:
                return qty  # qty_mt используется как часы ожидания
            return 24  # Default 1 день
        
        elif operation == 'bunkering':
            return 12  # Default 12 часов
        
        else:
            return 24  # Default
    
    def get_schedule_dataframe(self):
        """Получить расписание как DataFrame"""
        import pandas as pd
        
        rows = []
        for op in self.data.calculated_operations:
            rows.append({
                'voyage_id': op.voyage_id,
                'vessel_id': op.vessel_id,
                'vessel_name': op.vessel_name,
                'seq': op.seq,
                'operation': op.operation,
                'port': op.port,
                'cargo': op.cargo,
                'qty_mt': op.qty_mt,
                'start_time': op.start_time,
                'end_time': op.end_time,
                'duration_hours': round(op.duration_hours, 1),
                'duration_days': round(op.duration_hours / 24, 2),
                'can_optimize': op.can_optimize,
                'remarks': op.remarks
            })
        
        return pd.DataFrame(rows)
    
    def export_schedule_csv(self, filepath: str):
        """Экспорт расписания в CSV"""
        df = self.get_schedule_dataframe()
        df.to_csv(filepath, index=False, sep=';', encoding='utf-8')
        logger.info(f"   Расписание сохранено: {filepath}")