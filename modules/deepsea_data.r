"""
Структуры данных для Deep Sea
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum


class LegType(Enum):
    """Типы плеч"""
    LOADING = "loading"
    DISCHARGE = "discharge"
    SEA = "sea"
    CANAL = "canal"
    BUNKER = "bunker"
    WAITING = "waiting"


class CargoState(Enum):
    """Состояние груза"""
    LADEN = "laden"
    BALLAST = "ballast"


@dataclass
class Port:
    """Порт"""
    port_id: str
    port_name: str
    country: str
    region: str
    latitude: float
    longitude: float
    port_type: str  # load, discharge, transit, bunker
    max_draft_m: float
    load_rate_mt_day: float
    disch_rate_mt_day: float
    port_charges_usd: float
    remarks: str = ""


@dataclass
class Distance:
    """Расстояние между портами"""
    from_port: str
    to_port: str
    distance_nm: float
    via_canal: bool
    canal_id: Optional[str]
    eca_miles: float  # Мили в ECA зоне


@dataclass
class Canal:
    """Канал"""
    canal_id: str
    canal_name: str
    transit_hours: float
    base_fee_usd: float
    fee_per_ton_usd: float
    max_draft_m: float
    max_beam_m: float
    max_loa_m: float
    waiting_hours_avg: float


@dataclass
class Vessel:
    """Deep Sea судно"""
    vessel_id: str
    vessel_name: str
    imo: str
    vessel_type: str
    vessel_class: str  # MR2, MR1, Handysize, etc.
    dwt_mt: float
    capacity_mt: float
    loa_m: float
    beam_m: float
    draft_laden_m: float
    draft_ballast_m: float
    speed_laden_kn: float
    speed_ballast_kn: float
    consumption_laden_mt: float  # Топливо в сутки (MT)
    consumption_ballast_mt: float
    daily_hire_usd: float
    owner: str
    flag: str
    built_year: int
    ice_class: str
    tank_coated: bool
    heating_capable: bool
    
    def can_transit_canal(self, canal: Canal) -> bool:
        """Проверка возможности прохода канала"""
        if canal.max_draft_m > 0 and self.draft_laden_m > canal.max_draft_m:
            return False
        if canal.max_beam_m > 0 and self.beam_m > canal.max_beam_m:
            return False
        if canal.max_loa_m > 0 and self.loa_m > canal.max_loa_m:
            return False
        return True
    
    def can_enter_port(self, port: Port, laden: bool = True) -> bool:
        """Проверка возможности захода в порт"""
        draft = self.draft_laden_m if laden else self.draft_ballast_m
        return draft <= port.max_draft_m


@dataclass
class RouteLeg:
    """Плечо маршрута (шаблон)"""
    route_id: str
    route_name: str
    leg_seq: int
    leg_type: str  # loading, discharge, sea, canal, bunker
    from_port: str
    to_port: str
    cargo_state: str  # laden, ballast
    canal_id: Optional[str]
    remarks: str = ""


@dataclass
class VoyagePlan:
    """План рейса (входные данные)"""
    voyage_id: str
    vessel_id: str
    route_id: str
    cargo_type: str
    qty_mt: float
    load_port: str
    disch_port: str
    laycan_start: date
    laycan_end: date
    charterer: str
    freight_rate_mt: float
    remarks: str = ""


@dataclass
class CalculatedLeg:
    """Рассчитанное плечо"""
    voyage_id: str
    vessel_id: str
    vessel_name: str
    leg_seq: int
    leg_type: str
    from_port: str
    to_port: str
    cargo_state: str
    
    # Время
    start_time: datetime
    end_time: datetime
    duration_hours: float
    
    # Расстояние (для sea legs)
    distance_nm: float = 0
    speed_kn: float = 0
    
    # Груз
    cargo_type: str = ""
    qty_mt: float = 0
    
    # Стоимость
    bunker_cost_usd: float = 0
    port_cost_usd: float = 0
    canal_cost_usd: float = 0
    
    # Метаданные
    canal_id: Optional[str] = None
    remarks: str = ""
    
    @property
    def duration_days(self) -> float:
        return self.duration_hours / 24


@dataclass
class CalculatedVoyage:
    """Рассчитанный рейс"""
    voyage_id: str
    vessel_id: str
    vessel_name: str
    vessel_class: str
    route_id: str
    
    # Груз
    cargo_type: str
    qty_mt: float
    load_port: str
    disch_port: str
    
    # Время
    laycan_start: date
    laycan_end: date
    actual_start: datetime
    actual_end: datetime
    
    # Плечи
    legs: List[CalculatedLeg] = field(default_factory=list)
    
    # Финансы
    freight_revenue_usd: float = 0
    total_bunker_cost_usd: float = 0
    total_port_cost_usd: float = 0
    total_canal_cost_usd: float = 0
    hire_cost_usd: float = 0
    
    # Статистика
    total_distance_nm: float = 0
    sea_days: float = 0
    port_days: float = 0
    
    charterer: str = ""
    remarks: str = ""
    
    @property
    def total_days(self) -> float:
        if self.actual_start and self.actual_end:
            return (self.actual_end - self.actual_start).total_seconds() / 86400
        return 0
    
    @property
    def total_cost_usd(self) -> float:
        return (self.total_bunker_cost_usd + self.total_port_cost_usd + 
                self.total_canal_cost_usd + self.hire_cost_usd)
    
    @property
    def profit_usd(self) -> float:
        return self.freight_revenue_usd - self.total_cost_usd
    
    @property
    def tce_usd(self) -> float:
        """Time Charter Equivalent"""
        if self.total_days > 0:
            net_revenue = self.freight_revenue_usd - self.total_bunker_cost_usd - self.total_port_cost_usd - self.total_canal_cost_usd
            return net_revenue / self.total_days
        return 0


@dataclass
class DeepSeaParams:
    """Параметры системы"""
    # Скорости
    default_speed_laden: float = 13.5
    default_speed_ballast: float = 14.5
    eco_speed_laden: float = 11.0
    eco_speed_ballast: float = 12.0
    
    # Время в портах
    port_waiting_hours: float = 12
    pilot_boarding_hours: float = 2
    berthing_hours: float = 2
    departure_hours: float = 3
    
    # Нормы погрузки
    default_load_rate: float = 5000
    default_disch_rate: float = 5000
    
    # Бункер
    bunker_ifo_price: float = 450
    bunker_mgo_price: float = 650
    bunker_time_hours: float = 8
    
    # Ставки
    demurrage_rate: float = 25000
    despatch_rate: float = 12500
    canal_waiting_buffer: float = 6
    
    # Weather margins
    weather_margin_pct: float = 5
    winter_margin_pct: float = 10
    monsoon_margin_pct: float = 15
    
    @property
    def port_overhead_hours(self) -> float:
        """Общие накладные часы в порту"""
        return self.port_waiting_hours + self.pilot_boarding_hours + self.berthing_hours + self.departure_hours


@dataclass
class DeepSeaData:
    """Контейнер всех данных"""
    params: DeepSeaParams = field(default_factory=DeepSeaParams)
    ports: Dict[str, Port] = field(default_factory=dict)
    distances: Dict[Tuple[str, str], Distance] = field(default_factory=dict)
    canals: Dict[str, Canal] = field(default_factory=dict)
    vessels: Dict[str, Vessel] = field(default_factory=dict)
    route_legs: Dict[str, List[RouteLeg]] = field(default_factory=dict)  # route_id -> legs
    voyage_plans: List[VoyagePlan] = field(default_factory=list)
    
    # Рассчитанные данные
    calculated_voyages: Dict[str, CalculatedVoyage] = field(default_factory=dict)
    
    def get_distance(self, from_port: str, to_port: str) -> Optional[Distance]:
        """Получить расстояние"""
        key = (from_port, to_port)
        return self.distances.get(key)
    
    def get_route_legs(self, route_id: str) -> List[RouteLeg]:
        """Получить плечи маршрута"""
        return self.route_legs.get(route_id, [])