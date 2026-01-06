# Cargo Template API Screenshots

This directory contains screenshots demonstrating the Cargo Template API in action.

## Screenshot Checklist

Use Postman, Insomnia, or any REST API client to capture the following screenshots:

### Authentication
- [ ] **`AUTH_LOGIN.png`** - Login request and response with token

### Template CRUD Operations
- [ ] **`GET_ALL_TEMPLATES.png`** - GET /api/cargo-templates showing list of templates
- [ ] **`CREATE_TEMPLATE.png`** - POST /api/cargo-templates creating a new template
- [ ] **`GET_TEMPLATE_BY_ID.png`** - GET /api/cargo-templates/{id} retrieving specific template
- [ ] **`UPDATE_TEMPLATE.png`** - PUT /api/cargo-templates/{id} updating a template
- [ ] **`DELETE_TEMPLATE.png`** - DELETE /api/cargo-templates/{id} deleting a template
- [ ] **`GET_DEFAULT_TEMPLATE.png`** - GET /api/cargo-templates/default retrieving default template

### Template Application
- [ ] **`APPLY_TEMPLATE.png`** - POST /api/cargo-templates/{id}/apply applying template with overrides

### Error Cases
- [ ] **`VALIDATION_ERROR.png`** - Screenshot showing validation error (missing required fields)
- [ ] **`NOT_FOUND_ERROR.png`** - Screenshot showing 404 error for non-existent template
- [ ] **`UNAUTHORIZED_ERROR.png`** - Screenshot showing 401 error without authentication

### Response Times
- [ ] **`PERFORMANCE_METRICS.png`** - Screenshot showing response times for various endpoints

## Recommended Tools

- **Postman**: https://www.postman.com/downloads/
- **Insomnia**: https://insomnia.rest/download
- **REST Client (VS Code Extension**

## Screenshot Guidelines

1. **Resolution**: 1920x1080 or higher
2. **Format**: PNG preferred
3. **Content**: Include full request/response with:
   - HTTP method and URL
   - Request headers (Authorization)
   - Request body (if applicable)
   - Response status code
   - Response body
   - Response time

4. **Annotations**: Consider adding arrows or highlights for key information

## Example Screenshot Setup

### Postman Collections
Import the following Postman collection to easily test all endpoints:

```json
{
  "info": {
    "name": "Cargo Template API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "raw",
          "raw": "{\"username\": \"admin\", \"password\": \"admin\"}"
        },
        "url": {
          "raw": "http://localhost:5000/api/auth/login"
        }
      }
    },
    {
      "name": "GET All Templates",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          }
        ],
        "url": {
          "raw": "http://localhost:5000/api/cargo-templates"
        }
      }
    }
  ]
}
```

Save this configuration and use environment variables for the token.

## Current Status

Screenshots will be captured during User Acceptance Testing (UAT) phase.

Reference the UAT guide: [`../CARGO_TEMPLATE_UAT.md`](../CARGO_TEMPLATE_UAT.md)
