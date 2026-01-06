<template>
  <BaseModal
    :show="show"
    :title="isEditMode ? 'Edit Cargo Commitment' : 'Add Cargo Commitment'"
    @close="handleClose"
  >
    <form @submit.prevent="handleSubmit" class="cargo-form">
      <div class="form-group">
        <label for="cargo-id" class="form-label">
          Cargo ID <span class="required">*</span>
        </label>
        <BaseInput
          id="cargo-id"
          v-model="formData.id"
          :disabled="isEditMode"
          placeholder="Enter cargo ID..."
          required
          :error="errors.id"
        />
      </div>

      <div class="form-group">
        <label for="commodity" class="form-label">
          Commodity <span class="required">*</span>
        </label>
        <BaseInput
          id="commodity"
          v-model="formData.commodity"
          placeholder="Enter commodity type..."
          required
          :error="errors.commodity"
        />
      </div>

      <div class="form-group">
        <label for="quantity" class="form-label">
          Quantity (MT) <span class="required">*</span>
        </label>
        <BaseInput
          id="quantity"
          v-model.number="formData.quantity"
          type="number"
          min="0"
          placeholder="Enter quantity..."
          required
          :error="errors.quantity"
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="load-port" class="form-label">
            Load Port <span class="required">*</span>
          </label>
          <BaseInput
            id="load-port"
            v-model="formData.loadPort"
            placeholder="Enter load port..."
            required
            :error="errors.loadPort"
          />
        </div>

        <div class="form-group">
          <label for="disch-port" class="form-label">
            Discharge Port <span class="required">*</span>
          </label>
          <BaseInput
            id="disch-port"
            v-model="formData.dischPort"
            placeholder="Enter discharge port..."
            required
            :error="errors.dischPort"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="laycan-start" class="form-label">
            Laycan Start <span class="required">*</span>
          </label>
          <BaseInput
            id="laycan-start"
            v-model="formData.laycanStart"
            type="date"
            required
            :error="errors.laycanStart"
          />
        </div>

        <div class="form-group">
          <label for="laycan-end" class="form-label">
            Laycan End <span class="required">*</span>
          </label>
          <BaseInput
            id="laycan-end"
            v-model="formData.laycanEnd"
            type="date"
            required
            :error="errors.laycanEnd"
          />
        </div>
      </div>

      <div class="form-group" v-if="isEditMode">
        <label for="status" class="form-label">
          Status
        </label>
        <BaseSelect
          id="status"
          v-model="formData.status"
          :options="statusOptions"
        />
      </div>

      <div class="form-group">
        <label for="freight-rate" class="form-label">
          Freight Rate ($/MT)
        </label>
        <BaseInput
          id="freight-rate"
          v-model.number="formData.freightRate"
          type="number"
          min="0"
          step="0.01"
          placeholder="Enter freight rate..."
        />
      </div>

      <!-- Cost Allocation Fields -->
      <CostAllocationFields
        v-model="formData.costAllocation"
        @validation-change="handleCostValidationChange"
      />

      <div class="form-group">
        <label for="notes" class="form-label">
          Notes
        </label>
        <textarea
          id="notes"
          v-model="formData.notes"
          class="form-textarea"
          rows="3"
          placeholder="Enter any additional notes..."
        ></textarea>
      </div>

      <div class="form-actions">
        <BaseButton
          type="button"
          variant="secondary"
          @click="handleClose"
        >
          Cancel
        </BaseButton>
        <BaseButton
          type="submit"
          variant="primary"
          :disabled="submitting || !isFormValid"
        >
          {{ submitting ? 'Saving...' : (isEditMode ? 'Update Cargo' : 'Create Cargo') }}
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { CargoCommitment, CargoFormData, CostAllocation } from '@/types/cargo.types';
import BaseModal from '@/components/shared/BaseModal.vue';
import BaseInput from '@/components/shared/BaseInput.vue';
import BaseSelect from '@/components/shared/BaseSelect.vue';
import BaseButton from '@/components/shared/BaseButton.vue';
import CostAllocationFields from './CostAllocationFields.vue';

// Props
interface Props {
  show: boolean;
  cargo?: CargoCommitment | null;
  submitting?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  cargo: null,
  submitting: false,
});

// Emits
const emit = defineEmits<{
  close: [];
  submit: [data: CargoFormData];
}>();

// Computed
const isEditMode = computed(() => !!props.cargo);

