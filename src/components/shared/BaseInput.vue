<template>
  <div class="base-input" :class="{ 'base-input--error': error }">
    <label v-if="label" :for="inputId" class="base-input__label">
      {{ label }}
      <span v-if="required" class="base-input__required">*</span>
    </label>

    <div class="base-input__wrapper">
      <span v-if="prefix" class="base-input__prefix">{{ prefix }}</span>
      
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :min="min"
        :max="max"
        :step="step"
        class="base-input__field"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />
      
      <span v-if="suffix" class="base-input__suffix">{{ suffix }}</span>
    </div>

    <span v-if="error" class="base-input__error-message">{{ error }}</span>
    <span v-else-if="hint" class="base-input__hint">{{ hint }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string | number
  type?: 'text' | 'number' | 'email' | 'password' | 'tel' | 'url' | 'date' | 'time'
  label?: string
  placeholder?: string
  hint?: string
  error?: string
  prefix?: string
  suffix?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  min?: number | string
  max?: number | string
  step?: number | string
}

interface Emits {
  (e: 'update:modelValue', value: string | number): void
  (e: 'blur'): void
  (e: 'focus'): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  required: false
})

const emit = defineEmits<Emits>()

const inputId = computed(() => `input-${Math.random().toString(36).substring(7)}`)

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = props.type === 'number' ? Number(target.value) : target.value
  emit('update:modelValue', value)
}

const handleBlur = () => {
  emit('blur')
}

const handleFocus = () => {
  emit('focus')
}
</script>

<style scoped>
.base-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.base-input__label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #333;
}

.base-input__required {
  color: #e74c3c;
  margin-left: 0.25rem;
}

.base-input__wrapper {
  display: flex;
  align-items: center;
  position: relative;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  background: white;
  transition: border-color 0.2s ease;
}

.base-input__wrapper:focus-within {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.base-input--error .base-input__wrapper {
  border-color: #e74c3c;
}

.base-input--error .base-input__wrapper:focus-within {
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

.base-input__field {
  flex: 1;
  border: none;
  outline: none;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  font-family: inherit;
  background: transparent;
}

.base-input__field:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  background: #f5f5f5;
}

.base-input__field::placeholder {
  color: #999;
}

.base-input__prefix,
.base-input__suffix {
  padding: 0 0.75rem;
  color: #666;
  font-size: 0.875rem;
  white-space: nowrap;
}

.base-input__error-message {
  font-size: 0.875rem;
  color: #e74c3c;
}

.base-input__hint {
  font-size: 0.875rem;
  color: #666;
}
</style>
