<template>
  <aside class="app-sidebar" :class="{ 'app-sidebar--collapsed': !isOpen }">
    <nav class="sidebar-nav">
      <RouterLink
        v-for="item in navigationItems"
        :key="item.path"
        :to="item.path"
        class="sidebar-nav__item"
        active-class="sidebar-nav__item--active"
      >
        <span class="sidebar-nav__icon">{{ item.icon }}</span>
        <span v-if="isOpen" class="sidebar-nav__label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div v-if="isOpen" class="sidebar-footer">
      <div class="sidebar-footer__version">v1.0.0</div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { RouterLink } from 'vue-router'

const appStore = useAppStore()

const isOpen = computed(() => appStore.sidebarOpen)

const navigationItems = [
  {
    path: '/',
    label: 'Dashboard',
    icon: ''
  },
  {
    path: '/vessels',
    label: 'Vessels',
    icon: ''
  },
  {
    path: '/cargo',
    label: 'Cargo',
    icon: ''
  },
  {
    path: '/routes',
    label: 'Routes',
    icon: ''
  },
  {
    path: '/voyage-builder',
    label: 'Voyage Builder',
    icon: ''
  },
  {
    path: '/schedule',
    label: 'Schedule',
    icon: ''
  },
  {
    path: '/gantt',
    label: 'Gantt Chart',
    icon: ''
  },
  {
    path: '/network',
    label: 'Network',
    icon: ''
  },
  {
    path: '/financial',
    label: 'Financial',
    icon: ''
  },
  {
    path: '/reports',
    label: 'Reports',
    icon: ''
  }
]
</script>

<style scoped>
.app-sidebar {
  position: fixed;
  left: 0;
  top: 60px;
  bottom: 0;
  width: 240px;
  background: #34495e;
  color: white;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  z-index: 90;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}

.app-sidebar--collapsed {
  width: 60px;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.sidebar-nav__item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
  border-left: 3px solid transparent;
}

.sidebar-nav__item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.sidebar-nav__item--active {
  background: rgba(52, 152, 219, 0.2);
  border-left-color: #3498db;
  color: white;
  font-weight: 500;
}

.sidebar-nav__icon {
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
}

.sidebar-nav__label {
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-footer__version {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  text-align: center;
}

@media (max-width: 768px) {
  .app-sidebar {
    transform: translateX(-100%);
  }

  .app-sidebar:not(.app-sidebar--collapsed) {
    transform: translateX(0);
  }
}
</style>
