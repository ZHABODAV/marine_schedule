"""
Tests for Advanced Berth Constraints Module

Tests constraint validation, conflict detection, and integration with berth planning.
"""
import pytest
from datetime import datetime, date, time, timedelta
from modules.berth_constraints import (
    VesselSizeConstraint,
    TimeWindowConstraint,
    ConcurrentOperationsConstraint,
    CargoSegregationRule,
    PriorityConstraint,
    BerthConstraintSet,
    BerthConstraintValidator,
    ConstraintType,
    ConstraintSeverity,
    ViolationType
)


class TestVesselSizeConstraint:
    """Test vessel size constraint validation"""
    
    def test_vessel_within_limits(self):
        """Should accept vessel within size limits"""
        # Arrange
        constraint = VesselSizeConstraint(
            max_loa_m=180.0,
            max_beam_m=32.0,
            max_draft_m=10.0
        )
        
        # Act
        is_valid, msg = constraint.validate_vessel(loa=150.0, beam=28.0, draft=8.0)
        
        # Assert
        assert is_valid is True
        assert msg is None
    
    def test_vessel_exceeds_loa(self):
        """Should reject vessel exceeding LOA"""
        # Arrange
        constraint = VesselSizeConstraint(
            max_loa_m=180.0,
            max_beam_m=32.0,
            max_draft_m=10.0
        )
        
        # Act
        is_valid, msg = constraint.validate_vessel(loa=200.0, beam=28.0, draft=8.0)
        
        # Assert
        assert is_valid is False
        assert "LOA" in msg
        assert "200" in msg
    
    def test_vessel_with_allowed_overhang(self):
        """Should accept vessel with allowed overhang"""
        # Arrange
        constraint = VesselSizeConstraint(
            max_loa_m=180.0,
            max_beam_m=32.0,
            max_draft_m=10.0,
            allow_overhang=True,
            overhang_max_m=10.0
        )
        
        # Act
        is_valid, msg = constraint.validate_vessel(loa=185.0, beam=28.0, draft=8.0)
        
        # Assert
        assert is_valid is True
        assert msg is None
    
    def test_vessel_exceeds_overhang_limit(self):
        """Should reject vessel exceeding overhang limit"""
        # Arrange
        constraint = VesselSizeConstraint(
            max_loa_m=180.0,
            max_beam_m=32.0,
            max_draft_m=10.0,
            allow_overhang=True,
            overhang_max_m=10.0
        )
        
        # Act
        is_valid, msg = constraint.validate_vessel(loa=195.0, beam=28.0, draft=8.0)
        
        # Assert
        assert is_valid is False
        assert "LOA" in msg


class TestTimeWindowConstraint:
    """Test time window constraint validation"""
    
    def test_operation_within_time_window(self):
        """Should allow operation within time window"""
        # Arrange
        constraint = TimeWindowConstraint(
            window_id="day_shift",
            start_time=time(8, 0),
            end_time=time(18, 0),
            days_of_week={0, 1, 2, 3, 4}  # Monday-Friday
        )
        
        # Act - Wednesday at 10:00
        check_time = datetime(2025, 1, 15, 10, 0)  # Wednesday
        is_allowed, msg = constraint.is_operation_allowed(check_time, 'loading')
        
        # Assert
        assert is_allowed is True
        assert msg is None
    
    def test_operation_outside_time_window(self):
        """Should reject operation outside time window"""
        # Arrange
        constraint = TimeWindowConstraint(
            window_id="day_shift",
            start_time=time(8, 0),
            end_time=time(18, 0),
            days_of_week={0, 1, 2, 3, 4}
        )
        
        # Act - Wednesday at 20:00
        check_time = datetime(2025, 1, 15, 20, 0)
        is_allowed, msg = constraint.is_operation_allowed(check_time, 'loading')
        
        # Assert
        assert is_allowed is False
        assert "time window" in msg.lower()
    
    def test_operation_on_excluded_day(self):
        """Should reject operation on excluded day of week"""
        # Arrange
        constraint = TimeWindowConstraint(
            window_id="weekday_only",
            start_time=time(8, 0),
            end_time=time(18, 0),
            days_of_week={0, 1, 2, 3, 4}  # Monday-Friday only
        )
        
        # Act - Saturday at 10:00
        check_time = datetime(2025, 1, 18, 10, 0)  # Saturday
        is_allowed, msg = constraint.is_operation_allowed(check_time, 'loading')
        
        # Assert
        assert is_allowed is False
        assert "day" in msg.lower() or "saturday" in msg.lower()
    
    def test_overnight_window(self):
        """Should handle overnight time window correctly"""
        # Arrange
        constraint = TimeWindowConstraint(
            window_id="night_shift",
            start_time=time(22, 0),
            end_time=time(6, 0)
        )
        
        # Act - 23:00 (should be allowed)
        check_time = datetime(2025, 1, 15, 23, 0)
        is_allowed, _ = constraint.is_operation_allowed(check_time, 'loading')
        
        # Assert
        assert is_allowed is True
        
        # Act - 02:00 (should be allowed)
        check_time = datetime(2025, 1, 15, 2, 0)
        is_allowed, _ = constraint.is_operation_allowed(check_time, 'loading')
        
        # Assert
        assert is_allowed is True
        
        # Act - 12:00 (should be rejected)
        check_time = datetime(2025, 1, 15, 12, 0)
        is_allowed, _ = constraint.is_operation_allowed(check_time, 'loading')
        
        # Assert
        assert is_allowed is False


