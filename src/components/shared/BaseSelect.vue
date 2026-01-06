<template>
  <div class="base-select" :class="{ 'base-select--error': error }">
    <label v-if="label" :for="selectId" class="base-select__label">
      {{ label }}
      <span v-if="required" class="base-select__required">*</span>
    </label>

    <div class="base-select__wrapper">
      <select
        :id="selectId"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        class="base-select__field"
        @change="handleChange"
      >
        <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
        <option
          v-for="option in options"
          :key="getOptionValue(option)"
          :value="getOptionValue(option)"
        >
          {{ getOptionLabel(option) }}
        </option>
      </select>
      <span class="base-select__arrow">▼</span>
    </div>

    <span v-if="error" class="base-select__error-message">{{ error }}</span>
    <span v-else-if="hint" class="base-select__hint">{{ hint }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Option {
  value: string | number
  label: string
}

interface Props {
  modelValue: string | number
  options: Option[] | string[] | number[]
  label?: string
  placeholder?: string
  hint?: string
  error?: string
  disabled?: boolean
  required?: boolean
  valueKey?: string
  labelKey?: string
}

interface Emits {
  (e: 'update:modelValue', value: string | number): void
  (e: 'change', value: string | number): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  required: false,
  valueKey: 'value',
  labelKey: 'label'
})

const emit = defineEmits<Emits>()

const selectId = computed(() => `select-${Math.random().toString(36).substring(7)}`)

const getOptionValue = (option: Option | string | number): string | number => {
  if (typeof option === 'object') {
    return option[props.valueKey as keyof Option] as string | number
  }
  return option
}

const getOptionLabel = (option: Option | string | number): string => {
  if (typeof option === 'object') {
    return option[props.labelKey as keyof Option] as string
  }
  return String(option)
}

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const value = target.value
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style scoped>
.base-select {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.base-select__label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #333;
}

.base-select__required {
  color: #e74c3c;
  margin-left: 0.25rem;
}

.base-select__wrapper {
  position: relative;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  background: white;
  transition: border-color 0.2s ease;
}

.base-select__wrapper:focus-within {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.base-select--error .base-select__wrapper {
  border-color: #e74c3c;
}

.base-select--error .base-select__wrapper:focus-within {
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

.base-select__field {
  width: 100%;
  border: none;
  outline: none;
  padding: 0.5rem 2.5rem 0.5rem 0.75rem;
  font-size: 1rem;
  font-family: inherit;
  background: transparent;
  cursor: pointer;
  appearance: none;
}

.base-select__field:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  background: #f5f5f5;
}

.base-select__arrow {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #666;
  font-size: 0.75rem;
}

.base-select__error-message {
  font-size: 0.875rem;
  color: #e74c3c;
}

.base-select__hint {
  font-size: 0.875rem;
  color: #666;
}
</style>
