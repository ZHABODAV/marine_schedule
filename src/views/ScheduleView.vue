<template>
  <div class="schedule-view">
    <div class="schedule-header">
      <h1>Schedule & Calendar</h1>
      
      <div class="header-controls">
        <div class="view-toggle">
          <button 
            :class="{ active: viewMode === 'month' }" 
            @click="viewMode = 'month'"
          >
            Month
          </button>
          <button 
            :class="{ active: viewMode === 'week' }" 
            @click="viewMode = 'week'"
          >
            Week
          </button>
          <button 
            :class="{ active: viewMode === 'list' }" 
            @click="viewMode = 'list'"
          >
            List
          </button>
        </div>
        
        <div class="calendar-navigation">
          <button @click="previousPeriod" class="nav-btn">‹</button>
          <button @click="goToToday" class="today-btn">Today</button>
          <button @click="nextPeriod" class="nav-btn">›</button>
        </div>
        
        <div class="current-period">
          <h2>{{ currentPeriodLabel }}</h2>
        </div>
      </div>
    </div>

    <!-- Calendar Grid -->
    <div v-if="viewMode === 'month'" class="calendar-grid">
      <!-- Weekday Headers -->
      <div class="weekday-headers">
        <div v-for="day in weekdays" :key="day" class="weekday-header">
          {{ day }}
        </div>
      </div>

      <!-- Calendar Days -->
      <div class="calendar-days">
        <div 
          v-for="day in calendarDays" 
          :key="day.date" 
          class="calendar-day"
          :class="{
            'other-month': !day.isCurrentMonth,
            'today': day.isToday,
            'selected': isDateSelected(day.date),
            'has-events': dayHasEvents(day.date)
          }"
          @click="selectDate(day.date)"
        >
          <div class="day-number">{{ day.dayNumber }}</div>
          
          <!-- Events for this day -->
          <div class="day-events">
            <div 
              v-for="event in getEventsForDate(day.date).slice(0, 3)" 
              :key="event.id"
              class="event-item"
              :class="`event-${event.status}`"
              @click.stop="showEventDetails(event)"
            >
              <div class="event-dot"></div>
              <div class="event-title">{{ event.vessel_name || event.id }}</div>
            </div>
            <div 
              v-if="getEventsForDate(day.date).length > 3" 
              class="more-events"
            >
              +{{ getEventsForDate(day.date).length - 3 }} more
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Week View -->
    <div v-if="viewMode === 'week'" class="week-view">
      <div class="week-header">
        <div class="time-column-header">Time</div>
        <div 
          v-for="day in weekDays" 
          :key="day.date" 
          class="week-day-header"
          :class="{ 'today': day.isToday }"
        >
          <div class="day-name">{{  day.dayName }}</div>
          <div class="day-number">{{ day.dayNumber }}</div>
        </div>
      </div>

      <div class="week-grid">
        <div class="time-column">
          <div v-for="hour in 24" :key="hour" class="time-slot">
            {{ hour.toString().padStart(2, '0') }}:00
          </div>
        </div>

        <div class="week-columns">
          <div v-for="day in weekDays" :key="day.date" class="week-day-column">
            <div v-for="hour in 24" :key="hour" class="time-slot-cell"></div>
            
            <!-- Events overlay -->
            <div class="events-overlay">
              <div 
                v-for="event in getEventsForDate(day.date)" 
                :key="event.id"
                class="week-event"
                :class="`event-${event.status}`"
                @click="showEventDetails(event)"
              >
                {{ event.vessel_name || event.id }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-if="viewMode === 'list'" class="list-view">
      <div v-if="loading" class="loading-state">
        <LoadingSpinner />
      </div>
      
      <div v-else-if="groupedEvents.length === 0" class="empty-state">
        <p>No scheduled voyages found</p>
      </div>
      
      <div v-else class="events-list">
        <div v-for="group in groupedEvents" :key="group.date" class="event-group">
          <div class="group-header">
            <h3>{{ formatGroupDate(group.date) }}</h3>
            <span class="event-count">{{ group.events.length }} voyage{{ group.events.length > 1 ? 's' : '' }}</span>
          </div>
          
          <div class="group-events">
            <div 
              v-for="event in group.events" 
              :key="event.id" 
              class="list-event-item"
              :class="`status-${event.status}`"
              @click="showEventDetails(event)"
            >
              <div class="event-icon">
                {{ getStatusIcon(event.status) }}
              </div>
              <div class="event-info">
                <div class="event-name">{{ event.vessel_name || 'Vessel' }}</div>
                <div class="event-meta">
                  <span class="event-status">{{ event.status }}</span>
                  <span v-if="event.route_name">• {{ event.route_name }}</span>
                  <span v-if="event.legs && event.legs.length">• {{ event.legs.length }} legs</span>
                </div>
              </div>
              <div class="event-time">
                {{ formatTime(event.startDate) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Details Modal -->
    <BaseModal v-if="selectedEvent" @close="selectedEvent = null">
      <template #header>
        <h3>Voyage Details</h3>
      </template>
      <template #body>
        <div class="event-details">
          <div class="detail-row">
            <span class="detail-label">ID:</span>
            <span class="detail-value">{{ selectedEvent.id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Vessel:</span>
            <span class="detail-value">{{ selectedEvent.vessel_name || getVesselName(selectedEvent.vesselId) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value">
              <span :class="`status-badge status-${selectedEvent.status}`">
                {{ selectedEvent.status }}
              </span>
            </span>
          </div>
          <div class="detail-row" v-if="selectedEvent.startDate">
            <span class="detail-label">Start Date:</span>
            <span class="detail-value">{{ formatDateTime(selectedEvent.startDate) }}</span>
          </div>
          <div class="detail-row" v-if="selectedEvent.route_name">
            <span class="detail-label">Route:</span>
            <span class="detail-value">{{ selectedEvent.route_name }}</span>
          </div>
          <div class="detail-row" v-if="selectedEvent.legs && selectedEvent.legs.length">
            <span class="detail-label">Total Legs:</span>
            <span class="detail-value">{{ selectedEvent.legs.length }}</span>
          </div>
          
          <div v-if="selectedEvent.legs && selectedEvent.legs.length" class="legs-section">
            <h4>Route Legs</h4>
            <div class="legs-list">
              <div v-for="(leg, index) in selectedEvent.legs" :key="index" class="leg-item">
                <span class="leg-number">{{ index + 1 }}</span>
                <span class="leg-type">{{ leg.type }}</span>
                <span class="leg-route">{{ leg.from || 'Port' }} → {{ leg.to || 'Port' }}</span>
                <span v-if="leg.distance" class="leg-distance">{{ leg.distance }} nm</span>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <button @click="selectedEvent = null" class="btn btn-secondary">Close</button>
        <button @click="editEvent(selectedEvent)" class="btn btn-primary">Edit</button>
      </template>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useVoyageStore } from '@/stores/voyage'
import { useVesselStore } from '@/stores/vessel'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import BaseModal from '@/components/shared/BaseModal.vue'
import type { Voyage } from '@/types/voyage.types'

const router = useRouter()
const voyageStore = useVoyageStore()
const vesselStore = useVesselStore()

const viewMode = ref<'month' | 'week' | 'list'>('month')
const currentDate = ref(new Date())
const selectedDate = ref<string | null>(null)
const selectedEvent = ref<Voyage | null>(null)
const loading = ref(false)

const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const currentPeriodLabel = computed(() => {
  if (viewMode.value === 'month') {
    return currentDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  } else if (viewMode.value === 'week') {
    const weekStart = getWeekStart(currentDate.value)
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekEnd.getDate() + 6)
    return `${weekStart.toLocaleDateString('en-US',{ month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
  }
  return currentDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())
  
  const endDate = new Date(lastDay)
  endDate.setDate(endDate.getDate() + (6 - lastDay.getDay()))
  
  const days = []
  const currentIterDate = new Date(startDate)
  
  while (currentIterDate <= endDate) {
    const dateStr = currentIterDate.toISOString().split('T')[0]
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    days.push({
      date: dateStr,
      dayNumber: currentIterDate.getDate(),
      isCurrentMonth: currentIterDate.getMonth() === month,
      isToday: currentIterDate.toDateString() === today.toDateString()
    })
    
    currentIterDate.setDate(currentIterDate.getDate() + 1)
  }
  
  return days
})

const weekDays = computed(() => {
  const weekStart = getWeekStart(currentDate.value)
  const days = []
  
  for (let i = 0; i < 7; i++) {
    const day = new Date(weekStart)
    day.setDate(day.getDate() + i)
    
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    days.push({
      date: day.toISOString().split('T')[0],
      dayName: day.toLocaleDateString('en-US', { weekday: 'short' }),
      dayNumber: day.getDate(),
      isToday: day.toDateString() === today.toDateString()
    })
  }
  
  return days
})

const groupedEvents = computed(() => {
  const events = voyageStore.voyages
  const grouped = new Map<string, Voyage[]>()
  
  events.forEach(event => {
    if (event.startDate) {
      const date = event.startDate.split('T')[0]
      if (!grouped.has(date)) {
        grouped.set(date, [])
      }
      grouped.get(date)!.push(event)
    }
  })
  
  return Array.from(grouped.entries())
    .map(([date, events]) => ({ date, events }))
    .sort((a, b) => a.date.localeCompare(b.date))
})

function getWeekStart(date: Date): Date {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day
  return new Date(d.setDate(diff))
}

function previousPeriod() {
  if (viewMode.value === 'month') {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
  } else if (viewMode.value === 'week') {
    const newDate = new Date(currentDate.value)
    newDate.setDate(newDate.getDate() - 7)
    currentDate.value = newDate
  }
}

function nextPeriod() {
  if (viewMode.value === 'month') {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
  } else if (viewMode.value === 'week') {
    const newDate = new Date(currentDate.value)
    newDate.setDate(newDate.getDate() + 7)
    currentDate.value = newDate
  }
}

function goToToday() {
  currentDate.value = new Date()
}

function selectDate(date: string) {
  selectedDate.value = date === selectedDate.value ? null : date
}

function isDateSelected(date: string): boolean {
  return selectedDate.value === date
}

function dayHasEvents(date: string): boolean {
  return getEventsForDate(date).length > 0
}

function getEventsForDate(date: string): Voyage[] {
  return voyageStore.voyages.filter(voyage => {
    if (!voyage.startDate) return false
    const voyageDate = voyage.startDate.split('T')[0]
    return voyageDate === date
  })
}

function showEventDetails(event: Voyage) {
  selectedEvent.value = event
}

function editEvent(event: Voyage) {
  router.push(`/voyages/${event.id}/edit`)
}

function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    planned: '',
    active: '',
    completed: '',
    cancelled: ''
  }
  return icons[status] || ''
}

function getVesselName(vesselId: string | null): string {
  if (!vesselId) return 'Unknown'
  const vessel = vesselStore.vessels.find(v => v.id === vesselId)
  return vessel ? vessel.name : 'Unknown'
}

function formatGroupDate(dateStr: string): string {
  const date = new Date(dateStr)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const dateOnly = new Date(date)
  dateOnly.setHours(0, 0, 0, 0)
  
  const diffTime = dateOnly.getTime() - today.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Tomorrow'
  if (diffDays === -1) return 'Yesterday'
  
  return date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
}

function formatTime(dateStr: string | undefined): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { 
    weekday: 'short',
    month: 'short', 
    day: 'numeric', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      voyageStore.fetchVoyages(),
      vesselStore.fetchVessels()
    ])
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.schedule-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.schedule-header {
  margin-bottom: 2rem;
}

.schedule-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
}

.header-controls {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 8px;
}

.view-toggle button {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: #64748b;
  font-weight: 600;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.view-toggle button.active {
  background: white;
  color: #42b983;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.calendar-navigation {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.nav-btn,
.today-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  background: white;
  color: #2c3e50;
  font-weight: 600;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-btn:hover,
.today-btn:hover {
  background: #f8fafc;
  border-color: #42b983;
}

.current-period h2 {
  font-size: 1.25rem;
  color: #2c3e50;
  margin: 0;
}

.calendar-grid {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.weekday-headers {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f8fafc;
  border-bottom: 2px solid #e2e8f0;
}

.weekday-header {
  padding: 1rem;
  text-align: center;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  font-size: 0.875rem;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #e2e8f0;
}

.calendar-day {
  background: white;
  min-height: 120px;
  padding: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.calendar-day:hover {
  background: #f8fafc;
}

.calendar-day.other-month {
  background: #f8fafc;
  opacity: 0.5;
}

.calendar-day.today {
  background: #f0fdf4;
}

.calendar-day.selected {
  background: #ecfdf5;
  outline: 2px solid #42b983;
}

.day-number {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.calendar-day.today .day-number {
  color: #42b983;
  font-weight: 700;
}

.day-events {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem;
  border-radius: 4px;
  font-size: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-planned {
  background: #fef3c7;
  color: #92400e;
}

.event-active {
  background: #dbeafe;
  color: #1e40af;
}

.event-completed {
  background: #d1fae5;
  color: #065f46;
}

.event-cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.event-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}

.event-title {
  overflow: hidden;
  text-overflow: ellipsis;
}

.more-events {
  font-size: 0.75rem;
  color: #64748b;
  padding: 0.25rem;
  text-align: center;
}

.week-view {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.week-header {
  display: grid;
  grid-template-columns: 80px repeat(7, 1fr);
  background: #f8fafc;
  border-bottom: 2px solid #e2e8f0;
}

.time-column-header {
  padding: 1rem;
  font-weight: 600;
  color: #64748b;
  border-right: 1px solid #e2e8f0;
}

.week-day-header {
  padding: 1rem;
  text-align: center;
  border-right: 1px solid #e2e8f0;
}

.week-day-header:last-child {
  border-right: none;
}

.week-day-header.today {
  background: #ecfdf5;
  color: #42b983;
}

.day-name {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.875rem;
}

.day-number {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 0.25rem;
}

.week-grid {
  display: grid;
  grid-template-columns: 80px 1fr;
  max-height: 600px;
  overflow-y: auto;
}

.time-column {
  border-right: 2px solid #e2e8f0;
}

.time-slot {
  height: 60px;
  padding: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
}

.week-columns {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.week-day-column {
  position: relative;
  border-right: 1px solid #e2e8f0;
}

.week-day-column:last-child {
  border-right: none;
}

.time-slot-cell {
  height: 60px;
  border-bottom: 1px solid #e2e8f0;
}

.events-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.week-event {
  position: relative;
  margin: 0.25rem;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  pointer-events: auto;
  cursor: pointer;
  transition: transform 0.2s;
}

.week-event:hover {
  transform: scale(1.02);
}

.list-view {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #94a3b8;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.event-group {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.group-header {
  background: #f8fafc;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}

.group-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: #2c3e50;
}

.event-count {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 600;
}

.group-events {
  display: flex;
  flex-direction: column;
}

.list-event-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background 0.2s;
}

.list-event-item:last-child {
  border-bottom: none;
}

.list-event-item:hover {
  background: #f8fafc;
}

.event-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #f1f5f9;
}

.event-info {
  flex: 1;
}

.event-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.event-meta {
  font-size: 0.875rem;
  color: #64748b;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.event-status {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
  text-transform: capitalize;
}

.status-planned .event-status {
  background: #fef3c7;
  color: #92400e;
}

.status-active .event-status {
  background: #dbeafe;
  color: #1e40af;
}

.status-completed .event-status {
  background: #d1fae5;
  color: #065f46;
}

.status-cancelled .event-status {
  background: #fee2e2;
  color: #991b1b;
}

.event-time {
  font-weight: 600;
  color: #64748b;
}

.event-details {
  padding: 1rem 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.detail-label {
  font-weight: 600;
  color: #64748b;
}

.detail-value {
  color: #2c3e50;
  font-weight: 500;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.legs-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e2e8f0;
}

.legs-section h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.legs-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.leg-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 6px;
  font-size: 0.875rem;
}

.leg-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #42b983;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.75rem;
}

.leg-type {
  padding: 0.25rem 0.5rem;
  background: #e2e8f0;
  border-radius: 4px;
  font-weight: 600;
  text-transform: capitalize;
}

.leg-route {
  flex: 1;
  color: #2c3e50;
}

.leg-distance {
  color: #64748b;
  font-weight: 600;
}

.btn {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #42b983;
  color: white;
}

.btn-primary:hover {
  background: #369970;
}

.btn-secondary {
  background: #64748b;
  color: white;
}

.btn-secondary:hover {
  background: #475569;
}

@media (max-width: 768px) {
  .schedule-view {
    padding: 1rem;
  }

  .header-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .calendar-days {
    gap: 0;
  }

  .calendar-day {
    min-height: 80px;
    font-size: 0.875rem;
  }

  .event-item {
    font-size: 0.65rem;
  }

  .week-header,
  .week-grid {
    grid-template-columns: 60px repeat(7, 1fr);
  }
}
</style>
