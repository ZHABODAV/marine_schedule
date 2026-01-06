# UI Components API Integration Guide

## Overview

This document describes how UI components are connected to the backend API endpoints in the Vessel Scheduler System.

**Last Updated**: 2025-12-29  
**Status**: Active Development

---

## Recent Updates

### Calendar Events API Integration 

**Date**: 2025-12-29

#### Changes Made:

1. **API Client Enhancement** ([`js/services/api-client.js`](../js/services/api-client.js))
   - Added `getCalendarEvents()` method to support the new unified Calendar Events API
   - Endpoint: `GET /api/calendar/events`
   - Supports comprehensive filtering by module, vessel, status, and date range

2. **Operational Calendar Module Update** ([`js/modules/operational-calendar.js`](../js/modules/operational-calendar.js))
   - Migrated from module-specific endpoints to unified Calendar Events API
   - Implemented `loadCalendarEvents()` method that:
     - Uses the API client when available
     - Falls back to direct fetch if API client is unavailable
     - Transforms API response to internal event format
     - Maintains backward compatibility with legacy endpoints
   - Added comprehensive event property mapping for all three modules (DeepSea, Olya, Balakovo)

---

## API Client Service

### Location
[`js/services/api-client.js`](../js/services/api-client.js)

### Usage

```javascript
// Initialize (done automatically)
// apiClient is available globally

// Using Calendar Events API
const events = await apiClient.getCalendarEvents({
    module: 'deepsea',
    status: 'planned',
    limit: 1000
});

if (events.success) {
    console.log(`Loaded ${events.data.events.length} events`);
    console.log(`Total available: ${events.data.metadata.total}`);
}
```

### Available Methods

#### Calendar Events
- **`getCalendarEvents(filters)`** - Get calendar events from all modules
  ```javascript
  await apiClient.getCalendarEvents({
      module: 'all',        // 'deepsea', 'olya', 'balakovo', or 'all'
      vessel: 'OCEAN',      // Partial vessel name/ID match
      status: 'planned',    // 'planned', 'in_progress', 'completed', 'cancelled'
      start_date: '2025-01-01T00:00:00',
      end_date: '2025-12-31T23:59:59',
      limit: 1000          // Max events to return (1-10000)
  });
  ```

#### Vessels
- `getVessels(filters)` - Get all vessels with optional filters
- `getVessel(vesselId)` - Get single vessel details
- `createVessel(vesselData)` - Create new vessel
- `updateVessel(vesselId, vesselData)` - Update vessel
- `deleteVessel(vesselId)` - Delete vessel

#### Cargo
- `getCargo(filters)` - Get all cargo with filters
- `createCargo(cargoData)` - Create new cargo
- `updateCargo(cargoId, cargoData)` - Update cargo
- `deleteCargo(cargoId)` - Delete cargo

#### Routes & Ports
- `getRoutes()` - Get all routes
- `createRoute(routeData)` - Create new route
- `getPorts()` - Get all ports

#### Schedule & Voyages
- `generateSchedule(scheduleConfig)` - Generate optimized schedule
- `getSchedule(type, filters)` - Get schedule by type
- `calculateVoyage(voyageData)` - Calculate single voyage

#### Exports
- `exportGantt(exportConfig)` - Export Gantt chart
- `exportFleetOverview(exportConfig)` - Export fleet overview
- `exportVoyageSummary(exportConfig)` - Export voyage summary

#### Bunker Optimization
- `optimizeBunker(bunkerConfig)` - Optimize bunker plan
- `getBunkerPrices(filters)` - Get current bunker prices
- `getBunkerMarketAnalysis()` - Get market analysis

#### Reports
- `generateVesselSchedulePDF(reportConfig)` - Generate vessel schedule PDF
- `generateFleetOverviewPDF(reportConfig)` - Generate fleet overview PDF
- `generateBerthUtilizationPDF(reportConfig)` - Generate berth utilization PDF

