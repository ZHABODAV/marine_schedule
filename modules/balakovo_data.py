"""
Berth Planning Data Structures for Balakovo Terminal

Data structures for managing berth planning including vessels, cargo plans,
restrictions, and scheduling with advanced constraint support.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Set, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from modules.berth_constraints import BerthConstraintSet


class BerthType(Enum):
    """Тип причала"""
    LIQUID = "liquid"
    DRY = "dry"


class VesselType(Enum):
    """Тип судна"""
    BARGE = "barge"
    DRY = "dry"


class CargoType(Enum):
    """Тип груза"""
    SFO = "SFO"          # Подсолнечное масло
    RPO = "RPO"          # Рапсовое масло
    CSO = "CSO"          # Кукурузное масло
    MEAL = "MEAL"        # Шрот
    PELLETS = "PELLETS"  # Пеллеты
    GRAIN = "GRAIN"      # Зерно


class RestrictionSeverity(Enum):
    """Серьёзность ограничения"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BerthingStatus(Enum):
    """Статус постановки"""
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


@dataclass
class Berth:
    """
    Berth with advanced constraint support.
    
    Represents a physical berth with basic capabilities and optional
    advanced constraints for sophisticated planning.
    """
    berth_id: str
    berth_name: str
    berth_type: str  # liquid, dry
    max_loa_m: float
    max_beam_m: float
    max_draft_m: float
    cargo_types: Set[str]  # SFO, RPO, MEAL, PELLETS...
    load_rate_mt_day: float
    working_hours: int  # 24 or 12
    remarks: str = ""
    
    # Advanced constraints (optional)
    constraint_set: Optional['BerthConstraintSet'] = None
    
    def can_handle_vessel(self, vessel: 'BalakovoVessel') -> bool:
        """
        Check if berth can handle vessel using basic or advanced constraints.
        
        Args:
            vessel: Vessel to check
            
        Returns:
            True if vessel can be handled
        """
        # Use advanced constraints if available
        if self.constraint_set:
            is_valid, _ = self.constraint_set.validate_vessel_size(
                vessel.loa_m, vessel.beam_m, vessel.draft_m
            )
            if not is_valid:
                return False
            
            is_valid, _ = self.constraint_set.validate_vessel_class(vessel.vessel_class)
            if not is_valid:
                return False
            
            return True
        
        # Fallback to basic checks
        if vessel.loa_m > self.max_loa_m:
            return False
        if vessel.beam_m > self.max_beam_m:
            return False
        if vessel.draft_m > self.max_draft_m:
            return False
        return True
    
    def can_handle_cargo(self, cargo_type: str) -> bool:
        """
        Check if berth can handle cargo type using basic or advanced constraints.
        
        Args:
            cargo_type: Type of cargo
            
        Returns:
            True if cargo type can be handled
        """
        # Use advanced constraints if available
        if self.constraint_set:
            is_valid, _ = self.constraint_set.validate_cargo_type(cargo_type)
            return is_valid
        
        # Fallback to basic check
        return cargo_type.upper() in self.cargo_types
    
    def is_time_window_available(self, check_datetime: datetime, operation: str = 'loading') -> bool:
        """
        Check if operation is allowed at given time using advanced time window constraints.
        
        Args:
            check_datetime: Time to check
            operation: Operation type (berthing, loading, unberthing)
            
        Returns:
            True if operation is allowed at this time
        """
        if not self.constraint_set or not self.constraint_set.time_windows:
            return True
        
        for window in self.constraint_set.time_windows:
            is_allowed, _ = window.is_operation_allowed(check_datetime, operation)
            if is_allowed:
                return True
        
        return False
    
    def get_cargo_incompatibilities(self, cargo_type: str) -> List[str]:
        """
        Get list of cargo types incompatible with given cargo type.
        
        Args:
            cargo_type: Cargo type to check
            
        Returns:
            List of incompatible cargo types
        """
        if not self.constraint_set or not self.constraint_set.segregation_rules:
            return []
        
        incompatible = []
        for c1, c2 in self.constraint_set.segregation_rules.incompatible_pairs:
            if c1 == cargo_type:
                incompatible.append(c2)
            elif c2 == cargo_type:
                incompatible.append(c1)
        
        return incompatible
    
    def get_cleaning_time(self, from_cargo: str, to_cargo: str) -> float:
        """
        Get required cleaning/transition time between cargo types.
        
        Args:
            from_cargo: Previous cargo type
            to_cargo: Next cargo type
            
        Returns:
            Required transition time in hours
        """
        if not self.constraint_set or not self.constraint_set.segregation_rules:
            return 0.0
        
        return self.constraint_set.segregation_rules.get_transition_time(from_cargo, to_cargo)
    
    @property
    def is_24h(self) -> bool:
        """Check if berth operates 24 hours"""
        return self.working_hours == 24
    
    @property
    def has_advanced_constraints(self) -> bool:
        """Check if berth has advanced constraints configured"""
        return self.constraint_set is not None


