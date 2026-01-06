<template>
  <div class="route-list">
    <div class="filters-section">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Search routes by port..."
          class="search-input"
        />
      </div>
      
      <div class="filters">
        <input
          v-model="filterCanal"
          type="text"
          placeholder="Filter by canal..."
          class="filter-input"
        />
      </div>
      
      <BaseButton
        @click="$emit('add-route')"
        variant="primary"
        class="add-button"
      >
        <span class="icon">+</span>
        Add Route
      </BaseButton>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else-if="filteredRoutes.length === 0" class="empty-state">
      <p>No routes found.</p>
    </div>

    <div v-else class="table-container">
      <table class="routes-table">
        <thead>
          <tr>
            <th v-if="selectable">
              <input
                type="checkbox"
                @change="toggleSelectAll"
                :checked="allSelected"
                class="checkbox"
              />
            </th>
            <th @click="sort('from')">
              From
              <span class="sort-indicator" v-if="sortBy === 'from'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="sort('to')">
              To
              <span class="sort-indicator" v-if="sortBy === 'to'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="sort('distance')">
              Distance (nm)
              <span class="sort-indicator" v-if="sortBy === 'distance'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th>Canal</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="route in paginatedRoutes"
            :key="route.id"
            class="route-row"
          >
            <td v-if="selectable">
              <input
                type="checkbox"
                :checked="selectedRouteIds.includes(route.id)"
                @change="toggleRoute(route.id)"
                class="checkbox"
              />
            </td>
            <td><strong>{{ route.from }}</strong></td>
            <td><strong>{{ route.to }}</strong></td>
            <td>{{ formatNumber(route.distance) }}</td>
            <td>{{ route.canal || '-' }}</td>
            <td class="actions-cell">
              <BaseButton
                @click="$emit('transfer-to-builder', route)"
                variant="primary"
                size="small"
              >
                To Builder
              </BaseButton>
              <BaseButton
                @click="$emit('view-route', route)"
                variant="secondary"
                size="small"
              >
                View
              </BaseButton>
              <BaseButton
                @click="handleDelete(route)"
                variant="danger"
                size="small"
              >
                Delete
              </BaseButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="selectable && selectedRouteIds.length > 0" class="bulk-actions">
      <span class="selection-info">{{ selectedRouteIds.length }} route(s) selected</span>
      <BaseButton
        @click="$emit('transfer-selected', selectedRoutes)"
        variant="primary"
      >
        Transfer Selected to Builder
      </BaseButton>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <BaseButton
        @click="currentPage--"
        :disabled="currentPage === 1"
        variant="secondary"
        size="small"
      >
        Previous
      </BaseButton>
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <BaseButton
        @click="currentPage++"
        :disabled="currentPage === totalPages"
        variant="secondary"
        size="small"
      >
        Next
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Route } from '@/types/route.types';
import BaseButton from '@/components/shared/BaseButton.vue';
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue';

interface Props {
  routes: Route[];
  loading?: boolean;
  selectable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  selectable: false,
});

const emit = defineEmits<{
  'add-route': [];
  'view-route': [route: Route];
  'delete-route': [route: Route];
  'transfer-to-builder': [route: Route];
  'transfer-selected': [routes: Route[]];
}>();

// State
const searchTerm = ref('');
const filterCanal = ref('');
const sortBy = ref<keyof Route>('from');
const sortDirection = ref<'asc' | 'desc'>('asc');
const currentPage = ref(1);
const itemsPerPage = 10;
const selectedRouteIds = ref<(string | number)[]>([]);

// Computed
const filteredRoutes = computed(() => {
  let filtered = [...props.routes];

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(
      r =>
        r.from.toLowerCase().includes(term) ||
        r.to.toLowerCase().includes(term)
    );
  }

  if (filterCanal.value) {
    const canal = filterCanal.value.toLowerCase();
    filtered = filtered.filter(r => 
      r.canal?.toLowerCase().includes(canal)
    );
  }

  filtered.sort((a, b) => {
    const aVal = a[sortBy.value];
    const bVal = b[sortBy.value];
    
    if (aVal === bVal) return 0;
    
    const comparison = aVal < bVal ? -1 : 1;
    return sortDirection.value === 'asc' ? comparison : -comparison;
  });

  return filtered;
});

const totalPages = computed(() =>
  Math.ceil(filteredRoutes.value.length / itemsPerPage)
);

const paginatedRoutes = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredRoutes.value.slice(start, end);
});

const allSelected = computed(() => {
  return paginatedRoutes.value.length > 0 &&
    paginatedRoutes.value.every(r => selectedRouteIds.value.includes(r.id));
});

const selectedRoutes = computed(() => {
  return props.routes.filter(r => selectedRouteIds.value.includes(r.id));
});

// Methods
function sort(field: keyof Route) {
  if (sortBy.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortBy.value = field;
    sortDirection.value = 'asc';
  }
}

function formatNumber(value: number): string {
  return value.toLocaleString();
}

function toggleSelectAll() {
  if (allSelected.value) {
    paginatedRoutes.value.forEach(r => {
      const index = selectedRouteIds.value.indexOf(r.id);
      if (index > -1) {
        selectedRouteIds.value.splice(index, 1);
      }
    });
  } else {
    paginatedRoutes.value.forEach(r => {
      if (!selectedRouteIds.value.includes(r.id)) {
        selectedRouteIds.value.push(r.id);
      }
    });
  }
}

function toggleRoute(id: string | number) {
  const index = selectedRouteIds.value.indexOf(id);
  if (index > -1) {
    selectedRouteIds.value.splice(index, 1);
  } else {
    selectedRouteIds.value.push(id);
  }
}

function handleDelete(route: Route) {
  if (confirm(`Delete route ${route.from} → ${route.to}?`)) {
    emit('delete-route', route);
  }
}
</script>

<style scoped>
.route-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.filters-section {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.search-input,
.filter-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 6px;
  font-size: 0.95rem;
}

.search-input:focus,
.filter-input:focus {
  outline: none;
  border-color: var(--primary-color, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.filters {
  display: flex;
  gap: 0.5rem;
}

.filter-input {
  min-width: 180px;
}

.add-button .icon {
  margin-right: 0.5rem;
  font-size: 1.2rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted, #6b7280);
}

.table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid var(--border-color, #ddd);
}

.routes-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.routes-table thead {
  background: var(--bg-secondary, #f9fafb);
  border-bottom: 2px solid var(--border-color, #ddd);
}

.routes-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.routes-table th:hover {
  background: var(--bg-tertiary, #f3f4f6);
}

.sort-indicator {
  margin-left: 0.5rem;
  color: var(--primary-color, #2563eb);
}

.routes-table tbody tr {
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  transition: background 0.2s;
}

.route-row:hover {
  background: var(--bg-tertiary, #f9fafb);
}

.routes-table td {
  padding: 1rem;
}

.checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.bulk-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--bg-tertiary, #f9fafb);
  border-radius: 6px;
  border: 1px solid var(--border-color, #e5e7eb);
}

.selection-info {
  font-weight: 500;
  color: var(--text-secondary, #4b5563);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.page-info {
  color: var(--text-muted, #6b7280);
  font-size: 0.95rem;
}
</style>
