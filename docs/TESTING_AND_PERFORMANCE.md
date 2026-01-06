# Testing and Performance Guide

This document provides comprehensive information about testing and performance optimization in the Vessel Scheduler application.

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Component Tests](#component-tests)
3. [Store Tests](#store-tests)
4. [E2E Tests](#e2e-tests)
5. [Performance Optimization](#performance-optimization)
6. [Bundle Optimization](#bundle-optimization)
7. [Performance Monitoring](#performance-monitoring)

## Testing Overview

The application uses a multi-layered testing approach:

- **Unit Tests**: For components, stores, and utilities (Vitest + Vue Test Utils)
- **Integration Tests**: For store + service interactions
- **E2E Tests**: For critical user workflows (Playwright)
- **Performance Tests**: For measuring and monitoring performance

### Running Tests

```bash
# Run all unit tests
npm test

# Run tests in watch mode
npm run test

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage

# Run E2E testsнием
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run all tests
npm run test:all
```

## Component Tests

Component tests are located in `src/components/**/__tests__/` directories.

### Example: Testing a Vue Component

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import MyComponent from '../MyComponent.vue';

describe('MyComponent.vue', () => {
  let wrapper;
  let pinia;

  beforeEach(() => {
    pinia = createPinia();
    wrapper = mount(MyComponent, {
      global: {
        plugins: [pinia],
      },
    });
  });

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true);
  });

  it('handles user interaction', async () => {
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('click')).toBeTruthy();
  });
});
```

### Component Test Coverage

Current component tests:
-  [`GanttChart.vue`](../src/components/gantt/__tests__/GanttChart.spec.ts) - Comprehensive Gantt chart testing
-  [`BaseButton.vue`](../src/components/shared/__tests__/BaseButton.spec.ts) - Shared button component tests

Additional components should follow the same pattern.

## Store Tests

Store tests are located in `src/stores/__tests__/` directory.

### Example: Testing a Pinia Store

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useMyStore } from '../myStore';

vi.mock('@/services', () => ({
  myService: {
    getAll: vi.fn(() => Promise.resolve(mockData)),
  },
}));

describe('My Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('fetches data successfully', async () => {
    const store = useMyStore();
    await store.fetchData();
    
    expect(store.data).toHaveLength(2);
    expect(store.loading).toBe(false);
  });
});
```

### Store Test Coverage

Current store tests:
-  [`route.ts`](../src/stores/__tests__/route.spec.ts) - Complete route store testing with mocked services

## E2E Tests

E2E tests are located in the [`e2e/`](../e2e/) directory and use Playwright.

### Example: E2E Test

```typescript
import { test, expect } from '@playwright/test';

test('user can create a vessel', async ({ page }) => {
  await page.goto('/');
  await page.click('text=Vessels');
  await page.click('button:has-text("Add Vessel")');
  
  await page.fill('input[name="name"]', 'Test Vessel');
  await page.click('button[type="submit"]');
  
  await expect(page.locator('.notification')).toContainText(/success/i);
});
```

### E2E Test Scenarios

Current E2E tests cover:
-  Dashboard navigation
-  Vessel management (create, filter, edit)
-  Voyage planning workflow
-  Gantt chart display
-  Schedule export
-  Route calculation
-  Financial analysis
-  Network visualization
-  Data persistence
-  Error handling
-  Mobile responsiveness
-  Performance benchmarks
-  Accessibility

### Running E2E Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run with browser UI
npm run test:e2e:headed

# Interactive mode
npm run test:e2e:ui

# View test report
npm run test:e2e:report
```

## Performance Optimization

### Code Splitting

The application implements aggressive code splitting:

#### Router-based Splitting

All routes use lazy loading:

```typescript
{
  path: '/gantt',
  name: 'gantt',
  component: () => import('@/views/GanttView.vue'),
}
```

#### Manual Chunk Splitting

Vite configuration splits bundles by:
- **Vendor libraries**: Vue, Router, Pinia separated
- **Heavy libraries**: vis-network, chart.js, xlsx isolated
- **Feature modules**: Gantt, Network, Financial components separated
- **Views**: Each view in its own chunk

### Bundle Size Optimization

Current optimizations in [`vite.config.ts`](../vite.config.ts):

1. **Terser minification** with aggressive settings
2. **CSS code splitting** enabled
3. **Asset inlining** for files < 4KB
4. **Tree-shaking** enabled by default
5. **Image optimization** with proper naming
6. **Font subsetting** consideration

### Build Analysis

```bash
# Build with bundle analysis
npm run build:analyze

# View bundle size report
npm run build
```

### Optimization Checklist

-  Lazy-loaded routes
-  Code splitting by vendor
-  Code splitting by feature
-  CSS minification
-  JS minification with Terser
-  Tree-shaking enabled
-  Asset optimization
-  Chunk size limits
-  PWA caching strategy

## Performance Monitoring

The application includes a comprehensive performance monitoring system located in [`src/utils/performance.ts`](../src/utils/performance.ts).

### Features

- **Web Vitals Tracking**: FCP, LCP, FID, CLS, TTFB
- **Route Performance**: Measure navigation time
- **API Performance**: Track API call durations
- **Component Performance**: Monitor component render times
- **Custom Metrics**: Track any custom operation

### Usage

```typescript
import { usePerformance } from '@/utils/performance';

const { measureAsync, measureRoute, getWebVitals } = usePerformance();

// Measure async operation
const data = await measureAsync('fetchVessels', async () => {
  return await vesselService.getAll();
});

// Get Web Vitals
const vitals = getWebVitals();
console.log('LCP:', vitals.LCP);
console.log('FCP:', vitals.FCP);

// Get performance report
const report = getReport();
```

### Performance Thresholds

Target performance metrics:

| Metric | Target | Description |
|--------|--------|-------------|
| FCP | < 1.8s | First Contentful Paint |
| LCP | < 2.5s | Largest Contentful Paint |
| FID | < 100ms | First Input Delay |
| CLS | < 0.1 | Cumulative Layout Shift |
| TTI | < 3.8s | Time to Interactive |

### Monitoring in Production

Performance data is automatically sent to Google Analytics (if configured):

```typescript
// Automatic tracking on route changes
router.afterEach((to, from) => {
  const duration = performance.now() - navigationStart;
  performanceMonitor.measureRoute(to.name, duration);
});
```

## Best Practices

### Component Testing

1. **Test user interactions**, not implementation details
2. **Use semantic queries** (getByRole, getByLabelText)
3. **Mock external dependencies** (API calls, stores)
4. **Test error states** and loading states
5. **Keep tests isolated** and independent

### E2E Testing

1. **Test critical user journeys**
2. **Use stable selectors** (prefer data-test-id)
3. **Handle async operations properly**
4. **Test on multiple viewports**
5. **Include accessibility checks**

### Performance

1. **Lazy load heavy components**
2. **Optimize images** and assets
3. **Minimize bundle sizes**
4. **Use code splitting strategically**
5. **Monitor Web Vitals regularly**

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:run
      - run: npm run test:coverage
      - run: npm run test:e2e
```

## Coverage Reports

Coverage reports are generated in:
- `coverage/` - Unit test coverage (HTML, JSON, LCOV)
- `test-results/` - E2E test results
- `playwright-report/` - E2E HTML report

### Viewing Coverage

```bash
# Generate and open coverage report
npm run test:coverage
open coverage/index.html
```

## Performance Checklist

- [ ] All routes lazy-loaded
- [ ] Bundle size under budget
- [ ] Web Vitals in good range
- [ ] E2E tests passing
- [ ] Unit test coverage > 80%
- [ ] No console errors in production
- [ ] PWA configured and working
- [ ] Images optimized
- [ ] Fonts subseted if needed
- [ ] API calls optimized

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Web Vitals](https://web.dev/vitals/)
- [Vite Performance](https://vitejs.dev/guide/performance.html)

---

Last updated: 2025-12-26
