# Priority 1 Missing Features Implementation Plan

**Project**: Voyage Planning System  
**Date**: 2025-12-26  
**Status**: Planning Phase  
**Approach**: Parallel Development

## Executive Summary

This plan addresses the CRITICAL (Priority 1) missing features identified for the voyage planning system. The implementation follows a parallel development approach where infrastructure, backend, and frontend components are developed simultaneously to maximize efficiency.

## Missing Features Overview

###  CRITICAL Priority (Priority 1)

1. **Voyage Builder** - Leg-by-leg voyage construction (PARTIALLY EXISTS)
2. **Operational Calendar** - Month/Week/Year/Timeline views with filters (NEW)
3. **Year Schedule Generator** - Annual planning tool (NEW)
4. **PDF Export** - All 4 report types: Comprehensive, Fleet, Schedule, Financial (PARTIALLY EXISTS)
5. **Cost Allocations** - Missing in both Cargo forms and Templates (NEW)
6. **Global Filters Bar** - Top-level filtering across modules (NEW)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vue 3 + TypeScript)            │
├─────────────────────────────────────────────────────────────┤
│  GlobalFiltersBar.vue (Persistent across views)             │
├─────────────────────┬───────────────┬───────────────────────┤
│  VoyageBuilder      │  Operational  │  Year Schedule        │
│  (Enhanced)         │  Calendar     │  Generator            │
│                     │  (NEW)        │  (NEW)                │
├─────────────────────┴───────────────┴───────────────────────┤
│              Pinia Stores (State Management)                 │
│  - filters.ts  - calendar.ts  - schedule.ts  - reports.ts   │
├─────────────────────────────────────────────────────────────┤
│              Services Layer (API Communication)              │
│  - calendar.service.ts  - schedule.service.ts  - etc.       │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                    BACKEND (Python/Flask)                    │
├─────────────────────────────────────────────────────────────┤
│  API Endpoints:                                              │
│  - /api/calendar/events                                      │
│  - /api/schedule/year                                        │
│  - /api/reports/generate                                     │
│  - /api/voyage-templates (with cost allocations)            │
├─────────────────────────────────────────────────────────────┤
│  PDF Reporter (Extended):                                    │
│  - generate_comprehensive_report()                           │
│  - generate_fleet_report()                                   │
│  - generate_schedule_report()                                │
│  - generate_financial_report()                               │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Infrastructure Foundation (Parallel Track A)

**TypeScript Types**

- `src/types/cargo.types.ts` - Add CostAllocation interface
- `src/types/calendar.types.ts` - CalendarEvent, ViewType, FilterOptions
- `src/types/schedule.types.ts` - YearSchedule, ResourceAllocation
- `src/types/reports.types.ts` - ReportType, ReportConfig, ExportOptions

**Pinia Stores**

- `src/stores/filters.ts` - Global filter state (module, vessel, status, dateRange)
- `src/stores/calendar.ts` - Calendar events, view type, selected date
- `src/stores/schedule.ts` - Year schedule data, templates
- `src/stores/reports.ts` - Report generation state, history

### Phase 2: Backend API Development (Parallel Track B)

**API Extensions** (`api_extensions_hardened.py`)

```python
# New endpoints to add:
@app.route('/api/calendar/events', methods=['GET'])
@app.route('/api/schedule/year', methods=['GET', 'POST'])
@app.route('/api/reports/generate', methods=['POST'])
@app.route('/api/voyage-templates', methods=['GET', 'POST'])
```

**PDF Reporter Enhancement** (`modules/pdf_reporter.py`)

```python
def generate_comprehensive_report(data, output_path):
    """All voyage details with calculations"""
    
def generate_fleet_report(vessels, utilization, output_path):
    """Fleet-wide vessel utilization and performance"""
    
def generate_schedule_report(voyages, timeline, output_path):
    """Timeline view with Gantt-style visualization"""
    
def generate_financial_report(financial_data, output_path):
    """Cost breakdown, revenue, profitability analysis"""
```

### Phase 3: Shared Components (Parallel Track C)

**Reusable Vue Components**

1. **GlobalFiltersBar.vue**
   - Module selector (Olya, Balakovo, DeepSea, All)
   - Vessel multi-select dropdown
   - Status toggles (Planned, In-Progress, Completed)
   - Date range picker
   - Persistent state via filters store
   - Apply/Reset actions

2. **DateRangePicker.vue**
   - Start date input
   - End date input
   - Quick presets (This Month, This Quarter, This Year)
   - Validation

3. **MultiSelect.vue**
   - Searchable dropdown
   - Select all/none
   - Chip display for selected items
   - Generic reusable component

