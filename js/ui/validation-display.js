/**
 * Validation Error Display Components
 * Provides UI components for displaying validation errors
 */

class ValidationDisplay {
    /**
     * Display validation errors in a container
     * @param {array} errors - Array of error messages
     * @param {string|HTMLElement} container - Container element or ID
     * @param {object} options - Display options
     */
    static displayErrors(errors, container, options = {}) {
        const containerEl = typeof container === 'string' 
            ? document.getElementById(container) || document.querySelector(container)
            : container;

        if (!containerEl) {
            console.error('Validation error container not found');
            return;
        }

        // Clear container if no errors
        if (!errors || errors.length === 0) {
            containerEl.innerHTML = '';
            containerEl.style.display = 'none';
            containerEl.classList.remove('has-errors');
            return;
        }

        const {
            title = 'Validation Errors',
            type = 'error', // error, warning, info
            dismissible = true,
            autoHide = false,
            autoHideDelay = 5000,
            showIcon = true,
            animate = true
        } = options;

        // Create error HTML
        const errorHTML = this.createErrorHTML(errors, {
            title,
            type,
            dismissible,
            showIcon
        });

        containerEl.innerHTML = errorHTML;
        containerEl.style.display = 'block';
        containerEl.classList.add('has-errors');

        // Add animation
        if (animate) {
            containerEl.classList.add('fade-in');
        }

        // Add dismiss functionality
        if (dismissible) {
            const dismissBtn = containerEl.querySelector('.validation-dismiss');
            if (dismissBtn) {
                dismissBtn.addEventListener('click', () => {
                    this.hideErrors(containerEl, animate);
                });
            }
        }

        // Auto hide
        if (autoHide) {
            setTimeout(() => {
                this.hideErrors(containerEl, animate);
            }, autoHideDelay);
        }

        // Scroll to errors
        containerEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Create error HTML
     * @param {array} errors
     * @param {object} options
     * @returns {string}
     */
    static createErrorHTML(errors, options) {
        const { title, type, dismissible, showIcon } = options;

        const iconMap = {
            error: '',
            warning: '',
            info: 'ℹ',
            success: ''
        };

        const colorMap = {
            error: {
                bg: '#fee',
                border: '#fcc',
                text: '#c00',
                icon: '#d00'
            },
            warning: {
                bg: '#fff4e5',
                border: '#ffe0b2',
                text: '#f57c00',
                icon: '#ff9800'
            },
            info: {
                bg: '#e3f2fd',
                border: '#bbdefb',
                text: '#1976d2',
                icon: '#2196f3'
            },
            success: {
                bg: '#e8f5e9',
                border: '#c8e6c9',
                text: '#388e3c',
                icon: '#4caf50'
            }
        };

        const colors = colorMap[type] || colorMap.error;
        const icon = iconMap[type] || iconMap.error;

        return `
            <div class="validation-alert validation-${type}" 
                 style="background: ${colors.bg}; 
                        border: 1px solid ${colors.border}; 
                        border-radius: 4px; 
                        padding: 1rem; 
                        margin: 1rem 0;
                        position: relative;">
                ${dismissible ? `
                    <button class="validation-dismiss" 
                            style="position: absolute; 
                                   top: 0.5rem; 
                                   right: 0.5rem; 
                                   background: none; 
                                   border: none; 
                                   cursor: pointer;
                                   font-size: 1.2rem;
                                   color: ${colors.text};
                                   opacity: 0.7;
                                   transition: opacity 0.2s;"
                            onmouseover="this.style.opacity='1'"
                            onmouseout="this.style.opacity='0.7'">×</button>
                ` : ''}
                
                <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
                    ${showIcon ? `
                        <span class="validation-icon" 
                              style="font-size: 1.5rem; 
                                     flex-shrink: 0;
                                     color: ${colors.icon};">${icon}</span>
                    ` : ''}
                    
                    <div style="flex: 1;">
                        <h4 class="validation-title" 
                            style="margin: 0 0 0.5rem 0; 
                                   color: ${colors.text};
                                   font-size: 1rem;
                                   font-weight: 600;">${title}</h4>
                        
                        <ul class="validation-errors" 
                            style="margin: 0; 
                                   padding-left: 1.25rem;
                                   color: ${colors.text};">
                            ${errors.map(error => `
                                <li style="margin: 0.25rem 0;">${this.escapeHTML(error)}</li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Hide errors with animation
     * @param {HTMLElement} container
     * @param {boolean} animate
     */
    static hideErrors(container, animate = true) {
        if (animate) {
            container.classList.add('fade-out');
            setTimeout(() => {
                container.innerHTML = '';
                container.style.display = 'none';
                container.classList.remove('has-errors', 'fade-out', 'fade-in');
            }, 300);
        } else {
            container.innerHTML = '';
            container.style.display = 'none';
            container.classList.remove('has-errors');
        }
    }

    /**
     * Display inline field errors
     * @param {string} fieldId - Field element ID
     * @param {string} error - Error message
     * @param {object} options - Display options
     */
    static displayFieldError(fieldId, error, options = {}) {
        const field = document.getElementById(fieldId) || document.querySelector(fieldId);
        if (!field) {
            console.error(`Field ${fieldId} not found`);
            return;
        }

        const {
            position = 'after', // before, after, replace
            className = 'field-error',
            style = 'text'
        } = options;

        // Remove existing error
        this.clearFieldError(fieldId);

        if (!error) return;

        // Add error class to field
        field.classList.add('has-error', 'is-invalid');

        // Create error element
        const errorEl = document.createElement('div');
        errorEl.className = `${className} validation-field-error`;
        errorEl.setAttribute('data-field', fieldId);
        
        if (style === 'tooltip') {
            errorEl.innerHTML = `
                <span class="error-tooltip" 
                      style="display: block;
                             color: #d32f2f;
                             font-size: 0.875rem;
                             margin-top: 0.25rem;
                             padding: 0.25rem 0.5rem;
                             background: #ffebee;
                             border-left: 3px solid #d32f2f;
                             border-radius: 2px;">
                    ${this.escapeHTML(error)}
                </span>
            `;
        } else {
            errorEl.innerHTML = `
                <span style="display: block;
                             color: #d32f2f;
                             font-size: 0.875rem;
                             margin-top: 0.25rem;">
                    ${this.escapeHTML(error)}
                </span>
            `;
        }

        // Insert error element
        if (position === 'after') {
            field.parentNode.insertBefore(errorEl, field.nextSibling);
        } else if (position === 'before') {
            field.parentNode.insertBefore(errorEl, field);
        }

        // Add border color to field
        field.style.borderColor = '#d32f2f';
    }

    /**
     * Clear field error
     * @param {string} fieldId - Field element ID
     */
    static clearFieldError(fieldId) {
        const field = document.getElementById(fieldId) || document.querySelector(fieldId);
        if (!field) return;

        // Remove error classes
        field.classList.remove('has-error', 'is-invalid');
        field.style.borderColor = '';

        // Remove error elements
        const errorEls = document.querySelectorAll(`[data-field="${fieldId}"]`);
        errorEls.forEach(el => el.remove());
    }

    /**
     * Display field errors from validation result
     * @param {object} validationResult - Validation result object
     * @param {object} fieldMapping - Map of field names to element IDs
     */
    static displayFieldErrors(validationResult, fieldMapping = {}) {
        if (!validationResult || !validationResult.errors) return;

        // Clear all existing errors first
        Object.values(fieldMapping).forEach(fieldId => {
            this.clearFieldError(fieldId);
        });

        // Display new errors
        validationResult.errors.forEach(error => {
            // Try to extract field name from error message
            const match = error.match(/Field '(\w+)'/);
            if (match) {
                const fieldName = match[1];
                const fieldId = fieldMapping[fieldName];
                if (fieldId) {
                    this.displayFieldError(fieldId, error);
                }
            }
        });
    }

    /**
     * Display success message
     * @param {string} message
     * @param {string|HTMLElement} container
     * @param {object} options
     */
    static displaySuccess(message, container, options = {}) {
        this.displayErrors([message], container, {
            title: 'Success',
            type: 'success',
            ...options
        });
    }

    /**
     * Display warning message
     * @param {string|array} warnings
     * @param {string|HTMLElement} container
     * @param {object} options
     */
    static displayWarning(warnings, container, options = {}) {
        const warningArray = Array.isArray(warnings) ? warnings : [warnings];
        this.displayErrors(warningArray, container, {
            title: 'Warning',
            type: 'warning',
            ...options
        });
    }

    /**
     * Display info message
     * @param {string|array} info
     * @param {string|HTMLElement} container
     * @param {object} options
     */
    static displayInfo(info, container, options = {}) {
        const infoArray = Array.isArray(info) ? info : [info];
        this.displayErrors(infoArray, container, {
            title: 'Information',
            type: 'info',
            ...options
        });
    }

    /**
     * Create toast notification
     * @param {string} message
     * @param {object} options
     */
    static showToast(message, options = {}) {
        const {
            type = 'info',
            duration = 3000,
            position = 'top-right' // top-right, top-left, bottom-right, bottom-left, top-center, bottom-center
        } = options;

        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            
            const positionStyles = {
                'top-right': 'top: 1rem; right: 1rem;',
                'top-left': 'top: 1rem; left: 1rem;',
                'bottom-right': 'bottom: 1rem; right: 1rem;',
                'bottom-left': 'bottom: 1rem; left: 1rem;',
                'top-center': 'top: 1rem; left: 50%; transform: translateX(-50%);',
                'bottom-center': 'bottom: 1rem; left: 50%; transform: translateX(-50%);'
            };
            
            toastContainer.style.cssText = `
                position: fixed;
                ${positionStyles[position]}
                z-index: 10000;
                max-width: 400px;
            `;
            document.body.appendChild(toastContainer);
        }

        // Create toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const iconMap = {
            error: '',
            warning: '',
            info: 'ℹ',
            success: ''
        };

        const colorMap = {
            error: { bg: '#d32f2f', text: '#fff' },
            warning: { bg: '#f57c00', text: '#fff' },
            info: { bg: '#1976d2', text: '#fff' },
            success: { bg: '#388e3c', text: '#fff' }
        };

        const colors = colorMap[type] || colorMap.info;
        const icon = iconMap[type] || iconMap.info;

        toast.innerHTML = `
            <div style="display: flex; 
                        align-items: center; 
                        gap: 0.75rem; 
                        background: ${colors.bg}; 
                        color: ${colors.text};
                        padding: 0.75rem 1rem;
                        border-radius: 4px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                        margin-bottom: 0.5rem;
                        animation: slideIn 0.3s ease-out;">
                <span style="font-size: 1.25rem;">${icon}</span>
                <span style="flex: 1;">${this.escapeHTML(message)}</span>
                <button onclick="this.parentElement.parentElement.remove()"
                        style="background: none;
                               border: none;
                               color: ${colors.text};
                               cursor: pointer;
                               font-size: 1.25rem;
                               opacity: 0.8;
                               padding: 0;
                               line-height: 1;">×</button>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text
     * @returns {string}
     */
    static escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Install CSS animations
     */
    static installCSS() {
        if (document.getElementById('validation-display-css')) return;

        const style = document.createElement('style');
        style.id = 'validation-display-css';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }

            .fade-in {
                animation: fadeIn 0.3s ease-in;
            }

            .fade-out {
                animation: fadeOut 0.3s ease-out;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            @keyframes fadeOut {
                from { opacity: 1; transform: translateY(0); }
                to { opacity: 0; transform: translateY(-10px); }
            }
        `;
        document.head.appendChild(style);
    }
}

// Install CSS on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ValidationDisplay.installCSS());
} else {
    ValidationDisplay.installCSS();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ValidationDisplay };
}

console.log(' Validation Display components loaded successfully');
