<template>
  <BaseModal
    :show="show"
    :title="isEditMode ? 'Edit Vessel' : 'Add Vessel'"
    @close="handleClose"
  >
    <form @submit.prevent="handleSubmit" class="vessel-form">
      <div class="form-group">
        <label for="vessel-id" class="form-label">
          Vessel ID <span class="required">*</span>
        </label>
        <BaseInput
          id="vessel-id"
          v-model="formData.id"
          :disabled="isEditMode"
          placeholder="Enter vessel ID..."
          required
          :error="errors.id"
        />
      </div>

      <div class="form-group">
        <label for="vessel-name" class="form-label">
          Vessel Name <span class="required">*</span>
        </label>
        <BaseInput
          id="vessel-name"
          v-model="formData.name"
          placeholder="Enter vessel name..."
          required
          :error="errors.name"
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="vessel-type" class="form-label">
            Type <span class="required">*</span>
          </label>
          <BaseSelect
            id="vessel-type"
            v-model="formData.type"
            :options="typeOptions"
            placeholder="Select type..."
            required
            :error="errors.type"
          />
        </div>

        <div class="form-group">
          <label for="vessel-class" class="form-label">
            Class <span class="required">*</span>
          </label>
          <BaseInput
            id="vessel-class"
            v-model="formData.class"
            placeholder="Enter vessel class..."
            required
            :error="errors.class"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="vessel-dwt" class="form-label">
            DWT (tons) <span class="required">*</span>
          </label>
          <BaseInput
            id="vessel-dwt"
            v-model.number="formData.dwt"
            type="number"
            min="0"
            placeholder="Enter DWT..."
            required
            :error="errors.dwt"
          />
        </div>

        <div class="form-group">
          <label for="vessel-speed" class="form-label">
            Speed (knots) <span class="required">*</span>
          </label>
          <BaseInput
            id="vessel-speed"
            v-model.number="formData.speed"
            type="number"
            min="0"
            step="0.1"
            placeholder="Enter speed..."
            required
            :error="errors.speed"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="vessel-draft" class="form-label">
            Draft (m)
          </label>
          <BaseInput
            id="vessel-draft"
            v-model.number="formData.draft"
            type="number"
            min="0"
            step="0.1"
            placeholder="Enter draft..."
            :error="errors.draft"
          />
        </div>

        <div class="form-group">
          <label for="vessel-loa" class="form-label">
            LOA (m)
          </label>
          <BaseInput
            id="vessel-loa"
            v-model.number="formData.loa"
            type="number"
            min="0"
            step="0.1"
            placeholder="Enter length overall..."
            :error="errors.loa"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="vessel-fuel-consumption" class="form-label">
            Fuel Consumption (tons/day)
          </label>
          <BaseInput
            id="vessel-fuel-consumption"
            v-model.number="formData.fuelConsumption"
            type="number"
            min="0"
            step="0.1"
            placeholder="Enter fuel consumption..."
            :error="errors.fuelConsumption"
          />
        </div>

        <div class="form-group">
          <label for="vessel-status" class="form-label">
            Status <span class="required">*</span>
          </label>
          <BaseSelect
            id="vessel-status"
            v-model="formData.status"
            :options="statusOptions"
            required
            :error="errors.status"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="vessel-notes" class="form-label">
          Notes
        </label>
        <textarea
          id="vessel-notes"
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
          {{ submitting ? 'Saving...' : (isEditMode ? 'Update Vessel' : 'Create Vessel') }}
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { Vessel, VesselFormData } from '@/types/vessel.types';
import BaseModal from '@/components/shared/BaseModal.vue';
import BaseInput from '@/components/shared/BaseInput.vue';
import BaseSelect from '@/components/shared/BaseSelect.vue';
import BaseButton from '@/components/shared/BaseButton.vue';

// Props
interface Props {
  show: boolean;
  vessel?: Vessel | null;
  submitting?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  vessel: null,
  submitting: false,
});

// Emits
const emit = defineEmits<{
  close: [];
  submit: [data: VesselFormData];
}>();

// Computed
const isEditMode = computed(() => !!props.vessel);

// State
const formData = ref<VesselFormData>({
  id: '',
  name: '',
  type: '',
  class: '',
  dwt: 0,
  speed: 0,
  status: 'active',
  draft: undefined,
  loa: undefined,
  fuelConsumption: undefined,
  notes: undefined,
});

const errors = ref<Partial<Record<keyof VesselFormData, string>>>({});

// Options
const typeOptions = [
  { value: 'bulk_carrier', label: 'Bulk Carrier' },
  { value: 'tanker', label: 'Tanker' },
  { value: 'container', label: 'Container' },
  { value: 'general_cargo', label: 'General Cargo' },
  { value: 'ro_ro', label: 'Ro-Ro' },
];

const statusOptions = [
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'maintenance', label: 'Maintenance' },
];

// Computed
const isFormValid = computed(() => {
  return (
    formData.value.id &&
    formData.value.name &&
    formData.value.type &&
    formData.value.class &&
    formData.value.dwt > 0 &&
    formData.value.speed > 0 &&
    formData.value.status &&
    Object.keys(errors.value).length === 0
  );
});

// Watch for vessel changes
watch(
  () => props.vessel,
  (newVessel) => {
    if (newVessel) {
      formData.value = {
        id: newVessel.id,
        name: newVessel.name,
        type: newVessel.type,
        class: newVessel.class,
        dwt: newVessel.dwt,
        speed: newVessel.speed,
        status: newVessel.status,
        draft: newVessel.draft,
        loa: newVessel.loa,
        fuelConsumption: newVessel.fuelConsumption,
        notes: newVessel.notes,
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
    name: '',
    type: '',
    class: '',
    dwt: 0,
    speed: 0,
    status: 'active',
    draft: undefined,
    loa: undefined,
    fuelConsumption: undefined,
    notes: undefined,
  };
  errors.value = {};
}

function validateForm(): boolean {
  errors.value = {};
  let isValid = true;

  if (!formData.value.id) {
    errors.value.id = 'Vessel ID is required';
    isValid = false;
  }

  if (!formData.value.name) {
    errors.value.name = 'Vessel name is required';
    isValid = false;
  }

  if (!formData.value.type) {
    errors.value.type = 'Type is required';
    isValid = false;
  }

  if (!formData.value.class) {
    errors.value.class = 'Class is required';
    isValid = false;
  }

  if (formData.value.dwt <= 0) {
    errors.value.dwt = 'DWT must be greater than 0';
    isValid = false;
  }

  if (formData.value.speed <= 0) {
    errors.value.speed = 'Speed must be greater than 0';
    isValid = false;
  }

  return isValid;
}

function handleSubmit() {
  if (!validateForm()) {
    return;
  }

  const submitData: VesselFormData = { ...formData.value };
  
  // Remove undefined values for cleaner API calls
  Object.keys(submitData).forEach(key => {
    if (submitData[key as keyof VesselFormData] === undefined) {
      delete submitData[key as keyof VesselFormData];
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
.vessel-form {
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
