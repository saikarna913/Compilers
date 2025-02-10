# test_compiler.py
"""
Test suite for the arithmetic compiler.
This script uses the Calculator class from evaluator.py to test
a wide range of arithmetic expressions, including the new operators:
** (exponentiation), rem (remainder), and quot (integer division).
"""

import math
from evaluator import Calculator

def run_valid_tests():
    calculator = Calculator()
    # List of test cases: each is a dict with the expression and the expected value.
    # Floating point comparisons are done with a tolerance.
    test_cases = [
        # Original expressions:
        {"expr": "1 + 2", "expected": 3},
        {"expr": "1 - 2", "expected": -1},
        {"expr": "2 * 3", "expected": 6},
        {"expr": "8 / 4", "expected": 2},
        {"expr": "2 + 3 * 4", "expected": 14},          # 3*4 = 12, then 2+12 = 14
        {"expr": "(2 + 3) * 4", "expected": 20},
        {"expr": "-5 + 3", "expected": -2},
        {"expr": "-5 * -3", "expected": 15},
        {"expr": "-5 * 3", "expected": -15},
        {"expr": "3.5 + 2.5", "expected": 6.0},
        {"expr": "3.5 * 2", "expected": 7.0},
        {"expr": "-3.5 * 2", "expected": -7.0},
        {"expr": "10 / 3", "expected": 10 / 3},
        {"expr": "10 / 3.0", "expected": 10 / 3.0},
        {"expr": "(3 + 5) / 2", "expected": 4},
        {"expr": "-(3 + 5)", "expected": -8},
        {"expr": "+(3 + 5)", "expected": 8},
        {"expr": "3 + -5", "expected": -2},
        {"expr": "(3+4)*(5-2)", "expected": 21},
        {"expr": "-3+-5*8", "expected": -3 + (-5 * 8)},
        {"expr": "3 + 4 * 2 / (1 - 5)", "expected": 3 + 4 * 2 / (1 - 5)},
        {"expr": "  3 +   4 *2/(1-5)  ", "expected": 3 + 4 * 2 / (1 - 5)},
        {"expr": "((3))", "expected": 3},  # nested parentheses
        
        # New test cases for the extended operators:
        {"expr": "2 ** 3", "expected": 8},
        {"expr": "2 ** 3 ** 2", "expected": 512},   # 2 ** (3 ** 2) = 2 ** 9 = 512
        {"expr": "(2 ** 3) ** 2", "expected": 64},   # (2 ** 3) ** 2 = 8 ** 2 = 64
        {"expr": "10 rem 3", "expected": 10 % 3},     # remainder: 10 % 3 = 1
        {"expr": "10 quot 3", "expected": 10 // 3},     # integer division: 10 // 3 = 3
        {"expr": "2 + 3 ** 2 * 4 - 10 rem 3 + 10 quot 3", 
         "expected": 2 + (3 ** 2 * 4) - (10 % 3) + (10 // 3)},
        {"expr": "2 * 3 ** 2", "expected": 2 * (3 ** 2)},   # 2 * 9 = 18
        {"expr": "2 ** 3 * 4", "expected": (2 ** 3) * 4},     # 8 * 4 = 32
        {"expr": "10 + 2 quot 3", "expected": 10 + (2 // 3)}, # 2 // 3 = 0 → 10 + 0 = 10
        {"expr": "10 - 2 rem 3", "expected": 10 - (2 % 3)},   # 2 % 3 = 2 → 10 - 2 = 8
    ]
    
    passed = 0
    failed = 0
    print("Running valid expression tests...\n")
    for case in test_cases:
        expr = case["expr"]
        expected = case["expected"]
        try:
            result = calculator.calculate(expr)
            # Use a tolerance for floating-point comparisons
            if isinstance(expected, float) or isinstance(result, float):
                if abs(result - expected) < 1e-9:
                    print(f"PASSED: {expr} = {result}")
                    passed += 1
                else:
                    print(f"FAILED: {expr}\n  Expected: {expected}\n  Got:      {result}")
                    failed += 1
            else:
                if result == expected:
                    print(f"PASSED: {expr} = {result}")
                    passed += 1
                else:
                    print(f"FAILED: {expr}\n  Expected: {expected}\n  Got:      {result}")
                    failed += 1
        except Exception as e:
            print(f"FAILED: {expr}\n  Raised an unexpected exception: {str(e)}")
            failed += 1
    return passed, failed

def run_error_tests():
    calculator = Calculator()
    # Test cases that are expected to raise errors.
    error_cases = [
        {"expr": "10 / 0", "expected_error": ZeroDivisionError},
        {"expr": "10 quot 0", "expected_error": ZeroDivisionError},
        {"expr": "10 rem 0", "expected_error": ZeroDivisionError},
        {"expr": "5 +", "expected_error": Exception},   # incomplete expression
        {"expr": "(3 + 4", "expected_error": Exception},  # missing closing parenthesis
        {"expr": "", "expected_error": Exception},        # empty expression
        {"expr": "3 $ 4", "expected_error": Exception},   # invalid character
        {"expr": "3..5 + 2", "expected_error": Exception}, # malformed number
    ]
    
    passed = 0
    failed = 0
    print("\nRunning error expression tests...\n")
    for case in error_cases:
        expr = case["expr"]
        expected_error = case["expected_error"]
        try:
            result = calculator.calculate(expr)
            print(f"FAILED: {expr}\n  Expected error {expected_error.__name__}, but got result {result}")
            failed += 1
        except Exception as e:
            if isinstance(e, expected_error):
                print(f"PASSED: {expr} raised {expected_error.__name__} as expected.")
                passed += 1
            else:
                print(f"FAILED: {expr}\n  Raised unexpected error: {type(e).__name__}: {e}")
                failed += 1
    return passed, failed

def main():
    print("=== Arithmetic Compiler Test Suite ===\n")
    valid_passed, valid_failed = run_valid_tests()
    error_passed, error_failed = run_error_tests()
    total_passed = valid_passed + error_passed
    total_failed = valid_failed + error_failed

    print("\n=== Test Summary ===")
    print(f"Valid tests passed: {valid_passed}")
    print(f"Valid tests failed: {valid_failed}")
    print(f"Error tests passed: {error_passed}")
    print(f"Error tests failed: {error_failed}")
    print(f"Total tests passed: {total_passed}")
    print(f"Total tests failed: {total_failed}")

if __name__ == '__main__':
    main()
