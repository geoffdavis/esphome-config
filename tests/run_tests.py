#!/usr/bin/env python3
"""
Test Runner for ESPHome Security Framework

Runs all unit tests and provides comprehensive test reporting.
Supports different test modes and coverage reporting.
"""

import sys
import os
import unittest
import argparse
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

def discover_tests(test_dir="tests", pattern="test_*.py"):
    """Discover all test files in the test directory"""
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / test_dir if test_dir != "tests" else Path(__file__).parent
    suite = loader.discover(str(start_dir), pattern=pattern)
    return suite

def run_tests(verbosity=2, failfast=False, pattern="test_*.py"):
    """Run all discovered tests"""
    print("=" * 70)
    print("ESPHome Security Framework Test Suite")
    print("=" * 70)

    # Discover tests
    suite = discover_tests(pattern=pattern)

    # Count tests
    test_count = suite.countTestCases()
    print(f"Discovered {test_count} test cases")
    print()

    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        stream=sys.stdout
    )

    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}")

    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}")

    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")

    return result.wasSuccessful()

def run_specific_test(test_name, verbosity=2):
    """Run a specific test module or test case"""
    print(f"Running specific test: {test_name}")

    try:
        # Try to load as module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_name)

        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)

        return result.wasSuccessful()
    except Exception as e:
        print(f"Error running test {test_name}: {e}")
        return False

def check_test_environment():
    """Check if the test environment is properly set up"""
    print("Checking test environment...")

    # Check if scripts directory exists
    scripts_dir = Path(__file__).parent.parent / "scripts"
    if not scripts_dir.exists():
        print("❌ Scripts directory not found")
        return False

    # Check if security_lib.py exists
    security_lib = scripts_dir / "security_lib.py"
    if not security_lib.exists():
        print("❌ security_lib.py not found")
        return False

    # Try to import security_lib
    try:
        import security_lib
        print("✅ security_lib imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import security_lib: {e}")
        return False

    # Check test files
    test_files = [
        "test_security_lib.py",
        "test_scripts.py"
    ]

    for test_file in test_files:
        test_path = Path(__file__).parent / test_file
        if test_path.exists():
            print(f"✅ {test_file} found")
        else:
            print(f"❌ {test_file} not found")
            return False

    print("✅ Test environment is ready")
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ESPHome Security Framework Test Runner")
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=2,
        help="Increase verbosity (use -v, -vv, or -vvv)"
    )
    parser.add_argument(
        "--failfast", "-f",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--pattern", "-p",
        default="test_*.py",
        help="Test file pattern (default: test_*.py)"
    )
    parser.add_argument(
        "--test", "-t",
        help="Run specific test (module.TestClass.test_method)"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check test environment and exit"
    )
    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="List all available tests and exit"
    )

    args = parser.parse_args()

    # Check environment if requested
    if args.check_env:
        success = check_test_environment()
        sys.exit(0 if success else 1)

    # List tests if requested
    if args.list_tests:
        print("Discovering tests...")
        suite = discover_tests(pattern=args.pattern)

        def list_tests_in_suite(suite, indent=0):
            for test in suite:
                if hasattr(test, '_tests'):
                    # Test suite
                    print("  " * indent + str(test))
                    list_tests_in_suite(test, indent + 1)
                else:
                    # Individual test
                    print("  " * indent + str(test))

        list_tests_in_suite(suite)
        sys.exit(0)

    # Check environment before running tests
    if not check_test_environment():
        print("❌ Test environment check failed")
        sys.exit(1)

    # Run specific test if requested
    if args.test:
        success = run_specific_test(args.test, args.verbose)
        sys.exit(0 if success else 1)

    # Run all tests
    success = run_tests(
        verbosity=args.verbose,
        failfast=args.failfast,
        pattern=args.pattern
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
