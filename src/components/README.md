# Vue Components Documentation

This directory contains Vue 3 components for the vessel scheduling application, organized by functionality.

## Component Structure

### Gantt Chart Component
**Location:** `gantt/GanttChart.vue`

Displays a timeline visualization of vessel operations using a Gantt chart format.

**Features:**
- Timeline rendering with configurable days (7-365)
- Operation type filtering
- Color-coded operations (Loading, Discharge, Transit, Ballast, Canal, Bunker, Waiting)
- Export to Excel functionality
- Reactive updates when voyage data changes
- Interactive tooltips showing vessel and operation details

**Props:**
None (uses Vue stores for data)

**Emits:**
None

**Usage:**
```vue
<template>
  <GanttChart />
</template>

<script setup>
import GanttChart from '@/components/gantt/GanttChart.vue'
</script>
```

**Service:** [`gantt.service.ts`](../services/gantt.service.ts)

---

### Network Visualization Component
**Location:** `network/NetworkVisualization.vue`

Interactive network diagram showing ports, plants, and route connections using vis-network library.

**Features:**
- Interactive node and edge manipulation
- Port and plant node types with distinct styling
- Sea routes (solid lines) and rail routes (dashed lines)
- Toggle visibility of different node/edge types
- Physics-based layout with stabilization
- Network statistics display
- Export network data functionality
- Zoom and pan controls

**Props:**
None (uses Vue stores for data)

**Emits:**
None

**Usage:**
```vue
<template>
  <NetworkVisualization />
</template>

<script setup>
import NetworkVisualization from '@/components/network/NetworkVisualization.vue'
</script>
```

**Dependencies:**
- `vis-network/standalone` - Network visualization library

**Service:** [`network.service.ts`](../services/network.service.ts)

---

### Financial Analysis Component
**Location:** `financial/FinancialAnalysis.vue`

Comprehensive financial analysis dashboard with cost breakdown and voyage profitability.

**Features:**
- Summary cards showing total costs, revenue, profit, and TCE
- Cost breakdown by category (Bunker, Hire, Other)
- Interactive doughnut chart for cost distribution
- Detailed voyage-by-voyage financial table
- Bunker optimization suggestions
- Export to CSV functionality
- Reactive calculations based on cargo and vessel data

**Props:**
None (uses Vue stores for data)

**Emits:**
None

**Usage:**
```vue
<template>
  <FinancialAnalysis />
</template>

<script setup>
import FinancialAnalysis from '@/components/financial/FinancialAnalysis.vue'
</script>
```

**Dependencies:**
- `chart.js` - Chart rendering library

**Service:** [`financial.service.ts`](../services/financial.service.ts)

---

## Services

### Gantt Service
**File:** `src/services/gantt.service.ts`

Wraps the existing [`gantt-chart.js`](../../js/modules/gantt-chart.js) module with TypeScript types and Vue reactive integration.

**Key Functions:**
- `generateGanttFromVoyages(voyages, days)` - Generate Gantt data from voyage array
- `generateGanttData(days)` - Fetch and generate Gantt data from API
- `exportGantt()` - Export Gantt chart to Excel

### Network Service
**File:** `src/services/network.service.ts`

Provides network visualization functionality with TypeScript support.

**Key Functions:**
- `buildNetworkData(routes)` - Build network nodes and edges from routes
- `exportNetworkSnapshot()` - Export network data to Excel
- `calculateNetworkStats(data)` - Calculate network statistics

### Financial Service
**File:** `src/services/financial.service.ts`

Financial calculations and cost analysis based on the original [`financial-analysis.js`](../../js/modules/financial-analysis.js) module.

**Key Functions:**
- `calculateFinancialAnalysis(cargo, vessels, routes, params)` - Calculate voyage financials
- `optimizeBunkerStrategy()` - Optimize bunker costs
- `exportFinancialAnalysis(data)` - Export financial report

---

## Installation

Install required dependencies:

```bash
npm install vis-network chart.js
```

Or if using yarn:

```bash
yarn add vis-network chart.js
```

---

## TypeScript Types

All components use TypeScript for type safety. Key types include:

### Gantt Types
```typescript
interface GanttDay {
  operation: string
  class: string
}

interface GanttRow {
  vessel: string
  days: GanttDay[]
}
```

### Network Types
```typescript
interface NetworkNode {
  id: string
  label: string
  group: 'port' | 'plant'
  title: string
}

interface NetworkEdge {
  id: string
  from: string
  to: string
  label: string
  title: string
  color?: { color: string }
  width?: number
  dashes?: boolean
}
```

### Financial Types
```typescript
interface VoyageFinancial {
  id: string | number
  vessel: string
  cargo: number
  distance: number
  seaDays: number
  revenue: number
  bunkerCost: number
  hireCost: number
  portCost: number
  totalCost: number
  tce: number
  profit: number
}

interface FinancialData {
  voyages: VoyageFinancial[]
  totalVoyages: number
  totalRevenue: number
  totalCosts: number
  totalProfit: number
  avgTCE: number
  totalDistance: number
  totalDays: number
}
```

---

## Integration with Existing Code

These Vue components wrap the existing JavaScript modules located in [`js/modules/`](../../js/modules/):

- [`gantt-chart.js`](../../js/modules/gantt-chart.js) → `GanttChart.vue`
- [`network-viz.js`](../../js/modules/network-viz.js) → `NetworkVisualization.vue`
- [`financial-analysis.js`](../../js/modules/financial-analysis.js) → `FinancialAnalysis.vue`

The components maintain compatibility with the existing API while providing:
- Type safety through TypeScript
- Reactive data binding through Vue 3
- Modern component architecture
- Better code organization and reusability

---

## Styling

All components use scoped CSS with CSS custom properties (variables) for theming:

```css
--bg-primary: Background color (primary)
--bg-secondary: Background color (secondary)
--bg-tertiary: Background color (tertiary)
--text-primary: Text color (primary)
--text-secondary: Text color (secondary)
--border-color: Border color
--accent-primary: Accent color (primary)
--accent-danger: Danger/error color
--accent-warning: Warning color
```

These variables are defined globally and can be customized in your main CSS file.

---

## Testing

To test the components:

1. Ensure the backend API is running
2. Navigate to the appropriate view (GanttView, NetworkView, FinancialView)
3. Components will automatically fetch and display data

For development:
```bash
npm run dev
```

For building:
```bash
npm run build
```

---

## Notes

- All components are reactive and will automatically update when store data changes
- Error handling is built-in with user-friendly error messages
- Components support both API data and client-side calculations as fallback
- Export functionality requires backend API endpoints to be implemented
