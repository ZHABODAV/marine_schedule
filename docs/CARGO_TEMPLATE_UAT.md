# Cargo Template API - User Acceptance Test (UAT) Plan

## Test Overview
User Acceptance Testing for Cargo Template Management API endpoints.

**Test Date**: 2025-12-29  
**Tested By**: QA Team  
**System Version**: 2.0 Enhanced

---

## Test Environment Setup

### Prerequisites
1. API Server running at `http://localhost:5000`
2. Valid admin credentials
3. REST API client (Postman, curl, or browser)
4. Test data prepared

### Setup Steps
1. Start the API server:
   ```bash
   python api_server_enhanced.py
   ```

2. Login to get authentication token:
   ```bash
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "your_password"}'
   ```

3. Save the returned token for subsequent requests

---

## UAT Test Cases

### Test Case 1: Create Cargo Template
**Objective**: Verify users can create a new cargo template

**Steps**:
1. Send POST request to `/api/cargo-templates`
2. Include valid template data in JSON format
3. Include authentication token in header

**Request Example**:
```bash
curl -X POST http://localhost:5000/api/cargo-templates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
    "isDefault": false
  }'
```

**Expected Result**:
-  Status Code: 201 Created
-  Response includes template ID
-  Response includes all submitted fields
-  Response includes `createdAt` and `updatedAt` timestamps
-  Template is saved and retrievable

**Actual Result**: ________________

**Status**:  Pass  Fail

---

### Test Case 2: Get All Templates
**Objective**: Verify users can retrieve all cargo templates

**Steps**:
1. Send GET request to `/api/cargo-templates`
2. Include authentication token

**Request Example**:
```bash
curl -X GET http://localhost:5000/api/cargo-templates \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Result**:
-  Status Code: 200 OK
-  Response contains `templates` array
-  Response contains `count` field
-  All templates are listed
-  Template data is complete

**Actual Result**: ________________

**Status**:  Pass  Fail

---

### Test Case 3: Get Template by ID
**Objective**: Verify users can retrieve a specific template

**Steps**:
1. Create a template (or use existing ID)
2. Send GET request to `/api/cargo-templates/{template_id}`
3. Include authentication token

**Request Example**:
```bash
curl -X GET http://localhost:5000/api/cargo-templates/tpl_20251229123456_0 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Result**:
-  Status Code: 200 OK
-  Response contains complete template data
-  Template ID matches request
-  All fields are present

**Actual Result**: ________________

**Status**:  Pass  Fail

---

### Test Case 4: Update Template
**Objective**: Verify users can update existing templates

**Steps**:
1. Create or select an existing template
2. Send PUT request to `/api/cargo-templates/{template_id}`
3. Include authentication token
4. Include update data

**Request Example**:
```bash
curl -X PUT http://localhost:5000/api/cargo-templates/tpl_20251229123456_0 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Template Name",
    "quantity": 80000,
    "freightRate": 16.0
  }'
```

**Expected Result**:
-  Status Code: 200 OK
-  Updated fields reflect changes
-  Unchanged fields remain the same
-  `updatedAt` timestamp is updated
-  Changes are persisted

**Actual Result**: ________________

**Status**:  Pass  Fail

---

### Test Case 5: Delete Template
**Objective**: Verify users can delete templates

**Steps**:
1. Create a test template
2. Send DELETE request to `/api/cargo-templates/{template_id}`
3. Include authentication token
4. Verify template is removed

**Request Example**:
```bash
curl -X DELETE http://localhost:5000/api/cargo-templates/tpl_20251229123456_0 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Result**:
-  Status Code: 200 OK
-  Success message returned
-  Template is removed from storage
-  Subsequent GET returns 404

**Actual Result**: ________________

**Status**:  Pass  Fail

---

### Test Case 6: Apply Template
**Objective**: Verify template can be applied with overrides

**Steps**:
1. Create or select a template
2. Send POST request to `/api/cargo-templates/{template_id}/apply`
3. Include optional override data

**Request Example**:
```bash
curl -X POST http://localhost:5000/api/cargo-templates/tpl_20251229123456_0/apply \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 70000,
    "loadPort": "Newcastle"
  }'
```

**Expected Result**:
-  Status Code: 200 OK
-  Response contains merged data
-  Override values replace template values
-  Non-overridden values come from template
-  All required fields are present

**Actual Result**: ________________

**Status**:  Pass  Fail

---

### Test Case 7: Get Default Template
**Objective**: Verify default template retrieval

**Steps**:
1. Create a template with `isDefault: true`
2. Send GET request to `/api/cargo-templates/default`

**Request Example**:
```bash
curl -X GET http://localhost:5000/api/cargo-templates/default \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Result**:
-  Status Code: 200 OK
-  Response contains default template
-  `isDefault` field is true
-  Only one default template exists

