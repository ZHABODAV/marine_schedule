<template>
  <div class="route-management">
    <div class="header">
      <h1>Route Management</h1>
      <p class="subtitle">Manage shipping routes, distances, and canal transits.</p>
    </div>

    <RouteList
      :routes="routeStore.routes"
      :loading="routeStore.loading"
      :selectable="true"
      @add-route="handleAddRoute"
      @view-route="handleViewRoute"
      @delete-route="handleDeleteRoute"
      @transfer-to-builder="handleTransferToBuilder"
      @transfer-selected="handleTransferSelected"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouteStore } from '@/stores/route';
import RouteList from '@/components/route/RouteList.vue';
import type { Route } from '@/types/route.types';
import { useRouter } from 'vue-router';

const routeStore = useRouteStore();
const router = useRouter();

onMounted(() => {
  routeStore.fetchRoutes();
});

function handleAddRoute() {
  console.log('Add route clicked');
  alert('Add Route functionality to be implemented with RouteForm component');
}

function handleViewRoute(route: Route) {
  console.log('View route:', route);
  // Navigate to detail view or show modal
}

function handleDeleteRoute(route: Route) {
  routeStore.deleteRoute(route.id);
}

function handleTransferToBuilder(route: Route) {
  console.log('Transfer to builder:', route);
  // Logic to transfer route to voyage builder
  router.push({ name: 'voyage-builder', query: { routeId: route.id } });
}

function handleTransferSelected(routes: Route[]) {
  console.log('Transfer selected routes:', routes);
  // Logic to transfer multiple routes
  alert(`Transferring ${routes.length} routes to builder`);
}
</script>

<style scoped>
.route-management {
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
