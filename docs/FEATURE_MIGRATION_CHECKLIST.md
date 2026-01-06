# Feature Migration Checklist

**Comparing:** `vessel_scheduler_complete.html` → New Vue.js Application

**Purpose:** Ensure all features from the legacy application are transferred to the new system.

---

## Analysis Summary

### Legacy System Features (vessel_scheduler_complete.html)

Based on the comprehensive analysis of the 4459-line file, here's what the legacy system contains:

####  Core Tabs/Modules (23 tabs total):

1. **Dashboard (Общая панель)** - Summary statistics, cross-filtering
2. **Vessels (Суда)** - Fleet management
3. **Cargo (Грузы)** - Cargo commitments
4. **Routes (Маршруты)** - Route management
5. **Schedule (Расписание)** - Generated schedules with Gantt chart
6. **Voyage Builder (Конструктор рейсов)** - Build voyages leg-by-leg
7. **Comparison (Сравнение)** - Compare voyages/scenarios
8. **Port Stock (Склады портов)** - Port inventory tracking
9. **Sales Plan (План продаж)** - Sales planning calculator
10. **Network (Сеть)** - Network visualization (vis-network)
11. **Reports (Отчеты)** - Excel/PDF export
12. **Alerts (Оповещения)** - Alerts dashboard
13. **Berth Manager (Причалы)** - Berth management
14. **Bunker Opt (Бункер)** - Bunker optimization
15. **Weather (Погода)** - Weather integration
16. **Tracking (Трекинг)** - Vessel tracking
17. **Scenario Mgmt (Сценарии)** - Scenario management
18. **Templates (Шаблоны)** - Voyage templates
19. **Capacity Plan (Вместимость)** - Berth capacity planning
20. **Trading Lanes (Торговые линии)** - Trading lanes generation
21. **Vessel Cargo Assignment (Назначения)** - Auto vessel-cargo assignment
22. **Year Schedule (Годовое расписание)** - Annual schedule generator
23. **Operational Calendar (Оперативный календарь)** - Calendar view
24. **Financial Analysis (Финансовый анализ)** - Financial analysis

---

## Feature-by-Feature Comparison

### 1. Dashboard / General Panel 

| Feature | Legacy | Vue.js | Status | Notes |
|---------|--------|--------|--------|-------|
| Active vessels count |  |  | **Transferred** | In DashboardView.vue |
| Pending cargo count |  |  | **Transferred** | In DashboardView.vue |
| Active voyages count |  |  | **Transferred** | In DashboardView.vue |
| Fleet utilization % |  |  | **Transferred** | In DashboardView.vue |
| Cross-filtering panel |  |  | **Partial** | Needs enhancement |
| Unified info panel (Cargo-Vessel-Voyage-Route) |  |  | **MISSING** | Priority HIGH |

**Action Items:**
- [ ] Implement unified info panel component
- [ ] Enhance cross-filtering ReactiveTransitions
- [ ] Add quick search functionality

---

### 2. Vessel Management 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| List all vessels |  |  | **Transferred** |
| Add/Edit vessel modal |  |  | **Transferred** |
| Delete vessel |  |  | **Needs confirmation** |
| Vessel details (ID, Name, Class, DWT, Speed) |  |  | **Transferred** |
| Filter/Search vessels |  |  | **Partial** |

**Action Items:**
- [ ] Verify delete functionality
- [ ] Add advanced filtering

---

### 3. Cargo Management 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| List cargo commitments |  |  | **Transferred** |
| Add/Edit cargo |  |  | **Transferred** (CargoForm.vue) |
| Cargo fields (ID, Commodity, Quantity, Ports, Laycan) |  |  | **Transferred** |
| **Cost allocations** (Operational, Overhead, Other) |  |  | **MISSING** |
| Status badges |  |  | **Transferred** |

**Action Items:**
- [ ] **Add cost allocation fields to CargoForm.vue** (Priority HIGH)

---

### 4. Route Management 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| List routes |  |  | **Transferred** |
| Add/Edit route |  |  | **Transferred** |
| From/To ports, Distance, Canal |  |  | **Transferred** |
| Bulk select routes |  |  | **MISSING** |
| Transfer routes to Voyage Builder |  |  | **MISSING** |

**Action Items:**
- [ ] Add bulk selection checkboxes
- [ ] Add "Transfer to Builder" functionality

---

### 5. Schedule / Gantt Chart 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Generate schedule button |  |  | **Transferred** |
| Gantt table visualization |  |  | **Transferred** (GanttChart.vue) |
| Operation types legend |  |  | **Transferred** |
| Operation type filters (checkboxes) |  |  | **MISSING** |
| Voyage selection filter (all/active/planned/custom) |  |  | **Transferred** |
| Timeline days adjustment |  |  | **Transferred** |
| Export to Excel |  |  | **Transferred** |

**Action Items:**
- [ ] **Add operation type filter checkboxes** (П, В, Т, Б, К, Ф)

