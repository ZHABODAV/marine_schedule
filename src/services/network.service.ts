/**
 * Network Visualization Service
 * Wraps network visualization functionality with TypeScript types
 */

import type { Route } from '@/types/route.types'

export interface NetworkNode {
  id: string
  label: string
  group: 'port' | 'plant'
  title: string
}

export interface NetworkEdge {
  id: string
  from: string
  to: string
  label: string
  title: string
  color?: { color: string }
  width?: number
  dashes?: boolean
}

export interface NetworkData {
  nodes: NetworkNode[]
  edges: NetworkEdge[]
}

/**
 * Build network data from routes and related data
 */
export function buildNetworkData(routes: Route[]): NetworkData {
  const nodes: NetworkNode[] = []
  const edges: NetworkEdge[] = []
  const nodeIds = new Set<string>()

  // Extract unique ports from routes
  const ports = routes
    .map((r) => [r.from, r.to])
    .flat()
    .filter((port, index, self) => self.indexOf(port) === index)

  // Add ports as nodes
  ports.forEach((portName) => {
    nodes.push({
      id: portName,
      label: portName,
      group: 'port',
      title: `Port: ${portName}`,
    })
    nodeIds.add(portName)
  })

  // Add sea routes as edges
  routes.forEach((route, idx) => {
    if (nodeIds.has(route.from) && nodeIds.has(route.to)) {
      edges.push({
        id: `sea-${idx}`,
        from: route.from,
        to: route.to,
        label: `${route.distance || 0} nm`,
        title: `Route: ${route.from} → ${route.to}\nDistance: ${route.distance || 0} nm${
          route.canal ? `\nCanal: ${route.canal}` : ''
        }`,
        color: { color: '#4a9eff' },
        width: 2,
      })
    }
  })

  return { nodes, edges }
}

/**
 * Export network snapshot to Excel
 */
export async function exportNetworkSnapshot(): Promise<void> {
  try {
    // This would typically call an API endpoint
    // For now, we'll create a simple CSV export
    const response = await fetch('/api/network/export', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error('Failed to export network snapshot')
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `network_snapshot_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Network export error:', error)
    throw error
  }
}

/**
 * Calculate network statistics
 */
export function calculateNetworkStats(data: NetworkData) {
  const portNodes = data.nodes.filter((n) => n.group === 'port')
  const plantNodes = data.nodes.filter((n) => n.group === 'plant')
  const seaEdges = data.edges.filter((e) => !e.dashes)
  const railEdges = data.edges.filter((e) => e.dashes)

  return {
    totalNodes: data.nodes.length,
    ports: portNodes.length,
    plants: plantNodes.length,
    totalEdges: data.edges.length,
    seaRoutes: seaEdges.length,
    railRoutes: railEdges.length,
  }
}
