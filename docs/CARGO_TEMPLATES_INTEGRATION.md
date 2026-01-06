# Cargo Templates Integration Guide

**Created**: 2025-12-29  
**Status**:  Ready for Integration

## Overview

The cargo template system allows users to create reusable cargo commitment templates with predefined cost allocations, making cargo data entry faster and more consistent.

## Components Created

### Frontend Components

1. **[`src/components/cargo/CargoTemplateForm.vue`](../src/components/cargo/CargoTemplateForm.vue)**
   - Create/edit cargo templates
   - Integrates with CostAllocationFields
   - Supports default template flagging

2. **[`src/components/cargo/CargoTemplateList.vue`](../src/components/cargo/CargoTemplateList.vue)**
   - Display all templates in grid layout
   - Edit/Delete/Apply actions
   - Default template badge

3. **Type Definitions** ([`src/types/cargo.types.ts`](../src/types/cargo.types.ts))
   ```typescript
   export interface CargoTemplate {
     id: string
     name: string
     description?: string
     commodity: string
     quantity?: number
     loadPort?: string
     dischPort?: string
     freightRate?: number
     operationalCost?: number
     overheadCost?: number
     otherCost?: number
     isDefault?: boolean
     createdAt?: string | Date
     updatedAt?: string | Date
   }
   
   export interface CargoTemplateFormData {
     // Form data structure for creation/editing
   }
   ```

### Backend Modules

1. **[`modules/cargo_template_manager.py`](../modules/cargo_template_manager.py)**
   - CargoTemplateManager class
   - CRUD operations for templates
   - JSON file storage (`data/cargo_templates.json`)
   - Template application logic

2. **[`modules/cargo_template_api.py`](../modules/cargo_template_api.py)** 
   - REST API endpoint registration
   - Request validation
   - Auth integration support

## API Endpoints

All endpoints are prefixed with `/api/cargo-templates`

### GET /api/cargo-templates
Get all cargo templates.

**Response**:
```json
{
  "templates": [
    {
      "id": "tpl_20251229070000_0",
      "name": "Standard Container Cargo",
      "description": "Standard 20ft container shipment",
      "commodity": "General Cargo",
      "quantity": 500,
      "loadPort": "Shanghai",
      "dischPort": "Rotterdam",
      "freightRate": 45.50,
      "operationalCost": 12000,
      "overheadCost": 3000,
      "otherCost": 500,
      "isDefault": true,
      "createdAt": "2025-12-29T07:00:00.000Z",
      "updatedAt": "2025-12-29T07:00:00.000Z"
    }
  ],
  "total": 1
}
```

### GET /api/cargo-templates/default
Get the default template (if any).

**Response**:
```json
{
  "template": { /* template object */ }
}
```

**Error (404)**:
```json
{
  "error": "No default template set"
}
```

### GET /api/cargo-templates/:id
Get a specific template.

**Response**:
```json
{
  "template": { /* template object */ }
}
```

### POST /api/cargo-templates
Create a new template.

**Request Body**:
```json
{
  "name": "Standard Container Cargo",
  "description": "Standard 20ft container shipment",
  "commodity": "General Cargo",
  "quantity": 500,
  "loadPort": "Shanghai",
  "dischPort": "Rotterdam",
  "freightRate": 45.50,
  "operationalCost": 12000,
  "overheadCost": 3000,
  "otherCost": 500,
  "isDefault": false
}
```

**Response (201)**:
```json
{
  "success": true,
  "template": { /* created template with generated ID */ },
  "message": "Template created successfully"
}
```

### PUT /api/cargo-templates/:id
Update an existing template.

**Request Body**: Same as POST

**Response**:
```json
{
  "success": true,
  "template": { /* updated template */ },
  "message": "Template updated successfully"
}
```

### DELETE /api/cargo-templates/:id
Delete a template.

**Response**:
```json
{
  "success": true,
  "message": "Template tpl_xxx deleted successfully"
}
```

### POST /api/cargo-templates/:id/apply
Apply a template to create cargo commitment data.

**Request Body (optional)**:
```json
{
  "quantity": 750,
  "laycanStart": "2025-01-15",
  "laycanEnd": "2025-01-20"
}
```

**Response**:
```json
{
  "success": true,
  "cargo": {
    "commodity": "General Cargo",
    "quantity": 750,
    "loadPort": "Shanghai",
    "dischPort": "Rotterdam",
    "freightRate": 45.50,
    "operationalCost": 12000,
    "overheadCost": 3000,
    "otherCost": 500
  },
  "message": "Template applied successfully"
}
```

## Integration Steps

### 1. Register API Endpoints

Add to [`api_extensions_hardened.py`](../api_extensions_hardened.py):

```python
# At the top, add import
from modules.cargo_template_api import register_cargo_template_endpoints

# In register_ui_module_endpoints function, add:
def register_ui_module_endpoints(app):
    # ... existing code ...
    
    # Register cargo template endpoints
    register_cargo_template_endpoints(app, require_auth)
    
    logger.info("[OK] All API endpoints registered")
```

### 2. Add Template Management View (Optional)

Create [`src/views/CargoTemplatesView.vue`](../src/views):

