# User Guide

**Version:** 2.0.0  
**Last Updated:** December 26, 2025

## Introduction

The Vessel Scheduling System is a modern web platform for managing maritime cargo transportation. It helps plan voyages, track berth utilization, optimize routes, and calculate the economic efficiency of transportation.

### Key Features

-  Automatic schedule generation for fleet
-  Interactive Gantt charts
-  Cargo, vessel, and route management
-  Financial analysis and reporting
-  Route network visualization
-  Data export to Excel
-  Modern Vue.js-based web interface

The program runs in your browser (Chrome, Edge, or Firefox recommended). All data is stored locally on your computer. Internet connection is only required for initial loading.

## System Requirements

- **Operating System:** Windows 10/11, macOS, Linux
- **Python:** version 3.8 or higher
- **Node.js:** version 16 or higher (for development)
- **Browser:** Chrome 90+, Firefox 88+, Edge 90+, or Safari 14+
- **RAM:** minimum 4 GB
- **Disk Space:** minimum 500 MB

## Installation and First Launch

### Step 1: Install Dependencies

If you are running the program for the first time, perform the following steps:

1. Make sure **Python 3.8+** is installed on your computer.
   - Check version: open command line and type `python --version`
   
2. Open the program folder.

3. Run the **`install.bat`** file (for Windows) by double-clicking.
   - A command line window will open
   - Python packages and Node.js dependencies will be installed
   - Wait for the "Installation complete" message
   - Press any key to close the window

**For Linux/macOS users:**
```bash
pip install -r requirements.txt
npm install
```

### Step 2: Start the Program

To start working:

1. Run the **`start.bat`** file (double-click).
   
2. A server window will open (do not close it while working).
   - The window will display server operation messages
   - Message "Running on http://127.0.0.1:5000" indicates successful startup

3. Your browser will automatically open with the new program interface.

**If the browser did not open automatically:**

Open the browser manually and enter one of the addresses:

- **New Interface (Vue.js):** `http://localhost:5173` (development) or `http://localhost:5000` (production)
- **Classic Interface:** `http://localhost:5000/vessel_scheduler_complete.html`

**For Linux/macOS users:**
```bash
# In one terminal
python api_server_enhanced.py

# In another terminal (for development)
npm run dev
```

### Stop the Program

- Close the browser window
- In the server window, press `Ctrl+C` to stop
- Or simply close the server window

## Working with the Program

### Interface Overview

The new program interface is built on modern Vue.js architecture and includes:

- **Side Navigation Menu** - quick access to main sections
- **Top Menu** - actions and settings
- **Main Area** - active section content
- **Notification Panel** - important messages and alerts

### Main Sections

####  Dashboard

Starting page with system overview:

- **Statistics** - total number of vessels, cargo, routes
- **Active Voyages** - current operations
- **Notifications** - important events and tasks
- **Quick Actions** - buttons for frequent operations

**How to use:**
- On first login, you will see an empty dashboard
- After adding data, statistics will appear here
- Click on cards to navigate to the corresponding section

---

####  Vessel Management

Section for working with the fleet.

**View vessel list:**
1. Open the "Vessels" section in the menu
2. You will see a table with all fleet vessels
3. Use search and filters for quick lookup

**Add new vessel:**
1. Click the "+ Add Vessel" button
2. Fill in the form:
   - **Vessel ID** - unique identifier
   - **Name** - vessel name
   - **Type** - vessel type (tanker, bulker, etc.)
   - **Deadweight (DWT)** - cargo capacity in tons
   - **Speed** - cruising speed in knots
   - **Fuel Consumption** - consumption in tons/day
3. Click "Save"

**Editing:**
- Click on a vessel in the list to view details
- Click "Edit" to change parameters
- Make changes and save

---

####  Cargo Management

Working with cargo commitments.

**Add cargo:**
1. Open "Cargo" → "+ Add Cargo"
2. Fill in required fields:
   - **Cargo ID** - cargo identifier
   - **Commodity** - cargo type (coal, grain, ore, etc.)
   - **Quantity (MT)** - volume in metric tons
   - **Load Port** - from where
   - **Discharge Port** - to where
   - **Laycan Start** - loading window start
   - **Laycan End** - loading window end
