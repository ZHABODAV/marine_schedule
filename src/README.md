# Vue 3 Project Structure

This directory contains the Vue 3 application setup for the Vessel Scheduler.

## Directory Structure

```
src/
├── assets/          # Static assets (CSS, images, etc.)
│   └── main.css    # Global styles
├── components/      # Reusable Vue components
│   └── HelloWorld.vue
├── router/          # Vue Router configuration
│   └── index.ts    # Route definitions
├── stores/          # Pinia state management
│   ├── app.ts      # Application-wide state
│   └── vessel.ts   # Vessel-related state
├── views/           # Page-level components
│   ├── HomeView.vue
│   ├── DashboardView.vue
│   ├── AboutView.vue
│   └── NotFoundView.vue
├── App.vue          # Root component
└── main.ts          # Application entry point
```

## Key Files

### [`main.ts`](main.ts:1)
The main entry point that initializes Vue, Pinia, and Vue Router.

### [`App.vue`](App.vue:1)
The root component with navigation and routing.

### Router ([`router/index.ts`](router/index.ts:1))
Configured routes:
- `/` - Home page
- `/dashboard` - Dashboard view
- `/about` - About page
- Wildcard route for 404 handling

### Stores
- **[`stores/vessel.ts`](stores/vessel.ts:1)** - Vessel, voyage, and port management
- **[`stores/app.ts`](stores/app.ts:1)** - Application state (sidebar, theme, notifications)

## Running the Application

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Technology Stack

- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type safety
- **Pinia** - State management (Composition API style)
- **Vue Router** - Client-side routing
- **Vite** - Build tool with HMR

## Next Steps

1. Migrate existing JavaScript modules to Vue components
2. Integrate with the Python backend API
3. Implement vessel management features
4. Add visualization components (Gantt charts, network diagrams)
5. Implement financial analysis dashboards