@dataclass
class BalakovoVessel:
    """Судно для Балаково"""
    vessel_id: str
    vessel_name: str
    vessel_type: str  # barge, dry
    vessel_class: str
    cargo_type: str  # Основной тип груза
    capacity_mt: float
    loa_m: float
    beam_m: float
    draft_m: float
    speed_kn: float
    owner: str
    destination: str  # OYA, TUR
    remarks: str = ""
    
    @property
    def is_barge(self) -> bool:
        return self.vessel_type.lower() == 'barge'
    
    @property
    def is_dry(self) -> bool:
        return self.vessel_type.lower() == 'dry'
    
    @property
    def goes_to_olya(self) -> bool:
        return self.destination.upper() == 'OYA'
    
    @property
    def goes_to_turkey(self) -> bool:
        return self.destination.upper() == 'TUR'


@dataclass
class CargoPlan:
    """План отгрузки"""
    cargo_id: str
    cargo_type: str
    qty_mt: float
    destination: str  # OYA, TUR
    priority: int  # 1 = высший
    earliest_date: date
    latest_date: date
    vessel_preference: Optional[str]  # Предпочтительное судно
    remarks: str = ""
    
    @property
    def is_oil(self) -> bool:
        return self.cargo_type.upper() in ['SFO', 'RPO', 'CSO']
    
    @property
    def is_dry(self) -> bool:
        return self.cargo_type.upper() in ['MEAL', 'PELLETS', 'GRAIN']
    
    @property
    def window_days(self) -> int:
        return (self.latest_date - self.earliest_date).days


@dataclass
class Restriction:
    """Ограничение работы"""
    restriction_id: str
    restriction_type: str  # weather, water_level, maintenance, holiday
    start_date: date
    end_date: date
    berth_id: Optional[str]  # None = все причалы
    severity: str
    description: str
    
    def affects_date(self, check_date: date) -> bool:
        return self.start_date <= check_date <= self.end_date
    
    def affects_berth(self, berth_id: str) -> bool:
        if self.berth_id is None:
            return True
        return self.berth_id == berth_id
    
    @property
    def is_blocking(self) -> bool:
        return self.severity.lower() == 'high'


@dataclass
class BerthingSlot:
    """Слот постановки к причалу"""
    slot_id: str
    berth_id: str
    vessel_id: str
    vessel_name: str
    cargo_id: str
    cargo_type: str
    qty_mt: float
    destination: str
    
    # Время
    eta: datetime           # Прибытие судна
    berthing_start: datetime  # Начало швартовки
    loading_start: datetime   # Начало погрузки
    loading_end: datetime     # Окончание погрузки
    departure: datetime       # Отход
    
    # Статус
    status: BerthingStatus = BerthingStatus.PLANNED
    
    # Расчётные данные
    waiting_hours: float = 0  # Ожидание причала
    loading_hours: float = 0
    total_hours: float = 0
    
    remarks: str = ""
    
    @property
    def loading_days(self) -> float:
        return self.loading_hours / 24
    
    @property
    def has_waiting(self) -> bool:
        return self.waiting_hours > 0


