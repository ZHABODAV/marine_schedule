# Cargo Template API - Complete Documentation

## Overview

The Cargo Template API provides a complete CRUD interface for managing cargo templates with cost allocations. Templates allow users to save commonly used cargo configurations and reuse them with optional overrides.

**Version**: 2.0 Enhanced  
**Base URL**: `http://localhost:5000`  
**Authentication**: Required (Bearer Token)

---

## Features

 **CRUD Operations**: Create, read, update, and delete cargo templates  
 **Template Application**: Apply templates with custom overrides  
 **Default Templates**: Mark and retrieve default templates  
 **Cost Allocations**: Operational, overhead, and other costs  
 **Persistent Storage**: JSON-based file storage  
 **RBAC Integration**: Role-based access control  
 **Performance Profiling**: Automatic performance tracking

---

## API Endpoints

### Authentication

Before using cargo template endpoints, you must authenticate:

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

Response:
```json
{
  "token": "eyJhbGci...",
  "user": {...},
  "expires_at": "2025-12-29T18:00:00"
}
```

Use the returned token in all subsequent requests:
```
Authorization: Bearer eyJhbGci...
```

---

### Endpoint Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/cargo-templates` | Get all templates |  |
| GET | `/api/cargo-templates/{id}` | Get specific template |  |
| GET | `/api/cargo-templates/default` | Get default template |  |
| POST | `/api/cargo-templates` | Create new template |  (CREATE_VOYAGES) |
| PUT | `/api/cargo-templates/{id}` | Update template |  (CREATE_VOYAGES) |
| DELETE | `/api/cargo-templates/{id}` | Delete template |  (CREATE_VOYAGES) |
| POST | `/api/cargo-templates/{id}/apply` | Apply template |  (CREATE_VOYAGES) |

---

## Detailed Endpoint Documentation

### 1. Get All Templates

**Endpoint**: `GET /api/cargo-templates`

**Description**: Retrieves all cargo templates.

**Request**:
```bash
curl -X GET http://localhost:5000/api/cargo-templates \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response** (200 OK):
```json
{
  "templates": [
    {
      "id": "tpl_20251229103045_0",
      "name": "Iron Ore - Australia to China",
      "description": "Standard iron ore shipment",
      "commodity": "Iron Ore",
      "quantity": 75000,
      "loadPort": "Port Hedland",
      "dischPort": "Qingdao",
      "freightRate": 15.5,
      "operationalCost": 50000,
      "overheadCost": 10000,
      "otherCost": 5000,
      "isDefault": false,
      "createdAt": "2025-12-29T10:30:45.123456",
      "updatedAt": "2025-12-29T10:30:45.123456"
    }
  ],
  "count": 1
}
```

**Screenshot Ref**: `GET_ALL_TEMPLATES.png`

---

### 2. Get Template by ID

**Endpoint**: `GET /api/cargo-templates/{template_id}`

**Description**: Retrieves a specific cargo template by its ID.

**Parameters**:
- `template_id` (path): Template ID (string)

**Request**:
```bash
curl -X GET http://localhost:5000/api/cargo-templates/tpl_20251229103045_0 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response** (200 OK):
```json
{
  "id": "tpl_20251229103045_0",
  "name": "Iron Ore - Australia to China",
  "description": "Standard iron ore shipment",
  "commodity": "Iron Ore",
  "quantity": 75000,
  "loadPort": "Port Hedland",
  "dischPort": "Qingdao",
  "freightRate": 15.5,
  "operationalCost": 50000,
  "overheadCost": 10000,
  "otherCost": 5000,
  "isDefault": false,
  "createdAt": "2025-12-29T10:30:45.123456",
  "updatedAt": "2025-12-29T10:30:45.123456"
}
```

**Error Response** (404):
```json
{
  "error": "Template not found"
}
```

**Screenshot Ref**: `GET_TEMPLATE_BY_ID.png`

---

### 3. Get Default Template

**Endpoint**: `GET /api/cargo-templates/default`

**Description**: Retrieves the template marked as default (if any).

**Request**:
```bash
curl -X GET http://localhost:5000/api/cargo-templates/default \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response** (200 OK):
```json
{
  "id": "tpl_20251229103045_0",
  "name": "Default Cargo Template",
  "isDefault": true,
  ...
}
```

**Error Response** (404):
```json
{
  "error": "No default template found"
}
```

**Screenshot Ref**: `GET_DEFAULT_TEMPLATE.png`

---

### 4. Create Template

**Endpoint**: `POST /api/cargo-templates`

**Description**: Creates a new cargo template.

**Required Permission**: `CREATE_VOYAGES`

**Request Body**:
```json
{
  "name": "New Template Name",
  "description": "Template description (optional)",
  "commodity": "Iron Ore",
  "quantity": 75000,
  "loadPort": "Port Hedland",
  "dischPort": "Qingdao",
  "freightRate": 15.5,
  "operationalCost": 50000,
  "overheadCost": 10000,
  "otherCost": 5000,
  "isDefault": false
}
```

**Required Fields**:
- `name` (string): Template name
- `commodity` (string): Cargo commodity

**Optional Fields**:
- `description` (string): Template description
- `quantity` (number): Cargo quantity in MT
- `loadPort` (string): Loading port
- `dischPort` (string): Discharge port
- `freightRate` (number): Freight rate per MT
- `operationalCost` (number): Operational cost
- `overheadCost` (number): Overhead cost
- `otherCost` (number): Other costs
- `isDefault` (boolean): Mark as default template

**Request**:
```bash
curl -X POST http://localhost:5000/api/cargo-templates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Coal - Newcastle to Singapore",
    "commodity": "Coal",
    "quantity": 60000,
    "loadPort": "Newcastle",
    "dischPort": "Singapore",
    "freightRate": 18.0
  }'
