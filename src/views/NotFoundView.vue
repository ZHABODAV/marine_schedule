<template>
  <div class="not-found">
    <h1>404</h1>
    <h2>Page Not Found</h2>
    <p>The page you're looking for doesn't exist.</p>
    <router-link to="/" class="btn">Go Home</router-link>
  </div>
</template>

<script setup lang="ts">
// Component logic
</script>

<style scoped>
.not-found {
  text-align: center;
  padding: 4rem 2rem;
}

h1 {
  font-size: 6rem;
  color: #e74c3c;
  margin: 0;
}

h2 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 1rem 0;
}

p {
  color: #64748b;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
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
