# ESLint Setup and Configuration

## Overview

This project uses ESLint v9+ with the new flat configuration format to enforce code quality and consistency across JavaScript and TypeScript files.

## Configuration Files

### [`eslint.config.js`](../eslint.config.js)
Main ESLint configuration using the flat config format with:
- **JavaScript support**: ES2022 features with module syntax
- **TypeScript support**: Full type-aware linting with `@typescript-eslint`
- **Import management**: Organization and ordering with `eslint-plugin-import`
- **Code quality rules**: Best practices, style consistency, and error prevention

### [`.eslintignore`](../.eslintignore)
Specifies files and directories to exclude from linting (Python files, logs, data, build outputs, etc.)

## Installed Packages

```json
{
  "eslint": "^9.39.2",
  "@eslint/js": "^9.39.2",
  "@typescript-eslint/parser": "^8.50.1",
  "@typescript-eslint/eslint-plugin": "^8.50.1",
  "eslint-plugin-import": "^2.32.0",
  "eslint-config-prettier": "^10.1.8",
  "globals": "^16.5.0"
}
```

## Available Scripts

Run these commands from the project root:

### Lint All Files
```bash
npm run lint
```
Lints all JavaScript and TypeScript files in the project.

### Auto-fix Issues
```bash
npm run lint:fix
```
Automatically fixes fixable linting issues.

### Lint JavaScript Only
```bash
npm run lint:js
```
Lints only JavaScript files (`**/*.{js,mjs}`).

### Lint TypeScript Only
```bash
npm run lint:ts
```
Lints only TypeScript files (`**/*.{ts,tsx}`).

### Check for Warnings
```bash
npm run format:check
```
Runs linting and fails if there are any warnings (useful for CI/CD).

## Key Rules

### JavaScript Files

- **No `var`**: Use `const` or `let` instead
- **Prefer `const`**: For variables that don't change
- **Strict equality**: Use `===` and `!==`
- **Semicolons**: Required at statement ends
- **Single quotes**: For strings (unless escaping is needed)
- **2-space indentation**: Consistent formatting
- **No console.log**: Warnings for `console.log` (allow `console.warn` and `console.error`)

### TypeScript Files

All JavaScript rules plus:
- **Type imports**: Prefer `import type` for type-only imports
- **No explicit `any`**: Warnings when using `any` type
- **Unused variables**: Errors for unused variables (except those starting with `_`)
- **Consistent typing**: Enforce consistent type definitions

### Import Organization

Imports are automatically organized in this order:
1. Built-in Node modules
2. External packages
3. Internal modules
4. Parent directory imports
5. Sibling imports
6. Index imports
7. Type imports (TypeScript only)

## Integration with VS Code

Add this to your `.vscode/settings.json` for automatic formatting on save:

```json
{
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ]
}
```

## Common Commands

### Fix a specific file
```bash
npx eslint path/to/file.js --fix
```

### Check a specific directory
```bash
npx eslint js/modules/ 
```

### Output results to a file
```bash
npm run lint > lint-results.txt
```

## Excluding Files

Files can be excluded in three ways:

1. **In `eslint.config.js`** - Add patterns to the `ignores` array
2. **In `.eslintignore`** - Add file/directory patterns
3. **Inline comments** - Use `/* eslint-disable */` in the file

Example inline disable:
```javascript
/* eslint-disable no-console */
console.log('This is allowed');
/* eslint-enable no-console */
```

Disable specific rule:
```javascript
// eslint-disable-next-line no-alert
alert('This is allowed');
```

## TypeScript Integration

ESLint is configured to work with TypeScript's [`tsconfig.json`](../tsconfig.json):

- Parser: `@typescript-eslint/parser`
- Project reference: `./tsconfig.json`
- Type-aware linting enabled for advanced checks

## Troubleshooting

### ESLint not finding TypeScript files
Ensure your `tsconfig.json` includes the files you want to lint:
```json
{
  "include": ["js/**/*", "src/**/*"]
}
```

### Parser errors with ES modules
Make sure `"type": "module"` is set in [`package.json`](../package.json).

### Performance issues
The `project` option in TypeScript config can be slow. Consider:
- Excluding test files from type-aware rules
- Using `TIMING=1 npm run lint` to diagnose slow rules

## Pre-commit Hooks (Optional)

Consider adding lint checks to git hooks using `husky`:

```bash
npm install --save-dev husky lint-staged
npx husky init
```

Add to `.husky/pre-commit`:
```bash
npx lint-staged
```

Add to `package.json`:
```json
{
  "lint-staged": {
    "*.{js,ts}": "eslint --fix"
  }
}
```

## CI/CD Integration

For continuous integration, add to your pipeline:

```yaml
# GitHub Actions example
- name: Lint code
  run: npm run format:check
```

```yaml
# GitLab CI example
lint:
  script:
    - npm run format:check
```

## Related Documentation

- [TypeScript Configuration](../tsconfig.json)
- [JavaScript Modernization Plan](./JAVASCRIPT_MODERNIZATION_PLAN.md)
- [Testing Guide](./TESTING_GUIDE.md)
- [Module System Setup](./MODULE_SYSTEM_SETUP.md)

## References

- [ESLint Documentation](https://eslint.org/docs/latest/)
- [TypeScript ESLint](https://typescript-eslint.io/)
- [ESLint Flat Config](https://eslint.org/docs/latest/use/configure/configuration-files)
