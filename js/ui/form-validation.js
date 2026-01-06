/**
 * Form Validation Integration
 * Provides integration between forms, API validation, and error display
 */

class FormValidator {
    /**
     * Constructor
     * @param {string|HTMLFormElement} form - Form element or selector
     * @param {object} options - Configuration options
     */
    constructor(form, options = {}) {
        this.form = typeof form === 'string' 
            ? document.querySelector(form) 
            : form;

        if (!this.form) {
            throw new Error('Form element not found');
        }

        this.options = {
            entityType: options.entityType || 'default',
            validator: options.validator || (typeof apiValidator !== 'undefined' ? apiValidator : null),
            apiClient: options.apiClient || (typeof apiClient !== 'undefined' ? apiClient : null),
            errorContainer: options.errorContainer || null,
            validateOnBlur: options.validateOnBlur !== false,
            validateOnInput: options.validateOnInput || false,
            showFieldErrors: options.showFieldErrors !== false,
            showSummaryErrors: options.showSummaryErrors !== false,
            onValidate: options.onValidate || null,
            onSubmit: options.onSubmit || null,
            onSuccess: options.onSuccess || null,
            onError: options.onError || null
        };

        this.fieldMapping = {};
        this.errors = {};
        this.isSubmitting = false;

        this.init();
    }

