/**
 * Main Entry Point for Vessel Scheduler JavaScript Application
 * This file loads all required modules and initializes the application
 */

// Load core files in correct order
(function() {
    'use strict';
    
    console.log(' Initializing Vessel Scheduler Application...');
    
    // Configuration
    const config = {
        version: '3.1.0',
        modules: {
            variables: 'js/variables.js',
            validation: 'js/api-validation.js',
            documentation: 'js/api-documentation-generator.js'
        },
        requiredLibraries: [
            { name: 'XLSX', url: 'https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js', required: true },
            { name: 'html2pdf', url: 'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js', required: false },
            { name: 'vis', url: 'https://unpkg.com/vis-network/standalone/umd/vis-network.min.js', required: false }
        ]
    };
    
    // Check for required libraries
    function checkLibraries() {
        const missing = [];
        const warnings = [];
        
        config.requiredLibraries.forEach(lib => {
            if (typeof window[lib.name] === 'undefined') {
                if (lib.required) {
                    missing.push(lib);
                } else {
                    warnings.push(lib);
                }
            }
        });
        
        if (missing.length > 0) {
            console.error(' Missing required libraries:');
            missing.forEach(lib => {
                console.error(`   - ${lib.name}: ${lib.url}`);
            });
            
            // Show user warning
            if (document.body) {
                const warning = document.createElement('div');
                warning.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    background: #c00;
                    color: white;
                    padding: 1rem;
                    text-align: center;
                    z-index: 99999;
                    font-weight: bold;
                `;
                warning.innerHTML = `
                     Missing Required Libraries! Please include:<br>
                    ${missing.map(lib => lib.name).join(', ')}
                `;
                document.body.insertBefore(warning, document.body.firstChild);
            }
        }
        
        if (warnings.length > 0) {
            console.warn(' Optional libraries not loaded (some features may be unavailable):');
            warnings.forEach(lib => {
                console.warn(`   - ${lib.name} (${lib.url})`);
            });
        }
        
        if (missing.length === 0 && warnings.length === 0) {
            console.log(' All libraries loaded successfully');
        }
        
        return missing.length === 0;
    }
    
    // Initialize application
    function initializeApp() {
        console.log(` Vessel Scheduler v${config.version}`);
        
        // Check libraries
        if (!checkLibraries()) {
            console.error(' Application initialization failed: missing required libraries');
            return;
        }
        
        // Display loaded modules
        console.log(' Loaded modules:');
        console.log('   - Variables & Constants');
        console.log('   - API Validation');
        console.log('   - API Documentation Generator');
        
        // Global utilities
        window.vesselScheduler = {
            version: config.version,
            validator: window.apiValidator,
            docs: window.vesselSchedulerAPIDocs,
            
            // Utility functions
            generateDocs() {
                if (window.vesselSchedulerAPIDocs) {
                    window.vesselSchedulerAPIDocs.downloadHTML();
                } else {
                    console.error('Documentation generator not loaded');
                }
            },
            
            generateMarkdownDocs() {
                if (window.vesselSchedulerAPIDocs) {
                    window.vesselSchedulerAPIDocs.downloadMarkdown();
                } else {
                    console.error('Documentation generator not loaded');
                }
            },
            
            validateEntity(type, data) {
                if (window.apiValidator) {
                    return window.apiValidator.validateAndSanitize(type, data);
                } else {
                    console.error('Validator not loaded');
                    return { valid: false, errors: ['Validator not loaded'] };
                }
            },
            
            // Info display
            info() {
                console.log(`
═══════════════════════════════════════════════
    Vessel Scheduler v${config.version}
═══════════════════════════════════════════════

Available Commands:
  vesselScheduler.generateDocs()         - Download HTML documentation
  vesselScheduler.generateMarkdownDocs() - Download Markdown documentation
  vesselScheduler.validateEntity(type, data) - Validate entity data
  vesselScheduler.info()                 - Show this info

Loaded Modules:
   Variables & Constants
   API Validation
   API Documentation Generator
  ${typeof XLSX !== 'undefined' ? '' : ''} XLSX (Excel Export)
  ${typeof html2pdf !== 'undefined' ? '' : ''} html2pdf (PDF Export)
  ${typeof vis !== 'undefined' ? '' : ''} vis-network (Network Visualization)

Documentation:
  See docs/JAVASCRIPT_MODERNIZATION_PLAN.md for migration roadmap

═══════════════════════════════════════════════
                `);
            }
        };
        
        console.log(' Application initialized successfully');
        console.log(' Type `vesselScheduler.info()` in console for help');
        
        // Dispatch ready event
        document.dispatchEvent(new CustomEvent('vesselSchedulerReady', {
            detail: { version: config.version }
        }));
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeApp);
    } else {
        initializeApp();
    }
    
})();