// State
const formData = ref<CargoFormData>({
  id: '',
  commodity: '',
  quantity: 0,
  loadPort: '',
  dischPort: '',
  laycanStart: '',
  laycanEnd: '',
  status: 'Pending',
  freightRate: undefined,
  notes: undefined,
  costAllocation: undefined,
});

const errors = ref<Partial<Record<keyof CargoFormData, string>>>({});
const costValidationState = ref(true);

// Options
const statusOptions = [
  { value: 'Pending', label: 'Pending' },
  { value: 'Assigned', label: 'Assigned' },
  { value: 'Completed', label: 'Completed' },
  { value: 'Cancelled', label: 'Cancelled' },
];

// Computed
const isFormValid = computed(() => {
  return (
    formData.value.id &&
    formData.value.commodity &&
    formData.value.quantity > 0 &&
    formData.value.loadPort &&
    formData.value.dischPort &&
    formData.value.laycanStart &&
    formData.value.laycanEnd &&
    Object.keys(errors.value).length === 0 &&
    costValidationState.value
  );
});

// Watch for cargo changes
watch(
  () => props.cargo,
  (newCargo) => {
    if (newCargo) {
      formData.value = {
        id: newCargo.id,
        commodity: newCargo.commodity,
        quantity: newCargo.quantity,
        loadPort: newCargo.loadPort,
        dischPort: newCargo.dischPort,
        laycanStart: newCargo.laycanStart,
        laycanEnd: newCargo.laycanEnd,
        status: newCargo.status,
        freightRate: newCargo.freightRate,
        notes: newCargo.notes,
        costAllocation: newCargo.operationalCost !== undefined ? {
          operationalCost: newCargo.operationalCost || 0,
          overheadCost: newCargo.overheadCost || 0,
          otherCost: newCargo.otherCost || 0,
          totalCost: (newCargo.operationalCost || 0) + (newCargo.overheadCost || 0) + (newCargo.otherCost || 0),
        } : undefined,
      };
    } else {
      resetForm();
    }
    errors.value = {};
  },
  { immediate: true }
);

// Methods
function resetForm() {
  formData.value = {
    id: '',
    commodity: '',
    quantity: 0,
    loadPort: '',
    dischPort: '',
    laycanStart: '',
    laycanEnd: '',
    status: 'Pending',
    freightRate: undefined,
    notes: undefined,
    costAllocation: undefined,
  };
  errors.value = {};
  costValidationState.value = true;
}

function handleCostValidationChange(isValid: boolean) {
  costValidationState.value = isValid;
}

function validateForm(): boolean {
  errors.value = {};
  let isValid = true;

  if (!formData.value.id) {
    errors.value.id = 'Cargo ID is required';
    isValid = false;
  }

  if (!formData.value.commodity) {
    errors.value.commodity = 'Commodity is required';
    isValid = false;
  }

  if (formData.value.quantity <= 0) {
    errors.value.quantity = 'Quantity must be greater than 0';
    isValid = false;
  }

  if (!formData.value.loadPort) {
    errors.value.loadPort = 'Load port is required';
    isValid = false;
  }

  if (!formData.value.dischPort) {
    errors.value.dischPort = 'Discharge port is required';
    isValid = false;
  }

  if (!formData.value.laycanStart) {
    errors.value.laycanStart = 'Laycan start is required';
    isValid = false;
  }

  if (!formData.value.laycanEnd) {
    errors.value.laycanEnd = 'Laycan end is required';
    isValid = false;
  }

  if (formData.value.laycanStart && formData.value.laycanEnd) {
    if (new Date(formData.value.laycanStart) > new Date(formData.value.laycanEnd)) {
      errors.value.laycanEnd = 'Laycan end must be after laycan start';
      isValid = false;
    }
  }

  return isValid;
}

function handleSubmit() {
  if (!validateForm()) {
    return;
  }

  const submitData: CargoFormData = { ...formData.value };
  
  // Flatten cost allocation into individual fields for backward compatibility
  if (submitData.costAllocation) {
    submitData.operationalCost = submitData.costAllocation.operationalCost;
    submitData.overheadCost = submitData.costAllocation.overheadCost;
    submitData.otherCost = submitData.costAllocation.otherCost;
  }
  
  // Remove undefined values
  Object.keys(submitData).forEach(key => {
    if (submitData[key as keyof CargoFormData] === undefined) {
      delete submitData[key as keyof CargoFormData];
    }
  });

  emit('submit', submitData);
}

function handleClose() {
  resetForm();
  emit('close');
}
</script>

<style scoped>
.cargo-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 0.5rem;
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

.required {
  color: var(--danger-color, #dc2626);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color, #e5e7eb);
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
