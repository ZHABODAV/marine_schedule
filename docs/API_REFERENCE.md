# API Reference

Complete REST API documentation for the Vessel Scheduler System.

**Version**: 2.0.0  
**Last Updated**: 2025-12-18  
**Base URL**: `http://localhost:5000`

---

## Table of Contents

- [Authentication](#authentication)
- [Health & System](#health--system)
- [Vessels Management](#vessels-management)
- [Cargo Management](#cargo-management)
- [Routes & Ports](#routes--ports)
- [Schedule & Planning](#schedule--planning)
- [**Calendar Events** (NEW)](#calendar-events)
- [Export Functions](#export-functions)
- [Bunker Optimization](#bunker-optimization)
- [Reports](#reports)
- [File Upload](#file-upload)
- [Statistics & Monitoring](#statistics--monitoring)
- [WebSocket Events](#websocket-events)
- [Error Codes](#error-codes)
- [Rate Limiting](#rate-limiting)

---

## Authentication

All endpoints (except `/api/health` and `/api/auth/login`) require authentication via Bearer token.

### Login

**Endpoint**: `POST /api/auth/login`

**Request**:

```json
{
    "username": "string",
    "password": "string"
}
```

**Response (200)**:

```json
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "username": "admin",
        "full_name": "Administrator",
        "role": "Administrator",
        "permissions": ["*"]
    },
    "expires_in": 28800
}
```

**Response (401)**:

```json
{
    "error": "Invalid credentials"
}
```

**Example**:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Logout

**Endpoint**: `POST /api/auth/logout`

**Headers**: `Authorization: Bearer {token}`

**Response (200)**:

```json
{
    "success": true,
    "message": "Logged out successfully"
}
```

### Get Current User

**Endpoint**: `GET /api/auth/me`

**Headers**: `Authorization: Bearer {token}`

**Response (200)**:

```json
{
    "username": "admin",
    "full_name": "Administrator",
    "email": "admin@example.com",
    "role": "Administrator",
    "permissions": ["*"],
    "department": "IT"
}
```

---

## Health & System

### Health Check

**Endpoint**: `GET /api/health`

**No authentication required**

**Response (200)**:

```json
{
    "status": "healthy",
    "version": "2.0.0",
    "timestamp": "2025-12-18T10:30:00Z",
    "services": {
        "database": "ok",
        "api": "ok",
        "websocket": "ok"
    }
}
```

---

## Vessels Management

### Get All Vessels

**Endpoint**: `GET /api/vessels`

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:

- `module` (optional): Filter by module (`deepsea`, `olya`, `balakovo`)
- `status` (optional): Filter by status (`active`, `inactive`, `maintenance`)
- `vessel_class` (optional): Filter by class

**Response (200)**:

```json
{
    "vessels": [
        {
            "vessel_id": "V001",
            "vessel_name": "Atlantic Star",
            "vessel_class": "Handysize",
            "dwt_mt": 35000,
            "speed_kts": 14,
            "status": "active",
            "module": "deepsea"
        }
    ],
    "count": 1
}
```

### Get Single Vessel

**Endpoint**: `GET /api/vessels/{vessel_id}`

**Headers**: `Authorization: Bearer {token}`

**Response (200)**:

```json
{
    "vessel_id": "V001",
    "vessel_name": "Atlantic Star",
    "vessel_class": "Handysize",
    "type": "Dry Bulk",
    "dwt_mt": 35000,
    "capacity_mt": 33000,
    "speed_kts": 14.0,
    "tc_daily_hire_usd": 15000,
    "contract_type": "Time Charter",
    "module": "deepsea",
    "status": "active"
}
```

**Response (404)**:

```json
{
    "error": "Vessel not found"
}
```

### Create Vessel

**Endpoint**: `POST /api/vessels`

**Headers**: `Authorization: Bearer {token}`

**Required Permission**: `create_vessels`

**Request**:

```json
{
    "vessel_id": "V002",
    "vessel_name": "Pacific Dawn",
    "vessel_class": "Panamax",
    "type": "Dry Bulk",
    "dwt_mt": 75000,
    "capacity_mt": 73000,
    "speed_kts": 15.0,
    "tc_daily_hire_usd": 25000,
    "contract_type": "Time Charter",
    "module": "deepsea"
}
```

**Response (201)**:

```json
{
    "success": true,
    "vessel_id": "V002",
    "message": "Vessel created successfully"
}
```

### Update Vessel

**Endpoint**: `PUT /api/vessels/{vessel_id}`

**Headers**: `Authorization: Bearer {token}`

**Required Permission**: `edit_vessels`

**Request**: (partial update allowed)

```json
{
    "speed_kts": 15.5,
    "status": "maintenance"
}
```

**Response (200)**:

```json
{
    "success": true,
    "message": "Vessel updated successfully"
}
```

### Delete Vessel

**Endpoint**: `DELETE /api/vessels/{vessel_id}`

**Headers**: `Authorization: Bearer {token}`

**Required Permission**: `delete_vessels`

**Response (200)**:

```json
{
    "success": true,
    "message": "Vessel deleted successfully"
}
```

---

## Cargo Management

### Get All Cargo

**Endpoint**: `GET /api/cargo`

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:

- `module` (optional): Filter by module
- `status` (optional): Filter by status (`pending`, `scheduled`, `completed`)
- `product` (optional): Filter by product type

**Response (200)**:

```json
{
    "cargo": [
        {
            "cargo_id": "C001",
            "commodity": "Grain",
            "quantity_mt": 50000,
            "load_port": "Houston",
            "disch_port": "Rotterdam",
            "laycan_start": "2025-01-15",
            "laycan_end": "2025-01-20",
            "status": "pending",
            "module": "deepsea"
        }
    ],
    "count": 1
}
```

### Create Cargo

**Endpoint**: `POST /api/cargo`

**Headers**: `Authorization: Bearer {token}`

**Required Permission**: `create_voyages`

**Request**:

```json
{
    "cargo_id": "C002",
    "commodity": "Wheat",
    "quantity_mt": 60000,
    "load_port": "Buenos Aires",
    "disch_port": "Rotterdam",
    "laycan_start": "2025-02-01",
    "laycan_end": "2025-02-05",
    "module": "deepsea"
}
```

**Response (201)**:

```json
{
    "success": true,
    "cargo_id": "C002",
    "message": "Cargo created successfully"
}
```

---

## Routes & Ports

### Get All Routes

**Endpoint**: `GET /api/routes`

**Headers**: `Authorization: Bearer {token}`

**Response (200)**:

```json
{
    "routes": [
        {
            "route_id": "R001",
            "from_port": "Houston",
            "to_port": "Rotterdam",
            "distance_nm": 4800,
            "typical_duration_days": 14.5,
            "canal_transit": false
        }
    ]
}
```

### Get All Ports

**Endpoint**: `GET /api/ports`

**Headers**: `Authorization: Bearer {token}`

**Response (200)**:

```json
{
    "ports": [
        {
            "port_id": "P001",
            "port_name": "Houston",
            "country": "USA",
            "basin": "Gulf of Mexico",
            "latitude": 29.7604,
            "longitude": -95.3698,
            "can_handle_liquid": true,
            "can_handle_dry": true,
            "avg_loading_rate_tph": 400,
            "avg_discharge_rate_tph": 500
        }
    ]
}
```

---

## Schedule & Planning

### Generate Schedule

**Endpoint**: `POST /api/schedule/generate`

**Headers**: `Authorization: Bearer {token}`

**Required Permission**: `create_schedules`

**Request**:

```json
{
    "type": "deepsea",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "options": {
        "optimize_ballast": true,
        "include_bunker_stops": true
    }
}
```

**Response (200)**:

```json
{
    "success": true,
    "schedule_id": "SCH001",
    "voyages": 15,
    "vessels_utilized": 8,
    "total_cargo_mt": 450000,
    "utilization_pct": 87.5,
    "message": "Schedule generated successfully"
}
```

### Get Schedule

**Endpoint**: `GET /api/schedule/{type}`

**Headers**: `Authorization: Bearer {token}`

**Path Parameters**:

- `type`: `deepsea`, `olya`, or `balakovo`

**Query Parameters**:

- `month` (optional): Month (1-12)
- `year` (optional): Year

**Response (200)**:

```json
{
    "schedule_type": "deepsea",
    "period": "2025-01",
    "voyages": [
        {
            "voyage_id": "V001",
            "vessel_id": "V001",
            "vessel_name": "Atlantic Star",
            "cargo_id": "C001",
            "legs": [
                {
                    "leg_type": "loading",
                    "port": "Houston",
                    "start_date": "2025-01-15",
                    "end_date": "2025-01-17",
                    "cargo_qty_mt": 50000
                },
                {
                    "leg_type": "sea_transit",
                    "from_port": "Houston",
                    "to_port": "Rotterdam",
                    "distance_nm": 4800,
                    "start_date": "2025-01-17",
                    "end_date": "2025-01-31",
                    "speed_kts": 14
                }
            ]
        }
    ]
}
```

### Calculate Voyage

**Endpoint**: `POST /api/voyage/calculate`

**Headers**: `Authorization: Bearer {token}`

**Request**:

```json
{
    "vessel_id": "V001",
    "cargo_id": "C001",
    "route": ["Houston", "Rotterdam"],
    "calculation_options": {
        "include_waiting_time": true,
        "weather_margin_pct": 10
    }
}
```

**Response (200)**:

```json
{
    "voyage_id": "calculated_001",
    "total_distance_nm": 4800,
    "total_duration_days": 18.5,
    "breakdown": {
        "loading_days": 2.0,
        "sea_transit_days": 14.5,
        "discharge_days": 1.5,
        "waiting_days": 0.5
    },
    "costs": {
        "tc_hire_usd": 277500,
        "bunker_usd": 150000,
        "port_fees_usd": 25000,
        "total_usd": 452500
    },
    "tce_usd_per_day": 15000
}
```

---

## Calendar Events

### Get Calendar Events

**NEW FEATURE**: Aggregate events from all modules (Olya, Balakovo, DeepSea) with comprehensive filtering.

**Endpoint**: `GET /api/calendar/events`

**Headers**: `Authorization: Bearer {token}` (optional depending on configuration)

**Query Parameters**:

- `module` (optional): Filter by module (`olya`, `balakovo`, `deepsea`, or `all`). Default: `all`
- `vessel` (optional): Filter by vessel ID or name (partial match, case-insensitive)
- `status` (optional): Filter by status (`planned`, `in_progress`, `completed`, `cancelled`)
- `start_date` (optional): Filter events starting after this date (ISO 8601 format)
- `end_date` (optional): Filter events ending before this date (ISO 8601 format)
- `limit` (optional): Maximum number of events to return (1-10000). Default: `1000`

**Response (200)**:

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
      "location": "Novorossiysk",
      "cargo": "Wheat",
      "quantity_mt": 55000,
      "start": "2025-01-15T08:00:00",
      "end": "2025-01-17T20:00:00",
      "duration_hours": 60.0,
      "status": "planned",
      "voyage_id": "V001"
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
      }
    }
  }
}
```

**Event Types by Module**:

- **DeepSea**: Loading, Discharge, Sea Transit, Canal Transit, Bunkering, Waiting
- **Olya**: Loading, Discharge, Transit, Waiting, Bunkering
- **Balakovo**: Loading

**Example Requests**:

```bash
# Get all events
curl "http://localhost:5000/api/calendar/events"

# Get only DeepSea events
curl "http://localhost:5000/api/calendar/events?module=deepsea"

# Get planned events for next 30 days
curl "http://localhost:5000/api/calendar/events?status=planned&start_date=2025-01-15T00:00:00&end_date=2025-02-15T00:00:00"

# Find all events for a specific vessel
curl "http://localhost:5000/api/calendar/events?vessel=OCEAN%20PIONEER"

# Multiple filters
curl "http://localhost:5000/api/calendar/events?module=deepsea&status=planned&limit=50"
```

**For detailed documentation**, see [**API_CALENDAR_EVENTS.md**](API_CALENDAR_EVENTS.md)

---

## Export Functions

### Export Gantt Chart

**Endpoint**: `POST /api/export/gantt`

**Headers**: `Authorization: Bearer {token}`

**Request**:

```json
{
    "type": "deepsea",
    "month": 1,
    "year": 2025,
    "format": "xlsx"
}
```

**Response (200)**:
Binary Excel file download

**Response Headers**:

```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="gantt_deepsea_2025_01.xlsx"
```

### Export Fleet Overview

**Endpoint**: `POST /api/export/fleet-overview`

**Headers**: `Authorization: Bearer {token}`

**Request**:

```json
{
    "module": "deepsea",
    "period": "2025-Q1"
}
```

**Response (200)**:
Binary Excel file download

### Export Voyage Summary

**Endpoint**: `POST /api/export/voyage-summary`

**Headers**: `Authorization: Bearer {token}`

**Request**:

```json
{
    "voyage_ids": ["V001", "V002", "V003"],
    "include_financials": true
}
```

**Response (200)**:
Binary Excel file download

---

## Bunker Optimization

### Optimize Bunker Plan

**Endpoint**: `POST /api/bunker/optimize`

**Headers**: `Authorization: Bearer {token}`

**Required Permission**: `edit_voyages`

**Request**:

```json
{
    "voyage_id": "V001",
    "vessel_id": "V001",
    "route_ports": ["SINGAPORE", "ROTTERDAM", "HOUSTON"],
    "distances_nm": [5000, 4800],
    "port_times_days": [2, 1],
    "fuel_type": "VLSFO",
    "current_fuel_mt": 1000,
    "allow_eco_speed": true
}
```

**Response (200)**:

```json
{
    "optimized_plan": {
        "total_cost_usd": 245000,
        "savings_usd": 35000,
        "bunker_stops": [
            {
                "port": "SINGAPORE",
                "fuel_type": "VLSFO",
                "quantity_mt": 850,
                "price_per_mt": 680,
                "cost_usd": 578000
            }
        ],
        "speed_optimization": {
            "recommended_speed_kts": 13.5,
            "fuel_savings_pct": 12.5
        }
    }
}
```

### Get Bunker Prices

**Endpoint**: `GET /api/bunker/prices`

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:

- `port` (optional): Filter by port
- `fuel_type` (optional): Filter by fuel type

**Response (200)**:

```json
{
    "prices": [
        {
            "port": "SINGAPORE",
            "fuel_type": "VLSFO",
            "price_per_mt": 680,
            "currency": "USD",
            "updated_at": "2025-12-18T10:00:00Z"
        },
        {
            "port": "ROTTERDAM",
            "fuel_type": "VLSFO",
            "price_per_mt": 720,
            "currency": "USD",
            "updated_at": "2025-12-18T10:00:00Z"
        }
    ]
}
```

### Get Market Analysis

**Endpoint**: `GET /api/bunker/market-analysis`

**Headers**: `Authorization: Bearer {token}`

**Response (200)**:

```json
{
    "market_summary": {
        "avg_vlsfo_price": 695,
        "avg_mgo_price": 890,
        "price_trend": "stable",
        "volatility": "low"
    },
    "recommendations": [
        "Consider bunkering in Singapore for cost savings",
        "VLSFO prices expected to remain stable next 7 days"
    ]
}
```

---

## Reports

### Generate Vessel Schedule PDF

**Endpoint**: `POST /api/reports/pdf/vessel-schedule`

**Headers**: `Authorization: Bearer {token}`

**Required Permission**: `view_schedules`

**Request**:

```json
{
    "type": "deepsea",
    "month": 1,
    "year": 2025
}
```

**Response (200)**:
Binary PDF file download

### Generate Fleet Overview PDF

**Endpoint**: `POST /api/reports/pdf/fleet-overview`

**Headers**: `Authorization: Bearer {token}`

**Request**:

```json
{
    "period": "2025-Q1",
    "include_financials": true
}
```

**Response (200)**:
Binary PDF file download

### Generate Berth Utilization PDF

**Endpoint**: `POST /api/reports/pdf/berth-utilization`

**Headers**: `Authorization: Bearer {token}`

**Request**:

```json
{
    "terminal": "balakovo",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
}
```

**Response (200)**:
Binary PDF file download

---

## File Upload

### Upload CSV File

**Endpoint**: `POST /api/upload/csv`

**Headers**:

- `Authorization: Bearer {token}`
- `Content-Type: multipart/form-data`

**Form Data**:

- `file`: CSV file
- `type`: `vessels`, `cargo`, `routes`, `ports`, etc.
- `module`: `deepsea`, `olya`, or `balakovo`

**Response (200)**:

```json
{
    "success": true,
    "records_imported": 25,
    "errors": [],
    "warnings": ["Column 'optional_field' not found, using default"]
}
```

**Example**:

```bash
curl -X POST http://localhost:5000/api/upload/csv \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@vessels.csv" \
  -F "type=vessels" \
  -F "module=deepsea"
```

### Upload Excel File

**Endpoint**: `POST /api/upload/excel`

**Headers**:

- `Authorization: Bearer {token}`
- `Content-Type: multipart/form-data`

**Form Data**:

- `file`: Excel file
- `sheet`: Sheet name (optional, defaults to first sheet)
- `type`: Data type

**Response (200)**:

```json
{
    "success": true,
    "sheets_processed": 1,
    "records_imported": 50
}
```

---

## Statistics & Monitoring

### Get Dashboard Statistics

**Endpoint**: `GET /api/dashboard/stats`

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:

- `module` (optional): Filter by module

**Response (200)**:

```json
{
    "vessels": {
        "total": 25,
        "active": 20,
        "in_maintenance": 3,
        "idle": 2
    },
    "cargo": {
        "pending": 15,
        "scheduled": 30,
        "completed": 85
    },
    "utilization": {
        "fleet_utilization_pct": 87.5,
        "berth_utilization_pct": 92.0
    },
    "financials": {
        "total_revenue_usd": 5000000,
        "total_costs_usd": 3500000,
        "profit_margin_pct": 30.0
    }
}
```

### Get Berth Utilization

**Endpoint**: `GET /api/berths/utilization`

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:

- `terminal`: Terminal name
- `days`: Number of days (default: 30)

**Response (200)**:

```json
{
    "berths": [
        {
            "berth_id": "BERTH_01",
            "berth_name": "Main Tanker Berth",
            "utilization_pct": 85.5,
            "vessels_served": 12,
            "cargo_handled_mt": 150000,
            "avg_turnaround_hours": 36.5
        }
    ],
    "overall_utilization_pct": 87.2
}
```

---

## WebSocket Events

WebSocket connection: `ws://localhost:5000`

### Client → Server Events

#### Join Schedule Room

```javascript
socket.emit('join_schedule', {
    schedule_id: 'SCH001'
});
```

#### Leave Schedule Room

```javascript
socket.emit('leave_schedule', {
    schedule_id: 'SCH001'
});
```

#### Update Schedule

```javascript
socket.emit('schedule_update', {
    schedule_id: 'SCH001',
    updates: {
        voyage_id: 'V001',
        changes: {...}
    }
});
```

### Server → Client Events

#### Connected

```javascript
socket.on('connected', (data) => {
    console.log(data.message); // "Connected to server"
});
```

#### Schedule Changed

```javascript
socket.on('schedule_changed', (data) => {
    /*
    data = {
        schedule_id: 'SCH001',
        updated_by: 'user123',
        updates: {...},
        timestamp: '2025-12-18T10:30:00Z'
    }
    */
});
```

#### User Joined

```javascript
socket.on('user_joined', (data) => {
    /*
    data = {
        schedule_id: 'SCH001',
        user: 'john_doe',
        timestamp: '2025-12-18T10:30:00Z'
    }
    */
});
```

#### User Left

```javascript
socket.on('user_left', (data) => {
    /*
    data = {
        schedule_id: 'SCH001',
        user: 'john_doe',
        timestamp: '2025-12-18T10:30:00Z'
    }
    */
});
```

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists or conflict detected |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {
        "field": "Additional error details"
    },
    "timestamp": "2025-12-18T10:30:00Z"
}
```

---

## Rate Limiting

- **Anonymous requests**: 100 requests per hour
- **Authenticated requests**: 1000 requests per hour
- **File uploads**: 20 requests per hour
- **Export operations**: 50 requests per hour

Rate limit headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1640001234
```

---

## Best Practices

1. **Authentication**: Always include Authorization header
2. **Error Handling**: Check response status codes
3. **Rate Limiting**: Respect rate limit headers
4. **Pagination**: Use pagination for large datasets
5. **Caching**: Cache responses where appropriate
6. **Timeouts**: Set reasonable request timeouts
7. **Retries**: Implement exponential backoff for retries

---

## Support

For API support:

- See [**Phase 2 Enhancements**](PHASE2_ENHANCEMENTS.md)
- Check [**Troubleshooting Guide**](../README.md#troubleshooting)
- Review API server logs in `logs/`

---

**Last Updated**: 2025-12-18  
**API Version**: 2.0.0  
**Maintained By**: Maritime Logistics API Team
