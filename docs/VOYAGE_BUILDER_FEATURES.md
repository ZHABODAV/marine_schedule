# Voyage Builder - Advanced Features Documentation

## Overview

The Voyage Builder in [`src/views/VoyageBuilder.vue`](../src/views/VoyageBuilder.vue) provides a comprehensive set of tools for creating and optimizing voyage plans with advanced features including drag-and-drop reordering, bulk operations, real-time validation, route optimization, and cost calculation.

## Implemented Features

### 1. Drag-and-Drop Leg Reordering

**Technology**: vuedraggable v4.1.0

**Location**: Lines 189-290 in VoyageBuilder.vue

**Features**:
- Drag handle (⋮⋮) for intuitive reordering
- Visual feedback during drag operations
- Ghost element styling for better UX
- Animation (200ms) for smooth transitions
- Automatic recalculation after reordering

**Usage**:
```vue
<draggable 
  v-model="formData.legs" 
  item-key="id"
  handle=".drag-handle"
  animation="200"
  ghost-class="ghost"
  @start="drag = true" 
  @end="drag = false"
>
  <!-- Leg items -->
</draggable>
```

**User Actions**:
1. Hover over the drag handle (⋮⋮) on any leg
2. Click and hold to grab the leg
3. Drag to desired position
4. Release to drop

---

### 2. Bulk Operations

#### 2.1 Select Multiple Legs

**Location**: Lines 182-186 (Select All checkbox)

**Features**:
- Individual leg selection via checkboxes
- Select All / Deselect All toggle
- Visual indication of selected legs (highlighted in blue)
- Selected count displayed on action buttons

**User Actions**:
1. Check individual leg checkboxes to select specific legs
2. Or use "Select All" checkbox to select all legs at once

#### 2.2 Delete Multiple Legs

**Location**: Lines 111-113 (Delete button), 687-699 (logic)

**Features**:
- Bulk delete selected legs
- Confirmation dialog before deletion
- Disabled when no legs are selected
- Shows count of selected legs
- Maintains at least one leg in the voyage

**User Actions**:
1. Select one or more legs
2. Click "Delete (X)" button where X is the number of selected legs
3. Confirm deletion in the dialog

#### 2.3 Duplicate Selected Legs

**Location**: Lines 114-116 (Duplicate button), 662-668 (logic)

**Features**:
- Duplicates all selected legs
- Inserts duplicates immediately after originals
- Automatic ID generation for new legs
- Preserves all leg properties

**User Actions**:
1. Select one or more legs
2. Click "Duplicate (X)" button
3. Duplicated legs appear after each selected leg

#### 2.4 Import from Template

**Location**: Lines 94-107 (Template selector), 704-725 (logic)

**Features**:
- Load predefined voyage templates
- Replace current legs with template legs
- Template preview shows estimated days
- Automatic cost recalculation after import

**User Actions**:
1. Select a template from the "Select Route / Template" dropdown
2. Template legs automatically replace current legs
3. Review and modify as needed

---

### 3. Real-time Validation Against Vessel Capacity

**Location**: Lines 543-561 (computed property), 124-131 (UI alert)

**Features**:
- Continuous monitoring of total cargo vs vessel capacity
- Visual alerts (red = exceeded, green = within limits)
- Overload calculation when exceeded
- Utilization percentage display
- Automatic recalculation on any change

**Validation Logic**:
```typescript
const capacityValidation = computed(() => {
  const totalCargo = formData.value.legs
    .filter(leg => ['loading', 'discharge'].includes(leg.type))
    .reduce((sum, leg) => sum + (leg.cargo || 0), 0)
  
  const vesselCapacity = selectedVessel.value?.capacity || 0
  const exceeded = totalCargo > vesselCapacity
  const overload = exceeded ? totalCargo - vesselCapacity : 0
  const utilizationPercent = vesselCapacity > 0 
    ? Math.round((totalCargo / vesselCapacity) * 100) 
    : 0
  
  return { totalCargo, vesselCapacity, exceeded, overload, utilizationPercent }
})
```

