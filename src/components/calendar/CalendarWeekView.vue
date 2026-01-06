<template>
  <div class="calendar-week-view">
    <!-- Time Labels Column -->
    <div class="week-grid">
      <!-- Header Row -->
      <div class="time-label-header"></div>
      <div
        v-for="day in weekDays"
        :key="day.date.toISOString()"
        :class="['day-header', { today: day.isToday }]"
      >
        <div class="day-name">{{ day.dayName }}</div>
        <div class="day-number">{{ day.date.getDate() }}</div>
        <div v-if="day.eventCount > 0" class="day-event-count">
          {{ day.eventCount }} events
        </div>
      </div>

      <!-- Time Slots -->
      <template v-for="hour in hours" :key="hour">
        <div class="time-label">{{ formatHour(hour) }}</div>
        <div
          v-for="day in weekDays"
          :key="`${day.date.toISOString()}-${hour}`"
          :class="['time-slot', { 'current-hour': isCurrentHour(day.date, hour) }]"
        >
          <!-- Events in this time slot -->
          <div
            v-for="event in getEventsForSlot(day.date, hour)"
            :key="event.id"
            :class="[
              'event-block',
              `module-${event.module}`,
              `status-${event.status}`
            ]"
            :style="getEventStyle(event, day.date, hour)"
            @click="$emit('event-click', event)"
          >
            <div class="event-content">
              <div class="event-vessel">{{ event.vessel }}</div>
              <div class="event-route">{{ event.route }}</div>
              <div class="event-time-range">
                {{ formatEventTime(event.start) }} - {{ formatEventTime(event.end) }}
              </div>
            </div>
          </div>
        </div>
      </template>
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

interface WeekDay {
  date: Date;
  dayName: string;
  isToday: boolean;
  eventCount: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'event-click': [event: CalendarEvent];
}>();

const hours = Array.from({ length: 24 }, (_, i) => i);

const weekDays = computed<WeekDay[]>(() => {
  const days: WeekDay[] = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  // Get the start of the week (Sunday)
  const current = new Date(props.currentDate);
  const dayOfWeek = current.getDay();
  const startOfWeek = new Date(current);
  startOfWeek.setDate(current.getDate() - dayOfWeek);
  startOfWeek.setHours(0, 0, 0, 0);
  
  // Generate 7 days
  for (let i = 0; i < 7; i++) {
    const dayDate = new Date(startOfWeek);
    dayDate.setDate(startOfWeek.getDate() + i);
    
    const dayStart = new Date(dayDate);
    dayStart.setHours(0, 0, 0, 0);
    
    const dayEnd = new Date(dayDate);
    dayEnd.setHours(23, 59, 59, 999);
    
    const eventCount = props.events.filter(event => {
      const eventStart = new Date(event.start);
      const eventEnd = new Date(event.end);
      return eventStart <= dayEnd && eventEnd >= dayStart;
    }).length;
    
    days.push({
      date: dayDate,
      dayName: dayDate.toLocaleDateString('en-US', { weekday: 'short' }),
      isToday: dayStart.getTime() === today.getTime(),
      eventCount
    });
  }
  
  return days;
});

function formatHour(hour: number): string {
  const period = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  return `${displayHour}:00 ${period}`;
}

function formatEventTime(date: Date): string {
  return new Date(date).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}

function isCurrentHour(date: Date, hour: number): boolean {
  const now = new Date();
  return (
    date.getDate() === now.getDate() &&
    date.getMonth() === now.getMonth() &&
    date.getFullYear() === now.getFullYear() &&
    hour === now.getHours()
  );
}

function getEventsForSlot(date: Date, hour: number): CalendarEvent[] {
  const slotStart = new Date(date);
  slotStart.setHours(hour, 0, 0, 0);
  
  const slotEnd = new Date(date);
  slotEnd.setHours(hour, 59, 59, 999);
  
  return props.events.filter(event => {
    const eventStart = new Date(event.start);
    const eventEnd = new Date(event.end);
    
    // Check if event overlaps with this hour slot
    return eventStart <= slotEnd && eventEnd >= slotStart;
  });
}