3. Additionally:
   - **Freight Rate** - price per ton
   - **Notes** - additional information
4. Click "Create Cargo"

**Cargo statuses:**
-  **Pending** - awaiting assignment
-  **Assigned** - assigned to vessel
-  **Completed** - transported
- ⭕ **Cancelled** - cancelled

---

####  Route Management

Setting up sea routes between ports.

**Create route:**
1. Open "Routes" → "+ New Route"
2. Specify:
   - **Departure Port**
   - **Destination Port**
   - **Distance (miles)** - sea distance
   - **Straits/canals** - if any
   - **Restrictions** - maximum draft, width, etc.
3. Save route

**Network visualization:**
- Go to the "Network Visualization" tab
- You will see an interactive route map
- Hover over nodes and links for details

---

####  Schedule Generation

Main tool for voyage planning.

**Create schedule:**
1. Open "Voyage Builder"
2. Select mode:
   - **Balakovo** - for river transportation
   - **Deepsea** - for sea voyages
   - **Olya** - specialized routes
3. Click "Generate Schedule"
4. Wait while the system calculates optimal distribution
5. Result will be displayed in Gantt chart

**Gantt Chart:**

Interactive graph of fleet operations by days:

- **Color Legend:**
  -  L - Loading
  -  D - Discharge
  -  T - Transit
  -  B - Ballast
  -  C - Canal
  -  F - Bunker

- **Controls:**
  - Change **Timeline Days** to increase/decrease period
  - Use **Voyage Filter** to filter voyages
  - **Refresh** button updates data
  - **Export** button saves to Excel
  - Hover over cell for operation details

---

####  Financial Analysis

Calculate economic efficiency.

**View analysis:**
1. Open "Finance"
2. Select analysis period
3. System will show:
   - **Total Revenue** - freight sum
   - **Expenses** - bunker, port charges
   - **Profit** - final result
   - **Fleet Efficiency** - vessel utilization

**Export report:**
- Click "Download Report"
- Excel file will be saved to downloads folder

---

####  Reports and Export

**Available reports:**

1. **Gantt Chart** - schedule visualization
2. **Voyage Summary** - table of all operations
3. **Fleet Utilization** - vessel usage analysis
4. **Financial Report** - income and expenses
5. **Berth Utilization** - port capacity usage

**How to export:**
1. Open desired report
2. Click "Export to Excel" or "Download" button
3. Select format (Excel, CSV, PDF)
4. File will save to browser downloads folder

---

### Working with Data

#### Import Data from Files

The system supports import from CSV and Excel files.

**File templates are located in the `input/` folder:**

- `input/deepsea/vessels.csv` - vessels
- `input/deepsea/ports_deepsea.csv` - ports
- `input/deepsea/routes_deepsea.csv` - routes
- `input/deepsea/voyage_plan.csv` - voyage plan
- `sample_data/CargoCommitments.csv` - cargo

**Import process:**

1. Prepare file according to template
2. In the program, select "Import Data"
3. Click "Select File" and specify your file
4. Data will automatically load and validate
5. If there are errors, system will show their list

**Date formats:**
- Use YYYY-MM-DD format (e.g., 2025-01-15)
- Or DD.MM.YYYY format (e.g., 15.01.2025)

#### Backup

**Create backup:**
1. Open "Settings" → "Backup"
2. Click "Create Backup"
3. All data will be exported to ZIP archive

**Restore from backup:**
1. Open "Settings" → "Restore"
2. Select backup file
3. Confirm restoration

#### Clear Data

**Warning:** This operation cannot be undone!

1. Open "Settings" → "Clear Data"
2. Select what to clear:
   - All data
   - Only schedules
   - Only cargo
3. Confirm action

---

## Common Tasks

### Creating Your First Voyage

1. **Add vessel** (if not already added)
   - Vessels → Add Vessel
   - Fill in basic parameters

2. **Add cargo**
   - Cargo → Add Cargo
   - Specify ports and dates

3. **Generate schedule**
   - Voyage Builder → Generate Schedule
   - Select appropriate module

4. **Review result**
   - Check Gantt chart
   - Verify dates and operations

5. **Export report**
   - Reports → Export to Excel

### Analyzing Fleet Performance

