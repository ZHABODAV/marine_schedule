"""
Balakovo Berth Planner

Advanced berth planning with constraint validation for Balakovo terminal.
Assigns vessels to berths considering:
- Cargo type (oil → tanker berth, meal → dry berth)
- Restrictions (weather, maintenance, holidays)
- Cargo priorities
- Loading windows
- Advanced berth constraints (if configured)
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass

from modules.balakovo_data import (
    BalakovoData, BalakovoParams, Berth, BalakovoVessel,
    CargoPlan, Restriction, BerthingSlot, BerthSchedule, BerthingStatus
)
from modules.berth_constraints import (
    BerthConstraintValidator, ConstraintViolation, ConstraintSeverity
)
from modules.profiler import profile_performance

logger = logging.getLogger(__name__)


@dataclass
class PlanningConflict:
    """Planning conflict record"""
    cargo_id: str
    conflict_type: str  # no_vessel, no_berth, window_exceeded, restriction, constraint_violation
    description: str
    severity: str  # warning, error


class BalakovoPlanner:
    """
    Advanced Berth Planner
    
    Algorithm:
    1. Sort cargo by priority and date
    2. For each cargo:
       - Find suitable vessel
       - Find suitable berth
       - Validate against advanced constraints (if available)
       - Find free time window
       - Create berth slot
    3. Check conflicts and constraint violations
    """
    
    def __init__(self, data: BalakovoData):
        self.data = data
        self.params = data.params
        self.conflicts: List[PlanningConflict] = []
        
        # Initialize constraint validator if berths have constraints
        constraint_sets = {
            berth_id: berth.constraint_set
            for berth_id, berth in data.berths.items()
            if berth.constraint_set is not None
        }
        self.constraint_validator = BerthConstraintValidator(constraint_sets) if constraint_sets else None
        
        # Initialize berth schedules
        for berth_id, berth in data.berths.items():
            data.schedules[berth_id] = BerthSchedule(
                berth_id=berth_id,
                berth_name=berth.berth_name
            )
        
        logger.info(f"Initialized planner with constraint validation: {self.constraint_validator is not None}")
    
    @profile_performance
    def plan(self) -> BalakovoData:
        """Построить план постановок"""
        logger.info("\n" + "=" * 60)
        logger.info(" ПЛАНИРОВАНИЕ ПРИЧАЛА БАЛАКОВО")
        logger.info("=" * 60)
        
        # Сортируем грузы
        sorted_cargo = sorted(
            self.data.cargo_plans,
            key=lambda x: (x.priority, x.earliest_date)
        )
        
        slot_counter = 0
        
        for cargo in sorted_cargo:
            logger.info(f"\n {cargo.cargo_id}: {cargo.cargo_type} {cargo.qty_mt:,.0f} MT → {cargo.destination}")
            
            # 1. Находим судно
            vessel = self._find_vessel(cargo)
            if not vessel:
                self._add_conflict(cargo.cargo_id, 'no_vessel', 
                                  f"Нет подходящего судна для {cargo.cargo_type}")
                self.data.unassigned_cargo.append(cargo)
                continue
            
            logger.info(f"   Судно: {vessel.vessel_name}")
            
            # 2. Находим причал
            berth = self._find_berth(cargo, vessel)
            if not berth:
                self._add_conflict(cargo.cargo_id, 'no_berth',
                                  f"Нет подходящего причала для {vessel.vessel_name}")
                self.data.unassigned_cargo.append(cargo)
                continue
            
            logger.info(f"   Причал: {berth.berth_name}")
            
            # 3. Находим свободное окно
            slot = self._find_slot(cargo, vessel, berth)
            if not slot:
                self._add_conflict(cargo.cargo_id, 'no_window',
                                  f"Нет свободного окна в период {cargo.earliest_date} - {cargo.latest_date}")
                self.data.unassigned_cargo.append(cargo)
                continue
            
            # 4. Добавляем слот
            slot_counter += 1
            slot.slot_id = f"SLOT_{slot_counter:03d}"
            self.data.schedules[berth.berth_id].slots.append(slot)
            
            logger.info(f"    Запланировано: {slot.berthing_start.strftime('%d.%m %H:%M')} - {slot.departure.strftime('%d.%m %H:%M')}")
            
            if slot.has_waiting:
                logger.info(f"    Ожидание: {slot.waiting_hours:.1f}ч")
        
        # Итоги
        self._print_summary()
        
        # Сохраняем конфликты
        self.data.conflicts = [
            {'cargo_id': c.cargo_id, 'type': c.conflict_type, 
             'description': c.description, 'severity': c.severity}
            for c in self.conflicts
        ]
        
        return self.data
    
    def _find_vessel(self, cargo: CargoPlan) -> Optional[BalakovoVessel]:
        """Найти подходящее судно"""
        # Если указано предпочтение - пробуем его
        if cargo.vessel_preference:
            vessel = self.data.vessels.get(cargo.vessel_preference)
            if vessel and vessel.cargo_type == cargo.cargo_type:
                if self._is_vessel_available(vessel, cargo.earliest_date, cargo.latest_date):
                    return vessel
        
        # Ищем любое подходящее
        for vessel in self.data.vessels.values():
            # Проверяем тип груза
            if vessel.cargo_type != cargo.cargo_type:
                continue
            
            # Проверяем направление
            if cargo.destination == 'OYA' and not vessel.goes_to_olya:
                continue
            if cargo.destination == 'TUR' and not vessel.goes_to_turkey:
                continue
            
            # Проверяем вместимость
            if vessel.capacity_mt < cargo.qty_mt:
                continue
            
            # Проверяем доступность
            if self._is_vessel_available(vessel, cargo.earliest_date, cargo.latest_date):
                return vessel
        
        return None
    
    def _is_vessel_available(self, vessel: BalakovoVessel, start: date, end: date) -> bool:
        """Проверка доступности судна"""
        # Проверяем не занято ли судно в других слотах
        for schedule in self.data.schedules.values():
            for slot in schedule.slots:
                if slot.vessel_id == vessel.vessel_id:
                    slot_start = slot.berthing_start.date()
                    slot_end = slot.departure.date()
                    
                    # Проверяем пересечение
                    if slot_start <= end and slot_end >= start:
                        return False
        
        return True
    
    def _find_berth(self, cargo: CargoPlan, vessel: BalakovoVessel) -> Optional[Berth]:
        """Найти подходящий причал"""
        suitable = []
        
        for berth in self.data.berths.values():
            # Проверяем тип груза
            if not berth.can_handle_cargo(cargo.cargo_type):
                continue
            
            # Проверяем размеры судна
            if not berth.can_handle_vessel(vessel):
                continue
            
            suitable.append(berth)
        
        # Сортируем по приоритету (24ч причалы первые, потом по норме погрузки)
        suitable.sort(key=lambda b: (-b.working_hours, -b.load_rate_mt_day))
        
        return suitable[0] if suitable else None
    
    def _find_slot(
        self,
        cargo: CargoPlan,
        vessel: BalakovoVessel,
        berth: Berth
    ) -> Optional[BerthingSlot]:
        """
        Find free time window and create berth slot with constraint validation.
        """
        schedule = self.data.schedules[berth.berth_id]
        
        # Calculate durations
        loading_hours, total_berth_hours = self._calculate_durations(cargo)
        
        # Check transition time
        transition_time = self._get_transition_time(berth, schedule, cargo)
        
        # Search for window starting from earliest_date
        current_date = cargo.earliest_date
        
        while current_date <= cargo.latest_date:
            # Check basic restrictions
            if self.data.is_date_blocked(current_date, berth.berth_id):
                current_date += timedelta(days=1)
                continue
            
            # Determine start time
            start_time = self._determine_start_time(
                current_date, schedule, transition_time
            )
            
            # Check advanced time window constraints
            if berth.has_advanced_constraints:
                if not berth.is_time_window_available(start_time, 'berthing'):
                    current_date += timedelta(days=1)
                    continue
            
            # Calculate end time
            end_time = start_time + timedelta(hours=total_berth_hours)
            
            # Validate window validity (overlap, blocked dates, deadline)
            if not self._is_window_valid(
                start_time, end_time, cargo.latest_date, schedule, berth.berth_id
            ):
                current_date += timedelta(days=1)
                continue
            
            # Validate against advanced constraints if available
            if not self._validate_advanced_constraints(
                berth, vessel, cargo, start_time
            ):
                current_date += timedelta(days=1)
                continue
            
            # Create slot
            return self._create_slot(
                cargo, vessel, berth, start_time, loading_hours, total_berth_hours
            )
        
        return None

    def _calculate_durations(self, cargo: CargoPlan) -> Tuple[float, float]:
        """Calculate loading and total berth hours."""
        load_rate = self.params.get_load_rate(cargo.cargo_type)
        loading_hours = (cargo.qty_mt / load_rate) * 24
        
        total_berth_hours = (
            self.params.berthing_hours +
            loading_hours +
            self.params.unberthing_hours +
            self.params.doc_clearance_hours
        )
        return loading_hours, total_berth_hours

    def _get_transition_time(
        self, berth: Berth, schedule: BerthSchedule, cargo: CargoPlan
    ) -> float:
        """Calculate required transition/cleaning time."""
        transition_time = 0
        if berth.has_advanced_constraints and schedule.slots:
            last_slot = schedule.slots[-1]
            transition_time = berth.get_cleaning_time(last_slot.cargo_type, cargo.cargo_type)
            if transition_time > 0:
                logger.info(f"   Cargo transition required: {transition_time}h from {last_slot.cargo_type} to {cargo.cargo_type}")
        return transition_time

    def _determine_start_time(
        self, current_date: date, schedule: BerthSchedule, transition_time: float
    ) -> datetime:
        """Determine potential start time for berthing."""
        start_time = datetime.combine(current_date, datetime.min.time())
        start_time = start_time.replace(hour=self.params.working_hours_start)
        
        next_available = schedule.get_next_available(start_time)
        
        if next_available > start_time:
            start_time = next_available + timedelta(hours=self.params.safety_buffer_hours + transition_time)
        elif transition_time > 0:
            start_time += timedelta(hours=transition_time)
            
        return start_time

    def _is_window_valid(
        self,
        start_time: datetime,
        end_time: datetime,
        latest_date: date,
        schedule: BerthSchedule,
        berth_id: str
    ) -> bool:
        """Check if the time window is valid (no overlaps, within deadline, not blocked)."""
        # Check deadline
        if end_time.date() > latest_date:
            return False
        
        # Check overlap
        if schedule.is_occupied(start_time, end_time):
            return False
        
        # Check blocked dates in range
        check_date = start_time.date()
        while check_date <= end_time.date():
            if self.data.is_date_blocked(check_date, berth_id):
                return False
            check_date += timedelta(days=1)
            
        return True

    def _validate_advanced_constraints(
        self,
        berth: Berth,
        vessel: BalakovoVessel,
        cargo: CargoPlan,
        start_time: datetime
    ) -> bool:
        """Validate against advanced constraints if validator exists."""
        if not self.constraint_validator:
            return True
            
        is_valid, violations = self.constraint_validator.validate_berthing(
            berth_id=berth.berth_id,
            vessel_id=vessel.vessel_id,
            vessel_class=vessel.vessel_class,
            loa=vessel.loa_m,
            beam=vessel.beam_m,
            draft=vessel.draft_m,
            cargo_type=cargo.cargo_type,
            berthing_time=start_time,
            priority=cargo.priority
        )
        
        if not is_valid:
            for violation in violations:
                logger.warning(f"    Constraint violation: {violation.description}")
                self._add_conflict(
                    cargo.cargo_id,
                    'constraint_violation',
                    f"{violation.violation_type.value}: {violation.description}"
                )
            return False
            
        return True

    def _create_slot(
        self,
        cargo: CargoPlan,
        vessel: BalakovoVessel,
        berth: Berth,
        start_time: datetime,
        loading_hours: float,
        total_berth_hours: float
    ) -> BerthingSlot:
        """Create and populate BerthingSlot object."""
        eta = start_time - timedelta(hours=2)  # Arrival 2 hours before
        berthing_start = start_time
        loading_start = berthing_start + timedelta(hours=self.params.berthing_hours)
        loading_end = loading_start + timedelta(hours=loading_hours)
        departure = loading_end + timedelta(hours=self.params.unberthing_hours + self.params.doc_clearance_hours)
        
        # Calculate waiting time
        waiting_hours = 0
        if eta.date() < cargo.earliest_date:
            waiting_hours = (datetime.combine(cargo.earliest_date, datetime.min.time()) - eta).total_seconds() / 3600
        
        return BerthingSlot(
            slot_id="",  # Will be assigned later
            berth_id=berth.berth_id,
            vessel_id=vessel.vessel_id,
            vessel_name=vessel.vessel_name,
            cargo_id=cargo.cargo_id,
            cargo_type=cargo.cargo_type,
            qty_mt=cargo.qty_mt,
            destination=cargo.destination,
            eta=eta,
            berthing_start=berthing_start,
            loading_start=loading_start,
            loading_end=loading_end,
            departure=departure,
            status=BerthingStatus.PLANNED,
            waiting_hours=waiting_hours,
            loading_hours=loading_hours,
            total_hours=total_berth_hours,
            remarks=cargo.remarks
        )
    
    def _add_conflict(self, cargo_id: str, conflict_type: str, description: str):
        """Добавить конфликт"""
        conflict = PlanningConflict(
            cargo_id=cargo_id,
            conflict_type=conflict_type,
            description=description,
            severity='error' if conflict_type in ['no_vessel', 'no_berth'] else 'warning'
        )
        self.conflicts.append(conflict)
        logger.warning(f"    {description}")
    
    def _print_summary(self):
        """Печать сводки"""
        logger.info("\n" + "=" * 60)
        logger.info(" РЕЗУЛЬТАТЫ ПЛАНИРОВАНИЯ")
        logger.info("=" * 60)
        
        total_slots = sum(len(s.slots) for s in self.data.schedules.values())
        total_cargo = sum(
            slot.qty_mt 
            for schedule in self.data.schedules.values() 
            for slot in schedule.slots
        )
        
        logger.info(f"  Запланировано постановок: {total_slots}")
        logger.info(f"  Запланировано груза: {total_cargo:,.0f} MT")
        logger.info(f"  Не назначено: {len(self.data.unassigned_cargo)}")
        logger.info(f"  Конфликтов: {len(self.conflicts)}")
        
        # По причалам
        logger.info("\n  По причалам:")
        for berth_id, schedule in self.data.schedules.items():
            berth = self.data.berths[berth_id]
            slots = len(schedule.slots)
            cargo = sum(s.qty_mt for s in schedule.slots)
            logger.info(f"    {berth.berth_name}: {slots} постановок, {cargo:,.0f} MT")
        
        # По направлениям
        olya_qty = sum(
            s.qty_mt for sch in self.data.schedules.values() 
            for s in sch.slots if s.destination == 'OYA'
        )
        tur_qty = sum(
            s.qty_mt for sch in self.data.schedules.values()
            for s in sch.slots if s.destination == 'TUR'
        )
        
        logger.info("\n  По направлениям:")
        logger.info(f"    → Olya: {olya_qty:,.0f} MT")
        logger.info(f"    → Turkey: {tur_qty:,.0f} MT")
