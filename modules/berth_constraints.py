"""
Advanced Berth Constraints Module

Provides sophisticated berth constraint management including:
- Vessel compatibility constraints
- Time-based operational windows
- Concurrent operations limits
- Cargo segregation rules
- Priority-based allocation
- Dynamic capacity management
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConstraintType(Enum):
    """Types of berth constraints"""
    VESSEL_SIZE = "vessel_size"  # LOA, beam, draft limits
    CARGO_TYPE = "cargo_type"  # Allowed cargo types
    TIME_WINDOW = "time_window"  # Operational time windows
    CONCURRENT_OPS = "concurrent_ops"  # Max concurrent operations
    SEGREGATION = "segregation"  # Cargo segregation rules
    EXCLUSIVITY = "exclusivity"  # Exclusive use periods
    MAINTENANCE = "maintenance"  # Maintenance windows
    WEATHER = "weather"  # Weather restrictions
    WATER_LEVEL = "water_level"  # Water level restrictions
    PRIORITY = "priority"  # Priority-based access


class ConstraintSeverity(Enum):
    """Constraint severity levels"""
    MANDATORY = "mandatory"  # Must be satisfied
    PREFERRED = "preferred"  # Should be satisfied if possible
    ADVISORY = "advisory"  # Nice to have


class ViolationType(Enum):
    """Types of constraint violations"""
    SIZE_EXCEEDED = "size_exceeded"
    INCOMPATIBLE_CARGO = "incompatible_cargo"
    OUTSIDE_TIME_WINDOW = "outside_time_window"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    SEGREGATION_CONFLICT = "segregation_conflict"
    PRIORITY_CONFLICT = "priority_conflict"
    WEATHER_RESTRICTION = "weather_restriction"
    MAINTENANCE_PERIOD = "maintenance_period"


@dataclass
class VesselSizeConstraint:
    """Physical size constraints for berth"""
    max_loa_m: float
    max_beam_m: float
    max_draft_m: float
    min_loa_m: float = 0.0
    min_beam_m: float = 0.0
    min_draft_m: float = 0.0
    allow_overhang: bool = False
    overhang_max_m: float = 0.0
    
    def validate_vessel(self, loa: float, beam: float, draft: float) -> Tuple[bool, Optional[str]]:
        """
        Validate if vessel meets size constraints.
        
        Args:
            loa: Length overall in meters
            beam: Beam in meters
            draft: Draft in meters
            
        Returns:
            Tuple of (is_valid, violation_message)
        """
        if loa > self.max_loa_m:
            overhang = loa - self.max_loa_m
            if self.allow_overhang and overhang <= self.overhang_max_m:
                return True, None
            return False, f"LOA {loa}m exceeds max {self.max_loa_m}m"
        
        if loa < self.min_loa_m:
            return False, f"LOA {loa}m below min {self.min_loa_m}m"
            
        if beam > self.max_beam_m:
            return False, f"Beam {beam}m exceeds max {self.max_beam_m}m"
            
        if beam < self.min_beam_m:
            return False, f"Beam {beam}m below min {self.min_beam_m}m"
            
        if draft > self.max_draft_m:
            return False, f"Draft {draft}m exceeds max {self.max_draft_m}m"
            
        if draft < self.min_draft_m:
            return False, f"Draft {draft}m below min {self.min_draft_m}m"
            
        return True, None


@dataclass
class TimeWindowConstraint:
    """Time-based operational constraints"""
    window_id: str
    start_time: time
    end_time: time
    days_of_week: Set[int] = field(default_factory=lambda: {0, 1, 2, 3, 4, 5, 6})  # 0=Monday
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    operations_allowed: Set[str] = field(default_factory=lambda: {'berthing', 'loading', 'unberthing'})
    severity: ConstraintSeverity = ConstraintSeverity.MANDATORY
    description: str = ""
    
    def is_operation_allowed(self, check_datetime: datetime, operation: str) -> Tuple[bool, Optional[str]]:
        """
        Check if operation is allowed at given time.
        
        Args:
            check_datetime: Time to check
            operation: Operation type (berthing, loading, unberthing)
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        # Check date range
        if self.start_date and check_datetime.date() < self.start_date:
            return False, f"Before window start {self.start_date}"
            
        if self.end_date and check_datetime.date() > self.end_date:
            return False, f"After window end {self.end_date}"
        
        # Check day of week
        if check_datetime.weekday() not in self.days_of_week:
            return False, f"Day {check_datetime.strftime('%A')} not allowed"
        
        # Check time of day
        check_time = check_datetime.time()
        if self.end_time > self.start_time:
            # Normal range (e.g., 08:00 - 18:00)
            if not (self.start_time <= check_time <= self.end_time):
                return False, f"Outside time window {self.start_time}-{self.end_time}"
        else:
            # Overnight range (e.g., 22:00 - 06:00)
            if not (check_time >= self.start_time or check_time <= self.end_time):
                return False, f"Outside time window {self.start_time}-{self.end_time}"
        
        # Check operation type
        if operation not in self.operations_allowed:
            return False, f"Operation '{operation}' not allowed in this window"
        
        return True, None


