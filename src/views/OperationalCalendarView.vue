<template>
  <div class="operational-calendar-view">
    <!-- Header with Statistics and Actions -->
    <div class="calendar-header">
      <div class="calendar-title">
        <h1>Operational Calendar</h1>
        <p class="subtitle">Vessel Schedule & Voyage Planning</p>
      </div>
      
      <!-- Statistics Panel -->
      <div class="statistics-panel">
        <div class="stat-card">
          <div class="stat-icon"></div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.activeVessels }}</div>
            <div class="stat-label">Active Vessels</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon"></div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.totalVoyages }}</div>
            <div class="stat-label">Total Voyages</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon"></div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(statistics.totalCargo) }}</div>
            <div class="stat-label">Total Cargo (MT)</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon"></div>
          <div class="stat-content">
            <div class="stat-value">${{ formatNumber(statistics.totalCost) }}</div>
            <div class="stat-label">Total Cost (USD)</div>
          </div>
        </div>
      </div>

      <!-- Export Actions -->
      <div class="export-actions">
        <BaseButton
          variant="secondary"
          size="small"
          :disabled="loading"
          @click="exportToCSV"
        >
           Export CSV
        </BaseButton>
        <BaseButton
          variant="secondary"
          size="small"
          :disabled="loading"
          @click="exportToPDF"
        >
           Export PDF
        </BaseButton>
      </div>
    </div>

    <!-- Global Filters -->
    <GlobalFiltersBar
      context="calendar"
      :vessel-options="vesselOptions"
      :status-options="statusOptions"
      @filters-changed="handleFiltersChanged"
    />

    <!-- Calendar Controls -->
    <div class="calendar-controls">
      <!-- View Type Switcher -->
      <div class="view-switcher">
        <button
          v-for="view in viewTypes"
          :key="view.value"
          :class="['view-btn', { active: viewType === view.value }]"
          @click="changeView(view.value)"
        >
          <span class="view-icon">{{ view.icon }}</span>
          <span class="view-label">{{ view.label }}</span>
        </button>
      </div>

      <!-- Date Navigation -->
      <div class="date-navigation">
        <BaseButton
          variant="text"
          size="small"
          @click="navigatePrevious"
        >
          ◀ Previous
        </BaseButton>
        
        <button class="current-date-btn" @click="navigateToday">
          {{ formattedCurrentDate }}
        </button>
        
        <BaseButton
          variant="text"
          size="small"
          @click="navigateNext"
        >
          Next ▶
        </BaseButton>
      </div>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Loading calendar events..." />

    <!-- Error State -->
    <div v-else-if="error" class="error-message">
      <p> {{ error }}</p>
      <BaseButton variant="primary" @click="loadCalendar">Retry</BaseButton>
    </div>

    <!-- Calendar Views -->
    <div v-else class="calendar-content">
      <CalendarMonthView
        v-if="viewType === 'month'"
        :events="filteredEvents"
        :current-date="currentDate"
        @event-click="handleEventClick"
      />
      
      <CalendarWeekView
        v-else-if="viewType === 'week'"
        :events="filteredEvents"
        :current-date="currentDate"
        @event-click="handleEventClick"
      />
      
      <CalendarYearView
        v-else-if="viewType === 'year'"
        :events="filteredEvents"
        :current-date="currentDate"
        @event-click="handleEventClick"
        @month-click="handleMonthClick"
      />
      
      <CalendarTimelineView
        v-else-if="viewType === 'timeline'"
        :events="filteredEvents"
        :current-date="currentDate"
        @event-click="handleEventClick"
      />
    </div>

    <!-- Event Details Modal -->
    <EventModal
      v-if="selectedEvent"
      :event="selectedEvent"
      @close="selectedEvent = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useCalendarStore } from '@/stores/calendar';
import type { CalendarEvent, CalendarViewType } from '@/types/calendar.types';
import GlobalFiltersBar from '@/components/shared/GlobalFiltersBar.vue';
import BaseButton from '@/components/shared/BaseButton.vue';
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue';
import CalendarMonthView from '@/components/calendar/CalendarMonthView.vue';
import CalendarWeekView from '@/components/calendar/CalendarWeekView.vue';
import CalendarYearView from '@/components/calendar/CalendarYearView.vue';
import CalendarTimelineView from '@/components/calendar/CalendarTimelineView.vue';
import EventModal from '@/components/calendar/EventModal.vue';

const calendarStore = useCalendarStore();
const {
  currentDate,
  viewType,
  loading,
  error,
  filteredEvents,
  statistics,
  uniqueVessels
} = storeToRefs(calendarStore);

const selectedEvent = ref<CalendarEvent | null>(null);

const viewTypes = [
  { value: 'month' as CalendarViewType, label: 'Month', icon: '' },
  { value: 'week' as CalendarViewType, label: 'Week', icon: '' },
  { value: 'year' as CalendarViewType, label: 'Year', icon: '' },
  { value: 'timeline' as CalendarViewType, label: 'Timeline', icon: '' }
];

const vesselOptions = computed(() => 
  uniqueVessels.value.map(vessel => ({ value: vessel, label: vessel }))
);

const statusOptions = computed(() => [
  { value: 'planned', label: 'Planned' },
  { value: 'in-progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' }
]);

const formattedCurrentDate = computed(() => {
  const date = currentDate.value;
  const options: Intl.DateTimeFormatOptions = 
    viewType.value === 'year' 
      ? { year: 'numeric' }
      : { year: 'numeric', month: 'long' };
  
  return date.toLocaleDateString('en-US', options);
});

function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0
  }).format(value);
}

function changeView(type: CalendarViewType) {
  calendarStore.setViewType(type);
}