    /**
     * Initialize form validation
     */
    init() {
        // Prevent default form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmit();
        });

        // Add field validation listeners
        if (this.options.validateOnBlur) {
            this.addBlurListeners();
        }

        if (this.options.validateOnInput) {
            this.addInputListeners();
        }

        // Build field mapping
        this.buildFieldMapping();
    }

    /**
     * Build field mapping for error display
     */
    buildFieldMapping() {
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.name) {
                this.fieldMapping[input.name] = input.id || input.name;
            }
        });
    }

    /**
     * Add blur listeners for real-time validation
     */
    addBlurListeners() {
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                if (input.name && input.value) {
                    this.validateField(input.name, input.value);
                }
            });
        });
    }

    /**
     * Add input listeners for real-time validation
     */
    addInputListeners() {
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                if (this.errors[input.name]) {
                    // Clear error on input if field had error
                    this.validateField(input.name, input.value);
                }
            });
        });
    }

    /**
     * Validate single field
     * @param {string} fieldName
     * @param {*} value
     */
    validateField(fieldName, value) {
        if (!this.options.validator) return;

        const fieldId = this.fieldMapping[fieldName];
        if (!fieldId) return;

        // Validate field
        const result = this.options.validator.validate(this.options.entityType, {
            [fieldName]: value
        });

        // Update errors
        if (result.valid) {
            delete this.errors[fieldName];
            if (this.options.showFieldErrors) {
                ValidationDisplay.clearFieldError(fieldId);
            }
        } else {
            this.errors[fieldName] = result.errors;
            if (this.options.showFieldErrors) {
                const fieldError = result.errors.find(e => e.includes(fieldName));
                if (fieldError) {
                    ValidationDisplay.displayFieldError(fieldId, fieldError);
                }
            }
        }
    }

    /**
     * Get form data
     * @returns {object}
     */
    getFormData() {
        const formData = new FormData(this.form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            // Handle multiple values (checkboxes, multi-select)
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                // Try to parse numbers
                if (value && !isNaN(value) && value.trim() !== '') {
                    const num = parseFloat(value);
                    if (!isNaN(num) && num.toString() === value.trim()) {
                        data[key] = num;
                    } else {
                        data[key] = value;
                    }
                } else {
                    data[key] = value;
                }
            }
        }

        return data;
    }

    /**
     * Validate form
     * @returns {object} - Validation result
     */
    validate() {
        if (!this.options.validator) {
            return { valid: true, errors: [] };
        }

        const data = this.getFormData();
        const result = this.options.validator.validate(this.options.entityType, data);

        this.errors = {};
        
        if (!result.valid) {
            // Organize errors by field
            result.errors.forEach(error => {
                const match = error.match(/Field '(\w+)'/);
                if (match) {
                    const fieldName = match[1];
                    if (!this.errors[fieldName]) {
                        this.errors[fieldName] = [];
                    }
                    this.errors[fieldName].push(error);
                }
            });
        }

        // Call custom validation callback
        if (this.options.onValidate) {
            const customResult = this.options.onValidate(data, result);
            if (customResult && !customResult.valid) {
                return customResult;
            }
        }

        return result;
    }

    /**
     * Display validation errors
     * @param {object} validationResult
     */
    displayErrors(validationResult) {
        // Clear all errors first
        this.clearErrors();

        if (!validationResult || validationResult.valid) return;

        // Show field errors
        if (this.options.showFieldErrors) {
            ValidationDisplay.displayFieldErrors(validationResult, this.fieldMapping);
        }

        // Show summary errors
        if (this.options.showSummaryErrors && this.options.errorContainer) {
            ValidationDisplay.displayErrors(
                validationResult.errors,
                this.options.errorContainer,
                {
                    title: 'Please fix the following errors:',
                    type: 'error',
                    dismissible: true,
                    animate: true
                }
            );
        }
    }

    /**
     * Clear all errors
     */
    clearErrors() {
        this.errors = {};

        // Clear field errors
        if (this.options.showFieldErrors) {
            Object.values(this.fieldMapping).forEach(fieldId => {
                ValidationDisplay.clearFieldError(fieldId);
            });
        }

        // Clear summary errors
        if (this.options.errorContainer) {
            ValidationDisplay.hideErrors(
                typeof this.options.errorContainer === 'string'
                    ? document.querySelector(this.options.errorContainer)
                    : this.options.errorContainer
            );
        }
    }

    /**
     * Handle form submission
     */
    async handleSubmit() {
        if (this.isSubmitting) return;

        // Validate form
        const validationResult = this.validate();

        if (!validationResult.valid) {
            this.displayErrors(validationResult);
            if (this.options.onError) {
                this.options.onError(validationResult);
            }
            return;
        }

        // Clear errors
        this.clearErrors();

        // Get form data
        const data = this.getFormData();

        // Call custom submit handler if provided
        if (this.options.onSubmit) {
            this.isSubmitting = true;
            try {
                const result = await this.options.onSubmit(data);
                this.isSubmitting = false;
                
                if (result && result.success) {
                    this.handleSuccess(result);
                } else {
                    this.handleError(result);
                }
            } catch (error) {
                this.isSubmitting = false;
                this.handleError({ success: false, error: error.message });
            }
        }
    }

    /**
     * Handle successful submission
     * @param {object} result
     */
    handleSuccess(result) {
        // Show success message
        if (this.options.errorContainer) {
            ValidationDisplay.displaySuccess(
                result.message || 'Form submitted successfully',
                this.options.errorContainer,
                { autoHide: true, autoHideDelay: 3000 }
            );
        } else {
            ValidationDisplay.showToast(
                result.message || 'Form submitted successfully',
                { type: 'success' }
            );
        }

        // Reset form
        this.form.reset();

        // Call success callback
        if (this.options.onSuccess) {
            this.options.onSuccess(result);
        }
    }

    /**
     * Handle submission error
     * @param {object} result
     */
    handleError(result) {
        const errors = result.errors || [result.error || 'An error occurred'];

        this.displayErrors({ valid: false, errors });

        // Call error callback
        if (this.options.onError) {
            this.options.onError(result);
        }
    }

    /**
     * Set loading state
     * @param {boolean} loading
     */
    setLoading(loading) {
        const submitBtn = this.form.querySelector('[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = loading;
            submitBtn.textContent = loading ? 'Submitting...' : 'Submit';
        }
        this.isSubmitting = loading;
    }

    /**
     * Reset form and clear errors
     */
    reset() {
        this.form.reset();
        this.clearErrors();
    }

    /**
     * Destroy form validator
     */
    destroy() {
        // Remove event listeners would go here
        // For simplicity, we'll just clear errors
        this.clearErrors();
    }
}

/**
 * Quick form validation helper
 * @param {string|HTMLFormElement} form
 * @param {string} entityType
 * @param {function} onSubmit
 * @param {object} options
 * @returns {FormValidator}
 */
function validateForm(form, entityType, onSubmit, options = {}) {
    return new FormValidator(form, {
        entityType,
        onSubmit,
        ...options
    });
}

/**
 * Validate and submit via API
 * @param {string|HTMLFormElement} form
 * @param {string} entityType
 * @param {string} endpoint
 * @param {string} method
 * @param {object} options
 * @returns {FormValidator}
 */
function validateAndSubmitToAPI(form, entityType, endpoint, method = 'POST', options = {}) {
    const apiClientInstance = options.apiClient || (typeof apiClient !== 'undefined' ? apiClient : null);
    
    if (!apiClientInstance) {
        console.error('API client not available');
        return null;
    }

    return new FormValidator(form, {
        entityType,
        onSubmit: async (data) => {
            return await apiClientInstance.request(method, endpoint, data);
        },
        ...options
    });
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FormValidator, validateForm, validateAndSubmitToAPI };
}

console.log(' Form Validation integration loaded successfully');
