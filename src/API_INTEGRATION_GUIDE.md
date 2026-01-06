# API Integration Guide

This guide explains how to use the API services, Pinia stores, and composables in your Vue components.

## Table of Contents

1. [API Services](#api-services)
2. [Pinia Stores](#pinia-stores)
3. [Composables](#composables)
4. [Usage Examples](#usage-examples)

## API Services

API services are located in [`src/services/`](src/services/) and provide methods for interacting with the backend API.

### Available Services

- **[`vesselService`](src/services/vessel.service.ts)** - Vessel management
- **[`cargoService`](src/services/cargo.service.ts)** - Cargo commitments
- **[`routeService`](src/services/route.service.ts)** - Routes and distances
- **[`portService`](src/services/route.service.ts)** - Port management
- **[`voyageService`](src/services/voyage.service.ts)** - Voyage operations
- **[`voyageTemplateService`](src/services/voyage.service.ts)** - Voyage templates
- **[`scenarioService`](src/services/voyage.service.ts)** - Scenario management

### Base Configuration

The API client is configured in [`src/services/api.ts`](src/services/api.ts) with:
- Automatic request/response interceptors
- Error handling
- Authentication token management
- Request/response logging in development

### Environment Variables

Set the API base URL in `.env`:

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

## Pinia Stores

Stores provide centralized state management with built-in API integration.

### Available Stores

#### 1. Vessel Store ([`src/stores/vessel.ts`](src/stores/vessel.ts))

```typescript
import { useVesselStore } from '@/stores/vessel';

const vesselStore = useVesselStore();

// Fetch vessels
await vesselStore.fetchVessels('deepsea');

// Access state
console.log(vesselStore.vessels);
console.log(vesselStore.loading);
console.log(vesselStore.error);

// Computed values
console.log(vesselStore.totalVessels);
console.log(vesselStore.activeVessels);

// Actions
const vessel = await vesselStore.createVessel(vesselData);
await vesselStore.updateVessel(id, updates);
await vesselStore.deleteVessel(id);
```

#### 2. Cargo Store ([`src/stores/cargo.ts`](src/stores/cargo.ts))

```typescript
import { useCargoStore } from '@/stores/cargo';

const cargoStore = useCargoStore();

await cargoStore.fetchCargo('deepsea');
const cargo = await cargoStore.createCargo(cargoData);
const stats = await cargoStore.getCargoStatistics(startDate, endDate);
```

#### 3. Route Store ([`src/stores/route.ts`](src/stores/route.ts))

```typescript
import { useRouteStore } from '@/stores/route';

const routeStore = useRouteStore();

await routeStore.fetchRoutes();
await routeStore.fetchPorts();
const distance = await routeStore.calculateDistance('Port A', 'Port B');
const route = await routeStore.getOptimalRoute('Port A', 'Port B', 'tanker');
```

#### 4. Voyage Store ([`src/stores/voyage.ts`](src/stores/voyage.ts))

```typescript
import { useVoyageStore } from '@/stores/voyage';

const voyageStore = useVoyageStore();

await voyageStore.fetchVoyages();
await voyageStore.fetchTemplates();
const voyage = await voyageStore.createVoyage(voyageData);
const result = await voyageStore.calculateVoyage(voyageData);
const financials = await voyageStore.getVoyageFinancials(voyageId);
```

#### 5. App Store ([`src/stores/app.ts`](src/stores/app.ts))

```typescript
import { useAppStore } from '@/stores/app';

const appStore = useAppStore();

// Notifications
appStore.addNotification({
  type: 'success',
  message: 'Operation completed',
  duration: 5000
});

// Loading state
appStore.setLoading(true);

// Module switching
appStore.setCurrentModule('deepsea');
```

## Composables

Composables provide reusable logic for common patterns.

### 1. useApi ([`src/composables/useApi.ts`](src/composables/useApi.ts))

Handles API calls with automatic loading states and error handling.

```typescript
import { useApi } from '@/composables';
import { vesselService } from '@/services';

// In component setup
const { loading, error, data, execute } = useApi(
  vesselService.getAll,
  {
    showSuccessNotification: true,
    successMessage: 'Vessels loaded successfully'
  }
);

// Execute the API call
await execute('deepsea');
```

### 2. useFilters ([`src/composables/useFilters.ts`](src/composables/useFilters.ts))

Provides filtering and sorting functionality.

```typescript
import { useFilters } from '@/composables';
import { computed } from 'vue';

const vessels = ref([...]);
const { 
  searchQuery, 
  sortedItems, 
  setSearch, 
  setFilter, 
  sort 
} = useFilters(vessels, {
  searchFields: ['name', 'imo', 'type'],
  sortField: 'name',
  sortOrder: 'asc'
});

// Use in template
<input v-model="searchQuery" placeholder="Search vessels..." />
<button @click="sort('name')">Sort by Name</button>
```

### 3. usePagination ([`src/composables/usePagination.ts`](src/composables/usePagination.ts))

Handles pagination logic.

```typescript
import { usePagination } from '@/composables';

const items = ref([...]);
const {
  paginatedItems,
  currentPage,
  totalPages,
  nextPage,
  previousPage,
  goToPage
} = usePagination(items, {
  initialPage: 1,
  initialPerPage: 10
});
```

## Usage Examples

### Complete Component Example

```vue
<template>
  <div>
    <h1>Vessels</h1>
    
    <!-- Search -->
    <input v-model="searchQuery" placeholder="Search vessels..." />
    
    <!-- Loading State -->
    <div v-if="loading">Loading...</div>
    
    <!-- Error State -->
    <div v-if="error" class="error">{{ error }}</div>
    
    <!-- Vessel List -->
    <table v-else>
      <thead>
        <tr>
          <th @click="sort('name')">Name</th>
          <th @click="sort('type')">Type</th>
          <th @click="sort('dwt')">DWT</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="vessel in paginatedItems" :key="vessel.id">
          <td>{{ vessel.name }}</td>
          <td>{{ vessel.type }}</td>
          <td>{{ vessel.dwt }}</td>
          <td>
            <button @click="editVessel(vessel)">Edit</button>
            <button @click="deleteVesselHandler(vessel.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- Pagination -->
    <div class="pagination">
      <button @click="previousPage" :disabled="!hasPreviousPage">Previous</button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="!hasNextPage">Next</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useVesselStore } from '@/stores/vessel';
import { useFilters, usePagination } from '@/composables';

const vesselStore = useVesselStore();

// Filtering
const { 
  searchQuery, 
  sortedItems, 
  sort 
} = useFilters(vesselStore.vessels, {
  searchFields: ['name', 'imo', 'type']
});

// Pagination
const {
  paginatedItems,
  currentPage,
  totalPages,
  hasNextPage,
  hasPreviousPage,
  nextPage,
  previousPage
} = usePagination(sortedItems);

// Destructure store state
const { loading, error } = vesselStore;

// Load vessels on mount
onMounted(async () => {
  await vesselStore.fetchVessels('deepsea');
});

// Actions
const editVessel = (vessel: any) => {
  // Handle edit
};

const deleteVesselHandler = async (id: string | number) => {
  if (confirm('Are you sure?')) {
    await vesselStore.deleteVessel(id);
  }
};
</script>
```

### Direct Service Usage (without store)

```vue
<script setup lang="ts">
import { ref } from 'vue';
import { vesselService } from '@/services';
import { useApi } from '@/composables';

const { loading, error, execute } = useApi(vesselService.getAll, {
  showSuccessNotification: false,
  showErrorNotification: true
});

const vessels = ref([]);

const loadVessels = async () => {
  vessels.value = await execute('deepsea');
};
</script>
```

## Error Handling

All stores and services automatically handle errors through:

1. **Error interceptors** in [`apiClient`](src/services/api.ts)
2. **Store-level error handling** with notifications
3. **Composable error handling** with the [`useApi`](src/composables/useApi.ts) composable

Errors are automatically displayed as notifications using the App Store.

## TypeScript Support

All services, stores, and composables are fully typed. Import types from:

```typescript
import type { Vessel, VesselFormData } from '@/types/vessel.types';
import type { CargoCommitment } from '@/types/cargo.types';
import type { Route, Port } from '@/types/route.types';
import type { Voyage, VoyageTemplate } from '@/types/voyage.types';
```

## Best Practices

1. **Use stores for shared state** - Data that multiple components need
2. **Use composables for logic reuse** - Filtering, pagination, API calls
3. **Use services directly** for one-off operations
4. **Always handle loading and error states** in your UI
5. **Clear store data** when switching modules or logging out
6. **Use TypeScript** for type safety and better DX

## API Configuration

To change the API base URL, create a `.env` file:

```bash
cp .env.example .env
```

Then edit the `VITE_API_BASE_URL` variable.