@dataclass
class BerthSchedule:
    """Расписание причала"""
    berth_id: str
    berth_name: str
    slots: List[BerthingSlot] = field(default_factory=list)
    
    def get_slots_for_date(self, check_date: date) -> List[BerthingSlot]:
        """Слоты на конкретную дату"""
        result = []
        for slot in self.slots:
            slot_start = slot.berthing_start.date()
            slot_end = slot.departure.date()
            if slot_start <= check_date <= slot_end:
                result.append(slot)
        return result
    
    def is_occupied(self, start: datetime, end: datetime) -> bool:
        """Занят ли причал в период"""
        for slot in self.slots:
            if slot.berthing_start < end and slot.departure > start:
                return True
        return False
    
    def get_next_available(self, after: datetime) -> datetime:
        """Когда освободится причал"""
        latest_departure = after
        for slot in self.slots:
            if slot.departure > after and slot.departure > latest_departure:
                if slot.berthing_start <= after:
                    latest_departure = slot.departure
        return latest_departure


@dataclass
class BalakovoParams:
    """Параметры Балаково"""
    # Навигация
    season_start: Optional[date] = None
    season_end: Optional[date] = None
    
    # Время
    berthing_hours: float = 2
    unberthing_hours: float = 2
    doc_clearance_hours: float = 3
    safety_buffer_hours: float = 4
    
    # Нормы погрузки
    load_rate_sfo: float = 2500
    load_rate_rpo: float = 2200
    load_rate_meal: float = 1400
    load_rate_pellets: float = 1800
    
    # Ставки
    demurrage_barge: float = 8000
    demurrage_dry: float = 4000
    berth_fee_day: float = 0
    
    # Рабочее время
    working_hours_start: int = 6
    working_hours_end: int = 22
    night_work_allowed: bool = True
    
    def get_load_rate(self, cargo_type: str) -> float:
        """Норма погрузки по типу груза"""
        rates = {
            'SFO': self.load_rate_sfo,
            'RPO': self.load_rate_rpo,
            'CSO': self.load_rate_sfo,
            'MEAL': self.load_rate_meal,
            'PELLETS': self.load_rate_pellets,
            'GRAIN': self.load_rate_meal,
        }
        return rates.get(cargo_type.upper(), 2000)
    
    @property
    def port_overhead_hours(self) -> float:
        return self.berthing_hours + self.unberthing_hours + self.doc_clearance_hours


@dataclass
class BalakovoData:
    """Контейнер всех данных Балаково"""
    params: BalakovoParams = field(default_factory=BalakovoParams)
    berths: Dict[str, Berth] = field(default_factory=dict)
    vessels: Dict[str, BalakovoVessel] = field(default_factory=dict)
    cargo_plans: List[CargoPlan] = field(default_factory=list)
    restrictions: List[Restriction] = field(default_factory=list)
    
    # Рассчитанное расписание
    schedules: Dict[str, BerthSchedule] = field(default_factory=dict)
    unassigned_cargo: List[CargoPlan] = field(default_factory=list)
    conflicts: List[Dict] = field(default_factory=list)
    
    @property
    def liquid_berths(self) -> List[Berth]:
        return [b for b in self.berths.values() if b.berth_type == 'liquid']
    
    @property
    def dry_berths(self) -> List[Berth]:
        return [b for b in self.berths.values() if b.berth_type == 'dry']
    
    @property
    def barges(self) -> List[BalakovoVessel]:
        return [v for v in self.vessels.values() if v.is_barge]
    
    @property
    def dry_vessels(self) -> List[BalakovoVessel]:
        return [v for v in self.vessels.values() if v.is_dry]
    
    def get_restrictions_for_date(self, check_date: date, berth_id: Optional[str] = None) -> List[Restriction]:
        """Ограничения на дату"""
        result = []
        for r in self.restrictions:
            if r.affects_date(check_date):
                if berth_id is None or r.affects_berth(berth_id):
                    result.append(r)
        return result
    
    def is_date_blocked(self, check_date: date, berth_id: Optional[str] = None) -> bool:
        """Заблокирована ли дата"""
        restrictions = self.get_restrictions_for_date(check_date, berth_id)
        return any(r.is_blocking for r in restrictions)
