<template>
  <header class="app-header">
    <div class="app-header__left">
      <button
        class="app-header__menu-toggle"
        type="button"
        aria-label="Toggle menu"
        @click="toggleSidebar"
      >
        
      </button>
      <h1 class="app-header__title">Vessel Scheduler</h1>
    </div>

    <div class="app-header__center">
      <div class="module-selector">
        <label for="module-select" class="module-selector__label">Module:</label>
        <select
          id="module-select"
          v-model="selectedModule"
          class="module-selector__select"
          @change="handleModuleChange"
        >
          <option value="deepsea">Deep Sea</option>
          <option value="olya">Olya</option>
          <option value="balakovo">Balakovo</option>
        </select>
      </div>
    </div>

    <div class="app-header__right">
      <button
        class="app-header__user"
        type="button"
        aria-label="User menu"
        @click="showUserMenu = !showUserMenu"
      >
        
      </button>
      
      <Transition name="dropdown">
        <div v-if="showUserMenu" class="user-menu">
          <div class="user-menu__item">Profile</div>
          <div class="user-menu__item">Settings</div>
          <div class="user-menu__divider"></div>
          <div class="user-menu__item">Logout</div>
        </div>
      </Transition>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const showUserMenu = ref(false)

const selectedModule = ref(appStore.currentModule)

const toggleSidebar = () => {
  appStore.toggleSidebar()
}

const handleModuleChange = () => {
  appStore.setCurrentModule(selectedModule.value)
}

// Sync with store changes
watch(() => appStore.currentModule, (newModule) => {
  selectedModule.value = newModule
})
</script>

<style scoped>
.app-header {
  height: 60px;
  background: #2c3e50;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.app-header__left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.app-header__menu-toggle {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background 0.2s ease;
  display: none;
}

.app-header__menu-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
}

@media (max-width: 768px) {
  .app-header__menu-toggle {
    display: block;
  }
}

.app-header__title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.app-header__center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.module-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.module-selector__label {
  font-size: 0.875rem;
  font-weight: 500;
}

.module-selector__select {
  background: white;
  color: #2c3e50;
  border: none;
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  outline: none;
}

.module-selector__select:focus {
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.3);
}

.app-header__right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  position: relative;
}

.app-header__user {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.app-header__user:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  color: #333;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 150px;
  overflow: hidden;
}

.user-menu__item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.user-menu__item:hover {
  background: #f5f5f5;
}

.user-menu__divider {
  height: 1px;
  background: #e0e0e0;
  margin: 0.25rem 0;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
