<template>
  <div class="calendar-timeline-view">
    <!-- Timeline Header -->
    <div class="timeline-header">
      <div class="vessel-column-header">Vessel / Route</div>
      <div class="timeline-dates-header">
        <div
          v-for="date in dateRange"
          :key="date.toISOString()"
          :class="['timeline-date', { today: isToday(date) }]"
        >
          <div class="date-day">{{ date.getDate() }}</div>
          <div class="date-weekday">{{ getWeekdayShort(date) }}</div>
        </div>
      </div>
    </div>

    <!-- Timeline Body -->
    <div class="timeline-body">
      <div
        v-for="vessel in vesselsWithEvents"
        :key="vessel.name"
        class="timeline-row"
      >
        <!-- Vessel Info -->
        <div class="vessel-column">
          <div class="vessel-name">{{ vessel.name }}</div>
          <div class="vessel-stats">
            {{ vessel.eventCount }} voyages • {{ formatNumber(vessel.totalCargo) }} MT
          </div>
        </div>

        <!-- Timeline Grid -->
        <div class="timeline-grid">
          <!-- Background grid -->
          <div
            v-for="date in dateRange"
            :key="date.toISOString()"
            :class="['timeline-cell', { today: isToday(date) }]"
          >
          </div>

          <!-- Event Bars -->
          <div
            v-for="event in vessel.events"
            :key="event.id"
            :class="[
              'timeline-event',
              `module-${event.module}`,
              `status-${event.status}`
            ]"
            :style="getEventStyle(event)"
            @click="$emit('event-click', event)"
          >
            <div class="event-bar-content">
              <div class="event-bar-title">{{ event.route }}</div>
              <div class="event-bar-details">
                {{ formatEventDate(event.start) }} - {{ formatEventDate(event.end) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="vesselsWithEvents.length === 0" class="empty-state">
        <p>No events found for the selected period</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { CalendarEvent } from '@/types/calendar.types';

interface Props {
  events: CalendarEvent[];
  currentDate: Date;
}

interface VesselTimeline {
  name: string;
  events: CalendarEvent[];
  eventCount: number;
  totalCargo: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'event-click': [event: CalendarEvent];
}>();

// Generate date range (30 days from current date)
const dateRange = computed(() => {
  const dates: Date[] = [];
  const startDate = new Date(props.currentDate);
  startDate.setDate(1); // Start of month
  
  // Get number of days in month
  const year = startDate.getFullYear();
  const month = startDate.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  
  for (let i = 0; i < daysInMonth; i++) {
    const date = new Date(year, month, i + 1);
    dates.push(date);
  }
  
  return dates;
});

const timelineStart = computed(() => dateRange.value[0]);
const timelineEnd = computed(() => dateRange.value[dateRange.value.length - 1]);

// Group events by vessel
const vesselsWithEvents = computed<VesselTimeline[]>(() => {
  const vesselMap = new Map<string, CalendarEvent[]>();
  
  // Filter events within the timeline range
  const filteredEvents = props.events.filter(event => {
    const eventStart = new Date(event.start);
    const eventEnd = new Date(event.end);
    return eventStart <= timelineEnd.value && eventEnd >= timelineStart.value;
  });
  
  // Group by vessel
  filteredEvents.forEach(event => {
    if (!vesselMap.has(event.vessel)) {
      vesselMap.set(event.vessel, []);
    }
    vesselMap.get(event.vessel)!.push(event);
  });
  
  // Convert to array and sort
  return Array.from(vesselMap.entries())
    .map(([name, events]) => ({
      name,
      events: events.sort((a, b) => 
        new Date(a.start).getTime() - new Date(b.start).getTime()
      ),
      eventCount: events.length,
      totalCargo: events.reduce((sum, e) => sum + (e.cargo || 0), 0)
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
});

function isToday(date: Date): boolean {
  const today = new Date();
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
}

function getWeekdayShort(date: Date): string {
  return date.toLocaleDateString('en-US', { weekday: 'short' });
}

function getEventStyle(event: CalendarEvent) {
  const eventStart = new Date(event.start);
  const eventEnd = new Date(event.end);
  
  // Clamp to timeline bounds
  const start = eventStart < timelineStart.value ? timelineStart.value : eventStart;
  const end = eventEnd > timelineEnd.value ? timelineEnd.value : eventEnd;
  
  // Calculate position and width
  const totalDays = dateRange.value.length;
  const startDay = Math.floor(
    (start.getTime() - timelineStart.value.getTime()) / (1000 * 60 * 60 * 24)
  );
  const duration = Math.ceil(
    (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)
  ) + 1;
  
  const leftPercent = (startDay / totalDays) * 100;
  const widthPercent = (duration / totalDays) * 100;
  
  return {
    left: `${leftPercent}%`,
    width: `${widthPercent}%`
  };
}

function formatEventDate(date: Date): string {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  });
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0
  }).format(value);
}
</script>

<style scoped>
.calendar-timeline-view {
  width: 100%;
  overflow-x: auto;
}

.timeline-header {
  display: flex;
  background: var(--color-background-soft);
  border-bottom: 2px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 10;
}

.vessel-column-header {
  width: 200px;
  min-width: 200px;
  padding: 1rem;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-right: 2px solid var(--color-border);
}

.timeline-dates-header {
  display: flex;
  flex: 1;
  min-width: 0;
}

.timeline-date {
  flex: 1;
  min-width: 40px;
  padding: 0.5rem;
  text-align: center;
  border-right: 1px solid var(--color-border);
  transition: background 0.2s;
}

.timeline-date.today {
  background: #fff8e1;
}

.date-day {
  font-weight: 700;
  font-size: 0.875rem;
  color: var(--color-text);
}

.date-weekday {
  font-size: 0.625rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  margin-top: 0.125rem;
}

.timeline-body {
  position: relative;
}

.timeline-row {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  min-height: 80px;
}

.timeline-row:hover {
  background: var(--color-background-soft);
}

.vessel-column {
  width: 200px;
  min-width: 200px;
  padding: 1rem;
  border-right: 2px solid var(--color-border);
}

.vessel-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-heading);
  margin-bottom: 0.25rem;
}