```vue
<template>
  <div class="cargo-templates-view">
    <CargoTemplateList
      :templates="templates"
      :loading="loading"
      :error="error"
      @create="showCreateForm = true"
      @edit="handleEdit"
      @delete="handleDelete"
      @apply="handleApply"
      @retry="loadTemplates"
    />
    
    <CargoTemplateForm
      :show="showCreateForm || editingTemplate !== null"
      :template="editingTemplate"
      :submitting="submitting"
      @close="handleCloseForm"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import CargoTemplateList from '@/components/cargo/CargoTemplateList.vue';
import CargoTemplateForm from '@/components/cargo/CargoTemplateForm.vue';
import type { CargoTemplate, CargoTemplateFormData } from '@/types/cargo.types';

const templates = ref<CargoTemplate[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const showCreateForm = ref(false);
const editingTemplate = ref<CargoTemplate | null>(null);
const submitting = ref(false);

async function loadTemplates() {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetch('/api/cargo-templates');
    const data = await response.json();
    templates.value = data.templates || [];
  } catch (e: any) {
    error.value = e.message || 'Failed to load templates';
  } finally {
    loading.value = false;
  }
}

async function handleSubmit(formData: CargoTemplateFormData) {
  submitting.value = true;
  try {
    const url = editingTemplate.value
      ? `/api/cargo-templates/${editingTemplate.value.id}`
      : '/api/cargo-templates';
    const method = editingTemplate.value ? 'PUT' : 'POST';
    
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) throw new Error('Failed to save template');
    
    await loadTemplates();
    handleCloseForm();
  } catch (e: any) {
    error.value = e.message;
  } finally {
    submitting.value = false;
  }
}

function handleEdit(template: CargoTemplate) {
  editingTemplate.value = template;
}

async function handleDelete(template: CargoTemplate) {
  if (!confirm(`Delete template "${template.name}"?`)) return;
  
  try {
    const response = await fetch(`/api/cargo-templates/${template.id}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete');
    await loadTemplates();
  } catch (e: any) {
    error.value = e.message;
  }
}

async function handleApply(template: CargoTemplate) {
  // Navigate to cargo form with template data
  console.log('Apply template:', template);
}

function handleCloseForm() {
  showCreateForm.value = false;
  editingTemplate.value = null;
}

onMounted(() => {
  loadTemplates();
});
</script>
```

### 3. Add Route (Optional)

In [`src/router/index.ts`](../src/router/index.ts):

```typescript
{
  path: '/cargo-templates',
  name: 'cargo-templates',
  component: () => import('@/views/CargoTemplatesView.vue'),
  meta: {
    title: 'Cargo Templates',
    requiresAuth: true
  }
}
```

### 4. Update Cargo Form to Support Templates

In [`src/components/cargo/CargoForm.vue`](../src/components/cargo/CargoForm.vue), add template selector:

```vue
<div class="form-group">
  <label>Apply Template (Optional)</label>
  <select v-model="selectedTemplateId" @change="applyTemplate">
    <option value="">-- No Template --</option>
    <option v-for="tpl in templates" :key="tpl.id" :value="tpl.id">
      {{ tpl.name }}
    </option>
  </select>
</div>
```

## Testing

### Manual Testing

1. **Create Template**:
   ```bash
   curl -X POST http://localhost:5000/api/cargo-templates \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Template",
       "commodity": "Steel",
       "operationalCost": 10000,
       "overheadCost": 2000,
       "otherCost": 500,
       "isDefault": true
     }'
   ```

2. **Get All Templates**:
   ```bash
   curl http://localhost:5000/api/cargo-templates
   ```

3. **Apply Template**:
   ```bash
   curl -X POST http://localhost:5000/api/cargo-templates/tpl_xxx/apply
   ```

### Automated Testing

Create [`tests/test_cargo_templates.py`](../tests):

```python
import pytest
from modules.cargo_template_manager import CargoTemplateManager

def test_create_template():
    manager = CargoTemplateManager('test_templates.json')
    template = manager.create({
        'name': 'Test Template',
        'commodity': 'Test Commodity',
        'operationalCost': 1000
    })
    assert template['id'] is not None
    assert template['name'] == 'Test Template'

def test_get_default_template():
    manager = CargoTemplateManager('test_templates.json')
    # Create default template
    manager.create({
        'name': 'Default',
        'commodity': 'Test',
        'isDefault': True
    })
    default = manager.get_default()
    assert default is not None
    assert default['isDefault'] is True
```

## Storage

Templates are stored in **`data/cargo_templates.json`**:

```json
{
  "tpl_20251229070000_0": {
    "id": "tpl_20251229070000_0",
    "name": "Standard Container Cargo",
    "commodity": "General Cargo",
    "operationalCost": 12000,
    "overheadCost": 3000,
    "otherCost": 500,
    "isDefault": true,
    "createdAt": "2025-12-29T07:00:00.000Z",
    "updatedAt": "2025-12-29T07:00:00.000Z"
  }
}
```

## Security Considerations

- API endpoints support optional authentication via `require_auth` decorator
- Input validation via `CargoTemplateSchema`
- File permissions checked on storage directory
- No SQL injection risk (JSON file storage)

## Next Steps

1. **Import cargo template API** into main server
2. **Test CRUD operations** with real data
3. **Integrate template selector** into cargo form
4. **Add template management** to navigation menu (optional)
5. **Create user documentation** with screenshots

## Related Files

- [`src/components/cargo/CargoTemplateForm.vue`](../src/components/cargo/CargoTemplateForm.vue)
- [`src/components/cargo/CargoTemplateList.vue`](../src/components/cargo/CargoTemplateList.vue)
- [`src/components/cargo/CostAllocationFields.vue`](../src/components/cargo/CostAllocationFields.vue)
- [`src/components/cargo/CargoForm.vue`](../src/components/cargo/CargoForm.vue)
- [`src/types/cargo.types.ts`](../src/types/cargo.types.ts)
- [`modules/cargo_template_manager.py`](../modules/cargo_template_manager.py)
- [`modules/cargo_template_api.py`](../modules/cargo_template_api.py)
- [`api_extensions_hardened.py`](../api_extensions_hardened.py)
