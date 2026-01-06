import { ref, Ref } from 'vue';
import { handleApiError } from '@/services/api';
import { useAppStore } from '@/stores/app';

export interface UseApiOptions {
  showSuccessNotification?: boolean;
  showErrorNotification?: boolean;
  successMessage?: string;
  loadingState?: Ref<boolean>;
}

/**
 * Composable for handling API requests with loading states and error handling
 */
export function useApi<T = any>(
  apiCall: (...args: any[]) => Promise<T>,
  options: UseApiOptions = {}
) {
  const {
    showSuccessNotification = false,
    showErrorNotification = true,
    successMessage = 'Operation completed successfully',
    loadingState,
  } = options;

  const appStore = useAppStore();
  const loading = loadingState || ref(false);
  const error = ref<string | null>(null);
  const data = ref<T | null>(null) as Ref<T | null>;

  const execute = async (...args: any[]) => {
    loading.value = true;
    error.value = null;
    data.value = null;

    try {
      const result = await apiCall(...args);
      data.value = result;

      if (showSuccessNotification) {
        appStore.addNotification({
          type: 'success',
          message: successMessage,
        });
      }

      return result;
    } catch (e: any) {
      const errorMessage = handleApiError(e);
      error.value = errorMessage;

      if (showErrorNotification) {
        appStore.addNotification({
          type: 'error',
          message: errorMessage,
        });
      }

      throw e;
    } finally {
      loading.value = false;
    }
  };

  const reset = () => {
    loading.value = false;
    error.value = null;
    data.value = null;
  };

  return {
    loading,
    error,
    data,
    execute,
    reset,
  };
}

/**
 * Composable for handling async operations with automatic error handling
 */
export function useAsyncOperation() {
  const appStore = useAppStore();

  const withErrorHandling = async <T>(
    operation: () => Promise<T>,
    errorMessage?: string
  ): Promise<T | null> => {
    try {
      return await operation();
    } catch (e: any) {
      const message = errorMessage || handleApiError(e);
      appStore.addNotification({
        type: 'error',
        message,
      });
      return null;
    }
  };

  const withLoadingAndErrorHandling = async <T>(
    operation: () => Promise<T>,
    loadingRef: Ref<boolean>,
    errorRef?: Ref<string | null>,
    errorMessage?: string
  ): Promise<T | null> => {
    loadingRef.value = true;
    if (errorRef) {
      errorRef.value = null;
    }

    try {
      const result = await operation();
      return result;
    } catch (e: any) {
      const message = errorMessage || handleApiError(e);
      if (errorRef) {
        errorRef.value = message;
      }
      appStore.addNotification({
        type: 'error',
        message,
      });
      return null;
    } finally {
      loadingRef.value = false;
    }
  };

  return {
    withErrorHandling,
    withLoadingAndErrorHandling,
  };
}
