# Calendar Events API Documentation

## Overview

The `/api/calendar/events` endpoint provides a unified view of all vessel and cargo events across the Olya, Balakovo, and DeepSea modules. It aggregates events from all three operational modules into a standardized format with comprehensive filtering capabilities.

## Endpoint

```
GET /api/calendar/events
```

## Features

- **Multi-Module Aggregation**: Combines events from Olya, Balakovo, and DeepSea modules
- **Standardized Format**: All events follow a consistent data structure
- **Flexible Filtering**: Filter by module, vessel, status, and date range
- **Rich Metadata**: Includes statistics and filter information
- **Performance Optimized**: Supports pagination with configurable limits

## Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `module` | string | No | `all` | Filter by module: `olya`, `balakovo`, `deepsea`, or `all` |
| `vessel` | string | No | - | Filter by vessel ID or name (partial match, case-insensitive) |
| `status` | string | No | - | Filter by status: `planned`, `in_progress`, `completed`, `cancelled` |
| `start_date` | ISO 8601 | No | - | Filter events starting after this date |
| `end_date` | ISO 8601 | No | - | Filter events ending before this date |
| `limit` | integer | No | `1000` | Maximum number of events to return (1-10000) |

## Response Format

### Success Response (200 OK)

```json
{
  "events": [
    {
      "id": "deepsea_V001_1",
      "module": "deepsea",
      "type": "Loading",
      "title": "OCEAN PIONEER - Loading",
      "description": "Loading of Wheat (55000 MT) at Novorossiysk",
      "vessel": {
        "id": "V001",
        "name": "OCEAN PIONEER",
        "class": "Panamax"
      },
      "from_port": "Novorossiysk",
      "to_port": "Novorossiysk",
      "location": "Novorossiysk",
      "cargo": "Wheat",
      "cargo_state": "laden",
      "quantity_mt": 55000,
      "start": "2025-01-15T08:00:00",
      "end": "2025-01-17T20:00:00",
      "duration_hours": 60.0,
      "distance_nm": 0,
      "speed_kn": 0,
      "status": "planned",
      "voyage_id": "V001",
      "route_id": "R001",
      "canal_id": null,
      "remarks": ""
    },
    {
      "id": "olya_BG001_1",
      "module": "olya",
      "type": "Loading",
      "title": "Barge-01 - Loading at BKO",
      "description": "Loading of SFO (1800 MT)",
      "vessel": {
        "id": "BG001",
        "name": "Barge-01",
        "type": "barge"
      },
      "location": "BKO",
      "cargo": "SFO",
      "quantity_mt": 1800,
      "start": "2025-01-15T06:00:00",
      "end": "2025-01-16T00:00:00",
      "duration_hours": 18.0,
      "status": "planned",
      "voyage_id": "BG001",
      "remarks": ""
    },
    {
      "id": "balakovo_SLOT001",
      "module": "balakovo",
      "type": "Loading",
      "title": "Barge-01 - Loading at B1",
      "description": "Loading of SFO (1800 MT) to OYA",
      "vessel": {
        "id": "BG001",
        "name": "Barge-01",
        "type": "barge"
      },
      "location": "Berth 1",
      "berth_id": "B1",
      "cargo": "SFO",
      "quantity_mt": 1800,
      "destination": "OYA",
      "start": "2025-01-15T06:00:00",
      "end": "2025-01-16T02:00:00",
      "eta": "2025-01-15T04:00:00",
      "loading_start": "2025-01-15T08:00:00",
      "loading_end": "2025-01-15T22:00:00",
      "duration_hours": 20.0,
      "waiting_hours": 2.0,
      "status": "planned",
      "cargo_id": "C001",
      "remarks": ""
    }
  ],
  "metadata": {
    "total": 145,
    "returned": 100,
    "filters": {
      "module": "all",
      "vessel": null,
      "status": null,
      "start_date": null,
      "end_date": null
    },
    "statistics": {
      "by_module": {
        "deepsea": 45,
        "olya": 62,
        "balakovo": 38
      },
      "by_status": {
        "planned": 89,
        "in_progress": 12,
        "completed": 44
      },
      "by_vessel": {
        "OCEAN PIONEER": 15,
        "Barge-01": 8,
        "Vessel-02": 12
      }
    }
  }
}
```