function navigatePrevious() {
  calendarStore.navigatePrevious();
}

function navigateNext() {
  calendarStore.navigateNext();
}

function navigateToday() {
  calendarStore.navigateToday();
}

function handleEventClick(event: CalendarEvent) {
  selectedEvent.value = event;
}

function handleMonthClick(monthIndex: number) {
  const newDate = new Date(currentDate.value);
  newDate.setMonth(monthIndex);
  calendarStore.setCurrentDate(newDate);
  calendarStore.setViewType('month');
}

function handleFiltersChanged() {
  // Filters are automatically applied through the store
  console.log('Filters changed');
}

async function loadCalendar() {
  await calendarStore.fetchEvents();
}

function exportToCSV() {
  const events = filteredEvents.value;
  
  // CSV headers
  const headers = ['Date', 'Vessel', 'Module', 'Route', 'Status', 'Cargo (MT)', 'Cost (USD)'];
  
  // CSV rows
  const rows = events.map(event => [
    new Date(event.start).toLocaleDateString(),
    event.vessel,
    event.module,
    event.route || '',
    event.status,
    event.cargo?.toString() || '0',
    event.cost?.toString() || '0'
  ]);
  
  // Create CSV content
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');
  
  // Download
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `calendar-export-${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function exportToPDF() {
  // Create a printable version
  const printWindow = window.open('', '_blank');
  if (!printWindow) return;
  
  const events = filteredEvents.value;
  const stats = statistics.value;
  
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Operational Calendar Report</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #333; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
        .stat { padding: 15px; background: #f5f5f5; border-radius: 5px; }
        .stat-value { font-size: 24px; font-weight: bold; color: #0066cc; }
        .stat-label { font-size: 12px; color: #666; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #0066cc; color: white; }
        tr:hover { background: #f9f9f9; }
        @media print { 
          button { display: none; }
          .stats { page-break-inside: avoid; }
        }
      </style>
    </head>
    <body>
      <h1>Operational Calendar Report</h1>
      <p>Generated: ${new Date().toLocaleString()}</p>
      
      <div class="stats">
        <div class="stat">
          <div class="stat-value">${stats.activeVessels}</div>
          <div class="stat-label">Active Vessels</div>
        </div>
        <div class="stat">
          <div class="stat-value">${stats.totalVoyages}</div>
          <div class="stat-label">Total Voyages</div>
        </div>
        <div class="stat">
          <div class="stat-value">${formatNumber(stats.totalCargo)}</div>
          <div class="stat-label">Total Cargo (MT)</div>
        </div>
        <div class="stat">
          <div class="stat-value">$${formatNumber(stats.totalCost)}</div>
          <div class="stat-label">Total Cost (USD)</div>
        </div>
      </div>
      
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Vessel</th>
            <th>Module</th>
            <th>Route</th>
            <th>Status</th>
            <th>Cargo (MT)</th>
            <th>Cost (USD)</th>
          </tr>
        </thead>
        <tbody>
          ${events.map(event => `
            <tr>
              <td>${new Date(event.start).toLocaleDateString()}</td>
              <td>${event.vessel}</td>
              <td>${event.module}</td>
              <td>${event.route || '-'}</td>
              <td>${event.status}</td>
              <td>${formatNumber(event.cargo || 0)}</td>
              <td>$${formatNumber(event.cost || 0)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      
      <button onclick="window.print()" style="margin-top: 20px; padding: 10px 20px; background: #0066cc; color: white; border: none; border-radius: 5px; cursor: pointer;">
        Print / Save as PDF
      </button>
    </body>
    </html>
  `;
  
  printWindow.document.write(html);
  printWindow.document.close();
}

onMounted(() => {
  loadCalendar();
});
</script>

<style scoped>
.operational-calendar-view {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
}

.calendar-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.calendar-title h1 {
  margin: 0;
  font-size: 2rem;
  color: var(--color-heading);
}

.subtitle {
  margin: 0.25rem 0 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.statistics-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  flex: 1;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  transition: all 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 2rem;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
}

.export-actions {
  display: flex;
  gap: 0.5rem;
}

.calendar-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  flex-wrap: wrap;
  gap: 1rem;
}

.view-switcher {
  display: flex;
  gap: 0.5rem;
  background: var(--color-background);
  border-radius: 6px;
  padding: 0.25rem;
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  color: var(--color-text);
}

.view-btn:hover {
  background: var(--color-background-soft);
}

.view-btn.active {
  background: var(--color-primary);
  color: white;
}

.view-icon {
  font-size: 1.125rem;
}

.view-label {
  font-weight: 500;
}

.date-navigation {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.current-date-btn {
  padding: 0.5rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 200px;
  text-align: center;
}

.current-date-btn:hover {
  background: var(--color-background-soft);
}

.calendar-content {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1.5rem;
  min-height: 600px;
}

.error-message {
  text-align: center;
  padding: 3rem;
}

.error-message p {
  color: var(--color-danger);
  font-size: 1.125rem;
  margin-bottom: 1rem;
}

@media (max-width: 1024px) {
  .calendar-header {
    flex-direction: column;
    align-items: stretch;
  }

  .statistics-panel {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .operational-calendar-view {
    padding: 1rem;
  }

  .calendar-title h1 {
    font-size: 1.5rem;
  }

  .statistics-panel {
    grid-template-columns: 1fr;
  }

  .calendar-controls {
    flex-direction: column;
  }

  .view-switcher {
    width: 100%;
    flex-wrap: wrap;
  }

  .view-btn {
    flex: 1;
  }

  .date-navigation {
    width: 100%;
    justify-content: space-between;
  }

  .calendar-content {
    padding: 1rem;
  }
}
</style>
