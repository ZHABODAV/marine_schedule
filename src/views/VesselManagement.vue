<template>
  <div class="vessel-management">
    <div class="header">
      <h1>Vessel Management</h1>
      <p class="subtitle">Manage fleet, track vessel status and specifications.</p>
    </div>

    <VesselList
      :vessels="vesselStore.vessels"
      :loading="vesselStore.loading"
      @add-vessel="handleAddVessel"
      @edit-vessel="handleEditVessel"
      @delete-vessel="handleDeleteVessel"
      @view-vessel="handleViewVessel"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useVesselStore } from '@/stores/vessel';
import VesselList from '@/components/vessel/VesselList.vue';
import type { Vessel } from '@/types/vessel.types';

const vesselStore = useVesselStore();

onMounted(() => {
  vesselStore.fetchVessels();
});

function handleAddVessel() {
  console.log('Add vessel clicked');
  alert('Add Vessel functionality to be implemented with VesselForm component');
}

function handleEditVessel(vessel: Vessel) {
  console.log('Edit vessel:', vessel);
  alert(`Edit Vessel ${vessel.name} functionality to be implemented`);
}

function handleDeleteVessel(vessel: Vessel) {
  vesselStore.deleteVessel(vessel.id);
}

function handleViewVessel(vessel: Vessel) {
  console.log('View vessel:', vessel);
}
</script>

<style scoped>
.vessel-management {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

h1 {
  margin-bottom: 0.5rem;
  color: var(--text-primary, #111827);
  font-size: 1.875rem;
  font-weight: 600;
}

.subtitle {
  color: var(--text-secondary, #6b7280);
  font-size: 1.1rem;
}
</style>
