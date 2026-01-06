import { describe, it, expect, beforeEach, vi } from 'vitest';
import { generateGanttFromVoyages } from './schedule-generator.js';

// Mock dependencies
vi.mock('../core/app-state.js', () => ({
  appState: {
    filters: { opTypes: [] },
    vessels: [
      { id: 'V1', name: 'Vessel 1', status: 'Active' },
      { id: 'V2', name: 'Vessel 2', status: 'Active' }
    ],
    currentModule: 'deepsea'
  },
  getCurrentData: vi.fn(() => ({
    masters: {
      vessels: [
        { id: 'V1', name: 'Vessel 1', speed: 14 },
        { id: 'V2', name: 'Vessel 2', speed: 15 }
      ],
      routes: [
        { from: 'Port A', to: 'Port B', distance: 1000 }
      ],
      ports: [
        { name: 'Port A', loadRate: 5000, dischRate: 4000 },
        { name: 'Port B', loadRate: 5000, dischRate: 4000 }
      ]
    },
    planning: {
      commitments: [
        { id: 'C1', status: 'Pending', loadPort: 'Port A', dischPort: 'Port B', quantity: 10000, laycanStart: '2024-01-15' }
      ]
    },
    computed: {
      voyages: []
    }
  }))
}));

vi.mock('../core/utilities.js', () => ({
  showNotification: vi.fn(),
  toNumber: vi.fn((v) => {
    if (v === null || v === undefined) return 0;
    const s = String(v).trim();
    if (!s) return 0;
    const n = Number(s.replace(',', '.'));
    return Number.isFinite(n) ? n : 0;
  })
}));

vi.mock('../ui/filters.js', () => ({
  applyFiltersToData: vi.fn((data) => data || [])
}));

vi.mock('../services/storage-service.js', () => ({
  saveToLocalStorage: vi.fn()
}));

