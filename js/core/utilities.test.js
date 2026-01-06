import { describe, it, expect, beforeEach, vi } from 'vitest';
import { toNumber, formatDate, showNotification, updateCSSVariables } from './utilities.js';

describe('utilities', () => {
  describe('toNumber()', () => {
    it('should convert valid string numbers', () => {
      expect(toNumber('123')).toBe(123);
      expect(toNumber('45.67')).toBe(45.67);
      expect(toNumber(' 89 ')).toBe(89);
    });

    it('should handle comma as decimal separator', () => {
      expect(toNumber('12,34')).toBe(12.34);
      expect(toNumber('1234,56')).toBe(1234.56);
    });

    it('should return 0 for null/undefined', () => {
      expect(toNumber(null)).toBe(0);
      expect(toNumber(undefined)).toBe(0);
    });

    it('should return 0 for empty strings', () => {
      expect(toNumber('')).toBe(0);
      expect(toNumber('   ')).toBe(0);
    });

    it('should return 0 for invalid numbers', () => {
      expect(toNumber('abc')).toBe(0);
      expect(toNumber('12abc')).toBe(0);
      expect(toNumber(NaN)).toBe(0);
      expect(toNumber(Infinity)).toBe(0);
    });

    it('should handle negative numbers', () => {
      expect(toNumber('-123')).toBe(-123);
      expect(toNumber('-45,67')).toBe(-45.67);
    });

    it('should handle zero', () => {
      expect(toNumber('0')).toBe(0);
      expect(toNumber(0)).toBe(0);
    });
  });

  describe('formatDate()', () => {
    it('should format date in Russian locale', () => {
      const result = formatDate('2024-01-15');
      expect(result).toMatch(/\d{1,2}/); // Contains day
      expect(result).toMatch(/202\d/); // Contains year
    });

    it('should handle Date objects', () => {
      const date = new Date('2024-06-20');
      const result = formatDate(date);
      expect(result).toBeTruthy();
      expect(typeof result).toBe('string');
    });

    it('should handle different date formats', () => {
      expect(formatDate('2024-12-25')).toBeTruthy();
      expect(formatDate('12/25/2024')).toBeTruthy();
    });
  });

  describe('showNotification()', () => {
    beforeEach(() => {
      // Clear body
      document.body.innerHTML = '';
      vi.useFakeTimers();
    });

    it('should create notification element with default type', () => {
      showNotification('Test message');
      const notification = document.querySelector('div');
      expect(notification).toBeTruthy();
      expect(notification.textContent).toBe('Test message');
    });

    it('should handle success type', () => {
      showNotification('Success!', 'success');
      const notification = document.querySelector('div');
      expect(notification.style.cssText).toContain('var(--accent-success)');
    });

    it('should handle error type', () => {
      showNotification('Error!', 'error');
      const notification = document.querySelector('div');
      expect(notification.style.cssText).toContain('var(--accent-danger)');
    });

    it('should handle warning type', () => {
      showNotification('Warning!', 'warning');
      const notification = document.querySelector('div');
      expect(notification.style.cssText).toContain('var(--accent-warning)');
    });

    it('should handle info type', () => {
      showNotification('Info', 'info');
      const notification = document.querySelector('div');
      expect(notification.style.cssText).toContain('var(--accent-primary)');
    });

    it('should remove notification after timeout', () => {
      showNotification('Test');
      expect(document.querySelectorAll('div').length).toBe(1);
      
      // Fast-forward 3000ms
      vi.advanceTimersByTime(3000);
      expect(document.querySelector('div').style.animation).toContain('slideOut');
      
      // Fast-forward another 300ms
      vi.advanceTimersByTime(300);
      expect(document.querySelectorAll('div').length).toBe(0);
    });

    it('should append notification to body', () => {
      showNotification('Test');
      expect(document.body.children.length).toBe(1);
    });
  });

  describe('updateCSSVariables()', () => {
    beforeEach(() => {
      document.documentElement.style = {};
    });

    it('should update CSS variables', () => {
      const colors = {
        loading: '#FF0000',
        discharge: '#00FF00',
        sea_laden: '#0000FF',
      };

      updateCSSVariables(colors);
      
      const root = document.documentElement;
      expect(root.style.getPropertyValue('--operation-loading')).toBe('#FF0000');
      expect(root.style.getPropertyValue('--operation-discharge')).toBe('#00FF00');
      expect(root.style.getPropertyValue('--operation-transit')).toBe('#0000FF');
    });

    it('should add # prefix if missing', () => {
      const colors = {
        loading: 'FF0000',
        discharge: '00FF00',
      };

      updateCSSVariables(colors);
      
      const root = document.documentElement;
      expect(root.style.getPropertyValue('--operation-loading')).toBe('#FF0000');
      expect(root.style.getPropertyValue('--operation-discharge')).toBe('#00FF00');
    });

    it('should handle all operation colors', () => {
      const colors = {
        loading: '#111111',
        discharge: '#222222',
        sea_laden: '#333333',
        sea_ballast: '#444444',
        canal: '#555555',
        bunker: '#666666',
        waiting: '#777777',
      };

      updateCSSVariables(colors);
      
      const root = document.documentElement;
      expect(root.style.getPropertyValue('--operation-loading')).toBe('#111111');
      expect(root.style.getPropertyValue('--operation-discharge')).toBe('#222222');
      expect(root.style.getPropertyValue('--operation-transit')).toBe('#333333');
      expect(root.style.getPropertyValue('--operation-ballast')).toBe('#444444');
      expect(root.style.getPropertyValue('--operation-canal')).toBe('#555555');
      expect(root.style.getPropertyValue('--operation-bunker')).toBe('#666666');
      expect(root.style.getPropertyValue('--operation-waiting')).toBe('#777777');
    });

    it('should handle partial color updates', () => {
      const colors = {
        loading: '#FF0000',
      };

      updateCSSVariables(colors);
      
      const root = document.documentElement;
      expect(root.style.getPropertyValue('--operation-loading')).toBe('#FF0000');
    });

    it('should skip undefined colors', () => {
      const colors = {
        loading: undefined,
        discharge: '#00FF00',
      };

      updateCSSVariables(colors);
      
      const root = document.documentElement;
      expect(root.style.getPropertyValue('--operation-loading')).toBe('');
      expect(root.style.getPropertyValue('--operation-discharge')).toBe('#00FF00');
    });
  });

  describe('performance - toNumber', () => {
    it('should handle large number of conversions quickly', () => {
      const start = performance.now();
      
      for (let i = 0; i < 10000; i++) {
        toNumber('123.45');
      }
      
      const duration = performance.now() - start;
      expect(duration).toBeLessThan(100); // Should complete in less than 100ms
    });
  });
});
