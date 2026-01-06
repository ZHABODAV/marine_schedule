# API Client Integration Guide

Complete guide for using the API client service with validation in forms.

## Overview

The API client service provides:

1. **APIClient**: Centralized HTTP client with authentication
2. **APIValidator**: Input validation for all entity types
3. **ValidationDisplay**: UI components for displaying errors
4. **FormValidator**: Integration between forms and validation

## Quick Start

### 1. Include Required Scripts

```html
<!-- Load in this order -->
<script src="js/api-validation.js"></script>
<script src="js/services/api-client.js"></script>
<script src="js/ui/validation-display.js"></script>
<script src="js/ui/form-validation.js"></script>
```

### 2. Basic Form Validation

```html
<form id="vessel-form">
    <div id="form-errors"></div>
    
    <label for="vessel-name">Vessel Name:</label>
    <input type="text" id="vessel-name" name="name" required>
    
    <label for="vessel-class">Vessel Class:</label>
    <select id="vessel-class" name="class" required>
        <option value="">Select...</option>
        <option value="Handysize">Handysize</option>
        <option value="Panamax">Panamax</option>
    </select>
    
    <label for="vessel-dwt">DWT (MT):</label>
    <input type="number" id="vessel-dwt" name="dwt" required>
    
    <button type="submit">Create Vessel</button>
</form>

<script>
// Simple form validation
const vesselForm = new FormValidator('#vessel-form', {
    entityType: 'vessel',
    errorContainer: '#form-errors',
    onSubmit: async (data) => {
        return await apiClient.createVessel(data);
    },
    onSuccess: (result) => {
        console.log('Vessel created:', result);
        // Refresh vessel list, close modal, etc.
    }
});
</script>
```

## API Client Usage

### Authentication

```javascript
// Login
const loginResult = await apiClient.login('admin', 'password');
if (loginResult.success) {
    console.log('Logged in:', loginResult.data.user);
}

// Logout
await apiClient.logout();

// Get current user
const userResult = await apiClient.getCurrentUser();
```

### Vessel Operations

```javascript
// Get all vessels
const vessels = await apiClient.getVessels({ module: 'deepsea' });

// Get single vessel
const vessel = await apiClient.getVessel('V001');

// Create vessel
const newVessel = await apiClient.createVessel({
    vessel_id: 'V002',
    vessel_name: 'Pacific Dawn',
    vessel_class: 'Panamax',
    dwt_mt: 75000,
    speed_kts: 15.0
});

// Update vessel
await apiClient.updateVessel('V002', {
    speed_kts: 15.5
});

// Delete vessel
await apiClient.deleteVessel('V002');
```

### Cargo Operations

```javascript
// Get all cargo
const cargo = await apiClient.getCargo({ status: 'pending' });

// Create cargo
const newCargo = await apiClient.createCargo({
    cargo_id: 'C001',
    commodity: 'Grain',
    quantity_mt: 50000,
    load_port: 'Houston',
    disch_port: 'Rotterdam',
    laycan_start: '2025-01-15',
    laycan_end: '2025-01-20'
});
```

### Schedule Operations

```javascript
// Generate schedule
const schedule = await apiClient.generateSchedule({
    type: 'deepsea',
    start_date: '2025-01-01',
    end_date: '2025-01-31',
    options: {
        optimize_ballast: true
    }
});

// Get schedule
const scheduleData = await apiClient.getSchedule('deepsea', {
    month: 1,
    year: 2025
});

// Calculate voyage
const voyageCalc = await apiClient.calculateVoyage({
    vessel_id: 'V001',
    cargo_id: 'C001',
    route: ['Houston', 'Rotterdam']
});
```

## Validation

### Manual Validation

```javascript
// Validate data
const result = apiValidator.validate('vessel', {
    name: 'Test Ship',
    class: 'Panamax',
    dwt: 75000,
    speed: 15
});

if (!result.valid) {
    console.error('Validation errors:', result.errors);
}
```

### Batch Validation

```javascript
const vessels = [
    { name: 'Ship 1', class: 'Handysize', dwt: 35000, speed: 14 },
    { name: 'Ship 2', class: 'Invalid', dwt: -1, speed: 50 }
];

const batchResult = apiValidator.batchValidate('vessel', vessels);
console.log('Valid items:', batchResult.validItems);
console.log('Invalid items:', batchResult.invalidItems);
```

## Error Display

### Alert-style Errors

