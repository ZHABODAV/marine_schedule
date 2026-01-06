/**
 * Local Storage Service
 * Handles saving and loading application state from browser localStorage
 * @module services/storage-service
 */

import { appState, tradingLanesState } from '../core/app-state.js';
import { showNotification } from '../core/utils.js';

/**
 * Save application state to localStorage
 */
export function saveToLocalStorage() {
    // Create comprehensive storage object including trading lanes
    const storageData = {
        ...appState,
        tradingLanes: {
            lanes: tradingLanesState.lanes,
            assignmentsArray: Array.from(tradingLanesState.assignments.entries())
        },
        sessionInfo: {
            lastSaved: new Date().toISOString(),
            version: '3.0.0'
        }
    };
    
    try {
        localStorage.setItem('vesselSchedulerDataEnhanced', JSON.stringify(storageData));
        console.log('Session saved successfully:', new Date().toISOString());
        updateSessionInfo(); // Update the session info display
    } catch (error) {
        console.error('Error saving to localStorage:', error);
        showNotification('Ошибка сохранения сессии', 'error');
    }
}

/**
 * Load application state from localStorage
 * @returns {boolean} True if data was loaded successfully
 */
export function loadFromLocalStorage() {
    const data = localStorage.getItem('vesselSchedulerDataEnhanced');
    if (!data) return false;

    try {
        const loaded = JSON.parse(data);
        
        // Keep object identity; overwrite keys
        appState.currentModule = loaded.currentModule || 'deepsea';
        appState.deepsea = loaded.deepsea || appState.deepsea;
        appState.balakovo = loaded.balakovo || appState.balakovo;
        appState.olya = loaded.olya || appState.olya;
        appState.filters = loaded.filters || appState.filters;
        appState.voyageBuilder = loaded.voyageBuilder || appState.voyageBuilder;
        appState.portStocks = loaded.portStocks || {};
        appState.salesPlan = loaded.salesPlan || appState.salesPlan;

        // Load trading lanes state
        if (loaded.tradingLanes) {
            tradingLanesState.lanes = loaded.tradingLanes.lanes || [];
            tradingLanesState.assignments = new Map(loaded.tradingLanes.assignmentsArray || []);
        }

        return true;
    } catch (e) {
        console.error('Failed to load local storage state', e);
        return false;
    }
}

/**
 * Update session info display
 */
export function updateSessionInfo() {
    const sessionInfoEl = document.getElementById('sessionInfo');
    if (!sessionInfoEl) return;
    
    const saved = localStorage.getItem('vesselSchedulerDataEnhanced');
    if (!saved) {
        sessionInfoEl.innerHTML = ' Нет сохраненной сессии';
        return;
    }
    
    try {
        const data = JSON.parse(saved);
        const lastSaved = data.sessionInfo?.lastSaved;
        
        if (lastSaved) {
            const savedDate = new Date(lastSaved);
            const now = new Date();
            const diffMinutes = Math.floor((now - savedDate) / (1000 * 60));
            
            let timeText = '';
            if (diffMinutes < 1) {
                timeText = 'только что';
            } else if (diffMinutes < 60) {
                timeText = `${diffMinutes} мин. назад`;
            } else if (diffMinutes < 1440) {
                const hours = Math.floor(diffMinutes / 60);
                timeText = `${hours} ч. назад`;
            } else {
                timeText = savedDate.toLocaleDateString('ru-RU');
            }
            
            sessionInfoEl.innerHTML = ` Сессия сохранена: ${timeText} | Модуль: ${data.currentModule || 'deepsea'}`;
        } else {
            sessionInfoEl.innerHTML = ' Сессия сохранена';
        }
    } catch (e) {
        sessionInfoEl.innerHTML = ' Ошибка чтения сессии';
    }
}

/**
 * Save trading lanes to localStorage
 */
export function saveTradingLanesToLocalStorage() {
    // Save trading lanes state with serializable Map
    const tradingLanesData = {
        lanes: tradingLanesState.lanes,
        assignmentsArray: Array.from(tradingLanesState.assignments.entries())
    };
    
    const storageData = JSON.parse(localStorage.getItem('vesselSchedulerDataEnhanced') || '{}');
    storageData.tradingLanes = tradingLanesData;
    localStorage.setItem('vesselSchedulerDataEnhanced', JSON.stringify(storageData));
}

// Auto-save every 30 seconds
setInterval(saveToLocalStorage, 30000);
