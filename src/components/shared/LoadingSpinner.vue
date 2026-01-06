<template>
  <div class="loading-spinner" :class="{ 'loading-spinner--fullscreen': fullscreen }">
    <div class="spinner" :style="spinnerStyle">
      <div class="spinner__circle"></div>
    </div>
    <p v-if="message" class="loading-spinner__message">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'small' | 'medium' | 'large'
  message?: string
  fullscreen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  message: '',
  fullscreen: false
})

const spinnerStyle = computed(() => {
  const sizes = {
    small: '24px',
    medium: '40px',
    large: '60px'
  }
  return {
    width: sizes[props.size],
    height: sizes[props.size]
  }
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
}

.loading-spinner--fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(26, 29, 35, 0.9);
  z-index: 9999;
}

.spinner {
  position: relative;
  display: inline-block;
}

.spinner__circle {
  width: 100%;
  height: 100%;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner__message {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
  text-align: center;
}
</style>
