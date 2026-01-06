/**
 * Comprehensive Tests for GlobalFiltersBar State Management
 * 
 * Tests include:
 * - Filter state initialization
 * - Filter state updates
 * - Filter persistence
 * - Multiple filter combinations
 * - Edge cases and error scenarios
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useCalendarStore } from '@/stores/calendar'

describe('GlobalFiltersBar State Management', () => {
  let store: ReturnType<typeof useCalendarStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useCalendarStore()
  })

  describe('Filter Initialization', () => {
    it('should initialize with default filter values', () => {
      expect(store.filters.module).toBe('all')
      expect(store.filters.vessel).toBe('all')
      expect(store.filters.status).toBe('all')
      expect(store.filters.searchQuery).toBe('')
    })

    it('should have filteredEvents computed property defined', () => {
      expect(store.filteredEvents).toBeDefined()
      expect(Array.isArray(store.filteredEvents)).toBe(true)
    })

    it('should have statistics computed property defined', () => {
      expect(store.statistics).toBeDefined()
      expect(store.statistics).toHaveProperty('totalVoyages')
      expect(store.statistics).toHaveProperty('activeVessels')
      expect(store.statistics).toHaveProperty('totalCargo')
      expect(store.statistics).toHaveProperty('totalCost')
    })
  })

  describe('Module Filter', () => {
    beforeEach(() => {
      // Setup sample events
      store.events = [
        {
          id: '1',
          title: 'Voyage 1',
          module: 'deepsea',
          vessel: 'Vessel A',
          start: new Date('2025-01-01'),
          end: new Date('2025-01-05'),
          status: 'planned',
          cargo: 1000,
          cost: 50000,
          route: 'Port A → Port B',
          details: {}
        },
        {
          id: '2',
          title: 'Voyage 2',
          module: 'olya',
          vessel: 'Vessel B',
          start: new Date('2025-01-10'),
          end: new Date('2025-01-15'),
          status: 'in-progress',
          cargo: 1500,
          cost: 75000,
          route: 'Port C → Port D',
          details: {}
        }
      ]
    })

    it('should filter events by deepsea module', () => {
      store.updateFilters({ module: 'deepsea' })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].module).toBe('deepsea')
    })

    it('should filter events by olya module', () => {
      store.updateFilters({ module: 'olya' })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].module).toBe('olya')
    })

    it('should show all events when module is "all"', () => {
      store.updateFilters({ module: 'all' })
      
      expect(store.filteredEvents).toHaveLength(2)
    })

    it('should return empty array for balakovo module when no events exist', () => {
      store.updateFilters({ module: 'balakovo' })
      
      expect(store.filteredEvents).toHaveLength(0)
    })
  })

  describe('Vessel Filter', () => {
    beforeEach(() => {
      store.events = [
        {
          id: '1',
          title: 'Voyage 1',
          module: 'deepsea',
          vessel: 'Vessel A',
          start: new Date('2025-01-01'),
          end: new Date('2025-01-05'),
          status: 'planned',
          cargo: 1000,
          cost: 50000,
          route: 'Port A → Port B',
          details: {}
        },
        {
          id: '2',
          title: 'Voyage 2',
          module: 'deepsea',
          vessel: 'Vessel B',
          start: new Date('2025-01-10'),
          end: new Date('2025-01-15'),
          status: 'planned',
          cargo: 1500,
          cost: 75000,
          route: 'Port C → Port D',
          details: {}
        }
      ]
    })

    it('should filter events by specific vessel', () => {
      store.updateFilters({ vessel: 'Vessel A' })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].vessel).toBe('Vessel A')
    })

    it('should show all vessels when filter is "all"', () => {
      store.updateFilters({ vessel: 'all' })
      
      expect(store.filteredEvents).toHaveLength(2)
    })

    it('should return empty array for non-existent vessel', () => {
      store.updateFilters({ vessel: 'Non-existent Vessel' })
      
      expect(store.filteredEvents).toHaveLength(0)
    })
  })

  describe('Status Filter', () => {
    beforeEach(() => {
      store.events = [
        {
          id: '1',
          title: 'Planned Voyage',
          module: 'deepsea',
          vessel: 'Vessel A',
          start: new Date('2025-12-01'),
          end: new Date('2025-12-05'),
          status: 'planned',
          cargo: 1000,
          cost: 50000,
          route: 'Port A → Port B',
          details: {}
        },
        {
          id: '2',
          title: 'In Progress Voyage',
          module: 'deepsea',
          vessel: 'Vessel B',
          start: new Date('2025-01-01'),
          end: new Date('2026-01-01'),
          status: 'in-progress',
          cargo: 1500,
          cost: 75000,
          route: 'Port C → Port D',
          details: {}
        },
        {
          id: '3',
          title: 'Completed Voyage',
          module: 'olya',
          vessel: 'Vessel C',
          start: new Date('2024-01-01'),
          end: new Date('2024-01-05'),
          status: 'completed',
          cargo: 2000,
          cost: 100000,
          route: 'Port E → Port F',
          details: {}
        }
      ]
    })

    it('should filter events by planned status', () => {
      store.updateFilters({ status: 'planned' })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].status).toBe('planned')
    })

    it('should filter events by in-progress status', () => {
      store.updateFilters({ status: 'in-progress' })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].status).toBe('in-progress')
    })

    it('should filter events by completed status', () => {
      store.updateFilters({ status: 'completed' })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].status).toBe('completed')
    })

    it('should show all statuses when filter is "all"', () => {
      store.updateFilters({ status: 'all' })
      
      expect(store.filteredEvents).toHaveLength(3)
    })
  })

  describe('Search Query Filter', () => {
    beforeEach(() => {
      store.events = [
        {
          id: '1',
          title: 'Coal Transport',
          module: 'deepsea',
          vessel: 'Coal Carrier Alpha',
          start: new Date('2025-01-01'),
          end: new Date('2025-01-05'),
          status: 'planned',
          cargo: 1000,
          cost: 50000,
          route: 'Rotterdam → Shanghai',
          details: {}
        },
        {
          id: '2',
          title: 'Oil Shipment',
          module: 'deepsea',
          vessel: 'Tanker Beta',
          start: new Date('2025-01-10'),
          end: new Date('2025-01-15'),
          status: 'planned',
          cargo: 1500,
          cost: 75000,
          route: 'Dubai → Singapore',
          details: {}
        }
      ]
    })

    it('should filter events by title search', () => {
      store.updateFilters({ searchQuery: 'coal' })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].title.toLowerCase()).toContain('coal')
    })

    it('should filter events by vessel search', () => {
      store.updateFilters({ searchQuery: 'tanker' })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].vessel.toLowerCase()).toContain('tanker')
    })

    it('should filter events by route search', () => {
      store.updateFilters({ searchQuery: 'shanghai' })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].route.toLowerCase()).toContain('shanghai')
    })

    it('should be case-insensitive', () => {
      store.updateFilters({ searchQuery: 'COAL' })
      
      expect(store.filteredEvents).toHaveLength(1)
    })

    it('should show all events when search query is empty', () => {
      store.updateFilters({ searchQuery: '' })
      
      expect(store.filteredEvents).toHaveLength(2)
    })

    it('should return empty array when no match found', () => {
      store.updateFilters({ searchQuery: 'nonexistent' })
      
      expect(store.filteredEvents).toHaveLength(0)
    })
  })

  describe('Date Range Filter', () => {
    beforeEach(() => {
      store.events = [
        {
          id: '1',
          title: 'Voyage 1',
          module: 'deepsea',
          vessel: 'Vessel A',
          start: new Date('2025-01-01'),
          end: new Date('2025-01-05'),
          status: 'planned',
          cargo: 1000,
          cost: 50000,
          route: 'Port A → Port B',
          details: {}
        },
        {
          id: '2',
          title: 'Voyage 2',
          module: 'deepsea',
          vessel: 'Vessel B',
          start: new Date('2025-06-01'),
          end: new Date('2025-06-10'),
          status: 'planned',
          cargo: 1500,
          cost: 75000,
          route: 'Port C → Port D',
          details: {}
        }
      ]
    })

    it('should filter events within date range', () => {
      store.updateFilters({ 
        dateRange: {
          start: new Date('2025-01-01'),
          end: new Date('2025-01-31')
        }
      })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].id).toBe('1')
    })

    it('should filter events that overlap with date range', () => {
      store.updateFilters({ 
        dateRange: {
          start: new Date('2025-01-03'),
          end: new Date('2025-01-07')
        }
      })
      
      expect(store.filteredEvents).toHaveLength(1)
    })

    it('should exclude events outside date range', () => {
      store.updateFilters({ 
        dateRange: {
          start: new Date('2025-02-01'),
          end: new Date('2025-02-28')
        }
      })
      
      expect(store.filteredEvents).toHaveLength(0)
    })
  })

  describe('Multiple Filters', () => {
    beforeEach(() => {
      store.events = [
        {
          id: '1',
          title: 'Coal Transport',
          module: 'deepsea',
          vessel: 'Vessel A',
          start: new Date('2025-01-01'),
          end: new Date('2025-01-05'),
          status: 'planned',
          cargo: 1000,
          cost: 50000,
          route: 'Port A → Port B',
          details: {}
        },
        {
          id: '2',
          title: 'Oil Shipment',
          module: 'olya',
          vessel: 'Vessel A',
          start: new Date('2025-01-10'),
          end: new Date('2025-01-15'),
          status: 'in-progress',
          cargo: 1500,
          cost: 75000,
          route: 'Port C → Port D',
          details: {}
        },
        {
          id: '3',
          title: 'Coal Transport',
          module: 'deepsea',
          vessel: 'Vessel B',
          start: new Date('2025-01-20'),
          end: new Date('2025-01-25'),
          status: 'completed',
          cargo: 2000,
          cost: 100000,
          route: 'Port E → Port F',
          details: {}
        }
      ]
    })

    it('should apply module and vessel filters together', () => {
      store.updateFilters({ 
        module: 'deepsea',
        vessel: 'Vessel A'
      })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].id).toBe('1')
    })

    it('should apply module, vessel, and status filters together', () => {
      store.updateFilters({ 
        module: 'deepsea',
        vessel: 'Vessel B',
        status: 'completed'
      })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].id).toBe('3')
    })

    it('should apply all filters including search', () => {
      store.updateFilters({ 
        module: 'deepsea',
        searchQuery: 'coal',
        status: 'planned'
      })
      
      expect(store.filteredEvents).toHaveLength(1)
      expect(store.filteredEvents[0].id).toBe('1')
    })

    it('should return empty when no events match all filters', () => {
      store.updateFilters({ 
        module: 'deepsea',
        vessel: 'Vessel A',
        status: 'completed'
      })
      
      expect(store.filteredEvents).toHaveLength(0)
    })
  })

  describe('Filter Reset', () => {
    it('should reset all filters to default values', () => {
      store.updateFilters({
        module: 'deepsea',
        vessel: 'Vessel A',
        status: 'planned',
        searchQuery: 'test'
      })
      
      store.resetFilters()
      
      expect(store.filters.module).toBe('all')
      expect(store.filters.vessel).toBe('all')
      expect(store.filters.status).toBe('all')
      expect(store.filters.searchQuery).toBe('')
      expect(store.filters.dateRange).toBeUndefined()
    })
  })

  describe('Statistics Calculation', () => {
    beforeEach(() => {
      store.events = [
        {
          id: '1',
          title: 'Voyage 1',
          module: 'deepsea',
          vessel: 'Vessel A',
          start: new Date('2025-01-01'),
          end: new Date('2025-01-05'),
          status: 'planned',
          cargo: 1000,
          cost: 50000,
          route: 'Port A → Port B',
          details: {}
        },
        {
          id: '2',
          title: 'Voyage 2',
          module: 'deepsea',
          vessel: 'Vessel B',
          start: new Date('2025-01-10'),
          end: new Date('2025-01-15'),
          status: 'planned',
          cargo: 1500,
          cost: 75000,
          route: 'Port C → Port D',
          details: {}
        },
        {
          id: '3',
          title: 'Voyage 3',
          module: 'olya',
          vessel: 'Vessel A',
          start: new Date('2025-01-20'),
          end: new Date('2025-01-25'),
          status: 'completed',
          cargo: 2000,
          cost: 100000,
          route: 'Port E → Port F',
          details: {}
        }
      ]
    })

    it('should calculate total voyages correctly', () => {
      expect(store.statistics.totalVoyages).toBe(3)
    })

    it('should calculate active vessels correctly', () => {
      expect(store.statistics.activeVessels).toBe(2)
    })

    it('should calculate total cargo correctly', () => {
      expect(store.statistics.totalCargo).toBe(4500)
    })

    it('should calculate total cost correct ly', () => {
      expect(store.statistics.totalCost).toBe(225000)
    })

    it('should recalculate statistics after filtering', () => {
      store.updateFilters({ module: 'deepsea' })
      
      expect(store.statistics.totalVoyages).toBe(2)
      expect(store.statistics.activeVessels).toBe(2)
      expect(store.statistics.totalCargo).toBe(2500)
      expect(store.statistics.totalCost).toBe(125000)
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty events array', () => {
      store.events = []
      
      expect(store.filteredEvents).toHaveLength(0)
      expect(store.statistics.totalVoyages).toBe(0)
      expect(store.statistics.activeVessels).toBe(0)
    })

    it('should handle missing cargo values', () => {
      store.events = [
        {
          id: '1',
          title: 'Voyage 1',
          module: 'deepsea',
          vessel: 'Vessel A',
          start: new Date('2025-01-01'),
          end: new Date('2025-01-05'),
          status: 'planned',
          cargo: undefined,
          cost: 50000,
          route: 'Port A → Port B',
          details: {}
        }
      ]
      
      expect(store.statistics.totalCargo).toBe(0)
    })

    it('should handle missing cost values', () => {
      store.events = [
        {
          id: '1',
          title: 'Voyage 1',
          module: 'deepsea',
          vessel: 'Vessel A',
          start: new Date('2025-01-01'),
          end: new Date('2025-01-05'),
          status: 'planned',
          cargo: 1000,
          cost: undefined,
          route: 'Port A → Port B',
          details: {}
        }
      ]
      
      expect(store.statistics.totalCost).toBe(0)
    })

    it('should handle special characters in search query', () => {
      store.events = [
        {
          id: '1',
          title: 'Voyage #1 (Test)',
          module: 'deepsea',
          vessel: 'Vessel A',
          start: new Date('2025-01-01'),
          end: new Date('2025-01-05'),
          status: 'planned',
          cargo: 1000,
          cost: 50000,
          route: 'Port A → Port B',
          details: {}
        }
      ]
      
      store.updateFilters({ searchQuery: '#1' })
      
      expect(store.filteredEvents).toHaveLength(1)
    })
  })

  describe('Unique Vessels', () => {
    beforeEach(() => {
      store.events = [
        {
          id: '1',
          title: 'Voyage 1',
          module: 'deepsea',
          vessel: 'Vessel C',
          start: new Date('2025-01-01'),
          end: new Date('2025-01-05'),
          status: 'planned',
          cargo: 1000,
          cost: 50000,
          route: 'Port A → Port B',
          details: {}
        },
        {
          id: '2',
          title: 'Voyage 2',
          module: 'deepsea',
          vessel: 'Vessel A',
          start: new Date('2025-01-10'),
          end: new Date('2025-01-15'),
          status: 'planned',
          cargo: 1500,
          cost: 75000,
          route: 'Port C → Port D',
          details: {}
        },
        {
          id: '3',
          title: 'Voyage 3',
          module: 'olya',
          vessel: 'Vessel A',
          start: new Date('2025-01-20'),
          end: new Date('2025-01-25'),
          status: 'completed',
          cargo: 2000,
          cost: 100000,
          route: 'Port E → Port F',
          details: {}
        },
        {
          id: '4',
          title: 'Voyage 4',
          module: 'balakovo',
          vessel: 'Vessel B',
          start: new Date('2025-01-25'),
          end: new Date('2025-01-30'),
          status: 'planned',
          cargo: 800,
          cost: 40000,
          route: 'Port G → Port H',
          details: {}
        }
      ]
    })

    it('should return unique vessels', () => {
      const vessels = store.uniqueVessels
      
      expect(vessels).toHaveLength(3)
      expect(vessels).toContain('Vessel A')
      expect(vessels).toContain('Vessel B')
      expect(vessels).toContain('Vessel C')
    })

    it('should return vessels in alphabetical order', () => {
      const vessels = store.uniqueVessels
      
      expect(vessels).toEqual(['Vessel A', 'Vessel B', 'Vessel C'])
    })
  })
})
