# tests/language/test_cond.py
import unittest
from unittest.mock import patch
from src.lexer import Lexer
from src.parser import Parser
from src.evaluator import Evaluator, FluxRuntimeError

class TestConditionals(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator()

    def run_program(self, code):
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()
        return self.evaluator.interpret(ast)

    # Test basic if statement with True condition
    def test_if_true(self):
        code = """
        if (True) {
            print "Condition is true"
        }
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("Condition is true")

    # Test basic if statement with False condition
    def test_if_false(self):
        code = """
        if (False) {
            print "Condition is true"
        }
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_not_called()

    # Test if-else statement with True condition
    def test_if_else_true(self):
        code = """
        if (True) {
            print "True branch"
        } else {
            print "False branch"
        }
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("True branch")

    # Test if-else statement with False condition
    def test_if_else_false(self):
        code = """
        if (False) {
            print "True branch"
        } else {
            print "False branch"
        }
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("False branch")

    # Test nested if statements
    def test_nested_if(self):
        code = """
        let x = 10
        if (x > 5) {
            if (x < 15) {
                print "x is between 5 and 15"
            }
        }
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("x is between 5 and 15")

    # Test conditions with comparison operators
    def test_comparison_operators(self):
        code = """
        let x = 42
        if (x < 50) {
            print "x < 50"
        }
        if (x > 40) {
            print "x > 40"
        }
        if (x <= 42) {
            print "x <= 42"
        }
        if (x >= 42) {
            print "x >= 42"
        }
        if (x == 42) {
            print "x == 42"
        }
        if (x != 43) {
            print "x != 43"
        }
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_any_call("x < 50")
            mock_print.assert_any_call("x > 40")
            mock_print.assert_any_call("x <= 42")
            mock_print.assert_any_call("x >= 42")
            mock_print.assert_any_call("x == 42")
            mock_print.assert_any_call("x != 43")

    # Test conditions with logical operators
    def test_logical_operators(self):
        code = """
        let x = 10
        let y = 20
        if (x < 15 and y > 15) {
            print "Both conditions true"
        }
        if (x > 15 or y > 15) {
            print "At least one condition true"
        }
        if (not x == 15) {
            print "x is not 15"
        }
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_any_call("Both conditions true")
            mock_print.assert_any_call("At least one condition true")
            mock_print.assert_any_call("x is not 15")

    # Test complex conditions
    def test_complex_conditions(self):
        code = """
        let x = 5
        let y = 10
        if (x < 10 and (y > 5 or x == 5)) {
            print "Complex condition true"
        }
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("Complex condition true")

    # Test if with else-if (simulated with nested if-else)
    def test_else_if(self):
        code = """
        let x = 15
        if (x < 10) {
            print "x < 10"
        } else {
            if (x < 20) {
                print "x < 20"
            } else {
                print "x >= 20"
            }
        }
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("x < 20")

    # Test non-boolean condition (error case)
    def test_non_boolean_condition(self):
        code = """
        let x = 42
        if (x) {
            print "This should fail"
        }
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Condition must evaluate to a boolean", str(cm.exception))

    # Test undefined variable in condition (error case)
    def test_undefined_variable_in_condition(self):
        code = """
        if (undefined_var == 42) {
            print "This should fail"
        }
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Undefined variable", str(cm.exception))

    # Test invalid comparison (e.g., string vs number)
    def test_invalid_comparison(self):
        code = """
        let s = "text"
        let n = 42
        if (s == n) {
            print "This should fail"
        }
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Cannot compare string with number", str(cm.exception))

if __name__ == "__main__":
    unittest.main()