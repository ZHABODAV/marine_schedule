<template>
  <button
    :type="type"
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="button__spinner"></span>
    <span v-if="icon && !loading" class="button__icon">{{ icon }}</span>
    <span v-if="$slots.default" class="button__text">
      <slot></slot>
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'button' | 'submit' | 'reset'
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'ghost'
  size?: 'small' | 'medium' | 'large'
  icon?: string
  loading?: boolean
  disabled?: boolean
  fullWidth?: boolean
}

interface Emits {
  (e: 'click', event: MouseEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'button',
  variant: 'primary',
  size: 'medium',
  loading: false,
  disabled: false,
  fullWidth: false
})

const emit = defineEmits<Emits>()

const buttonClasses = computed(() => [
  'base-button',
  `base-button--${props.variant}`,
  `base-button--${props.size}`,
  {
    'base-button--loading': props.loading,
    'base-button--disabled': props.disabled,
    'base-button--full-width': props.fullWidth
  }
])

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.base-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
  border-radius: 4px;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
}

.base-button:focus-visible {
  outline: 2px solid #3498db;
  outline-offset: 2px;
}

/* Sizes */
.base-button--small {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.base-button--medium {
  padding: 0.5rem 1rem;
  font-size: 1rem;
}

.base-button--large {
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
}

/* Variants */
.base-button--primary {
  background: #3498db;
  color: white;
}

.base-button--primary:hover:not(:disabled) {
  background: #2980b9;
}

.base-button--secondary {
  background: #95a5a6;
  color: white;
}

.base-button--secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.base-button--danger {
  background: #e74c3c;
  color: white;
}

.base-button--danger:hover:not(:disabled) {
  background: #c0392b;
}

.base-button--success {
  background: #27ae60;
  color: white;
}

.base-button--success:hover:not(:disabled) {
  background: #229954;
}

.base-button--ghost {
  background: transparent;
  color: #3498db;
  border: 1px solid #3498db;
}

.base-button--ghost:hover:not(:disabled) {
  background: #e8f4f8;
}

/* States */
.base-button--disabled,
.base-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.base-button--loading {
  pointer-events: none;
}

.base-button--full-width {
  width: 100%;
}

/* Spinner */
.button__spinner {
  display: inline-block;
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.button__icon {
  display: inline-flex;
  align-items: center;
  font-size: 1.2em;
}

.button__text {
  display: inline-flex;
  align-items: center;
}
</style>