function getEventStyle(event: CalendarEvent, date: Date, hour: number) {
  const slotStart = new Date(date);
  slotStart.setHours(hour, 0, 0, 0);
  
  const slotEnd = new Date(date);
  slotEnd.setHours(hour + 1, 0, 0, 0);
  
  const eventStart = new Date(event.start);
  const eventEnd = new Date(event.end);
  
  // Calculate position and height
  const slotDuration = 60; // minutes
  const eventStartInSlot = Math.max(
    0,
    (eventStart.getTime() - slotStart.getTime()) / (1000 * 60)
  );
  const eventEndInSlot = Math.min(
    slotDuration,
    (eventEnd.getTime() - slotStart.getTime()) / (1000 * 60)
  );
  
  const top = (eventStartInSlot / slotDuration) * 100;
  const height = ((eventEndInSlot - eventStartInSlot) / slotDuration) * 100;
  
  return {
    top: `${top}%`,
    height: `${Math.max(height, 20)}%` // Minimum 20% height for visibility
  };
}
</script>

<style scoped>
.calendar-week-view {
  width: 100%;
  overflow-x: auto;
}

.week-grid {
  display: grid;
  grid-template-columns: 80px repeat(7, 1fr);
  min-width: 900px;
}

.time-label-header {
  grid-column: 1;
  border-bottom: 2px solid var(--color-border);
}

.day-header {
  padding: 1rem;
  text-align: center;
  border-bottom: 2px solid var(--color-border);
  background: var(--color-background-soft);
}

.day-header.today {
  background: #fff8e1;
  border-bottom-color: var(--color-primary);
}

.day-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.day-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin-top: 0.25rem;
}

.day-header.today .day-number {
  color: var(--color-primary);
}

.day-event-count {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
}

.time-label {
  grid-column: 1;
  padding: 0.5rem;
  text-align: right;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  border-right: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-background-soft);
}

.time-slot {
  position: relative;
  min-height: 60px;
  border-right: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-background);
  transition: background 0.2s;
}

.time-slot:hover {
  background: var(--color-background-soft);
}

.time-slot.current-hour {
  background: #fff8e1;
}

.event-block {
  position: absolute;
  left: 2px;
  right: 2px;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.event-block:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.event-content {
  font-size: 0.75rem;
  line-height: 1.3;
}

.event-vessel {
  font-weight: 600;
  margin-bottom: 0.125rem;
}

.event-route {
  font-size: 0.625rem;
  opacity: 0.9;
  margin-bottom: 0.125rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-time-range {
  font-size: 0.625rem;
  opacity: 0.8;
  font-weight: 500;
}

/* Module colors */
.module-deepsea {
  background: #e3f2fd;
  color: #1976d2;
  border-left: 4px solid #1976d2;
}

.module-olya {
  background: #f3e5f5;
  color: #7b1fa2;
  border-left: 4px solid #7b1fa2;
}

.module-balakovo {
  background: #e8f5e9;
  color: #388e3c;
  border-left: 4px solid #388e3c;
}

/* Status styles */
.status-completed {
  opacity: 0.7;
}

.status-cancelled {
  opacity: 0.5;
  text-decoration: line-through;
}

.status-in-progress {
  font-weight: 600;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .week-grid {
    grid-template-columns: 60px repeat(7, 1fr);
    min-width: 700px;
  }

  .time-label {
    font-size: 0.625rem;
    padding: 0.25rem;
  }

  .day-header {
    padding: 0.5rem;
  }

  .day-number {
    font-size: 1.125rem;
  }

  .time-slot {
    min-height: 50px;
  }

  .event-content {
    font-size: 0.625rem;
  }

  .event-route,
  .event-time-range {
    display: none;
  }
}
</style>
