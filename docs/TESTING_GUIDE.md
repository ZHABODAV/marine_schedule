# Testing Guide

## Overview

This document describes the testing infrastructure for the Voyage Vessel Scheduler project, including unit tests, performance tests, and best practices.

## Testing Framework

The project uses **Vitest** as the testing framework, which provides:
- Fast execution with Vite's transformation pipeline
- Native ES module support
- TypeScript support
- Happy-DOM for browser environment simulation
- Built-in coverage reporting

## Setup

### Installation

All testing dependencies are already installed via npm:

```bash
npm install
```

### Running Tests

```bash
# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run performance tests only
npm run test:perf
```

## Test Structure

### Directory Organization

```
js/
├── __tests__/              # Test utilities and performance tests
│   ├── setup.js            # Test environment setup
│   └── performance.test.js # Performance benchmarks
├── core/
│   ├── utilities.js
│   └── utilities.test.js   # Unit tests for utilities
└── modules/
    ├── schedule-generator.js
    └── schedule-generator.test.js  # Unit tests for schedule generator
```

## Writing Tests

### Basic Unit Test

```javascript
import { describe, it, expect } from 'vitest';
import { toNumber } from '../core/utilities.js';

describe('utilities', () => {
  describe('toNumber()', () => {
    it('should convert valid string numbers', () => {
      expect(toNumber('123')).toBe(123);
      expect(toNumber('45.67')).toBe(45.67);
    });

    it('should return 0 for null/undefined', () => {
      expect(toNumber(null)).toBe(0);
      expect(toNumber(undefined)).toBe(0);
    });
  });
});
```

### Performance Test

```javascript
import { describe, it, expect } from 'vitest';
import { toNumber } from '../core/utilities.js';

describe('performance tests', () => {
  it('should handle 10,000 conversions quickly', () => {
    const start = performance.now();
    
    for (let i = 0; i < 10000; i++) {
      toNumber('123.45');
    }
    
    const duration = performance.now() - start;
    expect(duration).toBeLessThan(100); // Should complete in < 100ms
  });
});
```

### Mocking Dependencies

```javascript
import { vi } from 'vitest';

// Mock a module
vi.mock('../core/app-state.js', () => ({
  appState: {
    filters: { opTypes: [] },
    vessels: []
  },
  getCurrentData: vi.fn(() => ({ /* mock data */ }))
}));

// Mock a function
const mockShowNotification = vi.fn();
vi.mock('../core/utilities.js', () => ({
  showNotification: mockShowNotification
}));
```

## Test Coverage

### Coverage Reports

Generate coverage reports:

```bash
npm run test:coverage
```

Coverage reports are generated in three formats:
- **Text**: Console output
- **JSON**: `coverage/coverage.json`
- **HTML**: `coverage/index.html` (open in browser)

### Coverage Goals

| Metric | Target |
|--------|--------|
| Statements | > 80% |
| Branches | > 75% |
| Functions | > 80% |
| Lines | > 80% |

## Testing Best Practices

### 1. Test Organization

- **Group related tests** using `describe` blocks
- **Use descriptive test names** that explain what is being tested
- **Follow AAA pattern**: Arrange, Act, Assert

```javascript
it('should format date in Russian locale', () => {
  // Arrange
  const date = '2024-01-15';
  
  // Act
  const result = formatDate(date);
  
  // Assert
  expect(result).toMatch(/\d{1,2}/);
});
```

### 2. Test Isolation

- Each test should be independent
- Use `beforeEach` and `afterEach` for setup/cleanup
- Avoid shared mutable state between tests

```javascript
beforeEach(() => {
  // Clear any mock calls
  vi.clearAllMocks();
});
```

### 3. Edge Cases

Always test:
- **Null/undefined** inputs
- **Empty** arrays/strings/objects
- **Boundary values** (0, -1, MAX_VALUE)
- **Invalid inputs** (wrong types, malformed data)

### 4. Performance Testing

Include performance tests for:
- Functions that process large datasets
- Time-critical operations
- Bulk operations

```javascript
it('should handle large datasets efficiently', () => {
  const largeDataset = Array.from({ length: 10000 }, (_, i) => i);
  
  const start = performance.now();
  const result = processData(largeDataset);
  const duration = performance.now() - start;
  
  expect(duration).toBeLessThan(200); // < 200ms threshold
});
```

## Performance Thresholds

| Operation Type | Threshold |
|----------------|-----------|
| Small operations | < 10ms |
| Medium operations | < 50ms |
| Large operations | < 200ms |
| Bulk operations | < 1000ms |

## Tested Modules

###  Core Utilities ([`js/core/utilities.js`](../js/core/utilities.js))

- `toNumber()` - Number conversion with edge cases
- `formatDate()` - Date formatting
- `showNotification()` - Toast notifications
- `updateCSSVariables()` - CSS variable updates

**Test Coverage**: 45+ test cases including edge cases and performance tests

###  Schedule Generator ([`js/modules/schedule-generator.js`](../js/modules/schedule-generator.js))

- `generateGanttFromVoyages()` - Gantt chart data generation
- Performance tests for large datasets
- Edge case handling

**Test Coverage**: 15+ test cases

###  Performance Tests ([`js/__tests__/performance.test.js`](../js/__tests__/performance.test.js))

- Array operations (filter, map, reduce)
- String operations (concatenation, search)
- Object operations (clone, merge)
- Date operations (format, calculate)
- DOM-like operations
- JSON operations (stringify, parse)
- Memory stress tests

**Test Coverage**: 20+ performance benchmarks

## Continuous Integration

### Pre-commit Checks

Before committing code:

```bash
# Run type checking
npm run type-check

# Run tests
npm run test:run

# Check coverage
npm run test:coverage
```

### CI/CD Integration

Add to your CI/CD pipeline:

```yaml
steps:
  - name: Install dependencies
    run: npm install
    
  - name: Run type check
    run: npm run type-check
    
  - name: Run tests
    run: npm run test:run
    
  - name: Generate coverage
    run: npm run test:coverage
```

## Troubleshooting

### Tests Not Found

If tests aren't being discovered:
1. Ensure test files end with `.test.js` or `.spec.js`
2. Check that files are in the `js/` directory
3. Verify [`vitest.config.js`](../vitest.config.js) includes the correct patterns

### Module Import Errors

If module imports fail:
1. Ensure all imports use `.js` extensions
2. Check that module paths are correct
3. Verify `"type": "module"` in [`package.json`](../package.json)

### Slow Tests

If tests run slowly:
1. Check for synchronous operations that should be optimized
2. Use `vi.mock()` to mock expensive operations
3. Consider splitting large test suites

## Future Enhancements

### Planned Test Coverage

- [ ] Table Renderers module
- [ ] CRUD Operations module
- [ ] Voyage Builder module
- [ ] Financial Analysis module
- [ ] Network Visualization module
- [ ] Integration tests with API
- [ ] E2E tests with Playwright

### Test Infrastructure Improvements

- [ ] Visual regression testing
- [ ] Snapshot testing for UI components
- [ ] Contract testing for API
- [ ] Load testing for performance
- [ ] Accessibility testing

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [JavaScript Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)

## Contributing

When adding new modules:
1. Create corresponding `.test.js` file
2. Aim for > 80% code coverage
3. Include edge cases and performance tests
4. Update this documentation

---

**Last Updated**: December 26, 2025  
**Status**: Testing framework established with core utilities and schedule generator coverage
