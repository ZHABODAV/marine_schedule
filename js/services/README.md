# Services

This directory contains service layer modules for the application.

## Files

### [`api-client.js`](api-client.js:1)

Centralized API client service for making HTTP requests to the backend API.

**Features:**
- Authentication handling (Bearer tokens)
- Request/response interceptors
- Built-in validation integration
- Comprehensive endpoint coverage
- Error handling and retry logic
- File upload support

**Usage:**
```javascript
// Get vessels
const vessels = await apiClient.getVessels({ module: 'deepsea' });

// Create vessel with validation
const result = await apiClient.createVessel({
    vessel_id: 'V001',
    vessel_name: 'Atlantic Star',
    vessel_class: 'Handysize',
    dwt_mt: 35000,
    speed_kts: 14.5
});

// Login
const loginResult = await apiClient.login('admin', 'password');
```

**Global Instance:**
- Available as `apiClient` globally
- Automatically integrates with `apiValidator` if available

## Related Files

- [`../api-validation.js`](../api-validation.js:1) - Validation rules and validator
- [`../ui/validation-display.js`](../ui/validation-display.js:1) - Error display components
- [`../ui/form-validation.js`](../ui/form-validation.js:1) - Form integration

## Documentation

See [API Client Integration Guide](../../docs/API_CLIENT_INTEGRATION_GUIDE.md) for complete documentation and examples.
