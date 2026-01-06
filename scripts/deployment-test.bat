@echo off
REM Deployment Testing Script for Windows
REM Tests the production build and deployment readiness

setlocal enabledelayedexpansion

echo =========================================
echo   Deployment Testing Script
echo =========================================
echo.

set TESTS_PASSED=0
set TESTS_FAILED=0

echo Step 1: Environment Check
echo -------------------------------------------

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%i in ('node --version') do set NODE_VERSION=%%i
    echo [32m√[0m Node.js !NODE_VERSION! installed
    set /a TESTS_PASSED+=1
) else (
    echo [31m×[0m Node.js not found
    set /a TESTS_FAILED+=1
)

REM Check npm
where npm >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%i in ('npm --version') do set NPM_VERSION=%%i
    echo [32m√[0m npm !NPM_VERSION! installed
    set /a TESTS_PASSED+=1
) else (
    echo [31m×[0m npm not found
    set /a TESTS_FAILED+=1
)

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [32m√[0m !PYTHON_VERSION! installed
    set /a TESTS_PASSED+=1
) else (
    echo [31m×[0m Python not found
    set /a TESTS_FAILED+=1
)

echo.
echo Step 2: Dependency Check
echo -------------------------------------------

REM Check if node_modules exists
if exist "node_modules\" (
    echo [32m√[0m node_modules directory exists
    set /a TESTS_PASSED+=1
) else (
    echo [33m![0m node_modules not found, installing...
    call npm install
    if %ERRORLEVEL% EQU 0 (
        echo [32m√[0m npm install completed
        set /a TESTS_PASSED+=1
    ) else (
        echo [31m×[0m npm install failed
        set /a TESTS_FAILED+=1
    )
)

echo.
echo Step 3: Code Quality Checks
echo -------------------------------------------

REM TypeScript type check
echo Running TypeScript type check...
call npm run type-check >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m√[0m TypeScript type check passed
    set /a TESTS_PASSED+=1
) else (
    echo [31m×[0m TypeScript type check failed
    set /a TESTS_FAILED+=1
)

REM ESLint check
echo Running ESLint...
call npm run lint >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m√[0m ESLint check passed
    set /a TESTS_PASSED+=1
) else (
    echo [31m×[0m ESLint check failed
    set /a TESTS_FAILED+=1
)

echo.
echo Step 4: Production Build Test
echo -------------------------------------------

REM Clean previous build
if exist "dist\" (
    echo Cleaning previous build...
    rmdir /s /q dist
    if %ERRORLEVEL% EQU 0 (
        echo [32m√[0m Cleaned dist directory
        set /a TESTS_PASSED+=1
    ) else (
        echo [31m×[0m Failed to clean dist directory
        set /a TESTS_FAILED+=1
    )
)

REM Build frontend
echo Building frontend for production...
call npm run build >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m√[0m Frontend build completed
    set /a TESTS_PASSED+=1
    
    REM Check if index.html exists
    if exist "dist\index.html" (
        echo [32m√[0m index.html generated
        set /a TESTS_PASSED+=1
    ) else (
        echo [31m×[0m index.html missing
        set /a TESTS_FAILED+=1
    )
    
    REM Check if assets directory exists
    if exist "dist\assets\" (
        echo [32m√[0m assets directory created
        set /a TESTS_PASSED+=1
    ) else (
        echo [31m×[0m assets directory missing
        set /a TESTS_FAILED+=1
    )
) else (
    echo [31m×[0m Frontend build failed
    set /a TESTS_FAILED+=1
)

echo.
echo Step 5: Configuration Files Check
echo -------------------------------------------

REM Check required files
set FILES=package.json tsconfig.json vite.config.ts config.yaml requirements.txt
for %%f in (%FILES%) do (
    if exist "%%f" (
        echo [32m√[0m Configuration file: %%f
        set /a TESTS_PASSED+=1
    ) else (
        echo [31m×[0m Configuration file missing: %%f
        set /a TESTS_FAILED+=1
    )
)

REM Check .env.example
if exist ".env.example" (
    echo [32m√[0m .env.example exists
    set /a TESTS_PASSED+=1
) else (
    echo [31m×[0m .env.example missing
    set /a TESTS_FAILED+=1
)

echo.
echo Step 6: Security Audit
echo -------------------------------------------

echo Running npm security audit...
call npm audit --production >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [32m√[0m npm security audit passed
    set /a TESTS_PASSED+=1
) else (
    echo [33m![0m Security vulnerabilities found
    echo Run 'npm audit' for details
    set /a TESTS_FAILED+=1
)

echo.
echo Step 7: API Server Check
echo -------------------------------------------

if exist "api_server_enhanced.py" (
    echo [32m√[0m API server file exists
    set /a TESTS_PASSED+=1
) else (
    echo [31m×[0m API server file missing
    set /a TESTS_FAILED+=1
)

echo.
echo Step 8: Module Structure Check
echo -------------------------------------------

REM Check required modules
set MODULES=modules\__init__.py modules\voyage_calculator.py modules\config.py
for %%m in (%MODULES%) do (
    if exist "%%m" (
        echo [32m√[0m Module: %%m
        set /a TESTS_PASSED+=1
    ) else (
        echo [31m×[0m Module missing: %%m
        set /a TESTS_FAILED+=1
    )
)

echo.
echo Step 9: Documentation Check
echo -------------------------------------------

REM Check documentation
if exist "docs\DEVELOPER_GUIDE.md" (
    echo [32m√[0m Documentation: DEVELOPER_GUIDE.md
    set /a TESTS_PASSED+=1
) else (
    echo [31m×[0m Documentation missing: DEVELOPER_GUIDE.md
    set /a TESTS_FAILED+=1
)

if exist "docs\COMPONENT_API.md" (
    echo [32m√[0m Documentation: COMPONENT_API.md
    set /a TESTS_PASSED+=1
) else (
    echo [31m×[0m Documentation missing: COMPONENT_API.md
    set /a TESTS_FAILED+=1
)

if exist "docs\PRODUCTION_DEPLOYMENT.md" (
    echo [32m√[0m Documentation: PRODUCTION_DEPLOYMENT.md
    set /a TESTS_PASSED+=1
) else (
    echo [31m×[0m Documentation missing: PRODUCTION_DEPLOYMENT.md
    set /a TESTS_FAILED+=1
)

echo.
echo =========================================
echo   Test Summary
echo =========================================
echo.
echo Tests Passed: [32m%TESTS_PASSED%[0m
echo Tests Failed: [31m%TESTS_FAILED%[0m
echo.

if %TESTS_FAILED% EQU 0 (
    echo [32m√ All tests passed! Ready for deployment.[0m
    exit /b 0
) else (
    echo [31m× Some tests failed. Please fix issues before deployment.[0m
    exit /b 1
)
