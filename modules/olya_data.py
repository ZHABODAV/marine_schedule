"""
Структуры данных для Olya
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum


class OperationType(Enum):
    """Типы операций"""
    LOADING = "loading"
    DISCHARGE = "discharge"
    TRANSIT = "transit"
    WAITING = "waiting"
    BUNKERING = "bunkering"


@dataclass
class OlyaParams:
    """Параметры системы"""
    # Скорости (узлы)
    speed_barge: float = 8.0
    speed_vessel: float = 10.0
    
    # Нормы погрузки (MT/день)
    load_rate_bko: float = 2500      # Балаково
    load_rate_oya: float = 3000      # Olya
    discharge_rate_oya: float = 2500  # Разгрузка барж в Olya
    discharge_rate_iran: float = 3500 # Выгрузка в Иране
    
    # Хранилище Olya
    storage_capacity: float = 10000
    storage_initial: float = 0
    
    # Буферы (часы)
    port_turnaround: float = 4       # Оформление в порту
    ideal_buffer: float = 6          # Идеальный буфер между операциями
    
    # Ставки (USD)
    demurrage_barge: float = 3000    # За день
    demurrage_vessel: float = 15000  # За день


@dataclass
class Port:
    """Порт"""
    port_id: str
    port_name: str
    country: str
    port_type: str  # river, transship, sea


@dataclass
class Distance:
    """Расстояние между портами"""
    from_port: str
    to_port: str
    distance_nm: float


@dataclass
class Vessel:
    """Судно"""
    vessel_id: str
    vessel_name: str
    vessel_type: str  # barge, vessel
    vessel_class: str
    capacity_mt: float
    draft_m: float
    speed_kn: float
    daily_rate_usd: float
    owner: str = ""
    
    @property
    def is_barge(self) -> bool:
        return self.vessel_type.lower() == 'barge'
    
    @property
    def is_vessel(self) -> bool:
        return self.vessel_type.lower() == 'vessel'


@dataclass
class VoyageConfig:
    """Конфигурация одной операции в рейсе (из CSV)"""
    voyage_id: str
    vessel_id: str
    seq: int
    operation: str  # loading, discharge, transit, waiting
    port: str
    cargo: str
    qty_mt: float
    start_date: Optional[date]  # Только для первой операции
    remarks: str = ""


@dataclass
class CalculatedOperation:
    """Рассчитанная операция с датами"""
    voyage_id: str
    vessel_id: str
    vessel_name: str
    seq: int
    operation: str
    port: str
    cargo: str
    qty_mt: float
    
    # Рассчитанные даты
    start_time: datetime
    end_time: datetime
    duration_hours: float
    
    # Метаданные
    can_optimize: bool = False  # True для waiting
    remarks: str = ""
    
    @property
    def duration_days(self) -> float:
        return self.duration_hours / 24
    
    @property
    def is_at_olya(self) -> bool:
        return self.port.upper() == 'OYA'


@dataclass
class CalculatedVoyage:
    """Рассчитанный рейс"""
    voyage_id: str
    vessel_id: str
    vessel_name: str
    vessel_type: str
    operations: List[CalculatedOperation] = field(default_factory=list)
    
    # Cost Allocations
    operational_cost_allocation: float = 0  # Custom operational costs
    overhead_cost_allocation: float = 0     # Overhead allocation
    other_cost_allocation: float = 0        # Other allocated costs
    hire_cost_usd: float = 0                # Vessel hire costs
    bunker_cost_usd: float = 0              # Bunker costs
    port_cost_usd: float = 0                # Port costs
    
    @property
    def start_time(self) -> Optional[datetime]:
        if self.operations:
            return self.operations[0].start_time
        return None
    
    @property
    def end_time(self) -> Optional[datetime]:
        if self.operations:
            return self.operations[-1].end_time
        return None
    
    @property
    def total_duration_days(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 86400
        return 0
    
    @property
    def cargo(self) -> str:
        for op in self.operations:
            if op.cargo:
                return op.cargo
        return ""
    
    @property
    def total_qty_mt(self) -> float:
        for op in self.operations:
            if op.operation == 'loading' and op.qty_mt > 0:
                return op.qty_mt
        return 0
    
    @property
    def total_cost_usd(self) -> float:
        """Total cost including all allocations"""
        return (self.hire_cost_usd + self.bunker_cost_usd + self.port_cost_usd +
                self.operational_cost_allocation + self.overhead_cost_allocation +
                self.other_cost_allocation)


@dataclass
class OlyaData:
    """Контейнер всех данных"""
    params: OlyaParams = field(default_factory=OlyaParams)
    ports: Dict[str, Port] = field(default_factory=dict)
    distances: Dict[Tuple[str, str], float] = field(default_factory=dict)
    vessels: Dict[str, Vessel] = field(default_factory=dict)
    voyage_configs: List[VoyageConfig] = field(default_factory=list)
    
    # Рассчитанные данные
    calculated_voyages: Dict[str, CalculatedVoyage] = field(default_factory=dict)
    calculated_operations: List[CalculatedOperation] = field(default_factory=list)
    
    def get_vessel(self, vessel_id: str) -> Optional[Vessel]:
        return self.vessels.get(vessel_id)
    
    def get_distance(self, from_port: str, to_port: str) -> Optional[float]:
        # Пробуем прямой ключ
        key = (from_port, to_port)
        if key in self.distances:
            return self.distances[key]
        
        # Пробуем извлечь из transit port (например BKO-OYA)
        if '-' in from_port:
            parts = from_port.split('-')
            if len(parts) == 2:
                key = (parts[0], parts[1])
                if key in self.distances:
                    return self.distances[key]
        
        return None
    
    @property
    def barges(self) -> Dict[str, Vessel]:
        return {k: v for k, v in self.vessels.items() if v.is_barge}
    
    @property
    def sea_vessels(self) -> Dict[str, Vessel]:
        return {k: v for k, v in self.vessels.items() if v.is_vessel}