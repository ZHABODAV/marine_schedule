# Vessel Scheduler Enhanced - UI Enhancement Integration Guide

This guide explains how to integrate the 4 major UI enhancements into [`vessel_scheduler_enhanced.html`](../vessel_scheduler_enhanced.html) and [`vessel_scheduler_enhanced.js`](../vessel_scheduler_enhanced.js).

## Overview

**Enhancement Files Created:**
1. [`vessel_scheduler_html_additions.html`](vessel_scheduler_html_additions.html) - HTML snippets to add
2. [`vessel_scheduler_js_additions.js`](vessel_scheduler_js_additions.js) - JavaScript functions to add
3. [`vessel_scheduler_css_additions.css`](vessel_scheduler_css_additions.css) - Additional CSS styles

## Features Being Added

1. **Voyage Planner Tab** - Offline voyage calculation with Excel file uploads
2. **Enhanced Gantt Styling** - Maritime-themed Gantt charts matching voyage_planner_ru.html
3. **Voyage Builder Enhancements** - Standard route legs loading and preview
4. **PDF Export UI** - Complete PDF report generation interface

---

## Integration Steps

### Step 1: Add CSS Styles

**Location:** [`vessel_scheduler_enhanced.html`](../vessel_scheduler_enhanced.html) around line 809 (inside `</style>` tag, before closing)

**Action:** Copy all CSS from [`vessel_scheduler_css_additions.css`](vessel_scheduler_css_additions.css) and paste before the closing `</style>` tag.

---

### Step 2: Add New Navigation Tab

**Location:** [`vessel_scheduler_enhanced.html`](../vessel_scheduler_enhanced.html) line 882 (in `<nav class="nav-tabs">`)

**Action:** Add this new tab button after the "network" tab:

```html
<button class="tab-button" data-tab="voyagePlanner">Планировщик Рейсов</button>
```

---

### Step 3: Add Voyage Planner Tab Content

**Location:** [`vessel_scheduler_enhanced.html`](../vessel_scheduler_enhanced.html) line 1259 (before `</main>` closing tag)

**Action:** Copy the entire "Voyage Planner Tab" section from [`vessel_scheduler_html_additions.html`](vessel_scheduler_html_additions.html) Section 1.

---

### Step 4: Update Voyage Builder Tab

**Location:** [`vessel_scheduler_enhanced.html`](../vessel_scheduler_enhanced.html) lines 1060-1077 (existing Voyage Builder tab)

**Action:** Replace the entire Voyage Builder tab content with Section 2 from [`vessel_scheduler_html_additions.html`](vessel_scheduler_html_additions.html).

---

### Step 5: Update Schedule Tab Gantt Display

**Location:** [`vessel_scheduler_enhanced.html`](../vessel_scheduler_enhanced.html) line 1050 (inside `<div id="scheduleContent">`)

**Action:** Replace the `<div id="scheduleContent">` inner HTML with Section 3 from [`vessel_scheduler_html_additions.html`](vessel_scheduler_html_additions.html).

---

### Step 6: Add PDF Export Panel to Reports Tab

**Location:** [`vessel_scheduler_enhanced.html`](../vessel_scheduler_enhanced.html) line 1211 (after the last report card in Reports tab)

**Action:** Add Section 4 from [`vessel_scheduler_html_additions.html`](vessel_scheduler_html_additions.html) before the "Импорт данных" section.

---

### Step 7: Add JavaScript Functions

**Location:** [`vessel_scheduler_enhanced.js`](../vessel_scheduler_enhanced.js) - End of file (before closing script tag if inline, or end of file if external)

**Action:** Copy ALL JavaScript code from [`vessel_scheduler_js_additions.js`](vessel_scheduler_js_additions.js) and append to the end of the file.

---

### Step 8: Update appState Object

**Location:** [`vessel_scheduler_enhanced.js`](../vessel_scheduler_enhanced.js) - Find the `appState` object (likely near the top)

**Action:** Add these new properties to the `appState` object:

