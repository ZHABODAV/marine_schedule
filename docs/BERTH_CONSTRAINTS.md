# Advanced Berth Constraints Integration

## Overview

Phase 1 of the Advanced Berth Constraints Integration provides sophisticated constraint management for berth planning operations. This system extends the basic berth capabilities with advanced validation rules for vessel compatibility, time windows, concurrent operations, cargo segregation, and priority-based allocation.

## Features

### 1. Vessel Size Constraints

Enhanced physical constraints with overhang support:

- Maximum/minimum LOA (Length Overall)
- Maximum/minimum beam width
- Maximum/minimum draft depth
- Optional overhang allowance
- Precise violation reporting

### 2. Time Window Constraints

Flexible operational time restrictions:

- Hour-based operation windows (e.g., 08:00-18:00)
- Day-of-week restrictions (e.g., weekdays only)
- Date range limitations
- Overnight window support (e.g., 22:00-06:00)
- Operation-specific rules (berthing, loading, unberthing)

### 3. Concurrent Operations Constraints

Control simultaneous berth activities:

- Maximum concurrent vessels
- Maximum concurrent berthing operations
- Maximum concurrent loading operations
- Maximum concurrent unberthing operations
- Total cargo capacity limits
- Mixed cargo type policies

### 4. Cargo Segregation Rules

Ensure safe cargo handling:

- Incompatible cargo pair definitions
- Minimum separation time between cargo types
- Cleaning requirement specifications
- Automatic transition time calculation

### 5. Priority-Based Allocation

Sophisticated priority management:

- Vessel class priority levels
- Cargo priority integration
- Preemption rules
- Notice period requirements

## Module Structure

```
modules/
├── berth_constraints.py      # Core constraint types and validator
├── balakovo_data.py          # Extended Berth model with constraints
└── balakovo_planner.py       # Integrated constraint validation

tests/
└── test_berth_constraints.py # Comprehensive test coverage (27 tests)
```

## Usage Examples

### Example 1: Basic Size Constraints

```python
from modules.berth_constraints import VesselSizeConstraint, BerthConstraintSet
from modules.balakovo_data import Berth

# Create size constraint
size_constraint = VesselSizeConstraint(
    max_loa_m=180.0,
    max_beam_m=32.0,
    max_draft_m=10.0,
    allow_overhang=True,
    overhang_max_m=10.0
)

# Create constraint set
constraint_set = BerthConstraintSet(
    berth_id="BERTH_01",
    berth_name="Main Tanker Berth",
    size_constraint=size_constraint
)

# Attach to berth
berth = Berth(
    berth_id="BERTH_01",
    berth_name="Main Tanker Berth",
    berth_type="liquid",
    max_loa_m=180.0,
    max_beam_m=32.0,
    max_draft_m=10.0,
    cargo_types={"SFO", "RPO"},
    load_rate_mt_day=15000.0,
    working_hours=24,
    constraint_set=constraint_set
)

# Validate vessel
can_handle = berth.can_handle_vessel(vessel)  # Uses advanced constraints
```

### Example 2: Time Window Restrictions

```python
from datetime import time
from modules.berth_constraints import TimeWindowConstraint

# Weekday day shift only
day_shift = TimeWindowConstraint(
    window_id="day_operations",
    start_time=time(8, 0),
    end_time=time(18, 0),
    days_of_week={0, 1, 2, 3, 4},  # Monday-Friday
    operations_allowed={'berthing', 'loading', 'unberthing'}
)

# Add to constraint set
constraint_set.time_windows = [day_shift]

# Check if operation allowed
is_allowed = berth.is_time_window_available(
    check_datetime=datetime(2025, 1, 15, 10, 0),
    operation='loading'
)
```

### Example 3: Cargo Segregation

```python
from modules.berth_constraints import CargoSegregationRule

# Define incompatible cargo pairs
segregation = CargoSegregationRule(
    rule_id="oil_meal_segregation",
    incompatible_pairs=[
        ("SFO", "MEAL"),
        ("RPO", "PELLETS")
    ],
    min_separation_hours=2.0,
    requires_cleaning={("SFO", "MEAL")},
    cleaning_hours=4.0
)

constraint_set.segregation_rules = segregation

# Check compatibility
incompatible = berth.get_cargo_incompatibilities("SFO")
# Returns: ["MEAL"]

# Get cleaning time
transition_time = berth.get_cleaning_time("SFO", "MEAL")
# Returns: 6.0 hours (2h separation + 4h cleaning)
```

