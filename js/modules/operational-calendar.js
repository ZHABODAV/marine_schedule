/**
 * Operational Calendar Module
 * Interactive year schedule and vessel planning calendar
 */

class OperationalCalendar {
    constructor() {
        this.currentDate = new Date();
        this.viewType = 'month';
        this.selectedModule = 'all';
        this.selectedVessel = 'all';
        this.selectedStatus = 'all';
        this.events = [];
        this.vessels = [];
        this.apiBaseUrl = 'http://localhost:5000/api';
        
        this.init();
    }

    async init() {
        this.cacheElements();
        this.attachEventListeners();
        await this.loadData();
        this.render();
    }

    cacheElements() {
        // Control elements
        this.viewTypeSelect = document.getElementById('viewType');
        this.moduleFilterSelect = document.getElementById('moduleFilter');
        this.vesselFilterSelect = document.getElementById('vesselFilter');
        this.statusFilterSelect = document.getElementById('statusFilter');
        this.searchInput = document.getElementById('searchInput');
        
        // Navigation
        this.currentPeriodEl = document.getElementById('currentPeriod');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.todayBtn = document.getElementById('todayBtn');
        
        // Views
        this.monthView = document.getElementById('monthView');
        this.timelineView = document.getElementById('timelineView');
        this.yearView = document.getElementById('yearView');
        this.calendarGrid = document.getElementById('calendarGrid');
        
        // Stats
        this.totalVoyagesEl = document.getElementById('totalVoyages');
        this.activeVesselsEl = document.getElementById('activeVessels');
        this.totalCargoEl = document.getElementById('totalCargo');
        this.totalCostEl = document.getElementById('totalCost');
        
        // Events list
        this.upcomingEventsEl = document.getElementById('upcomingEvents');
        
        // Modal
        this.modal = document.getElementById('eventModal');
        this.modalTitle = document.getElementById('modalTitle');
        this.modalBody = document.getElementById('modalBody');
        this.modalClose = document.getElementById('modalClose');
        this.closeModalBtn = document.getElementById('closeModalBtn');
        
        // Buttons
        this.exportBtn = document.getElementById('exportBtn');
        this.refreshBtn = document.getElementById('refreshBtn');
        
        // Loading
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }

    attachEventListeners() {
        // View change
        this.viewTypeSelect.addEventListener('change', (e) => {
            this.viewType = e.target.value;
            this.switchView();
        });
        
        // Filters
        this.moduleFilterSelect.addEventListener('change', (e) => {
            this.selectedModule = e.target.value;
            this.render();
        });
        
        this.vesselFilterSelect.addEventListener('change', (e) => {
            this.selectedVessel = e.target.value;
            this.render();
        });
        
        this.statusFilterSelect.addEventListener('change', (e) => {
            this.selectedStatus = e.target.value;
            this.render();
        });
        
        this.searchInput.addEventListener('input', (e) => {
            this.searchQuery = e.target.value.toLowerCase();
            this.render();
        });
        
        // Navigation
        this.prevBtn.addEventListener('click', () => this.navigatePrevious());
        this.nextBtn.addEventListener('click', () => this.navigateNext());
        this.todayBtn.addEventListener('click', () => this.navigateToday());
        
        // Buttons
        this.exportBtn.addEventListener('click', () => this.exportCalendar());
        this.refreshBtn.addEventListener('click', () => this.refresh());
        
        // Modal
        this.modalClose.addEventListener('click', () => this.closeModal());
        this.closeModalBtn.addEventListener('click', () => this.closeModal());
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.closeModal();
        });
    }

    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
    }

    async loadData() {
        this.showLoading();
        try {
            // Load events from unified calendar endpoint
            await this.loadCalendarEvents();
            
            this.populateVesselFilter();
            this.updateStatistics();
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load calendar data');
        } finally {
            this.hideLoading();
        }
    }

    async loadCalendarEvents() {
        try {
            // Use the unified calendar events API
            const filters = {
                module: this.selectedModule !== 'all' ? this.selectedModule : 'all',
                limit: 10000
            };

            let response;
            if (typeof apiClient !== 'undefined' && apiClient.getCalendarEvents) {
                // Use API client if available
                response = await apiClient.getCalendarEvents(filters);
                if (!response.success) {
                    throw new Error(response.error || 'Failed to load events');
                }
                var data = response.data;
            } else {
                // Fallback to direct fetch
                const queryString = new URLSearchParams(filters).toString();
                const fetchResponse = await fetch(`${this.apiBaseUrl}/calendar/events${queryString ? '?' + queryString : ''}`);
                if (!fetchResponse.ok) {
                    throw new Error(`HTTP ${fetchResponse.status}: ${fetchResponse.statusText}`);
                }
                var data = await fetchResponse.json();
            }

            // Transform events to internal format
            this.events = (data.events || []).map(event => ({
                id: event.id,
                title: event.title,
                module: event.module,
                vessel: event.vessel?.name || event.vessel?.id || 'Unknown',
                vesselId: event.vessel?.id,
                vesselClass: event.vessel?.class || event.vessel?.type,
                start: new Date(event.start),
                end: new Date(event.end),
                status: event.status,
                type: event.type,
                cargo: event.cargo,
                quantity: event.quantity_mt || 0,
                cost: 0, // Cost not provided in unified API
                route: event.location ? event.location : (event.from_port && event.to_port ? `${event.from_port} → ${event.to_port}` : ''),
                location: event.location,
                fromPort: event.from_port,
                toPort: event.to_port,
                description: event.description,
                voyageId: event.voyage_id,
                duration: event.duration_hours,
                distance: event.distance_nm,
                speed: event.speed_kn,
                cargoState: event.cargo_state,
                berthId: event.berth_id,
                destination: event.destination,
                remarks: event.remarks,
                details: event
            }));

            console.log(`Loaded ${this.events.length} events from calendar API`);
            
        } catch (error) {
            console.error('Failed to load calendar events:', error);
            // Fallback to old method if unified API fails
            console.warn('Falling back to module-specific endpoints');
            await this.loadDataLegacy();
        }
    }

    async loadDataLegacy() {
        // Legacy loading method as fallback
        await Promise.all([
            this.loadDeepSeaData(),
            this.loadOlyaData(),
            this.loadBalakovoData()
        ]);
    }

    async loadDeepSeaData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/deepsea/voyages/calculated`);
            if (response.ok) {
                const data = await response.json();
                const events = Object.values(data.calculated_voyages || {}).map(voyage => ({
                    id: voyage.voyage_id,
                    title: `${voyage.vessel_id}: ${voyage.cargo_type}`,
                    module: 'deepsea',
                    vessel: voyage.vessel_id,
                    start: new Date(voyage.laycan_start),
                    end: new Date(voyage.laycan_end),
                    status: this.determineStatus(voyage.laycan_start, voyage.laycan_end),
                    cargo: voyage.qty_mt,
                    cost: voyage.total_cost_usd,
                    route: `${voyage.load_port} → ${voyage.discharge_port}`,
                    details: voyage
                }));
                this.events.push(...events);
            }
        } catch (error) {
            console.warn('Deep Sea data not available:', error);
        }
    }

    async loadOlyaData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/olya/voyages`);
            if (response.ok) {
                const data = await response.json();
                const events = (data.voyages || []).map(voyage => ({
                    id: voyage.voyage_id || `OLYA_${Math.random()}`,
                    title: `${voyage.vessel_name}: ${voyage.cargo_name || 'Cargo'}`,
                    module: 'olya',
                    vessel: voyage.vessel_name,
                    start: new Date(voyage.start_date || Date.now()),
                    end: new Date(voyage.end_date || Date.now()),
                    status: 'planned',
                    cargo: voyage.cargo_qty || 0,
                    cost: voyage.total_cost || 0,
                    route: `${voyage.from_port || 'Origin'} → ${voyage.to_port || 'Destination'}`,
                    details: voyage
                }));
                this.events.push(...events);
            }
        } catch (error) {
            console.warn('Olya data not available:', error);
        }
    }

    async loadBalakovoData() {
        // Placeholder for Balakovo data
        console.log('Balakovo data loading (placeholder)');
    }

    determineStatus(startDate, endDate) {
        const now = new Date();
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        if (now < start) return 'planned';
        if (now > end) return 'completed';
        return 'in-progress';
    }

    populateVesselFilter() {
        const uniqueVessels = [...new Set(this.events.map(e => e.vessel))];
        this.vessels = uniqueVessels.sort();
        
        this.vesselFilterSelect.innerHTML = '<option value="all">All Vessels</option>';
        this.vessels.forEach(vessel => {
            const option = document.createElement('option');
            option.value = vessel;
            option.textContent = vessel;
            this.vesselFilterSelect.appendChild(option);
        });
    }

    getFilteredEvents() {
        return this.events.filter(event => {
            // Module filter
            if (this.selectedModule !== 'all' && event.module !== this.selectedModule) {
                return false;
            }
            
            // Vessel filter
            if (this.selectedVessel !== 'all' && event.vessel !== this.selectedVessel) {
                return false;
            }
            
            // Status filter
            if (this.selectedStatus !== 'all' && event.status !== this.selectedStatus) {
                return false;
            }
            
            // Search filter
            if (this.searchQuery) {
                const searchText = `${event.title} ${event.route} ${event.vessel}`.toLowerCase();
                if (!searchText.includes(this.searchQuery)) {
                    return false;
                }
            }
            
            return true;
        });
    }

    updateStatistics() {
        const filteredEvents = this.getFilteredEvents();
        
        this.totalVoyagesEl.textContent = filteredEvents.length;
        this.activeVesselsEl.textContent = [...new Set(filteredEvents.map(e => e.vessel))].length;
        
        const totalCargo = filteredEvents.reduce((sum, e) => sum + (e.cargo || 0), 0);
        this.totalCargoEl.textContent = this.formatNumber(totalCargo);
        
        const totalCost = filteredEvents.reduce((sum, e) => sum + (e.cost || 0), 0);
        this.totalCostEl.textContent = '$' + this.formatNumber(totalCost);
        
        this.renderUpcomingEvents(filteredEvents);
    }

    renderUpcomingEvents(events) {
        const now = new Date();
        const upcoming = events
            .filter(e => e.start > now)
            .sort((a, b) => a.start - b.start)
            .slice(0, 10);
        
        this.upcomingEventsEl.innerHTML = '';
        
        if (upcoming.length === 0) {
            this.upcomingEventsEl.innerHTML = '<p style="color: #7f8c8d;">No upcoming events</p>';
            return;
        }
        
        upcoming.forEach(event => {
            const item = document.createElement('div');
            item.className = `event-list-item ${event.module}`;
            item.innerHTML = `
                <div class="event-list-title">${event.title}</div>
                <div class="event-list-date">${this.formatDate(event.start)}</div>
            `;
            item.addEventListener('click', () => this.showEventDetails(event));
            this.upcomingEventsEl.appendChild(item);
        });
    }

    switchView() {
        this.monthView.classList.add('hidden');
        this.timelineView.classList.add('hidden');
        this.yearView.classList.add('hidden');
        
        switch (this.viewType) {
            case 'month':
                this.monthView.classList.remove('hidden');
                break;
            case 'timeline':
                this.timelineView.classList.remove('hidden');
                break;
            case 'year':
                this.yearView.classList.remove('hidden');
                break;
        }
        
        this.render();
    }

    render() {
        this.updateCurrentPeriod();
        
        switch (this.viewType) {
            case 'month':
                this.renderMonthView();
                break;
            case 'timeline':
                this.renderTimelineView();
                break;
            case 'year':
                this.renderYearView();
                break;
        }
        
        this.updateStatistics();
    }

    updateCurrentPeriod() {
        const months = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
        
        if (this.viewType === 'year') {
            this.currentPeriodEl.textContent = this.currentDate.getFullYear();
        } else {
            const month = months[this.currentDate.getMonth()];
            const year = this.currentDate.getFullYear();
            this.currentPeriodEl.textContent = `${month} ${year}`;
        }
    }

    renderMonthView() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startingDayOfWeek = firstDay.getDay();
        const daysInMonth = lastDay.getDate();
        
        // Build calendar grid
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        let html = '';
        
        // Day headers
        days.forEach(day => {
            html += `<div class="day-name">${day}</div>`;
        });
        
        // Empty cells before month starts
        for (let i = 0; i < startingDayOfWeek; i++) {
            html += '<div class="calendar-day other-month"></div>';
        }
        
        // Days of month
        const today = new Date();
        const filteredEvents = this.getFilteredEvents();
        
        for (let day = 1; day <= daysInMonth; day++) {
            const currentDay = new Date(year, month, day);
            const isToday = this.isSameDay(currentDay, today);
            
            const dayEvents = filteredEvents.filter(event => 
                this.isEventOnDay(event, currentDay)
            );
            
            let dayClass = 'calendar-day';
            if (isToday) dayClass += ' today';
            
            html += `
                <div class="${dayClass}" data-date="${currentDay.toISOString()}">
                    <div class="day-header">${day}</div>
                    <div class="day-events">
                        ${dayEvents.slice(0, 3).map(event => `
                            <div class="event-item ${event.module} ${event.status}" 
                                 data-event-id="${event.id}">
                                ${event.title}
                            </div>
                        `).join('')}
                        ${dayEvents.length > 3 ? `<div class="event-item" style="background: #95a5a6;">+${dayEvents.length - 3} more</div>` : ''}
                    </div>
                </div>
            `;
        }
        
        this.calendarGrid.innerHTML = html;
        
        // Attach event listeners
        this.calendarGrid.querySelectorAll('.event-item').forEach(el => {
            el.addEventListener('click', (e) => {
                e.stopPropagation();
                const eventId = el.dataset.eventId;
                const event = this.events.find(ev => ev.id === eventId);
                if (event) this.showEventDetails(event);
            });
        });
    }

