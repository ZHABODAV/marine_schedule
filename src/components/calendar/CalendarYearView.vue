<template>
  <div class="calendar-year-view">
    <div class="year-grid">
      <div
        v-for="(month, index) in months"
        :key="index"
        class="mini-month"
      >
        <!-- Month Header -->
        <div class="mini-month-header">
          <h3 class="month-name">{{ month.name }}</h3>
          <span class="event-count-badge">{{ month.eventCount }}</span>
        </div>

        <!-- Mini Calendar Grid -->
        <div class="mini-calendar-grid">
          <!-- Day headers -->
          <div
            v-for="day in weekDaysShort"
            :key="day"
            class="mini-day-header"
          >
            {{ day }}
          </div>

          <!-- Calendar days -->
          <div
            v-for="(day, dayIndex) in month.days"
            :key="dayIndex"
            :class="[
              'mini-day',
              {
                'other-month': !day.isCurrentMonth,
                'today': day.isToday,
                'has-events': day.eventCount > 0,
                'clickable': day.eventCount > 0
              }
            ]"
            @click="day.eventCount > 0 && handleDayClick(month.monthIndex, day.date)"
          >
            <span class="mini-day-number">{{ day.number }}</span>
            <span v-if="day.eventCount > 0" class="mini-event-indicator">
              {{ day.eventCount }}
            </span>
          </div>
        </div>

        <!-- Month Summary -->
        <div v-if="month.eventCount > 0" class="month-summary">
          <div class="summary-item">
            <span class="summary-icon"></span>
            <span class="summary-text">{{ month.vesselCount }} vessels</span>
          </div>
          <div class="summary-item">
            <span class="summary-icon"></span>
            <span class="summary-text">{{ formatNumber(month.totalCargo) }} MT</span>
          </div>
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

interface MiniDay {
  number: number;
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  eventCount: number;
}

interface MonthData {
  monthIndex: number;
  name: string;
  days: MiniDay[];
  eventCount: number;
  vesselCount: number;
  totalCargo: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'event-click': [event: CalendarEvent];
  'month-click': [monthIndex: number];
}>();

const weekDaysShort = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

const months = computed<MonthData[]>(() => {
  const year = props.currentDate.getFullYear();
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  return Array.from({ length: 12 }, (_, monthIndex) => {
    const monthStart = new Date(year, monthIndex, 1);
    const monthEnd = new Date(year, monthIndex + 1, 0);
    const daysInMonth = monthEnd.getDate();
    const firstDayOfWeek = monthStart.getDay();
    
    // Calculate previous month's days to show
    const prevMonthEnd = new Date(year, monthIndex, 0);
    const prevMonthDays = prevMonthEnd.getDate();
    const daysToShowFromPrevMonth = firstDayOfWeek;
    
    // Calculate next month's days to show
    const totalCells = 42; // 6 weeks
    const daysToShowFromNextMonth = totalCells - (daysToShowFromPrevMonth + daysInMonth);
    
    const days: MiniDay[] = [];
    
    // Previous month days
    for (let i = daysToShowFromPrevMonth - 1; i >= 0; i--) {
      const date = new Date(year, monthIndex - 1, prevMonthDays - i);
      days.push(createMiniDay(date, false, today));
    }
    
    // Current month days
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, monthIndex, day);
      days.push(createMiniDay(date, true, today));
    }
    
    // Next month days
    for (let day = 1; day <= daysToShowFromNextMonth; day++) {
      const date = new Date(year, monthIndex + 1, day);
      days.push(createMiniDay(date, false, today));
    }
    
    // Get month events
    const monthEvents = props.events.filter(event => {
      const eventDate = new Date(event.start);
      return eventDate.getFullYear() === year && eventDate.getMonth() === monthIndex;
    });
    
    // Calculate month statistics
    const vesselCount = new Set(monthEvents.map(e => e.vessel)).size;
    const totalCargo = monthEvents.reduce((sum, e) => sum + (e.cargo || 0), 0);
    
    return {
      monthIndex,
      name: monthStart.toLocaleDateString('en-US', { month: 'long' }),
      days,
      eventCount: monthEvents.length,
      vesselCount,
      totalCargo
    };
  });
});

function createMiniDay(date: Date, isCurrentMonth: boolean, today: Date): MiniDay {
  const dayStart = new Date(date);
  dayStart.setHours(0, 0, 0, 0);
  
  const dayEnd = new Date(date);
  dayEnd.setHours(23, 59, 59, 999);
  
  const eventCount = props.events.filter(event => {
    const eventStart = new Date(event.start);
    const eventEnd = new Date(event.end);
    return eventStart <= dayEnd && eventEnd >= dayStart;
  }).length;
  
  return {
    number: date.getDate(),
    date,
    isCurrentMonth,
    isToday: dayStart.getTime() === today.getTime(),
    eventCount
  };
}

function handleDayClick(monthIndex: number, date: Date) {
  emit('month-click', monthIndex);
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0
  }).format(value);
}
</script>

<style scoped>
.calendar-year-view {
  width: 100%;
}

.year-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.mini-month {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s;
}

.mini-month:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mini-month-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--color-border);
}

.month-name {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-heading);
}

.event-count-badge {
  padding: 0.25rem 0.625rem;
  background: var(--color-primary);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.mini-calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 0.75rem;
}

.mini-day-header {
  text-align: center;
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  padding: 0.25rem;
  text-transform: uppercase;
}

.mini-day {
  position: relative;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  border-radius: 4px;
  transition: all 0.2s;
  background: var(--color-background-soft);
}

.mini-day.other-month {
  opacity: 0.3;
}

.mini-day.today {
  background: var(--color-primary);
  color: white;
  font-weight: 700;
}

.mini-day.has-events {
  background: #e3f2fd;
  font-weight: 600;
}

.mini-day.clickable {
  cursor: pointer;
}

.mini-day.clickable:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1;
}

.mini-day-number {
  position: relative;
  z-index: 1;
}

.mini-event-indicator {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 14px;
  height: 14px;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-size: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.mini-day.today .mini-event-indicator {
  background: white;
  color: var(--color-primary);
}

.month-summary {
  display: flex;
  gap: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.summary-icon {
  font-size: 1rem;
}

.summary-text {
  font-weight: 500;
}

@media (max-width: 1200px) {
  .year-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .year-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .mini-month {
    padding: 0.75rem;
  }

  .month-name {
    font-size: 1rem;
  }

  .mini-calendar-grid {
    gap: 1px;
  }
}

@media (max-width: 480px) {
  .year-grid {
    grid-template-columns: 1fr;
  }
}
</style>