### Error Response (4xx/5xx)

```json
{
  "error": "Invalid module. Must be one of: olya, balakovo, deepsea, or \"all\"",
  "events": []
}
```

## Event Types

### DeepSea Module Events

- **Loading**: Cargo loading operations at ports
- **Discharge**: Cargo discharge operations at ports
- **Sea Transit**: Voyage between ports
- **Canal Transit**: Transit through canals (Suez, Panama, etc.)
- **Bunkering**: Fuel bunkering operations
- **Waiting**: Waiting time at ports or anchorages

**Additional Fields**:
- `from_port`: Departure port
- `to_port`: Destination port
- `cargo_state`: `laden` or `ballast`
- `distance_nm`: Distance in nautical miles
- `speed_kn`: Speed in knots
- `route_id`: Route identifier
- `canal_id`: Canal identifier (for canal transits)

### Olya Module Events

- **Loading**: Cargo loading at river ports
- **Discharge**: Cargo discharge operations
- **Transit**: River/sea transit between ports
- **Waiting**: Waiting for operations
- **Bunkering**: Fuel bunkering

**Additional Fields**:
- `voyage_id`: Voyage identifier
- `location`: Port location

### Balakovo Module Events

- **Loading**: Berth loading operations

**Additional Fields**:
- `berth_id`: Berth identifier
- `destination`: Cargo destination
- `eta`: Estimated time of arrival
- `loading_start`: Loading start time
- `loading_end`: Loading end time
- `waiting_hours`: Waiting time in hours
- `cargo_id`: Cargo plan identifier

## Event Status

| Status | Description |
|--------|-------------|
| `planned` | Event is scheduled but not yet started |
| `in_progress` | Event is currently ongoing |
| `completed` | Event has been completed |
| `cancelled` | Event has been cancelled (Balakovo only) |

Status is automatically determined based on event start/end times compared to current time.

## Usage Examples

### Get All Events

```bash
curl "http://localhost:5000/api/calendar/events"
```

### Filter by Module

```bash
# Get only DeepSea events
curl "http://localhost:5000/api/calendar/events?module=deepsea"

# Get only Olya events
curl "http://localhost:5000/api/calendar/events?module=olya"

# Get only Balakovo events
curl "http://localhost:5000/api/calendar/events?module=balakovo"
```

### Filter by Vessel

```bash
# Find all events for vessels containing "OCEAN"
curl "http://localhost:5000/api/calendar/events?vessel=OCEAN"

# Find all events for Barge-01
curl "http://localhost:5000/api/calendar/events?vessel=Barge-01"
```

### Filter by Status

```bash
# Get only planned events
curl "http://localhost:5000/api/calendar/events?status=planned"

# Get only in-progress events
curl "http://localhost:5000/api/calendar/events?status=in_progress"

# Get only completed events
curl "http://localhost:5000/api/calendar/events?status=completed"
```

### Filter by Date Range

```bash
# Get events for next 7 days
curl "http://localhost:5000/api/calendar/events?start_date=2025-01-15T00:00:00&end_date=2025-01-22T00:00:00"

# Get events for January 2025
curl "http://localhost:5000/api/calendar/events?start_date=2025-01-01T00:00:00&end_date=2025-01-31T23:59:59"
```

### Multiple Filters

```bash
# Get DeepSea planned events for next 30 days, limit to 50
curl "http://localhost:5000/api/calendar/events?module=deepsea&status=planned&start_date=2025-01-15T00:00:00&end_date=2025-02-15T00:00:00&limit=50"

# Get all events for OCEAN PIONEER
curl "http://localhost:5000/api/calendar/events?vessel=OCEAN%20PIONEER"
```

