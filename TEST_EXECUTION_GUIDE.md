# Comprehensive Test Suite - Execution Guide

## Overview

This document provides instructions for running the comprehensive test suite for the Vessel Scheduler System. The test suite covers:

1. **API Endpoints with Real Data** - Tests all major API endpoints
2. **End-to-End Voyage Creation Workflow** - Complete workflow from data upload to export
3. **Calendar Data Loading from All Modules** - Tests Olya, DeepSea, and Balakovo modules
4. **Year Schedule Generation with Optimization** - Tests optimization strategies
5. **PDF Export from Various Views** - Tests PDF report generation

## Prerequisites

### 1. Install Dependencies

```bash
pip install requests pandas numpy openpyxl reportlab
```

### 2. Start the API Server

Before running tests, you must start the API server:

**Option A: Standard Server**
```bash
python api_server.py
```

**Option B: Enhanced Server**
```bash
python api_server_enhanced.py
```

The server should be running on `http://localhost:5000`

## Running the Tests

### Run Complete Test Suite

```bash
python test_comprehensive_suite.py
```

### Run Individual Test Categories

You can also run the existing individual test files:

```bash
# Test PDF Reports
python test_pdf_reports.py

# Test Calendar Events
python test_calendar_events.py

# Test Year Schedule API
python test_year_schedule_api.py
```

## Test Categories

### Category 1: API Endpoints with Real Data

Tests the following endpoints:
- `GET /api/health` - Health check
- `GET /api/vessels` - Retrieve vessel data
- `GET /api/cargo` - Retrieve cargo data
- `GET /api/dashboard/stats` - Dashboard statistics
- `POST /api/calculate` - Calculate schedules
- `GET /api/gantt-data` - Retrieve Gantt chart data

**Expected Results:**
- All endpoints should return HTTP 200
- Response data should contain expected fields
- No server errors

### Category 2: End-to-End Voyage Creation Workflow

Tests the complete workflow:
1. Upload vessel data
2. Upload cargo data
3. Generate schedule
4. Calculate voyages
5. Export to Excel

**Expected Results:**
- All upload operations should succeed
- Schedule generation should complete without errors
- Excel export should create valid files

### Category 3: Calendar Data Loading from All Modules

Tests calendar event endpoints for each module:
- `GET /api/calendar/events` - All events
- `GET /api/calendar/events?module=olya` - Olya module events
- `GET /api/calendar/events?module=deepsea` - DeepSea module events
- `GET /api/calendar/events?module=balakovo` - Balakovo module events
- Date range filtering
- Status filtering
- Error handling for invalid modules

**Expected Results:**
- Each module should return its specific events
- Filters should work correctly
- Invalid parameters should return appropriate errors

### Category 4: Year Schedule Generation with Optimization

Tests optimization strategies:
- Max Revenue strategy
- Min Cost strategy
- Balanced strategy
- List schedules
- Detect conflicts
- Compare strategies

**Test Endpoints:**
- `POST /api/schedule/year` - Generate optimized schedule
- `GET /api/schedule/year?list=true` - List all schedules
- `POST /api/schedule/year/conflicts` - Detect conflicts
- `POST /api/schedule/year/compare` - Compare strategies

**Expected Results:**
- Each strategy should generate valid schedules
- KPIs should be calculated correctly
- Optimality scores should be between 0-100
- Conflict detection should identify issues

### Category 5: PDF Export from Various Views

Tests PDF report generation:
- Comprehensive Voyage Report
- Fleet Analysis Report
- Schedule Timeline Report
- Financial Analysis Report

**Expected Results:**
- Each report type should generate a valid PDF file
- Files should be saved to `output/test_results/`
- PDF files should contain expected data visualizations

## Test Output

### Console Output

The test suite provides detailed console output:
-  PASSED - Test succeeded
-  FAILED - Test failed
-  WARNING - Partial success

### Test Report

A detailed JSON report is saved to:
```
output/test_results/test_report_<timestamp>.json
```

