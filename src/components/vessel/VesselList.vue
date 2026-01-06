<template>
  <div class="vessel-list">
    <!-- Search and Filters -->
    <div class="filters-section">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Search vessels by name or ID..."
          class="search-input"
        />
      </div>
      
      <div class="filters">
        <BaseSelect
          v-model="filterStatus"
          :options="statusOptions"
          placeholder="Filter by status"
          class="filter-select"
        />
        <BaseSelect
          v-model="filterType"
          :options="typeOptions"
          placeholder="Filter by type"
          class="filter-select"
        />
      </div>
      
      <BaseButton
        @click="$emit('add-vessel')"
        variant="primary"
        class="add-button"
      >
        <span class="icon">+</span>
        Add Vessel
      </BaseButton>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Empty State -->
    <div v-else-if="filteredVessels.length === 0" class="empty-state">
      <p>No vessels found.</p>
    </div>

    <!-- Vessels Table -->
    <div v-else class="table-container">
      <table class="vessels-table">
        <thead>
          <tr>
            <th @click="sort('id')">
              ID
              <span class="sort-indicator" v-if="sortBy === 'id'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="sort('name')">
              Name
              <span class="sort-indicator" v-if="sortBy === 'name'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="sort('class')">
              Class
              <span class="sort-indicator" v-if="sortBy === 'class'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="sort('dwt')">
              DWT
              <span class="sort-indicator" v-if="sortBy === 'dwt'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="sort('speed')">
              Speed (kn)
              <span class="sort-indicator" v-if="sortBy === 'speed'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="vessel in paginatedVessels"
            :key="vessel.id"
            @click="$emit('view-vessel', vessel)"
            class="vessel-row"
          >
            <td>{{ vessel.id }}</td>
            <td><strong>{{ vessel.name }}</strong></td>
            <td>{{ vessel.class }}</td>
            <td>{{ formatNumber(vessel.dwt) }}</td>
            <td>{{ vessel.speed }}</td>
            <td>
              <span :class="['status-badge', `status-${vessel.status.toLowerCase()}`]">
                {{ vessel.status }}
              </span>
            </td>
            <td class="actions-cell" @click.stop>
              <BaseButton
                @click="$emit('edit-vessel', vessel)"
                variant="secondary"
                size="small"
              >
                Edit
              </BaseButton>
              <BaseButton
                @click="handleDelete(vessel)"
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

    <!-- Pagination -->
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
import type { Vessel } from '@/types/vessel.types';
import BaseButton from '@/components/shared/BaseButton.vue';
import BaseSelect from '@/components/shared/BaseSelect.vue';
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue';

// Props
interface Props {
  vessels: Vessel[];
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

// Emits
const emit = defineEmits<{
  'add-vessel': [];
  'edit-vessel': [vessel: Vessel];
  'delete-vessel': [vessel: Vessel];
  'view-vessel': [vessel: Vessel];
}>();

// State
const searchTerm = ref('');
const filterStatus = ref('');
const filterType = ref('');
const sortBy = ref<keyof Vessel>('name');
const sortDirection = ref<'asc' | 'desc'>('asc');
const currentPage = ref(1);
const itemsPerPage = 10;

// Options
const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'maintenance', label: 'Maintenance' },
];

const typeOptions = computed(() => {
  const types = [...new Set(props.vessels.map(v => v.type))];
  return [
    { value: '', label: 'All Types' },
    ...types.map(type => ({ value: type, label: type })),
  ];
});

// Computed
const filteredVessels = computed(() => {
  let filtered = [...props.vessels];

  // Search filter
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(
      v =>
        v.name.toLowerCase().includes(term) ||
        v.id.toString().toLowerCase().includes(term)
    );
  }

  // Status filter
  if (filterStatus.value) {
    filtered = filtered.filter(v => v.status === filterStatus.value);
  }

  // Type filter
  if (filterType.value) {
    filtered = filtered.filter(v => v.type === filterType.value);
  }

  // Sorting
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
  Math.ceil(filteredVessels.value.length / itemsPerPage)
);

const paginatedVessels = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredVessels.value.slice(start, end);
});

// Methods
function sort(field: keyof Vessel) {
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

function handleDelete(vessel: Vessel) {
  if (confirm(`Delete vessel ${vessel.name}? This action cannot be undone.`)) {
    emit('delete-vessel', vessel);
  }
}
</script>

<style scoped>
.vessel-list {
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

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 6px;
  font-size: 0.95rem;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.filters {
  display: flex;
  gap: 0.5rem;
}

.filter-select {
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

.vessels-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.vessels-table thead {
  background: var(--bg-secondary, #f9fafb);
  border-bottom: 2px solid var(--border-color, #ddd);
}

.vessels-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.vessels-table th:hover {
  background: var(--bg-tertiary, #f3f4f6);
}

.sort-indicator {
  margin-left: 0.5rem;
  color: var(--primary-color, #2563eb);
}

.vessels-table tbody tr {
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  transition: background 0.2s;
}

.vessel-row {
  cursor: pointer;
}

.vessel-row:hover {
  background: var(--bg-tertiary, #f9fafb);
}

.vessels-table td {
  padding: 1rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-active {
  background: #d1fae5;
  color: #065f46;
}

.status-inactive {
  background: #fee2e2;
  color: #991b1b;
}

.status-maintenance {
  background: #fef3c7;
  color: #92400e;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
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
