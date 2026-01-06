import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAppStore = defineStore('app', () => {
  // State
  const sidebarOpen = ref(true);
  const theme = ref<'light' | 'dark'>('light');
  const notifications = ref<any[]>([]);
  const currentModule = ref<'deepsea' | 'olya' | 'balakovo'>('deepsea');
  const loading = ref(false);

  // Actions
  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value;
  }

  function setSidebarOpen(value: boolean) {
    sidebarOpen.value = value;
  }

  function closeSidebar() {
    sidebarOpen.value = false;
  }

  function openSidebar() {
    sidebarOpen.value = true;
  }

  function setCurrentModule(module: 'deepsea' | 'olya' | 'balakovo') {
    currentModule.value = module;
  }

  function setLoading(value: boolean) {
    loading.value = value;
  }

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light';
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme.value);
  }

  function addNotification(notification: {
    id?: string
    type: 'info' | 'success' | 'warning' | 'error'
    message: string
    duration?: number
  }) {
    const id = notification.id || Date.now().toString();
    const duration = notification.duration || 5000;
    
    notifications.value.push({
      ...notification,
      id,
      timestamp: Date.now(),
    });

    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }
  }

  function removeNotification(id: string) {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index !== -1) {
      notifications.value.splice(index, 1);
    }
  }

  function clearNotifications() {
    notifications.value = [];
  }

  return {
    // State
    sidebarOpen,
    theme,
    notifications,
    currentModule,
    loading,
    // Actions
    toggleSidebar,
    setSidebarOpen,
    closeSidebar,
    openSidebar,
    setCurrentModule,
    setLoading,
    toggleTheme,
    addNotification,
    removeNotification,
    clearNotifications,
  };
});
