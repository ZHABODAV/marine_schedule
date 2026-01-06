/**
 * API Input Validation Module
 * Provides comprehensive validation for all API endpoints
 */

class APIValidator {
    constructor() {
        this.rules = {
            // Vessel validation rules
            vessel: {
                id: { type: 'string', required: true, minLength: 1, maxLength: 50, pattern: /^[A-Z0-9_-]+$/i },
                name: { type: 'string', required: true, minLength: 1, maxLength: 100 },
                class: { type: 'string', required: true, enum: ['Handysize', 'Handymax', 'Panamax', 'Suez max', 'Capesize', 'VLCC', 'Barge'] },
                dwt: { type: 'number', required: true, min: 1000, max: 500000 },
                speed: { type: 'number', required: true, min: 1, max: 30 },
                status: { type: 'string', required: false, enum: ['Active', 'Inactive', 'Pending', 'Maintenance'] }
            },
            
            // Cargo validation rules
            cargo: {
                id: { type: 'string', required: true, minLength: 1, maxLength: 50 },
                commodity: { type: 'string', required: true, minLength: 1, maxLength: 100 },
                quantity: { type: 'number', required: true, min: 1, max: 500000 },
                loadPort: { type: 'string', required: true, minLength: 1, maxLength: 100 },
                dischPort: { type: 'string', required: true, minLength: 1, maxLength: 100 },
                laycanStart: { type: 'date', required: true },
                laycanEnd: { type: 'date', required: true },
                status: { type: 'string', required: false, enum: ['Pending', 'Assigned', 'Completed', 'Cancelled'] }
            },
            
            // Route validation rules
            route: {
                from: { type: 'string', required: true, minLength: 1, maxLength: 100 },
                to: { type: 'string', required: true, minLength: 1, maxLength: 100 },
                distance: { type: 'number', required: true, min: 1, max: 50000 },
                canal: { type: 'string', required: false, maxLength: 100 }
            },
            
            // Voyage validation rules
            voyage: {
                id: { type: 'string', required: true },
                vesselId: { type: 'string', required: true },
                commitmentId: { type: 'string', required: false },
                startDate: { type: 'date', required: true },
                legs: { type: 'array', required: true, minLength: 1 }
            },
            
            // Berth constraint validation
            berthConstraint: {
                berth: { type: 'string', required: true },
                type: { type: 'string', required: true, enum: ['max_length', 'max_draft', 'max_beam', 'min_gap', 'maintenance'] },
                value: { type: 'number', required: true, min: 0 },
                startDate: { type: 'date', required: false },
                endDate: { type: 'date', required: false }
            },
            
            // Financial data validation
            financial: {
                operationalCost: { type: 'number', required: false, min: 0 },
                overheadCost: { type: 'number', required: false, min: 0 },
                otherCost: { type: 'number', required: false, min: 0 }
            }
        };
    }
    
