/**
 * Utility Functions
 * Common utility functions used throughout the application
 * @module core/utils
 */

/**
 * Convert value to number, handling null/undefined and string formats
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
 * Format date to localized string
 * @param {string|Date} dateStr - Date to format
 * @returns {string} Formatted date string
 */
export function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {year: 'numeric', month: 'short', day: 'numeric'});
}

/**
 * Show notification popup
 * @param {string} message - Notification message
 * @param {string} type - Type of notification (info, success, error, warning)
 */
export function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        padding: 1rem 1.5rem;
        background-color: ${type === 'success' ? 'var(--accent-success)' : type === 'info' ? 'var(--accent-primary)' : type === 'warning' ? 'var(--accent-warning)' : 'var(--accent-danger)'};
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
