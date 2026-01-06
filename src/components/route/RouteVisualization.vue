<template>
  <div class="route-visualization">
    <div v-if="loading" class="loading-state">
      <LoadingSpinner />
    </div>

    <div v-else-if="!route" class="empty-state">
      <p>No route data available</p>
    </div>

    <div v-else class="visualization-container">
      <!-- Route Header -->
      <div class="route-header">
        <h3 class="route-title">
          {{ route.from }} → {{ route.to }}
        </h3>
        <div class="route-metadata">
          <span class="metadata-item">
            <strong>Distance:</strong> {{ formatNumber(route.distance) }} nm
          </span>
          <span v-if="route.canal" class="metadata-item canal-badge">
            <strong>Canal:</strong> {{ route.canal }}
          </span>
        </div>
      </div>

      <!-- Visual Route Map -->
      <div class="route-map">
        <div class="port-marker start-port">
          <div class="port-icon"></div>
          <div class="port-label">{{ route.from }}</div>
        </div>

        <div class="route-path">
          <svg class="path-svg" viewBox="0 0 100 20" preserveAspectRatio="none">
            <path
              d="M 0 10 Q 25 5, 50 10 T 100 10"
              stroke="var(--primary-color, #2563eb)"
              stroke-width="2"
              fill="none"
              stroke-dasharray="5,5"
            />
          </svg>
          
          <!-- Waypoints -->
          <div v-if="route.waypoints && route.waypoints.length > 0" class="waypoints">
            <div
              v-for="(waypoint, index) in route.waypoints"
              :key="index"
              class="waypoint"
              :style="{ left: `${((index + 1) / (route.waypoints.length + 1)) * 100}%` }"
            >
              <div class="waypoint-marker">
                <span class="waypoint-icon"></span>
              </div>
              <div class="waypoint-label">{{ waypoint }}</div>
            </div>
          </div>

          <!-- Canal Marker -->
          <div v-if="route.canal" class="canal-marker">
            <div class="canal-icon"></div>
            <div class="canal-label">{{ route.canal }} Canal</div>
          </div>
        </div>

        <div class="port-marker end-port">
          <div class="port-icon"></div>
          <div class="port-label">{{ route.to }}</div>
        </div>
      </div>

      <!-- Route Statistics -->
      <div class="route-stats">
        <div class="stat-card">
          <div class="stat-value">{{ formatNumber(route.distance) }}</div>
          <div class="stat-label">Nautical Miles</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-value">{{ estimateTime(route.distance, 15) }}</div>
          <div class="stat-label">Est. Time @ 15kn</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-value">{{ estimateTime(route.distance, 12) }}</div>
          <div class="stat-label">Est. Time @ 12kn</div>
        </div>
        
        <div class="stat-card" v-if="route.waypoints">
          <div class="stat-value">{{ route.waypoints.length }}</div>
          <div class="stat-label">Waypoints</div>
        </div>
      </div>

      <!-- Route Legs Breakdown -->
      <div v-if="showDetails" class="route-details">
        <h4 class="details-title">Route Details</h4>
        <div class="details-grid">
          <div class="detail-item">
            <span class="detail-label">Departure Port:</span>
            <span class="detail-value">{{ route.from }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Arrival Port:</span>
            <span class="detail-value">{{ route.to }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Total Distance:</span>
            <span class="detail-value">{{ formatNumber(route.distance) }} nm</span>
          </div>
          <div class="detail-item" v-if="route.canal">
            <span class="detail-label">Canal Transit:</span>
            <span class="detail-value">{{ route.canal }} Canal</span>
          </div>
          <div class="detail-item" v-if="route.notes">
            <span class="detail-label">Notes:</span>
            <span class="detail-value">{{ route.notes }}</span>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="route-actions">
        <BaseButton
          @click="showDetails = !showDetails"
          variant="secondary"
          size="small"
        >
          {{ showDetails ? 'Hide Details' : 'Show Details' }}
        </BaseButton>
        <BaseButton
          @click="$emit('transfer-to-builder', route)"
          variant="primary"
        >
          Transfer to Voyage Builder
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { Route } from '@/types/route.types';
import BaseButton from '@/components/shared/BaseButton.vue';
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue';

interface Props {
  route: Route | null;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  'transfer-to-builder': [route: Route];
}>();

const showDetails = ref(false);

function formatNumber(value: number): string {
  return value.toLocaleString();
}

function estimateTime(distance: number, speed: number): string {
  const hours = distance / speed;
  const days = Math.floor(hours / 24);
  const remainingHours = Math.round(hours % 24);
  
  if (days > 0) {
    return `${days}d ${remainingHours}h`;
  }
  return `${remainingHours}h`;
}
</script>

<style scoped>
.route-visualization {
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  border: 1px solid var(--border-color, #e5e7eb);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted, #6b7280);
}

.visualization-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.route-header {
  text-align: center;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--border-color, #e5e7eb);
}

.route-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: var(--text-primary, #1f2937);
}

.route-metadata {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

.metadata-item {
  font-size: 0.95rem;
  color: var(--text-secondary, #4b5563);
}

.canal-badge {
  padding: 0.35rem 0.85rem;
  background: var(--bg-tertiary, #f0f9ff);
  border-radius: 12px;
  color: var(--primary-color, #2563eb);
  font-weight: 500;
}

.route-map {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  background: var(--bg-tertiary, #f9fafb);
  border-radius: 8px;
  position: relative;
}

.port-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 80px;
}

.port-icon {
  font-size: 2rem;
}

.port-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-primary, #1f2937);
  text-align: center;
}

.route-path {
  flex: 1;
  height: 80px;
  position: relative;
}

.path-svg {
  width: 100%;
  height: 100%;
}

.waypoints {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.waypoint {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.waypoint-marker {
  width: 28px;
  height: 28px;
  background: white;
  border: 2px solid var(--primary-color, #2563eb);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.waypoint-icon {
  font-size: 1rem;
}

.waypoint-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary, #4b5563);
  white-space: nowrap;
}

.canal-marker {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -120%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.canal-icon {
  font-size: 1.5rem;
}

.canal-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary-color, #2563eb);
  background: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  white-space: nowrap;
}

.route-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-card {
  text-align: center;
  padding: 1.5rem;
  background: var(--bg-tertiary, #f9fafb);
  border-radius: 8px;
  border: 1px solid var(--border-color, #e5e7eb);
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary-color, #2563eb);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted, #6b7280);
}

.route-details {
  padding: 1.5rem;
  background: var(--bg-tertiary, #f9fafb);
  border-radius: 8px;
}

.details-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: var(--text-primary, #1f2937);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.875rem;
  color: var(--text-muted, #6b7280);
  font-weight: 500;
}

.detail-value {
  font-size: 1rem;
  color: var(--text-primary, #1f2937);
}

.route-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color, #e5e7eb);
}

@media (max-width: 768px) {
  .route-map {
    flex-direction: column;
  }

  .route-path {
    width: 100%;
    height: 150px;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .route-actions {
    flex-direction: column;
  }
}
</style>