    /**
     * Validate data against a rule set
     * @param {string} entityType - Type of entity (vessel, cargo, etc.)
     * @param {object} data - Data to validate
     * @returns {object} - { valid: boolean, errors: array }
     */
    validate(entityType, data) {
        const rules = this.rules[entityType];
        if (!rules) {
            return { valid: false, errors: [`Unknown entity type: ${entityType}`] };
        }
        
        const errors = [];
        
        // Check required fields
        for (const [field, rule] of Object.entries(rules)) {
            if (rule.required && (data[field] === undefined || data[field] === null || data[field] === '')) {
                errors.push(`Field '${field}' is required`);
                continue;
            }
            
            // Skip validation for optional empty fields
            if (!rule.required && (data[field] === undefined || data[field] === null || data[field] === '')) {
                continue;
            }
            
            const value = data[field];
            
            // Type validation
            if (rule.type === 'string' && typeof value !== 'string') {
                errors.push(`Field '${field}' must be a string`);
                continue;
            }
            
            if (rule.type === 'number' && (typeof value !== 'number' || isNaN(value))) {
                errors.push(`Field '${field}' must be a valid number`);
                continue;
            }
            
            if (rule.type === 'date') {
                const dateValue = new Date(value);
                if (isNaN(dateValue.getTime())) {
                    errors.push(`Field '${field}' must be a valid date`);
                    continue;
                }
            }
            
            if (rule.type === 'array' && !Array.isArray(value)) {
                errors.push(`Field '${field}' must be an array`);
                continue;
            }
            
            // String length validation
            if (rule.type === 'string') {
                if (rule.minLength && value.length < rule.minLength) {
                    errors.push(`Field '${field}' must be at least ${rule.minLength} characters`);
                }
                if (rule.maxLength && value.length > rule.maxLength) {
                    errors.push(`Field '${field}' must not exceed ${rule.maxLength} characters`);
                }
                if (rule.pattern && !rule.pattern.test(value)) {
                    errors.push(`Field '${field}' has invalid format`);
                }
            }
            
            // Number range validation
            if (rule.type === 'number') {
                if (rule.min !== undefined && value < rule.min) {
                    errors.push(`Field '${field}' must be at least ${rule.min}`);
                }
                if (rule.max !== undefined && value > rule.max) {
                    errors.push(`Field '${field}' must not exceed ${rule.max}`);
                }
            }
            
            // Array length validation
            if (rule.type === 'array') {
                if (rule.minLength && value.length < rule.minLength) {
                    errors.push(`Field '${field}' must have at least ${rule.minLength} items`);
                }
                if (rule.maxLength && value.length > rule.maxLength) {
                    errors.push(`Field '${field}' must not exceed ${rule.maxLength} items`);
                }
            }
            
            // Enum validation
            if (rule.enum && !rule.enum.includes(value)) {
                errors.push(`Field '${field}' must be one of: ${rule.enum.join(', ')}`);
            }
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
    
    /**
     * Validate and sanitize input
     * @param {string} entityType - Type of entity
     * @param {object} data - Data to validate and sanitize
     * @returns {object} - { valid: boolean, data: object, errors: array }
     */
    validateAndSanitize(entityType, data) {
        const validation = this.validate(entityType, data);
        
        if (!validation.valid) {
            return {
                valid: false,
                data: null,
                errors: validation.errors
            };
        }
        
        // Sanitize data
        const sanitized = {};
        const rules = this.rules[entityType];
        
        for (const [field, rule] of Object.entries(rules)) {
            if (data[field] !== undefined && data[field] !== null) {
                let value = data[field];
                
                // String sanitization
                if (rule.type === 'string') {
                    value = String(value).trim();
                    // Remove any potentially dangerous characters
                    value = value.replace(/[<>]/g, '');
                }
                
                // Number sanitization
                if (rule.type === 'number') {
                    value = parseFloat(value);
                }
                
                // Date sanitization
                if (rule.type === 'date') {
                    value = new Date(value).toISOString();
                }
                
                sanitized[field] = value;
            } else if (rule.required) {
                return {
                    valid: false,
                    data: null,
                    errors: [`Required field '${field}' is missing`]
                };
            }
        }
        
        return {
            valid: true,
            data: sanitized,
            errors: []
        };
    }
    
    /**
     * Batch validate multiple items
     * @param {string} entityType - Type of entity
     * @param {array} items - Array of items to validate
     * @returns {object} - { valid: boolean, validItems: array, invalidItems: array }
     */
    batchValidate(entityType, items) {
        const validItems = [];
        const invalidItems = [];
        
        items.forEach((item, index) => {
            const result = this.validateAndSanitize(entityType, item);
            if (result.valid) {
                validItems.push(result.data);
            } else {
                invalidItems.push({
                    index: index,
                    item: item,
                    errors: result.errors
                });
            }
        });
        
        return {
            valid: invalidItems.length === 0,
            validItems: validItems,
            invalidItems: invalidItems
        };
    }
    
    /**
     * Display validation errors in UI
     * @param {array} errors - Array of error messages
     * @param {string} containerId - ID of container element
     */
    displayErrors(errors, containerId = 'validation-errors') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Validation error container not found');
            return;
        }
        
        if (errors.length === 0) {
            container.innerHTML = '';
            container.style.display = 'none';
            return;
        }
        
        container.innerHTML = `
            <div class="validation-errors" style="background: #fee; border: 1px solid #fcc; border-radius: 4px; padding: 1rem; margin: 1rem 0;">
                <h4 style="margin-top: 0; color: #c00;">Validation Errors:</h4>
                <ul style="margin-bottom: 0;">
                    ${errors.map(error => `<li>${error}</li>`).join('')}
                </ul>
            </div>
        `;
        container.style.display = 'block';
    }
}

// Create global validator instance
const apiValidator = new APIValidator();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIValidator, apiValidator };
}

console.log(' API Validation module loaded successfully');
