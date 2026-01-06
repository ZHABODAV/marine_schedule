import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  // Base public path
  base: './',

  // Path aliases
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/modules': path.resolve(__dirname, './src/modules'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/core': path.resolve(__dirname, './src/core'),
      '@/services': path.resolve(__dirname, './src/services'),
      '@/ui': path.resolve(__dirname, './src/ui'),
      '@/legacy': path.resolve(__dirname, './js'),
    },
  },

  // Development server configuration
  server: {
    port: 5173,
    host: true,
    open: true,
    cors: true,
    // Proxy API requests to Python backend
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
    // HMR configuration
    hmr: {
      overlay: true,
    },
  },

  // Build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    minify: 'terser',
    target: 'es2020',
    
    // Chunk splitting strategy - improved
    rollupOptions: {
      output: {
        // Advanced code splitting
        manualChunks(id): string | undefined {
          // Vue core libraries
          if (id.includes('node_modules/vue') || id.includes('node_modules/@vue') || id.includes('node_modules/pinia')) {
            return 'vendor-vue';
          }
          
          // Router
          if (id.includes('node_modules/vue-router')) {
            return 'vendor-router';
          }
          
          // Heavy visualization libraries
          if (id.includes('node_modules/vis-network')) {
            return 'vendor-vis';
          }
          
          if (id.includes('node_modules/chart.js')) {
            return 'vendor-charts';
          }
          
          // XLSX library
          if (id.includes('node_modules/xlsx')) {
            return 'vendor-xlsx';
          }
          
          // Axios
          if (id.includes('node_modules/axios')) {
            return 'vendor-axios';
          }
          
          // Other node_modules
          if (id.includes('node_modules')) {
            return 'vendor-misc';
          }
          
          // Feature-based splitting
          if (id.includes('/src/views/')) {
            const parts = id.split('/src/views/')[1];
            if (parts) {
              const viewName = parts.split('.')[0];
              if (viewName) {
                return `view-${viewName.toLowerCase()}`;
              }
            }
          }
          
          if (id.includes('/src/components/gantt/')) {
            return 'component-gantt';
          }
          
          if (id.includes('/src/components/network/')) {
            return 'component-network';
          }
          
          if (id.includes('/src/components/financial/')) {
            return 'component-financial';
          }
          
          if (id.includes('/src/stores/')) {
            return 'stores';
          }
          
          if (id.includes('/src/services/')) {
            return 'services';
          }
          
          // Default: let Vite decide
          return undefined;
        },
        
        // Optimize chunk file names
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.');
          const ext = info?.[info.length - 1];
          
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext || '')) {
            return 'images/[name]-[hash][extname]';
          } else if (/woff2?|ttf|otf|eot/i.test(ext || '')) {
            return 'fonts/[name]-[hash][extname]';
          } else if (/css/i.test(ext || '')) {
            return 'css/[name]-[hash][extname]';
          }
          
          return 'assets/[name]-[hash][extname]';
        },
      },
    },
    
    // Optimization
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug'],
        passes: 2,
      },
      mangle: {
        safari10: true,
      },
      format: {
        comments: false,
      },
    },
    
    // Asset handling
    assetsInlineLimit: 4096,
    chunkSizeWarningLimit: 500,
    
    // CSS code splitting
    cssCodeSplit: true,
    
    // Report compressed size
    reportCompressedSize: true,
    
    // Enable CSS minification
    cssMinify: true,
  },

  // Preview server configuration
  preview: {
    port: 4173,
    host: true,
    open: true,
  },

  // PWA Plugin Configuration
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
      
      manifest: {
        name: 'Vessel Scheduler',
        short_name: 'VesselSched',
        description: 'Vessel Scheduling and Voyage Planning System',
        theme_color: '#2c3e50',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'landscape',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable',
          },
        ],
      },
      
      workbox: {
        // Cache strategies
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24, // 24 hours
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'image-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 30, // 30 days
              },
            },
          },
          {
            urlPattern: /\.(?:css|js)$/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'static-resources',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 7, // 7 days
              },
            },
          },
        ],
        
        // Assets to precache
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        
        // Files to exclude from precaching
        globIgnores: ['**/node_modules/**/*', 'sw.js', 'workbox-*.js'],
        
        // Service worker options
        cleanupOutdatedCaches: true,
        skipWaiting: true,
        clientsClaim: true,
      },
      
      devOptions: {
        enabled: false, // Disable in development
        type: 'module',
      },
    }),
  ],

  // Optimization configuration
  optimizeDeps: {
    include: ['vis-network', 'xlsx', 'vuedraggable'],
    exclude: [],
  },

  // Environment variables
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
});