class TestConcurrentOperationsConstraint:
    """Test concurrent operations constraint validation"""
    
    def test_within_concurrent_limits(self):
        """Should allow operations within concurrent limits"""
        # Arrange
        constraint = ConcurrentOperationsConstraint(
            max_vessels=2,
            max_berthing_ops=1,
            max_loading_ops=2,
            max_unberthing_ops=1
        )
        
        # Act
        is_valid, msg = constraint.validate_concurrent(
            current_vessels=1,
            current_berthing=0,
            current_loading=1,
            current_unberthing=0,
            current_cargo_mt=5000.0
        )
        
        # Assert
        assert is_valid is True
        assert msg is None
    
    def test_exceeds_max_vessels(self):
        """Should reject when max vessels exceeded"""
        # Arrange
        constraint = ConcurrentOperationsConstraint(max_vessels=2)
        
        # Act
        is_valid, msg = constraint.validate_concurrent(
            current_vessels=2,
            current_berthing=0,
            current_loading=0,
            current_unberthing=0,
            current_cargo_mt=0.0
        )
        
        # Assert
        assert is_valid is False
        assert "vessels" in msg.lower()


class TestCargoSegregationRule:
    """Test cargo segregation rules"""
    
    def test_compatible_cargo_types(self):
        """Should allow compatible cargo types"""
        # Arrange
        rule = CargoSegregationRule(
            rule_id="basic_segregation",
            incompatible_pairs=[("SFO", "MEAL")]
        )
        
        # Act
        is_compatible, msg = rule.check_compatibility("SFO", "RPO")
        
        # Assert
        assert is_compatible is True
        assert msg is None
    
    def test_incompatible_cargo_types(self):
        """Should reject incompatible cargo types"""
        # Arrange
        rule = CargoSegregationRule(
            rule_id="basic_segregation",
            incompatible_pairs=[("SFO", "MEAL"), ("RPO", "PELLETS")]
        )
        
        # Act
        is_compatible, msg = rule.check_compatibility("SFO", "MEAL")
        
        # Assert
        assert is_compatible is False
        assert "incompatible" in msg.lower()
    
    def test_transition_time_with_cleaning(self):
        """Should calculate transition time including cleaning"""
        # Arrange
        rule = CargoSegregationRule(
            rule_id="cleaning_required",
            min_separation_hours=2.0,
            requires_cleaning={("SFO", "MEAL")},
            cleaning_hours=4.0
        )
        
        # Act
        transition_time = rule.get_transition_time("SFO", "MEAL")
        
        # Assert
        assert transition_time == 6.0  # 2h separation + 4h cleaning
    
    def test_transition_time_without_cleaning(self):
        """Should calculate transition time without cleaning"""
        # Arrange
        rule = CargoSegregationRule(
            rule_id="no_cleaning",
            min_separation_hours=2.0,
            requires_cleaning={("SFO", "MEAL")},
            cleaning_hours=4.0
        )
        
        # Act
        transition_time = rule.get_transition_time("SFO", "RPO")
        
        # Assert
        assert transition_time == 2.0  # Only separation time


