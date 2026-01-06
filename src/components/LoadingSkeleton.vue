<template>
  <div class="loading-skeleton" :class="skeletonClass">
    <!-- Card skeleton -->
    <div v-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-header">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-title-group">
          <div class="skeleton-title"></div>
          <div class="skeleton-subtitle"></div>
        </div>
      </div>
      <div class="skeleton-content">
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line" style="width: 80%;"></div>
      </div>
    </div>

    <!-- Table skeleton -->
    <div v-else-if="type === 'table'" class="skeleton-table">
      <div class="skeleton-table-header">
        <div class="skeleton-cell" v-for="i in columns" :key="`header-${i}`"></div>
      </div>
      <div class="skeleton-table-row" v-for="row in rows" :key="`row-${row}`">
        <div class="skeleton-cell" v-for="col in columns" :key="`cell-${row}-${col}`"></div>
      </div>
    </div>

    <!-- List skeleton -->
    <div v-else-if="type === 'list'" class="skeleton-list">
      <div class="skeleton-list-item" v-for="i in items" :key="`item-${i}`">
        <div class="skeleton-icon"></div>
        <div class="skeleton-text-group">
          <div class="skeleton-text"></div>
          <div class="skeleton-text-small"></div>
        </div>
      </div>
    </div>

    <!-- Gantt chart skeleton -->
    <div v-else-if="type === 'gantt'" class="skeleton-gantt">
      <div class="skeleton-gantt-header"></div>
      <div class="skeleton-gantt-body">
        <div class="skeleton-gantt-row" v-for="i in rows" :key="`gantt-${i}`">
          <div class="skeleton-gantt-label"></div>
          <div class="skeleton-gantt-bar" :style="{ width: `${Math.random() * 60 + 20}%`, marginLeft: `${Math.random() * 20}%` }"></div>
        </div>
      </div>
    </div>

    <!-- Network/Graph skeleton -->
    <div v-else-if="type === 'network'" class="skeleton-network">
      <svg width="100%" height="400">
        <circle v-for="i in 5" :key="`node-${i}`" 
                :cx="Math.random() * 80 + 10 + '%'" 
                :cy="Math.random() * 80 + 10 + '%'" 
                r="30" 
                class="skeleton-node" />
        <line v-for="i in 4" :key="`edge-${i}`"
              :x1="Math.random() * 80 + 10 + '%'"
              :y1="Math.random() * 80 + 10 + '%'"
              :x2="Math.random() * 80 + 10 + '%'"
              :y2="Math.random() * 80 + 10 + '%'"
              class="skeleton-edge" />
      </svg>
    </div>

    <!-- Calendar skeleton -->
    <div v-else-if="type === 'calendar'" class="skeleton-calendar">
      <div class="skeleton-calendar-header">
        <div class="skeleton-month"></div>
        <div class="skeleton-nav"></div>
      </div>
      <div class="skeleton-calendar-grid">
        <div class="skeleton-day-header" v-for="i in 7" :key="`day-${i}`"></div>
        <div class="skeleton-day" v-for="i in 35" :key="`date-${i}`"></div>
      </div>
    </div>

    <!-- Generic skeleton (default) -->
    <div v-else class="skeleton-generic">
      <div class="skeleton-line"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line" style="width: 60%;"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  type?: 'card' | 'table' | 'list' | 'gantt' | 'network' | 'calendar' | 'generic';
  rows?: number;
  columns?: number;
  items?: number;
  animated?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'generic',
  rows: 5,
  columns: 4,
  items: 3,
  animated: true,
});

const skeletonClass = computed(() => ({
  'skeleton-animated': props.animated,
}));
</script>

<style scoped>
.loading-skeleton {
  width: 100%;
  padding: 1rem;
}

/* Animation */
.skeleton-animated .skeleton-line,
.skeleton-animated .skeleton-title,
.skeleton-animated .skeleton-subtitle,
.skeleton-animated .skeleton-text,
.skeleton-animated .skeleton-text-small,
.skeleton-animated .skeleton-cell,
.skeleton-animated .skeleton-icon,
.skeleton-animated .skeleton-avatar,
.skeleton-animated .skeleton-gantt-label,
.skeleton-animated .skeleton-gantt-bar,
.skeleton-animated .skeleton-node,
.skeleton-animated .skeleton-edge,
.skeleton-animated .skeleton-month,
.skeleton-animated .skeleton-nav,
.skeleton-animated .skeleton-day-header,
.skeleton-animated .skeleton-day {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

/* Base skeleton styles */
.skeleton-line,
.skeleton-title,
.skeleton-subtitle,
.skeleton-text,
.skeleton-text-small,
.skeleton-cell,
.skeleton-gantt-label,
.skeleton-gantt-bar,
.skeleton-month,
.skeleton-nav,
.skeleton-day-header,
.skeleton-day {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 4px;
}

.skeleton-icon,
.skeleton-avatar {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 50%;
}

/* Card skeleton */
.skeleton-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}

.skeleton-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  margin-right: 1rem;
}

.skeleton-title-group {
  flex: 1;
}

.skeleton-title {
  height: 20px;
  width: 60%;
  margin-bottom: 0.5rem;
}

.skeleton-subtitle {
  height: 16px;
  width: 40%;
}

.skeleton-content {
  margin-top: 1rem;
}

.skeleton-line {
  height: 16px;
  margin-bottom: 0.75rem;
}

/* Table skeleton */
.skeleton-table {
  width: 100%;
}

.skeleton-table-header {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e0e0e0;
}

.skeleton-table-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.skeleton-cell {
  height: 20px;
}

/* List skeleton */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
}

.skeleton-icon {
  width: 40px;
  height: 40px;
  margin-right: 1rem;
}

.skeleton-text-group {
  flex: 1;
}

.skeleton-text {
  height: 18px;
  width: 70%;
  margin-bottom: 0.5rem;
}

.skeleton-text-small {
  height: 14px;
  width: 50%;
}

/* Gantt skeleton */
.skeleton-gantt {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.skeleton-gantt-header {
  height: 40px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  border-bottom: 2px solid #d0d0d0;
}

.skeleton-gantt-body {
  padding: 1rem;
}

.skeleton-gantt-row {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.skeleton-gantt-label {
  width: 120px;
  height: 24px;
  margin-right: 1rem;
}

.skeleton-gantt-bar {
  height: 24px;
  flex: 1;
  max-width: 80%;
}

/* Network skeleton */
.skeleton-network {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}

.skeleton-node {
  fill: #f0f0f0;
  stroke: #e0e0e0;
  stroke-width: 2;
}

.skeleton-edge {
  stroke: #e0e0e0;
  stroke-width: 2;
}

/* Calendar skeleton */
.skeleton-calendar {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
}

.skeleton-calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.skeleton-month {
  height: 24px;
  width: 120px;
}

.skeleton-nav {
  height: 24px;
  width: 80px;
}

.skeleton-calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
}

.skeleton-day-header {
  height: 20px;
}

.skeleton-day {
  height: 40px;
}

/* Generic skeleton */
.skeleton-generic {
  padding: 1rem;
}
</style>
