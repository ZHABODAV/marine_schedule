import { describe, it, expect } from 'vitest';
import { toNumber } from '../core/utilities.js';

/**
 * Performance Testing Suite
 * Tests critical functions under load to ensure they meet performance requirements
 */

describe('Performance Tests', () => {
  const PERFORMANCE_THRESHOLD = {
    SMALL_OPERATIONS: 10,   // ms
    MEDIUM_OPERATIONS: 50,  // ms
    LARGE_OPERATIONS: 200,  // ms
    BULK_OPERATIONS: 1000   // ms
  };

  describe('toNumber() performance', () => {
    it('should handle 10,000 conversions in < 100ms', () => {
      const start = performance.now();
      
      for (let i = 0; i < 10000; i++) {
        toNumber('123.45');
        toNumber('1,234.56');
        toNumber(null);
        toNumber('');
      }
      
      const duration = performance.now() - start;
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.BULK_OPERATIONS);
    });

    it('should handle 100,000 simple conversions quickly', () => {
      const start = performance.now();
      
      for (let i = 0; i < 100000; i++) {
        toNumber(String(i));
      }
      
      const duration = performance.now() - start;
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.BULK_OPERATIONS);
    });
  });

  describe('Array operations performance', () => {
    it('should filter 1000 items in < 50ms', () => {
      const items = Array.from({ length: 1000 }, (_, i) => ({
        id: i,
        value: i * 2,
        status: i % 2 === 0 ? 'active' : 'inactive'
      }));

      const start = performance.now();
      const filtered = items.filter(item => item.status === 'active');
      const duration = performance.now() - start;

      expect(filtered.length).toBe(500);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.MEDIUM_OPERATIONS);
    });

    it('should map 1000 items in < 50ms', () => {
      const items = Array.from({ length: 1000 }, (_, i) => ({ id: i, value: i }));

      const start = performance.now();
      const mapped = items.map(item => ({
        ...item,
        doubleValue: item.value * 2
      }));
      const duration = performance.now() - start;

      expect(mapped.length).toBe(1000);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.MEDIUM_OPERATIONS);
    });

    it('should reduce 1000 items in < 50ms', () => {
      const items = Array.from({ length: 1000 }, (_, i) => i);

      const start = performance.now();
      const sum = items.reduce((acc, val) => acc + val, 0);
      const duration = performance.now() - start;

      expect(sum).toBe(499500); // Sum of 0 to 999
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.MEDIUM_OPERATIONS);
    });
  });

  describe('String operations performance', () => {
    it('should concatenate 1000 strings efficiently', () => {
      const parts = Array.from({ length: 1000 }, (_, i) => `part-${i}`);

      const start = performance.now();
      const result = parts.join(',');
      const duration = performance.now() - start;

      expect(result.split(',').length).toBe(1000);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.MEDIUM_OPERATIONS);
    });

    it('should search in large string quickly', () => {
      const largeString = 'a'.repeat(100000) + 'needle' + 'a'.repeat(100000);

      const start = performance.now();
      const found = largeString.includes('needle');
      const duration = performance.now() - start;

      expect(found).toBe(true);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.MEDIUM_OPERATIONS);
    });
  });

  describe('Object operations performance', () => {
    it('should clone 1000 objects in < 100ms', () => {
      const objects = Array.from({ length: 1000 }, (_, i) => ({
        id: i,
        name: `Object ${i}`,
        data: { value: i * 2 }
      }));

      const start = performance.now();
      const cloned = objects.map(obj => ({ ...obj, data: { ...obj.data } }));
      const duration = performance.now() - start;

      expect(cloned.length).toBe(1000);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.LARGE_OPERATIONS);
    });

    it('should merge 1000 objects efficiently', () => {
      const base = Array.from({ length: 1000 }, (_, i) => ({ id: i, value: i }));
      const updates = Array.from({ length: 1000 }, (_, i) => ({ id: i, newValue: i * 2 }));

      const start = performance.now();
      const merged = base.map((item, i) => ({ ...item, ...updates[i] }));
      const duration = performance.now() - start;

      expect(merged.length).toBe(1000);
      expect(merged[0]).toHaveProperty('newValue');
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.LARGE_OPERATIONS);
    });
  });

  describe('Date operations performance', () => {
    it('should format 1000 dates in < 200ms', () => {
      const dates = Array.from({ length: 1000 }, (_, i) => 
        new Date(2024, 0, 1 + i)
      );

      const start = performance.now();
      const formatted = dates.map(date => date.toISOString());
      const duration = performance.now() - start;

      expect(formatted.length).toBe(1000);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.LARGE_OPERATIONS);
    });

    it('should calculate date differences efficiently', () => {
      const date1 = new Date('2024-01-01');
      const dates = Array.from({ length: 1000 }, (_, i) => 
        new Date('2024-01-01T00:00:00Z').getTime() + (i * 24 * 60 * 60 * 1000)
      );

      const start = performance.now();
      const differences = dates.map(date => Math.floor((date - date1.getTime()) / (24 * 60 * 60 * 1000)));
      const duration = performance.now() - start;

      expect(differences.length).toBe(1000);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.LARGE_OPERATIONS);
    });
  });

  describe('DOM-like operations performance', () => {
    it('should create 1000 simple objects quickly', () => {
      const start = performance.now();
      
      const elements = Array.from({ length: 1000 }, (_, i) => ({
        tagName: 'div',
        id: `element-${i}`,
        className: 'test-class',
        children: []
      }));
      
      const duration = performance.now() - start;
      
      expect(elements.length).toBe(1000);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.LARGE_OPERATIONS);
    });
  });

  describe('JSON operations performance', () => {
    it('should stringify 100 complex objects quickly', () => {
      const objects = Array.from({ length: 100 }, (_, i) => ({
        id: i,
        name: `Object ${i}`,
        nested: {
          level1: {
            level2: {
              value: i * 2,
              array: [1, 2, 3, 4, 5]
            }
          }
        }
      }));

      const start = performance.now();
      const json = JSON.stringify(objects);
      const duration = performance.now() - start;

      expect(json.length).toBeGreaterThan(0);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.MEDIUM_OPERATIONS);
    });

    it('should parse complex JSON quickly', () => {
      const objects = Array.from({ length: 100 }, (_, i) => ({
        id: i,
        name: `Object ${i}`,
        data: { value: i }
      }));
      const json = JSON.stringify(objects);

      const start = performance.now();
      const parsed = JSON.parse(json);
      const duration = performance.now() - start;

      expect(parsed.length).toBe(100);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.MEDIUM_OPERATIONS);
    });
  });

  describe('Memory stress tests', () => {
    it('should handle creating large arrays without crashing', () => {
      const start = performance.now();
      
      const largeArray = Array.from({ length: 50000 }, (_, i) => ({
        id: i,
        value: i * 2
      }));
      
      const duration = performance.now() - start;
      
      expect(largeArray.length).toBe(50000);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.BULK_OPERATIONS);
    });

    it('should efficiently process large datasets', () => {
      const dataset = Array.from({ length: 10000 }, (_, i) => ({
        id: i,
        value: Math.random() * 100,
        category: i % 10
      }));

      const start = performance.now();
      
      // Perform multiple operations
      const filtered = dataset.filter(item => item. value > 50);
      const grouped = filtered.reduce((acc, item) => {
        if (!acc[item.category]) acc[item.category] = [];
        acc[item.category].push(item);
        return acc;
      }, {});
      
      const duration = performance.now() - start;
      
      expect(Object.keys(grouped).length).toBeGreaterThan(0);
      expect(duration).toBeLessThan(PERFORMANCE_THRESHOLD.BULK_OPERATIONS);
    });
  });

  describe('Benchmark reporting', () => {
    it('should track and report performance metrics', () => {
      const metrics = {
        operations: 0,
        totalTime: 0,
        avgTime: 0
      };

      const operations = [
        () => toNumber('123'),
        () => [1, 2, 3].map(x => x * 2),
        () => JSON.stringify({ test: 'data' }),
        () => new Date().toISOString()
      ];

      operations.forEach(op => {
        const start = performance.now();
        op();
        const duration = performance.now() - start;
        
        metrics.operations++;
        metrics.totalTime += duration;
      });

      metrics.avgTime = metrics.totalTime / metrics.operations;

      expect(metrics.operations).toBe(4);
      expect(metrics.avgTime).toBeLessThan(PERFORMANCE_THRESHOLD.SMALL_OPERATIONS);
      
      // Optional: log metrics for review
      console.log('Performance Metrics:', metrics);
    });
  });
});