class TestPriorityConstraint:
    """Test priority-based constraints"""
    
    def test_get_priority_with_vessel_class(self):
        """Should get priority based on vessel class"""
        # Arrange
        constraint = PriorityConstraint(
            priority_levels={"TANKER": 1, "BARGE": 3}
        )
        
        # Act
        priority = constraint.get_priority("TANKER", cargo_priority=5)
        
        # Assert
        assert priority == 1  # Vessel class priority
    
    def test_get_priority_with_cargo(self):
        """Should use cargo priority when vessel class unknown"""
        # Arrange
        constraint = PriorityConstraint(
            priority_levels={"TANKER": 1}
        )
        
        # Act
        priority = constraint.get_priority("UNKNOWN_CLASS", cargo_priority=2)
        
        # Assert
        assert priority == 2  # Cargo priority used
    
    def test_preemption_allowed(self):
        """Should allow preemption when conditions met"""
        # Arrange
        constraint = PriorityConstraint(
            preemption_allowed=True,
            preemption_notice_hours=24.0
        )
        
        # Act
        can_preempt = constraint.can_preempt(
            new_priority=1,
            existing_priority=3,
            notice_hours=48.0
        )
        
        # Assert
        assert can_preempt is True
    
    def test_preemption_insufficient_notice(self):
        """Should reject preemption with insufficient notice"""
        # Arrange
        constraint = PriorityConstraint(
            preemption_allowed=True,
            preemption_notice_hours=24.0
        )
        
        # Act
        can_preempt = constraint.can_preempt(
            new_priority=1,
            existing_priority=3,
            notice_hours=12.0
        )
        
        # Assert
        assert can_preempt is False


class TestBerthConstraintSet:
    """Test complete berth constraint set"""
    
    def test_validate_vessel_size(self):
        """Should validate vessel size through constraint set"""
        # Arrange
        constraint_set = BerthConstraintSet(
            berth_id="BERTH_01",
            berth_name="Test Berth",
            size_constraint=VesselSizeConstraint(
                max_loa_m=180.0,
                max_beam_m=32.0,
                max_draft_m=10.0
            )
        )
        
        # Act
        is_valid, msg = constraint_set.validate_vessel_size(150.0, 28.0, 8.0)
        
        # Assert
        assert is_valid is True
    
    def test_validate_cargo_type_allowed(self):
        """Should validate allowed cargo types"""
        # Arrange
        constraint_set = BerthConstraintSet(
            berth_id="BERTH_01",
            berth_name="Test Berth",
            allowed_cargo_types={"SFO", "RPO"}
        )
        
        # Act
        is_valid, msg = constraint_set.validate_cargo_type("SFO")
        
        # Assert
        assert is_valid is True
    
    def test_validate_cargo_type_prohibited(self):
        """Should reject prohibited cargo types"""
        # Arrange
        constraint_set = BerthConstraintSet(
            berth_id="BERTH_01",
            berth_name="Test Berth",
            prohibited_cargo_types={"MEAL"}
        )
        
        # Act
        is_valid, msg = constraint_set.validate_cargo_type("MEAL")
        
        # Assert
        assert is_valid is False
        assert "prohibited" in msg.lower()


