import { ref, computed, Ref } from 'vue';

export interface FilterOptions<T> {
  searchFields?: (keyof T)[];
  sortField?: keyof T;
  sortOrder?: 'asc' | 'desc';
}

/**
 * Composable for filtering and sorting data
 */
export function useFilters<T extends Record<string, any>>(
  items: Ref<T[]>,
  options: FilterOptions<T> = {}
) {
  const { searchFields = [], sortField, sortOrder = 'asc' } = options;

  const searchQuery = ref('');
  const currentSortField = ref<keyof T | undefined>(sortField);
  const currentSortOrder = ref<'asc' | 'desc'>(sortOrder);
  const filters = ref<Partial<Record<keyof T, any>>>({});

  // Filtered items based on search and filters
  const filteredItems = computed(() => {
    let result = items.value;

    // Apply search filter
    if (searchQuery.value && searchFields.length > 0) {
      const query = searchQuery.value.toLowerCase();
      result = result.filter(item =>
        searchFields.some(field => {
          const value = item[field];
          return value && String(value).toLowerCase().includes(query);
        })
      );
    }

    // Apply custom filters
    Object.entries(filters.value).forEach(([field, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        result = result.filter(item => {
          const itemValue = item[field as keyof T];
          if (Array.isArray(value)) {
            return value.includes(itemValue);
          }
          return itemValue === value;
        });
      }
    });

    return result;
  });

  // Sorted items
  const sortedItems = computed(() => {
    if (!currentSortField.value) return filteredItems.value;

    const sorted = [...filteredItems.value].sort((a, b) => {
      const aValue = a[currentSortField.value!];
      const bValue = b[currentSortField.value!];

      if (aValue === bValue) return 0;

      let comparison = 0;
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        comparison = aValue.localeCompare(bValue);
      } else if (typeof aValue === 'number' && typeof bValue === 'number') {
        comparison = aValue - bValue;
      } else {
        comparison = String(aValue).localeCompare(String(bValue));
      }

      return currentSortOrder.value === 'asc' ? comparison : -comparison;
    });

    return sorted;
  });

  const setSearch = (query: string) => {
    searchQuery.value = query;
  };

  const setFilter = (field: keyof T, value: any) => {
    filters.value[field] = value;
  };

  const clearFilter = (field: keyof T) => {
    delete filters.value[field];
  };

  const clearAllFilters = () => {
    searchQuery.value = '';
    filters.value = {};
  };

  const sort = (field: keyof T) => {
    if (currentSortField.value === field) {
      currentSortOrder.value = currentSortOrder.value === 'asc' ? 'desc' : 'asc';
    } else {
      currentSortField.value = field;
      currentSortOrder.value = 'asc';
    }
  };

  return {
    searchQuery,
    filters,
    currentSortField,
    currentSortOrder,
    filteredItems,
    sortedItems,
    setSearch,
    setFilter,
    clearFilter,
    clearAllFilters,
    sort,
  };
}
