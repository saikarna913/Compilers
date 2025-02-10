"""
Test suite for variables and data types (numbers and booleans) in the extended compiler.
This suite uses a persistent interpreter so that variables declared with the
'let' keyword persist across evaluations.
"""

import math
import traceback
from lexer import Lexer
from parser import Parser
from evaluator import Interpreter

class PersistentCalculator:
    def __init__(self):
        self.interpreter = Interpreter()

    def calculate(self, expression: str):
        try:
            lexer = Lexer(expression)
            parser = Parser(lexer)
            tree = parser.parse()
            result = self.interpreter.interpret(tree)
            return result
        except Exception as e:
            traceback.print_exc()
            raise

def run_valid_tests():
    calc = PersistentCalculator()
    # List of valid test cases
    test_cases = [
        # Simple numeric and boolean literals
        {"expr": "10", "expected": 10},
        {"expr": "3.14", "expected": 3.14},
        {"expr": "True", "expected": True},
        {"expr": "False", "expected": False},

        # Variable declarations with let and subsequent usage
        {"expr": "let x = 10", "expected": 10},
        {"expr": "x", "expected": 10},
        {"expr": "let y = 3.14", "expected": 3.14},
        {"expr": "y * 2", "expected": 6.28},
        {"expr": "let flag = True", "expected": True},
        {"expr": "flag", "expected": True},

        # More complex expressions involving variables
        {"expr": "let a = 5", "expected": 5},
        {"expr": "let b = a + 2", "expected": 7},
        {"expr": "a * b", "expected": 35},
        {"expr": "let c = (a + b) * 2", "expected": 24},
        {"expr": "c - a", "expected": 19},
    ]

    passed = 0
    failed = 0
    print("Running valid tests for variables and data types...\n")
    for case in test_cases:
        expr = case["expr"]
        expected = case["expected"]
        try:
            result = calc.calculate(expr)
            # For floating-point comparisons, use a tolerance
            if isinstance(expected, float):
                if math.isclose(result, expected, rel_tol=1e-9):
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
            print(f"FAILED: {expr}\n  Raised unexpected exception: {e}")
            failed += 1
    print(f"\nValid tests: {passed} passed, {failed} failed.\n")
    return passed, failed

def run_error_tests():
    calc = PersistentCalculator()
    # Error test cases. These should raise exceptions.
    test_cases = [
        # Using an undefined variable
        {"expr": "z", "expected_error": "Undefined variable"},
        # Malformed let statement: identifier expected (here "1x" is not a valid identifier)
        {"expr": "let 1x = 10", "expected_error": "Invalid syntax"},
        # Syntax error: missing expression after equals
        {"expr": "let w =", "expected_error": "Invalid syntax"},
        # Error in expression: unmatched parenthesis
        {"expr": "(10 + 5", "expected_error": "Invalid syntax"},
    ]

    passed = 0
    failed = 0
    print("Running error tests for variables and data types...\n")
    for case in test_cases:
        expr = case["expr"]
        expected_error = case["expected_error"]
        try:
            result = calc.calculate(expr)
            print(f"FAILED: {expr}\n  Expected error containing '{expected_error}', but got result: {result}")
            failed += 1
        except Exception as e:
            if expected_error in str(e):
                print(f"PASSED: {expr}\n  Raised expected error: {e}")
                passed += 1
            else:
                print(f"FAILED: {expr}\n  Expected error containing '{expected_error}', but got: {e}")
                failed += 1
    print(f"\nError tests: {passed} passed, {failed} failed.\n")
    return passed, failed

def main():
    print("=== Extended Compiler Test Suite (Variables & Data Types) ===\n")
    valid_passed, valid_failed = run_valid_tests()
    error_passed, error_failed = run_error_tests()
    total_passed = valid_passed + error_passed
    total_failed = valid_failed + error_failed

    print("=== Test Summary ===")
    print(f"Valid tests passed: {valid_passed}")
    print(f"Valid tests failed: {valid_failed}")
    print(f"Error tests passed: {error_passed}")
    print(f"Error tests failed: {error_failed}")
    print(f"Total tests passed: {total_passed}")
    print(f"Total tests failed: {total_failed}")

if __name__ == '__main__':
    main()
