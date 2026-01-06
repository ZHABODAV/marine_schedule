/**
 * Vue Router Configuration with Lazy Loading and Code Splitting
 */

import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';

/**
 * Route definitions with lazy loading for optimal bundle sizes
 * Each view is loaded only when the route is visited
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: {
      title: 'Home - Voyage Vessel Scheduler',
      requiresAuth: false,
    },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import(/* webpackChunkName: "dashboard" */ '../views/DashboardView.vue'),
    meta: {
      title: 'Dashboard',
      requiresAuth: true,
      skeleton: 'card',
    },
  },
  {
    path: '/voyage-builder',
    name: 'VoyageBuilder',
    // Lazy load with webpackChunkName for better debugging
    component: () => import(/* webpackChunkName: "voyage-builder" */ '../views/VoyageBuilder.vue'),
    meta: {
      title: 'Voyage Builder',
      requiresAuth: true,
      skeleton: 'gantt', // Type of loading skeleton to show
    },
  },
  {
    path: '/network',
    name: 'NetworkView',
    component: () => import(/* webpackChunkName: "network" */ '../views/NetworkView.vue'),
    meta: {
      title: 'Network View',
      requiresAuth: true,
      skeleton: 'network',
    },
  },
  {
    path: '/calendar',
    name: 'Calendar',
    component: () => import(/* webpackChunkName: "calendar" */ '../views/OperationalCalendarView.vue'),
    meta: {
      title: 'Operational Calendar',
      requiresAuth: true,
      skeleton: 'calendar',
    },
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import(/* webpackChunkName: "schedule" */ '../views/ScheduleView.vue'),
    meta: {
      title: 'Schedule View',
      requiresAuth: true,
      skeleton: 'table',
    },
  },
  {
    path: '/schedule/generator',
    name: 'YearScheduleGenerator',
    component: () => import(/* webpackChunkName: "schedule-generator" */ '../views/YearScheduleGeneratorView.vue'),
    meta: {
      title: 'Year Schedule Generator',
      requiresAuth: true,
      skeleton: 'generic',
    },
  },
  {
    path: '/gantt',
    name: 'Gantt',
    component: () => import(/* webpackChunkName: "gantt" */ '../views/GanttView.vue'),
    meta: {
      title: 'Gantt Chart',
      requiresAuth: true,
      skeleton: 'gantt',
    },
  },
  {
    path: '/vessels',
    name: 'Vessels',
    component: () => import(/* webpackChunkName: "vessels" */ '../views/VesselManagement.vue'),
    meta: {
      title: 'Vessel Management',
      requiresAuth: true,
      skeleton: 'table',
    },
  },
  {
    path: '/cargo',
    name: 'Cargo',
    component: () => import(/* webpackChunkName: "cargo" */ '../views/CargoManagement.vue'),
    meta: {
      title: 'Cargo Management',
      requiresAuth: true,
      skeleton: 'list',
    },
  },
  {
    path: '/routes',
    name: 'Routes',
    component: () => import(/* webpackChunkName: "routes" */ '../views/RouteManagement.vue'),
    meta: {
      title: 'Route Management',
      requiresAuth: true,
      skeleton: 'table',
    },
  },
  {
    path: '/financial',
    name: 'Financial',
    component: () => import(/* webpackChunkName: "financial" */ '../views/FinancialView.vue'),
    meta: {
      title: 'Financial Analysis',
      requiresAuth: true,
      skeleton: 'card',
    },
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import(/* webpackChunkName: "reports" */ '../views/ReportsView.vue'),
    meta: {
      title: 'Reports',
      requiresAuth: true,
      skeleton: 'generic',
    },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import(/* webpackChunkName: "settings" */ '../views/DashboardView.vue'),
    meta: {
      title: 'Settings',
      requiresAuth: true,
      skeleton: 'card',
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import(/* webpackChunkName: "auth" */ '../views/AboutView.vue'),
    meta: {
      title: 'Login',
      requiresAuth: false,
      hideNav: true,
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import(/* webpackChunkName: "error" */ '../views/NotFoundView.vue'),
    meta: {
      title: '404 Not Found',
      requiresAuth: false,
    },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    // Scroll to saved position when using browser back/forward
    if (savedPosition) {
      return savedPosition;
    }
    // Scroll to top for new routes
    return { top: 0 };
  },
});

/**
 * Navigation guards for authentication and analytics
 */
router.beforeEach((to, _from, next) => {
  // Update document title
  document.title = (to.meta.title as string) || 'Voyage Vessel Scheduler';
  
  // Check authentication (placeholder - implement actual auth logic)
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
  
  // Bypass auth in development
  if (import.meta.env.DEV) {
    // Set default authenticated state for dev
    if (localStorage.getItem('isAuthenticated') !== 'true') {
      localStorage.setItem('isAuthenticated', 'true');
    }
    next();
    return;
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login if authentication is required
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else {
    next();
  }
});

router.afterEach((to, from) => {
  // Track page views for analytics
  if (window.analytics) {
    window.analytics.track_page_view(to.path, to.meta.title as string);
  }
  
  // Log navigation for debugging
  if (import.meta.env.DEV) {
    console.log(`Navigated from ${from.path} to ${to.path}`);
  }
});

/**
 * Error handler for lazy loading failures
 */
router.onError((error) => {
  console.error('Router error:', error);
  
  // If chunk loading failed, try to reload the page
  if (/ChunkLoadError|Failed to fetch dynamically imported module/.test(error.message)) {
    console.warn('Chunk load error detected, attempting page reload...');
    window.location.reload();
  }
  
  // Track error in monitoring
  if (window.errorTracker) {
    window.errorTracker.capture_exception(error, {
      context: 'router',
      message: 'Route navigation error',
    });
  }
});

export default router;

// Type augmentation for window object
declare global {
  interface Window {
    analytics?: {
      track_page_view: (path: string, title: string) => void;
    };
    errorTracker?: {
      capture_exception: (error: Error, context: any) => void;
    };
  }
}
