# API Reference

**Version:** 2.0.0  
**Last Updated:** January 2026  
**Base URL:** `http://localhost:5000`

## 1. Introduction

This document provides a complete reference for the Vessel Scheduler System REST API.

## 2. Authentication

All endpoints, with the exception of `/api/health` and `/api/auth/login`, require authentication via a Bearer token.

### 2.1 Login

**Endpoint**: `POST /api/auth/login`

**Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```

**Response (200 OK)**:
```json
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "username": "admin",
        "role": "Administrator"
    },
    "expires_in": 28800
}
```

### 2.2 Logout

**Endpoint**: `POST /api/auth/logout`  
**Headers**: `Authorization: Bearer {token}`

**Response (200 OK)**:
```json
{
    "success": true,
    "message": "Logged out successfully"
}
```

## 3. System Status

### 3.1 Health Check

**Endpoint**: `GET /api/health`  
**Authentication**: Not required

**Response (200 OK)**:
```json
{
    "status": "healthy",
    "version": "2.0.0",
    "services": {
        "database": "ok",
        "api": "ok"
    }
}
```

## 4. Vessel Management

### 4.1 Get All Vessels

**Endpoint**: `GET /api/vessels`  
**Headers**: `Authorization: Bearer {token}`  
**Query Parameters**:
*   `module` (optional): Filter by module (`deepsea`, `olya`, `balakovo`)
*   `status` (optional): Filter by status (`active`, `inactive`)

**Response (200 OK)**:
```json
{
    "vessels": [
        {
            "vessel_id": "V001",
            "vessel_name": "Atlantic Star",
            "dwt_mt": 35000,
            "status": "active"
        }
    ],
    "count": 1
}
```

### 4.2 Create Vessel

**Endpoint**: `POST /api/vessels`  
**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
    "vessel_id": "V002",
    "vessel_name": "Pacific Dawn",
    "type": "Dry Bulk",
    "dwt_mt": 75000,
    "speed_kts": 15.0,
    "module": "deepsea"
}
```

**Response (201 Created)**:
```json
{
    "success": true,
    "vessel_id": "V002",
    "message": "Vessel created successfully"
}
```

## 5. Cargo Management

### 5.1 Get All Cargo

**Endpoint**: `GET /api/cargo`  
**Headers**: `Authorization: Bearer {token}`

**Response (200 OK)**:
```json
{
    "cargo": [
        {
            "cargo_id": "C001",
            "commodity": "Grain",
            "quantity_mt": 50000,
            "load_port": "Houston",
            "disch_port": "Rotterdam",
            "status": "pending"
        }
    ]
}
```

### 5.2 Create Cargo

**Endpoint**: `POST /api/cargo`  
**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
    "cargo_id": "C002",
    "commodity": "Wheat",
    "quantity_mt": 60000,
    "load_port": "Buenos Aires",
    "disch_port": "Rotterdam",
    "laycan_start": "2025-02-01",
    "laycan_end": "2025-02-05"
}
```

## 6. Schedule & Planning

### 6.1 Generate Schedule

**Endpoint**: `POST /api/schedule/generate`  
**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
    "type": "deepsea",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "options": {
        "optimize_ballast": true
    }
}
```

**Response (200 OK)**:
```json
{
    "success": true,
    "schedule_id": "SCH001",
    "voyages": 15,
    "utilization_pct": 87.5
}
```

### 6.2 Get Schedule

**Endpoint**: `GET /api/schedule/{type}`  
**Path Parameters**: `type` (`deepsea`, `olya`, `balakovo`)

**Response (200 OK)**:
```json
{
    "schedule_type": "deepsea",
    "period": "2025-01",
    "voyages": []
}
```

### 6.3 Calculate Voyage

**Endpoint**: `POST /api/voyage/calculate`  
**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
    "vessel_id": "V001",
    "cargo_id": "C001",
    "route": ["Houston", "Rotterdam"]
}
```

**Response (200 OK)**:
```json
{
    "voyage_id": "calculated_001",
    "total_distance_nm": 4800,
    "total_duration_days": 18.5,
    "costs": {
        "total_usd": 452500
    }
}
```

## 7. Calendar Events

### 7.1 Get Calendar Events

**Endpoint**: `GET /api/calendar/events`  
**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:
*   `module`: Filter by module (`olya`, `balakovo`, `deepsea`, `all`). Default: `all`
*   `vessel`: Filter by vessel ID.
*   `start_date`: ISO 8601 date.
*   `end_date`: ISO 8601 date.

**Response (200 OK)**:
```json
{
    "events": [
        {
            "id": "deepsea_V001_1",
            "title": "OCEAN PIONEER - Loading",
            "start": "2025-01-15T08:00:00",
            "end": "2025-01-17T20:00:00",
            "type": "Loading"
        }
    ]
}
```

## 8. Reports and Export

### 8.1 Export Gantt Chart

**Endpoint**: `POST /api/export/gantt`  
**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
    "type": "deepsea",
    "month": 1,
    "year": 2025,
    "format": "xlsx"
}
```

**Response**: Binary Excel file.

### 8.2 Generate PDF Report

**Endpoint**: `POST /api/reports/pdf/vessel-schedule`  
**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
    "type": "deepsea",
    "month": 1,
    "year": 2025
}
```

**Response**: Binary PDF file.

## 9. Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request.

| Code | Description |
|------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server failure |

**Error Response Format**:
```json
{
    "error": "Error message description",
    "code": "ERROR_CODE",
    "timestamp": "2025-12-18T10:30:00Z"
}
```

## 10. Rate Limiting

To ensure system stability, the following rate limits apply:

*   **Anonymous requests**: 100 requests per hour
*   **Authenticated requests**: 1000 requests per hour
*   **File uploads**: 20 requests per hour

Rate limit status is provided in the response headers:
*   `X-RateLimit-Limit`
*   `X-RateLimit-Remaining`
*   `X-RateLimit-Reset`