4. **CostAllocationFields.vue**
   - operationalCost input
   - overheadCost input
   - otherCost input
   - totalCost calculated display
   - Validation

5. **ExportButton.vue**
   - Report type selector
   - Export format (PDF, Excel)
   - Loading state during generation
   - Download trigger

### Phase 4: Feature Implementation

#### A. Voyage Builder Enhancement (`src/views/VoyageBuilder.vue`)

**New Features:**

- Drag-and-drop leg reordering using vue-draggable
- Bulk operations: duplicate leg, delete multiple, import from template
- Real-time validation against vessel capacity
- Route optimization suggestions based on distance matrix
- Cost calculation preview

**Technical Details:**

```vue
<template>
  <draggable 
    v-model="formData.legs" 
    @end="onLegReorder"
    item-key="id"
  >
    <template #item="{ element, index }">
      <LegItem 
        :leg="element" 
        :index="index"
        @remove="removeLeg"
        @duplicate="duplicateLeg"
      />
    </template>
  </draggable>
</template>
```

#### B. Operational Calendar (`src/views/OperationalCalendarView.vue`)

**View Components:**

- `CalendarMonthView.vue` - Traditional calendar grid
- `CalendarWeekView.vue` - Week-by-week detailed view
- `CalendarYearView.vue` - 12-month miniature overview
- `CalendarTimelineView.vue` - Gantt-style vessel timeline

**Features:**

- View switching (Month/Week/Year/Timeline)
- Event filtering via GlobalFiltersBar
- Click event to show details in EventModal
- Export to CSV/PDF
- Statistics panel (total voyages, active vessels, cargo, cost)
- Upcoming events list

**Data Integration:**

```typescript
// Loads from multiple modules
async loadCalendarEvents() {
  const [deepsea, olya, balakovo] = await Promise.all([
    calendarService.getDeepSeaEvents(),
    calendarService.getOlyaEvents(),
    calendarService.getBalakovoEvents()
  ])
  this.events = [...deepsea, ...olya, ...balakovo]
}
```

#### C. Year Schedule Generator (`src/views/YearScheduleGeneratorView.vue`)

**Components:**

- `ScheduleConfigForm.vue` - Input parameters (year, module, optimization goals)
- `ResourceAllocationGrid.vue` - Visual vessel allocation across months
- `ConflictDetector.vue` - Highlights scheduling conflicts
- `TemplateSelector.vue` - Choose from predefined voyage templates

**Workflow:**

1. Select year and module
2. Choose vessels to include
3. Set optimization goals (maximize revenue, minimize cost, balance utilization)
4. Load cargo commitments
5. Generate schedule (backend calculation)
6. Review conflicts
7. Adjust manually
8. Export to PDF/Excel
9. Save as scenario

#### D. Cost Allocations

**CargoForm.vue Enhancement:**

```vue
<CostAllocationFields
  v-model:operational-cost="formData.operationalCost"
  v-model:overhead-cost="formData.overheadCost"
  v-model:other-cost="formData.otherCost"
/>
```

**New CargoTemplateForm.vue:**

- Similar to CargoForm but for templates
- Save/edit reusable cargo patterns with cost structures
- Apply template to new cargo commitments

**Data Model:**

```typescript
interface CostAllocation {
  operationalCost: number
  overheadCost: number
  otherCost: number
  totalCost?: number // computed
}

interface CargoCommitment {
  // ... existing fields
  costAllocation?: CostAllocation
}
```

### Phase 5: Routing & Navigation

**Router Updates** (`src/router/index.ts`)

```typescript
{
  path: '/operational-calendar',
  name: 'OperationalCalendar',
  component: () => import('@/views/OperationalCalendarView.vue'),
  meta: { title: 'Operational Calendar' }
},
{
  path: '/year-schedule',
  name: 'YearSchedule',
  component: () => import('@/views/YearScheduleGeneratorView.vue'),
  meta: { title: 'Year Schedule Generator' }
},
{
  path: '/reports',
  name: 'Reports',
  component: () => import('@/views/ReportsView.vue'),
  meta: { title: 'Reports & Export' }
}
```

**AppSidebar.vue Updates**

```vue
<nav-item icon="calendar" to="/operational-calendar">
  Operational Calendar
</nav-item>
<nav-item icon="schedule" to="/year-schedule">
  Year Schedule
</nav-item>
<nav-item icon="document" to="/reports">
  Reports
</nav-item>
```

### Phase 6: PDF Export Integration

**ReportsView.vue**

- Select report type (Comprehensive/Fleet/Schedule/Financial)
- Configure report parameters (date range, modules, vessels)
- Preview report data
- Generate and download PDF

**Integration Points:**

