# User Guide

**Version:** 2.0.0  
**Last Updated:** January 2026

## 1. Introduction

The Vessel Scheduling System is a comprehensive web platform designed for managing maritime cargo transportation. It facilitates voyage planning, berth utilization tracking, route optimization, and economic efficiency calculation.

### 1.1 Key Features

*   **Automatic Schedule Generation**: Optimize fleet schedules automatically.
*   **Interactive Gantt Charts**: Visualize schedules and operations.
*   **Management Modules**: Dedicated tools for Cargo, Vessel, and Route management.
*   **Financial Analysis**: Detailed reporting on revenue, expenses, and profit.
*   **Network Visualization**: Interactive maps for route analysis.
*   **Data Export**: Seamless export capabilities to Excel and PDF.
*   **Modern Interface**: Responsive Vue.js-based web interface.

The application operates within a web browser (Chrome, Edge, or Firefox recommended). All data is stored locally on the user's machine, ensuring data privacy. An internet connection is required only for the initial setup.

## 2. System Requirements

*   **Operating System**: Windows 10/11, macOS, Linux
*   **Python**: Version 3.8 or higher
*   **Node.js**: Version 16 or higher (required for development)
*   **Browser**: Chrome 90+, Firefox 88+, Edge 90+, or Safari 14+
*   **RAM**: Minimum 4 GB
*   **Disk Space**: Minimum 500 MB

## 3. Installation and First Launch

### 3.1 Step 1: Install Dependencies

To set up the application for the first time:

1.  Ensure **Python 3.8+** is installed. Verify by running `python --version` in the command line.
2.  Navigate to the program directory.
3.  **Windows Users**: Double-click the `install.bat` file.
    *   A command line window will appear.
    *   Wait for the "Installation complete" message.
    *   Press any key to close the window.
4.  **Linux/macOS Users**: Run the following commands in the terminal:
    ```bash
    pip install -r requirements.txt
    npm install
    ```

### 3.2 Step 2: Start the Program

To launch the application:

1.  **Windows Users**: Double-click the `start.bat` file.
2.  A server window will open. **Do not close this window** as it maintains the application server.
    *   Successful startup is indicated by the message: "Running on http://127.0.0.1:5000".
3.  The default web browser will automatically open the application interface.

**Manual Access**:
If the browser does not open automatically, navigate to:
*   **New Interface**: `http://localhost:5173` (Development) or `http://localhost:5000` (Production)
*   **Classic Interface**: `http://localhost:5000/vessel_scheduler_complete.html`

**Linux/macOS Launch**:
```bash
# Terminal 1: Start Backend
python api_server_enhanced.py

# Terminal 2: Start Frontend (Development)
npm run dev
```

### 3.3 Stopping the Program

To shut down the application:
1.  Close the browser tab.
2.  In the server window, press `Ctrl+C` or close the window directly.

## 4. Interface Overview

The interface is designed for efficiency and ease of use, featuring:

*   **Side Navigation Menu**: Provides quick access to all modules.
*   **Top Menu**: Contains global settings and user actions.
*   **Main Workspace**: Displays the active module's content.
*   **Notification Panel**: Shows system alerts and status updates.

### 4.1 Dashboard

The Dashboard provides a high-level overview of the system status:

*   **Statistics**: Summary counts of vessels, cargo, and routes.
*   **Active Voyages**: Real-time status of current operations.
*   **Notifications**: Alerts regarding schedule conflicts or required actions.
*   **Quick Actions**: Shortcuts to frequently used functions.

### 4.2 Vessel Management

This module handles the fleet database.

**Viewing the Vessel List**:
1.  Navigate to the "Vessels" section.
2.  The table displays all registered vessels.
3.  Use the search bar and filters to locate specific vessels.

**Adding a New Vessel**:
1.  Click the "Add Vessel" button.
2.  Complete the vessel details form:
    *   **Vessel ID**: Unique identifier.
    *   **Name**: Official vessel name.
    *   **Type**: Classification (e.g., Tanker, Bulker).
    *   **Deadweight (DWT)**: Cargo capacity in metric tons.
    *   **Speed**: Service speed in knots.
    *   **Fuel Consumption**: Daily consumption in tons.
3.  Click "Save" to confirm.

**Editing Vessel Details**:
1.  Select a vessel from the list.
2.  Click "Edit" to modify parameters.
3.  Save changes to update the record.

### 4.3 Cargo Management

Manage cargo commitments and orders.

**Adding Cargo**:
1.  Navigate to "Cargo" and click "Add Cargo".
2.  Enter the required information:
    *   **Cargo ID**: Unique reference number.
    *   **Commodity**: Type of cargo (e.g., Coal, Grain).
    *   **Quantity (MT)**: Volume in metric tons.
    *   **Load Port**: Port of origin.
    *   **Discharge Port**: Port of destination.
    *   **Laycan Start/End**: Agreed loading window.
3.  Optional fields include Freight Rate and Notes.
4.  Click "Create Cargo".

**Cargo Status Definitions**:
*   **Pending**: Awaiting vessel assignment.
*   **Assigned**: Scheduled for transport.
*   **Completed**: Transport finished.
*   **Cancelled**: Order withdrawn.