@dataclass
class ConcurrentOperationsConstraint:
    """Constraints on concurrent operations at berth"""
    max_vessels: int = 1
    max_berthing_ops: int = 1
    max_loading_ops: int = 1
    max_unberthing_ops: int = 1
    max_total_cargo_mt: Optional[float] = None
    allow_mixed_cargo_types: bool = True
    
    def validate_concurrent(
        self,
        current_vessels: int,
        current_berthing: int,
        current_loading: int,
        current_unberthing: int,
        current_cargo_mt: float
    ) -> Tuple[bool, Optional[str]]:
        """Validate if concurrent operations are within limits"""
        if current_vessels >= self.max_vessels:
            return False, f"Max vessels ({self.max_vessels}) reached"
            
        if current_berthing >= self.max_berthing_ops:
            return False, f"Max berthing ops ({self.max_berthing_ops}) reached"
            
        if current_loading >= self.max_loading_ops:
            return False, f"Max loading ops ({self.max_loading_ops}) reached"
            
        if current_unberthing >= self.max_unberthing_ops:
            return False, f"Max unberthing ops ({self.max_unberthing_ops}) reached"
            
        if self.max_total_cargo_mt and current_cargo_mt >= self.max_total_cargo_mt:
            return False, f"Max cargo ({self.max_total_cargo_mt}MT) reached"
            
        return True, None


@dataclass
class CargoSegregationRule:
    """Rules for cargo segregation at berth"""
    rule_id: str
    incompatible_pairs: List[Tuple[str, str]] = field(default_factory=list)
    min_separation_hours: float = 0.0
    requires_cleaning: Set[Tuple[str, str]] = field(default_factory=set)
    cleaning_hours: float = 2.0
    
    def check_compatibility(self, cargo_type_1: str, cargo_type_2: str) -> Tuple[bool, Optional[str]]:
        """Check if two cargo types can be at berth simultaneously"""
        for c1, c2 in self.incompatible_pairs:
            if (cargo_type_1 == c1 and cargo_type_2 == c2) or \
               (cargo_type_1 == c2 and cargo_type_2 == c1):
                return False, f"Incompatible cargo types: {cargo_type_1} and {cargo_type_2}"
        return True, None
    
    def get_transition_time(self, from_cargo: str, to_cargo: str) -> float:
        """Get required time between cargo types (including cleaning)"""
        base_time = self.min_separation_hours
        
        if (from_cargo, to_cargo) in self.requires_cleaning:
            base_time += self.cleaning_hours
        elif (to_cargo, from_cargo) in self.requires_cleaning:
            base_time += self.cleaning_hours
            
        return base_time


@dataclass
class PriorityConstraint:
    """Priority-based berth allocation constraint"""
    priority_levels: Dict[str, int] = field(default_factory=dict)  # vessel_class -> priority
    preemption_allowed: bool = False
    preemption_notice_hours: float = 24.0
    
    def get_priority(self, vessel_class: str, cargo_priority: int = 5) -> int:
        """Get combined priority score (lower is higher priority)"""
        vessel_priority = self.priority_levels.get(vessel_class, 5)
        return min(vessel_priority, cargo_priority)
    
    def can_preempt(self, new_priority: int, existing_priority: int, notice_hours: float) -> bool:
        """Check if new vessel can preempt existing"""
        if not self.preemption_allowed:
            return False
        if new_priority >= existing_priority:
            return False
        if notice_hours < self.preemption_notice_hours:
            return False
        return True


@dataclass
class ConstraintViolation:
    """Record of a constraint violation"""
    violation_type: ViolationType
    severity: ConstraintSeverity
    constraint_id: str
    vessel_id: Optional[str]
    berth_id: str
    timestamp: datetime
    description: str
    can_override: bool = False
    override_authority: Optional[str] = None


