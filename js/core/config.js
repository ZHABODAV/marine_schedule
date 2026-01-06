/**
 * Application Configuration
 * Handles configuration loading and CSS variable updates
 * @module core/config
 */

import { appConfig } from './app-state.js';

/**
 * Update CSS variables based on configuration
 */
export function updateCSSVariables() {
    const colors = appConfig.gantt.colors;
    const root = document.documentElement;
    
    // Add # if missing
    const fmt = (c) => c.startsWith('#') ? c : '#' + c;

    if (colors.loading) root.style.setProperty('--operation-loading', fmt(colors.loading));
    if (colors.discharge) root.style.setProperty('--operation-discharge', fmt(colors.discharge));
    if (colors.sea_laden) root.style.setProperty('--operation-transit', fmt(colors.sea_laden));
    if (colors.sea_ballast) root.style.setProperty('--operation-ballast', fmt(colors.sea_ballast));
    if (colors.canal) root.style.setProperty('--operation-canal', fmt(colors.canal));
    if (colors.bunker) root.style.setProperty('--operation-bunker', fmt(colors.bunker));
    if (colors.waiting) root.style.setProperty('--operation-waiting', fmt(colors.waiting));
}

/**
 * Load configuration from server
 * @returns {Promise<Object>} Configuration object
 */
export async function loadConfigFromServer() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        if (config && config.gantt) {
            Object.assign(appConfig, config);
            updateCSSVariables();
        }
        
        return config;
    } catch (error) {
        console.warn('Could not load config from server:', error);
        return null;
    }
}
