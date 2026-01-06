#!/usr/bin/env python3
"""
Comprehensive Test Runner with Coverage Analysis

Runs all test suites and generates coverage report.
Target: >80% code coverage

Usage:
    python run_all_tests.py                 # Run all tests
    python run_all_tests.py --coverage      # Run with coverage report
    python run_all_tests.py --verbose       # Verbose output
    python run_all_tests.py --module=tests/test_conflict_detection.py  # Run specific module
"""

import subprocess
import sys
import os
from pathlib import Path


def print_banner():
    """Print test runner banner."""
    print("\n" + "="*80)
    print(" COMPREHENSIVE TEST SUITE RUNNER")
    print(" Testing: Filters, Calendar, Conflicts, Costs, PDF Reports")
    print("="*80 + "\n")


def run_python_tests(verbose=False, coverage=False, specific_module=None):
    """Run Python tests with pytest."""
    print("="*80)
    print(" Running Python Tests (pytest)")
    print("="*80 + "\n")
    
    cmd = ["pytest"]
    
    if coverage:
        cmd.extend([
            "--cov=modules",
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    if specific_module:
        cmd.append(specific_module)
    else:
        # Run all Python test files
        cmd.extend([
            "tests/test_conflict_detection.py",
            "tests/test_cost_allocation.py",
            "tests/test_pdf_reports_enhanced.py",
            "tests/"  # Include any other tests in tests/ dir
        ])
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print(" pytest not found. Please install with: pip install pytest pytest-cov")
        return False


def run_typescript_tests(verbose=False):
    """Run TypeScript/JavaScript tests with vitest."""
    print("\n" + "="*80)
    print(" Running TypeScript Tests (vitest)")
    print("="*80 + "\n")
    
    cmd = ["npm", "run", "test"]
    
    if verbose:
        cmd.append("--")
        cmd.append("--reporter=verbose")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print(" npm not found. TypeScript tests skipped.")
        return None  # Return None to indicate test was skipped, not failed


def generate_coverage_report():
    """Generate and display coverage summary."""
    print("\n" + "="*80)
    print(" COVERAGE ANALYSIS")
    print("="*80 + "\n")
    
    # Check if coverage HTML report was generated
    coverage_dir = Path("htmlcov")
    if coverage_dir.exists():
        print(f" Detailed coverage report available at:")
        print(f"   file:///{coverage_dir.absolute()}/index.html\n")
    
    print("To view coverage report:")
    print("  1. Open htmlcov/index.html in your browser")
    print("  2. Or run: python -m http.server 8000 --directory htmlcov")
    print("     Then open http://localhost:8000\n")


def print_summary(python_passed, ts_passed):
    """Print test execution summary."""
    print("\n" + "="*80)
    print(" TEST EXECUTION SUMMARY")
    print("="*80 + "\n")
    
    # Python tests
    if python_passed is not None:
        status = " PASSED" if python_passed else " FAILED"
        print(f"Python Tests (pytest):      {status}")
    else:
        print("Python Tests (pytest):      ⏭  SKIPPED")
    
    # TypeScript tests
    if ts_passed is not None:
        status = " PASSED" if ts_passed else " FAILED"
        print(f"TypeScript Tests (vitest):  {status}")
    else:
        print("TypeScript Tests (vitest):  ⏭  SKIPPED")
    
    print("\n" + "-"*80)
    
    # Overall result
    all_passed = (python_passed if python_passed is not None else True) and \
                 (ts_passed if ts_passed is not None else True)
    
    if all_passed:
        print("\n ALL TESTS PASSED!")
        print("\nTest Coverage:")
        print("   GlobalFiltersBar state management")
        print("   Calendar view switching logic")
        print("   Schedule conflict detection algorithm")
        print("   Cost allocation calculations")
        print("   PDF report generation (all 4 types)")
    else:
        print("\n  SOME TESTS FAILED")
        print("Please review the output above for details.")
    
    print("\n" + "="*80 + "\n")
    
    return all_passed


def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run comprehensive test suite")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--python-only", action="store_true", help="Run only Python tests")
    parser.add_argument("--ts-only", action="store_true", help="Run only TypeScript tests")
    parser.add_argument("--module", help="Run specific test module")
    
    args = parser.parse_args()
    
    print_banner()
    
    python_passed = None
    ts_passed = None
    
    # Run Python tests
    if not args.ts_only:
        python_passed = run_python_tests(
            verbose=args.verbose,
            coverage=args.coverage,
            specific_module=args.module
        )
        
        if args.coverage and python_passed:
            generate_coverage_report()
    
    # Run TypeScript tests
    if not args.python_only and args.module is None:
        ts_passed = run_typescript_tests(verbose=args.verbose)
    
    # Print summary
    all_passed = print_summary(python_passed, ts_passed)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