.vessel-stats {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.timeline-grid {
  position: relative;
  display: flex;
  flex: 1;
  min-width: 0;
}

.timeline-cell {
  flex: 1;
  min-width: 40px;
  border-right: 1px solid var(--color-border);
}

.timeline-cell.today {
  background: #fff8e1;
}

.timeline-event {
  position: absolute;
  top: 10px;
  height: calc(100% - 20px);
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.timeline-event:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 5;
}

.event-bar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.event-bar-title {
  font-weight: 600;
  font-size: 0.75rem;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-bar-details {
  font-size: 0.625rem;
  opacity: 0.9;
}

/* Module colors */
.module-deepsea {
  background: linear-gradient(135deg, #e3f2fd 0%, #90caf9 100%);
  color: #1976d2;
  border-left: 4px solid #1976d2;
}

.module-olya {
  background: linear-gradient(135deg, #f3e5f5 0%, #ce93d8 100%);
  color: #7b1fa2;
  border-left: 4px solid #7b1fa2;
}

.module-balakovo {
  background: linear-gradient(135deg, #e8f5e9 0%, #a5d6a7 100%);
  color: #388e3c;
  border-left: 4px solid #388e3c;
}

/* Status styles */
.status-planned {
  opacity: 0.85;
}

.status-in-progress {
  font-weight: 700;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.15);
}

.status-completed {
  opacity: 0.6;
}

.status-cancelled {
  opacity: 0.4;
  text-decoration: line-through;
}

.empty-state {
  padding: 3rem;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 1rem;
}

@media (max-width: 768px) {
  .vessel-column-header,
  .vessel-column {
    width: 150px;
    min-width: 150px;
    padding: 0.75rem;
  }

  .vessel-name {
    font-size: 0.75rem;
  }

  .vessel-stats {
    font-size: 0.625rem;
  }

  .timeline-date {
    min-width: 30px;
    padding: 0.375rem;
  }

  .timeline-cell {
    min-width: 30px;
  }

  .event-bar-details {
    display: none;
  }
}
</style>
