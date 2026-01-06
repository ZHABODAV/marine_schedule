# Developer Guide

Complete guide for developers working on the Vessel Scheduler application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Architecture Overview](#architecture-overview)
5. [Backend Development](#backend-development)
6. [Frontend Development](#frontend-development)
7. [Testing Strategy](#testing-strategy)
8. [API Integration](#api-integration)
9. [Database & Data Models](#database--data-models)
10. [Deployment](#deployment)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

**Required Software:**
- Python 3.8+ 
- Node.js 16+ and npm/yarn
- Git

**Recommended Tools:**
- VS Code with extensions:
  - Volar (Vue Language Features)
  - Python
  - ESLint
  - Prettier
- Postman or similar for API testing

### Initial Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd project
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node Dependencies**
   ```bash
   npm install
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize Database**
   ```bash
   python main.py  # Creates necessary data structures
   ```

### Running the Application

**Development Mode:**

```bash
# Terminal 1: Start Flask API Server
python api_server_enhanced.py

# Terminal 2: Start Vue.js Dev Server
npm run dev
```

**Access Points:**
- Frontend: http://localhost:5173
- API: http://localhost:5000
- API Docs: http://localhost:5000/api/docs

---

## Project Structure

```
project/
├── docs/                    # Documentation
│   ├── API_REFERENCE.md
│   ├── COMPONENT_API.md
│   ├── TESTING_GUIDE.md
│   └── ...
├── src/                     # Vue.js Frontend
│   ├── components/          # Vue components
│   │   ├── cargo/          # Cargo management
│   │   ├── gantt/          # Gantt chart
│   │   ├── shared/         # Reusable components
│   │   ├── vessel/         # Vessel management
│   │   └── route/          # Route management
│   ├── composables/        # Vue composables
│   ├── services/           # API services
│   ├── stores/             # Pinia state stores
│   ├── types/              # TypeScript type definitions
│   ├── router/             # Vue Router config
│   ├── views/              # Page components
│   └── main.ts             # App entry point
├── modules/                 # Python Backend Modules
│   ├── balakovo_*.py       # Balakovo module
│   ├── deepsea_*.py        # Deep Sea module
│   ├── olya_*.py           # Olya module
│   ├── voyage_calculator.py
│   └── ...
├── js/                      # Legacy JavaScript (being migrated)
│   ├── modules/
│   ├── services/
│   └── types/
├── input/                   # Input data files
│   ├── balakovo/
│   ├── deepsea/
│   └── olya/
├── output/                  # Generated outputs
├── tests/                   # Test files
├── api_server_enhanced.py   # Flask API server
├── config.yaml             # Application configuration
├── package.json            # Node dependencies
├── requirements.txt        # Python dependencies
├── vite.config.ts          # Vite configuration
└── tsconfig.json           # TypeScript configuration
```

### Module Organization

The application is organized into three main calculation modules:

1. **Balakovo Module** - River shipping optimization
2. **Deepsea Module** - Ocean vessel routing  
3. **Olya Module** - Specialized route calculations

Each module follows a consistent pattern:
- `*_data.py` - Data loading and validation
- `*_calculator.py` - Core calculation logic
- `*_loader.py` - Input file processing
- `*_gantt.py` - Gantt chart generation

---

## Development Workflow

### Branch Strategy

```
main           # Production-ready code
├── develop    # Integration branch
│   ├── feature/component-api
│   ├── feature/route-optimization
│   ├── bugfix/gantt-display
│   └── hotfix/calculation-error
```

**Branch Naming:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical production fixes
- `refactor/` - Code refactoring

### Commit Message Convention

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```bash
git commit -m "feat(cargo): add cargo validation form"
git commit -m "fix(gantt): resolve timeline calculation error"
git commit -m "docs(api): update endpoint documentation"
```

### Code Review Process

1. Create feature branch from `develop`
2. Implement changes with tests
3. Run linters and tests locally
4. Push and create Pull Request
5. Address review comments
6. Merge after approval

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────┐
│         Vue.js Frontend (SPA)            │
│  ┌────────────┐  ┌─────────────────┐   │
│  │ Components │  │ Pinia Stores    │   │
│  └────────────┘  └─────────────────┘   │
│  ┌────────────┐  ┌─────────────────┐   │
│  │ Services   │  │ Router/Views    │   │
│  └────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
               │ HTTP/REST API
               ▼
┌─────────────────────────────────────────┐
│         Flask API Server                 │
│  ┌────────────────────────────────────┐ │
│  │  API Routes & Endpoints            │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  Business Logic Modules            │ │
│  │  - Balakovo  - Deepsea  - Olya    │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Data Layer                       │
│  CSV Files / Excel / JSON               │
└─────────────────────────────────────────┘
```

### Design Patterns

**Frontend:**
- **Composition API**: For reactive component logic
- **State Management**: Centralized with Pinia
- **Service Layer**: Separation of API logic
- **Component Composition**: Reusable base components

**Backend:**
- **Module Pattern**: Functional modules for calculations
- **Service Layer**: Business logic separation
- **Data Access Layer**: File I/O abstraction
- **Factory Pattern**: Object creation for voyages

---

## Backend Development

### Python Module Structure

**Example Module Structure:**

```python
# modules/example_calculator.py

from typing import List, Dict, Optional
from dataclasses import dataclass
import pandas as pd

@dataclass
class VoyageResult:
    """Voyage calculation result"""
    vessel_id: str
    total_time: float
    distance_nm: float
    bunker_mt: float

class ExampleCalculator:
    """Calculator for specific voyage type"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.vessels = []
        
    def load_data(self, path: str) -> None:
        """Load input data from file"""
        df = pd.read_csv(path)
        self.vessels = df.to_dict('records')
        
    def calculate_voyage(self, vessel: Dict, route: Dict) -> VoyageResult:
        """
        Calculate voyage parameters
        
        Args:
            vessel: Vessel specifications
            route: Route information
            
        Returns:
            VoyageResult with calculation results
        """
        # Implementation
        pass
        
    def optimize_schedule(self) -> List[VoyageResult]:
        """Generate optimized schedule"""
        results = []
        for vessel in self.vessels:
            result = self.calculate_voyage(vessel, {})
            results.append(result)
        return results
```

### Creating New API Endpoints

**Add to [`api_server_enhanced.py`](../api_server_enhanced.py):**

```python
@app.route('/api/v1/example/calculate', methods=['POST'])
def calculate_example():
    """
    Calculate example voyage
    
    Request Body:
        {
            "vessel_id": str,
            "route": object
        }
        
    Returns:
        {
            "success": bool,
            "data": object,
            "message": str
        }
    """
    try:
        data = request.json
        
        # Validation
        if not data or 'vessel_id' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
            
        # Calculation
        calculator = ExampleCalculator(config)
        result = calculator.calculate_voyage(
            data['vessel_id'],
            data.get('route', {})
        )
        
        return jsonify({
            'success': True,
            'data': asdict(result)
        })
        
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
```

### Configuration Management

Edit [`config.yaml`](../config.yaml):

```yaml
# Application Configuration
app:
  name: "Vessel Scheduler"
  version: "2.0.0"
  debug: false

# Module Settings
balakovo:
  default_speed: 12.0
  bunker_consumption: 2.5
  
deepsea:
  default_speed: 14.0
  canal_waiting_time: 24.0

# File Paths
paths:
  input: "./input"
  output: "./output"
  logs: "./logs"
```

**Loading Configuration:**

```python
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

---

## Frontend Development

### Component Development

**Component Template:**

```vue
<template>
  <div class="my-component">
    <h2>{{ title }}</h2>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Props
interface Props {
  title: string
  data?: any[]
}

const props = withDefaults(defineProps<Props>(), {
  data: () => []
})

// Emits
const emit = defineEmits<{
  update: [value: string]
  delete: [id: number]
}>()

// State
const isLoading = ref(false)

// Computed
const itemCount = computed(() => props.data.length)

// Methods
const handleUpdate = (value: string) => {
  emit('update', value)
}

// Lifecycle
onMounted(() => {
  console.log('Component mounted')
})
</script>

<style scoped>
.my-component {
  padding: 1rem;
}
</style>
```

### State Management with Pinia

**Creating a Store:**

```typescript
// src/stores/example.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Example } from '@/types/example.types'

export const useExampleStore = defineStore('example', () => {
  // State
  const items = ref<Example[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const itemCount = computed(() => items.value.length)
  const hasItems = computed(() => items.value.length > 0)

  // Actions
  async function fetchItems() {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch('/api/v1/examples')
      const data = await response.json()
      items.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  function addItem(item: Example) {
    items.value.push(item)
  }

  function removeItem(id: string) {
    const index = items.value.findIndex(i => i.id === id)
    if (index > -1) {
      items.value.splice(index, 1)
    }
  }

  return {
    // State
    items,
    loading,
    error,
    // Getters
    itemCount,
    hasItems,
    // Actions
    fetchItems,
    addItem,
    removeItem
  }
})
```

**Using the Store:**

```vue
<script setup lang="ts">
import { useExampleStore } from '@/stores/example'

const store = useExampleStore()

// Access state
console.log(store.items)

// Call actions
store.fetchItems()
</script>
```

### API Service Layer

**Creating an API Service:**

```typescript
// src/services/example.service.ts
import { apiClient } from './api'
import type { Example, ExampleFormData } from '@/types/example.types'

export const exampleService = {
  async getAll(): Promise<Example[]> {
    const response = await apiClient.get('/api/v1/examples')
    return response.data
  },

  async getById(id: string): Promise<Example> {
    const response = await apiClient.get(`/api/v1/examples/${id}`)
    return response.data
  },

  async create(data: ExampleFormData): Promise<Example> {
    const response = await apiClient.post('/api/v1/examples', data)
    return response.data
  },

  async update(id: string, data: Partial<ExampleFormData>): Promise<Example> {
    const response = await apiClient.put(`/api/v1/examples/${id}`, data)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/examples/${id}`)
  }
}
```

### TypeScript Type Definitions

```typescript
// src/types/example.types.ts

export interface Example {
  id: string
  name: string
  description: string
  status: 'active' | 'inactive'
  createdAt: string
  updatedAt: string
}

export interface ExampleFormData {
  name: string
  description: string
  status: 'active' | 'inactive'
}

export type ExampleStatus = Example['status']
```

---

## Testing Strategy

### Unit Testing (Python)

```python
# tests/test_calculator.py
import pytest
from modules.voyage_calculator import VoyageCalculator

class TestVoyageCalculator:
    @pytest.fixture
    def calculator(self):
        return VoyageCalculator(config={})
        
    def test_distance_calculation(self, calculator):
        distance = calculator.calculate_distance(
            from_port="Port A",
            to_port="Port B"
        )
        assert distance > 0
        
    def test_time_calculation(self, calculator):
        time = calculator.calculate_time(
            distance=100,
            speed=10
        )
        assert time == 10
```

### Component Testing (Vue)

```typescript
// src/components/shared/__tests__/BaseButton.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '../BaseButton.vue'

describe('BaseButton', () => {
  it('renders properly', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'primary' },
      slots: { default: 'Click me' }
    })
    expect(wrapper.text()).toContain('Click me')
  })

  it('emits click event', async () => {
    const wrapper = mount(BaseButton)
    await wrapper.trigger('click')
    expect(wrapper.emitted()).toHaveProperty('click')
  })

  it('does not emit when disabled', async () => {
    const wrapper = mount(BaseButton, {
      props: { disabled: true }
    })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeUndefined()
  })
})
```

### E2E Testing

```typescript
// e2e/voyage-workflow.spec.ts
import { test, expect } from '@playwright/test'

test('complete voyage creation workflow', async ({ page }) => {
  await page.goto('http://localhost:5173')
  
  // Navigate to voyage builder
  await page.click('text=Voyage Builder')
  
  // Fill form
  await page.fill('#vessel-id', 'VESSEL-001')
  await page.fill('#load-port', 'Port A')
  await page.fill('#discharge-port', 'Port B')
  
  // Submit
  await page.click('button:has-text("Calculate")')
  
  // Verify result
  await expect(page.locator('.result-card')).toBeVisible()
})
```

**Run Tests:**

```bash
# Python tests
pytest

# Vue component tests
npm run test:unit

# E2E tests
npm run test:e2e
```

---

## API Integration

See [`API_REFERENCE.md`](./API_REFERENCE.md) for detailed endpoint documentation.

### API Client Configuration

```typescript
// src/services/api.ts
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

---

## Database & Data Models

### Data Storage

The application currently uses file-based storage:

- **CSV Files**: Primary data input format
- **Excel Files**: Output reports and schedules
- **JSON Files**: Configuration and templates
- **JSONL**: Audit logs

### Data Models

See type definitions in:
- [`src/types/`](../src/types/) - TypeScript types
- [`modules/`](../modules/) - Python dataclasses

---

## Deployment

### Production Build

```bash
# Build frontend
npm run build

# Test production build locally
npm run preview
```

### Environment Variables

Create `.env.production`:

```bash
VITE_API_URL=https://api.production.com
VITE_APP_ENV=production
```

### Deployment Checklist

- [ ] Run all tests
- [ ] Update version in `package.json`
- [ ] Build production assets
- [ ] Configure environment variables
- [ ] Set up logging
- [ ] Configure error monitoring
- [ ] Set up backups
- [ ] Security audit
- [ ] Performance testing
- [ ] Documentation up to date

---

## Best Practices

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Docstrings for all public functions

**TypeScript/Vue:**
- Use ESLint + Prettier
- Prefer `const` over `let`
- Use strict TypeScript mode
- Component names in PascalCase

### Performance

**Frontend:**
- Lazy load routes and components
- Use computed properties for derived state
- Debounce user inputs
- Optimize bundle size

**Backend:**
- Cache expensive calculations
- Use generators for large datasets
- Profile performance bottlenecks
- Optimize database queries

### Security

- Validate all inputs
- Sanitize user data
- Use HTTPS in production
- Implement CSRF protection
- Keep dependencies updated
- Regular security audits

---

## Troubleshooting

### Common Issues

**Frontend Dev Server Not Starting:**
```bash
# Clear cache
rm -rf node_modules .vite
npm install
npm run dev
```

**API Server Errors:**
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Build Failures:**
```bash
# TypeScript errors
npm run type-check

# Clear build cache
rm -rf dist
npm run build
```

### Debug Mode

Enable debug logging:

```python
# Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

```typescript
// Vue
if (import.meta.env.DEV) {
  console.log('Debug info:', data)
}
```

---

## Additional Resources

- [Component API Documentation](./COMPONENT_API.md)
- [API Reference](./API_REFERENCE.md)
- [Testing Guide](./TESTING_GUIDE.md)
- [User Documentation](../РУКОВОДСТВО_ПОЛЬЗОВАТЕЛЯ.md)
- [Vue.js Documentation](https://vuejs.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

## Contributing

1. Fork the repository
2. Create your feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

## Support

For questions or issues:
- Check documentation first
- Search existing issues
- Create new issue with detailed description

---

**Last Updated:** 2025-12-26
**Version:** 2.0.0