**Alerts**:
- **Error (Red)**: "Total cargo (X tons) exceeds vessel capacity (Y tons)! Overload: Z tons"
- **Success (Green)**: " Cargo within limits: X / Y tons (Z% utilization)"

---

### 4. Route Optimization Suggestions

**Location**: Lines 117-119 (Optimize button), 751-815 (logic), 133-145 (UI panel)

**Features**:
- Automatic detection of routing inefficiencies
- Actionable suggestions with one-click fixes
- Multiple optimization types:
  - Missing transit legs
  - Consecutive transit legs that can be merged
  - Zero-distance transit legs
  - Low/high utilization warnings

**Optimization Types**:

#### 4.1 Missing Transit Legs
**Detection**: Leg endings don't match next leg's beginning
**Suggestion**: "Leg X ends at Port A but Leg Y starts at Port B. Consider adding a transit leg."
**Action**: Click "Apply" to auto-insert transit leg

#### 4.2 Merge Consecutive Transit Legs
**Detection**: Two consecutive legs are both transit type
**Suggestion**: "Legs X and Y are both transit legs. Consider merging them."
**Action**: Click "Apply" to merge into one leg

#### 4.3 Zero-Distance Transit
**Detection**: Transit leg with 0 distance
**Suggestion**: "Leg X is a transit leg with zero distance. Please verify."
**Action**: Manual review required

#### 4.4 Utilization Optimization
**Detection**: Vessel utilization < 50% or > 90%
**Suggestions**:
- Low: "Low vessel utilization (X%). Consider adding more cargo or using a smaller vessel."
- Excellent: "Excellent vessel utilization (X%)!" 

**User Actions**:
1. Click "Optimize" button in the route toolbar
2. Review suggestions in the optimization panel
3. Click "Apply" on actionable suggestions
4. Manually review informational suggestions

---

### 5. Cost Calculation Preview

**Location**: Lines 148-176 (UI), 857-908 (calculation logic)

**Features**:
- Real-time cost estimation
- Breakdown by category:
  - Fuel costs
  - Port fees
  - Canal fees
  - Other costs
- Total voyage cost
- Cost per nautical mile
- Automatic recalculation on changes

**Cost Calculation Logic**:

```typescript
const fuelPricePerTon = 600 // USD
const fuelConsumptionPerNm = 0.3 // tons per nm
const portFeeAverage = 5000 // USD per port call
const canalFeeAverage = 50000 // USD per canal transit

formData.value.legs.forEach(leg => {
  // Fuel costs (transit legs)
  if (leg.type === 'transit' && leg.distance) {
    fuelCost += leg.distance * fuelConsumptionPerNm * fuelPricePerTon
  }
  
  // Port fees (loading/discharge legs)
  if (['loading', 'discharge'].includes(leg.type)) {
    portFees += portFeeAverage
  }
  
  // Canal fees (canal legs)
  if (leg.type === 'canal') {
    canalFees += canalFeeAverage
  }
})
```

**Display**:
- Fuel Cost: $X
- Port Fees: $Y
- Canal Fees: $Z
- Other Costs: $W
- **Total Estimated Cost: $Total** (highlighted)
- Cost per nm: $A.BC

---

### 6. Distance Matrix Integration

**Location**: Lines 931-967 (loading), 841-856 (usage), 980-987 (module watcher)

**Features**:
- Automatic loading of distance data from CSV files
- Module-specific distance matrices
- Bidirectional distance lookup
- Used for route optimization suggestions
- Fallback to default estimate when data unavailable

**Data Source**:
```
/input/{module}/distances_{module}.csv
```

**CSV Format**:
```csv
From,To,Distance
Port A,Port B,500
Port B,Port C,350
...
```

**Usage in Code**:
```typescript
function getDistanceBetweenPorts(from: string, to: string): number {
  const key = `${from}-${to}`
  if (distanceMatrix.value[key]) {
    return distanceMatrix.value[key]
  }
  return 500 // Default estimate
}
```