describe('schedule-generator', () => {
  describe('generateGanttFromVoyages()', () => {
    let sampleVoyages;

    beforeEach(() => {
      sampleVoyages = [
        {
          id: 'VOY-1',
          vesselId: 'V1',
          startDate: new Date().toISOString(),
          legs: [
            { type: 'ballast', duration: 24 },
            { type: 'loading', duration: 12 },
            { type: 'transit', duration: 48 },
            { type: 'discharge', duration: 12 }
          ]
        },
        {
          id: 'VOY-2',
          vesselId: 'V2',
          startDate: new Date().toISOString(),
          legs: [
            { type: 'loading', duration: 24 },
            { type: 'transit', duration: 72 }
          ]
        }
      ];
    });

    it('should generate Gantt data from voyages', () => {
      const result = generateGanttFromVoyages(sampleVoyages, 30);
      
      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
    });

    it('should create correct structure', () => {
      const result = generateGanttFromVoyages(sampleVoyages, 30);
      
      result.forEach(row => {
        expect(row).toHaveProperty('vessel');
        expect(row).toHaveProperty('days');
        expect(Array.isArray(row.days)).toBe(true);
        expect(row.days.length).toBe(30);
      });
    });

    it('should populate days with operations', () => {
      const result = generateGanttFromVoyages(sampleVoyages, 30);
      
      const vessel1Row = result.find(r => r.vessel === 'Vessel 1');
      expect(vessel1Row).toBeDefined();
      
      // Check that some days have operations
      const hasOperations = vessel1Row.days.some(day => day.operation !== '');
      expect(hasOperations).toBe(true);
    });

    it('should map operation types correctly', () => {
      const result = generateGanttFromVoyages(sampleVoyages, 30);
      
      const allOperations = result.flatMap(row => row.days);
      const operationTypes = allOperations
        .filter(day => day.operation !== '')
        .map(day => day.class);
      
      // Should only contain valid operation types
      const validTypes = ['ballast', 'loading', 'transit', 'discharge', 'canal', 'bunker', 'waiting'];
      operationTypes.forEach(type => {
        expect(validTypes).toContain(type);
      });
    });

    it('should handle empty voyages array', () => {
      const result = generateGanttFromVoyages([], 30);
      
      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
    });

    it('should respect days parameter', () => {
      const result = generateGanttFromVoyages(sampleVoyages, 15);
      
      result.forEach(row => {
        expect(row.days.length).toBe(15);
      });
    });

    it('should handle voyages outside timeline', () => {
      const futureVoyages = [{
        id: 'VOY-FUTURE',
        vesselId: 'V1',
        startDate: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString(), // 60 days in future
        legs: [
          { type: 'loading', duration: 24 }
        ]
      }];
      
      const result = generateGanttFromVoyages(futureVoyages, 30);
      
      // Should still generate rows but with empty days
      expect(result).toBeDefined();
      expect(result.length).toBeGreaterThan(0);
    });

    it('should calculate operation labels correctly', () => {
      const result = generateGanttFromVoyages(sampleVoyages, 30);
      
      const allDays = result.flatMap(row => row.days);
      const operations = allDays.filter(day => day.operation !== '');
      
      // Check that operations have correct labels
      operations.forEach(op => {
        expect(op.operation).toMatch(/^[ПВТБКФО]$/); // Russian letters for operations
      });
    });

    it('should handle multi-day operations', () => {
      const longVoyages = [{
        id: 'VOY-LONG',
        vesselId: 'V1',
        startDate: new Date().toISOString(),
        legs: [
          { type: 'transit', duration: 120 } // 5 days
        ]
      }];
      
      const result = generateGanttFromVoyages(longVoyages, 30);
      const vessel1Row = result.find(r => r.vessel === 'Vessel 1');
      
      // Count consecutive transit operations
      let consecutiveDays = 0;
      vessel1Row.days.forEach(day => {
        if (day.class === 'transit') consecutiveDays++;
      });
      
      expect(consecutiveDays).toBeGreaterThan(1);
    });
  });

  describe('performance tests', () => {
    it('should handle large voyages dataset efficiently', () => {
      const largeVoyages = [];
      for (let i = 0; i < 100; i++) {
        largeVoyages.push({
          id: `VOY-${i}`,
          vesselId: `V${i % 2 + 1}`,
          startDate: new Date().toISOString(),
          legs: [
            { type: 'ballast', duration: 24 },
            { type: 'loading', duration: 12 },
            { type: 'transit', duration: 48 },
            { type: 'discharge', duration: 12 }
          ]
        });
      }
      
      const start = performance.now();
      const result = generateGanttFromVoyages(largeVoyages, 30);
      const duration = performance.now() - start;
      
      expect(duration).toBeLessThan(500); // Should complete in less than 500ms
      expect(result).toBeDefined();
    });

    it('should handle many days efficiently', () => {
      const voyages = [{
        id: 'VOY-1',
        vesselId: 'V1',
        startDate: new Date().toISOString(),
        legs: [{ type: 'transit', duration: 240 }]
      }];
      
      const start = performance.now();
      const result = generateGanttFromVoyages(voyages, 365); // One year
      const duration = performance.now() - start;
      
      expect(duration).toBeLessThan(200); // Should complete quickly
      expect(result[0].days.length).toBe(365);
    });
  });

  describe('edge cases', () => {
    it('should handle voyages with no legs', () => {
      const voyages = [{
        id: 'VOY-EMPTY',
        vesselId: 'V1',
        startDate: new Date().toISOString(),
        legs: []
      }];
      
      const result = generateGanttFromVoyages(voyages, 30);
      expect(result).toBeDefined();
    });

    it('should handle voyages with null duration', () => {
      const voyages = [{
        id: 'VOY-NULL',
        vesselId: 'V1',
        startDate: new Date().toISOString(),
        legs: [{ type: 'loading', duration: null }]
      }];
      
      const result = generateGanttFromVoyages(voyages, 30);
      expect(result).toBeDefined();
    });

    it('should handle unknown operation types', () => {
      const voyages = [{
        id: 'VOY-UNKNOWN',
        vesselId: 'V1',
        startDate: new Date().toISOString(),
        legs: [{ type: 'unknown_type', duration: 24 }]
      }];
      
      const result = generateGanttFromVoyages(voyages, 30);
      const vessel1Row = result.find(r => r.vessel === 'Vessel 1');
      
      // Should use default 'waiting' type
      const hasWaitingClass = vessel1Row.days.some(day => day.class === 'waiting');
      expect(hasWaitingClass).toBe(true);
    });
  });
});
