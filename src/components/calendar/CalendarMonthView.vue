<template>
  <div class="calendar-month-view">
    <!-- Month Grid -->
    <div class="calendar-grid">
      <!-- Day Headers -->
      <div
        v-for="day in weekDays"
        :key="day"
        class="calendar-header-cell"
      >
        {{ day }}
      </div>

      <!-- Calendar Days -->
      <div
        v-for="(day, index) in calendarDays"
        :key="index"
        :class="[
          'calendar-day',
          {
            'other-month': !day.isCurrentMonth,
            'today': day.isToday,
            'has-events': day.events.length > 0
          }
        ]"
      >
        <div class="day-header">
          <span class="day-number">{{ day.date.getDate() }}</span>
          <span v-if="day.events.length > 0" class="event-count">
            {{ day.events.length }}
          </span>
        </div>

        <div class="day-events">
          <div
            v-for="event in day.events.slice(0, 3)"
            :key="event.id"
            :class="['event-item', `module-${event.module}`, `status-${event.status}`]"
            @click="$emit('event-click', event)"
          >
            <div class="event-dot"></div>
            <div class="event-title">{{ event.vessel }}</div>
            <div class="event-time">{{ formatTime(event.start) }}</div>
          </div>

          <button
            v-if="day.events.length > 3"
            class="more-events"
            @click="showMoreEvents(day)"
          >
            +{{ day.events.length - 3 }} more
          </button>
        </div>
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

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  events: CalendarEvent[];
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'event-click': [event: CalendarEvent];
}>();

const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const calendarDays = computed<CalendarDay[]>(() => {
  const year = props.currentDate.getFullYear();
  const month = props.currentDate.getMonth();
  
  // First day of the month
  const firstDay = new Date(year, month, 1);
  const firstDayOfWeek = firstDay.getDay();
  
  // Last day of the month
  const lastDay = new Date(year, month + 1, 0);
  const lastDate = lastDay.getDate();
  
  // Days from previous month
  const prevMonthDays = firstDayOfWeek;
  const prevMonthLastDay = new Date(year, month, 0).getDate();
  
  // Days needed for next month to complete the grid
  const totalCells = 42; // 6 weeks × 7 days
  const nextMonthDays = totalCells - (prevMonthDays + lastDate);
  
  const days: CalendarDay[] = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  // Previous month days
  for (let i = prevMonthDays - 1; i >= 0; i--) {
    const date = new Date(year, month - 1, prevMonthLastDay - i);
    days.push(createCalendarDay(date, false, today));
  }
  
  // Current month days
  for (let date = 1; date <= lastDate; date++) {
    const dayDate = new Date(year, month, date);
    days.push(createCalendarDay(dayDate, true, today));
  }
  
  // Next month days
  for (let date = 1; date <= nextMonthDays; date++) {
    const dayDate = new Date(year, month + 1, date);
    days.push(createCalendarDay(dayDate, false, today));
  }
  
  return days;
});

function createCalendarDay(date: Date, isCurrentMonth: boolean, today: Date): CalendarDay {
  const dayStart = new Date(date);
  dayStart.setHours(0, 0, 0, 0);
  
  const dayEnd = new Date(date);
  dayEnd.setHours(23, 59, 59, 999);
  
  const dayEvents = props.events.filter(event => {
    const eventStart = new Date(event.start);
    const eventEnd = new Date(event.end);
    
    // Event overlaps with this day
    return eventStart <= dayEnd && eventEnd >= dayStart;
  });
  
  return {
    date,
    isCurrentMonth,
    isToday: dayStart.getTime() === today.getTime(),
    events: dayEvents
  };
}

function formatTime(date: Date): string {
  return new Date(date).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}

function showMoreEvents(day: CalendarDay) {
  // Could open a modal or expand the day
  console.log('Show more events for', day.date, day.events);
}
</script>

<style scoped>
.calendar-month-view {
  width: 100%;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: var(--color-border);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
}

.calendar-header-cell {
  padding: 0.75rem;
  text-align: center;
  font-weight: 600;
  font-size: 0.875rem;
  background: var(--color-background-soft);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.calendar-day {
  min-height: 120px;
  background: var(--color-background);
  padding: 0.5rem;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.calendar-day:hover {
  background: var(--color-background-soft);
}

.calendar-day.other-month {
  background: var(--color-background-mute);
  opacity: 0.6;
}

.calendar-day.today {
  background: #fff8e1;
  outline: 2px solid var(--color-primary);
}

.calendar-day.has-events {
  cursor: pointer;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.day-number {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text);
}

.today .day-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
}

.event-count {
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
  background: var(--color-primary);
  color: white;
  border-radius: 10px;
  font-weight: 600;
}

.day-events {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.375rem;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
}

.event-item:hover {
  transform: translateX(2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.event-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.event-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.event-time {
  font-size: 0.625rem;
  opacity: 0.8;
}

/* Module colors */
.module-deepsea {
  background: #e3f2fd;
  color: #1976d2;
}

.module-deepsea .event-dot {
  background: #1976d2;
}

.module-olya {
  background: #f3e5f5;
  color: #7b1fa2;
}

.module-olya .event-dot {
  background: #7b1fa2;
}

.module-balakovo {
  background: #e8f5e9;
  color: #388e3c;
}

.module-balakovo .event-dot {
  background: #388e3c;
}

/* Status overlays */
.status-completed {
  opacity: 0.7;
}

.status-cancelled {
  opacity: 0.5;
  text-decoration: line-through;
}

.status-in-progress {
  font-weight: 600;
}

.more-events {
  padding: 0.25rem;
  font-size: 0.625rem;
  color: var(--color-primary);
  background: transparent;
  border: 1px dashed var(--color-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: auto;
}

.more-events:hover {
  background: var(--color-background-soft);
  border-color: var(--color-primary);
}

@media (max-width: 768px) {
  .calendar-day {
    min-height: 80px;
    padding: 0.25rem;
  }

  .calendar-header-cell {
    padding: 0.5rem;
    font-size: 0.75rem;
  }

  .day-number {
    font-size: 0.75rem;
  }

  .event-item {
    font-size: 0.625rem;
    padding: 0.125rem 0.25rem;
  }

  .event-time {
    display: none;
  }
}
</style>