- VoyageBuilder: Export current voyage plan
- Calendar: Export calendar view as PDF
- Schedule: Export year schedule as PDF
- Financial: Export financial analysis as PDF

### Phase 7: Testing Strategy

**Unit Tests:**

- GlobalFiltersBar state management
- Calendar view switching logic
- Schedule conflict detection
- Cost allocation calculation
- PDF report generation

**Integration Tests:**

- API endpoints with real data
- End-to-end voyage creation workflow
- Calendar data loading from all modules
- Year schedule generation with optimization

**E2E Tests (Playwright):**

- Complete voyage builder flow
- Calendar navigation and filtering
- Year schedule generation and export
- PDF report download

## File Structure

```
src/
├── components/
│   ├── calendar/
│   │   ├── CalendarMonthView.vue
│   │   ├── CalendarWeekView.vue
│   │   ├── CalendarYearView.vue
│   │   ├── CalendarTimelineView.vue
│   │   └── EventModal.vue
│   ├── schedule/
│   │   ├── ScheduleConfigForm.vue
│   │   ├── ResourceAllocationGrid.vue
│   │   ├── ConflictDetector.vue
│   │   └── TemplateSelector.vue
│   ├── reports/
│   │   ├── ReportTypeSelector.vue
│   │   └── ReportPreview.vue
│   ├── cargo/
│   │   ├── CargoForm.vue (ENHANCE)
│   │   └── CargoTemplateForm.vue (NEW)
│   └── shared/
│       ├── GlobalFiltersBar.vue
│       ├── DateRangePicker.vue
│       ├── MultiSelect.vue
│       ├── CostAllocationFields.vue
│       └── ExportButton.vue
├── views/
│   ├── VoyageBuilder.vue (ENHANCE)
│   ├── OperationalCalendarView.vue (NEW)
│   ├── YearScheduleGeneratorView.vue (NEW)
│   └── ReportsView.vue (NEW)
├── stores/
│   ├── filters.ts (NEW)
│   ├── calendar.ts (NEW)
│   ├── schedule.ts (NEW)
│   ├── reports.ts (NEW)
│   └── cargo.ts (UPDATE)
├── services/
│   ├── calendar.service.ts (NEW)
│   ├── schedule.service.ts (NEW)
│   ├── voyage-builder.service.ts (NEW)
│   └── reports.service.ts (NEW)
└── types/
    ├── calendar.types.ts (NEW)
    ├── schedule.types.ts (NEW)
    ├── reports.types.ts (NEW)
    └── cargo.types.ts (UPDATE)

modules/
└── pdf_reporter.py (ENHANCE with 4 report types)

api_extensions_hardened.py (ADD new endpoints)
```

## Dependencies

**Frontend:**

```json
{
  "vue-draggable-next": "^2.2.1",  // Drag-drop for voyage builder
  "date-fns": "^2.30.0",           // Date manipulation
  "@vueuse/core": "^10.7.0"        // Composition utilities
}
```

**Backend:**

```
reportlab>=4.0.0  # PDF generation (already exists)
matplotlib>=3.7.0 # Charts for reports
```

## Success Criteria

- [ ] Voyage Builder supports full leg-by-leg construction with drag-drop
- [ ] Operational Calendar displays events from all modules with 4 view types
- [ ] Year Schedule Generator can create annual plans with conflict detection
- [ ] All 4 PDF report types generate successfully
- [ ] Cost allocations work in cargo forms and templates
- [ ] Global Filters Bar persists state and filters all views
- [ ] All new routes accessible via navigation
- [ ] All components have unit tests with >80% coverage
- [ ] E2E tests pass for critical workflows
- [ ] Documentation complete for all new features

## Migration Notes

**JavaScript to Vue Migration:**

- [`js/modules/voyage-builder.js`](js/modules/voyage-builder.js:1) → `src/services/voyage-builder.service.ts`
- [`js/modules/operational-calendar.js`](js/modules/operational-calendar.js:1) → `src/services/calendar.service.ts`

**Legacy Compatibility:**

- Keep JavaScript modules until Vue migration verified
- Use feature flags to switch between old/new implementations
- Gradual deprecation of JavaScript code

## Next Steps

1. Review and approve this plan
2. Set up development branches for parallel tracks
3. Assign tasks to development team
4. Begin infrastructure setup (Phase 1)
5. Daily standup to track progress across parallel tracks
6. Integration checkpoint after Phase 4 completion
7. QA and testing phase
8. Production deployment

---

**Note:** This plan focuses exclusively on Priority 1 CRITICAL features. Priority 2 (HIGH) and Priority 3 (MEDIUM) features will be planned separately after Priority 1 completion.
