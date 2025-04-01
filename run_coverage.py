# run_coverage.py
import coverage
import unittest
import os

cov = coverage.Coverage(source=['src'])  
cov.start()

project_root = os.path.dirname(os.path.abspath(__file__))

# Initialize test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

language_dir = os.path.join(project_root, 'tests', 'language')
suite.addTests(loader.discover(language_dir, pattern='test_*.py', top_level_dir=project_root))

# Discover tests in tests/euler
euler_dir = os.path.join(project_root, 'tests', 'euler')
suite.addTests(loader.discover(euler_dir, pattern='test_*.py', top_level_dir=project_root))

# Discover tests in tests/unit
unit_dir = os.path.join(project_root, 'tests', 'unit')
suite.addTests(loader.discover(unit_dir, pattern='test_*.py', top_level_dir=project_root))

# Run the tests
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Stop coverage and generate the report
cov.stop()
cov.save()

# Generate a terminal report
cov.report(show_missing=True)

# Generate an HTML report
cov.html_report(directory='htmlcov')

# Check if tests passed
if result.wasSuccessful():
    print("\nAll tests passed successfully!")
else:
    print("\nSome tests failed. Check the output above for details.")
    exit(1)