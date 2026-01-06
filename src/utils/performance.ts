/**
 * Performance Monitoring Utilities
 * Tracks and reports application performance metrics
 */

interface PerformanceMetrics {
  name: string;
  duration: number;
  timestamp: number;
  type: 'route' | 'api' | 'component' | 'custom';
  metadata?: Record<string, any>;
}

interface WebVitals {
  FCP?: number; // First Contentful Paint
  LCP?: number; // Largest Contentful Paint
  FID?: number; // First Input Delay
  CLS?: number; // Cumulative Layout Shift
  TTFB?: number; // Time to First Byte
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private maxMetrics = 100;
  private webVitals: WebVitals = {};

  constructor() {
    this.initWebVitals();
  }

  /**
   * Initialize Web Vitals monitoring
   */
  private initWebVitals() {
    if (typeof window === 'undefined') return;

    // First Contentful Paint
    this.observePaint('first-contentful-paint', (duration) => {
      this.webVitals.FCP = duration;
    });

    // Largest Contentful Paint
    this.observeLCP();

    // First Input Delay
    this.observeFID();

    // Cumulative Layout Shift
    this.observeCLS();

    // Time to First Byte
    this.measureTTFB();
  }

  /**
   * Observe paint timing
   */
  private observePaint(name: string, callback: (duration: number) => void) {
    if (!('PerformanceObserver' in window)) return;

    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === name) {
          callback(entry.startTime);
        }
      }
    });

    observer.observe({ entryTypes: ['paint'] });
  }

  /**
   * Observe Largest Contentful Paint
   */
  private observeLCP() {
    if (!('PerformanceObserver' in window)) return;

    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1] as any;
      this.webVitals.LCP = lastEntry.renderTime || lastEntry.loadTime;
    });

    observer.observe({ entryTypes: ['largest-contentful-paint'] });
  }

  /**
   * Observe First Input Delay
   */
  private observeFID() {
    if (!('PerformanceObserver' in window)) return;

    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      if (entries.length > 0) {
        const firstInput = entries[0] as any;
        this.webVitals.FID = firstInput.processingStart - firstInput.startTime;
      }
    });

    observer.observe({ entryTypes: ['first-input'] });
  }

  /**
   * Observe Cumulative Layout Shift
   */
  private observeCLS() {
    if (!('PerformanceObserver' in window)) return;

    let clsValue = 0;

    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          clsValue += (entry as any).value;
          this.webVitals.CLS = clsValue;
        }
      }
    });

    observer.observe({ entryTypes: ['layout-shift'] });
  }

  /**
   * Measure Time to First Byte
   */
  private measureTTFB() {
    if (typeof window === 'undefined' || !window.performance) return;

    window.addEventListener('load', () => {
      const navTiming = performance.getEntriesByType('navigation')[0] as any;
      if (navTiming) {
        this.webVitals.TTFB = navTiming.responseStart - navTiming.requestStart;
      }
    });
  }

  /**
   * Start a performance measurement
   */
  start(name: string): () => void {
    const startTime = performance.now();

    return () => {
      const duration = performance.now() - startTime;
      this.record({
        name,
        duration,
        timestamp: Date.now(),
        type: 'custom',
      });
    };
  }

  /**
   * Measure route navigation time
   */
  measureRoute(routeName: string, duration: number) {
    this.record({
      name: `route:${routeName}`,
      duration,
      timestamp: Date.now(),
      type: 'route',
    });
  }

  /**
   * Measure API call time
   */
  measureAPI(endpoint: string, duration: number, metadata?: Record<string, any>) {
    this.record({
      name: `api:${endpoint}`,
      duration,
      timestamp: Date.now(),
      type: 'api',
      metadata,
    });
  }

  /**
   * Measure component render time
   */
  measureComponent(componentName: string, duration: number) {
    this.record({
      name: `component:${componentName}`,
      duration,
      timestamp: Date.now(),
      type: 'component',
    });
  }

  /**
   * Record a performance metric
   */
  private record(metric: PerformanceMetrics) {
    this.metrics.push(metric);

    // Keep only the last N metrics
    if (this.metrics.length > this.maxMetrics) {
      this.metrics.shift();
    }

    // Log in development
    if (import.meta.env.DEV) {
      console.log(`[Performance] ${metric.name}: ${metric.duration.toFixed(2)}ms`);
    }

    // Send to analytics in production
    if (import.meta.env.PROD && (window as any).gtag) {
      (window as any).gtag('event', 'timing_complete', {
        name: metric.name,
        value: Math.round(metric.duration),
        event_category: metric.type,
      });
    }
  }

  /**
   * Get all recorded metrics
   */
  getMetrics(): PerformanceMetrics[] {
    return [...this.metrics];
  }

  /**
   * Get metrics by type
   */
  getMetricsByType(type: PerformanceMetrics['type']): PerformanceMetrics[] {
    return this.metrics.filter(m => m.type === type);
  }

  /**
   * Get average duration for a metric name
   */
  getAverageDuration(name: string): number {
    const filtered = this.metrics.filter(m => m.name === name);
    if (filtered.length === 0) return 0;
    
    const sum = filtered.reduce((acc, m) => acc + m.duration, 0);
    return sum / filtered.length;
  }

  /**
   * Get Web Vitals
   */
  getWebVitals(): WebVitals {
    return { ...this.webVitals };
  }

  /**
   * Get performance report
   */
  getReport() {
    return {
      webVitals: this.getWebVitals(),
      metrics: this.getMetrics(),
      summary: {
        totalMeasurements: this.metrics.length,
        averageAPITime: this.getAverageDuration('api'),
        averageRouteTime: this.getAverageDuration('route'),
        averageComponentTime: this.getAverageDuration('component'),
      },
    };
  }

  /**
   * Clear all metrics
   */
  clear() {
    this.metrics = [];
  }

  /**
   * Export metrics as JSON
   */
  export(): string {
    return JSON.stringify(this.getReport(), null, 2);
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();

/**
 * Vue composable for performance tracking
 */
export function usePerformance() {
  const measureAsync = async <T>(
    name: string,
    fn: () => Promise<T>
  ): Promise<T> => {
    const end = performanceMonitor.start(name);
    try {
      return await fn();
    } finally {
      end();
    }
  };

  const measure = <T>(name: string, fn: () => T): T => {
    const end = performanceMonitor.start(name);
    try {
      return fn();
    } finally {
      end();
    }
  };

  return {
    measureAsync,
    measure,
    start: (name: string) => performanceMonitor.start(name),
    measureRoute: (name: string, duration: number) => 
      performanceMonitor.measureRoute(name, duration),
    measureAPI: (endpoint: string, duration: number, metadata?: Record<string, any>) => 
      performanceMonitor.measureAPI(endpoint, duration, metadata),
    measureComponent: (name: string, duration: number) => 
      performanceMonitor.measureComponent(name, duration),
    getMetrics: () => performanceMonitor.getMetrics(),
    getWebVitals: () => performanceMonitor.getWebVitals(),
    getReport: () => performanceMonitor.getReport(),
    clear: () => performanceMonitor.clear(),
  };
}

// Export for direct use
export default performanceMonitor;
