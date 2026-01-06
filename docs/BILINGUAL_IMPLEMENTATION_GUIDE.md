# Bilingual Implementation Guide

**Version:** 1.0  
**Created:** 2025-12-29  
**Purpose:** Step-by-step guide for implementing bilingual support in HTML templates

## Overview

This guide explains how to add English/Russian language switching to the vessel scheduling system's HTML templates using the new i18n service.

---

## Quick Start

### 1. Include the i18n Service

Add this script tag to your HTML file:

```html
<script src="js/services/i18n-service.js"></script>
```

### 2. Add Language Toggle Button

Insert a language toggle in your navigation or header:

```html
<div id="language-toggle-container"></div>

<script>
// After DOM load, create the toggle button
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('language-toggle-container');
    window.i18n.createLanguageToggle(container);
});
</script>
```

### 3. Mark Elements for Translation

Add `data-i18n` attribute to elements that need translation:

```html
<!-- Text content translation -->
<h1 data-i18n="app.title"></h1>
<button data-i18n="app.save"></button>

<!-- Attribute translation (e.g., placeholder) -->
<input type="text" 
       data-i18n="vessel.name" 
       data-i18n-attr="placeholder">
```

### 4. Use Translation Function in JavaScript

```javascript
// Get translated text
const saveLabel = window.t('app.save');

// With parameters
const message = window.t('notify.itemDeleted', { item: 'Vessel ABC' });
```

---

## Detailed Implementation

### Implementing in operational_calendar.html

**Step 1:** Add i18n script reference

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- existing head content -->
    <script src="js/services/i18n-service.js"></script>
</head>
```

**Step 2:** Add language toggle to header

```html
<div class="header">
    <h1 data-i18n="calendar.title"></h1>
    <div class="header-actions">
        <div id="lang-toggle"></div>
        <!-- other header buttons -->
    </div>
</div>
```

**Step 3:** Update button labels

Before:
```html
<button id="addEventBtn">Добавить событие</button>
```

After:
```html
<button id="addEventBtn" data-i18n="calendar.addEvent"></button>
```

**Step 4:** Update notification calls

Before:
```javascript
alert('Событие успешно добавлено');
```

After:
```javascript
alert(window.t('notify.saveSuccess'));
```

**Step 5:** Initialize language toggle

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Create language toggle
    const langContainer = document.getElementById('lang-toggle');
    window.i18n.createLanguageToggle(langContainer);
    
    // Listen for language changes and update DOM
    window.i18n.onLanguageChange(function(newLang) {
        console.log('Language changed to:', newLang);
        window.i18n.updateDOM();
        
        // Update any dynamic content
        refreshDynamicContent();
    });
});
</script>
```

### Implementing in vessel_scheduler_complete.html

Similar approach with additional considerations for complex UI:

**Step 1:** Add i18n service

```html
<script src="js/services/i18n-service.js"></script>
```

**Step 2:** Update all static text

```html
<!-- Navigation -->
<nav>
    <a href="#vessels" data-i18n="nav.vessels"></a>
    <a href="#cargo" data-i18n="nav.cargo"></a>
    <a href="#schedule" data-i18n="nav.schedule"></a>
</nav>

<!-- Form labels -->
<label data-i18n="vessel.name"></label>
<input data-i18n="vessel.name" data-i18n-attr="placeholder">

<!-- Buttons -->
<button data-i18n="app.save"></button>
<button data-i18n="app.cancel"></button>
```

**Step 3:** Update table headers

```html
<thead>
    <tr>
        <th data-i18n="vessel.name"></th>
        <th data-i18n="vessel.type"></th>
        <th data-i18n="vessel.dwt"></th>
        <th data-i18n="vessel.speed"></th>
    </tr>
</thead>
```

**Step 4:** Handle dynamic content

```javascript
function renderVesselTable(vessels) {
    let html = '<table><thead><tr>';
    html += `<th>${window.t('vessel.name')}</th>`;
    html += `<th>${window.t('vessel.type')}</th>`;
    html += `<th>${window.t('vessel.dwt')}</th>`;
    html += '</tr></thead><tbody>';
    
    vessels.forEach(vessel => {
        html += '<tr>';
        html += `<td>${vessel.name}</td>`;
        html += `<td>${vessel.type}</td>`;
        html += `<td>${vessel.dwt}</td>`;
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    return html;
}

// Re-render when language changes
window.i18n.onLanguageChange(() => {
    const vesselTable = document.getElementById('vessel-table');
    if (vesselTable) {
        vesselTable.innerHTML = renderVesselTable(currentVessels);
    }
});
```

---

## Adding New Translations

### 1. Edit i18n-service.js

Add new translation keys to both language dictionaries:

```javascript
const translations = {
    en: {
        // ... existing translations
        'myfeature.title': 'My New Feature',
        'myfeature.button': 'Click Me'
    },
    ru: {
        // ... existing translations
        'myfeature.title': 'Моя новая функция',
        'myfeature.button': 'Нажми меня'
    }
};
```

### 2. Use the new keys

```html
<h2 data-i18n="myfeature.title"></h2>
<button data-i18n="myfeature.button"></button>
```

---

## Best Practices

### 1. Consistent Key Naming

Use hierarchical dot notation:
```
module.element.action
```

Examples:
- `vessel.list.title`
- `cargo.form.save`
- `schedule.gantt.export`

