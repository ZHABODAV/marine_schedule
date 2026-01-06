# Operational Calendar User Guide

## Overview

The **Operational Calendar** is a comprehensive web-based interface for visualizing and managing vessel schedules across all modules (Deep Sea, Olya, and Balakovo). It provides interactive calendar views, filtering capabilities, and export functionality for year-long vessel planning.

## Features

###  Multiple View Types
- **Month View**: Traditional calendar grid showing events by day
- **Timeline View**: Horizontal Gantt-style view showing vessel schedules
- **Year View**: 12-month overview with event indicators
- **Week View**: Detailed weekly schedule (coming soon)

###  Advanced Filtering
- Filter by module (Deep Sea, Olya, Balakovo)
- Filter by vessel
- Filter by status (Planned, In Progress, Completed, Delayed)
- Real-time search across all events

###  Statistics Dashboard
- Total voyages count
- Active vessels
- Total cargo (MT)
- Total costs (USD)
- Upcoming events list

###  Export Capabilities
- CSV export
- Excel export with multiple sheets
- Filtered data export

###  Visual Features
- Color-coded events by module
- Status indicators
- Interactive event details modal
- Responsive design for mobile and desktop

## Getting Started

### Prerequisites

1. **Backend API Running**
   ```bash
   python api_server.py
   # or
   python api_server_enhanced.py
   ```

2. **Data Available**
   - Deep Sea voyages calculated
   - Olya voyage configurations loaded
   - Balakovo data (if applicable)

### Launch the Calendar

1. **Open the Calendar Interface**
   ```bash
   # Navigate to the project directory
   cd c:/Users/Asus/Documents/project
   
   # Open in browser
   start operational_calendar.html
   ```

2. **Or via Web Server**
   If using a local web server:
   ```
   http://localhost:8000/operational_calendar.html
   ```

## User Interface Guide

### Header Section

**Navigation Controls:**
- **Today Button**: Jump to current date
- **Export Button**: Download calendar data
- **Refresh Button**: Reload data from API

### Control Panel

**View Selector:**
- Choose between Month, Timeline, Year, or Week views

**Filters:**
- **Module Filter**: Show events from specific modules
- **Vessel Filter**: Show events for specific vessels
- **Status Filter**: Filter by voyage status
- **Search**: Free-text search across all event data

### Main Calendar Area

#### Month View
- Grid layout showing days of the month
- Events displayed as colored bars
- Click on events to see details
- Today highlighted in blue
- Hover for quick preview

#### Timeline View
- Vessels listed vertically
- Time scale horizontally
- Events shown as bars across timeline
- Drag and scroll to navigate
- Click events for details

#### Year View
- 12 mini-months in grid layout
- Days with events highlighted
- Click month to navigate to month view
- Quick overview of annual schedule

### Sidebar

**Statistics Cards:**
- Quick metrics for filtered data
- Real-time updates based on filters

**Upcoming Events:**
- Next 10 upcoming voyages
- Sorted by start date
- Click to view details

**Legend:**
- Color coding explanation
- Module identification
- Status indicators

### Event Details Modal

Click any event to see:
- Voyage ID
- Module and vessel
- Start and end dates
- Route information
- Cargo quantity
- Cost breakdown
- Additional voyage details

**Actions:**
- Edit (future feature)
- Delete (future feature)
- Close

## API Integration

The calendar connects to the following API endpoints:

### Deep Sea Module
```
GET /api/deepsea/voyages/calculated
```
Returns calculated voyages with full details.

### Olya Module
```
GET /api/olya/voyages
```
Returns Olya voyage configurations.

### Balakovo Module
```
GET /api/balakovo/voyages
```
Returns Balakovo voyage plans (if available).

### Calendar Aggregation
The calendar automatically merges data from all modules into a unified view.

## Data Structure

### Event Object
```javascript
{
  id: "VOY_Y2026_001",
  title: "DS_01: Grain",
  module: "deepsea",
  vessel: "DS_01",
  start: "2026-01-05",
  end: "2026-01-25",
  status: "planned",
  cargo: 50000,
  cost: 125000,
  route: "Houston → Rotterdam",
  details: { /* additional voyage data */ }
}
```

### Status Types
- **planned**: Voyage scheduled for future
- **in-progress**: Voyage currently underway
- **completed**: Voyage finished
- **delayed**: Voyage behind schedule (future feature)

## Export Formats

### CSV Export
- Single file with all filtered events
- Headers include: ID, Title, Module, Vessel, Start, End, Status, Cargo, Cost, Route
- Download name: `calendar_export_YYYYMMDD.csv`

### Excel Export (API)
Using the Calendar API module:
```python
from modules.calendar_api import CalendarAPI

calendar = CalendarAPI(deepsea_data, olya_data, balakovo_data)
file_path = calendar.export_to_excel(
    start_date='2026-01-01',
    end_date='2026-12-31'
)
```

Multiple sheets:
- **All Events**: Complete event list
- **Statistics**: Aggregated metrics
- **Deep Sea**: Deep Sea events only
- **Olya**: Olya events only
- **Balakovo**: Balakovo events only