### 4.4 Route Management

Configure maritime routes and constraints.

**Creating a Route**:
1.  Navigate to "Routes" and click "New Route".
2.  Define the route parameters:
    *   **Departure/Destination Ports**: Origin and destination.
    *   **Distance**: Sea distance in nautical miles.
    *   **Straits/Canals**: Transit points (e.g., Suez, Panama).
    *   **Restrictions**: Draft or beam limitations.
3.  Save the route configuration.

**Network Visualization**:
Access the "Network Visualization" tab to view an interactive map of the route network, displaying nodes (ports) and links (routes).

### 4.5 Schedule Generation

The core planning tool for voyage scheduling.

**Generating a Schedule**:
1.  Open the "Voyage Builder" module.
2.  Select the operational region:
    *   **Balakovo**: River transportation.
    *   **Deepsea**: International sea voyages.
    *   **Olya**: Specialized regional routes.
3.  Click "Generate Schedule".
4.  The system calculates the optimal assignment and displays the results in a Gantt chart.

**Gantt Chart Operations**:
*   **Timeline**: Visual representation of vessel activities.
*   **Legend**:
    *   **L**: Loading
    *   **D**: Discharge
    *   **T**: Transit (Laden)
    *   **B**: Ballast (Empty)
    *   **C**: Canal Transit
    *   **F**: Bunkering (Refueling)
*   **Controls**: Adjust timeline scale, filter by vessel, refresh data, or export to Excel.

### 4.6 Financial Analysis

Analyze the economic performance of the fleet.

**Viewing Reports**:
1.  Navigate to the "Finance" section.
2.  Select the analysis period.
3.  Review key metrics:
    *   **Total Revenue**: Gross freight earnings.
    *   **Expenses**: Operational costs (fuel, port dues).
    *   **Profit**: Net earnings.
    *   **Fleet Efficiency**: Utilization percentage.

**Exporting Reports**:
Click "Download Report" to generate a detailed Excel statement.

### 4.7 Reports and Export

The system offers various reporting formats:

1.  **Gantt Chart**: Schedule visualization.
2.  **Voyage Summary**: Tabular data of all operations.
3.  **Fleet Utilization**: Analysis of vessel usage.
4.  **Financial Report**: Income and expense breakdown.
5.  **Berth Utilization**: Port capacity analysis.

**Export Procedure**:
1.  Select the desired report type.
2.  Click "Export" or "Download".
3.  Choose the format (Excel, CSV, PDF).
4.  The file will be saved to the default downloads directory.

## 5. Data Management

### 5.1 Importing Data

The system supports bulk data import via CSV and Excel files. Templates are located in the `input/` directory.

**Key Templates**:
*   `input/deepsea/vessels.csv`: Vessel registry.
*   `input/deepsea/ports_deepsea.csv`: Port database.
*   `input/deepsea/routes_deepsea.csv`: Route definitions.
*   `sample_data/CargoCommitments.csv`: Cargo orders.

**Import Steps**:
1.  Prepare the data file using the standard template.
2.  In the application, select "Import Data".
3.  Upload the file.
4.  The system validates the data and reports any errors.

**Date Format**: Use `YYYY-MM-DD` (e.g., 2025-01-15) or `DD.MM.YYYY`.

### 5.2 Backup and Restore

**Creating a Backup**:
1.  Go to "Settings" > "Backup".
2.  Click "Create Backup".
3.  Data is exported as a ZIP archive.

**Restoring Data**:
1.  Go to "Settings" > "Restore".
2.  Upload the backup ZIP file.
3.  Confirm the restoration process.

### 5.3 Clearing Data

**Warning**: This action is irreversible.
1.  Go to "Settings" > "Clear Data".
2.  Select the scope (All Data, Schedules Only, Cargo Only).
3.  Confirm deletion.

## 6. Troubleshooting

### 6.1 Server Startup Issues
*   **Symptom**: Error message during startup.
*   **Resolution**:
    *   Ensure port 5000 is free.
    *   Verify Python installation.
    *   Re-run `install.bat` to check dependencies.

### 6.2 Interface Display Issues
*   **Symptom**: Blank page or rendering errors.
*   **Resolution**:
    *   Clear browser cache (`Ctrl+Shift+Delete`).
    *   Try a different browser.
    *   Check the browser console (`F12`) for errors.

### 6.3 Data Persistence Issues
*   **Symptom**: Changes lost after refresh.
*   **Resolution**:
    *   Ensure browser LocalStorage is enabled.
    *   Check available disk space.

## 7. Glossary

*   **Ballast**: Voyage leg where the vessel travels empty to a loading port.
*   **Berth**: Designated location in a port for mooring vessels.
*   **DWT (Deadweight Tonnage)**: Total weight a ship can carry, including cargo, fuel, and stores.
*   **Gantt Chart**: A bar chart that illustrates a project schedule.
*   **Laycan**: The period during which the shipowner must tender the ship for loading.
*   **MT**: Metric Ton (1,000 kg).
*   **Transit**: Voyage leg where the vessel travels with cargo.
*   **Voyage**: A complete shipping cycle including loading, transit, and discharge.

---
*For technical implementation details, please refer to the Developer Guide and API Reference.*
