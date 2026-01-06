# Year-Long Schedule Generator

## Overview

The `generate_year_schedule.py` script extends existing voyage plans to create a full year schedule by replicating voyages with appropriate time offsets based on vessel turnaround times.

## Installation

No additional dependencies required - uses standard Python libraries included with the project.

## Usage

### Basic Usage

Generate a year schedule from existing deep sea voyage plans:

```bash
python generate_year_schedule.py
```

This will:

- Read from `input/deepsea/voyage_plan.csv`
- Generate a year schedule starting from 2026-01-01
- Save to `input/deepsea/voyage_plan_year.csv`

### Custom Parameters

```bash
python generate_year_schedule.py <input_file> <output_file> <start_date>
```

Example:

```bash
python generate_year_schedule.py input/deepsea/voyage_plan.csv output/deepsea_2027.csv 2027-01-01
```

## How It Works

1. **Loads Base Voyages**: Reads existing voyage plans from CSV
2. **Calculates Turnaround Time**: Estimates vessel turn around based on laycan windows
   - Average laycan window calculated from all voyages
   - Turnaround time = 2x laycan window (includes voyage time + port time + positioning)
3. **Generates Cycles**: For each vessel:
   - Calculates how many voyage cycles fit in a year
   - Replicates voyages with appropriate date offsets
   - Creates unique voyage IDs (e.g., `VOY_Y2026_001`)
4. **Saves Output**: Exports year-long schedule to CSV

## Output

The script generates:

- **voyage_plan_year.csv**: Full year schedule with 100+ voyages
- Multiple voyages per vessel based on turnaround capacity
- Unique voyage IDs with year prefix

### Example Output Stats

```
Total voyages generated: 107
Vessels utilized: 6
Time span: 2026-01-01 to 2027-01-02

Voyages by vessel:
  DS_01: 20 voyages
  DS_02: 18 voyages
  DS_03: 17 voyages
  DS_04: 17 voyages
  DS_05: 18 voyages
  DS_06: 17 voyages
```

## Using with the Scheduler

After generating the year schedule, you can use it with the vessel scheduler:

### Option 1: Replace Current Plan

```bash
# Backup original
cp input/deepsea/voyage_plan.csv input/deepsea/voyage_plan_original.csv

# Use year plan
cp input/deepsea/voyage_plan_year.csv input/deepsea/voyage_plan.csv
```

### Option 2: Via API

Update `api_server.py` or `main_deepsea.py` to point to the year schedule file.

### Option 3: Via UI

Upload the `voyage_plan_year.csv` through the web interface upload feature.

## Customization

### Adjust Turnaround Time

Edit line 40 in `generate_year_schedule.py`:

```python
# Default: 2x laycan window
turnaround_days = avg_laycan_days * 2

# Faster turnaround:
turnaround_days = int(avg_laycan_days * 1.5)

# Slower turnaround (more buffer):
turnaround_days = int(avg_laycan_days * 3)
```

### Extend Beyond One Year

Change line 44:

```python
# Default: 365 days
year_end = year_start + timedelta(days=365)

# Two years:
year_end = year_start + timedelta(days=730)
```

## Limitations

- Assumes consistent cargo types and routes for each vessel throughout the year
- Does not account for seasonal variations or special events
- Uses simplified turnaround calculation
- Does not optimize voyages (just replicates existing patterns)

## Next Steps

After generating the year schedule:

1. **Review the generated voyages**: Check for reasonable spacing and vessel utilization
2. **Calculate the full schedule**: Run the deep sea calculator with the year plan
3. **Optimize if needed**: Use scenario management to create variations
4. **Export results**: Generate Gantt charts and Excel reports

## Troubleshooting

### "No voyages generated"

- Check that input file exists and has valid voyage data
- Ensure laycan dates are properly formatted (YYYY-MM-DD)

### Too few/many voyages

- Adjust turnaround time multiplier (see Customization section)
- Check vessel count in input file

### Date ranges don't match

- Verify start_date parameter format (YYYY-MM-DD)
- Ensure base voyage dates are valid

## See Also

- [Deep Sea Calculator Documentation](docs/DEEPSEA_CALCULATOR.md)
- [API Reference](docs/API_REFERENCE.md)
- [Scenario Management](docs/SCENARIO_MANAGEMENT.md)
