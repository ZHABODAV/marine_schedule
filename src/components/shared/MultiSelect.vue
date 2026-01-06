<template>
  <div class="multi-select" :class="{ 'is-open': isOpen, 'is-disabled': disabled }">
    <div class="multi-select-trigger" @click="toggleDropdown">
      <div class="selected-items">
        <template v-if="selectedOptions.length === 0">
          <span class="placeholder">{{ placeholder }}</span>
        </template>
        <template v-else-if="selectedOptions.length <= 3">
          <span v-for="option in selectedOptions" :key="option.value" class="selected-tag">
            {{ option.label }}
            <button class="tag-remove" @click.stop="removeItem(option.value)">×</button>
          </span>
        </template>
        <template v-else>
          <span class="selected-count">{{ selectedOptions.length }} selected</span>
        </template>
      </div>
      <svg class="dropdown-arrow" width="12" height="8" viewBox="0 0 12 8" fill="none">
        <path d="M1 1L6 6L11 1" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
      </svg>
    </div>

    <Transition name="dropdown">
      <div v-if="isOpen" class="multi-select-dropdown">
        <!-- Search -->
        <div v-if="searchable" class="dropdown-search">
          <input
            ref="searchInput"
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="Search..."
            @click.stop
          />
        </div>

        <!-- Select All -->
        <div v-if="showSelectAll" class="dropdown-option select-all" @click="toggleSelectAll">
          <input
            type="checkbox"
            :checked="isAllSelected"
            :indeterminate.prop="isSomeSelected"
            @click.stop
          />
          <span>Select All</span>
        </div>

        <!-- Options -->
        <div class="dropdown-options">
          <div
            v-for="option in filteredOptions"
            :key="option.value"
            class="dropdown-option"
            :class="{ 'is-selected': isSelected(option.value) }"
            @click="toggleOption(option.value)"
          >
            <input
              type="checkbox"
              :checked="isSelected(option.value)"
              @click.stop
            />
            <span>{{ option.label }}</span>
          </div>
          <div v-if="filteredOptions.length === 0" class="dropdown-empty">
            No options found
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';

interface Option {
  value: string;
  label: string;
}

interface Props {
  modelValue: string[];
  options: Option[];
  placeholder?: string;
  disabled?: boolean;
  searchable?: boolean;
  showSelectAll?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Select...',
  disabled: false,
  searchable: true,
  showSelectAll: true,
});

const emit = defineEmits<{
  'update:modelValue': [value: string[]];
}>();

const isOpen = ref(false);
const searchQuery = ref('');
const searchInput = ref<HTMLInputElement>();

const selectedOptions = computed(() =>
  props.options.filter(opt => props.modelValue.includes(opt.value))
);

const filteredOptions = computed(() => {
  if (!searchQuery.value) return props.options;
  const query = searchQuery.value.toLowerCase();
  return props.options.filter(opt =>
    opt.label.toLowerCase().includes(query)
  );
});

const isAllSelected = computed(() =>
  props.options.length > 0 && props.modelValue.length === props.options.length
);

const isSomeSelected = computed(() =>
  props.modelValue.length > 0 && props.modelValue.length < props.options.length
);

function toggleDropdown() {
  if (props.disabled) return;
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    setTimeout(() => searchInput.value?.focus(), 50);
  }
}

function isSelected(value: string): boolean {
  return props.modelValue.includes(value);
}

function toggleOption(value: string) {
  const newValue = isSelected(value)
    ? props.modelValue.filter(v => v !== value)
    : [...props.modelValue, value];
  emit('update:modelValue', newValue);
}

function removeItem(value: string) {
  const newValue = props.modelValue.filter(v => v !== value);
  emit('update:modelValue', newValue);
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    emit('update:modelValue', []);
  } else {
    emit('update:modelValue', props.options.map(opt => opt.value));
  }
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement;
  if (!target.closest('.multi-select')) {
    isOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});

watch(isOpen, (newValue) => {
  if (!newValue) {
    searchQuery.value = '';
  }
});
</script>

<style scoped>
.multi-select {
  position: relative;
  width: 100%;
}

.multi-select-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 38px;
}

.multi-select-trigger:hover {
  border-color: var(--color-primary);
}

.multi-select.is-open .multi-select-trigger {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.multi-select.is-disabled .multi-select-trigger {
  opacity: 0.5;
  cursor: not-allowed;
}

.selected-items {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  overflow: hidden;
}

.placeholder {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.125rem 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.tag-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  padding: 0;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 12px;
  line-height: 1;
  transition: background 0.2s;
}

.tag-remove:hover {
  background: rgba(255, 255, 255, 0.3);
}

.selected-count {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
}

.dropdown-arrow {
  flex-shrink: 0;
  color: var(--color-text-secondary);
  transition: transform 0.2s;
}

.multi-select.is-open .dropdown-arrow {
  transform: rotate(180deg);
}

.multi-select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 300px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dropdown-search {
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.search-input {
  width: 100%;
  padding: 0.5rem;
  font-size: 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background);
  color: var(--color-text);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.dropdown-options {
  overflow-y: auto;
  flex: 1;
}

.dropdown-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 0.875rem;
}

.dropdown-option:hover {
  background: var(--color-background-soft);
}

.dropdown-option.is-selected {
  background: rgba(var(--color-primary-rgb), 0.1);
}

.dropdown-option.select-all {
  border-bottom: 1px solid var(--color-border);
  font-weight: 500;
}

.dropdown-option input[type="checkbox"] {
  cursor: pointer;
}

.dropdown-empty {
  padding: 1rem;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

/* Enter/leave transitions */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
