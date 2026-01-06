<template>
  <div class="cargo-list">
    <!-- Search and Filters -->
    <div class="filters-section">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Search cargo by ID or commodity..."
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
        <input
          v-model="filterPort"
          type="text"
          placeholder="Filter by port..."
          class="filter-input"
        />
      </div>
      
      <BaseButton
        @click="$emit('add-cargo')"
        variant="primary"
        class="add-button"
      >
        <span class="icon">+</span>
        Add Cargo
      </BaseButton>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" />

    <!-- Empty State -->
    <div v-else-if="filteredCargo.length === 0" class="empty-state">
      <p>No cargo commitments found.</p>
    </div>

    <!-- Cargo Table -->
    <div v-else class="table-container">
      <table class="cargo-table">
        <thead>
          <tr>
            <th @click="sort('id')">
              ID
              <span class="sort-indicator" v-if="sortBy === 'id'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="sort('commodity')">
              Commodity
              <span class="sort-indicator" v-if="sortBy === 'commodity'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="sort('quantity')">
              Quantity (MT)
              <span class="sort-indicator" v-if="sortBy === 'quantity'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th>Load Port</th>
            <th>Discharge Port</th>
            <th @click="sort('laycanStart')">
              Laycan Start
              <span class="sort-indicator" v-if="sortBy === 'laycanStart'">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th>Laycan End</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="cargo in paginatedCargo"
            :key="cargo.id"
            @click="$emit('view-cargo', cargo)"
            class="cargo-row"
          >
            <td>{{ cargo.id }}</td>
            <td><strong>{{ cargo.commodity }}</strong></td>
            <td>{{ formatNumber(cargo.quantity) }}</td>
            <td>{{ cargo.loadPort }}</td>
            <td>{{ cargo.dischPort }}</td>
            <td>{{ formatDate(cargo.laycanStart) }}</td>
            <td>{{ formatDate(cargo.laycanEnd) }}</td>
            <td>
              <span :class="['status-badge', `status-${cargo.status.toLowerCase()}`]">
                {{ cargo.status }}
              </span>
            </td>
            <td class="actions-cell" @click.stop>
              <BaseButton
                @click="$emit('edit-cargo', cargo)"
                variant="secondary"
                size="small"
              >
                Edit
              </BaseButton>
              <BaseButton
                @click="handleDelete(cargo)"
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
import type { CargoCommitment } from '@/types/cargo.types';
import BaseButton from '@/components/shared/BaseButton.vue';
import BaseSelect from '@/components/shared/BaseSelect.vue';
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue';

// Props
interface Props {
  cargo: CargoCommitment[];
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

// Emits
const emit = defineEmits<{
  'add-cargo': [];
  'edit-cargo': [cargo: CargoCommitment];
  'delete-cargo': [cargo: CargoCommitment];
  'view-cargo': [cargo: CargoCommitment];
}>();

// State
const searchTerm = ref('');
const filterStatus = ref('');
const filterPort = ref('');
const sortBy = ref<keyof CargoCommitment>('laycanStart');
const sortDirection = ref<'asc' | 'desc'>('asc');
const currentPage = ref(1);
const itemsPerPage = 10;

// Options
const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'Pending', label: 'Pending' },
  { value: 'Assigned', label: 'Assigned' },
  { value: 'Completed', label: 'Completed' },
  { value: 'Cancelled', label: 'Cancelled' },
];

// Computed
const filteredCargo = computed(() => {
  let filtered = [...props.cargo];

  // Search filter
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(
      c =>
        c.id.toString().toLowerCase().includes(term) ||
        c.commodity.toLowerCase().includes(term)
    );
  }

  // Status filter
  if (filterStatus.value) {
    filtered = filtered.filter(c => c.status === filterStatus.value);
  }

  // Port filter
  if (filterPort.value) {
    const port = filterPort.value.toLowerCase();
    filtered = filtered.filter(
      c =>
        c.loadPort.toLowerCase().includes(port) ||
        c.dischPort.toLowerCase().includes(port)
    );
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
  Math.ceil(filteredCargo.value.length / itemsPerPage)
);

const paginatedCargo = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredCargo.value.slice(start, end);
});

// Methods
function sort(field: keyof CargoCommitment) {
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

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function handleDelete(cargo: CargoCommitment) {
  if (confirm(`Delete cargo commitment ${cargo.id}? This action cannot be undone.`)) {
    emit('delete-cargo', cargo);
  }
}
</script>

<style scoped>
.cargo-list {
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

.filter-select {
  min-width: 180px;
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

.cargo-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.cargo-table thead {
  background: var(--bg-secondary, #f9fafb);
  border-bottom: 2px solid var(--border-color, #ddd);
}

.cargo-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
  white-space: nowrap;
}

.cargo-table th:hover {
  background: var(--bg-tertiary, #f3f4f6);
}

.sort-indicator {
  margin-left: 0.5rem;
  color: var(--primary-color, #2563eb);
}

.cargo-table tbody tr {
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  transition: background 0.2s;
}

.cargo-row {
  cursor: pointer;
}

.cargo-row:hover {
  background: var(--bg-tertiary, #f9fafb);
}

.cargo-table td {
  padding: 1rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-assigned {
  background: #dbeafe;
  color: #1e40af;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
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
