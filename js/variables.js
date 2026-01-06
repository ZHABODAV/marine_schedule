/**
 * Global Variables and Constants Definition
 * This file defines all missing variables referenced across the application
 */

// ===== MISSING VARIABLE DECLARATIONS =====

// Global revenue tracker in calculateDeepSeaFinancials()
let totalRevenue = 0;

// Color map for Gantt chart operations
const colorMap = {
    'П': '#92D050',  // Loading (Green)
    'В': '#00B0F0',  // Discharge (Blue)
    'Т': '#FFC000',  // Transit laden (Orange)
    'Б': '#D9D9D9',  // Ballast (Gray)
    'К': '#7030A0',  // Canal (Purple)
    'Ф': '#833C0C',  // Bunker (Brown)
    'О': '#FF0000',  // Waiting (Red)
    'LD': '#92D050', // Loading
    'DS': '#00B0F0', // Discharge
    'UNK': '#666666' // Unknown (Dark Gray)
};

// Voyage planner data object
const data = {
    calculatedLegs: [],
    voyages: [],
    alerts: []
};

// PDF Export fallback check
if (typeof PDFExport === 'undefined') {
    window.PDFExport = class {
        constructor(config = {}) {
            this.config = {
                apiEndpoint: config.apiEndpoint || '/api/export/pdf',
                ...config
            };
        }
        
        async generateReport(reportType, options) {
            console.warn('PDFExport: Using fallback implementation');
            
            if (typeof html2pdf !== 'undefined') {
                return this.generateClientSidePDF(reportType, options);
            }
            
            // Try server-side generation
            try {
                const response = await fetch(this.config.apiEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reportType, options })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${reportType}_${new Date().toISOString().slice(0,10)}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                } else {
                    throw new Error('Server-side PDF generation failed');
                }
            } catch (error) {
                console.error('PDF generation error:', error);
                throw error;
            }
        }
        
        generateClientSidePDF(reportType, options) {
            // Fallback implementation
            alert('PDF generation requires html2pdf library. Please include it in your HTML.');
            return Promise.reject(new Error('html2pdf not available'));
        }
    };
}

// XLSX (SheetJS) fallback check
if (typeof XLSX === 'undefined') {
    window.XLSX = {
        utils: {
            book_new: () => ({ SheetNames: [], Sheets: {} }),
            json_to_sheet: (data) => {
                console.warn('XLSX library not loaded. Excel export unavailable.');
                return {};
            },
            aoa_to_sheet: (data) => {
                console.warn('XLSX library not loaded. Excel export unavailable.');
                return {};
            },
            book_append_sheet: (wb, ws, name) => {
                console.warn('XLSX library not loaded. Excel export unavailable.');
            }
        },
        writeFile: (wb, filename) => {
            alert('Excel export requires SheetJS library. Please include xlsx.full.min.js in your HTML.');
        }
    };
}

// html2pdf fallback check
if (typeof html2pdf === 'undefined') {
    window.html2pdf = function() {
        const api = {
            set: (opt) => api,
            from: (element) => api,
            save: () => {
                alert('PDF export requires html2pdf library. Please include it in your HTML.');
                return Promise.reject(new Error('html2pdf not available'));
            }
        };
        return api;
    };
}

// vis.Network fallback for network visualization
if (typeof vis === 'undefined') {
    window.vis = {
        Network: class {
            constructor(container, data, options) {
                console.warn('vis.Network library not loaded. Network visualization unavailable.');
                if (container) {
                    container.innerHTML = '<div style="padding: 20px; text-align: center; color: #999;">Network visualization requires vis-network library. Please include it in your HTML.</div>';
                }
            }
        }
    };
}

// Helper function to get operation code
function getOpCode(legType, opDetail) {
    if (opDetail) return opDetail.substring(0, 2).toUpperCase();
    if (legType) {
        const typeMap = {
            'loading': 'LD',
            'discharge': 'DS',
            'transit': 'Т',
            'ballast': 'Б',
            'canal': 'К',
            'bunker': 'Ф',
            'waiting': 'О'
        };
        return typeMap[legType.toLowerCase()] || 'UNK';
    }
    return 'UNK';
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        totalRevenue,
        colorMap,
        data,
        getOpCode
    };
}

console.log(' Variables module loaded successfully');
