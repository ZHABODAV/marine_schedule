<template>
  <div class="cost-allocation-fields">
    <div class="section-header">
      <h3 class="section-title">Cost Allocation</h3>
      <p class="section-description">Enter cost breakdown for this cargo commitment</p>
    </div>

    <div class="cost-inputs">
      <div class="form-group">
        <label for="operational-cost" class="form-label">
          Operational Cost ($)
        </label>
        <BaseInput
          id="operational-cost"
          v-model.number="localCosts.operationalCost"
          type="number"
          min="0"
          step="0.01"
          placeholder="0.00"
          :error="errors.operationalCost"
          @input="handleCostChange"
        />
        <span v-if="errors.operationalCost" class="error-message">
          {{ errors.operationalCost }}
        </span>
      </div>

      <div class="form-group">
        <label for="overhead-cost" class="form-label">
          Overhead Cost ($)
        </label>
        <BaseInput
          id="overhead-cost"
          v-model.number="localCosts.overheadCost"
          type="number"
          min="0"
          step="0.01"
          placeholder="0.00"
          :error="errors.overheadCost"
          @input="handleCostChange"
        />
        <span v-if="errors.overheadCost" class="error-message">
          {{ errors.overheadCost }}
        </span>
      </div>

      <div class="form-group">
        <label for="other-cost" class="form-label">
          Other Cost ($)
        </label>
        <BaseInput
          id="other-cost"
          v-model.number="localCosts.otherCost"
          type="number"
          min="0"
          step="0.01"
          placeholder="0.00"
          :error="errors.otherCost"
          @input="handleCostChange"
        />
        <span v-if="errors.otherCost" class="error-message">
          {{ errors.otherCost }}
        </span>
      </div>
    </div>

    <div class="total-cost-display">
      <div class="total-cost-label">
        <strong>Total Cost:</strong>
      </div>
      <div class="total-cost-value" :class="{ 'has-value': totalCost > 0 }">
        ${{ formatCurrency(totalCost) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { CostAllocation } from '@/types/cargo.types';
import BaseInput from '@/components/shared/BaseInput.vue';

// Props
interface Props {
  modelValue?: CostAllocation | null;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  disabled: false,
});

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: CostAllocation];
  'validation-change': [isValid: boolean];
}>();

// State
const localCosts = ref<CostAllocation>({
  operationalCost: 0,
  overheadCost: 0,
  otherCost: 0,
  totalCost: 0,
});

const errors = ref<Partial<Record<keyof CostAllocation, string>>>({});

// Computed
const totalCost = computed(() => {
  const operational = Number(localCosts.value.operationalCost) || 0;
  const overhead = Number(localCosts.value.overheadCost) || 0;
  const other = Number(localCosts.value.otherCost) || 0;
  return operational + overhead + other;
});

const isValid = computed(() => {
  return Object.keys(errors.value).length === 0 && 
         localCosts.value.operationalCost >= 0 &&
         localCosts.value.overheadCost >= 0 &&
         localCosts.value.otherCost >= 0;
});

// Watch for external changes
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      localCosts.value = {
        operationalCost: newValue.operationalCost || 0,
        overheadCost: newValue.overheadCost || 0,
        otherCost: newValue.otherCost || 0,
        totalCost: newValue.totalCost || 0,
      };
    } else {
      resetCosts();
    }
  },
  { immediate: true }
);

// Watch totalCost and update local state
watch(totalCost, (newTotal) => {
  localCosts.value.totalCost = newTotal;
  emitUpdate();
});

// Watch isValid and emit validation change
watch(isValid, (valid) => {
  emit('validation-change', valid);
});

// Methods
function handleCostChange() {
  validateCosts();
  emitUpdate();
}

function validateCosts(): boolean {
  errors.value = {};
  let valid = true;

  if (localCosts.value.operationalCost < 0) {
    errors.value.operationalCost = 'Operational cost cannot be negative';
    valid = false;
  }

  if (localCosts.value.overheadCost < 0) {
    errors.value.overheadCost = 'Overhead cost cannot be negative';
    valid = false;
  }

  if (localCosts.value.otherCost < 0) {
    errors.value.otherCost = 'Other cost cannot be negative';
    valid = false;
  }

  return valid;
}

function emitUpdate() {
  emit('update:modelValue', { ...localCosts.value });
}

function resetCosts() {
  localCosts.value = {
    operationalCost: 0,
    overheadCost: 0,
    otherCost: 0,
    totalCost: 0,
  };
  errors.value = {};
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

// Expose methods for parent component
defineExpose({
  validateCosts,
  resetCosts,
});
</script>

<style scoped>
.cost-allocation-fields {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background-color: var(--bg-secondary, #f9fafb);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
}

.section-header {
  margin-bottom: 0.5rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
  margin: 0 0 0.25rem 0;
}

.section-description {
  font-size: 0.875rem;
  color: var(--text-secondary, #6b7280);
  margin: 0;
}

.cost-inputs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 500;
  color: var(--text-primary, #1f2937);
  font-size: 0.95rem;
}

.error-message {
  color: var(--danger-color, #dc2626);
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.total-cost-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--bg-primary, #ffffff);
  border: 2px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  margin-top: 0.5rem;
}

.total-cost-label {
  font-size: 1rem;
  color: var(--text-primary, #1f2937);
}

.total-cost-label strong {
  font-weight: 600;
}

.total-cost-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-secondary, #6b7280);
  transition: color 0.2s ease;
}

.total-cost-value.has-value {
  color: var(--success-color, #059669);
}

@media (max-width: 1024px) {
  .cost-inputs {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .cost-allocation-fields {
    padding: 1rem;
  }

  .cost-inputs {
    grid-template-columns: 1fr;
  }

  .total-cost-display {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }

  .total-cost-value {
    font-size: 1.25rem;
  }
}
</style>