@dataclass
class BerthConstraintSet:
    """Complete set of constraints for a berth"""
    berth_id: str
    berth_name: str
    
    # Core constraints
    size_constraint: Optional[VesselSizeConstraint] = None
    time_windows: List[TimeWindowConstraint] = field(default_factory=list)
    concurrent_ops: Optional[ConcurrentOperationsConstraint] = None
    segregation_rules: Optional[CargoSegregationRule] = None
    priority_constraint: Optional[PriorityConstraint] = None
    
    # Allowed cargo types
    allowed_cargo_types: Set[str] = field(default_factory=set)
    prohibited_cargo_types: Set[str] = field(default_factory=set)
    
    # Allowed vessel classes
    allowed_vessel_classes: Set[str] = field(default_factory=set)
    prohibited_vessel_classes: Set[str] = field(default_factory=set)
    
    # Operational parameters
    max_daily_capacity_mt: Optional[float] = None
    seasonal_restrictions: List[Tuple[date, date, str]] = field(default_factory=list)
    
    def validate_vessel_size(self, loa: float, beam: float, draft: float) -> Tuple[bool, Optional[str]]:
        """Validate vessel size against constraints"""
        if self.size_constraint:
            return self.size_constraint.validate_vessel(loa, beam, draft)
        return True, None
    
    def validate_cargo_type(self, cargo_type: str) -> Tuple[bool, Optional[str]]:
        """Validate cargo type allowed at this berth"""
        if cargo_type in self.prohibited_cargo_types:
            return False, f"Cargo type {cargo_type} prohibited at this berth"
            
        if self.allowed_cargo_types and cargo_type not in self.allowed_cargo_types:
            return False, f"Cargo type {cargo_type} not in allowed list"
            
        return True, None
    
    def validate_vessel_class(self, vessel_class: str) -> Tuple[bool, Optional[str]]:
        """Validate vessel class allowed at this berth"""
        if vessel_class in self.prohibited_vessel_classes:
            return False, f"Vessel class {vessel_class} prohibited at this berth"
            
        if self.allowed_vessel_classes and vessel_class not in self.allowed_vessel_classes:
            return False, f"Vessel class {vessel_class} not in allowed list"
            
        return True, None
    
    def get_active_time_window(self, check_datetime: datetime) -> Optional[TimeWindowConstraint]:
        """Get active time window constraint for given datetime"""
        for window in self.time_windows:
            is_allowed, _ = window.is_operation_allowed(check_datetime, 'loading')
            if is_allowed:
                return window
        return None
    
    def is_seasonal_restriction_active(self, check_date: date) -> Tuple[bool, Optional[str]]:
        """Check if seasonal restriction applies"""
        for start, end, reason in self.seasonal_restrictions:
            if start <= check_date <= end:
                return True, reason
        return False, None