#### Statistics
- `getDashboardStats(filters)` - Get dashboard statistics
- `getBerthUtilization(filters)` - Get berth utilization data

#### Berth Constraints
- `createBerthConstraint(constraintData)` - Create berth constraint
- `getBerthConstraints(filters)` - Get berth constraints

---

## UI Component Integration Status

###  Fully Integrated Components

#### 1. Operational Calendar
**File**: [`js/modules/operational-calendar.js`](../js/modules/operational-calendar.js)

**API Endpoints Used**:
- `GET /api/calendar/events` - Primary data source
- Legacy fallback endpoints (when unified API unavailable):
  - `GET /api/deepsea/voyages/calculated`
  - `GET /api/olya/voyages`

**Features**:
- Multi-module event aggregation
- Real-time filtering by module, vessel, status
- Date range filtering
- Multiple view modes (month, timeline, year)
- Event details modal
- CSV export

**Code Example**:
```javascript
// Load events with filters
async loadCalendarEvents() {
    const filters = {
        module: this.selectedModule !== 'all' ? this.selectedModule : 'all',
        limit: 10000
    };

    let response;
    if (typeof apiClient !== 'undefined' && apiClient.getCalendarEvents) {
        response = await apiClient.getCalendarEvents(filters);
        if (!response.success) {
            throw new Error(response.error);
        }
        var data = response.data;
    } else {
        // Fallback to direct fetch
        const queryString = new URLSearchParams(filters).toString();
        const fetchResponse = await fetch(`${this.apiBaseUrl}/calendar/events${queryString ? '?' + queryString : ''}`);
        var data = await fetchResponse.json();
    }

    // Transform to internal format
    this.events = (data.events || []).map(event => ({
        id: event.id,
        title: event.title,
        module: event.module,
        vessel: event.vessel?.name || event.vessel?.id,
        start: new Date(event.start),
        end: new Date(event.end),
        status: event.status,
        // ... more properties
    }));
}
```

###  Partially Integrated Components

#### 2. Gantt Chart
**File**: [`js/modules/gantt-chart.js`](../js/modules/gantt-chart.js)

**Current Implementation**: Direct fetch calls
**Recommended**: Migrate to API client

**Current Code**:
```javascript
fetch('/api/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
});

fetch('/api/gantt-data')
    .then(response => response.json());
```

**Recommended Migration**:
```javascript
// Use API client
await apiClient.getCalendarEvents({
    module: 'deepsea',
    limit: 10000
});

// Or if custom gantt endpoint exists
await apiClient.request('GET', '/api/gantt-data');
```

#### 3. Schedule Generator
**File**: [`js/modules/schedule-generator.js`](../js/modules/schedule-generator.js)

**Current**: Direct fetch  
**Recommended**: Use `apiClient.generateSchedule()`

#### 4. Voyage Builder
**File**: [`js/modules/voyage-builder.js`](../js/modules/voyage-builder.js)

**Current**: Direct fetch to `/api/voyage-templates`  
**Recommended**: Add dedicated method to API client

#### 5. Trading Lanes
**File**: [`js/modules/trading-lanes.js`](../js/modules/trading-lanes.js)

**Current**: Direct fetch to `/api/voyage-templates`  
**Recommended**: Use centralized template management

#### 6. Financial Analysis
**File**: [`js/modules/financial-analysis.js`](../js/modules/financial-analysis.js)

**Integration**: Uses `apiClient.optimizeBunker()` 

#### 7. Exports Module
**File**: [`js/modules/exports.js`](../js/modules/exports.js)

**Current**: Direct fetch  
**Recommended**: Use `apiClient.exportGantt()`, `apiClient.exportFleetOverview()`

---

## Migration Guidelines

### Why Use the API Client?

