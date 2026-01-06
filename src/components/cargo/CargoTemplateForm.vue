<template>
  <BaseModal
    :show="show"
    :title="isEditMode ? 'Edit Cargo Template' : 'Create Cargo Template'"
    size="large"
    @close="handleClose"
  >
    <form @submit.prevent="handleSubmit" class="cargo-template-form">
      <div class="form-section">
        <h3 class="section-title">Template Information</h3>
        
        <div class="form-group">
          <label for="template-name" class="form-label">
            Template Name <span class="required">*</span>
          </label>
          <BaseInput
            id="template-name"
            v-model="formData.name"
            placeholder="e.g., Standard Container Cargo"
            required
            :error="errors.name"
          />
        </div>

        <div class="form-group">
          <label for="description" class="form-label">
            Description
          </label>
          <textarea
            id="description"
            v-model="formData.description"
            class="form-textarea"
            rows="3"
            placeholder="Enter template description..."
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Cargo Details</h3>
        
        <div class="form-group">
          <label for="commodity" class="form-label">
            Default Commodity <span class="required">*</span>
          </label>
          <BaseInput
            id="commodity"
            v-model="formData.commodity"
            placeholder="Enter commodity type..."
            required
            :error="errors.commodity"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="quantity" class="form-label">
              Standard Quantity (MT)
            </label>
            <BaseInput
              id="quantity"
              v-model.number="formData.quantity"
              type="number"
              min="0"
              placeholder="Optional quantity..."
            />
          </div>

          <div class="form-group">
            <label for="freight-rate" class="form-label">
              Default Freight Rate ($/MT)
            </label>
            <BaseInput
              id="freight-rate"
              v-model.number="formData.freightRate"
              type="number"
              min="0"
              step="0.01"
              placeholder="Optional freight rate..."
            />
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">Route Information</h3>
        
        <div class="form-row">
          <div class="form-group">
            <label for="load-port" class="form-label">
              Default Load Port
            </label>
            <BaseInput
              id="load-port"
              v-model="formData.loadPort"
              placeholder="Optional load port..."
            />
          </div>

          <div class="form-group">
            <label for="disch-port" class="form-label">
              Default Discharge Port
            </label>
            <BaseInput
              id="disch-port"
              v-model="formData.dischPort"
              placeholder="Optional discharge port..."
            />
          </div>
        </div>
      </div>

      <!-- Cost Allocation Fields -->
      <div class="form-section">
        <CostAllocationFields
          v-model="formData.costAllocation"
          @validation-change="handleCostValidationChange"
        />
      </div>

      <div class="form-section">
        <div class="form-group">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="formData.isDefault"
              class="checkbox-input"
            />
            <span>Set as default template</span>
          </label>
          <p class="help-text">The default template will be pre-selected when creating new cargo commitments.</p>
        </div>
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
          {{ submitting ? 'Saving...' : (isEditMode ? 'Update Template' : 'Create Template') }}
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { CargoTemplate, CargoTemplateFormData, CostAllocation } from '@/types/cargo.types';
import BaseModal from '@/components/shared/BaseModal.vue';
import BaseInput from '@/components/shared/BaseInput.vue';
import BaseButton from '@/components/shared/BaseButton.vue';
import CostAllocationFields from './CostAllocationFields.vue';

// Props
interface Props {
  show: boolean;
  template?: CargoTemplate | null;
  submitting?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  template: null,
  submitting: false,
});

// Emits
const emit = defineEmits<{
  close: [];
  submit: [data: CargoTemplateFormData];
}>();

// Computed
const isEditMode = computed(() => !!props.template);

// State
const formData = ref<CargoTemplateFormData>({
  name: '',
  description: '',
  commodity: '',
  quantity: undefined,
  loadPort: '',
  dischPort: '',
  freightRate: undefined,
  costAllocation: undefined,
  isDefault: false,
});

const errors = ref<Partial<Record<keyof CargoTemplateFormData, string>>>({});
const costValidationState = ref(true);

// Computed
const isFormValid = computed(() => {
  return (
    formData.value.name.trim() !== '' &&
    formData.value.commodity.trim() !== '' &&
    Object.keys(errors.value).length === 0 &&
    costValidationState.value
  );
});

// Watch for template changes
watch(
  () => props.template,
  (newTemplate) => {
    if (newTemplate) {
      formData.value = {
        name: newTemplate.name,
        description: newTemplate.description || '',
        commodity: newTemplate.commodity,
        quantity: newTemplate.quantity,
        loadPort: newTemplate.loadPort || '',
        dischPort: newTemplate.dischPort || '',
        freightRate: newTemplate.freightRate,
        costAllocation: newTemplate.operationalCost !== undefined ? {
          operationalCost: newTemplate.operationalCost || 0,
          overheadCost: newTemplate.overheadCost || 0,
          otherCost: newTemplate.otherCost || 0,
          totalCost: (newTemplate.operationalCost || 0) + (newTemplate.overheadCost || 0) + (newTemplate.otherCost || 0),
        } : undefined,
        isDefault: newTemplate.isDefault || false,
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
    name: '',
    description: '',
    commodity: '',
    quantity: undefined,
    loadPort: '',
    dischPort: '',
    freightRate: undefined,
    costAllocation: undefined,
    isDefault: false,
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

  if (!formData.value.name.trim()) {
    errors.value.name = 'Template name is required';
    isValid = false;
  }

  if (!formData.value.commodity.trim()) {
    errors.value.commodity = 'Commodity is required';
    isValid = false;
  }

  if (formData.value.quantity !== undefined && formData.value.quantity < 0) {
    errors.value.quantity = 'Quantity cannot be negative';
    isValid = false;
  }

  if (formData.value.freightRate !== undefined && formData.value.freightRate < 0) {
    errors.value.freightRate = 'Freight rate cannot be negative';
    isValid = false;
  }

  return isValid;
}

function handleSubmit() {
  if (!validateForm()) {
    return;
  }

  const submitData: CargoTemplateFormData = { ...formData.value };
  
  // Flatten cost allocation into individual fields
  if (submitData.costAllocation) {
    submitData.operationalCost = submitData.costAllocation.operationalCost;
    submitData.overheadCost = submitData.costAllocation.overheadCost;
    submitData.otherCost = submitData.costAllocation.otherCost;
  }
  
  // Remove undefined values
  Object.keys(submitData).forEach(key => {
    if (submitData[key as keyof CargoTemplateFormData] === undefined || 
        submitData[key as keyof CargoTemplateFormData] === '') {
      delete submitData[key as keyof CargoTemplateFormData];
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
.cargo-template-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 0.5rem;
  max-height: 70vh;
  overflow-y: auto;
}

.form-section {
  padding: 1.5rem;
  background-color: var(--bg-secondary, #f9fafb);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
}

.section-title {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-group:last-child {
  margin-bottom: 0;
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-size: 0.95rem;
  color: var(--text-primary, #1f2937);
}

.checkbox-input {
  width: 1.25rem;
  height: 1.25rem;
  cursor: pointer;
  accent-color: var(--primary-color, #2563eb);
}

.help-text {
  margin: 0.5rem 0 0 2rem;
  font-size: 0.85rem;
  color: var(--text-secondary, #6b7280);
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

  .cargo-template-form {
    padding: 0;
    max-height: 80vh;
  }

  .form-section {
    padding: 1rem;
  }
}
</style>