**Actual Result**: ________________

**Status**:  Pass  Fail

---

### Test Case 8: Validation Tests
**Objective**: Verify proper validation of input data

**Test 8a - Missing Required Fields**:
```bash
curl -X POST http://localhost:5000/api/cargo-templates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"commodity": "Coal"}'
```

**Expected Result**:
-  Status Code: 400 Bad Request
-  Error message indicates missing fields

**Test 8b - Invalid Template ID**:
```bash
curl -X GET http://localhost:5000/api/cargo-templates/invalid_id \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Result**:
-  Status Code: 404 Not Found
-  Error message indicates template not found

**Status**:  Pass  Fail

---

### Test Case 9: Authorization Tests
**Objective**: Verify proper authorization enforcement

**Test 9a - No Token**:
```bash
curl -X GET http://localhost:5000/api/cargo-templates
```

**Expected Result**:
-  Status Code: 401 Unauthorized
-  Error message about missing token

**Test 9b - Invalid Token**:
```bash
curl -X GET http://localhost:5000/api/cargo-templates \
  -H "Authorization: Bearer invalid_token"
```

**Expected Result**:
-  Status Code: 401 Unauthorized
-  Error message about invalid token

**Status**:  Pass  Fail

---

### Test Case 10: Multiple Default Templates
**Objective**: Verify only one template can be default

**Steps**:
1. Create template A with `isDefault: true`
2. Create template B with `isDefault: true`
3. Verify template A's `isDefault` is now false

**Expected Result**:
-  Only template B hasdefault flag true
-  Previous default is automatically cleared
-  GET /api/cargo-templates/default returns template B

**Actual Result**: ________________

**Status**:  Pass  Fail

---

## Performance Tests

### Test Case 11: Response Time
**Objective**: Verify acceptable response times

**Endpoints to Test**:
- GET /api/cargo-templates (all)
- GET /api/cargo-templates/{id}
- POST /api/cargo-templates
- PUT /api/cargo-templates/{id}
- DELETE /api/cargo-templates/{id}

**Expected Result**:
-  All responses < 500ms under normal load
-  No timeouts
-  Consistent performance

**Actual Results**: ________________

**Status**:  Pass  Fail

---

### Test Case 12: Concurrent Access
**Objective**: Verify system handles concurrent requests

**Steps**:
1. Make simultaneous requests from multiple clients
2. Verify data integrity
3. Check for race conditions

**Expected Result**:
-  All requests process correctly
-  No data corruption
-  Proper locking/consistency

**Actual Result**: ________________

**Status**:  Pass  Fail

---

## Data Integrity Tests

### Test Case 13: Data Persistence
**Objective**: Verify templates persist across server restarts

**Steps**:
1. Create several templates
2. Stop the API server
3. Start the API server
4. retrieve templates

**Expected Result**:
-  All templates still exist
-  Data is intact
-  No data loss

**Actual Result**: ________________

**Status**:  Pass  Fail

---

## Summary

**Total Test Cases**: 13  
**Passed**: _______  
**Failed**: _______  
**Blocked**: _______  

**Overall Status**:  Approved  Rejected  Conditional Approval

**Comments**:
_____________________________________________
_____________________________________________
_____________________________________________

**Tested By**: ________________  
**Date**: ________________  
**Signature**: ________________

---

## Appendix: Quick Reference

### All Cargo Template Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cargo-templates` | Get all templates |
| GET | `/api/cargo-templates/{id}` | Get template by ID |
| GET | `/api/cargo-templates/default` | Get default template |
| POST | `/api/cargo-templates` | Create new template |
| PUT | `/api/cargo-templates/{id}` | Update template |
| DELETE | `/api/cargo-templates/{id}` | Delete template |
| POST | `/api/cargo-templates/{id}/apply` | Apply template |

### Sample Template Structure

```json
{
  "id": "tpl_20251229123456_0",
  "name": "Template Name",
  "description": "Description",
  "commodity": "Iron Ore",
  "quantity": 75000,
  "loadPort": "Port Hedland",
  "dischPort": "Qingdao",
  "freightRate": 15.5,
  "operationalCost": 50000,
  "overheadCost": 10000,
  "otherCost": 5000,
  "isDefault": false,
  "createdAt": "2025-12-29T10:30:00.000000",
  "updatedAt": "2025-12-29T10:30:00.000000"
}
```
