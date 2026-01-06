#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Modules Integration Script
Automatically integrates UI modules from ui_modules/ into vessel_scheduler_enhanced.html
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Fix Unicode encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class UIModulesIntegrator:
    """Integrates UI modules into the main HTML file"""
    
    def __init__(self, base_html='vessel_scheduler_enhanced.html', output_html='vessel_scheduler_complete.html'):
        self.base_html = base_html
        self.output_html = output_html
        self.ui_modules_dir = 'ui_modules'
        
    def read_file(self, filepath):
        """Read file content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    def write_file(self, filepath, content):
        """Write content to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f" Successfully wrote {filepath}")
            return True
        except Exception as e:
            print(f" Error writing {filepath}: {e}")
            return False
    
    def integrate_modules(self):
        """Main integration process"""
        print("=" * 60)
        print("UI Modules Integration Script")
        print("=" * 60)
        
        # Read base HTML
        html_content = self.read_file(self.base_html)
        if not html_content:
            print(f" Could not read base HTML file: {self.base_html}")
            return False
        
        # Read combined CSS
        css_path = os.path.join(self.ui_modules_dir, 'ALL_MODULES_COMBINED.css')
        css_content = self.read_file(css_path)
        
        # Read combined JS
        js_path = os.path.join(self.ui_modules_dir, 'ALL_MODULES_COMBINED.js')
        js_content = self.read_file(js_path)
        
        # Prepare injection markers
        print("\n Preparing content injection...")
        
        # 1. Add external library references (Leaflet for maps, html2pdf for PDF export)
        external_libs = '''
    <!-- External Libraries for UI Modules -->
    <!-- Leaflet for maps (vessel tracking) -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <!-- html2pdf for PDF export -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>'''
        
        # 2. Inject CSS before </style>
        if css_content:
            print("   Injecting module CSS...")
            css_injection = f"\n\n/* ===== UI MODULES STYLES ===== */\n{css_content}\n"
            html_content = html_content.replace('</style>', f'{css_injection}</style>')
        
        # 3. Inject external libs before </head>
        print("   Injecting external libraries...")
        html_content = html_content.replace('</head>', f'{external_libs}\n</head>')
        
        # 4. Add new tabs for UI modules
        print("   Adding new tabs...")
        new_tabs = '''
<button class="tab-button" data-tab="alerts">Alerts</button>
            <button class="tab-button" data-tab="berthManager">Berth Mgmt</button>
            <button class="tab-button" data-tab="bunkerOpt">Bunker Opt</button>
            <button class="tab-button" data-tab="weather">Weather</button>
            <button class="tab-button" data-tab="tracking">Tracking</button>
            <button class="tab-button" data-tab="scenarioMgmt">Scenarios</button>
            <button class="tab-button" data-tab="templates">Templates</button>
            <button class="tab-button" data-tab="capacityPlan">Capacity Plan</button>'''
        
        # Find and update tabs
        html_content = html_content.replace(
            '<button class="tab-button" data-tab="reports">Отчеты</button>',
            f'<button class="tab-button" data-tab="reports">Отчеты</button>{new_tabs}'
        )
        
        # 5. Add new tab content sections before Reports tab
        print("   Adding module containers...")
        module_sections = '''
            <!-- Alerts Dashboard Tab -->
            <div class="tab-content" id="alerts">
                <div id="alerts-dashboard" class="module-container"></div>
            </div>

            <!-- Berth Management Tab -->
            <div class="tab-content" id="berthManager">
                <div id="berth-management" class="module-container"></div>
            </div>

            <!-- Bunker Optimization Tab -->
            <div class="tab-content" id="bunkerOpt">
                <div id="bunker-optimization" class="module-container"></div>
            </div>

            <!-- Weather Integration Tab -->
            <div class="tab-content" id="weather">
                <div id="weather-integration" class="module-container"></div>
            </div>

            <!-- Vessel Tracking Tab -->
            <div class="tab-content" id="tracking">
                <div id="vessel-tracking" class="module-container"></div>
            </div>

            <!-- Scenario Management Tab -->
            <div class="tab-content" id="scenarioMgmt">
                <div id="scenario-management" class="module-container"></div>
            </div>

            <!-- Voyage Templates Tab -->
            <div class="tab-content" id="templates">
                <div id="voyage-templates" class="module-container"></div>
            </div>

            <!-- Berth Capacity Planning Tab -->
            <div class="tab-content" id="capacityPlan">
                <div id="berth-capacity-planning" class="module-container"></div>
            </div>

'''
        
        html_content = html_content.replace(
            '<!-- Reports Tab -->',
            f'{module_sections}\n            <!-- Reports Tab -->'
        )
        
        # 6. Inject JavaScript before closing </body>
        if js_content:
            print("   Injecting module JavaScript...")
            js_injection = f'''
    <!-- UI Modules JavaScript -->
    <script>
    {js_content}
    
    // Initialize UI modules when document is ready
    (function initUIModules() {{
        const API_BASE = '/api'; // Adjust to your API endpoint
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', setupModules);
        }} else {{
            setupModules();
        }}
        
        function setupModules() {{
            console.log(' Initializing UI Modules...');
            
            // Initialize modules on tab switch
            document.querySelectorAll('.tab-button').forEach(btn => {{
                btn.addEventListener('click', async function() {{
                    const tabId = this.dataset.tab;
                    await initializeModuleForTab(tabId);
                }});
            }});
            
            console.log(' UI Modules setup complete');
        }}
        
        async function initializeModuleForTab(tabId) {{
            // Prevent re-initialization
            if (window.initializedModules && window.initializedModules[tabId]) {{
                return;
            }}
            
            if (!window.initializedModules) {{
                window.initializedModules = {{}};
            }}
            
            try {{
                switch(tabId) {{
                    case 'alerts':
                        const alertsDashboard = new AlertsDashboard({{
                            containerId: 'alerts-dashboard',
                            apiEndpoint: `${{API_BASE}}/alerts`,
                            refreshInterval: 30000
                        }});
                        await alertsDashboard.init();
                        window.initializedModules.alerts = alertsDashboard;
                        break;
                    
                    case 'berthManager':
                        const berthMgmt = new BerthManagement({{
                            containerId: 'berth-management',
                            apiEndpoint: `${{API_BASE}}/berths`
                        }});
                        await berthMgmt.init();
                        window.initializedModules.berthManager = berthMgmt;
                        break;
                    
                    case 'bunkerOpt':
                        const bunkerOpt = new BunkerOptimization({{
                            containerId: 'bunker-optimization',
                            apiEndpoint: `${{API_BASE}}/bunker`
                        }});
                        await bunkerOpt.init();
                        window.initializedModules.bunkerOpt = bunkerOpt;
                        break;
                    
                    case 'weather':
                        const weather = new WeatherIntegration({{
                            containerId: 'weather-integration',
                            apiEndpoint: `${{API_BASE}}/weather`
                        }});
                        await weather.init();
                        window.initializedModules.weather = weather;
                        break;
                    
                    case 'tracking':
                        const tracking = new VesselTracking({{
                            containerId: 'vessel-tracking',
                            apiEndpoint: `${{API_BASE}}/vessels/tracking`,
                            mapProvider: 'leaflet',
                            updateInterval: 60000
                        }});
                        await tracking.init();
                        window.initializedModules.tracking = tracking;
                        break;
                    
                    case 'scenarioMgmt':
                        const scenarios = new ScenarioManagement({{
                            containerId: 'scenario-management',
                            apiEndpoint: `${{API_BASE}}/scenarios`
                        }});
                        await scenarios.init();
                        window.initializedModules.scenarioMgmt = scenarios;
                        break;
                    
                    case 'templates':
                        const templates = new VoyageTemplates({{
                            containerId: 'voyage-templates',
                            apiEndpoint: `${{API_BASE}}/voyage-templates`
                        }});
                        await templates.init();
                        window.initializedModules.templates = templates;
                        break;
                    
                    case 'capacityPlan':
                        const capacity = new BerthCapacityPlanning({{
                            containerId: 'berth-capacity-planning',
                            apiEndpoint: `${{API_BASE}}/capacity`
                        }});
                        await capacity.init();
                        window.initializedModules.capacityPlan = capacity;
                        break;
                }}
            }} catch (error) {{
                console.error(`Error initializing module ${{tabId}}:`, error);
            }}
        }}
        
        // Setup event listeners for cross-module communication
        document.addEventListener('showNotification', (e) => {{
            const {{ type, message }} = e.detail;
            // Integration with existing notification system can go here
            console.log(`[${{type.toUpperCase()}}] ${{message}}`);
        }});
        
        document.addEventListener('showModal', (e) => {{
            const {{ content }} = e.detail;
            // Integration with existing modal system can go here
            console.log('Show modal:', content);
        }});
    }})();
    </script>
'''
            
            html_content = html_content.replace('</body>', f'{js_injection}\n</body>')
        
        # 7. Update version and timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html_content = html_content.replace(
            '<p>Версия 3.0.0 Enhanced | Offline Ready</p>',
            f'<p>Версия 4.0.0 Complete with UI Modules | Generated: {timestamp}</p>'
        )
        
        # 8. Write output file
        print(f"\n Writing integrated HTML to {self.output_html}...")
        if self.write_file(self.output_html, html_content):
            print(f"\n{'=' * 60}")
            print(f" SUCCESS! Integrated HTML created:")
            print(f"    {self.output_html}")
            print(f"    Included modules:")
            print(f"      - Alerts Dashboard")
            print(f"      - Berth Management")
            print(f"      - Bunker Optimization")
            print(f"      - Weather Integration")
            print(f"      - Vessel Tracking")
            print(f"      - Scenario Management")
            print(f"      - Voyage Templates")
            print(f"      - Berth Capacity Planning")
            print(f"\n{'=' * 60}")
            print(f"\n Next Steps:")
            print(f"   1. Open {self.output_html} in your browser")
            print(f"   2. Check the new tabs (Alerts, Berth Mgmt, etc.)")
            print(f"   3. Implement backend API endpoints:")
            print(f"      - GET /api/alerts")
            print(f"      - GET /api/berths")
            print(f"      - GET /api/bunker")
            print(f"      - GET /api/weather")
            print(f"      - GET /api/vessels/tracking")
            print(f"      - GET /api/scenarios")
            print(f"      - GET /api/voyage-templates")
            print(f"      - GET /api/capacity")
            print(f"   4. See ui_modules/README.md for API specifications")
            print(f"\n{'=' * 60}")
            return True
        
        return False


def main():
    """Main entry point"""
    integrator = UIModulesIntegrator()
    success = integrator.integrate_modules()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
