<template>
  <div class="the-layout">
    <AppHeader />
    <AppSidebar />
    
    <main class="the-layout__main" :class="{ 'the-layout__main--sidebar-collapsed': !sidebarOpen }">
      <Transition name="page" mode="out-in">
        <LoadingSpinner v-if="isLoading" fullscreen message="Loading..." />
        <RouterView v-else />
      </Transition>
    </main>

    <!-- Global overlay when sidebar is open on mobile -->
    <Transition name="fade">
      <div
        v-if="sidebarOpen && isMobile"
        class="the-layout__overlay"
        @click="closeSidebar"
      ></div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterView } from 'vue-router'
import { useAppStore } from '@/stores/app'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'

const appStore = useAppStore()

const sidebarOpen = computed(() => appStore.sidebarOpen)
const isLoading = computed(() => appStore.loading)

const isMobile = ref(window.innerWidth <= 768)

const handleResize = () => {
  isMobile.value = window.innerWidth <= 768
}

const closeSidebar = () => {
  appStore.closeSidebar()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.the-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f5f5f5;
}

.the-layout__main {
  margin-top: 60px; /* Header height */
  margin-left: 240px; /* Sidebar width */
  padding: 2rem;
  min-height: calc(100vh - 60px);
  transition: margin-left 0.3s ease;
}

.the-layout__main--sidebar-collapsed {
  margin-left: 60px; /* Collapsed sidebar width */
}

.the-layout__overlay {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 85;
}

@media (max-width: 768px) {
  .the-layout__main {
    margin-left: 0;
    padding: 1rem;
  }

  .the-layout__main--sidebar-collapsed {
    margin-left: 0;
  }
}

/* Page transitions */
.page-enter-active,
.page-leave-active {
  transition: all 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