```javascript
// Display errors
ValidationDisplay.displayErrors(
    ['Field vessel_name is required', 'DWT must be at least 1000'],
    '#error-container',
    {
        title: 'Validation Errors',
        type: 'error',
        dismissible: true
    }
);

// Display success
ValidationDisplay.displaySuccess(
    'Vessel created successfully',
    '#error-container',
    { autoHide: true, autoHideDelay: 3000 }
);

// Display warning
ValidationDisplay.displayWarning(
    'Some optional fields are missing',
    '#error-container'
);
```

### Field-level Errors

```javascript
// Show error on specific field
ValidationDisplay.displayFieldError(
    'vessel-name',
    'Vessel name is required',
    { style: 'tooltip' }
);

// Clear field error
ValidationDisplay.clearFieldError('vessel-name');
```

### Toast Notifications

```javascript
// Show toast
ValidationDisplay.showToast('Vessel saved successfully', {
    type: 'success',
    duration: 3000,
    position: 'top-right'
});

// Error toast
ValidationDisplay.showToast('Failed to save vessel', {
    type: 'error',
    duration: 5000
});
```

## Advanced Form Integration

### Custom Validation Logic

```javascript
const cargoForm = new FormValidator('#cargo-form', {
    entityType: 'cargo',
    errorContainer: '#cargo-errors',
    
    // Add custom validation
    onValidate: (data, validationResult) => {
        const errors = [...validationResult.errors];
        
        // Check laycan dates
        const start = new Date(data.laycanStart);
        const end = new Date(data.laycanEnd);
        
        if (start > end) {
            errors.push('Laycan start date must be before end date');
        }
        
        if (errors.length > 0) {
            return { valid: false, errors };
        }
        
        return validationResult;
    },
    
    onSubmit: async (data) => {
        return await apiClient.createCargo(data);
    },
    
    onSuccess: (result) => {
        console.log('Cargo created:', result);
        // Close modal, refresh list, etc.
    },
    
    onError: (result) => {
        console.error('Failed to create cargo:', result);
    }
});
```

### Real-time Validation

```javascript
const vesselForm = new FormValidator('#vessel-form', {
    entityType: 'vessel',
    validateOnBlur: true,  // Validate when field loses focus
    validateOnInput: true, // Validate as user types
    showFieldErrors: true, // Show errors on individual fields
    showSummaryErrors: true // Show summary in error container
});
```

### Dynamic Forms

```javascript
// Programmatically validate
const result = vesselForm.validate();
if (result.valid) {
    console.log('Form is valid');
}

// Get form data
const data = vesselForm.getFormData();

// Set loading state
vesselForm.setLoading(true);

// Reset form
vesselForm.reset();

// Clear errors
vesselForm.clearErrors();
```

## API Client Customization

### Request Interceptors

```javascript
// Add authentication header
apiClient.addRequestInterceptor((config) => {
    console.log('Sending request:', config.method, config.url);
    return config;
});
```

### Response Interceptors

```javascript
// Log all responses
apiClient.addResponseInterceptor(async (response) => {
    console.log('Response received:', response.status);
    return response;
});
```

### Handle Unauthorized

```javascript
// Override unauthorized handler
apiClient.onUnauthorized = () => {
    console.warn('Session expired');
    window.location.href = '/login.html';
};
```

## Complete Examples

### Vessel Management Form

```html
<div class="vessel-management">
    <h2>Add New Vessel</h2>
    
    <div id="vessel-errors"></div>
    
    <form id="vessel-form">
        <div class="form-group">
            <label for="vessel-id">Vessel ID*</label>
            <input type="text" id="vessel-id" name="id" required>
        </div>
        
        <div class="form-group">
            <label for="vessel-name">Vessel Name*</label>
            <input type="text" id="vessel-name" name="name" required>
        </div>
        
        <div class="form-group">
            <label for="vessel-class">Class*</label>
            <select id="vessel-class" name="class" required>
                <option value="">Select class...</option>
                <option value="Handysize">Handysize</option>
                <option value="Handymax">Handymax</option>
                <option value="Panamax">Panamax</option>
                <option value="Suez max">Suez max</option>
                <option value="Capesize">Capesize</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="vessel-dwt">DWT (MT)*</label>
            <input type="number" id="vessel-dwt" name="dwt" min="1000" max="500000" required>
        </div>
        
        <div class="form-group">
            <label for="vessel-speed">Speed (knots)*</label>
            <input type="number" id="vessel-speed" name="speed" min="1" max="30" step="0.1" required>
        </div>
        
        <div class="form-group">
            <label for="vessel-status">Status</label>
            <select id="vessel-status" name="status">
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
                <option value="Maintenance">Maintenance</option>
            </select>
        </div>
        
        <button type="submit" class="btn-primary">Create Vessel</button>
        <button type="button" class="btn-secondary" onclick="vesselFormValidator.reset()">Reset</button>
    </form>
</div>

<script>
const vesselFormValidator = new FormValidator('#vessel-form', {
    entityType: 'vessel',
    errorContainer: '#vessel-errors',
    validateOnBlur: true,
    showFieldErrors: true,
    showSummaryErrors: true,
    
    onSubmit: async (data) => {
        // Show loading state
        vesselFormValidator.setLoading(true);
        
        try {
            const result = await apiClient.createVessel(data);
            return result;
        } finally {
            vesselFormValidator.setLoading(false);
        }
    },
    
    onSuccess: (result) => {
        // Show success message
        ValidationDisplay.showToast('Vessel created successfully!', {
            type: 'success',
            duration: 3000
        });
        
        // Refresh vessel list
        loadVesselList();
    },
    
    onError: (result) => {
        // Error is already displayed by FormValidator
        console.error('Failed to create vessel:', result);
    }
});
</script>
```