class TestBerthConstraintValidator:
    """Test integrated constraint validation"""
    
    def test_validate_berthing_success(self):
        """Should validate successful berthing"""
        # Arrange
        constraint_set = BerthConstraintSet(
            berth_id="BERTH_01",
            berth_name="Test Berth",
            size_constraint=VesselSizeConstraint(
                max_loa_m=180.0,
                max_beam_m=32.0,
                max_draft_m=10.0
            ),
            allowed_cargo_types={"SFO", "RPO"},
            allowed_vessel_classes={"TANKER"}
        )
        
        validator = BerthConstraintValidator({"BERTH_01": constraint_set})
        
        # Act
        is_valid, violations = validator.validate_berthing(
            berth_id="BERTH_01",
            vessel_id="VESSEL_01",
            vessel_class="TANKER",
            loa=150.0,
            beam=28.0,
            draft=8.0,
            cargo_type="SFO",
            berthing_time=datetime(2025, 1, 15, 10, 0)
        )
        
        # Assert
        assert is_valid is True
        assert len(violations) == 0
    
    def test_validate_berthing_size_violation(self):
        """Should detect size constraint violation"""
        # Arrange
        constraint_set = BerthConstraintSet(
            berth_id="BERTH_01",
            berth_name="Test Berth",
            size_constraint=VesselSizeConstraint(
                max_loa_m=180.0,
                max_beam_m=32.0,
                max_draft_m=10.0
            )
        )
        
        validator = BerthConstraintValidator({"BERTH_01": constraint_set})
        
        # Act
        is_valid, violations = validator.validate_berthing(
            berth_id="BERTH_01",
            vessel_id="VESSEL_01",
            vessel_class="TANKER",
            loa=200.0,  # Exceeds limit
            beam=28.0,
            draft=8.0,
            cargo_type="SFO",
            berthing_time=datetime(2025, 1, 15, 10, 0)
        )
        
        # Assert
        assert is_valid is False
        assert len(violations) > 0
        assert violations[0].violation_type == ViolationType.SIZE_EXCEEDED
    
    def test_validate_berthing_cargo_violation(self):
        """Should detect cargo type violation"""
        # Arrange
        constraint_set = BerthConstraintSet(
            berth_id="BERTH_01",
            berth_name="Test Berth",
            allowed_cargo_types={"SFO", "RPO"}
        )
        
        validator = BerthConstraintValidator({"BERTH_01": constraint_set})
        
        # Act
        is_valid, violations = validator.validate_berthing(
            berth_id="BERTH_01",
            vessel_id="VESSEL_01",
            vessel_class="TANKER",
            loa=150.0,
            beam=28.0,
            draft=8.0,
            cargo_type="MEAL",  # Not allowed
            berthing_time=datetime(2025, 1, 15, 10, 0)
        )
        
        # Assert
        assert is_valid is False
        assert len(violations) > 0
        assert violations[0].violation_type == ViolationType.INCOMPATIBLE_CARGO
    
    def test_check_cargo_segregation(self):
        """Should check cargo segregation rules"""
        # Arrange
        segregation = CargoSegregationRule(
            rule_id="seg_01",
            incompatible_pairs=[("SFO", "MEAL")]
        )
        
        constraint_set = BerthConstraintSet(
            berth_id="BERTH_01",
            berth_name="Test Berth",
            segregation_rules=segregation
        )
        
        validator = BerthConstraintValidator({"BERTH_01": constraint_set})
        
        # Act
        is_compatible, msg = validator.check_cargo_segregation("BERTH_01", "SFO", "MEAL")
        
        # Assert
        assert is_compatible is False
        assert "incompatible" in msg.lower()
    
    def test_get_violations_summary(self):
        """Should generate violations summary"""
        # Arrange
        constraint_set = BerthConstraintSet(
            berth_id="BERTH_01",
            berth_name="Test Berth",
            size_constraint=VesselSizeConstraint(
                max_loa_m=100.0,
                max_beam_m=20.0,
                max_draft_m=5.0
            )
        )
        
        validator = BerthConstraintValidator({"BERTH_01": constraint_set})
        
        # Act - Generate some violations
        validator.validate_berthing(
            berth_id="BERTH_01",
            vessel_id="VESSEL_01",
            vessel_class="TANKER",
            loa=200.0,  # Exceeds
            beam=28.0,   # Exceeds
            draft=8.0,   # Exceeds
            cargo_type="SFO",
            berthing_time=datetime(2025, 1, 15, 10, 0)
        )
        
        summary = validator.get_violations_summary()
        
        # Assert
        assert "size_exceeded" in summary
        assert summary["size_exceeded"] > 0


class TestAdvancedScenarios:
    """Test complex real-world scenarios"""
    
    def test_complete_berth_with_all_constraints(self):
        """Should handle berth with all constraint types"""
        # Arrange
        constraint_set = BerthConstraintSet(
            berth_id="BERTH_COMPLEX",
            berth_name="Complex Berth",
            size_constraint=VesselSizeConstraint(
                max_loa_m=180.0,
                max_beam_m=32.0,
                max_draft_m=10.0
            ),
            time_windows=[
                TimeWindowConstraint(
                    window_id="day_operations",
                    start_time=time(6, 0),
                    end_time=time(22, 0),
                    days_of_week={0, 1, 2, 3, 4}
                )
            ],
            concurrent_ops=ConcurrentOperationsConstraint(
                max_vessels=1,
                max_loading_ops=1
            ),
            segregation_rules=CargoSegregationRule(
                rule_id="segregation",
                incompatible_pairs=[("SFO", "MEAL")],
                min_separation_hours=2.0
            ),
            allowed_cargo_types={"SFO", "RPO"},
            allowed_vessel_classes={"TANKER", "BARGE"}
        )
        
        validator = BerthConstraintValidator({"BERTH_COMPLEX": constraint_set})
        
        # Act - Valid berthing
        is_valid, violations = validator.validate_berthing(
            berth_id="BERTH_COMPLEX",
            vessel_id="VESSEL_01",
            vessel_class="TANKER",
            loa=150.0,
            beam=28.0,
            draft=8.0,
            cargo_type="SFO",
            berthing_time=datetime(2025, 1, 15, 10, 0)  # Wednesday 10:00
        )
        
        # Assert
        assert is_valid is True
        assert len(violations) == 0
