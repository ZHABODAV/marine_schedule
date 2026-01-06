# Developer Guide

**Version:** 2.0.0  
**Last Updated:** January 2026

## 1. Introduction

This document serves as a comprehensive guide for developers working on the Vessel Scheduler application. It covers the system architecture, development workflow, backend and frontend implementation details, and testing strategies.

## 2. Getting Started

### 2.1 Prerequisites

**Required Software:**
*   **Python**: Version 3.8 or higher
*   **Node.js**: Version 16 or higher (with npm/yarn)
*   **Git**: Version control system

**Recommended Tools:**
*   **VS Code**: Integrated Development Environment
    *   Extensions: Volar (Vue), Python, ESLint, Prettier
*   **Postman**: API testing tool

### 2.2 Initial Setup

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd project
    ```

2.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Node Dependencies**:
    ```bash
    npm install
    ```

4.  **Environment Configuration**:
    ```bash
    cp .env.example .env
    # Configure .env with local settings
    ```

5.  **Initialize Database**:
    ```bash
    python main.py  # Initializes data structures
    ```

### 2.3 Running the Application

**Development Mode**:

1.  **Start Flask API Server** (Terminal 1):
    ```bash
    python api_server_enhanced.py
    ```

2.  **Start Vue.js Dev Server** (Terminal 2):
    ```bash
    npm run dev
    ```

**Access Points**:
*   **Frontend**: `http://localhost:5173`
*   **API**: `http://localhost:5000`
*   **API Documentation**: `http://localhost:5000/api/docs`

## 3. Project Structure

The project follows a modular structure separating frontend, backend, and documentation.

```text
project/
├── docs/                    # Documentation
├── src/                     # Vue.js Frontend Source
│   ├── components/          # Vue components (Atomic design)
│   ├── composables/         # Shared logic (Composition API)
│   ├── services/            # API communication layer
│   ├── stores/              # State management (Pinia)
│   ├── types/               # TypeScript definitions
│   ├── views/               # Page-level components
│   └── main.ts              # Application entry point
├── modules/                 # Python Backend Modules
│   ├── balakovo_*.py        # Balakovo specific logic
│   ├── deepsea_*.py         # Deep Sea specific logic
│   ├── olya_*.py            # Olya specific logic
│   └── voyage_calculator.py # Core calculation engine
├── input/                   # Data input directory
├── output/                  # Generated reports and schedules
├── tests/                   # Test suite
├── api_server_enhanced.py   # Main Flask application
└── config.yaml              # System configuration
```

### 3.1 Module Organization

The backend logic is divided into three primary calculation modules:

1.  **Balakovo Module**: Optimizes river shipping operations.
2.  **Deepsea Module**: Manages ocean vessel routing and scheduling.
3.  **Olya Module**: Handles specialized regional route calculations.

Each module adheres to a consistent file naming convention:
*   `*_data.py`: Data validation and loading.
*   `*_calculator.py`: Core algorithms and business logic.
*   `*_loader.py`: Input file processing.
*   `*_gantt.py`: Visualization data generation.

## 4. Architecture Overview

### 4.1 System Architecture

The application utilizes a decoupled client-server architecture:

*   **Frontend**: Single Page Application (SPA) built with Vue.js 3.
*   **Backend**: RESTful API built with Flask (Python).
*   **Data Layer**: File-based storage (CSV/JSON) for portability.

```text
[Vue.js Frontend] <--> [HTTP/REST API] <--> [Flask Server] <--> [Data Layer]
```

### 4.2 Design Patterns

**Frontend**:
*   **Composition API**: For reusable and organized component logic.
*   **Store Pattern**: Centralized state management using Pinia.
*   **Service Layer**: Abstraction of API calls to separate data fetching from UI.

**Backend**:
*   **Module Pattern**: Encapsulation of domain-specific logic.
*   **Factory Pattern**: Dynamic creation of voyage objects based on parameters.
*   **Data Access Object (DAO)**: Abstraction of file I/O operations.

## 5. Backend Development

### 5.1 Python Module Implementation

New calculation modules should implement the standard interface.

**Example Structure**:
```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class VoyageResult:
    vessel_id: str
    total_time: float
    # ... other fields

class ExampleCalculator:
    def __init__(self, config: Dict):
        self.config = config

    def calculate_voyage(self, vessel: Dict, route: Dict) -> VoyageResult:
        # Implementation logic
        pass
```

### 5.2 Creating API Endpoints

Endpoints are defined in `api_server_enhanced.py`.

```python
@app.route('/api/v1/resource', methods=['POST'])
def create_resource():
    try:
        data = request.json
        # Validation logic
        # Business logic
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
```

### 5.3 Configuration

System settings are managed in `config.yaml`. Use the `yaml` library to load configuration at runtime.

## 6. Frontend Development

### 6.1 Component Guidelines

*   Use **Single File Components (SFC)** (`.vue`).
*   Employ `<script setup lang="ts">` for concise syntax.
*   Define props and emits using TypeScript interfaces.
*   Scoped styles are mandatory.

### 6.2 State Management (Pinia)

Stores should be modular and focused on specific domains (e.g., `useVesselStore`, `useCargoStore`).

```typescript
export const useExampleStore = defineStore('example', () => {
  const items = ref([]);
  const fetchItems = async () => { /* ... */ };
  return { items, fetchItems };
});
```

### 6.3 API Services

All HTTP requests must be routed through the service layer (`src/services/`).

```typescript
import { apiClient } from './api';

export const exampleService = {
  getAll: () => apiClient.get('/resource'),
  create: (data) => apiClient.post('/resource', data)
};
```

## 7. Testing Strategy

### 7.1 Unit Testing (Python)

Use `pytest` for backend logic verification.

```bash
pytest tests/test_calculator.py
```

### 7.2 Component Testing (Vue)

Use `Vitest` and `Vue Test Utils` for frontend components.

```bash
npm run test:unit
```

### 7.3 End-to-End (E2E) Testing

Use `Playwright` for full system workflow testing.

```bash
npm run test:e2e
```

## 8. Deployment

### 8.1 Production Build

1.  **Frontend**:
    ```bash
    npm run build
    ```
    This generates optimized static assets in the `dist/` directory.

2.  **Backend**:
    Ensure all dependencies are pinned in `requirements.txt`.

### 8.2 Environment Variables

Configure production settings in `.env.production`:
*   `VITE_API_URL`: Production API endpoint.
*   `FLASK_ENV`: Set to `production`.

## 9. Best Practices

### 9.1 Code Style

*   **Python**: Adhere to PEP 8 standards. Use type hints.
*   **TypeScript**: Enable strict mode. Use ESLint and Prettier.

### 9.2 Performance

*   **Frontend**: Implement lazy loading for routes. Optimize asset sizes.
*   **Backend**: Cache expensive calculations. Optimize data processing loops.

### 9.3 Security

*   Validate all user inputs on both client and server.
*   Sanitize data to prevent injection attacks.
*   Use HTTPS for all production communications.

## 10. Troubleshooting

*   **Server Errors**: Check `logs/app.log` for stack traces.
*   **Frontend Errors**: Inspect the browser developer console.
*   **Build Issues**: Clear `node_modules` and `dist` directories and reinstall dependencies.

---
*For API specifications, refer to the API Reference.*