renderTimelineView() {
        const filteredEvents = this.getFilteredEvents();
        const vessels = [...new Set(filteredEvents.map(e => e.vessel))].sort();
        
        // Generate date range for current month
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        let vesselsHtml = '<div class="timeline-vessel-row" style="height: 40px; font-weight: bold;">Vessel</div>';
        let datesHtml = '';
        let bodyHtml = '';
        
        // Generate date columns
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const isWeekend = date.getDay() === 0 || date.getDay() === 6;
            datesHtml += `<div class="timeline-date-col ${isWeekend ? 'weekend' : ''}">${day}</div>`;
        }
        
        // Generate vessel rows and events
        vessels.forEach(vessel => {
            vesselsHtml += `<div class="timeline-vessel-row">${vessel}</div>`;
            
            const vesselEvents = filteredEvents.filter(e => e.vessel === vessel);
            let rowHtml = '<div class="timeline-row">';
            
            vesselEvents.forEach(event => {
                const startDay = event.start.getDate();
                const endDay = event.end.getDate();
                const left = ((startDay - 1) / daysInMonth) * 100;
                const width = ((endDay - startDay + 1) / daysInMonth) * 100;
                
                rowHtml += `
                    <div class="timeline-event ${event.module}" 
                         style="left: ${left}%; width: ${width}%;"
                         data-event-id="${event.id}">
                        ${event.title}
                    </div>
                `;
            });
            
            rowHtml += '</div>';
            bodyHtml += rowHtml;
        });
        
        document.getElementById('timelineVessels').innerHTML = vesselsHtml;
        document.getElementById('timelineDates').innerHTML = datesHtml;
        document.getElementById('timelineBody').innerHTML = bodyHtml;
        
        // Attach event listeners
        document.querySelectorAll('.timeline-event').forEach(el => {
            el.addEventListener('click', () => {
                const eventId = el.dataset.eventId;
                const event = this.events.find(ev => ev.id === eventId);
                if (event) this.showEventDetails(event);
            });
        });
    }

    renderYearView() {
        const year = this.currentDate.getFullYear();
        const months = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
        
        let html = '';
        
        months.forEach((monthName, monthIndex) => {
            const firstDay = new Date(year, monthIndex, 1);
            const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
            const startingDay = firstDay.getDay();
            
            let miniHtml = `
                <div class="mini-month">
                    <div class="mini-month-header">${monthName}</div>
                    <div class="mini-calendar">
            `;
            
            // Empty cells
            for (let i = 0; i < startingDay; i++) {
                miniHtml += '<div class="mini-day"></div>';
            }
            
            // Days
            for (let day = 1; day <= daysInMonth; day++) {
                const date = new Date(year, monthIndex, day);
                const hasEvents = this.events.some(e => this.isEventOnDay(e, date));
                miniHtml += `<div class="mini-day ${hasEvents ? 'has-events' : ''}">${day}</div>`;
            }
            
            miniHtml += '</div></div>';
            html += miniHtml;
        });
        
        document.getElementById('yearGrid').innerHTML = html;
    }

    isEventOnDay(event, day) {
        const dayStart = new Date(day.getFullYear(), day.getMonth(), day.getDate());
        const dayEnd = new Date(day.getFullYear(), day.getMonth(), day.getDate(), 23, 59, 59);
        
        return (event.start <= dayEnd && event.end >= dayStart);
    }

    isSameDay(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }

    showEventDetails(event) {
        this.modalTitle.textContent = event.title;
        
        this.modalBody.innerHTML = `
            <div class="detail-row">
                <div class="detail-label">Voyage ID:</div>
                <div class="detail-value">${event.id}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Module:</div>
                <div class="detail-value">${event.module.toUpperCase()}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Vessel:</div>
                <div class="detail-value">${event.vessel}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Status:</div>
                <div class="detail-value">${event.status}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Start Date:</div>
                <div class="detail-value">${this.formatDate(event.start)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">End Date:</div>
                <div class="detail-value">${this.formatDate(event.end)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Route:</div>
                <div class="detail-value">${event.route}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Cargo:</div>
                <div class="detail-value">${this.formatNumber(event.cargo)} MT</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Cost:</div>
                <div class="detail-value">$${this.formatNumber(event.cost)}</div>
            </div>
        `;
        
        this.modal.classList.remove('hidden');
    }

    closeModal() {
        this.modal.classList.add('hidden');
    }

    navigatePrevious() {
        if (this.viewType === 'year') {
            this.currentDate.setFullYear(this.currentDate.getFullYear() - 1);
        } else {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        }
        this.render();
    }

    navigateNext() {
        if (this.viewType === 'year') {
            this.currentDate.setFullYear(this.currentDate.getFullYear() + 1);
        } else {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        }
        this.render();
    }

    navigateToday() {
        this.currentDate = new Date();
        this.render();
    }

    async refresh() {
        this.events = [];
        await this.loadData();
        this.render();
    }

    exportCalendar() {
        const filteredEvents = this.getFilteredEvents();
        const csv = this.convertToCSV(filteredEvents);
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `calendar_export_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    convertToCSV(events) {
        const headers = ['ID', 'Title', 'Module', 'Vessel', 'Start', 'End', 'Status', 'Cargo', 'Cost', 'Route'];
        const rows = events.map(e => [
            e.id,
            e.title,
            e.module,
            e.vessel,
            this.formatDate(e.start),
            this.formatDate(e.end),
            e.status,
            e.cargo,
            e.cost,
            e.route
        ]);
        
        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    }

    formatNumber(num) {
        if (!num) return '0';
        return num.toLocaleString('en-US', { maximumFractionDigits: 0 });
    }

    showError(message) {
        console.error(message);
        // Could implement a toast notification here
    }
}

// Initialize calendar when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new OperationalCalendar();
});
