/**
 * Internationalization (i18n) Service
 * Provides bilingual support for English and Russian
 * @module services/i18n-service
 */

// Translation dictionaries
const translations = {
    en: {
        // Common UI elements
        'app.title': 'Vessel Scheduling System',
        'app.save': 'Save',
        'app.cancel': 'Cancel',
        'app.delete': 'Delete',
        'app.edit': 'Edit',
        'app.add': 'Add',
        'app.close': 'Close',
        'app.confirm': 'Confirm',
        'app.loading': 'Loading...',
        'app.error': 'Error',
        'app.success': 'Success',
        'app.warning': 'Warning',
        'app.info': 'Information',
        
        // Navigation
        'nav.dashboard': 'Dashboard',
        'nav.vessels': 'Vessels',
        'nav.cargo': 'Cargo',
        'nav.routes': 'Routes',
        'nav.schedule': 'Schedule',
        'nav.reports': 'Reports',
        'nav.settings': 'Settings',
        
        // Vessel management
        'vessel.list': 'Vessel List',
        'vessel.add': 'Add Vessel',
        'vessel.edit': 'Edit Vessel',
        'vessel.delete': 'Delete Vessel',
        'vessel.name': 'Vessel Name',
        'vessel.type': 'Type',
        'vessel.dwt': 'Deadweight (DWT)',
        'vessel.speed': 'Speed (knots)',
        'vessel.consumption': 'Fuel Consumption',
        
        // Cargo management
        'cargo.list': 'Cargo List',
        'cargo.add': 'Add Cargo',
        'cargo.edit': 'Edit Cargo',
        'cargo.commodity': 'Commodity',
        'cargo.quantity': 'Quantity (MT)',
        'cargo.loadPort': 'Load Port',
        'cargo.dischargePort': 'Discharge Port',
        'cargo.laycanStart': 'Laycan Start',
        'cargo.laycanEnd': 'Laycan End',
        'cargo.freight': 'Freight Rate',
        'cargo.status': 'Status',
        
        // Schedule
        'schedule.generate': 'Generate Schedule',
        'schedule.gantt': 'Gantt Chart',
        'schedule.export': 'Export to Excel',
        'schedule.timeline': 'Timeline Days',
        'schedule.filter': 'Voyage Filter',
        'schedule.refresh': 'Refresh',
        
        // Calendar/Operations
        'calendar.title': 'Operational Calendar',
        'calendar.subtitle': 'Year Schedule & Vessel Planning',
        'calendar.today': 'Today',
        'calendar.week': 'Week',
        'calendar.month': 'Month',
        'calendar.year': 'Year',
        'calendar.timeline': 'Timeline',
        'calendar.addEvent': 'Add Event',
        'calendar.editEvent': 'Edit Event',
        'calendar.deleteEvent': 'Delete Event',
        
        // Common actions
        'app.export': 'Export',
        'app.refresh': 'Refresh',
        
        // Reports
        'report.voyageSummary': 'Voyage Summary',
        'report.financial': 'Financial Report',
        'report.fleetUtilization': 'Fleet Utilization',
        'report.berthUtilization': 'Berth Utilization',
        'report.download': 'Download Report',
        
        // Notifications
        'notify.saveSuccess': 'Data saved successfully',
        'notify.saveError': 'Error saving data',
        'notify.deleteSuccess': 'Deleted successfully',
        'notify.deleteError': 'Error deleting',
        'notify.loadError': 'Error loading data',
        'notify.validationError': 'Please check your input',
        
        // Confirmation dialogs
        'confirm.delete': 'Are you sure you want to delete this item?',
        'confirm.unsavedChanges': 'You have unsaved changes. Do you want to leave?',
        'confirm.clearData': 'This will clear all data. Are you sure?',
        
        // Status
        'status.pending': 'Pending',
        'status.assigned': 'Assigned',
        'status.inProgress': 'In Progress',
        'status.completed': 'Completed',
        'status.cancelled': 'Cancelled',
        
        // Gantt operations
        'gantt.loading': 'Loading',
        'gantt.discharge': 'Discharge',
        'gantt.transit': 'Transit',
        'gantt.ballast': 'Ballast',
        'gantt.canal': 'Canal',
        'gantt.bunker': 'Bunker',
        
        // Language selector
        'lang.select': 'Select Language',
        'lang.english': 'English',
        'lang.russian': 'Русский'
    },
    
    ru: {
        // Common UI elements
        'app.title': 'Система планирования судов',
        'app.save': 'Сохранить',
        'app.cancel': 'Отмена',
        'app.delete': 'Удалить',
        'app.edit': 'Редактировать',
        'app.add': 'Добавить',
        'app.close': 'Закрыть',
        'app.confirm': 'Подтвердить',
        'app.loading': 'Загрузка...',
        'app.error': 'Ошибка',
        'app.success': 'Успешно',
        'app.warning': 'Предупреждение',
        'app.info': 'Информация',
        
        // Navigation
        'nav.dashboard': 'Панель управления',
        'nav.vessels': 'Суда',
        'nav.cargo': 'Грузы',
        'nav.routes': 'Маршруты',
        'nav.schedule': 'Расписание',
        'nav.reports': 'Отчеты',
        'nav.settings': 'Настройки',
        
        // Vessel management
        'vessel.list': 'Список судов',
        'vessel.add': 'Добавить судно',
        'vessel.edit': 'Редактировать судно',
        'vessel.delete': 'Удалить судно',
        'vessel.name': 'Название судна',
        'vessel.type': 'Тип',
        'vessel.dwt': 'Дедвейт (DWT)',
        'vessel.speed': 'Скорость (узлы)',
        'vessel.consumption': 'Расход топлива',
        
        // Cargo management
        'cargo.list': 'Список грузов',
        'cargo.add': 'Добавить груз',
        'cargo.edit': 'Редактировать груз',
        'cargo.commodity': 'Товар',
        'cargo.quantity': 'Количество (МТ)',
        'cargo.loadPort': 'Порт погрузки',
        'cargo.dischargePort': 'Порт выгрузки',
        'cargo.laycanStart': 'Начало лейкана',
        'cargo.laycanEnd': 'Конец лейкана',
        'cargo.freight': 'Фрахтовая ставка',
        'cargo.status': 'Статус',
        
        // Schedule
        'schedule.generate': 'Сгенерировать расписание',
        'schedule.gantt': 'График Ганта',
        'schedule.export': 'Экспорт в Excel',
        'schedule.timeline': 'Период (дни)',
        'schedule.filter': 'Фильтр рейсов',
        'schedule.refresh': 'Обновить',
        
        // Calendar/Operations
        'calendar.title': 'Операционный календарь',
        'calendar.subtitle': 'Годовое расписание и планирование судов',
        'calendar.today': 'Сегодня',
        'calendar.week': 'Неделя',
        'calendar.month': 'Месяц',
        'calendar.year': 'Год',
        'calendar.timeline': 'Хронология',
        'calendar.addEvent': 'Добавить событие',
        'calendar.editEvent': 'Редактировать событие',
        'calendar.deleteEvent': 'Удалить событие',
        
        // Common actions
        'app.export': 'Экспорт',
        'app.refresh': 'Обновить',
        
        // Reports
        'report.voyageSummary': 'Сводка по рейсам',
        'report.financial': 'Финансовый отчет',
        'report.fleetUtilization': 'Загрузка флота',
        'report.berthUtilization': 'Загрузка причалов',
        'report.download': 'Скачать отчет',
        
        // Notifications
        'notify.saveSuccess': 'Данные успешно сохранены',
        'notify.saveError': 'Ошибка сохранения данных',
        'notify.deleteSuccess': 'Успешно удалено',
        'notify.deleteError': 'Ошибка удаления',
        'notify.loadError': 'Ошибка загрузки данных',
        'notify.validationError': 'Проверьте правильность ввода',
        
        // Confirmation dialogs
        'confirm.delete': 'Вы уверены, что хотите удалить этот элемент?',
        'confirm.unsavedChanges': 'У вас есть несохраненные изменения. Выйти?',
        'confirm.clearData': 'Это удалит все данные. Вы уверены?',
        
        // Status
        'status.pending': 'Ожидает',
        'status.assigned': 'Назначен',
        'status.inProgress': 'В процессе',
        'status.completed': 'Завершен',
        'status.cancelled': 'Отменен',
        
        // Gantt operations
        'gantt.loading': 'Погрузка',
        'gantt.discharge': 'Выгрузка',
        'gantt.transit': 'Транзит',
        'gantt.ballast': 'Балласт',
        'gantt.canal': 'Канал',
        'gantt.bunker': 'Бункеровка',
        
        // Language selector
        'lang.select': 'Выберите язык',
        'lang.english': 'English',
        'lang.russian': 'Русский'
    }
};

