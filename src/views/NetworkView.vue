<template>
  <div class="network-view">
    <div class="header">
      <h1>Network Visualization</h1>
      <p class="subtitle">Interactive map of ports, plants, and transportation routes.</p>
    </div>

    <NetworkVisualization />
  </div>
</template>

<script setup lang="ts">
import NetworkVisualization from '@/components/network/NetworkVisualization.vue';
</script>

<style scoped>
.network-view {
  padding: 1.5rem;
  max-width: 100%;
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