---

## UI Components Structure

### Route Configuration Step (Step 2)

```
┌─────────────────────────────────────────────────────────┐
│ Route Toolbar                                            │
│ ┌─────────────────┐  ┌────────┐ ┌────────┐ ┌────────┐ │
│ │ Template Select │  │ Delete │ │Duplicate│ │Optimize│ │
│ └─────────────────┘  └────────┘ └────────┘ └────────┘ │
├─────────────────────────────────────────────────────────┤
│ Capacity Validation Alert (Red/Green)                   │
├─────────────────────────────────────────────────────────┤
│ Optimization Suggestions Panel (if suggestions exist)   │
│ ┌───────────────────────────────────────────────┐      │
│ │  Suggestion message              [Apply]     │      │
│ │  Suggestion message              [Apply]     │      │
│ └───────────────────────────────────────────────┘      │
├─────────────────────────────────────────────────────────┤
│ Cost Preview Panel                                       │
│ ┌───────────────────────────────────────────────┐      │
│ │ Fuel Cost:      $X                             │      │
│ │ Port Fees:      $Y                             │      │
│ │ Canal Fees:     $Z                             │      │
│ │ Total:          $T                             │      │
│ │ Cost per nm:    $A.BC                          │      │
│ └───────────────────────────────────────────────┘      │
├─────────────────────────────────────────────────────────┤
│ Route Legs (X legs, Y nm, ~Z days)    [] Select All   │
│                                                          │
│ ┌────────────────────────────────────────────────┐     │
│ │ [] ⋮⋮ Leg 1                 [Remove]         │     │
│ │ Type: Loading  From: A  To: B  Distance: 500   │     │
│ └────────────────────────────────────────────────┘     │
│ ┌────────────────────────────────────────────────┐     │
│ │ [ ] ⋮⋮ Leg 2                 [Remove]         │     │
│ │ Type: Transit  From: B  To: C  Distance: 350   │     │
│ └────────────────────────────────────────────────┘     │
│                                                          │
│              [+ Add Leg]                                │
└─────────────────────────────────────────────────────────┘
```

---

## Styling Classes

### Leg States
- `.leg-item` - Base leg styling
- `.leg-item.selected` - Selected leg (blue highlight)
- `.leg-item.ghost` - Dragging state (semi-transparent)

### Alerts
- `.alert.alert-error` - Red alert for capacity exceeded
- `.alert.alert-success` - Green alert for valid capacity

### Panels
- `.optimization-panel` - Blue-tinted suggestion panel
- `.cost-preview` - Yellow-tinted cost breakdown panel

---

## Performance Optimizations

1. **Reactive Computations**: All calculations use Vue computed properties for efficiency
2. **Debouncing**: Input changes trigger immediate recalculation (no artificial delays)
3. **Efficient Array Operations**: Uses native array methods (filter, reduce, map)
4. **Selective Re-rendering**: Only affected components re-render on changes

---

## Error Handling

1. **Type Safety**: Full TypeScript type checking with null/undefined guards
2. **Validation**: Step-by-step validation prevents invalid voyage creation
3. **User Feedback**: Clear error messages and alerts
4. **Graceful Degradation**: Features work even if optional data (templates, distance matrix) fails to load

---

## Browser Compatibility

- Chrome/Edge: Full support 
- Firefox: Full support 
- Safari: Full support 
- Mobile browsers: Responsive design with mobile-friendly interactions

---

## Future Enhancements

1. **Advanced Optimization**: AI-powered route optimization using machine learning
2. **What-If Analysis**: Compare multiple voyage scenarios side-by-side
3. **Weather Integration**: Real-time weather data for route optimization
4. **Cost Refinement**: More granular cost models based on vessel characteristics
5. **Historical Analysis**: Learn from past voyages to improve suggestions

---

## Troubleshooting

