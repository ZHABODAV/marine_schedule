# Operational Calendar - Quick Start Guide

##  Get Started in 3 Steps

### Step 1: Generate Year Schedule Data

```bash
# Generate Deep Sea year schedule
python generate_year_schedule.py

# Calculate all voyages and create Gantt charts
python run_year_gantt.py
```

**What this does:**
- Creates a full year of voyage plans (107+ voyages)
- Calculates all voyage details (costs, timing, routes)
- Generates monthly Gantt charts in Excel

**Output:**
- `input/deepsea/voyage_plan_year.csv`
- `output/deepsea/gantt_deepsea_*.xlsx`
- `output/deepsea/fleet_overview_*.xlsx`

### Step 2: Start the API Server

```bash
# Start the enhanced API server
python api_server_enhanced.py

# Or use the standard server
python api_server.py
```

**What this does:**
- Launches REST API on `http://localhost:5000`
- Loads all calculated voyage data
- Provides endpoints for calendar to fetch data

**Check it's running:**
- Open browser: `http://localhost:5000`
- You should see API documentation

### Step 3: Open the Operational Calendar

```bash
# Open in default browser
start operational_calendar.html

# Or navigate manually to:
# file:///c:/Users/Asus/Documents/project/operational_calendar.html
```

**What you'll see:**
- Interactive calendar interface
- All your scheduled voyages
- Statistics and upcoming events
- Multiple view options (Month, Timeline, Year)

##  Quick Reference

### Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│   Operational Calendar                 [Today] [Export] │
├─────────────────────────────────────────────────────────┤
│  View: [Month ▼]  Module: [All ▼]  Vessel: [All ▼]     │
├──────────────────────────────┬──────────────────────────┤
│                              │   Statistics           │
│    January 2026              │  100 Voyages             │
│  S  M  T  W  T  F  S        │  6 Vessels               │
│           1  2  3  4         │  500K MT                 │
│  5  6  7  8  9 10 11        │  $10M Cost               │
│     [Events here]            │                          │
│                              │   Upcoming             │
│                              │  • DS_01: Grain          │
│                              │  • DS_02: Coal           │
└──────────────────────────────┴──────────────────────────┘
```

### Controls

| Button | Action |
|--------|--------|
| **Today** | Jump to current date |
| **Previous** | Go to previous month/year |
| **Next** | Go to next month/year |
| **Export** | Download as CSV |
| **Refresh** | Reload data from API |

### Filters

| Filter | Options |
|--------|---------|
| **View** | Month, Timeline, Year |
| **Module** | All, Deep Sea, Olya, Balakovo |
| **Vessel** | All, DS_01, DS_02, etc. |
| **Status** | All, Planned, In Progress, Completed |
| **Search** | Free text search |

### Color Coding

| Color | Module |
|-------|--------|
|  Blue | Deep Sea voyages |
|  Green | Olya operations |
|  Red | Balakovo activities |
|  Orange | In-progress status |
|  Gray | Completed voyages |

##  Common Tasks

### View Specific Vessel's Schedule

1. Select vessel from **Vessel** dropdown
2. Calendar shows only that vessel's events
3. Click events for details

### Export Schedule

1. Apply desired filters
2. Click **Export** button
3. CSV downloads with filtered data
4. Open in Excel or other spreadsheet

### See Voyage Details

1. Click any event in calendar
2. Modal shows full details:
   - Voyage ID and route
   - Dates and duration
   - Cargo and costs
   - All calculated values
3. Click anywhere outside to close

### Check Upcoming Voyages

1. Look at **Upcoming Events** sidebar
2. Shows next 10 voyages
3. Click any to see details
4. Automatically updates as you navigate

### Compare Modules

1. Switch to **Timeline** view
2. Shows all vessels on one screen
3. See vessel utilization
4. Identify gaps in schedule

### Annual Overview

1. Switch to **Year** view
2. See all 12 months at once
3. Days with events highlighted
4. Click month to zoom in

##  Troubleshooting

### "No events showing"

**Solution:**
```bash
# Ensure API is running
python api_server.py

# Check if data exists
dir output\deepsea\

# Regenerate if needed
python run_year_gantt.py
```

### "Loading forever"

**Check:**
1. Is API server running? → Start it
2. Open browser console (F12) → Check for errors
3. Try `http://localhost:5000` → Should see API docs
4. Check firewall → Allow port 5000

### "Events in wrong dates"

**Verify:**
```bash
# Check year schedule file
type input\deepsea\voyage_plan_year.csv

# Look at laycan_start and laycan_end dates
# They should be in format: YYYY-MM-DD
```

##  Sample Workflow

### Planning a Year of Operations

```bash
# 1. Generate base schedule
python generate_year_schedule.py

# 2. Calculate all details
python run_year_gantt.py

# 3. Start API
python api_server.py

# 4. Open calendar
start operational_calendar.html

# 5. Review in Calendar
# - Check vessel utilization
# - Verify no conflicts
# - Export for stakeholders

# 6. Make adjustments if needed
# - Edit voyage_plan_year.csv
# - Re-run calculations
# - Refresh calendar
```

### Monthly Operations Review

1. **Start of Month:**
   - Open calendar in Month view
   - Check upcoming voyages
   - Export month's schedule

2. **During Month:**
   - Track in-progress voyages
   - Monitor upcoming events
   - Adjust as needed

3. **End of Month:**
   - Review completed voyages
   - Export actuals for reporting
   - Plan next month

##  Browser Compatibility

 **Supported:**
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

 **Not Supported:**
- Internet Explorer (use Edge)
- Chrome < 80
- Very old browsers

##  Mobile Usage

The calendar is responsive and works on mobile:

- Portrait: Shows simplified month view
- Landscape: Shows timeline view
- Tap events for details
- Swipe to navigate months

## 🆘 Getting Help

1. **Read Full Documentation:**
   - [`docs/OPERATIONAL_CALENDAR.md`](docs/OPERATIONAL_CALENDAR.md)

2. **Check Browser Console:**
   - Press F12
   - Look for red errors
   - Check Network tab for API calls

3. **Verify Data Pipeline:**
   ```bash
   # Is year schedule generated?
   dir input\deepsea\voyage_plan_year.csv
   
   # Are voyages calculated?
   dir output\deepsea\
   
   # Is API running?
   curl http://localhost:5000
   ```

4. **Review Related Docs:**
   - [Year Schedule Generator](docs/YEAR_SCHEDULE_GENERATOR.md)
   - [Deep Sea Module](docs/МОДУЛЬ_DEEPSEA.md)
   - [API Reference](docs/API_REFERENCE.md)

##  Next Steps

Once comfortable with basics:

1. **Customize Colors**: Edit `operational_calendar.css`
2. **Add Custom Filters**: Modify `js/modules/operational-calendar.js`
3. **Integrate with Reports**: Use Calendar API in Python
4. **Automate Workflows**: Schedule data generation and exports

##  Best Practices

### Data Updates
- Regenerate schedules regularly
- Calculate voyages after changes
- Keep API running during work sessions
- Refresh calendar after data updates

### Performance
- Filter data for large datasets
- Use Timeline view for many vessels
- Close other browser tabs if slow
- Check API response times

### Collaboration
- Export filtered views for teams
- Share screenshots of calendar
- Use consistent naming conventions
- Document schedule changes

---

**Ready to Start?** Run these three commands:

```bash
python run_year_gantt.py && python api_server.py
# Then open: operational_calendar.html
```

 **You're all set!** Enjoy your operational calendar!