### Cargo Commitment Form

```javascript
const cargoFormValidator = new FormValidator('#cargo-form', {
    entityType: 'cargo',
    errorContainer: '#cargo-errors',
    validateOnBlur: true,
    
    onValidate: (data, result) => {
        const errors = [...result.errors];
        
        // Custom validation: check dates
        if (data.laycanStart && data.laycanEnd) {
            const start = new Date(data.laycanStart);
            const end = new Date(data.laycanEnd);
            
            if (start >= end) {
                errors.push('Laycan end date must be after start date');
            }
            
            // Check if laycan is in the past
            if (start < new Date()) {
                errors.push('Laycan start date cannot be in the past');
            }
        }
        
        // Check quantity vs vessel capacity
        if (data.quantity && data.vesselId) {
            // This would typically fetch vessel data
            // For now, just a placeholder check
            if (data.quantity > 200000) {
                errors.push('Quantity exceeds typical vessel capacity');
            }
        }
        
        return errors.length > 0 ? { valid: false, errors } : result;
    },
    
    onSubmit: async (data) => {
        return await apiClient.createCargo(data);
    },
    
    onSuccess: (result) => {
        ValidationDisplay.displaySuccess(
            `Cargo commitment ${result.data.cargo_id} created successfully`,
            '#cargo-errors',
            { autoHide: true }
        );
        
        // Close modal or redirect
        setTimeout(() => {
            window.location.href = '/cargo-list.html';
        }, 2000);
    }
});
```

## Validation Rules Reference

### Vessel
- `id`: string, required, 1-50 chars, alphanumeric
- `name`: string, required, 1-100 chars
- `class`: enum (Handysize, Handymax, Panamax, etc.)
- `dwt`: number, 1000-500000
- `speed`: number, 1-30 knots
- `status`: optional enum

### Cargo
- `id`: string, required
- `commodity`: string, required
- `quantity`: number, 1-500000 MT
- `loadPort`: string, required
- `dischPort`: string, required
- `laycanStart`: date, required
- `laycanEnd`: date, required
- `status`: optional enum

### Route
- `from`: string, required
- `to`: string, required
- `distance`: number, 1-50000 NM
- `canal`: optional string

### Voyage
- `id`: string, required
- `vesselId`: string, required
- `startDate`: date, required
- `legs`: array, minimum 1 item

## Best Practices

1. **Always validate on the client side** before sending to API
2. **Show field-level errors** for better user experience
3. **Use toast notifications** for success messages
4. **Handle loading states** during API calls
5. **Clear errors** when user corrects input
6. **Provide helpful error messages** that guide the user
7. **Use real-time validation** for critical fields
8. **Keep error container** visible near the form

## Troubleshooting

### Validation not working
- Ensure [`apiValidator`](js/api-validation.js:283) is loaded
- Check entity type matches validation rules
- Verify form field names match entity properties

### Errors not displaying
- Check error container exists in DOM
- Ensure ValidationDisplay CSS is loaded
- Verify field IDs are correct

### API calls failing
- Check network connection
- Verify authentication token
- Check API server is running on correct port
- Review browser console for errors

## Related Documentation

- [API Reference](API_REFERENCE.md)
- [JavaScript Modernization Plan](JAVASCRIPT_MODERNIZATION_PLAN.md)
- [Testing Guide](TESTING_GUIDE.md)

---

**Last Updated**: 2025-12-26  
**Version**: 1.0.0
