# Component API Reference

This document provides comprehensive API documentation for all Vue.js components in the Vessel Scheduler application.

## Table of Contents

- [Gantt Chart Components](#gantt-chart-components)
- [Cargo Management Components](#cargo-management-components)
- [Vessel Management Components](#vessel-management-components)
- [Route Management Components](#route-management-components)
- [Shared Base Components](#shared-base-components)
- [Layout Components](#layout-components)

---

## Gantt Chart Components

### GanttChart

**Location:** [`src/components/gantt/GanttChart.vue`](../src/components/gantt/GanttChart.vue)

**Description:** Interactive Gantt chart visualization for vessel scheduling operations.

#### Props

This component uses no props - it's a self-contained view component.

#### Events

This component emits no events.

#### Slots

This component has no slots.

#### Exposed Methods

None - uses internal reactive state.

#### Usage Example

```vue
<template>
  <GanttChart />
</template>

<script setup>
import GanttChart from '@/components/gantt/GanttChart.vue'
</script>
```

#### Features

- **Timeline Control**: Adjustable timeline from 7 to 365 days
- **Voyage Filtering**: Filter by all, active, planned, or custom selection
- **Interactive Display**: Hover to view operation details
- **Export Capability**: Export to Excel format
- **Real-time Refresh**: Refresh button to reload data
- **Operation Legend**: Visual legend for different operation types:
  - П (Green) - Loading
  - В (Blue) - Discharge
  - Т (Purple) - Transit
  - Б (Yellow) - Ballast
  - К (Orange) - Canal
  - Ф (Pink) - Bunker

#### State Management

- Uses [`useVoyageStore()`](../src/stores/voyage.ts) for voyage data
- Uses [`useVesselStore()`](../src/stores/vessel.ts) for vessel data

---

## Cargo Management Components

### CargoForm

**Location:** [`src/components/cargo/CargoForm.vue`](../src/components/cargo/CargoForm.vue)

**Description:** Modal form for creating and editing cargo commitments.

#### Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `show` | `boolean` | Yes | - | Controls modal visibility |
| `cargo` | `CargoCommitment \| null` | No | `null` | Cargo data for editing (null for create) |
| `submitting` | `boolean` | No | `false` | Indicates submission in progress |

#### Events

| Event | Payload | Description |
|-------|---------|-------------|
| `close` | None | Emitted when modal is closed |
| `submit` | `CargoFormData` | Emitted when form is submitted with valid data |

#### Slots

None

#### Usage Example

```vue
<template>
  <CargoForm
    :show="showForm"
    :cargo="selectedCargo"
    :submitting="isSubmitting"
    @close="showForm = false"
    @submit="handleCargoSubmit"
  />
</template>

<script setup>
import { ref } from 'vue'
import CargoForm from '@/components/cargo/CargoForm.vue'
import type { CargoCommitment, CargoFormData } from '@/types/cargo.types'

const showForm = ref(false)
const selectedCargo = ref<CargoCommitment | null>(null)
const isSubmitting = ref(false)

const handleCargoSubmit = async (data: CargoFormData) => {
  isSubmitting.value = true
  // Handle submission logic
  isSubmitting.value = false
  showForm.value = false
}
</script>
```

#### Form Fields

**Required Fields:**
- `id` - Cargo identifier (disabled in edit mode)
- `commodity` - Type of commodity
- `quantity` - Quantity in metric tons
- `loadPort` - Loading port name
- `dischPort` - Discharge port name
- `laycanStart` - Laycan start date
- `laycanEnd` - Laycan end date

**Optional Fields:**
- `status` - Cargo status (visible in edit mode only)
- `freightRate` - Freight rate in $/MT
- `notes` - Additional notes

#### Validation

- All required fields must be filled
- Quantity must be greater than 0
- Laycan end date must be after start date
- Real-time validation with error messages

### CargoList

**Location:** [`src/components/cargo/CargoList.vue`](../src/components/cargo/CargoList.vue)

**Description:** Table display of cargo commitments with sorting and filtering.

*(Refer to component file for detailed API)*

### CargoDetail

**Location:** [`src/components/cargo/CargoDetail.vue`](../src/components/cargo/CargoDetail.vue)

**Description:** Detailed view of a single cargo commitment.

*(Refer to component file for detailed API)*

---

## Vessel Management Components

### VesselForm

**Location:** [`src/components/vessel/VesselForm.vue`](../src/components/vessel/VesselForm.vue)

**Description:** Form for creating and editing vessel information.

*(Refer to component file for detailed API)*

### VesselList

**Location:** [`src/components/vessel/VesselList.vue`](../src/components/vessel/VesselList.vue)

**Description:** Table display of vessel fleet with filtering capabilities.

*(Refer to component file for detailed API)*

### VesselDetail

**Location:** [`src/components/vessel/VesselDetail.vue`](../src/components/vessel/VesselDetail.vue)

**Description:** Detailed view of vessel specifications and history.

*(Refer to component file for detailed API)*

---

## Route Management Components

### RouteForm

**Location:** [`src/components/route/RouteForm.vue`](../src/components/route/RouteForm.vue)

**Description:** Form for creating and editing shipping routes.

*(Refer to component file for detailed API)*

### RouteList

**Location:** [`src/components/route/RouteList.vue`](../src/components/route/RouteList.vue)

**Description:** List view of available shipping routes.

*(Refer to component file for detailed API)*

### RouteVisualization

**Location:** [`src/components/route/RouteVisualization.vue`](../src/components/route/RouteVisualization.vue)

**Description:** Visual representation of route networks.

*(Refer to component file for detailed API)*

---

## Shared Base Components

### BaseButton

**Location:** [`src/components/shared/BaseButton.vue`](../src/components/shared/BaseButton.vue)

**Description:** Reusable button component with multiple variants and states.

#### Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `type` | `'button' \| 'submit' \| 'reset'` | No | `'button'` | HTML button type |
| `variant` | `'primary' \| 'secondary' \| 'danger' \| 'success' \| 'ghost'` | No | `'primary'` | Visual style variant |
| `size` | `'small' \| 'medium' \| 'large'` | No | `'medium'` | Button size |
| `icon` | `string` | No | - | Icon to display |
| `loading` | `boolean` | No | `false` | Shows loading spinner |
| `disabled` | `boolean` | No | `false` | Disables the button |
| `fullWidth` | `boolean` | No | `false` | Makes button full width |

#### Events

| Event | Payload | Description |
|-------|---------|-------------|
| `click` | `MouseEvent` | Emitted on button click |

#### Slots

| Slot | Description |
|------|-------------|
| `default` | Button text content |

#### Usage Example

```vue
<template>
  <BaseButton
    variant="primary"
    size="medium"
    :loading="isSubmitting"
    @click="handleClick"
  >
    Submit
  </BaseButton>
</template>

<script setup>
import { ref } from 'vue'
import BaseButton from '@/components/shared/BaseButton.vue'

const isSubmitting = ref(false)

const handleClick = () => {
  console.log('Button clicked')
}
</script>
```

#### Variants

- **primary**: Blue background, white text
- **secondary**: Gray background, white text
- **danger**: Red background, white text
- **success**: Green background, white text
- **ghost**: Transparent background, blue text with border

#### Accessibility

- Proper keyboard navigation support
- Focus-visible outline for keyboard users
- Disabled state properly communicated to screen readers

### BaseInput

**Location:** [`src/components/shared/BaseInput.vue`](../src/components/shared/BaseInput.vue)

**Description:** Reusable input component with validation support.

*(Refer to component file for detailed API)*

### BaseSelect

**Location:** [`src/components/shared/BaseSelect.vue`](../src/components/shared/BaseSelect.vue)

**Description:** Reusable select dropdown component.

*(Refer to component file for detailed API)*

### BaseModal

**Location:** [`src/components/shared/BaseModal.vue`](../src/components/shared/BaseModal.vue)

**Description:** Modal dialog component for overlays.

*(Refer to component file for detailed API)*

### LoadingSpinner

**Location:** [`src/components/shared/LoadingSpinner.vue`](../src/components/shared/LoadingSpinner.vue)

**Description:** Animated loading indicator.

*(Refer to component file for detailed API)*

---

## Layout Components

### TheLayout

**Location:** [`src/components/layout/TheLayout.vue`](../src/components/layout/TheLayout.vue)

**Description:** Main application layout with header and sidebar.

*(Refer to component file for detailed API)*

### AppHeader

**Location:** [`src/components/layout/AppHeader.vue`](../src/components/layout/AppHeader.vue)

**Description:** Application header with navigation and branding.

*(Refer to component file for detailed API)*

### AppSidebar

**Location:** [`src/components/layout/AppSidebar.vue`](../src/components/layout/AppSidebar.vue)

**Description:** Application sidebar navigation menu.

*(Refer to component file for detailed API)*

---

## Financial Components

### FinancialAnalysis

**Location:** [`src/components/financial/FinancialAnalysis.vue`](../src/components/financial/FinancialAnalysis.vue)

**Description:** Financial analysis and reporting component.

*(Refer to component file for detailed API)*

---

## Network Visualization Components

### NetworkVisualization

**Location:** [`src/components/network/NetworkVisualization.vue`](../src/components/network/NetworkVisualization.vue)

**Description:** Interactive visualization of shipping network.

*(Refer to component file for detailed API)*

---

## Best Practices

### Component Development Guidelines

1. **TypeScript First**: Use TypeScript with proper type definitions
2. **Composition API**: Use `<script setup>` syntax for cleaner code
3. **Props Validation**: Always define prop types and defaults
4. **Event Typing**: Type all emitted events with payloads
5. **Accessibility**: Include ARIA labels and keyboard navigation
6. **Error Handling**: Provide user feedback for errors
7. **Loading States**: Show loading indicators for async operations

### State Management

- Use Pinia stores for global state
- Keep local component state minimal
- Use composables for shared logic

### Testing

Each component should have:
- Unit tests for business logic
- Component tests for user interactions
- Accessibility tests for WCAG compliance

See [`TESTING_GUIDE.md`](./TESTING_GUIDE.md) for more details.

---

## Related Documentation

- [Developer Guide](./DEVELOPER_GUIDE.md)
- [API Reference](./API_REFERENCE.md)
- [Testing Guide](./TESTING_GUIDE.md)
- [Vue Migration Plan](../plans/VUE_MIGRATION_PLAN.md)