---

### 6. Voyage Builder 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Add voyage leg |  |  | **MISSING** |
| Leg-by-leg construction |  |  | **MISSING** |
| Validate voyage |  |  | **MISSING** |
| Save as template |  |  | **MISSING** |
| Transfer routes from Routes tab |  |  | **MISSING** |

**Status:**  **NOT TRANSFERRED**

**Action Items:**
- [ ] **Create VoyageBuilder.vue component** (Priority CRITICAL)
- [ ] Implement leg management
- [ ] Add validation logic
- [ ] Integrate with templates

---

### 7. Voyage Comparison 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Select voyages/scenarios for comparison |  |  | **MISSING** |
| Run comparison |  |  | **MISSING** |
| Display comparison results |  |  | **MISSING** |

**Status:**  **NOT TRANSFERRED**

**Action Items:**
- [ ] **Create ComparisonView.vue** (Priority HIGH)

---

### 8. Port Stock / Inventory 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Select port |  |  | **MISSING** |
| Calculate daily stock levels |  |  | **MISSING** |
| Show rail arrivals |  |  | **MISSING** |
| Show sea shipments |  |  | **MISSING** |

**Status:**  **NOT TRANSFERRED**

**Action Items:**
- [ ] **Create PortStockView.vue** (Priority HIGH)

---

### 9. Sales Plan Calculator 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Calculate sales plan |  |  | **MISSING** |
| Required shipments |  |  | **MISSING** |
| Suggested trips |  |  | **MISSING** |
| Capacity gap |  |  | **MISSING** |
| Place volume in trading lanes |  |  | **MISSING** |

**Status:**  **NOT TRANSFERRED**

**Action Items:**
- [ ] **Create SalesPlanView.vue** (Priority MEDIUM)

---

### 10. Network Visualization 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Generate network button |  |  | **Transferred** |
| vis-network integration |  |  | **Transferred** (NetworkVisualization.vue) |
| Export snapshot |  |  | **Needs verification** |

---

### 11. Reports & Export 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| **PDF Reports** |  |  | **MISSING** |
| - Comprehensive PDF |  |  | **MISSING** |
| - Fleet PDF |  |  | **MISSING** |
| - Schedule PDF |  |  | **MISSING** |
| - Financial PDF |  |  | **MISSING** |
| **Excel Exports** | | | |
| - Gantt export |  |  | **Transferred** |
| - Fleet overview |  |  | **Needs verification** |
| - Voyage summary |  |  | **Needs verification** |
| - Scenario comparison |  |  | **MISSING** |
| - DeepSea financial |  |  | **MISSING** |
| - Olya coordination |  |  | **MISSING** |
| - Voyage comparison |  |  | **MISSING** |
| - Port stock timeline |  |  | **MISSING** |
| **Data Import** | | | |
| - Ports.csv |  |  | **Partial** |
| - Routes.csv |  |  | **Partial** |
| - Vessels.csv |  |  | **Partial** |
| - Cargo.csv |  |  | **Partial** |
| - CargoCommitments.csv |  |  | **Partial** |
| - rail_cargo.csv |  |  | **MISSING** |
| - cargo_movements.csv |  |  | **MISSING** |
| - voyage_legs.csv |  |  | **MISSING** |
| **Utilities** | | | |
| - Generate templates |  |  | **MISSING** |
| - Clear all data |  |  | **MISSING** |

**Action Items:**
- [ ] **Implement PDF export functionality** (Priority HIGH)
- [ ] Add all Excel export types
- [ ] Complete CSV import handlers
- [ ] Add template generation
- [ ] Add data clear functionality

---

### 12-24. UI Modules (All in embedded JS)

#### 12. Alerts Dashboard 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Alerts display |  |  | **Needs Vue component** |
| Severity filtering |  |  | **MISSING** |
| Acknowledge/Resolve |  |  | **MISSING** |

#### 13. Berth Management 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Berth dashboard |  |  | **Needs Vue component** |
| Constraints view |  |  | **MISSING** |
| Capacity view |  |  | **MISSING** |
| Conflicts view |  |  | **MISSING** |

#### 14. Bunker Optimization 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Bunker calculator |  |  | **MISSING** |
| Recommended ports |  |  | **MISSING** |
| Fuel type selection |  |  | **MISSING** |

#### 15. Weather Integration 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Weather warnings |  |  | **MISSING** |
| 5-day forecast |  |  | **MISSING** |
| Route risk assessment |  |  | **MISSING** |
| Gantt overlay |  |  | **MISSING** |

#### 16. Vessel Tracking 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Leaflet map integration |  |  | **MISSING** |
| Real-time positions |  |  | **MISSING** |
| Vessel status table |  |  | **MISSING** |
| Auto-refresh |  |  | **MISSING** |

#### 17. Scenario Management 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Create scenarios |  |  | **Partial (store exists)** |
| Load/Edit/Delete |  |  | **MISSING UI** |
| Compare scenarios |  |  | **MISSING** |

