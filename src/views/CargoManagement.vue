<template>
  <div class="cargo-management">
    <div class="header">
      <div class="header-content">
        <h1>Cargo Management</h1>
        <p class="subtitle">Manage cargo commitments and templates.</p>
      </div>
      
      <div class="view-toggle">
        <button 
          class="toggle-btn" 
          :class="{ active: activeView === 'commitments' }"
          @click="activeView = 'commitments'"
        >
          Commitments
        </button>
        <button 
          class="toggle-btn" 
          :class="{ active: activeView === 'templates' }"
          @click="activeView = 'templates'"
        >
          Templates
        </button>
      </div>
    </div>

    <!-- Commitments View -->
    <div v-if="activeView === 'commitments'">
      <CargoList
        :cargo="cargoStore.cargoList"
        :loading="cargoStore.loading"
        @add-cargo="handleAddCargo"
        @edit-cargo="handleEditCargo"
        @delete-cargo="handleDeleteCargo"
        @view-cargo="handleViewCargo"
      />
    </div>

    <!-- Templates View -->
    <div v-else-if="activeView === 'templates'">
      <CargoTemplateList
        :templates="cargoStore.templates"
        :loading="cargoStore.loading"
        @create="handleCreateTemplate"
        @edit="handleEditTemplate"
        @delete="handleDeleteTemplate"
        @apply="handleApplyTemplate"
      />
    </div>

    <!-- Cargo Form Modal -->
    <CargoForm
      :show="showCargoModal"
      :cargo="selectedCargo"
      :submitting="cargoStore.loading"
      @close="closeCargoModal"
      @submit="handleCargoSubmit"
    />

    <!-- Template Form Modal -->
    <CargoTemplateForm
      :show="showTemplateModal"
      :template="selectedTemplate"
      :submitting="cargoStore.loading"
      @close="closeTemplateModal"
      @submit="handleTemplateSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useCargoStore } from '@/stores/cargo';
import CargoList from '@/components/cargo/CargoList.vue';
import CargoTemplateList from '@/components/cargo/CargoTemplateList.vue';
import CargoTemplateForm from '@/components/cargo/CargoTemplateForm.vue';
import CargoForm from '@/components/cargo/CargoForm.vue';
import type { CargoCommitment, CargoTemplate, CargoTemplateFormData, CargoFormData } from '@/types/cargo.types';

const cargoStore = useCargoStore();
const activeView = ref<'commitments' | 'templates'>('commitments');

// Cargo Modal State
const showCargoModal = ref(false);
const selectedCargo = ref<CargoCommitment | null>(null);

// Template Modal State
const showTemplateModal = ref(false);
const selectedTemplate = ref<CargoTemplate | null>(null);

onMounted(() => {
  loadData();
});

watch(activeView, () => {
  loadData();
});

function loadData() {
  if (activeView.value === 'commitments') {
    cargoStore.fetchCargo();
  } else {
    cargoStore.fetchTemplates();
  }
}

// Cargo Handlers
function handleAddCargo() {
  selectedCargo.value = null;
  showCargoModal.value = true;
}

function handleEditCargo(cargo: CargoCommitment) {
  selectedCargo.value = cargo;
  showCargoModal.value = true;
}

async function handleDeleteCargo(cargo: CargoCommitment) {
  if (confirm('Are you sure you want to delete this cargo commitment?')) {
    await cargoStore.deleteCargo(cargo.id);
  }
}

function handleViewCargo(cargo: CargoCommitment) {
  console.log('View cargo:', cargo);
}

async function handleCargoSubmit(data: CargoFormData) {
  let success = false;
  
  if (selectedCargo.value) {
    success = !!(await cargoStore.updateCargo(selectedCargo.value.id, data));
  } else {
    success = !!(await cargoStore.createCargo(data));
  }
  
  if (success) {
    closeCargoModal();
  }
}

function closeCargoModal() {
  showCargoModal.value = false;
  selectedCargo.value = null;
}

// Template Handlers
function handleCreateTemplate() {
  selectedTemplate.value = null;
  showTemplateModal.value = true;
}

function handleEditTemplate(template: CargoTemplate) {
  selectedTemplate.value = template;
  showTemplateModal.value = true;
}

async function handleDeleteTemplate(template: CargoTemplate) {
  if (confirm(`Are you sure you want to delete template "${template.name}"?`)) {
    await cargoStore.deleteTemplate(template.id);
  }
}

function handleApplyTemplate(template: CargoTemplate) {
  // Switch to commitments view and open add modal with template data
  activeView.value = 'commitments';
  
  // Create a partial cargo object from template
  const cargoFromTemplate: any = {
    commodity: template.commodity,
    quantity: template.quantity || 0,
    loadPort: template.loadPort || '',
    dischPort: template.dischPort || '',
    freightRate: template.freightRate,
    operationalCost: template.costAllocations?.operationalCost,
    overheadCost: template.costAllocations?.overheadCost,
    otherCost: template.costAllocations?.otherCost,
    status: 'Pending'
  };
  
  // We don't set ID so it's treated as new
  selectedCargo.value = cargoFromTemplate;
  showCargoModal.value = true;
}

async function handleTemplateSubmit(data: CargoTemplateFormData) {
  let success = false;
  
  if (selectedTemplate.value) {
    success = await cargoStore.updateTemplate(selectedTemplate.value.id, data);
  } else {
    success = await cargoStore.createTemplate(data);
  }
  
  if (success) {
    closeTemplateModal();
  }
}

function closeTemplateModal() {
  showTemplateModal.value = false;
  selectedTemplate.value = null;
}
</script>

<style scoped>
.cargo-management {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary, #111827);
  font-size: 1.875rem;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: var(--text-secondary, #6b7280);
  font-size: 1.1rem;
}

.view-toggle {
  display: flex;
  background: var(--bg-secondary, #f3f4f6);
  padding: 0.25rem;
  border-radius: 0.5rem;
}

.toggle-btn {
  padding: 0.5rem 1.5rem;
  border: none;
  background: transparent;
  color: var(--text-secondary, #6b7280);
  font-weight: 500;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: white;
  color: var(--primary-color, #2563eb);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.modal-placeholder {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  min-width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
}

.modal-actions button {
  padding: 0.5rem 1rem;
  background: var(--bg-secondary, #f3f4f6);
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 0.375rem;
  cursor: pointer;
}

@media (max-width: 640px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .view-toggle {
    width: 100%;
  }
  
  .toggle-btn {
    flex: 1;
  }
}
</style>