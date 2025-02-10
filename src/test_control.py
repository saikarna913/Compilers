# test_compiler_control.py
"""
Test suite for control statements:
- Comparison Operators: <, >, <=, >=, ==, !=
- Logical Operators: and, or, not
- Assignment Operators: let (for declaration) and assign (for reassigning)
"""

import traceback
from evaluator import Lexer, Parser, Interpreter

class PersistentCalculator:
    """
    A persistent calculator that reuses the same interpreter
    so that variable declarations and reassignments persist.
    """
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
    test_cases = [
        # Comparison tests:
        {"expr": "10 < 20", "expected": True},
        {"expr": "10 > 20", "expected": False},
        {"expr": "10 <= 10", "expected": True},
        {"expr": "10 >= 11", "expected": False},
        {"expr": "10 == 10", "expected": True},
        {"expr": "10 != 20", "expected": True},
        
        # Logical tests:
        {"expr": "True and False", "expected": False},
        {"expr": "True or False", "expected": True},
        {"expr": "not False", "expected": True},
        {"expr": "not True", "expected": False},
        {"expr": "10 < 20 and 20 < 30", "expected": True},
        {"expr": "10 < 20 or 20 < 10", "expected": True},
        {"expr": "not (10 < 20)", "expected": False},
        
        # Assignment tests:
        {"expr": "let x = 10", "expected": 10},
        {"expr": "x", "expected": 10},
        {"expr": "x assign 20", "expected": 20},
        {"expr": "x == 20", "expected": True},
        {"expr": "let y = 5", "expected": 5},
        {"expr": "y assign 6", "expected": 6},
        {"expr": "y < 10 and y != 5", "expected": True},
        {"expr": "let a = 10", "expected": 10},
        {"expr": "a assign 15", "expected": 15},
        {"expr": "a > 10 and a < 20", "expected": True},
    ]
    passed = 0
    failed = 0
    print("Running valid control tests...\n")
    for case in test_cases:
        expr = case["expr"]
        expected = case["expected"]
        try:
            result = calc.calculate(expr)
            if result == expected:
                print(f"PASSED: {expr} = {result}")
                passed += 1
            else:
                print(f"FAILED: {expr}\n  Expected: {expected}\n  Got: {result}")
                failed += 1
        except Exception as e:
            print(f"FAILED: {expr}\n  Raised unexpected exception: {e}")
            failed += 1
    return passed, failed

def run_error_tests():
    calc = PersistentCalculator()
    test_cases = [
        # Reassignment without prior declaration:
        {"expr": "z assign 30", "expected_error": "Variable 'z' is not declared."},
        # Malformed comparison:
        {"expr": "let z = 10 < ", "expected_error": "Invalid syntax"},
        # Incomplete logical expression:
        {"expr": "10 < 20 and", "expected_error": "Invalid syntax"},
    ]
    passed = 0
    failed = 0
    print("\nRunning error control tests...\n")
    for case in test_cases:
        expr = case["expr"]
        expected_error = case["expected_error"]
        try:
            result = calc.calculate(expr)
            print(f"FAILED: {expr}\n  Expected error containing '{expected_error}', but got result: {result}")
            failed += 1
        except Exception as e:
            if expected_error in str(e):
                print(f"PASSED: {expr} raised expected error: {e}")
                passed += 1
            else:
                print(f"FAILED: {expr}\n  Expected error containing '{expected_error}', but got: {e}")
                failed += 1
    return passed, failed

def main():
    print("=== Compiler Control Statements Test Suite ===\n")
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
