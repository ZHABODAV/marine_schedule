<template>
  <div class="about">
    <h1>About Vessel Scheduler</h1>
    
    <div class="login-section" v-if="$route.name === 'Login'">
      <p>Please login to access the application.</p>
      <button @click="handleLogin" class="login-btn">Login</button>
    </div>

    <div class="content">
      <section>
        <h2>Overview</h2>
        <p>
          Vessel Scheduler is a comprehensive vessel scheduling and voyage planning system
          designed to optimize maritime operations, route planning, and fleet management.
        </p>
      </section>
      
      <section>
        <h2>Features</h2>
        <ul>
          <li>Real-time vessel tracking and management</li>
          <li>Optimized route planning and voyage calculations</li>
          <li>Berth utilization and capacity planning</li>
          <li>Financial analysis and cost optimization</li>
          <li>Gantt chart visualizations</li>
          <li>Comprehensive reporting and analytics</li>
        </ul>
      </section>
      
      <section>
        <h2>Technology Stack</h2>
        <ul>
          <li>Vue 3 with Composition API</li>
          <li>TypeScript for type safety</li>
          <li>Pinia for state management</li>
          <li>Vue Router for navigation</li>
          <li>Vite for fast development</li>
          <li>Python backend with Flask</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const handleLogin = () => {
  localStorage.setItem('isAuthenticated', 'true');
  const redirect = route.query.redirect as string || '/';
  router.push(redirect);
};
</script>

<style scoped>
.about {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.content {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

section {
  margin-bottom: 2rem;
}

section:last-child {
  margin-bottom: 0;
}

h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

p {
  color: #64748b;
  line-height: 1.6;
}

ul {
  color: #64748b;
  line-height: 1.8;
}

li {
  margin-bottom: 0.5rem;
}

.login-section {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.login-btn {
  background-color: #3b82f6;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-btn:hover {
  background-color: #2563eb;
}
</style>