1. **Centralized Error Handling**: Consistent error responses across all API calls
2. **Authentication Management**: Automatic token handling and refresh
3. **Request/Response Interceptors**: Add logging, analytics, or custom headers
4. **Validation**: Built-in data validation before sending requests
5. **Type Safety**: Better IDE support with JSDoc annotations
6. **Maintainability**: Single source of truth for API endpoints

### Migration Example

**Before** (Direct fetch):
```javascript
async loadData() {
    try {
        const response = await fetch('/api/vessels', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}
```

**After** (API Client):
```javascript
async loadData() {
    const result = await apiClient.getVessels({ module: 'deepsea' });
    
    if (!result.success) {
        throw new Error(result.error);
    }
    
    return result.data;
}
```

### Step-by-Step Migration

1. **Identify the endpoint** being used
2. **Check if method exists** in API client
3. **If not exists**, add new method to API client:
   ```javascript
   async getMyData(filters = {}) {
       const queryString = new URLSearchParams(filters).toString();
       const endpoint = `/api/my-endpoint${queryString ? '?' + queryString : ''}`;
       return this.request('GET', endpoint);
   }
   ```
4. **Update component** to use API client
5. **Test thoroughly**
6. **Remove old fetch code**

---

## Event Data Structure

### Calendar Event Format

The unified Calendar Events API returns events in this standardized format:

```javascript
{
    "id": "deepsea_V001_1",
    "module": "deepsea",      // "deepsea", "olya", "balakovo"
    "type": "Loading",         // Event type
    "title": "OCEAN PIONEER - Loading",
    "description": "Loading of Wheat (55000 MT) at Novorossiysk",
    
    // Vessel info
    "vessel": {
        "id": "V001",
        "name": "OCEAN PIONEER",
        "class": "Panamax"
    },
    
    // Location
    "location": "Novorossiysk",
    "from_port": "Novorossiysk",   // DeepSea only
    "to_port": "Rotterdam",        // DeepSea only
    
    // Cargo
    "cargo": "Wheat",
    "quantity_mt": 55000,
    "cargo_state": "laden",        // DeepSea: "laden" or "ballast"
    
    // Timing
    "start": "2025-01-15T08:00:00",
    "end": "2025-01-17T20:00:00",
    "duration_hours": 60.0,
    
    // Status
    "status": "planned",           // "planned", "in_progress", "completed", "cancelled"
    
    // References
    "voyage_id": "V001",
    "route_id": "R001",            // DeepSea only
    "berth_id": "B1",              // Balakovo only
    
    // Additional fields
    "distance_nm": 4800,           // DeepSea transit
    "speed_kn": 14.5,              // DeepSea transit
    "waiting_hours": 2.0,          // Balakovo
    "remarks": ""
}
```

### Event Types by Module

**DeepSea**:
- Loading
- Discharge
- Sea Transit
- Canal Transit
- Bunkering
- Waiting

**Olya**:
- Loading
- Discharge
- Transit
- Waiting
- Bunkering

**Balakovo**:
- Loading

---

## Error Handling

### API Client Response Format

All API client methods return a standardized response:

```javascript
{
    "success": true,           // or false
    "data": { ... },          // on success
    "error": "Error message", // on failure
    "details": { ... },       // additional error info
    "status": 200             // HTTP status code
}
```

### Best Practices

```javascript
async function fetchData() {
    const result = await apiClient.getCalendarEvents({ module: 'deepsea' });
    
    if (!result.success) {
        // Handle error
        console.error('API Error:', result.error);
        
        if (result.status === 401) {
            // Redirect to login
            window.location.href = '/login';
        } else if (result.status === 404) {
            // Show not found message
            showMessage('No events found');
        } else {
            // Show generic error
            showMessage('Failed to load data');
        }
        
        return;
    }
    
    // Use data
    const events = result.data.events;
    renderEvents(events);
}
```

---

## Testing Integration

### Manual Testing Checklist

For each integrated component:

