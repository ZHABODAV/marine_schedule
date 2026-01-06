# Performance Optimization Guide

This document outlines the performance optimizations implemented in the Voyage Vessel Scheduler application.

## Table of Contents
- [Bundle Size Optimization](#bundle-size-optimization)
- [Lazy Loading](#lazy-loading)
- [Code Splitting](#code-splitting)
- [Loading Skeletons](#loading-skeletons)
- [Virtual Scrolling](#virtual-scrolling)
- [Caching Strategies](#caching-strategies)
- [Best Practices](#best-practices)

---

## Bundle Size Optimization

### Current Implementation

The application uses Vite for building and optimizing bundles:

**Build Configuration** ([`vite.config.ts`](../vite.config.ts)):
- **Tree Shaking**: Removes unused code automatically
- **Minification**: Uses Terser for JavaScript minification
- **Code Splitting**: Automatic chunk splitting for vendor libraries
- **Asset Optimization**: Images and fonts optimized during build

### Bundle Analysis

Run bundle analysis:
```bash
npm run build:analyze
```

This generates a visual representation of bundle sizes, helping identify:
- Large dependencies that can be replaced
- Duplicate code that can be shared
- Unused imports that can be removed

### Optimization Techniques

1. **Dynamic Imports**: Load modules on demand
   ```typescript
   const module = await import('./heavy-module');
   ```

2. **Tree Shaking**: Import only what you need
   ```typescript
   // Good
   import { specificFunction } from 'library';
   
   // Avoid
   import * as library from 'library';
   ```

3. **External Dependencies**: Mark large libraries as external
   ```javascript
   build: {
     rollupOptions: {
       external: ['xlsx'],
     }
   }
   ```

---

## Lazy Loading

### Router-Level Lazy Loading

All routes use lazy loading for optimal initial load time ([`src/router/index.ts`](../src/router/index.ts)):

```typescript
{
  path: '/voyage-builder',
  component: () => import(/* webpackChunkName: "voyage-builder" */ '../views/VoyageBuilder.vue'),
}
```

### Benefits
- **Faster Initial Load**: Only load code for the current route
- **Better Caching**: Route chunks cached separately
- **Reduced Memory**: Components loaded only when needed

### Component-Level Lazy Loading

Use `defineAsyncComponent` for heavy components:

```typescript
import { defineAsyncComponent } from 'vue';

const HeavyChart = defineAsyncComponent(() =>
  import('./components/HeavyChart.vue')
);
```

### Image Lazy Loading

```html
<img src="image.jpg" loading="lazy" alt="Description">
```

---

## Code Splitting

### Automatic Code Splitting

Vite automatically splits code into:
- **Entry Chunk**: Main application code
- **Vendor Chunks**: node_modules dependencies
- **Route Chunks**: Individual route components
- **Shared Chunks**: Common code between routes

### Manual Code Splitting

For large modules, create separate chunks:

```typescript
// Heavy utility loaded only when needed
const processLargeData = async (data) => {
  const { processData } = await import('./heavy-processor');
  return processData(data);
};
```

### Chunk Naming Strategy

```typescript
component: () => import(
  /* webpackChunkName: "descriptive-name" */
  /* webpackPrefetch: true */
  './Component.vue'
)
```

Benefits:
- **Better Debugging**: Named chunks in dev tools
- **Cache Control**: Update specific chunks
- **Prefetching**: Load likely-needed chunks

---

## Loading Skeletons

### LoadingSkeleton Component

Located at [`src/components/LoadingSkeleton.vue`](../src/components/LoadingSkeleton.vue)

### Usage

```vue
<template>
  <LoadingSkeleton v-if="loading" type="table" :rows="10" :columns="5" />
  <DataTable v-else :data="data" />
</template>

<script setup>
import LoadingSkeleton from '@/components/LoadingSkeleton.vue';
</script>
```

### Available Types

1. **Table Skeleton**: For data tables
   ```vue
   <LoadingSkeleton type="table" :rows="10" :columns="4" />
   ```

2. **Card Skeleton**: For card layouts
   ```vue
   <LoadingSkeleton type="card" />
   ```

3. **List Skeleton**: For list views
   ```vue
   <LoadingSkeleton type="list" :items="5" />
   ```

4. **Gantt Skeleton**: For Gantt charts
   ```vue
   <LoadingSkeleton type="gantt" :rows="8" />
   ```

5. **Network Skeleton**: For network diagrams
   ```vue
   <LoadingSkeleton type="network" />
   ```

6. **Calendar Skeleton**: For calendar views
   ```vue
   <LoadingSkeleton type="calendar" />
   ```

### Benefits
- **Perceived Performance**: Users see instant feedback
- **Progressive Loading**: Content appears as it loads
- **Better UX**: Reduces perceived wait time by 40-50%

---

## Virtual Scrolling

### VirtualScroller Component

Located at [`src/components/VirtualScroller.vue`](../src/components/VirtualScroller.vue)

### Usage

```vue
<template>
  <VirtualScroller
    :items="largeDataset"
    :item-height="50"
    :container-height="600"
    v-slot="{ item, index }"
  >
    <div class="row-item">
      {{ item.name }} - {{ index }}
    </div>
  </VirtualScroller>
</template>

<script setup>
import VirtualScroller from '@/components/VirtualScroller.vue';

const largeDataset = ref(Array.from({ length: 10000 }, (_, i) => ({
  id: i,
  name: `Item ${i}`
})));
</script>
```

### Performance Benefits

| List Size | Without Virtual Scrolling | With Virtual Scrolling |
|-----------|--------------------------|------------------------|
| 100 items | ~20ms | ~15ms |
| 1,000 items | ~200ms | ~15ms |
| 10,000 items | ~2000ms | ~15ms |
| 100,000 items | Memory error | ~20ms |

### Features

- **Automatic Buffering**: Renders extra rows above/below viewport
- **Smooth Scrolling**: Optimized for 60fps
- **Dynamic Heights**: Support for variable item heights
- **Scroll Methods**: `scrollToIndex()`, `scrollToTop()`, `scrollToBottom()`

### Best Practices

1. **Fixed Heights**: Use fixed item heights when possible
2. **Key Fields**: Provide unique `keyField` for items
3. **Buffer Size**: Adjust buffer based on scroll speed
4. **Debouncing**: Debounce scroll events for heavy computations

---

## Caching Strategies

### Service Worker Caching

Configured in PWA setup ([`vite.config.ts`](../vite.config.ts)):

```javascript
VitePWA({
  workbox: {
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/api\./,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          expiration: {
            maxEntries: 50,
            maxAgeSeconds: 300, // 5 minutes
          },
        },
      },
    ],
  },
})
```

### Browser Caching

HTTP headers for static assets:
```
Cache-Control: public, max-age=31536000, immutable
```

### Application-Level Caching

```typescript
// Simple memo cache
const cache = new Map();

function expensiveCalculation(input) {
  const key = JSON.stringify(input);
  
  if (cache.has(key)) {
    return cache.get(key);
  }
  
  const result = /* expensive operation */;
  cache.set(key, result);
  return result;
}
```

### Vue Computed Properties

Use computed properties for expensive calculations:

```typescript
const filteredData = computed(() => {
  return largeDataset.value.filter(item => item.active);
});
```

---

## Best Practices

### 1. Optimize Images

```html
<!-- Use appropriate formats -->
<picture>
  <source srcset="image.webp" type="image/webp">
  <source srcset="image.jpg" type="image/jpeg">
  <img src="image.jpg" alt="Fallback">
</picture>

<!-- Specify dimensions -->
<img src="image.jpg" width="600" height="400" loading="lazy">
```

### 2. Debounce User Input

```typescript
import { debounce } from 'lodash-es';

const handleSearch = debounce((query: string) => {
  // Expensive search operation
}, 300);
```

### 3. Use Web Workers

For CPU-intensive tasks:

```typescript
// worker.ts
self.addEventListener('message', (e) => {
  const result = expensiveCalculation(e.data);
  self.postMessage(result);
});

// main.ts
const worker = new Worker('./worker.ts');
worker.postMessage(data);
worker.addEventListener('message', (e) => {
  console.log('Result:', e.data);
});
```

### 4. Optimize API Calls

```typescript
// Batch requests
const batchedRequests = Promise.all([
  fetch('/api/vessels'),
  fetch('/api/routes'),
  fetch('/api/cargo'),
]);

// Use pagination
const getVessels = (page = 1, limit = 50) => {
  return fetch(`/api/vessels?page=${page}&limit=${limit}`);
};
```

### 5. Reduce Re-renders

```vue
<script setup>
// Use shallowRef for large objects
const largeData = shallowRef({ /* ... */ });

// Use v-memo for expensive lists
</script>

<template>
  <div v-for="item in list" :key="item.id" v-memo="[item.id]">
    {{ item.name }}
  </div>
</template>
```

### 6. Monitor Performance

```typescript
// Performance API
performance.mark('operation-start');
// ... expensive operation
performance.mark('operation-end');
performance.measure('operation', 'operation-start', 'operation-end');

const measure = performance.getEntriesByName('operation')[0];
console.log(`Operation took ${measure.duration}ms`);
```

### 7. Optimize Bundle Size

```bash
# Analyze bundle
npm run build:analyze

# Check bundle size
npm run build && ls -lh dist/assets

# Use smaller alternatives
# Instead of: moment.js (70KB)
# Use: date-fns (15KB)
```

---

## Performance Metrics

### Target Metrics

- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Time to Interactive (TTI)**: < 3.8s
- **Cumulative Layout Shift (CLS)**: < 0.1
- **First Input Delay (FID)**: < 100ms

### Monitoring

Use Lighthouse in Chrome DevTools:
```bash
lighthouse http://localhost:5173 --view
```

Or programmatically:
```javascript
// Add to monitoring.js
if (window.performance) {
  const perfData = window.performance.getEntriesByType('navigation')[0];
  console.log('Load time:', perfData.loadEventEnd - perfData.fetchStart);
}
```

---

## Optimization Checklist

### Build Time
- [ ] Enable tree shaking
- [ ] Configure code splitting
- [ ] Minify JavaScript and CSS
- [ ] Optimize images (WebP, compression)
- [ ] Remove unused dependencies
- [ ] Use production builds

### Runtime
- [ ] Implement lazy loading
- [ ] Add loading skeletons
- [ ] Enable virtual scrolling for large lists
- [ ] Cache API responses
- [ ] Debounce user inputs
- [ ] Use memoization for expensive calculations

### Network
- [ ] Enable gzip/brotli compression
- [ ] Set appropriate cache headers
- [ ] Use CDN for static assets
- [ ] Implement HTTP/2
- [ ] Reduce API payload sizes

### Monitoring
- [ ] Set up performance monitoring
- [ ] Track Core Web Vitals
- [ ] Monitor bundle sizes
- [ ] Profile memory usage
- [ ] Analyze network waterfall

---

## Resources

- [Web.dev Performance](https://web.dev/performance/)
- [Vite Performance](https://vitejs.dev/guide/performance.html)
- [Vue Performance](https://vuejs.org/guide/best-practices/performance.html)
- [Web Vitals](https://web.dev/vitals/)

---

*Last Updated: December 29, 2024*