```

**Response** (201 Created):
```json
{
  "id": "tpl_20251229120000_1",
  "name": "Coal - Newcastle to Singapore",
  "description": "",
  "commodity": "Coal",
  "quantity": 60000,
  "loadPort": "Newcastle",
  "dischPort": "Singapore",
  "freightRate": 18.0,
  "operationalCost": 0,
  "overheadCost": 0,
  "otherCost": 0,
  "isDefault": false,
  "createdAt": "2025-12-29T12:00:00.000000",
  "updatedAt": "2025-12-29T12:00:00.000000"
}
```

**Error Response** (400):
```json
{
  "error": "Missing required fields: name, commodity"
}
```

**Screenshot Ref**: `CREATE_TEMPLATE.png`

---

### 5. Update Template

**Endpoint**: `PUT /api/cargo-templates/{template_id}`

**Description**: Updates an existing cargo template.

**Required Permission**: `CREATE_VOYAGES`

**Parameters**:
- `template_id` (path): Template ID to update

**Request Body** (partial update - only include fields to change):
```json
{
  "name": "Updated Template Name",
  "quantity": 80000,
  "freightRate": 16.5
}
```

**Request**:
```bash
curl -X PUT http://localhost:5000/api/cargo-templates/tpl_20251229120000_1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Coal Template",
    "quantity": 65000
  }'
```

**Response** (200 OK):
```json
{
  "id": "tpl_20251229120000_1",
  "name": "Updated Coal Template",
  "commodity": "Coal",
  "quantity": 65000,
  "loadPort": "Newcastle",
  "dischPort": "Singapore",
  "freightRate": 18.0,
  ...
  "updatedAt": "2025-12-29T12:15:00.000000"
}
```

**Error Response** (404):
```json
{
  "error": "Template not found"
}
```

**Screenshot Ref**: `UPDATE_TEMPLATE.png`

---

### 6. Delete Template

**Endpoint**: `DELETE /api/cargo-templates/{template_id}`

**Description**: Deletes a cargo template.

**Required Permission**: `CREATE_VOYAGES`

**Parameters**:
- `template_id` (path): Template ID to delete

**Request**:
```bash
curl -X DELETE http://localhost:5000/api/cargo-templates/tpl_20251229120000_1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response** (200 OK):
```json
{
  "message": "Template deleted successfully"
}
```

**Error Response** (404):
```json
{
  "error": "Template not found"
}
```

**Screenshot Ref**: `DELETE_TEMPLATE.png`

---

### 7. Apply Template

**Endpoint**: `POST /api/cargo-templates/{template_id}/apply`

**Description**: Applies a template to generate cargo commitment data. Optionally override template values.

**Required Permission**: `CREATE_VOYAGES`

**Parameters**:
- `template_id` (path): Template ID to apply

**Request Body** (optional overrides):
```json
{
  "quantity": 70000,
  "loadPort": "Alternative Port"
}
```

**Request**:
```bash
curl -X POST http://localhost:5000/api/cargo-templates/tpl_20251229103045_0/apply \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 70000,
    "dischPort": "Shanghai"
  }'
```

**Response** (200 OK):
```json
{
  "commodity": "Iron Ore",
  "quantity": 70000,
  "loadPort": "Port Hedland",
  "dischPort": "Shanghai",
  "freightRate": 15.5,
  "operationalCost": 50000,
  "overheadCost": 10000,
  "otherCost": 5000
}
```

**Note**: The response contains the merged data (template values with overrides applied).

**Error Response** (404):
```json
{
  "error": "Template not found"
}
```

**Screenshot Ref**: `APPLY_TEMPLATE.png`

---

## Data Model

### Template Object

```typescript
interface CargoTemplate {
  id: string;                    // Auto-generated, format: tpl_YYYYMMDDHHMMSS_N
  name: string;                  // Template name
  description?: string;          // Optional description
  commodity: string;             // Cargo commodity
  quantity?: number;             // Cargo quantity in MT
  loadPort?: string;             // Loading port name
  dischPort?: string;            // Discharge port name
  freightRate?: number;          // Freight rate per MT (USD)
  operationalCost?: number;      // Operational cost (USD)
  overheadCost?: number;         // Overhead cost (USD)
  otherCost?: number;            // Other costs (USD)
  isDefault: boolean;            // Default template flag
  createdAt: string;             // ISO 8601 timestamp
  updatedAt: string;             // ISO 8601 timestamp
}
```

---

## Usage Examples

### Example 1: Complete Workflow

