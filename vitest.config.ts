import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['./src/__tests__/setup.ts'],
    
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/**',
        '**/__tests__/**',
        '**/*.test.{js,ts,vue}',
        '**/*.spec.{js,ts,vue}',
        'vite.config.ts',
        'vitest.config.ts',
        'src/main.ts',
        'dist/**',
      ],
      all: true,
      lines: 80,
      functions: 80,
      branches: 75,
      statements: 80,
    },
    
    include: [
      'src/**/*.{test,spec}.{js,ts,vue}',
      'src/**/__tests__/*.{test,spec}.{js,ts,vue}',
      'js/**/*.{test,spec}.js',
      'js/**/__tests__/*.{test,spec}.js',
    ],
    
    exclude: [
      'node_modules',
      'dist',
      '.vscode',
      '.kilocode',
      'output/**',
      'logs/**',
      'src/__tests__/setup.ts',
      'js/__tests__/setup.js',
    ],
  },
  
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
});
