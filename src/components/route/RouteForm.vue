<template>
  <BaseModal
    :show="show"
    :title="isEditMode ? 'Edit Route' : 'Add Route'"
    @close="handleClose"
  >
    <form @submit.prevent="handleSubmit" class="route-form">
      <div class="form-row">
        <div class="form-group">
          <label for="route-from" class="form-label">
            From Port <span class="required">*</span>
          </label>
          <BaseInput
            id="route-from"
            v-model="formData.from"
            placeholder="Enter departure port..."
            required
            :error="errors.from"
          />
        </div>

        <div class="form-group">
          <label for="route-to" class="form-label">
            To Port <span class="required">*</span>
          </label>
          <BaseInput
            id="route-to"
            v-model="formData.to"
            placeholder="Enter arrival port..."
            required
            :error="errors.to"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="distance" class="form-label">
          Distance (nm) <span class="required">*</span>
        </label>
        <BaseInput
          id="distance"
          v-model.number="formData.distance"
          type="number"
          min="0"
          placeholder="Enter distance in nautical miles..."
          required
          :error="errors.distance"
        />
      </div>

      <div class="form-group">
        <label for="canal" class="form-label">
          Canal (Optional)
        </label>
        <BaseSelect
          id="canal"
          v-model="formData.canal"
          :options="canalOptions"
          placeholder="Select canal if applicable..."
        />
      </div>

      <div class="form-group">
        <label class="form-label">
          Waypoints
        </label>
        <div class="waypoints-list">
          <div
            v-for="(waypoint, index) in formData.waypoints"
            :key="index"
            class="waypoint-item"
          >
            <BaseInput
              v-model="formData.waypoints[index]"
              placeholder="Enter waypoint..."
            />
            <BaseButton
              @click="removeWaypoint(index)"
              variant="danger"
              size="small"
            >
              Remove
            </BaseButton>
          </div>
          <BaseButton
            @click="addWaypoint"
            variant="secondary"
            size="small"
            type="button"
          >
            + Add Waypoint
          </BaseButton>
        </div>
      </div>

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
          {{ submitting ? 'Saving...' : (isEditMode ? 'Update Route' : 'Create Route') }}
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { Route, RouteFormData } from '@/types/route.types';
import BaseModal from '@/components/shared/BaseModal.vue';
import BaseInput from '@/components/shared/BaseInput.vue';
import BaseSelect from '@/components/shared/BaseSelect.vue';
import BaseButton from '@/components/shared/BaseButton.vue';

interface Props {
  show: boolean;
  route?: Route | null;
  submitting?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  route: null,
  submitting: false,
});

const emit = defineEmits<{
  close: [];
  submit: [data: RouteFormData];
}>();

const isEditMode = computed(() => !!props.route);

const formData = ref<RouteFormData>({
  from: '',
  to: '',
  distance: 0,
  canal: undefined,
  waypoints: [],
  notes: undefined,
});

const errors = ref<Partial<Record<keyof RouteFormData, string>>>({});

const canalOptions = [
  { value: '', label: 'None' },
  { value: 'Suez', label: 'Suez Canal' },
  { value: 'Panama', label: 'Panama Canal' },
  { value: 'Kiel', label: 'Kiel Canal' },
  { value: 'Corinth', label: 'Corinth Canal' },
];

const isFormValid = computed(() => {
  return (
    formData.value.from &&
    formData.value.to &&
    formData.value.distance > 0 &&
    Object.keys(errors.value).length === 0
  );
});

watch(
  () => props.route,
  (newRoute) => {
    if (newRoute) {
      formData.value = {
        from: newRoute.from,
        to: newRoute.to,
        distance: newRoute.distance,
        canal: newRoute.canal,
        waypoints: newRoute.waypoints ? [...newRoute.waypoints] : [],
        notes: newRoute.notes,
      };
    } else {
      resetForm();
    }
    errors.value = {};
  },
  { immediate: true }
);

function resetForm() {
  formData.value = {
    from: '',
    to: '',
    distance: 0,
    canal: undefined,
    waypoints: [],
    notes: undefined,
  };
  errors.value = {};
}

function validateForm(): boolean {
  errors.value = {};
  let isValid = true;

  if (!formData.value.from) {
    errors.value.from = 'Departure port is required';
    isValid = false;
  }

  if (!formData.value.to) {
    errors.value.to = 'Arrival port is required';
    isValid = false;
  }

  if (formData.value.distance <= 0) {
    errors.value.distance = 'Distance must be greater than 0';
    isValid = false;
  }

  return isValid;
}

function addWaypoint() {
  if (!formData.value.waypoints) {
    formData.value.waypoints = [];
  }
  formData.value.waypoints.push('');
}

function removeWaypoint(index: number) {
  if (formData.value.waypoints) {
    formData.value.waypoints.splice(index, 1);
  }
}

function handleSubmit() {
  if (!validateForm()) {
    return;
  }

  const submitData: RouteFormData = { ...formData.value };
  
  // Clean up empty waypoints
  if (submitData.waypoints) {
    submitData.waypoints = submitData.waypoints.filter(w => w.trim() !== '');
    if (submitData.waypoints.length === 0) {
      delete submitData.waypoints;
    }
  }
  
  // Remove undefined values
  Object.keys(submitData).forEach(key => {
    if (submitData[key as keyof RouteFormData] === undefined) {
      delete submitData[key as keyof RouteFormData];
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
.route-form {
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

.waypoints-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.waypoint-item {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
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
