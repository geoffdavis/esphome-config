#!/usr/bin/env python3
"""
Simple test runner for ESPHome security scripts
"""

import unittest
import sys
import os
from pathlib import Path

def main():
    """Run all tests"""
    # Add the project root to the path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(str(start_dir), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(main())