#### 18. Voyage Templates 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Template library |  |  | **Partial** |
| Create/Edit/Delete |  |  | **MISSING** |
| Apply template |  |  | **MISSING** |
| Category filtering |  |  | **MISSING** |
| **Cost allocations in templates** |  |  | **MISSING** |

#### 19. Berth Capacity Planning 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Capacity vs Demand chart |  |  | **MISSING** |
| Utilization forecast |  |  | **MISSING** |
| Recommendations |  |  | **MISSING** |
| Optimize allocation |  |  | **MISSING** |

#### 20. Trading Lanes 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Generate trading lanes |  |  | **MISSING** |
| Lane display |  |  | **MISSING** |

#### 21. Vessel-Cargo Assignment 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Assignment table |  |  | **MISSING** |
| Auto-assignment |  |  | **MISSING** |
| Manual assignment |  |  | **MISSING** |

#### 22. Year Schedule Generator 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Start date, period, turnaround factor |  |  | **MISSING** |
| Base plan selection |  |  | **MISSING** |
| Generate annual schedule |  |  | **MISSING** |

#### 23. Operational Calendar 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Month/Week/Year/Timeline views |  |  | **MISSING** |
| Module/Vessel/Status filters |  |  | **MISSING** |
| Search |  |  | **MISSING** |
| Navigation (Prev/Next) |  |  | **MISSING** |
| Statistics sidebar |  |  | **MISSING** |
| Upcoming events |  |  | **MISSING** |
| Event details modal |  |  | **MISSING** |

#### 24. Financial Analysis 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Total costs |  |  | **Transferred** (FinancialView.vue) |
| Time charter costs |  |  | **Needs verification** |
| Bunker costs |  |  | **Needs verification** |
| Port/allocation costs |  |  | **MISSING** |
| **Bunker optimization section** |  |  | **MISSING** |
| **Potential savings** |  |  | **MISSING** |
| **Optimize strategy button** |  |  | **MISSING** |
| Financial details table |  |  | **MISSING** |

---

## Global Features

### Module Selector 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Deepsea/Balakovo/Olya selector |  |  | **Transferred** |
| Switch module function |  |  | **Transferred** |

### Global Filters 

| Feature | Legacy | Vue.js | Status |
|---------|--------|--------|--------|
| Module filter |  |  | **MISSING** |
| Date range (from/to) |  |  | **MISSING** |
| Product filter |  |  | **MISSING** |
| Port filter |  |  | **MISSING** |
| Vessel filter |  |  | **MISSING** |
| Apply/Reset buttons |  |  | **MISSING** |

---

## Priority Summary

###  CRITICAL - Must Transfer Immediately

1. **Voyage Builder** - Core functionality missing
2. **Operational Calendar** - Major feature with complex views
3. **Year Schedule Generator** - Important planning tool
4. **PDF Export** - All report types missing

###  HIGH Priority

5. **Cost Allocations** - Missing in Cargo and Templates
6. **Port Stock Management** - Inventory tracking
7. **Voyage/Scenario Comparison** - Analysis tools
8. **Global Filters Bar** - Top-level filtering
9. **Unified Info Panel** - Dashboard enhancement
10. **Complete Financial Analysis** - Missing bunker optimization section

###  MEDIUM Priority

11. **Sales Plan Calculator**
12. **Trading Lanes**
13. **Vessel-Cargo Assignment**
14. **Weather Integration**
15. **Vessel Tracking with Maps**
16. **Bunker Optimization Calculator**
17. **Berth Capacity Planning**

###  LOW Priority (Nice to Have)

18. **Operation type filters** (checkboxes)
19. **Bulk route selection**
20. **Advanced filtering in lists**
21. **Template generation utility**
22. **Clear all data utility**

---

## Recommendations

### Immediate Actions

1. **Create missing critical views:**
   - VoyageBuilderView.vue
   - OperationalCalendarView.vue
   - YearScheduleView.vue

2. **Enhance existing components:**
   - Add cost allocation fields to CargoForm.vue and template system
   - Extend FinancialView.vue with bunker optimization

3. **Implement global filtering:**
   - Create GlobalFilters.vue component
   - Wire to Pinia stores

4. **Add PDF export:**
   - Install html2pdf or similar
   - Create PDF service
   - Add export buttons to views

### Phase 2 (Post-Critical)

5. Create remaining analysis views (Comparison, Port Stock, Sales Plan)
6. Implement UI modules as Vue components
7. Add map integration for tracking
8. Implement weather overlay

---

## Testing Strategy

For each transferred feature:
1. **Functional Test:** Verify feature works
2. **Data Flow Test:** Confirm API integration
3. **UI/UX Test:** Match or improve on legacy
4. **Edge Case Test:** Handle errors gracefully

---

**Last Updated:** 2025-12-26  
**Status:** Feature analysis complete, migration roadmap defined