- [ ] Component loads without errors
- [ ] API calls are made with correct parameters
- [ ] Success responses are handled correctly
- [ ] Error responses show appropriate messages
- [ ] Loading states are displayed
- [ ] Data is transformed correctly for display
- [ ] Filters work as expected
- [ ] Pagination works (if applicable)
- [ ] Export functions work
- [ ] Network errors are handled gracefully

### Browser Console Testing

```javascript
// Test API client availability
console.log('API Client:', typeof apiClient !== 'undefined');

// Test calendar events
apiClient.getCalendarEvents({ module: 'deepsea', limit: 10 })
    .then(result => {
        console.log('Success:', result.success);
        console.log('Events:', result.data?.events?.length);
        console.log('Total:', result.data?.metadata?.total);
    });

// Test with filters
apiClient.getCalendarEvents({
    module: 'olya',
    status: 'planned',
    start_date: '2025-01-01T00:00:00',
    end_date: '2025-12-31T23:59:59'
}).then(console.log);
```

---

## Performance Considerations

### 1. Caching
```javascript
class OptimizedCalendar {
    constructor() {
        this.eventCache = new Map();
        this.cacheExpiry = 5 * 60 * 1000; // 5 minutes
    }
    
    async loadEvents(filters) {
        const cacheKey = JSON.stringify(filters);
        const cached = this.eventCache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
            return cached.data;
        }
        
        const result = await apiClient.getCalendarEvents(filters);
        
        if (result.success) {
            this.eventCache.set(cacheKey, {
                data: result.data,
                timestamp: Date.now()
            });
        }
        
        return result.data;
    }
}
```

### 2. Pagination
```javascript
// Load events in batches
async loadEventsBatch(module, offset = 0, limit = 100) {
    return await apiClient.getCalendarEvents({
        module,
        limit,
        offset  // If API supports offset
    });
}
```

### 3. Debounced Search
```javascript
const debouncedSearch = debounce(async (searchTerm) => {
    const result = await apiClient.getCalendarEvents({
        vessel: searchTerm,
        limit: 50
    });
    updateResults(result.data);
}, 300);
```

---

## Future Enhancements

### Planned Integrations

1. **WebSocket Support** for real-time updates
2. **GraphQL Endpoint** for flexible data queries
3. **Batch Operations** for bulk updates
4. **Offline Mode** with IndexedDB caching
5. **Progressive Loading** for large datasets

### API Client Improvements

- [ ] Request queuing for rate limiting
- [ ] Automatic retry with exponential backoff
- [ ] Request cancellation support
- [ ] Upload progress tracking
- [ ] Download progress tracking
- [ ] Request deduplication

---

## Support & Troubleshooting

### Common Issues

**Issue**: `apiClient is not defined`  
**Solution**: Ensure [`api-client.js`](../js/services/api-client.js) is loaded before your module

**Issue**: CORS errors  
**Solution**: Check backend CORS configuration in [`api_server.py`](../api_server.py)

**Issue**: 401 Unauthorized  
**Solution**: Check authentication token in localStorage: `localStorage.getItem('auth_token')`

**Issue**: No events returned  
**Solution**: Check if backend modules have data loaded

### Debugging

```javascript
// Enable verbose logging
apiClient.addRequestInterceptor((config) => {
    console.log('Request:', config);
    return config;
});

apiClient.addResponseInterceptor(async (response) => {
    console.log('Response:', response.status, await response.clone().json());
    return response;
});
```

---

## Related Documentation

- [API Reference](./API_REFERENCE.md) - Complete API endpoint documentation
- [Calendar Events API](./API_CALENDAR_EVENTS.md) - Detailed calendar endpoint docs
- [JavaScript Modernization Plan](./JAVASCRIPT_MODERNIZATION_PLAN.md) - Code modernization roadmap
- [Testing Guide](./TESTING_GUIDE.md) - Testing procedures

---

**Maintained By**: Frontend Development Team  
**Contact**: For issues or questions, see project documentation
