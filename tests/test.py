#!/usr/bin/env python

import unittest
import coverage
import os
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_tests_with_coverage():
    """Run all tests with coverage reporting"""
    
    # Start coverage measurement
    cov = coverage.Coverage(
        source=["src"],  # Measure coverage for the src directory
        omit=["*/__pycache__/*", "*/\__init__\.py"],  # Omit some files
    )
    cov.start()
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)  # Current directory (test/)
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Stop coverage measurement
    cov.stop()
    cov.save()
    
    # Report coverage
    print("\n\n====== Coverage Report ======")
    cov.report()
    
    # Generate HTML report
    html_dir = os.path.join(os.path.dirname(__file__), "coverage_html")
    print(f"\nGenerating HTML report in {html_dir}")
    cov.html_report(directory=html_dir)
    
    # Return test result
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests_with_coverage()
    sys.exit(0 if success else 1)