### Example 4: Complete Berth Configuration

```python
from modules.berth_constraints import (
    VesselSizeConstraint,
    TimeWindowConstraint,
    ConcurrentOperationsConstraint,
    CargoSegregationRule,
    BerthConstraintSet
)
from datetime import time

# Comprehensive constraint set
constraint_set = BerthConstraintSet(
    berth_id="BERTH_COMPLEX",
    berth_name="Complex Operational Berth",
    
    # Size constraints with overhang
    size_constraint=VesselSizeConstraint(
        max_loa_m=180.0,
        max_beam_m=32.0,
        max_draft_m=10.0,
        allow_overhang=True,
        overhang_max_m=15.0
    ),
    
    # Multiple time windows
    time_windows=[
        TimeWindowConstraint(
            window_id="day_shift",
            start_time=time(6, 0),
            end_time=time(18, 0),
            days_of_week={0, 1, 2, 3, 4},
            operations_allowed={'berthing', 'loading', 'unberthing'}
        ),
        TimeWindowConstraint(
            window_id="night_emergency",
            start_time=time(18, 0),
            end_time=time(6, 0),
            operations_allowed={'emergency'}
        )
    ],
    
    # Concurrent operations limits
    concurrent_ops=ConcurrentOperationsConstraint(
        max_vessels=2,
        max_berthing_ops=1,
        max_loading_ops=2,
        max_unberthing_ops=1,
        max_total_cargo_mt=20000.0
    ),
    
    # Cargo segregation
    segregation_rules=CargoSegregationRule(
        rule_id="safety_segregation",
        incompatible_pairs=[("SFO", "MEAL"), ("RPO", "GRAIN")],
        min_separation_hours=2.0,
        requires_cleaning={("SFO", "MEAL")},
        cleaning_hours=4.0
    ),
    
    # Cargo type restrictions
    allowed_cargo_types={"SFO", "RPO", "CSO"},
    prohibited_cargo_types={"HAZMAT"},
    
    # Vessel class restrictions
    allowed_vessel_classes={"TANKER", "CHEMICAL_TANKER"},
    prohibited_vessel_classes={"BULK_CARRIER"}
)
```

### Example 5: Constraint Validation

```python
from modules.berth_constraints import BerthConstraintValidator
from datetime import datetime

# Create validator
validator = BerthConstraintValidator({
    "BERTH_01": constraint_set
})

# Validate berthing operation
is_valid, violations = validator.validate_berthing(
    berth_id="BERTH_01",
    vessel_id="VESSEL_123",
    vessel_class="TANKER",
    loa=175.0,
    beam=30.0,
    draft=9.0,
    cargo_type="SFO",
    berthing_time=datetime(2025, 1, 15, 10, 0),
    priority=1
)

if not is_valid:
    for violation in violations:
        print(f"Violation: {violation.description}")
        print(f"Type: {violation.violation_type.value}")
        print(f"Severity: {violation.severity.value}")

# Get violations summary
summary = validator.get_violations_summary()
print(f"Total violations by type: {summary}")
```

## Integration with Balakovo Planner

The constraints are automatically integrated into the berth planning process:

```python
from modules.balakovo_data import BalakovoData
from modules.balakovo_planner import BalakovoPlanner

# Load berth data with constraints
data = BalakovoData()

# Configure berths with constraints
berth = data.berths["BERTH_01"]
berth.constraint_set = constraint_set

# Run planner (constraints validated automatically)
planner = BalakovoPlanner(data)
result = planner.plan()

# Check for constraint violations in conflicts
for conflict in result.conflicts:
    if conflict['type'] == 'constraint_violation':
        print(f"Constraint violation: {conflict['description']}")
```

## Constraint Violation Handling

Violations are classified by type and severity:

### Violation Types

- `SIZE_EXCEEDED`: Vessel exceeds physical limits
- `INCOMPATIBLE_CARGO`: Cargo type not allowed or incompatible
- `OUTSIDE_TIME_WINDOW`: Operation outside allowed time
- `CAPACITY_EXCEEDED`: Concurrent capacity limits exceeded
- `SEGREGATION_CONFLICT`: Cargo segregation rules violated
- `PRIORITY_CONFLICT`: Priority rules not satisfied
- `WEATHER_RESTRICTION`: Weather/seasonal restrictions active
- `MAINTENANCE_PERIOD`: Berth in maintenance

