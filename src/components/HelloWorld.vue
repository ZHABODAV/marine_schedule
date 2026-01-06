<template>
  <div class="hello-world">
    <h2>{{ msg }}</h2>
    <p>You've successfully set up a Vue 3 application!</p>
    <button @click="increment" class="btn btn-primary">
      Count is: {{ count }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  msg: string
}>()

const count = ref(0)

function increment() {
  count.value++
}
</script>

<style scoped>
.hello-world {
  padding: 2rem;
  text-align: center;
}

h2 {
  color: #42b983;
  margin-bottom: 1rem;
}

p {
  margin-bottom: 1.5rem;
  color: #64748b;
}

button {
  margin-top: 1rem;
}
</style>