/**
 * i18n Service class
 */
class I18nService {
    constructor() {
        this.currentLanguage = this.loadLanguagePreference();
        this.listeners = [];
    }
    
    /**
     * Load language preference from localStorage
     * @returns {string} Language code ('en' or 'ru')
     */
    loadLanguagePreference() {
        try {
            const saved = localStorage.getItem('app_language');
            return (saved === 'en' || saved === 'ru') ? saved : 'en';
        } catch (e) {
            console.warn('Cannot access localStorage for language preference:', e);
            return 'en';
        }
    }
    
    /**
     * Save language preference to localStorage
     * @param {string} lang - Language code
     */
    saveLanguagePreference(lang) {
        try {
            localStorage.setItem('app_language', lang);
        } catch (e) {
            console.warn('Cannot save language preference to localStorage:', e);
        }
    }
    
    /**
     * Get current language
     * @returns {string} Current language code
     */
    getLanguage() {
        return this.currentLanguage;
    }
    
    /**
     * Set current language
     * @param {string} lang - Language code ('en' or 'ru')
     */
    setLanguage(lang) {
        if (lang !== 'en' && lang !== 'ru') {
            console.warn(`Unsupported language: ${lang}. Using English.`);
            lang = 'en';
        }
        
        this.currentLanguage = lang;
        this.saveLanguagePreference(lang);
        this.notifyListeners();
    }
    
