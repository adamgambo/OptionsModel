# run_tests.py
import unittest
import sys
import os

def run_tests():
    """Run all unit tests and return success status."""
    # Add project root to path
    sys.path.insert(0, os.path.abspath('.'))
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return True if successful, False otherwise
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    
    # Use appropriate exit code
    sys.exit(0 if success else 1)