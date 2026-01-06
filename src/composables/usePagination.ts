import { ref, computed, Ref } from 'vue';

export interface PaginationOptions {
  initialPage?: number;
  initialPerPage?: number;
}

/**
 * Composable for handling pagination
 */
export function usePagination<T>(
  items: Ref<T[]>,
  options: PaginationOptions = {}
) {
  const { initialPage = 1, initialPerPage = 10 } = options;

  const currentPage = ref(initialPage);
  const perPage = ref(initialPerPage);

  const totalItems = computed(() => items.value.length);
  const totalPages = computed(() => Math.ceil(totalItems.value / perPage.value));

  const paginatedItems = computed(() => {
    const start = (currentPage.value - 1) * perPage.value;
    const end = start + perPage.value;
    return items.value.slice(start, end);
  });

  const hasNextPage = computed(() => currentPage.value < totalPages.value);
  const hasPreviousPage = computed(() => currentPage.value > 1);

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page;
    }
  };

  const nextPage = () => {
    if (hasNextPage.value) {
      currentPage.value++;
    }
  };

  const previousPage = () => {
    if (hasPreviousPage.value) {
      currentPage.value--;
    }
  };

  const setPerPage = (count: number) => {
    perPage.value = count;
    currentPage.value = 1; // Reset to first page
  };

  const reset = () => {
    currentPage.value = initialPage;
    perPage.value = initialPerPage;
  };

  return {
    currentPage,
    perPage,
    totalItems,
    totalPages,
    paginatedItems,
    hasNextPage,
    hasPreviousPage,
    goToPage,
    nextPage,
    previousPage,
    setPerPage,
    reset,
  };
}