### JavaScript Example

```javascript
async function getCalendarEvents(filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/api/calendar/events?${params}`);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  return data;
}

// Usage
const events = await getCalendarEvents({
  module: 'deepsea',
  status: 'planned',
  limit: 100
});

console.log(`Found ${events.metadata.total} events`);
console.log(`Returned ${events.events.length} events`);
```

### Python Example

```python
import requests
from datetime import datetime, timedelta

def get_calendar_events(module=None, vessel=None, status=None, 
                        start_date=None, end_date=None, limit=1000):
    """Get calendar events with optional filters"""
    
    params = {}
    if module:
        params['module'] = module
    if vessel:
        params['vessel'] = vessel
    if status:
        params['status'] = status
    if start_date:
        params['start_date'] = start_date.isoformat()
    if end_date:
        params['end_date'] = end_date.isoformat()
    if limit:
        params['limit'] = limit
    
    response = requests.get(
        'http://localhost:5000/api/calendar/events',
        params=params
    )
    response.raise_for_status()
    return response.json()

# Usage
start = datetime.now()
end = start + timedelta(days=30)

data = get_calendar_events(
    module='deepsea',
    status='planned',
    start_date=start,
    end_date=end
)

print(f"Total events: {data['metadata']['total']}")
for event in data['events'][:5]:
    print(f"- {event['title']} ({event['start']} to {event['end']})")
```

## Integration with Frontend

### Calendar View Example

```javascript
// Fetch events for calendar display
async function loadCalendarMonth(year, month) {
  const startDate = new Date(year, month - 1, 1);
  const endDate = new Date(year, month, 0);
  
  const data = await getCalendarEvents({
    start_date: startDate.toISOString(),
    end_date: endDate.toISOString()
  });
  
  // Group events by module
  const eventsByModule = {};
  data.events.forEach(event => {
    if (!eventsByModule[event.module]) {
      eventsByModule[event.module] = [];
    }
    eventsByModule[event.module].push(event);
  });
  
  return eventsByModule;
}
```

### Gantt Chart Integration

```javascript
// Convert events to Gantt chart format
function convertToGanttFormat(events) {
  return events.map(event => ({
    id: event.id,
    name: event.title,
    start: new Date(event.start),
    end: new Date(event.end),
    progress: event.status === 'completed' ? 100 :
              event.status === 'in_progress' ? 50 : 0,
    dependencies: [],
    custom_class: `event-${event.module}`,
    vessel: event.vessel.name,
    type: event.type
  }));
}
```

## Performance Considerations

- **Caching**: Consider caching results on the client side for frequently accessed date ranges
- **Pagination**: Use the `limit` parameter to reduce payload size
- **Date Filtering**: Always use date filters for large datasets
- **Module Filtering**: Filter by module when only specific data is needed

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 500 | Internal Server Error - Check server logs |

## Common Error Messages

- `Invalid module. Must be one of: olya, balakovo, deepsea, or "all"`
- `Invalid status. Must be one of: planned, in_progress, completed, cancelled`
- `Invalid start_date format: ...`
- `Invalid end_date format: ...`
- `Limit must be between 1 and 10000`
- `Invalid limit parameter`

## Notes

- All datetime values are in ISO 8601 format
- Vessel name filtering is case-insensitive and supports partial matches
- Events are sorted by start time in ascending order
- The endpoint aggregates data from all three modules on each request
- Module-specific errors (e.g., missing data files) are logged but don't fail the entire request

## Related Endpoints

- [`GET /api/gantt-data`](./API_REFERENCE.md#gantt-data) - Get Gantt chart data from last calculation
- [`POST /api/calculate`](./API_REFERENCE.md#calculate) - Calculate schedules for modules
- [`GET /api/berths`](./API_REFERENCE.md#berths) - Get berth data and utilization