```javascript
appState.voyagePlannerData = {
    ports: null,
    fleet: null,
    templates: null,
    templateLegs: null,
    voyages: null,
    constraints: null,
    calculatedLegs: null,
    alerts: null
};
appState.standardLegs = null;
appState.currentVoyageLegs = [];
appState.pdfExportConfig = {
    module: 'deepsea',
    startDate: null,
    endDate: null,
    selectedVoyages: []
};
```

---

## Testing Checklist

After integration, test each feature:

- [ ] **Voyage Planner Tab**
  - [ ] Click "Планировщик Рейсов" tab - it should display
  - [ ] Upload Excel files (ports, fleet, templates, voyages, constraints)
  - [ ] Click "Generate Test Data" - sample data should load
  - [ ] Click "Calculate Voyages" - results should display with metrics
  - [ ] Verify Gantt chart renders with color-coded bars
  
- [ ] **Enhanced Gantt**
  - [ ] Go to Schedule tab
  - [ ] Generate schedule for any module
  - [ ] Verify Gantt uses maritime color scheme (green=loading, cyan=discharge, blue=sea, etc.)
  - [ ] Check timeline bars have proper width based on duration
  - [ ] Verify legend displays operation types

- [ ] **Voyage Builder Enhancements**
  - [ ] Go to Voyage Builder tab
  - [ ] Click "Load Standard Legs" button
  - [ ] Verify legs catalog displays with routes
  - [ ] Click "Insert" on a leg - it should add to voyage
  - [ ] Verify total distance calculates
  - [ ] Test validation - try adding disconnected legs

- [ ] **PDF Export**
  - [ ] Go to Reports tab
  - [ ] Find "PDF Voyage Report" card
  - [ ] Select module, date range, voyages
  - [ ] Click "Generate PDF Report"
  - [ ] Verify file downloads

---

## Troubleshooting

### Problem: Tabs don't switch properly

**Solution:** Ensure tab switching JavaScript is working. Check browser console for errors.

### Problem: Voyage Planner calculations fail

**Solution:** Verify Excel file format matches expected structure (see voyage_planner_ru.html for schema).

### Problem: Gantt chart doesn't render

**Solution:** Check that `/api/gantt-data` endpoint returns proper format: `{ "assets": { "vessel_name": [legs] } }`

### Problem: PDF export fails

**Solution:** Verify `/api/export/pdf` endpoint is implemented in api_server.py (currently may need implementation).

---

## API Endpoint Requirements

These enhancements require the following API endpoints to be implemented:

### Already Implemented (in api_server.py):

-  `POST /api/calculate` - Voyage calculation
-  `GET /api/gantt-data` - Gantt chart data
-  `POST /api/upload/<type>` - File uploads

### Needs Implementation:

-  `GET /api/routes/legs` - Standard route legs catalog
-  `POST /api/export/pdf` - PDF report generation
-  `POST /api/voyage/validate` - Voyage leg validation

If these endpoints are missing, create stubs that return sample data or implement them in [`api_server.py`](../api_server.py).

---

## File Structure After Integration

```
project/
├── docs/
│   ├── UI_ENHANCEMENT_GUIDE.md (this file)
│   ├── vessel_scheduler_html_additions.html
│   ├── vessel_scheduler_js_additions.js
│   └── vessel_scheduler_css_additions.css
├── vessel_scheduler_enhanced.html (MODIFIED)
├── vessel_scheduler_enhanced.js (MODIFIED)
└── api_server.py (may need new endpoints)
```

---

## Maintenance Notes

- All Russian UI text is intentional for user-facing labels
- Code comments and variable names remain in English per project rules
- Functions follow existing naming conventions
- Color scheme matches voyage_planner_ru.html maritime theme
- Excel file parsing uses SheetJS library (already included)

---

## Support

If integration issues arise:
1. Check browser console for JavaScript errors
2. Verify all API endpoints are responding
3. Ensure Excel file formats match expected schemas
4. Review network tab in browser dev tools for failed requests

---

**Last Updated:** 2025-12-18  
**Version:** 1.0  
**Compatibility:** vessel_scheduler_enhanced v3.0.0+
