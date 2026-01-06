<template>
  <div class="year-schedule-generator">
    <div class="page-header">
      <h1>Year Schedule Generator</h1>
      <p class="subtitle">Plan and optimize annual vessel schedules</p>
    </div>

    <div class="generator-layout">
      <!-- Configuration Panel -->
      <aside class="config-panel">
        <ScheduleConfigForm
          v-model:config="scheduleConfig"
          :loading="scheduleStore.generating"
          @submit="handleGenerateSchedule"
        />
        
        <TemplateSelector
          v-if="scheduleConfig.useTemplates"
          v-model:selected="scheduleConfig.selectedTemplateIds"
          :module="scheduleConfig.module"
          :templates="scheduleStore.templates"
          @load-templates="loadTemplates"
        />

        <div class="action-buttons">
          <button
            class="btn btn-primary"
            :disabled="!canGenerate || scheduleStore.generating"
            @click="handleGenerateSchedule"
          >
            <i class="icon-wand"></i>
            {{ scheduleStore.generating ? 'Generating...' : 'Generate Schedule' }}
          </button>

          <button
            v-if="currentSchedule"
            class="btn btn-secondary"
            @click="handleSaveScenario"
          >
            <i class="icon-save"></i>
            Save Scenario
          </button>

          <button
            v-if="currentSchedule"
            class="btn btn-secondary"
            @click="handleExportPDF"
          >
            <i class="icon-pdf"></i>
            Export PDF
          </button>

          <button
            v-if="currentSchedule"
            class="btn btn-secondary"
            @click="handleExportExcel"
          >
            <i class="icon-excel"></i>
            Export Excel
          </button>
        </div>
      </aside>

      <!-- Main Content Area -->
      <main class="content-panel">
        <div v-if="scheduleStore.loading" class="loading-state">
          <LoadingSpinner size="large" />
          <p>Loading schedule data...</p>
        </div>

        <div v-else-if="scheduleStore.error" class="error-state">
          <i class="icon-alert-circle"></i>
          <p>{{ scheduleStore.error }}</p>
          <button class="btn btn-primary" @click="scheduleStore.clearError">
            Dismiss
          </button>
        </div>

        <div v-else-if="!currentSchedule" class="empty-state">
          <i class="icon-calendar"></i>
          <h3>No Schedule Generated</h3>
          <p>Configure your schedule parameters and click "Generate Schedule" to begin.</p>
        </div>

        <div v-else class="schedule-content">
          <!-- Schedule Statistics -->
          <div class="statistics-panel">
            <div class="stat-card">
              <span class="stat-label">Total Voyages</span>
              <span class="stat-value">{{ currentSchedule.statistics.totalVoyages }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">Total Cargo (t)</span>
              <span class="stat-value">{{ formatNumber(currentSchedule.statistics.totalCargo) }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">Total Revenue</span>
              <span class="stat-value">${{ formatNumber(currentSchedule.statistics.totalRevenue) }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">Net Profit</span>
              <span class="stat-value">${{ formatNumber(currentSchedule.statistics.netProfit) }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">Avg Utilization</span>
              <span class="stat-value">{{ currentSchedule.statistics.averageUtilization.toFixed(1) }}%</span>
            </div>
          </div>

          <!-- Conflict Detector -->
          <ConflictDetector
            :conflicts="currentSchedule.conflicts"
            :schedule-id="currentSchedule.id"
            @resolve="handleResolveConflict"
          />

          <!-- Resource Allocation Grid -->
          <ResourceAllocationGrid
            :allocations="currentSchedule.monthlyAllocations"
            :year="currentSchedule.config.year"
            @adjust="handleManualAdjustment"
            @edit-voyage="handleEditVoyage"
          />

          <!-- Manual Adjustment Controls -->
          <div class="manual-controls">
            <h3>Manual Adjustments</h3>
            <div class="control-group">
              <label>Add Voyage to Month:</label>
              <select v-model="manualAdjustment.month">
                <option v-for="m in 12" :key="m" :value="m">
                  {{ getMonthName(m) }}
                </option>
              </select>
              <select v-model="manualAdjustment.vesselId">
                <option value="">Select Vessel</option>
                <option
                  v-for="vessel in availableVessels"
                  :key="vessel.id"
                  :value="vessel.id"
                >
                  {{ vessel.name }}
                </option>
              </select>
              <button
                class="btn btn-small"
                :disabled="!canAddVoyage"
                @click="handleAddVoyage"
              >
                Add Voyage
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Edit Voyage Modal (Integration with Voyage Builder) -->
    <BaseModal
      v-if="editingVoyage"
      :show="editingVoyage !== null"
      title="Edit Voyage"
      size="large"
      @close="editingVoyage = null"
    >
      <div class="voyage-editor">
        <p>Editing voyage: {{ editingVoyage.id }}</p>
        <button class="btn btn-primary" @click="openVoyageBuilder">
          Open in Voyage Builder
        </button>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="editingVoyage = null">
            Close
          </button>
        </div>
      </div>
    </BaseModal>

    <!-- Save Scenario Modal -->
    <BaseModal
      v-if="showSaveModal"
      :show="showSaveModal"
      title="Save Schedule Scenario"
      @close="showSaveModal = false"
    >
      <div class="save-scenario-form">
        <label>
          Scenario Name:
          <input
            v-model="scenarioName"
            type="text"
            placeholder="e.g., 2025 Optimized Plan"
            class="input-field"
          />
        </label>
        <label>
          Description (optional):
          <textarea
            v-model="scenarioDescription"
            placeholder="Add notes about this scenario..."
            class="input-field"
            rows="3"
          ></textarea>
        </label>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showSaveModal = false">
            Cancel
          </button>
          <button
            class="btn btn-primary"
            :disabled="!scenarioName.trim()"
            @click="saveScenario"
          >
            Save
          </button>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useScheduleStore } from '@/stores/schedule';
import { useVesselStore } from '@/stores/vessel';
import type { YearScheduleConfig, YearSchedule } from '@/types/schedule.types';
import ScheduleConfigForm from '@/components/schedule/ScheduleConfigForm.vue';
import ResourceAllocationGrid from '@/components/schedule/ResourceAllocationGrid.vue';
import ConflictDetector from '@/components/schedule/ConflictDetector.vue';
import TemplateSelector from '@/components/schedule/TemplateSelector.vue';
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue';
import BaseModal from '@/components/shared/BaseModal.vue';

const router = useRouter();
const scheduleStore = useScheduleStore();
const vesselStore = useVesselStore();

// State
const scheduleConfig = ref<YearScheduleConfig>({
  year: new Date().getFullYear(),
  module: 'deepsea',
  vessels: [],
  optimizationGoal: 'maximize-revenue',
  loadCargoCommitments: true,
  useTemplates: false,
  selectedTemplateIds: [],
});

const manualAdjustment = ref({
  month: 1,
  vesselId: '',
});

const editingVoyage = ref<any>(null);
const showSaveModal = ref(false);
const scenarioName = ref('');
const scenarioDescription = ref('');

// Computed
const currentSchedule = computed(() => scheduleStore.currentSchedule);

const canGenerate = computed(() => {
  return scheduleConfig.value.vessels.length > 0 && scheduleConfig.value.year > 0;
});

const availableVessels = computed(() => {
  return vesselStore.vessels.filter(v => 
    scheduleConfig.value.vessels.includes(v.id)
  );
});

const canAddVoyage = computed(() => {
  return manualAdjustment.value.vesselId && manualAdjustment.value.month;
});

// Methods
async function handleGenerateSchedule() {
  await scheduleStore.generateSchedule(scheduleConfig.value);
}

async function loadTemplates() {
  await scheduleStore.fetchTemplates(scheduleConfig.value.module);
}

function handleManualAdjustment(data: any) {
  console.log('Manual adjustment:', data);
  // Update schedule with manual changes
  if (currentSchedule.value) {
    scheduleStore.updateSchedule(currentSchedule.value.id, data);
  }
}

function handleEditVoyage(voyageData: any) {
  editingVoyage.value = voyageData;
}

function openVoyageBuilder() {
  if (editingVoyage.value) {
    router.push({
      name: 'voyage-builder',
      query: { voyageId: editingVoyage.value.id }
    });
  }
}

async function handleResolveConflict(conflictId: string, resolution: string) {
  if (currentSchedule.value) {
    await scheduleStore.resolveConflict(
      currentSchedule.value.id,
      conflictId,
      resolution
    );
  }
}

function handleAddVoyage() {
  console.log('Adding voyage:', manualAdjustment.value);
  // Implement voyage addition logic
}

function handleSaveScenario() {
  showSaveModal.value = true;
  if (currentSchedule.value) {
    scenarioName.value = currentSchedule.value.name || '';
  }
}

async function saveScenario() {
  if (currentSchedule.value && scenarioName.value.trim()) {
    await scheduleStore.updateSchedule(currentSchedule.value.id, {
      name: scenarioName.value,
      status: 'finalized',
    });
    showSaveModal.value = false;
  }
}

async function handleExportPDF() {
  if (!currentSchedule.value) return;
  
  try {
    const response = await fetch(`/api/schedules/${currentSchedule.value.id}/export/pdf`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `schedule-${currentSchedule.value.config.year}.pdf`;
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Export PDF failed:', error);
  }
}

async function handleExportExcel() {
  if (!currentSchedule.value) return;
  
  try {
    const response = await fetch(`/api/schedules/${currentSchedule.value.id}/export/excel`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `schedule-${currentSchedule.value.config.year}.xlsx`;
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Export Excel failed:', error);
  }
}

function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num);
}

function getMonthName(month: number): string {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  return months[month - 1];
}

// Lifecycle
onMounted(async () => {
  await vesselStore.fetchVessels();
});
</script>

<style scoped>
.year-schedule-generator {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.page-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
}

.subtitle {
  margin: 0;
  color: var(--text-secondary, #6b7280);
}

.generator-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 0;
  overflow: hidden;
}

.config-panel {
  background: var(--bg-secondary, #f9fafb);
  border-right: 1px solid var(--border-color, #e5e7eb);
  padding: 1.5rem;
  overflow-y: auto;
}

.action-buttons {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.content-panel {
  overflow-y: auto;
  padding: 1.5rem;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  color: var(--text-secondary, #6b7280);
}

.error-state {
  color: var(--error-color, #dc2626);
}

.error-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.3;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary, #111827);
}

.schedule-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.statistics-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary, #6b7280);
  font-weight: 500;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #111827);
}

.manual-controls {
  background: white;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.manual-controls h3 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
}

.control-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.control-group label {
  font-weight: 500;
  margin-right: 0.5rem;
}

.control-group select {
  padding: 0.5rem;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.375rem;
  min-width: 150px;
}

.btn {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color, #3b82f6);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover, #2563eb);
}

.btn-secondary {
  background: white;
  color: var(--text-primary, #111827);
  border: 1px solid var(--border-color, #e5e7eb);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-secondary, #f9fafb);
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.voyage-editor,
.save-scenario-form {
  padding: 1rem;
}

.input-field {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.375rem;
  margin-top: 0.25rem;
}

.save-scenario-form label {
  display: block;
  margin-bottom: 1rem;
  font-weight: 500;
}

.modal-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
</style>
