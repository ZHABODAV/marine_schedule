# JavaScript Modules

##  **NEW: Modern Module System**

The application now uses ES6 modules with a centralized entry point [`main.js`](main.js).

### Quick Start
```html
<!-- Include in HTML -->
<script type="module" src="js/main.js"></script>
```

```javascript
// In browser console
vesselScheduler.info()  // Show available commands
```

** See [`MODULE_LOADING.md`](MODULE_LOADING.md) for complete documentation.**

---

## Legacy Documentation

This directory contains modularized JavaScript code for the Vessel Scheduler application.

## Structure

```
js/
├── index.js                          # Main entry point & initialization
├── variables.js                      # Global variables & library fallbacks
├── api-validation.js                 # Input validation for all API endpoints
├── api-documentation-generator.js    # Automatic API documentation generation
└── README.md                         # This file
```

## Usage

### Include in HTML

Add these scripts in your HTML file in the following order:

```html
<!-- Required Libraries -->
<script src="https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>

<!-- Application Modules -->
<script src="js/variables.js"></script>
<script src="js/api-validation.js"></script>
<script src="js/api-documentation-generator.js"></script>
<script src="js/index.js"></script>

<!-- Existing Application Code -->
<script src="vessel_scheduler_enhanced.js"></script>
```

## Modules

### 1. variables.js

Defines all global variables and provides fallbacks for missing libraries.

**Features:**
- Missing variable declarations (`totalRevenue`, `colorMap`, `data`)
- Library fallbacks (XLSX, html2pdf, vis.Network, PDFExport)
- Helper functions
- Error handling for missing dependencies

**Usage:**
```javascript
// Variables are automatically available globally
console.log(colorMap);  // Operation colors
console.log(data);      // Voyage planner data

// Helper function
const opCode = getOpCode('loading', 'LD');
```

### 2. api-validation.js

Provides comprehensive input validation for all API endpoints.

**Features:**
- Validation rules for all entity types
- Type checking and sanitization
- Batch validation
- Error display functionality

**Usage:**
```javascript
// Validate a vessel
const vesselData = {
    id: 'V001',
    name: 'Atlantic Star',
    class: 'Handysize',
    dwt: 35000,
    speed: 14
};

const result = apiValidator.validateAndSanitize('vessel', vesselData);

if (result.valid) {
    // Use result.data (sanitized)
    await saveVessel(result.data);
} else {
    // Display errors
    apiValidator.displayErrors(result.errors);
}
```

**Supported Entity Types:**
- `vessel` - Vessel data
- `cargo` - Cargo commitments
- `route` - Shipping routes
- `voyage` - Voyage data
- `berthConstraint` - Berth constraints
- `financial` - Financial data

**Validation Example:**
```javascript
// Example: Validate cargo before submission
document.getElementById('cargoForm').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const cargoData = {
        id: document.getElementById('cargoId').value,
        commodity: document.getElementById('commodity').value,
        quantity: parseInt(document.getElementById('quantity').value),
        loadPort: document.getElementById('loadPort').value,
        dischPort: document.getElementById('dischPort').value,
        laycanStart: document.getElementById('laycanStart').value,
        laycanEnd: document.getElementById('laycanEnd').value
    };
    
    const validation = apiValidator.validateAndSanitize('cargo', cargoData);
    
    if (!validation.valid) {
        apiValidator.displayErrors(validation.errors, 'cargo-errors');
        return;
    }
    
    // Submit sanitized data
    submitCargo(validation.data);
});
```

### 3. api-documentation-generator.js

Automatically generates API documentation in HTML and Markdown formats.

**Features:**
- Register endpoints with parameters and responses
- Generate HTML documentation
- Generate Markdown documentation
- Download functionality

**Usage:**
```javascript
// Generate and download HTML documentation
vesselSchedulerAPIDocs.downloadHTML();

// Generate and download Markdown documentation
vesselSchedulerAPIDocs.downloadMarkdown();

// Add custom endpoint
vesselSchedulerAPIDocs.registerEndpoint({
    method: 'POST',
    path: '/api/custom-endpoint',
    description: 'Custom endpoint description',
    parameters: [
        { name: 'param1', type: 'string', required: true, description: 'Parameter description' }
    ],
    responses: [
        { code: 200, description: 'Success', body: { success: true } }
    ]
});
```

### 4. index.js

Main entry point that initializes the application and provides global utilities.

**Features:**
- Library dependency checking
- Application initialization
- Global utility object
- Ready event dispatching