### Drag-and-drop not working
- Ensure vuedraggable dependency is installed: `npm install vuedraggable@4.1.0`
- Check browser console for JavaScript errors
- Verify drag handle (⋮⋮) is visible

### Distance matrix not loading
- Check network tab for failed CSV request
- Verify file exists at `/input/{module}/distances_{module}.csv`
- Check CSV format matches expected structure
- Feature degrades gracefully with default estimates

### Cost calculations seem incorrect
- Verify vessel selection (costs depend on vessel properties)
- Check leg types are correctly set
- Review default cost constants in code (lines 869-872)
- Ensure all leg distances are entered

### Optimization suggestions not appearing
- Click "Optimize" button to trigger analysis
- Ensure voyage has at least 2 legs
- Some suggestions only appear for specific route configurations

---

## API Reference

### Key Functions

#### `duplicateLeg(index: number)`
Duplicates a single leg at the specified index.

#### `duplicateSelectedLegs()`
Duplicates all currently selected legs.

#### `showBulkDeleteDialog()`
Shows confirmation dialog and deletes selected legs.

#### `toggleLegSelection(index: number)`
Toggles selection state of a leg.

#### `toggleSelectAll()`
Toggles selection of all legs.

#### `optimizeRoute()`
Analyzes route and generates optimization suggestions.

#### `applySuggestion(suggestion: any)`
Applies an actionable optimization suggestion.

#### `recalculateCosts()`
Recalculates all voyage costs based on current legs.

#### `validateCapacity()`
Validates total cargo against vessel capacity.

#### `loadDistanceMatrix()`
Loads distance data from CSV file for current module.

#### `getDistanceBetweenPorts(from: string, to: string): number`
Retrieves distance between two ports from the matrix.

---

## Testing

### Manual Testing Checklist

- [ ] Drag-and-drop reordering works smoothly
- [ ] Single leg duplication creates exact copy
- [ ] Bulk duplication works with multiple selections
- [ ] Bulk delete shows confirmation and removes legs
- [ ] Select All toggles all checkboxes
- [ ] Template import replaces legs correctly
- [ ] Capacity validation shows correct alerts
- [ ] Utilization percentage calculates correctly
- [ ] Optimization suggestions appear appropriately
- [ ] Apply suggestion modifies route as expected
- [ ] Cost preview updates in real-time
- [ ] Distance matrix loads for each module
- [ ] All features work on mobile devices

### Automated Testing

Unit tests should cover:
- Capacity calculation logic
- Cost calculation logic
- Optimization suggestion detection
- Distance matrix parsing
- Bulk operations

---

## Code Examples

### Adding a Custom Optimization Rule

```typescript
// In optimizeRoute() function, add new rule:
if (formData.value.legs.some(leg => leg.type === 'bunker' && !leg.port)) {
  optimizationSuggestions.value.push({
    icon: '',
    message: 'Bunker leg detected without port specification.',
    action: null,
    data: null
  })
}
```

### Customizing Cost Calculation

```typescript
// Modify cost constants in recalculateCosts():
const fuelPricePerTon = 700 // Increase fuel price
const heavyWeatherMultiplier = 1.15 // Add weather factor

if (leg.weatherRisk === 'high') {
  fuelCost *= heavyWeatherMultiplier
}
```

---

## Related Documentation

- [`PRIORITY1_MISSING_FEATURES_PLAN.md`](../plans/PRIORITY1_MISSING_FEATURES_PLAN.md) - Overall feature plan
- [`COMPREHENSIVE_CALCULATION_GUIDE.md`](COMPREHENSIVE_CALCULATION_GUIDE.md) - Detailed calculation methods
- [`FEATURE_MIGRATION_CHECKLIST.md`](FEATURE_MIGRATION_CHECKLIST.md) - Migration from legacy code
- [`TESTING_GUIDE.md`](TESTING_GUIDE.md) - Testing strategies

---

**Last Updated**: 2025-12-26
**Version**: 1.0.0
**Component**: VoyageBuilder.vue
