<template>
  <div class="home">
    <h1>Welcome to Vessel Scheduler</h1>
    <p class="subtitle">Vessel Scheduling and Voyage Planning System</p>
    
    <div class="features">
      <div class="feature-card">
        <h3> Dashboard</h3>
        <p>View your vessel schedules and voyage planning at a glance</p>
        <router-link to="/dashboard" class="btn">Go to Dashboard</router-link>
      </div>
      
      <div class="feature-card">
        <h3> Vessel Management</h3>
        <p>Manage your fleet and track vessel positions</p>
      </div>
      
      <div class="feature-card">
        <h3> Route Planning</h3>
        <p>Optimize routes and calculate voyage durations</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component logic will go here
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.2rem;
  color: #64748b;
  margin-bottom: 3rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.feature-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.feature-card p {
  color: #64748b;
  line-height: 1.6;
}

.btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #42b983;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #359268;
}
</style>