class BerthConstraintValidator:
    """Validates berth operations against constraints"""
    
    def __init__(self, constraint_sets: Dict[str, BerthConstraintSet]):
        """
        Initialize validator with constraint sets.
        
        Args:
            constraint_sets: Dictionary mapping berth_id to BerthConstraintSet
        """
        self.constraint_sets = constraint_sets
        self.violations: List[ConstraintViolation] = []
    
    def validate_berthing(
        self,
        berth_id: str,
        vessel_id: str,
        vessel_class: str,
        loa: float,
        beam: float,
        draft: float,
        cargo_type: str,
        berthing_time: datetime,
        priority: int = 5
    ) -> Tuple[bool, List[ConstraintViolation]]:
        """
        Validate a berthing operation against all constraints.
        
        Args:
            berth_id: Berth identifier
            vessel_id: Vessel identifier
            vessel_class: Vessel class
            loa: Length overall
            beam: Beam width
            draft: Draft depth
            cargo_type: Type of cargo
            berthing_time: Proposed berthing time
            priority: Operation priority
            
        Returns:
            Tuple of (is_valid, list of violations)
        """
        violations = []
        constraints = self.constraint_sets.get(berth_id)
        
        if not constraints:
            logger.warning(f"No constraints defined for berth {berth_id}")
            return True, []
        
        # Validate vessel size
        is_valid, msg = constraints.validate_vessel_size(loa, beam, draft)
        if not is_valid:
            violations.append(ConstraintViolation(
                violation_type=ViolationType.SIZE_EXCEEDED,
                severity=ConstraintSeverity.MANDATORY,
                constraint_id=f"{berth_id}_size",
                vessel_id=vessel_id,
                berth_id=berth_id,
                timestamp=berthing_time,
                description=msg
            ))
        
        # Validate cargo type
        is_valid, msg = constraints.validate_cargo_type(cargo_type)
        if not is_valid:
            violations.append(ConstraintViolation(
                violation_type=ViolationType.INCOMPATIBLE_CARGO,
                severity=ConstraintSeverity.MANDATORY,
                constraint_id=f"{berth_id}_cargo",
                vessel_id=vessel_id,
                berth_id=berth_id,
                timestamp=berthing_time,
                description=msg
            ))
        
        # Validate vessel class
        is_valid, msg = constraints.validate_vessel_class(vessel_class)
        if not is_valid:
            violations.append(ConstraintViolation(
                violation_type=ViolationType.INCOMPATIBLE_CARGO,
                severity=ConstraintSeverity.MANDATORY,
                constraint_id=f"{berth_id}_vessel_class",
                vessel_id=vessel_id,
                berth_id=berth_id,
                timestamp=berthing_time,
                description=msg
            ))
        
        # Check seasonal restrictions
        is_restricted, reason = constraints.is_seasonal_restriction_active(berthing_time.date())
        if is_restricted:
            violations.append(ConstraintViolation(
                violation_type=ViolationType.WEATHER_RESTRICTION,
                severity=ConstraintSeverity.MANDATORY,
                constraint_id=f"{berth_id}_seasonal",
                vessel_id=vessel_id,
                berth_id=berth_id,
                timestamp=berthing_time,
                description=f"Seasonal restriction: {reason}"
            ))
        
        # Check time windows
        window_valid = False
        window_msg = "No valid time window"
        for window in constraints.time_windows:
            is_valid, msg = window.is_operation_allowed(berthing_time, 'berthing')
            if is_valid:
                window_valid = True
                break
            window_msg = msg or window_msg
        
        if constraints.time_windows and not window_valid:
            violations.append(ConstraintViolation(
                violation_type=ViolationType.OUTSIDE_TIME_WINDOW,
                severity=ConstraintSeverity.MANDATORY,
                constraint_id=f"{berth_id}_time_window",
                vessel_id=vessel_id,
                berth_id=berth_id,
                timestamp=berthing_time,
                description=window_msg
            ))
        
        # Store violations
        self.violations.extend(violations)
        
        # Check if any mandatory violations
        mandatory_violations = [v for v in violations if v.severity == ConstraintSeverity.MANDATORY]
        
        return len(mandatory_violations) == 0, violations
    
    def validate_concurrent_operations(
        self,
        berth_id: str,
        current_vessels: int,
        current_berthing: int,
        current_loading: int,
        current_unberthing: int,
        current_cargo_mt: float,
        timestamp: datetime
    ) -> Tuple[bool, Optional[ConstraintViolation]]:
        """Validate concurrent operations at berth"""
        constraints = self.constraint_sets.get(berth_id)
        
        if not constraints or not constraints.concurrent_ops:
            return True, None
        
        is_valid, msg = constraints.concurrent_ops.validate_concurrent(
            current_vessels,
            current_berthing,
            current_loading,
            current_unberthing,
            current_cargo_mt
        )
        
        if not is_valid:
            violation = ConstraintViolation(
                violation_type=ViolationType.CAPACITY_EXCEEDED,
                severity=ConstraintSeverity.MANDATORY,
                constraint_id=f"{berth_id}_concurrent",
                vessel_id=None,
                berth_id=berth_id,
                timestamp=timestamp,
                description=msg
            )
            self.violations.append(violation)
            return False, violation
        
        return True, None
    
    def check_cargo_segregation(
        self,
        berth_id: str,
        cargo_type_1: str,
        cargo_type_2: str
    ) -> Tuple[bool, Optional[str]]:
        """Check if two cargo types can be at berth together"""
        constraints = self.constraint_sets.get(berth_id)
        
        if not constraints or not constraints.segregation_rules:
            return True, None
        
        return constraints.segregation_rules.check_compatibility(cargo_type_1, cargo_type_2)
    
    def get_cargo_transition_time(
        self,
        berth_id: str,
        from_cargo: str,
        to_cargo: str
    ) -> float:
        """Get required transition time between cargo types"""
        constraints = self.constraint_sets.get(berth_id)
        
        if not constraints or not constraints.segregation_rules:
            return 0.0
        
        return constraints.segregation_rules.get_transition_time(from_cargo, to_cargo)
    
    def get_violations_summary(self) -> Dict[str, int]:
        """Get summary of violations by type"""
        summary = {}
        for violation in self.violations:
            vtype = violation.violation_type.value
            summary[vtype] = summary.get(vtype, 0) + 1
        return summary
    
    def clear_violations(self):
        """Clear violation history"""
        self.violations = []
