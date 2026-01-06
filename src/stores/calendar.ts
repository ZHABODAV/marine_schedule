import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  CalendarEvent,
  CalendarViewType,
  FilterOptions,
  CalendarStatistics,
  Module,
  EventStatus
} from '@/types/calendar.types'

export const useCalendarStore = defineStore('calendar', () => {
  // State
  const currentDate = ref<Date>(new Date())
  const viewType = ref<CalendarViewType>('month')
  const events = ref<CalendarEvent[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  const filters = ref<FilterOptions>({
    module: 'all' as Module,
    vessel: 'all',
    status: 'all' as EventStatus | 'all',
    searchQuery: ''
  })

  // Getters
  const filteredEvents = computed(() => {
    return events.value.filter(event => {
      // Module filter
      if (filters.value.module !== 'all' && event.module !== filters.value.module) {
        return false
      }
      
      // Vessel filter
      if (filters.value.vessel !== 'all' && event.vessel !== filters.value.vessel) {
        return false
      }
      
      // Status filter
      if (filters.value.status !== 'all' && event.status !== filters.value.status) {
        return false
      }
      
      // Search filter
      if (filters.value.searchQuery) {
        const searchText = `${event.title} ${event.route} ${event.vessel}`.toLowerCase()
        if (!searchText.includes(filters.value.searchQuery.toLowerCase())) {
          return false
        }
      }
      
      // Date range filter
      if (filters.value.dateRange) {
        const eventStart = new Date(event.start)
        const eventEnd = new Date(event.end)
        const filterStart = filters.value.dateRange.start
        const filterEnd = filters.value.dateRange.end
        
        if (eventEnd < filterStart || eventStart > filterEnd) {
          return false
        }
      }
      
      return true
    })
  })

  const statistics = computed<CalendarStatistics>(() => {
    const filtered = filteredEvents.value
    
    return {
      totalVoyages: filtered.length,
      activeVessels: [...new Set(filtered.map(e => e.vessel))].length,
      totalCargo: filtered.reduce((sum, e) => sum + (e.cargo || 0), 0),
      totalCost: filtered.reduce((sum, e) => sum + (e.cost || 0), 0)
    }
  })

  const upcomingEvents = computed(() => {
    const now = new Date()
    return filteredEvents.value
      .filter(e => new Date(e.start) > now)
      .sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())
      .slice(0, 10)
  })

  const uniqueVessels = computed(() => {
    return [...new Set(events.value.map(e => e.vessel))].sort()
  })

  // Actions
  async function fetchEvents() {
    loading.value = true
    error.value = null
    
    try {
      // Load events from all modules
      const [deepseaData, olyaData, balakovoData] = await Promise.all([
        fetchDeepSeaEvents(),
        fetchOlyaEvents(),
        fetchBalakovoEvents()
      ])
      
      events.value = [...deepseaData, ...olyaData, ...balakovoData]
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load events'
      console.error('Error fetching calendar events:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchDeepSeaEvents(): Promise<CalendarEvent[]> {
    try {
      const response = await fetch('/api/deepsea/voyages/calculated')
      if (!response.ok) return []
      
      const data = await response.json()
      return Object.values(data.calculated_voyages || {}).map((voyage: any) => ({
        id: voyage.voyage_id,
        title: `${voyage.vessel_id}: ${voyage.cargo_type}`,
        module: 'deepsea' as const,
        vessel: voyage.vessel_id,
        start: new Date(voyage.laycan_start),
        end: new Date(voyage.laycan_end),
        status: determineStatus(voyage.laycan_start, voyage.laycan_end),
        cargo: voyage.qty_mt,
        cost: voyage.total_cost_usd,
        route: `${voyage.load_port} → ${voyage.discharge_port}`,
        details: voyage
      }))
    } catch (err) {
      console.warn('Deep Sea data not available:', err)
      return []
    }
  }

  async function fetchOlyaEvents(): Promise<CalendarEvent[]> {
    try {
      const response = await fetch('/api/olya/voyages')
      if (!response.ok) return []
      
      const data = await response.json()
      return (data.voyages || []).map((voyage: any) => ({
        id: voyage.voyage_id || `OLYA_${Math.random()}`,
        title: `${voyage.vessel_name}: ${voyage.cargo_name || 'Cargo'}`,
        module: 'olya' as const,
        vessel: voyage.vessel_name,
        start: new Date(voyage.start_date || Date.now()),
        end: new Date(voyage.end_date || Date.now()),
        status: 'planned' as EventStatus,
        cargo: voyage.cargo_qty || 0,
        cost: voyage.total_cost || 0,
        route: `${voyage.from_port || 'Origin'} → ${voyage.to_port || 'Destination'}`,
        details: voyage
      }))
    } catch (err) {
      console.warn('Olya data not available:', err)
      return []
    }
  }

  async function fetchBalakovoEvents(): Promise<CalendarEvent[]> {
    try {
      const response = await fetch('/api/balakovo/voyages')
      if (!response.ok) return []
      
      const data = await response.json()
      
      // Transform Balakovo data to CalendarEvent format
      return (data.voyages || []).map((voyage: any) => {
        const startDate = voyage.departure_time || voyage.load_time || Date.now()
        const endDate = voyage.arrival_time || voyage.discharge_time || Date.now()
        
        return {
          id: voyage.voyage_id || `BALAKOVO_${Math.random()}`,
          title: `${voyage.vessel_name || 'Unknown'}: ${voyage.cargo || 'River Cargo'}`,
          module: 'balakovo' as const,
          vessel: voyage.vessel_name || 'Unknown Vessel',
          start: new Date(startDate),
          end: new Date(endDate),
          status: determineStatus(startDate.toString(), endDate.toString()),
          cargo: voyage.cargo_qty_mt || voyage.qty_mt || 0,
          cost: voyage.total_cost || voyage.voyage_cost || 0,
          route: `${voyage.from_port || voyage.load_port || 'Origin'} → ${voyage.to_port || voyage.discharge_port || 'Destination'}`,
          details: {
            ...voyage,
            berth: voyage.berth_name || voyage.berth_id,
            loadingRate: voyage.loading_rate_mt_day,
            waitingTime: voyage.waiting_time_days
          }
        }
      })
    } catch (err) {
      console.warn('Balakovo data not available:', err)
      return []
    }
  }

  function determineStatus(startDate: string, endDate: string): EventStatus {
    const now = new Date()
    const start = new Date(startDate)
    const end = new Date(endDate)
    
    if (now < start) return 'planned'
    if (now > end) return 'completed'
    return 'in-progress'
  }

  function setViewType(type: CalendarViewType) {
    viewType.value = type
  }

  function setCurrentDate(date: Date) {
    currentDate.value = date
  }

  function navigatePrevious() {
    const newDate = new Date(currentDate.value)
    if (viewType.value === 'year') {
      newDate.setFullYear(newDate.getFullYear() - 1)
    } else {
      newDate.setMonth(newDate.getMonth() - 1)
    }
    currentDate.value = newDate
  }

  function navigateNext() {
    const newDate = new Date(currentDate.value)
    if (viewType.value === 'year') {
      newDate.setFullYear(newDate.getFullYear() + 1)
    } else {
      newDate.setMonth(newDate.getMonth() + 1)
    }
    currentDate.value = newDate
  }

  function navigateToday() {
    currentDate.value = new Date()
  }

  function updateFilters(newFilters: Partial<FilterOptions>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function resetFilters() {
    filters.value = {
      module: 'all',
      vessel: 'all',
      status: 'all',
      searchQuery: ''
    }
  }

  return {
    // State
    currentDate,
    viewType,
    events,
    loading,
    error,
    filters,
    
    // Getters
    filteredEvents,
    statistics,
    upcomingEvents,
    uniqueVessels,
    
    // Actions
    fetchEvents,
    setViewType,
    setCurrentDate,
    navigatePrevious,
    navigateNext,
    navigateToday,
    updateFilters,
    resetFilters
  }
})