1. Open "Financial Analysis"
2. Set date range
3. Review key metrics:
   - Total voyages completed
   - Revenue vs expenses
   - Fleet utilization rate
4. Use filters to drill down

### Optimizing Routes

1. Open "Routes" → "Network Visualization"
2. Identify frequently used routes
3. Check for optimization opportunities:
   - Direct routes vs multi-leg
   - Bunker station locations
   - Port congestion patterns
4. Adjust routes as needed

---

## Troubleshooting

### Server Won't Start

**Problem:** Server shows error on startup

**Solutions:**
- Check if port 5000 is already in use
- Verify Python is installed correctly
- Check if all dependencies are installed
- Try running `install.bat` again

### Browser Shows Blank Page

**Problem:** Page loads but nothing displays

**Solutions:**
- Clear browser cache (Ctrl+Shift+Delete)
- Try different browser
- Check browser console for errors (F12)
- Verify server is running

### Data Not Saving

**Problem:** Changes don't persist after refresh

**Solutions:**
- Check browser localStorage is enabled
- Verify you have disk space available
- Try exporting data as backup
- Clear browser data and re-import

### Import Fails

**Problem:** File import shows errors

**Solutions:**
- Verify file format matches template
- Check date formats (YYYY-MM-DD)
- Ensure all required fields are present
- Look for special characters or encoding issues

---

## Tips and Best Practices

### Data Management

1. **Regular Backups**
   - Export data weekly
   - Keep multiple backup versions
   - Store backups in safe location

2. **Data Validation**
   - Always review imported data
   - Check for duplicate entries
   - Verify dates and numbers

3. **Naming Conventions**
   - Use consistent vessel IDs
   - Standardize port names
   - Keep cargo IDs meaningful

### Performance Optimization

1. **Keep Schedule Scope Reasonable**
   - Don't generate schedules for too long periods
   - Filter data before generating reports
   - Clear old completed voyages regularly

2. **Browser Performance**
   - Close unused tabs
   - Clear cache periodically
   - Use modern browser versions

### Workflow Efficiency

1. **Use Templates**
   - Save frequently used cargo types
   - Create route templates
   - Set up default vessel configurations

2. **Keyboard Shortcuts**
   - Ctrl+S: Save (in forms)
   - Ctrl+F: Search
   - Esc: Close dialogs

---

## Advanced Features

### API Integration

The system provides RESTful API for integration:

**Base URL:** `http://localhost:5000/api`

**Key Endpoints:**
- GET `/vessels` - List all vessels
- POST `/cargo` - Create new cargo
- GET `/schedule/:module` - Generate schedule
- POST `/export/excel` - Export to Excel

**Authentication:**
- Store token in localStorage
- Include in Authorization header

### Custom Modules

The system supports custom calculation modules:

1. Create module in `modules/` directory
2. Implement required interface
3. Register in configuration
4. Access via Voyage Builder

### Batch Operations

For bulk data management:

```bash
# Example: Import multiple files
python scripts/batch_import.py --dir input/bulk/

# Export all data
python scripts/export_all.py --format excel
```

---

## Support and Resources

### Documentation

- **API Reference:** `docs/API_REFERENCE.md`
- **Developer Guide:** `docs/DEVELOPER_GUIDE.md`
- **Module Guides:** 
  - `docs/MODULE_BALAKOVO_EN.md`
  - `docs/MODULE_DEEPSEA_EN.md`
  - `docs/MODULE_OLYA_EN.md`

### Getting Help

- Check troubleshooting section first
- Review error messages in console (F12)
- Consult documentation
- Check system logs in server window

### Version History

**Version 2.0.0** (Current)
- New Vue.js interface
- Enhanced API
- Improved performance
- Bilingual support

**Version 1.0.0**
- Initial release
- Basic scheduling
- Classic interface

---

## Glossary

- **Ballast** - Vessel traveling empty
- **Berth** - Docking location at port
- **DWT** - Deadweight Tonnage, cargo capacity
- **Gantt Chart** - Timeline visualization
- **Laycan** - Loading period window
- **MT** - Metric Ton (1000 kg)
- **Transit** - Vessel traveling with cargo
- **Voyage** - Complete trip from load to discharge

---

**End of User Guide**

*For technical details, see Developer Guide and API Reference documentation.*