## Customization

### Changing Colors

Edit [`operational_calendar.css`](../operational_calendar.css):

```css
:root {
    --primary-color: #2c3e50;
    --accent-color: #3498db;
    --success-color: #2ecc71;
    --warning-color: #f39c12;
    --danger-color: #e74c3c;
}
```

### Module Colors

```css
.event-item.deepsea {
    background-color: #3498db; /* Blue */
}

.event-item.olya {
    background-color: #2ecc71; /* Green */
}

.event-item.balakovo {
    background-color: #e74c3c; /* Red */
}
```

### Adding Custom Filters

Edit [`js/modules/operational-calendar.js`](../js/modules/operational-calendar.js):

```javascript
// Add new filter in getFilteredEvents()
if (this.customFilter) {
    return events.filter(e => /* your condition */);
}
```

## Keyboard Shortcuts (Future Feature)

- `←` / `→`: Navigate previous/next period
- `T`: Go to today
- `E`: Export calendar
- `R`: Refresh data
- `Esc`: Close modal

## Performance Tips

### Large Datasets (1000+ Voyages)

1. **Use Filters**: Apply module/vessel filters to reduce rendered events
2. **Timeline View**: More efficient for large datasets than month view
3. **Date Range**: Use year start/end filters via API
4. **Pagination**: Consider implementing if needed

### Slow Loading

1. **Check API Response Time**: Ensure backend is responding quickly
2. **Network Tab**: Verify API calls complete successfully
3. **Console Errors**: Check browser console for JavaScript errors
4. **Data Caching**: Calendar caches data until refresh

## Troubleshooting

### No Events Showing

**Possible Causes:**
1. API server not running
2. No calculated voyages in backend
3. Filters too restrictive
4. Date range outside event dates

**Solutions:**
```bash
# 1. Start API server
python api_server.py

# 2. Generate schedules
python run_year_gantt.py

# 3. Check browser console for errors
# 4. Reset filters to "All"
```

### Events Not Loading

**Check API Connection:**
```javascript
// Open browser console
fetch('http://localhost:5000/api/deepsea/voyages/calculated')
  .then(r => r.json())
  .then(d => console.log(d));
```

**Verify API URL:**
Edit in [`js/modules/operational-calendar.js`](../js/modules/operational-calendar.js:18):
```javascript
this.apiBaseUrl = 'http://localhost:5000/api';
```

### Calendar Not Rendering

1. **Check File Paths**: Ensure CSS and JS files are correctly linked
2. **Browser Console**: Look for 404 errors
3. **JavaScript Errors**: Fix any syntax errors
4. **Browser Compatibility**: Use modern browser (Chrome, Firefox, Edge)

## Integration with Year Schedule

The calendar works seamlessly with year schedule generators:

```bash
# 1. Generate year schedule
python generate_year_schedule.py

# 2. Calculate voyages
python run_year_gantt.py

# 3. Start API server
python api_server.py

# 4. Open operational calendar
start operational_calendar.html
```

## Advanced Usage

### Programmatic Access

Use the Calendar API in Python:

```python
from modules.calendar_api import CalendarAPI
from modules.deepsea_loader import DeepSeaLoader
from modules.deepsea_calculator import DeepSeaCalculator

# Load data
loader = DeepSeaLoader(input_dir='input/deepsea')
data = loader.load()
calculator = DeepSeaCalculator(data)
data = calculator.calculate_all()

# Create calendar API
calendar = CalendarAPI(deepsea_data=data)

# Get all events
events = calendar.get_all_events()

# Get statistics
stats = calendar.get_statistics()

# Get upcoming events
upcoming = calendar.get_upcoming_events(days=30, limit=10)

# Export
calendar.export_to_excel('my_calendar.xlsx')
```

### Custom Event Handlers

Add custom logic in JavaScript:

```javascript
class CustomCalendar extends OperationalCalendar {
    showEventDetails(event) {
        // Custom event detail logic
        super.showEventDetails(event);
        
        // Add your custom code
        console.log('Event clicked:', event);
        this.trackAnalytics(event);
    }
}
```

## Future Enhancements

- [ ] Drag-and-drop event editing
- [ ] Recurring events
- [ ] Event conflicts detection
- [ ] Real-time updates via WebSocket
- [ ] Email notifications
- [ ] Print view
- [ ] Mobile app
- [ ] Multi-user collaboration
- [ ] Event attachments
- [ ] Comments and notes

## See Also

- [Year Schedule Generator](YEAR_SCHEDULE_GENERATOR.md)
- [Deep Sea Module](МОДУЛЬ_DEEPSEA.md)
- [Olya Module](МОДУЛЬ_OLYA.md)
- [Balakovo Module](МОДУЛЬ_BALAKOVO.md)
- [API Reference](API_REFERENCE.md)

## Support

For issues or feature requests:
1. Check this documentation
2. Review browser console for errors
3. Verify API connectivity
4. Check data availability

## Version History

- **v1.0** (2025-12-25): Initial release
  - Month, Timeline, and Year views
  - Multi-module support
  - Filtering and search
  - Export functionality
  - Statistics dashboard