### 2. Avoid Hardcoded Text

 Bad:
```javascript
alert('Data saved successfully');
```

 Good:
```javascript
alert(window.t('notify.saveSuccess'));
```

### 3. Extract Repeated Phrases

If a phrase appears in multiple places, create a reusable key:

```javascript
// translations
en: {
    'common.confirm': 'Confirm',
    'common.delete': 'Delete'
}

// usage everywhere
<button data-i18n="common.confirm"></button>
<button data-i18n="common.delete"></button>
```

### 4. Handle Dynamic Values

For messages with variables, use parameter interpolation:

```javascript
// Add to translations
en: {
    'notify.itemSaved': '{item} saved successfully'
}

// Use with parameters
const message = window.t('notify.itemSaved', { item: vesselName });
```

### 5. Update on Language Change

For dynamically generated content, refresh it when language changes:

```javascript
window.i18n.onLanguageChange(() => {
    // Refresh all dynamic content
    updateGanttChart();
    updateReports();
    updateNotifications();
});
```

---

## Styling the Language Toggle

Add CSS to style the language toggle button:

```css
.language-toggle-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s ease;
}

.language-toggle-btn:hover {
    background: #f5f5f5;
    border-color: #2196F3;
}

.language-toggle-btn .flag {
    font-size: 1.2rem;
}

.language-toggle-btn .lang-code {
    font-weight: 600;
    color: #333;
}
```

---

## Testing Checklist

After implementing bilingual support, verify:

- [ ] Language toggle button appears and functions
- [ ] All static text translates when language changes
- [ ] Dynamic content (tables, lists) updates correctly
- [ ] Form placeholders and labels translate
- [ ] Notifications and alerts show in selected language
- [ ] Language preference persists after page reload
- [ ] No console errors when switching languages
- [ ] Both languages display properly (no encoding issues)
- [ ] Layout doesn't break with longer Russian text

---

## Troubleshooting

### Language doesn't persist after refresh

**Cause:** localStorage not accessible  
**Solution:** Check browser privacy settings, ensure site has localStorage permission

### Some elements don't translate

**Cause:** Elements added dynamically after i18n initialization  
**Solution:** Call `window.i18n.updateDOM()` after adding elements, or use `window.t()` function directly

### Console shows "Unsupported language" warning

**Cause:** Invalid language code in localStorage  
**Solution:** Clear localStorage or set valid code:
```javascript
localStorage.setItem('app_language', 'en'); // or 'ru'
```

### Russian text displays as boxes/question marks

**Cause:** Character encoding issue  
**Solution:** Ensure HTML has UTF-8 encoding:
```html
<meta charset="UTF-8">
```

---

## Migration Path for Existing Templates

### Phase 1: Add i18n Service (Week 1)
1. Include i18n-service.js in all HTML files
2. Add language toggle to main navigation
3. Test basic functionality

### Phase 2: Convert Static Content (Week 2)
1. Replace hardcoded text in HTML with data-i18n attributes
2. Test page by page
3. Fix any layout issues

### Phase 3: Update JavaScript (Week 3)
1. Replace alert/confirm messages with translated versions
2. Update dynamic content generation
3. Add language change listeners

### Phase 4: Testing & Refinement (Week 4)
1. Cross-browser testing
2. User acceptance testing
3. Fix bugs and polish

---

## Example: Complete Bilingual Page

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title data-i18n="app.title"></title>
    <link rel="stylesheet" href="styles.css">
    <script src="js/services/i18n-service.js"></script>
</head>
<body>
    <header>
        <h1 data-i18n="app.title"></h1>
        <div id="language-toggle"></div>
    </header>
    
    <main>
        <section>
            <h2 data-i18n="vessel.list"></h2>
            <button id="addBtn" data-i18n="vessel.add"></button>
            
            <table id="vessel-table">
                <thead>
                    <tr>
                        <th data-i18n="vessel.name"></th>
                        <th data-i18n="vessel.type"></th>
                        <th data-i18n="vessel.dwt"></th>
                    </tr>
                </thead>
                <tbody id="vessel-tbody"></tbody>
            </table>
        </section>
    </main>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize language toggle
            const langContainer = document.getElementById('language-toggle');
            window.i18n.createLanguageToggle(langContainer);
            
            // Handle language changes
            window.i18n.onLanguageChange(function(lang) {
                console.log('Language changed to:', lang);
                loadVessels(); // Reload dynamic content
            });
            
            // Add button handler
            document.getElementById('addBtn').addEventListener('click', function() {
                const confirmMsg = window.t('confirm.addVessel');
                if (confirm(confirmMsg)) {
                    addVessel();
                }
            });
            
            // Initial load
            loadVessels();
        });
        
        function loadVessels() {
            // Load and display vessels with translated headers
            const tbody = document.getElementById('vessel-tbody');
            // ... implementation
        }
    </script>
</body>
</html>
```

---

## Next Steps

1. Review this guide thoroughly
2. Start with one template (operational_calendar.html recommended)
3. Test thoroughly before moving to next template
4. Document any template-specific issues
5. Create pull request for review

For questions or issues, refer to:
- [`js/services/i18n-service.js`](../js/services/i18n-service.js) - Service implementation
- [`docs/TECHNICAL_DEBT_RESOLUTION.md`](TECHNICAL_DEBT_RESOLUTION.md) - Overall project status

---

**Document Status:**  Complete and ready for implementation