### Severity Levels

- `MANDATORY`: Must be satisfied (blocking)
- `PREFERRED`: Should be satisfied if possible (warning)
- `ADVISORY`: Nice to have (informational)

## Advanced Features

### 1. Cargo Transition Time

The system automatically calculates required time between different cargo types:

```python
# Automatic transition time in planning
if berth.has_advanced_constraints and schedule.slots:
    last_slot = schedule.slots[-1]
    transition_time = berth.get_cleaning_time(
        last_slot.cargo_type, 
        cargo.cargo_type
    )
    # Adds cleaning time to scheduling
```

### 2. Seasonal Restrictions

```python
constraint_set.seasonal_restrictions = [
    (date(2025, 12, 1), date(2025, 3, 31), "Winter ice restrictions"),
    (date(2025, 5, 1), date(2025, 5, 10), "Annual maintenance")
]

# Automatically checked during planning
is_restricted, reason = constraint_set.is_seasonal_restriction_active(check_date)
```

### 3. Constraint Override

Some violations can be overridden with proper authority:

```python
violation = ConstraintViolation(
    violation_type=ViolationType.SIZE_EXCEEDED,
    severity=ConstraintSeverity.PREFERRED,  # Not mandatory
    can_override=True,
    override_authority="PORT_CAPTAIN"
)
```

## Testing

Comprehensive test suite with 27 tests covering:

- Individual constraint types
- Constraint sets and combinations
- Validator integration
- Real-world scenarios
- Edge cases

Run tests:

```bash
pytest tests/test_berth_constraints.py -v
```

## Performance Considerations

1. **Lazy Validation**: Constraints only evaluated when berth has `constraint_set` configured
2. **Fallback Logic**: Basic validation used if advanced constraints not available
3. **Efficient Checking**: Time window checks use binary operations on date/time ranges
4. **Caching**: Berth can cache computed transition times

## Best Practices

1. **Start Simple**: Begin with basic constraints, add complexity as needed
2. **Test Thoroughly**: Use test suite to verify constraint behavior
3. **Document Rules**: Clear descriptions in constraint definitions
4. **Monitor Violations**: Track violation patterns to optimize rules
5. **Review Regularly**: Update constraints based on operational experience

## Future Enhancements (Phase 2+)

- Dynamic constraint learning from historical data
- Machine learning-based priority optimization
- Real-time constraint updates via API
- Geographic/environmental constraint integration
- Multi-berth coordination constraints
- Cost optimization within constraints

## API Integration

The constraints system is designed to integrate with the REST API:

```python
# Example: Get berth constraints via API
GET /api/berths/{berth_id}/constraints

# Response
{
    "berth_id": "BERTH_01",
    "has_constraints": true,
    "size_limits": {
        "max_loa_m": 180.0,
        "max_beam_m": 32.0,
        "max_draft_m": 10.0
    },
    "time_windows": [...],
    "cargo_restrictions": {...}
}
```

## Troubleshooting

### Common Issues

**Issue**: Constraint violations not detected

- **Solution**: Ensure `constraint_set` is attached to berth
- **Check**: Validator initialization includes berth_id

**Issue**: Time window always fails

- **Solution**: Verify timezone consistency
- **Check**: Day of week calculation (Monday=0)

**Issue**: Cargo segregation not applied

- **Solution**: Ensure incompatible pairs defined correctly
- **Check**: Cargo type names match exactly (case-sensitive)

## Support and Documentation

- Module documentation: [`berth_constraints.py`](modules/berth_constraints.py)
- Test examples: [`test_berth_constraints.py`](tests/test_berth_constraints.py)
- Integration: [`balakovo_planner.py`](modules/balakovo_planner.py)
- Data structures: [`balakovo_data.py`](modules/balakovo_data.py)

## Conclusion

Phase 1 of the Advanced Berth Constraints Integration provides a solid foundation for sophisticated berth planning with comprehensive constraint validation. The system is backward-compatible (works without constraints), fully tested (27 test cases), and production-ready.
