/**
 * Core Utility Functions
 * Extracted from vessel_scheduler_enhanced.js
 */

/**
 * Convert value to number safely
 * @param {*} v - Value to convert
 * @returns {number} Converted number or 0
 */
export function toNumber(v) {
    if (v === null || v === undefined) return 0;
    const s = String(v).trim();
    if (!s) return 0;
    const n = Number(s.replace(',', '.'));
    return Number.isFinite(n) ? n : 0;
}

/**
 * Format date to Russian locale
 * @param {string|Date} dateStr - Date to format
 * @returns {string} Formatted date string
 */
export function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Show notification toast
 * @param {string} message - Message to display
 * @param {'info'|'success'|'error'|'warning'} type - Notification type
 */
export function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        padding: 1rem 1.5rem;
        background-color: ${type === 'success' ? 'var(--accent-success)' : 
                           type === 'info' ? 'var(--accent-primary)' : 
                           type === 'warning' ? 'var(--accent-warning)' :
                           'var(--accent-danger)'};
        color: white;
        border-radius: 6px;
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
        font-weight: 500;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Update CSS variables from config
 * @param {Object} colors - Color configuration object
 */
export function updateCSSVariables(colors) {
    const root = document.documentElement;
    
    // Add # if missing
    const fmt = (c) => c && c.startsWith('#') ? c : '#' + c;

    if (colors.loading) root.style.setProperty('--operation-loading', fmt(colors.loading));
    if (colors.discharge) root.style.setProperty('--operation-discharge', fmt(colors.discharge));
    if (colors.sea_laden) root.style.setProperty('--operation-transit', fmt(colors.sea_laden));
    if (colors.sea_ballast) root.style.setProperty('--operation-ballast', fmt(colors.sea_ballast));
    if (colors.canal) root.style.setProperty('--operation-canal', fmt(colors.canal));
    if (colors.bunker) root.style.setProperty('--operation-bunker', fmt(colors.bunker));
    if (colors.waiting) root.style.setProperty('--operation-waiting', fmt(colors.waiting));
}