```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'admin'})
});
const {token} = await loginResponse.json();

// 2 Create a template
const createResponse = await fetch('http://localhost:5000/api/cargo-templates', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Iron Ore Route',
    commodity: 'Iron Ore',
    quantity: 75000,
    loadPort: 'Port Hedland',
    dischPort: 'Qingdao',
    freightRate: 15.5,
    isDefault: true
  })
});
const template = await createResponse.json();

// 3. Apply template with overrides
const applyResponse = await fetch(
  `http://localhost:5000/api/cargo-templates/${template.id}/apply`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      quantity: 80000  // Override quantity
    })
  }
);
const cargoData = await applyResponse.json();
console.log(cargoData);
```

### Example 2: Get and Use Default Template

```python
import requests

# Login
response = requests.post('http://localhost:5000/api/auth/login',
                        json={'username': 'admin', 'password': 'admin'})
token = response.json()['token']

headers = {'Authorization': f'Bearer {token}'}

# Get default template
response = requests.get('http://localhost:5000/api/cargo-templates/default',
                       headers=headers)
default_template = response.json()

# Apply with custom values
response = requests.post(
    f"http://localhost:5000/api/cargo-templates/{default_template['id']}/apply",
    headers={**headers, 'Content-Type': 'application/json'},
    json={'quantity': 65000, 'dischPort': 'Shanghai'}
)
cargo = response.json()
print(f"Cargo: {cargo['quantity']} MT of {cargo['commodity']}")
```

---

## Testing

### Integration Tests

Run the comprehensive integration test suite:

```bash
pytest tests/test_cargo_templates_integration.py -v
```

**Test Coverage**:
-  Template creation with validation
-  Template retrieval (all, by ID, default)
-  Template updates
-  Template deletion
-  Template application with overrides
-  Manager class unit tests
-  Default template behavior

### User Acceptance Tests

Run automated UAT:

```bash
python tests/run_cargo_template_uat.py
```

This will execute all UAT scenarios and generate a test report.

Manual UAT guide: [`CARGO_TEMPLATE_UAT.md`](./CARGO_TEMPLATE_UAT.md)

---

## Error Handling

The API returns standard HTTP status codes:

| Status Code | Meaning |
|------------|---------|
| 200 | Success |
| 201 | Created successfully |
| 400 | Bad request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found |
| 500 | Server error |

Error responses include a descriptive message:

```json
{
  "error": "Missing required fields: name, commodity"
}
```

---

## Performance

All endpoints are automatically profiled using the `@profile_performance` decorator.

Performance metrics are logged to the server console and can be viewed in monitoring dashboards.

**Expected Response Times**:
- GET operations: < 50ms
- POST/PUT operations: < 100ms
- DELETE operations: < 50ms

---

## Security

### Authentication
All endpoints require Bearer token authentication (except login).

### Authorization
Modifying endpoints require `CREATE_VOYAGES` permission.

### Data Validation
- Required fields are validated
- Input sanitization prevents injection attacks
- File path validation prevents directory traversal

### Audit Logging
All template operations are logged to audit trail with:
- User ID and username
- Action performed
- Timestamp
- Resource ID
- Success/failure status

---

## Storage

Templates are stored in `data/cargo_templates.json`.

**Storage Format**:
```json
{
  "tpl_20251229103045_0": {
    "id": "tpl_20251229103045_0",
    "name": "Iron Ore Template",
    ...
  }
}
```

**Backup**: Regularly backup this file to prevent data loss.

---

## Screenshots

### API Testing with Postman

**Location**: `docs/screenshots/cargo-templates/`

1. **`GET_ALL_TEMPLATES.png`**: Screenshot showing GET request to retrieve all templates
2. **`CREATE_TEMPLATE.png`**: Screenshot showing POST request to create a template
3. **`GET_TEMPLATE_BY_ID.png`**: Screenshot showing GET request for specific template
4. **`UPDATE_TEMPLATE.png`**: Screenshot showing PUT request to update a template
5. **`DELETE_TEMPLATE.png`**: Screenshot showing DELETE request
6. **`APPLY_TEMPLATE.png`**: Screenshot showing template application with overrides
7. **`GET_DEFAULT_TEMPLATE.png`**: Screenshot showing default template retrieval
8. **`VALIDATION_ERROR.png`**: Screenshot showing validation error response

*Note: Screenshots can be generated using Postman or any REST client during UAT.*

---

## Support

For issues or questions:
- Review the [API Reference](./API_REFERENCE.md)
- Check the [Testing Guide](./TESTING_GUIDE.md)
- Review UAT documentation: [CARGO_TEMPLATE_UAT.md](./CARGO_TEMPLATE_UAT.md)
- Examine integration tests: `tests/test_cargo_templates_integration.py`

---

## Changelog

### Version 2.0 (2025-12-29)
-  Initial release of Cargo Template API
-  Full CRUD operations
-  Template application with overrides
-  Default template support
-  RBAC integration
-  Performance profiling
-  Comprehensive testing
-  Complete documentation

---

**Last Updated**: 2025-12-29  
**Document Version**: 1.0  
**API Version**: 2.0 Enhanced
