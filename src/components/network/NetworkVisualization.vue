<template>
  <div class="network-container">
    <div class="network-controls">
      <div class="control-group">
        <label>
          <input v-model="showPorts" type="checkbox" />
          Show Ports
        </label>
        <label>
          <input v-model="showPlants" type="checkbox" />
          Show Plants
        </label>
        <label>
          <input v-model="showSeaRoutes" type="checkbox" />
          Sea Routes
        </label>
        <label>
          <input v-model="showRailRoutes" type="checkbox" />
          Rail Routes
        </label>
      </div>

      <div class="button-group">
        <button @click="refreshNetwork" class="btn btn-primary">
          <span v-if="isLoading">Loading...</span>
          <span v-else>Refresh</span>
        </button>
        <button @click="exportNetwork" class="btn btn-secondary">
          Export Data
        </button>
        <button @click="resetView" class="btn btn-secondary">
          Reset View
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>

    <div v-if="isLoading" class="loading-state">
      <LoadingSpinner />
      <p>Building network visualization...</p>
    </div>

    <div
      v-show="!isLoading"
      ref="networkContainer"
      class="network-graph"
    ></div>

    <div v-if="networkStats" class="network-stats">
      <div class="stat-card">
        <h4>Total Nodes</h4>
        <p class="stat-value">{{ networkStats.totalNodes }}</p>
      </div>
      <div class="stat-card">
        <h4>Ports</h4>
        <p class="stat-value">{{ networkStats.ports }}</p>
      </div>
      <div class="stat-card">
        <h4>Plants</h4>
        <p class="stat-value">{{ networkStats.plants }}</p>
      </div>
      <div class="stat-card">
        <h4>Total Connections</h4>
        <p class="stat-value">{{ networkStats.totalEdges }}</p>
      </div>
      <div class="stat-card">
        <h4>Sea Routes</h4>
        <p class="stat-value">{{ networkStats.seaRoutes }}</p>
      </div>
      <div class="stat-card">
        <h4>Rail Routes</h4>
        <p class="stat-value">{{ networkStats.railRoutes }}</p>
      </div>
    </div>

    <div class="network-legend">
      <h4>Legend</h4>
      <div class="legend-items">
        <div class="legend-item">
          <div class="legend-node port-node"></div>
          <span>Port</span>
        </div>
        <div class="legend-item">
          <div class="legend-node plant-node"></div>
          <span>Plant/Station</span>
        </div>
        <div class="legend-item">
          <div class="legend-line sea-route"></div>
          <span>Sea Route</span>
        </div>
        <div class="legend-item">
          <div class="legend-line rail-route"></div>
          <span>Rail Route</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { Network, DataSet } from 'vis-network/standalone'
import type { Node, Edge, Options } from 'vis-network/standalone'
import { useRouteStore } from '@/stores/route'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import { exportNetworkSnapshot } from '@/services/network.service'

interface NetworkStats {
  totalNodes: number
  ports: number
  plants: number
  totalEdges: number
  seaRoutes: number
  railRoutes: number
}

const routeStore = useRouteStore()

const networkContainer = ref<HTMLElement | null>(null)
const showPorts = ref(true)
const showPlants = ref(true)
const showSeaRoutes = ref(true)
const showRailRoutes = ref(true)
const isLoading = ref(false)
const error = ref('')

let network: Network | null = null
let nodesDataSet: DataSet<Node> | null = null
let edgesDataSet: DataSet<Edge> | null = null

const networkStats = ref<NetworkStats | null>(null)

const initializeNetwork = () => {
  if (!networkContainer.value) return

  nodesDataSet = new DataSet<Node>([])
  edgesDataSet = new DataSet<Edge>([])

  const options: Options = {
    nodes: {
      shape: 'dot',
      size: 20,
      font: {
        size: 14,
        color: '#e4e6eb',
      },
      borderWidth: 2,
    },
    edges: {
      arrows: { to: { enabled: true, scaleFactor: 0.5 } },
      smooth: { type: 'continuous' },
    },
    groups: {
      port: {
        color: { background: '#0984e3', border: '#74b9ff' },
        shape: 'circle',
      },
      plant: {
        color: { background: '#00b894', border: '#55efc4' },
        shape: 'square',
      },
    },
    physics: {
      enabled: true,
      stabilization: {
        enabled: true,
        iterations: 200,
      },
      barnesHut: {
        gravitationalConstant: -2000,
        springConstant: 0.001,
        springLength: 200,
        damping: 0.5,
      },
    },
    interaction: {
      hover: true,
      tooltipDelay: 100,
      zoomView: true,
      dragView: true,
    },
  }

  network = new Network(
    networkContainer.value,
    { nodes: nodesDataSet, edges: edgesDataSet },
    options
  )

  // Event listeners
  network.on('selectNode', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      console.log('Selected node:', nodeId)
    }
  })

  network.on('selectEdge', (params) => {
    if (params.edges.length > 0) {
      const edgeId = params.edges[0]
      console.log('Selected edge:', edgeId)
    }
  })
}

