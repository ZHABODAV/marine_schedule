/**
 * API Documentation Generator
 * Automatically generates comprehensive API documentation from endpoint definitions
 */

class APIDocumentationGenerator {
    constructor() {
        this.endpoints = [];
        this.version = '1.0.0';
        this.baseURL = window.location.origin;
    }
    
    /**
     * Register an API endpoint
     * @param {object} endpoint - Endpoint configuration
     */
    registerEndpoint(endpoint) {
        const defaults = {
            method: 'GET',
            authentication: false,
            parameters: [],
            responses: [],
            examples: []
        };
        
        this.endpoints.push({ ...defaults, ...endpoint });
    }
    
    /**
     * Register multiple endpoints
     * @param {array} endpoints - Array of endpoint configurations
     */
    registerEndpoints(endpoints) {
        endpoints.forEach(ep => this.registerEndpoint(ep));
    }
    
    /**
     * Generate HTML documentation
     * @returns {string} - HTML documentation
     */
    generateHTML() {
        return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - v${this.version}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        header p { opacity: 0.9; font-size: 1.1rem; }
        .nav {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nav h3 { margin-bottom: 1rem; color: #667eea; }
        .nav ul { list-style: none; }
        .nav li { margin: 0.5rem 0; }
        .nav a {
            color: #333;
            text-decoration: none;
            padding: 0.5rem;
            display: block;
            border-radius: 4px;
            transition: all 0.2s;
        }
        .nav a:hover { background: #f5f5f5; color: #667eea; }
        .endpoint {
            background: white;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .endpoint-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #f0f0f0;
        }
        .method {
            padding: 0.4rem 1rem;
            border-radius: 4px;
            font-weight: 700;
            font-size: 0.9rem;
            text-transform: uppercase;
        }
        .method.get { background: #61affe; color: white; }
        .method.post { background: #49cc90; color: white; }
        .method.put { background: #fca130; color: white; }
        .method.delete { background: #f93e3e; color: white; }
        .path {
            font-family: 'Courier New', monospace;
            font-size: 1.1rem;
            color: #333;
        }
        .description { margin-bottom: 1.5rem; color: #666; }
        .section { margin-bottom: 1.5rem; }
        .section h4 {
            color: #667eea;
            margin-bottom: 0.75rem;
            font-size: 1.1rem;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.5rem;
        }
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        .code-block {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        .badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        .badge.required { background: #fee; color: #c00; }
        .badge.optional { background: #e8f5e9; color: #2e7d32; }
        .response-code {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            background: #f0f0f0;
            border-radius: 4px;
            font-family: monospace;
            font-weight: 600;
        }
        .auth-badge {
            background: #fff3cd;
            color: #856404;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1> API Documentation</h1>
            <p>Version ${this.version} • Base URL: ${this.baseURL}</p>
        </div>
    </header>
    
    <div class="container">
        <div class="nav">
            <h3> Endpoints</h3>
            <ul>
                ${this.endpoints.map((ep, i) => `
                    <li><a href="#endpoint-${i}">${ep.method} ${ep.path}</a></li>
                `).join('')}
            </ul>
        </div>
        
        ${this.endpoints.map((ep, i) => this.generateEndpointHTML(ep, i)).join('')}
    </div>
</body>
</html>
        `;
    }
    
    /**
     * Generate HTML for a single endpoint
     * @param {object} endpoint - Endpoint configuration
     * @param {number} index - Endpoint index
     * @returns {string} - HTML for endpoint
     */
    generateEndpointHTML(endpoint, index) {
        return `
<div class="endpoint" id="endpoint-${index}">
    <div class="endpoint-header">
        <span class="method ${endpoint.method.toLowerCase()}">${endpoint.method}</span>
        <span class "path">${endpoint.path}</span>
    </div>
    
    ${endpoint.authentication ? '<div class="auth-badge"> Authentication Required</div>' : ''}
    
    <div class="description">${endpoint.description || 'No description provided'}</div>
    
    ${endpoint.parameters && endpoint.parameters.length > 0 ? `
        <div class="section">
            <h4>Parameters</h4>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Required</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    ${endpoint.parameters.map(param => `
                        <tr>
                            <td><code>${param.name}</code></td>
                            <td>${param.type}</td>
                            <td><span class="badge ${param.required ? 'required' : 'optional'}">${param.required ? 'Required' : 'Optional'}</span></td>
                            <td>${param.description || ''}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    ` : ''}
    
    ${endpoint.requestBody ? `
        <div class="section">
            <h4>Request Body</h4>
            <div class="code-block">${this.formatJSON(endpoint.requestBody)}</div>
        </div>
    ` : ''}
    
    ${endpoint.responses && endpoint.responses.length > 0 ? `
        <div class="section">
            <h4>Responses</h4>
            ${endpoint.responses.map(response => `
                <div style="margin-bottom: 1rem;">
                    <div style="margin-bottom: 0.5rem;">
                        <span class="response-code">${response.code}</span>
                        <span style="margin-left: 0.5rem;">${response.description}</span>
                    </div>
                    ${response.body ? `<div class="code-block">${this.formatJSON(response.body)}</div>` : ''}
                </div>
            `).join('')}
        </div>
    ` : ''}
    
    ${endpoint.examples && endpoint.examples.length > 0 ? `
        <div class="section">
            <h4>Examples</h4>
            ${endpoint.examples.map(example => `
                <div style="margin-bottom: 1rem;">
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">${example.title}</div>
                    <div class="code-block">${this.escapeHTML(example.code)}</div>
                </div>
            `).join('')}
        </div>
    ` : ''}
</div>
        `;
    }
    
    /**
     * Format JSON for display
     * @param {object|string} json - JSON to format
     * @returns {string} - Formatted JSON
     */
    formatJSON(json) {
        const jsonString = typeof json === 'string' ? json : JSON.stringify(json, null, 2);
        return this.escapeHTML(jsonString);
    }
    
    /**
     * Escape HTML special characters
     * @param {string} str - String to escape
     * @returns {string} - Escaped string
     */
    escapeHTML(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
    
    /**
     * Generate and download documentation as HTML file
     */
    downloadHTML() {
        const html = this.generateHTML();
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `api-documentation-v${this.version}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    /**
     * Generate Markdown documentation
     * @returns {string} - Markdown documentation
     */
    generateMarkdown() {
        let md = `# API Documentation\n\n`;
        md += `**Version:** ${this.version}  \n`;
        md += `**Base URL:** \`${this.baseURL}\`\n\n`;
        md += `## Table of Contents\n\n`;
        
        // Table of contents
        this.endpoints.forEach((ep, i) => {
            md += `${i + 1}. [${ep.method} ${ep.path}](#${this.slugify(ep.path)})\n`;
        });
        
        md += `\n---\n\n`;
        
        // Endpoints
        this.endpoints.forEach(ep => {
            md += `## ${ep.method} ${ep.path}\n\n`;
            md += `${ep.description || 'No description'}\n\n`;
            
            if (ep.authentication) {
                md += ` **Authentication Required**\n\n`;
            }
            
            if (ep.parameters && ep.parameters.length > 0) {
                md += `### Parameters\n\n`;
                md += `| Name | Type | Required | Description |\n`;
                md += `|------|------|----------|-------------|\n`;
                ep.parameters.forEach(param => {
                    md += `| \`${param.name}\` | ${param.type} | ${param.required ? '' : '○'} | ${param.description || ''} |\n`;
                });
                md += `\n`;
            }
            
            if (ep.requestBody) {
                md += `### Request Body\n\n`;
                md += `\`\`\`json\n${JSON.stringify(ep.requestBody, null, 2)}\n\`\`\`\n\n`;
            }
            
            if (ep.responses && ep.responses.length > 0) {
                md += `### Responses\n\n`;
                ep.responses.forEach(response => {
                    md += `**${response.code}** - ${response.description}\n\n`;
                    if (response.body) {
                        md += `\`\`\`json\n${JSON.stringify(response.body, null, 2)}\n\`\`\`\n\n`;
                    }
                });
            }
            
            md += `---\n\n`;
        });
        
        return md;
    }
    
    /**
     * Create slug from string
     * @param {string} str - String to slugify
     * @returns {string} - Slug
     */
    slugify(str) {
        return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    }
    
    /**
     * Download Markdown documentation
     */
    downloadMarkdown() {
        const md = this.generateMarkdown();
        const blob = new Blob([md], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `api-documentation-v${this.version}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Initialize default documentation for vessel scheduler API
const vesselSchedulerAPIDocs = new APIDocumentationGenerator();

// Register all API endpoints
vesselSchedulerAPIDocs.registerEndpoints([
    {
        method: 'GET',
        path: '/api/vessels',
        description: 'Retrieve all vessels',
        responses: [
            {
                code: 200,
                description: 'Success',
                body: { vessels: [{ id: 'V001', name: 'Atlantic Star', class: 'Handysize', dwt: 35000, speed: 14, status: 'Active' }] }
            }
        ]
    },
    {
        method: 'POST',
        path: '/api/vessels',
        description: 'Create a new vessel',
        authentication: true,
        requestBody: { id: 'V001', name: 'Atlantic Star', class: 'Handysize', dwt: 35000, speed: 14 },
        responses: [
            { code: 201, description: 'Created', body: { success: true, vessel_id: 'V001' } },
            { code: 400, description: 'Invalid input', body:{ success: false, error: 'Validation failed' } }
        ]
    },
    {
        method: 'GET',
        path: '/api/cargo',
        description: 'Retrieve all cargo commitments',
        responses: [
            {
                code: 200,
                description: 'Success',
                body: { cargo: [{ id: 'C001', commodity: 'Grain', quantity: 50000, loadPort: 'Houston', dischPort: 'Rotterdam' }] }
            }
        ]
    },
    {
        method: 'POST',
        path: '/api/calculate',
        description: 'Calculate voyage schedule',
        authentication: true,
        parameters: [
            { name: 'module', type: 'string', required: true, description: 'Module name (deepsea, balakovo, olya)' },
            { name: 'voyageFilter', type: 'string', required: false, description: 'Filter type (all, custom)' }
        ],
        requestBody: { module: 'deepsea', voyageFilter: 'all' },
        responses: [
            { code: 200, description: 'Success', body: { success: true, legs_count: 45, alerts_count: 2 } },
            { code: 400, description: 'Invalid module', body: { success: false, error: 'Unknown module' } }
        ]
    },
    {
        method: 'GET',
        path: '/api/gantt-data',
        description: 'Get Gantt chart data',
        responses: [
            {
                code: 200,
                description: 'Success',
                body: { assets: { 'V001': [{ leg_type: 'loading', start_time: '2025-01-15T08:00:00Z', end_time: '2025-01-15T20:00:00Z' }] } }
            }
        ]
    },
    {
        method: 'POST',
        path: '/api/export/excel',
        description: 'Export data to Excel',
        parameters: [
            { name: 'type', type: 'string', required: true, description: 'Export type (gantt, fleet)' },
            { name: 'year_month', type: 'string', required: false, description: 'Year-month in YYYY-MM format' }
        ],
        responses: [
            { code: 200, description: 'Excel file download' },
            { code: 404, description: 'No data found', body: { error: 'No voyages found for this month' } }
        ]
    }
]);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIDocumentationGenerator, vesselSchedulerAPIDocs };
}

console.log(' API Documentation Generator loaded successfully');