    /**
     * Translate a key to current language
     * @param {string} key - Translation key
     * @param {object} params - Optional parameters for interpolation
     * @returns {string} Translated text
     */
    t(key, params = {}) {
        const langDict = translations[this.currentLanguage];
        let text = langDict[key] || translations.en[key] || key;
        
        // Simple parameter interpolation
        Object.keys(params).forEach(param => {
            text = text.replace(`{${param}}`, params[param]);
        });
        
        return text;
    }
    
    /**
     * Add language change listener
     * @param {Function} callback - Function to call when language changes
     */
    onLanguageChange(callback) {
        this.listeners.push(callback);
    }
    
    /**
     * Remove language change listener
     * @param {Function} callback - Function to remove
     */
    offLanguageChange(callback) {
        this.listeners = this.listeners.filter(cb => cb !== callback);
    }
    
    /**
     * Notify all listeners of language change
     */
    notifyListeners() {
        this.listeners.forEach(callback => {
            try {
                callback(this.currentLanguage);
            } catch (e) {
                console.error('Error in language change listener:', e);
            }
        });
    }
    
    /**
     * Update all elements with data-i18n attribute
     */
    updateDOM() {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            const attr = el.getAttribute('data-i18n-attr');
            
            if (attr) {
                // Update specified attribute
                el.setAttribute(attr, this.t(key));
            } else {
                // Update text content
                el.textContent = this.t(key);
            }
        });
    }
    
    /**
     * Create a language toggle button
     * @param {HTMLElement} container - Container to append button to
     * @returns {HTMLElement} The created button
     */
    createLanguageToggle(container) {
        const button = document.createElement('button');
        button.className = 'language-toggle-btn';
        button.innerHTML = `
            <span class="flag">${this.currentLanguage === 'en' ? '' : ''}</span>
            <span class="lang-code">${this.currentLanguage.toUpperCase()}</span>
        `;
        
        button.addEventListener('click', () => {
            const newLang = this.currentLanguage === 'en' ? 'ru' : 'en';
            this.setLanguage(newLang);
            button.innerHTML = `
                <span class="flag">${newLang === 'en' ? '' : ''}</span>
                <span class="lang-code">${newLang.toUpperCase()}</span>
            `;
            this.updateDOM();
        });
        
        if (container) {
            container.appendChild(button);
        }
        
        return button;
    }
    
    /**
     * Get all available languages
     * @returns {Array} Array of language objects
     */
    getAvailableLanguages() {
        return [
            { code: 'en', name: 'English', flag: '' },
            { code: 'ru', name: 'Русский', flag: '' }
        ];
    }
}

// Create singleton instance
const i18nService = new I18nService();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { i18nService, I18nService };
}

// Global access for HTML inline scripts
if (typeof window !== 'undefined') {
    window.i18n = i18nService;
    window.t = (key, params) => i18nService.t(key, params);
}

/**
 * Initialize i18n on DOM load
 */
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        i18nService.updateDOM();
    });
}
