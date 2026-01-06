<template>
  <div class="schedule-config-form">
    <h3>Schedule Configuration</h3>

    <div class="form-group">
      <label for="year">Year</label>
      <input
        id="year"
        v-model.number="localConfig.year"
        type="number"
        min="2020"
        :max="maxYear"
        class="form-control"
        @input="emitUpdate"
      />
    </div>

    <div class="form-group">
      <label for="module">Module</label>
      <select
        id="module"
        v-model="localConfig.module"
        class="form-control"
        @change="emitUpdate"
      >
        <option value="deepsea">Deep Sea</option>
        <option value="olya">Olya</option>
        <option value="balakovo">Balakovo</option>
      </select>
    </div>

    <div class="form-group">
      <label>Vessels</label>
      <MultiSelect
        v-model="localConfig.vessels"
        :options="vesselOptions"
        placeholder="Select vessels..."
        @update:model-value="emitUpdate"
      />
      <small class="form-text">
        {{ localConfig.vessels.length }} vessel(s) selected
      </small>
    </div>

    <div class="form-group">
      <label for="goal">Optimization Goal</label>
      <select
        id="goal"
        v-model="localConfig.optimizationGoal"
        class="form-control"
        @change="emitUpdate"
      >
        <option value="maximize-revenue">Maximize Revenue</option>
        <option value="minimize-cost">Minimize Cost</option>
        <option value="balance-utilization">Balance Utilization</option>
      </select>
    </div>

    <div class="form-group">
      <label class="checkbox-label">
        <input
          v-model="localConfig.loadCargoCommitments"
          type="checkbox"
          @change="emitUpdate"
        />
        <span>Load Cargo Commitments</span>
      </label>
      <small class="form-text">
        Include existing cargo commitments in schedule generation
      </small>
    </div>

    <div class="form-group">
      <label class="checkbox-label">
        <input
          v-model="localConfig.useTemplates"
          type="checkbox"
          @change="emitUpdate"
        />
        <span>Use Voyage Templates</span>
      </label>
      <small class="form-text">
        Apply predefined voyage patterns to the schedule
      </small>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useVesselStore } from '@/stores/vessel';
import type { YearScheduleConfig } from '@/types/schedule.types';
import MultiSelect from '@/components/shared/MultiSelect.vue';

interface Props {
  config: YearScheduleConfig;
  loading?: boolean;
}

interface Emits {
  (e: 'update:config', config: YearScheduleConfig): void;
  (e: 'submit'): void;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<Emits>();

const vesselStore = useVesselStore();

// Local state
const localConfig = ref<YearScheduleConfig>({ ...props.config });

// Computed
const maxYear = computed(() => new Date().getFullYear() + 5);

const vesselOptions = computed(() => {
  return vesselStore.vessels.map(v => ({
    value: v.id,
    label: v.name,
  }));
});

// Methods
function emitUpdate() {
  emit('update:config', { ...localConfig.value });
}

// Watch for external config changes
watch(() => props.config, (newConfig) => {
  localConfig.value = { ...newConfig };
}, { deep: true });

// Lifecycle
onMounted(async () => {
  if (vesselStore.vessels.length === 0) {
    await vesselStore.fetchVessels();
  }
});
</script>

<style scoped>
.schedule-config-form {
  background: white;
  border-radius: 0.5rem;
  padding: 1.25rem;
  border: 1px solid var(--border-color, #e5e7eb);
}

.schedule-config-form h3 {
  margin: 0 0 1.25rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary, #111827);
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--text-primary, #111827);
}

.form-control {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
}

.checkbox-label input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.checkbox-label span {
  user-select: none;
}

.form-text {
  display: block;
  margin-top: 0.375rem;
  font-size: 0.75rem;
  color: var(--text-secondary, #6b7280);
  line-height: 1.4;
}
</style>