**Usage: **
```javascript
// Wait for application to be ready
document.addEventListener('vesselSchedulerReady', (e) => {
    console.log(`App ready! Version: ${e.detail.version}`);
    
    // Use global utilities
    vesselScheduler.info();  // Show help
    
    // Generate documentation
    vesselScheduler.generateDocs();
    
    // Validate data
    const result = vesselScheduler.validateEntity('vessel', myVesselData);
});
```

**Console Commands:**
```javascript
// Show application info
vesselScheduler.info();

// Generate HTML documentation
vesselScheduler.generateDocs();

// Generate Markdown documentation
vesselScheduler.generateMarkdownDocs();

// Validate entity
vesselScheduler.validateEntity('vessel', {
    id: 'V001',
    name: 'Test Vessel',
    class: 'Handysize',
    dwt: 35000,
    speed: 14
});
```

## Integration with Existing Code

### Step 1: Update HTML

Replace the existing script includes with the new modular structure:

```html
<!-- OLD (remove or comment out) -->
<!-- <script src="vessel_scheduler_enhanced.js"></script> -->

<!-- NEW -->
<script src="js/variables.js"></script>
<script src="js/api-validation.js"></script>
<script src="js/api-documentation-generator.js"></script>
<script src="js/index.js"></script>
<script src="vessel_scheduler_enhanced.js"></script>
```

### Step 2: Add Validation to Forms

Example for vessel form:

```javascript
// Find this in vessel_scheduler_enhanced.js:
document.getElementById('vesselForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const vesselData = {
        id: document.getElementById('vesselId').value,
        // ... rest of fields
    };
    
    // ADD VALIDATION HERE
    const validation = apiValidator.validateAndSanitize('vessel', vesselData);
    
    if (!validation.valid) {
        apiValidator.displayErrors(validation.errors);
        return;
    }
    
    // Use validation.data instead of vesselData
    // ... rest of submission logic
});
```

### Step 3: Test

1. Open the application in a browser
2. Open dev tools console
3. Type `vesselScheduler.info()` to verify modules are loaded
4. Test form validation by submitting invalid data

## Best Practices

### Validation

Always validate data before:
- API calls
- LocalStorage saves
- Form submissions
- File imports

### Error Handling

```javascript
try {
    const result = apiValidator.validateAndSanitize('vessel', data);
    
    if (!result.valid) {
        apiValidator.displayErrors(result.errors);
        return;
    }
    
    await processData(result.data);
} catch (error) {
    console.error('Validation error:', error);
    showNotification('An error occurred', 'error');
}
```

### Documentation

When adding new API endpoints, register them:

```javascript
vesselSchedulerAPIDocs.registerEndpoint({
    method: 'POST',
    path: '/api/new-endpoint',
    description: 'Description of what this endpoint does',
    authentication: true,
    parameters: [
        {
            name: 'parameter_name',
            type: 'string',
            required: true,
            description: 'What this parameter does'
        }
    ],
    requestBody: {
        example: 'value'
    },
    responses: [
        {
            code: 200,
            description: 'Success',
            body: { success: true, data: {} }
        },
        {
            code: 400,
            description: 'Invalid input',
            body: { success: false, error: 'Error message' }
        }
    ],
    examples: [
        {
            title: 'Example Request',
            code: `fetch('/api/new-endpoint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ example: 'value' })
});`
        }
    ]
});
```

## Troubleshooting

### "apiValidator is not defined"

Make sure `api-validation.js` is loaded before your code:

```html
<script src="js/api-validation.js"></script>
<script src="your-code.js"></script>
```

### "XLSX is not defined"

Include the SheetJS library:

```html
<script src="https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js"></script>
```

### Validation errors not showing

Ensure you have a container element with the correct ID:

```html
<div id="validation-errors"></div>
```

Or specify a custom container:

```javascript
apiValidator.displayErrors(errors, 'my-custom-error-container');
```

## Future Enhancements

See [JAVASCRIPT_MODERNIZATION_PLAN.md](../docs/JAVASCRIPT_MODERNIZATION_PLAN.md) for:
- Module splitting roadmap
- Vue.js migration plan
- Build process setup
- Testing strategy

## Support

For questions or issues:
1. Check the modernization plan: `docs/ JAVASCRIPT_MODERNIZATION_PLAN.md`
2. Review API documentation: `docs/API_REFERENCE.md`
3. Type `vesselScheduler.info()` in browser console for quick help
