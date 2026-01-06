<template>
  <div class="gantt-view">
    <div class="header">
      <h1>Gantt Chart</h1>
      <p class="subtitle">Visualize vessel schedules and operations timeline.</p>
    </div>

    <GanttChart />
  </div>
</template>

<script setup lang="ts">
import GanttChart from '@/components/gantt/GanttChart.vue';
</script>

<style scoped>
.gantt-view {
  padding: 1.5rem;
  max-width: 100%; /* Gantt charts often need full width */
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
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