const buildNetworkData = () => {
  if (!nodesDataSet || !edgesDataSet) return

  const nodes: Node[] = []
  const edges: Edge[] = []
  const nodeIds = new Set<string>()

  // Add ports as nodes
  const ports = routeStore.routes
    .map(r => [r.from, r.to])
    .flat()
    .filter((port, index, self) => self.indexOf(port) === index)

  ports.forEach(portName => {
    if (showPorts.value) {
      nodes.push({
        id: portName,
        label: portName,
        group: 'port',
        title: `Port: ${portName}`,
      })
      nodeIds.add(portName)
    }
  })

  // Add plants (mock data - should come from rail cargo)
  const plants = ['Plant A', 'Plant B', 'Plant C']
  plants.forEach(plantName => {
    if (showPlants.value) {
      nodes.push({
        id: plantName,
        label: plantName,
        group: 'plant',
        title: `Plant: ${plantName}`,
      })
      nodeIds.add(plantName)
    }
  })

  // Add sea routes as edges
  if (showSeaRoutes.value) {
    routeStore.routes.forEach((route, idx) => {
      if (nodeIds.has(route.from) && nodeIds.has(route.to)) {
        edges.push({
          id: `sea-${idx}`,
          from: route.from,
          to: route.to,
          label: `${route.distance || 0} nm`,
          title: `Route: ${route.from} → ${route.to}\nDistance: ${route.distance || 0} nm`,
          color: { color: '#4a9eff' },
          width: 2,
        })
      }
    })
  }

  // Add rail routes (mock connections)
  if (showRailRoutes.value && showPlants.value) {
    plants.forEach((plant, idx) => {
      const targetPort = ports[idx % ports.length]
      if (nodeIds.has(plant) && nodeIds.has(targetPort)) {
        edges.push({
          id: `rail-${idx}`,
          from: plant,
          to: targetPort,
          label: 'Rail',
          title: `Rail: ${plant} → ${targetPort}`,
          color: { color: '#00b894' },
          width: 1,
          dashes: true,
        })
      }
    })
  }

  nodesDataSet.clear()
  edgesDataSet.clear()
  nodesDataSet.add(nodes)
  edgesDataSet.add(edges)

  // Update stats
  networkStats.value = {
    totalNodes: nodes.length,
    ports: ports.length,
    plants: plants.length,
    totalEdges: edges.length,
    seaRoutes: edges.filter(e => e.id?.toString().startsWith('sea-')).length,
    railRoutes: edges.filter(e => e.id?.toString().startsWith('rail-')).length,
  }
}

const refreshNetwork = async () => {
  isLoading.value = true
  error.value = ''

  try {
    await routeStore.fetchRoutes()
    buildNetworkData()
    
    if (network) {
      network.stabilize()
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to build network'
    console.error('Network build error:', err)
  } finally {
    isLoading.value = false
  }
}

const exportNetwork = async () => {
  try {
    await exportNetworkSnapshot()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to export network'
  }
}

const resetView = () => {
  if (network) {
    network.fit({
      animation: {
        duration: 500,
        easingFunction: 'easeInOutQuad',
      },
    })
  }
}

// Watch filter changes
watch([showPorts, showPlants, showSeaRoutes, showRailRoutes], () => {
  buildNetworkData()
})

onMounted(async () => {
  initializeNetwork()
  await refreshNetwork()
})

onUnmounted(() => {
  if (network) {
    network.destroy()
    network = null
  }
})
</script>

<style scoped>
.network-container {
  width: 100%;
  padding: 1.5rem;
  background: var(--bg-primary);
  border-radius: 8px;
}

.network-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.control-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.control-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: var(--text-primary);
}

.control-group input[type='checkbox'] {
  cursor: pointer;
}

.button-group {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-primary-dark);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-tertiary);
}

.alert {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.alert-error {
  background: var(--accent-danger-light);
  color: var(--accent-danger);
  border-left: 4px solid var(--accent-danger);
}

.loading-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.network-graph {
  width: 100%;
  height: 600px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.network-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--bg-secondary);
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  border: 1px solid var(--border-color);
}

.stat-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.stat-value {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent-primary);
}

.network-legend {
  background: var(--bg-secondary);
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.network-legend h4 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 600;
}

.legend-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-primary);
}

.legend-node {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.port-node {
  background: #0984e3;
  border-color: #74b9ff;
}

.plant-node {
  background: #00b894;
  border-color: #55efc4;
  border-radius: 3px;
}

.legend-line {
  width: 30px;
  height: 3px;
  position: relative;
}

.sea-route {
  background: #4a9eff;
}

.rail-route {
  background: #00b894;
  background-image: linear-gradient(
    90deg,
    #00b894 50%,
    transparent 50%,
    transparent
  );
  background-size: 10px 3px;
}
</style>