The report includes:
- Summary statistics
- Individual test results
- Pass/fail rates
- Execution times
- Error details

## Example Output

```
================================================================================
 COMPREHENSIVE TEST SUITE FOR VESSEL SCHEDULER SYSTEM
================================================================================

Test Date: 2025-12-29 09:00:00
API Base URL: http://localhost:5000/api
Output Directory: output/test_results

================================================================================
TEST CATEGORY 1: API ENDPOINTS WITH REAL DATA
================================================================================
   PASSED: API Health Check
    Status: healthy
    Duration: 0.05s
   PASSED: Get Vessels Endpoint
    Retrieved 15 vessels
    Duration: 0.12s
  ...

  Category 1 Results: 6/6 tests passed

================================================================================
 COMPREHENSIVE TEST SUMMARY
================================================================================

 API Endpoints:
   Passed: 6/6 (100.0%)

 E2E Voyage Workflow:
   Passed: 5/5 (100.0%)

 Calendar Data Loading:
   Passed: 7/7 (100.0%)

 Year Schedule Generation:
   Passed: 6/6 (100.0%)

 PDF Exports:
   Passed: 4/4 (100.0%)

--------------------------------------------------------------------------------

OVERALL RESULTS:
  Total Tests: 28
  Passed: 28
  Failed: 0
  Success Rate: 100.0%

 ALL TESTS PASSED!
================================================================================
```

## Troubleshooting

### API Server Not Running

**Error:**
```
 ERROR: API server is not running!
```

**Solution:**
Start the API server before running tests:
```bash
python api_server.py
```

### Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
Install required dependencies:
```bash
pip install -r requirements.txt
```

### PDF Generation Fails

**Error:**
```
 Skipping PDF tests - PDF reporter module not available
```

**Solution:**
Ensure ReportLab is installed:
```bash
pip install reportlab
```

### Connection Timeout

**Error:**
```
Exception: Connection timeout
```

**Solution:**
1. Check if the API server is running
2. Verify the server is accessible at `http://localhost:5000`
3. Check firewall settings

## Test Data

The test suite uses:
- Sample vessel data (generated)
- Sample cargo data (generated)
- Real data from `input/` directory (for actual calculations)

## Continuous Integration

To integrate with CI/CD pipelines:

```bash
# Start server in background
python api_server.py &
SERVER_PID=$!

# Wait for server to be ready
sleep 5

# Run tests
python test_comprehensive_suite.py

# Capture exit code
TEST_EXIT_CODE=$?

# Stop server
kill $SERVER_PID

# Exit with test result
exit $TEST_EXIT_CODE
```

## Test Coverage

The test suite provides comprehensive coverage:

| Category | Endpoints/Features | Tests | Coverage |
|----------|-------------------|-------|----------|
| API Endpoints | 6 endpoints | 6 tests | 100% |
| Voyage Workflow | 5 steps | 5 tests | 100% |
| Calendar Events | 7 scenarios | 7 tests | 100% |
| Year Schedule | 6 features | 6 tests | 100% |
| PDF Exports | 4 report types | 4 tests | 100% |
| **Total** | **28 features** | **28 tests** | **100%** |

## Best Practices

1. **Always start the API server first**
2. **Review test output carefully** - Look for patterns in failures
3. **Check generated files** - Verify Excel and PDF outputs manually
4. **Save test reports** - Keep historical test results for comparison
5. **Run tests after changes** - Ensure modifications don't break functionality

## Next Steps

After running tests:
1. Review the JSON test report in `output/test_results/`
2. Examine any failed tests
3. Check generated files (Excel, PDF) for correctness
4. Fix any issues and re-run tests
5. Update this guide if new tests are added

## Support

For issues or questions:
- Review error messages in console output
- Check `logs/` directory for server logs
- Review `test_report_*.json` for detailed test results
- Consult API documentation in `docs/API_REFERENCE.md`
