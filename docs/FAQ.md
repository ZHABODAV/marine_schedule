# Frequently Asked Questions (FAQ)

## Table of Contents
- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [Usage & Features](#usage--features)
- [Performance](#performance)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

---

## General Questions

### What is the Voyage Vessel Scheduler?
The Voyage Vessel Scheduler is a comprehensive vessel scheduling and voyage planning system designed to optimize maritime operations. It supports multiple operational modules including deep-sea voyages, river transportation (Olya), and port management (Balakovo).

### What are the main features?
- **Voyage Planning**: Create and optimize vessel schedules
- **Route Management**: Define and manage trading lanes and routes
- **Cargo Management**: Track cargo commitments and assignments
- **Financial Analysis**: Calculate costs, revenues, and profitability
- **Gantt Charts**: Visual timeline representation of vessel schedules
- **Network Visualization**: Interactive network diagrams of routes
- **Excel Integration**: Import/export vessel schedules and data
- **Multi-module Support**: Deepsea, Olya, and Balakovo modules

### What technologies does it use?
- **Frontend**: Vue 3, TypeScript, Vite
- **Backend**: Python, Flask
- **Data Processing**: Pandas, NumPy
- **Visualization**: Chart.js, Vis-network
- **Testing**: Vitest, Playwright
- **Build Tools**: Vite, TypeScript compiler

---

## Installation & Setup

### What are the system requirements?
- **Node.js**: Version 18 or higher
- **Python**: Version 3.8 or higher
- **npm**: Version 8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 500MB free space

### How do I install the application?

#### On Windows:
```batch
# Run the installation script
install.bat
```

#### On macOS/Linux:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install
```

### How do I start the application?

#### Development Mode:
```batch
# Windows
start.bat

# Or manually:
# Terminal 1 - Start Python backend
python api_server.py

# Terminal 2 - Start frontend dev server
npm run dev
```

#### Production Mode:
```bash
# Build the frontend
npm run build

# Start the production server
python api_server.py
```

### What ports does the application use?
- **Frontend Dev Server**: Port 5173 (Vite default)
- **Backend API**: Port 5002 (configurable in [`api_server.py`](../api_server.py))
- **Preview Server**: Port 4173 (for production preview)

---

## Usage & Features

### How do I create a new voyage?
1. Navigate to the "Voyage Builder" section
2. Click "New Voyage" button
3. Fill in the voyage details (vessel, route, dates, cargo)
4. Click "Calculate" to compute voyage metrics
5. Click "Save" to store the voyage

### How do I import vessel schedules from Excel?
1. Go to the "Import/Export" section
2. Click "Choose File" and select your Excel file
3. Ensure the file follows the template format (download template if needed)
4. Click "Import" and verify the data
5. Review any validation errors and correct them

### How do I generate Gantt charts?
1. Create or select voyages in the system
2. Navigate to the "Gantt Chart" view
3. Select the date range and filters
4. Click "Generate Chart"
5. Export to Excel or PDF as needed

### How do I use the Network View?
The Network View visualizes your trading lanes and ports:
- **Nodes** represent ports
- **Edges** represent routes
- **Click** on nodes/edges for details
- **Drag** nodes to rearrange the layout
- **Zoom** using mouse wheel
- **Pan** by dragging the background

### Can I use multiple modules simultaneously?
Yes, the system supports multiple operational modules:
- **Deepsea Module**: Ocean-going vessels
- **Olya Module**: River transportation
- **Balakovo Module**: Port operations

Each module has its own data structures and calculations. Switch between modules using the module selector.

---

## Performance

### The application is slow. How can I improve performance?
1. **Clear Browser Cache**: Old cached data may cause issues
2. **Reduce Data Range**: Filter voyages by date range
3. **Use Virtual Scrolling**: Enabled automatically for large tables
4. **Update Browser**: Use latest Chrome, Firefox, or Edge
5. **Close Unused Tabs**: Free up browser resources
6. **Check Network**: Slow API responses may indicate network issues

### How much data can the system handle?
- **Voyages**: Tested with 10,000+ voyages
- **Vessels**: Supports 500+ vessels
- **Ports**: Supports 200+ ports
- **Routes**: Supports 1,000+ routes
- **Large Excel Files**: Up to 10MB (with virtual scrolling)

### Are there any bundle size optimizations?
Yes, the application uses:
- **Code Splitting**: Large components loaded on demand
- **Lazy Loading**: Routes loaded when accessed
- **Tree Shaking**: Unused code removed during build
- **Minification**: Production builds are minimized
- **Compression**: Gzip compression recommended for production

---

## Security

### Is my data secure?
Yes, the application implements multiple security measures:
- **CSRF Protection**: All API endpoints protected
- **Rate Limiting**: Prevents abuse and DDoS attacks
- **Input Sanitization**: All inputs validated and sanitized
- **Security Headers**: CSP, HSTS, X-Frame-Options configured
- **HTTPS**: Use HTTPS in production (recommended)

### What about the XLSX vulnerability?
The `xlsx` library has known vulnerabilities (prototype pollution and ReDoS). Mitigations:
- **Trusted Files Only**: Only process Excel files from trusted sources
- **File Size Limits**: Maximum 10MB enforced
- **Sandboxed Processing**: Excel processing isolated
- **Future Migration**: Consider ExcelJS as alternative

### How do I configure HTTPS?
For production deployment:
1. Obtain SSL certificate (Let's Encrypt recommended)
2. Configure your reverse proxy (nginx/Apache)
3. Update [`config.yaml`](../config.yaml) with HTTPS URLs
4. Enable HSTS in security headers

### What authentication methods are supported?
Current version supports:
- **Basic Authentication**: Username/password
- **Role-Based Access Control (RBAC)**: See [`data/rbac/users.json`](../data/rbac/users.json)
- **Session Management**: Server-side sessions

Planned features:
- OAuth 2.0 integration
- JWT tokens
- Two-factor authentication (2FA)

---

## Troubleshooting

### The backend API isn't responding
1. **Check if server is running**: Look for "Running on http://..." message
2. **Verify port**: Ensure port 5002 isn't used by another application
3. **Check firewall**: Allow Python through firewall
4. **Review logs**: Check console for error messages
5. **Restart server**: Stop and restart the API server

### I get CORS errors in the browser
CORS (Cross-Origin Resource Sharing) errors occur when frontend and backend are on different origins:
1. Verify frontend URL in backend CORS configuration
2. Check that API server has CORS enabled
3. Ensure proper headers are set in [`api_server.py`](../api_server.py:50)
4. In development, use the same origin or proxy

### Excel import fails with validation errors
Common causes and solutions:
- **Wrong Template**: Download and use the latest template
- **Date Format**: Use YYYY-MM-DD format
- **Missing Columns**: Ensure all required columns present
- **Data Types**: Verify numeric fields contain numbers
- **Empty Rows**: Remove empty rows from Excel file

### Gantt chart doesn't display
Troubleshooting steps:
1. **Check Data**: Ensure voyages have valid dates
2. **Browser Console**: Look for JavaScript errors
3. **Date Range**: Verify date range includes your voyages
4. **Browser Compatibility**: Use modern browser (Chrome, Firefox, Edge)
5. **Clear Cache**: Hard refresh with Ctrl+Shift+R

### Virtual scrolling shows blank rows
This usually indicates:
1. **Data Loading**: Wait for data to load completely
2. **Scroll Too Fast**: Scroll more slowly to allow rendering
3. **Browser Performance**: Close other tabs/applications
4. **Component Update**: Refresh the page

### Build fails with TypeScript errors
Common solutions:
1. **Clean Build**: Delete `node_modules` and reinstall
   ```bash
   rm -rf node_modules
   npm install
   ```
2. **Type Check**: Run `npm run type-check` to see all errors
3. **Update Dependencies**: Ensure compatible versions
4. **Check Imports**: Verify all imports are correct

---

## Development

### How do I run tests?
```bash
# Unit tests with Vitest
npm run test

# E2E tests with Playwright
npm run test:e2e

# Coverage report
npm run test:coverage

# All tests
npm run test:all
```

### How do I add a new module?
1. Create module directory: `modules/your_module.py`
2. Define data structures and calculations
3. Add API endpoints in [`api_server.py`](../api_server.py)
4. Create frontend components in `src/views/`
5. Update routing in `src/router/`
6. Add tests in `tests/`
7. Document in `docs/`

### How do I contribute to the project?
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Follow coding standards (ESLint for JS/TS, PEP8 for Python)
4. Write tests for new features
5. Update documentation
6. Submit a pull request

### What's the project structure?
```
project/
├── modules/          # Python backend modules
├── src/              # Vue 3 frontend source
│   ├── components/   # Vue components
│   ├── views/        # Page views
│   ├── stores/       # Pinia stores
│   └── types/        # TypeScript types
├── js/               # JavaScript modules (legacy/modular)
├── docs/             # Documentation
├── tests/            # Test files
├── input/            # Sample input data
└── output/           # Generated outputs
```

### How do I debug the application?
1. **Frontend**: Use browser DevTools (F12)
   - Console: See errors and logs
   - Network: Monitor API calls
   - Vue DevTools: Inspect component state

2. **Backend**: Use Python debugger
   ```python
   import pdb; pdb.set_trace()
   ```

3. **Performance**: Use browser Performance tab
4. **Memory**: Use memory profiler for Python

### Where can I find more documentation?
- **API Reference**: [`docs/API_REFERENCE.md`](API_REFERENCE.md)
- **Developer Guide**: [`docs/DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md)
- **Testing Guide**: [`docs/TESTING_GUIDE.md`](TESTING_GUIDE.md)
- **Deployment**: [`docs/PRODUCTION_DEPLOYMENT.md`](PRODUCTION_DEPLOYMENT.md)
- **Module Docs**: [`docs/МОДУЛИ_ФУНКЦИОНАЛЬНЫЕ.md`](МОДУЛИ_ФУНКЦИОНАЛЬНЫЕ.md)

### How do I report bugs or request features?
1. Check existing issues to avoid duplicates
2. Create a new issue with:
   - Clear description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (OS, browser, versions)
   - Screenshots if applicable
3. Use appropriate labels (bug, enhancement, documentation, etc.)

---

## Still Have Questions?

If your question isn't answered here:
1. Check the comprehensive documentation in the [`docs/`](.) folder
2. Review the code comments and examples
3. Search closed issues for similar questions
4. Create a new issue with your question

---

*Last Updated: December 29, 2024*
