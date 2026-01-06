#!/bin/bash

# Deployment Testing Script
# Tests the production build and deployment readiness

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "  Deployment Testing Script"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

echo "Step 1: Environment Check"
echo "-------------------------------------------"

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION installed"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Node.js not found"
    ((TESTS_FAILED++))
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm $NPM_VERSION installed"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} npm not found"
    ((TESTS_FAILED++))
fi

# Check Python
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION installed"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} Python not found"
    ((TESTS_FAILED++))
fi

echo ""
echo "Step 2: Dependency Check"
echo "-------------------------------------------"

cd "$PROJECT_DIR"

# Check if node_modules exists
if [ -d "node_modules" ]; then
    print_result 0 "node_modules directory exists"
else
    echo -e "${YELLOW}!${NC} node_modules not found, installing..."
    npm install
    print_result $? "npm install"
fi

# Check if Python venv exists
if [ -d "venv" ] || [ -d ".venv" ]; then
    print_result 0 "Python virtual environment exists"
else
    echo -e "${YELLOW}!${NC} Virtual environment not found (optional)"
fi

echo ""
echo "Step 3: Code Quality Checks"
echo "-------------------------------------------"

# TypeScript type check
echo "Running TypeScript type check..."
npm run type-check > /dev/null 2>&1
print_result $? "TypeScript type check"

# ESLint check
echo "Running ESLint..."
npm run lint > /dev/null 2>&1
print_result $? "ESLint check"

# Python tests (if pytest is available)
if command -v pytest &> /dev/null; then
    echo "Running Python tests..."
    pytest --quiet > /dev/null 2>&1
    print_result $? "Python unit tests"
else
    echo -e "${YELLOW}!${NC} pytest not installed, skipping Python tests"
fi

echo ""
echo "Step 4: Production Build Test"
echo "-------------------------------------------"

# Clean previous build
if [ -d "dist" ]; then
    echo "Cleaning previous build..."
    rm -rf dist
    print_result $? "Clean dist directory"
fi

# Build frontend
echo "Building frontend for production..."
npm run build > /dev/null 2>&1
BUILD_RESULT=$?

if [ $BUILD_RESULT -eq 0 ]; then
    print_result 0 "Frontend build"
    
    # Check if critical files exist
    if [ -f "dist/index.html" ]; then
        print_result 0 "index.html generated"
    else
        print_result 1 "index.html missing"
    fi
    
    # Check if assets directory exists
    if [ -d "dist/assets" ]; then
        print_result 0 "assets directory created"
    else
        print_result 1 "assets directory missing"
    fi
    
    # Check build size
    DIST_SIZE=$(du -sh dist 2>/dev/null | cut -f1)
    echo "  Build size: $DIST_SIZE"
    
else
    print_result 1 "Frontend build"
fi

echo ""
echo "Step 5: Configuration Files Check"
echo "-------------------------------------------"

# Check if required config files exist
REQUIRED_FILES=(
    "package.json"
    "tsconfig.json"
    "vite.config.ts"
    "config.yaml"
    "requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_result 0 "Configuration file: $file"
    else
        print_result 1 "Configuration file missing: $file"
    fi
done

# Check for .env.example
if [ -f ".env.example" ]; then
    print_result 0 ".env.example exists"
else
    print_result 1 ".env.example missing"
fi

echo ""
echo "Step 6: Security Audit"
echo "-------------------------------------------"

# npm audit
echo "Running npm security audit..."
npm audit --production > /dev/null 2>&1
AUDIT_RESULT=$?

if [ $AUDIT_RESULT -eq 0 ]; then
    print_result 0 "npm security audit (no vulnerabilities)"
else
    echo -e "${YELLOW}!${NC} Security vulnerabilities found, run 'npm audit' for details"
    print_result 1 "npm security audit"
fi

echo ""
echo "Step 7: API Server Check"
echo "-------------------------------------------"

# Check if API server file exists
if [ -f "api_server_enhanced.py" ]; then
    print_result 0 "API server file exists"
    
    # Try to import as syntax check
    python -c "import ast; ast.parse(open('api_server_enhanced.py').read())" 2>/dev/null
    print_result $? "API server Python syntax"
else
    print_result 1 "API server file missing"
fi

echo ""
echo "Step 8: Static File Check"
echo "-------------------------------------------"

# Check if important static files exist
STATIC_FILES=(
    "index.html"
    "styles.css"
    "README.md"
)

for file in "${STATIC_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_result 0 "Static file: $file"
    else
        echo -e "${YELLOW}!${NC} Optional file missing: $file"
    fi
done

echo ""
echo "Step 9: Module Structure Check"
echo "-------------------------------------------"

# Check if required modules exist
REQUIRED_MODULES=(
    "modules/__init__.py"
    "modules/voyage_calculator.py"
    "modules/config.py"
)

for module in "${REQUIRED_MODULES[@]}"; do
    if [ -f "$module" ]; then
        print_result 0 "Module: $module"
    else
        print_result 1 "Module missing: $module"
    fi
done

echo ""
echo "Step 10: Documentation Check"
echo "-------------------------------------------"

# Check if documentation exists
DOCS=(
    "docs/DEVELOPER_GUIDE.md"
    "docs/COMPONENT_API.md"
    "docs/PRODUCTION_DEPLOYMENT.md"
    "РУКОВОДСТВО_ПОЛЬЗОВАТЕЛЯ.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        print_result 0 "Documentation: $doc"
    else
        print_result 1 "Documentation missing: $doc"
    fi
done

echo ""
echo "========================================="
echo "  Test Summary"
echo "========================================="
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! Ready for deployment.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please fix issues before deployment.${NC}"
    exit 1
fi
