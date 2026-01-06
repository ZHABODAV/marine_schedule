<template>
  <div class="financial-view">
    <div class="header">
      <h1>Financial Analysis</h1>
      <p class="subtitle">Analyze costs, revenue, and profitability of voyages.</p>
    </div>

    <FinancialAnalysis />
  </div>
</template>

<script setup lang="ts">
import FinancialAnalysis from '@/components/financial/FinancialAnalysis.vue';
</script>

<style scoped>
.financial-view {
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
