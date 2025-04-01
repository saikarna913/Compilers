# tests/language/test_func.py
import unittest
from unittest.mock import patch
from src.lexer import Lexer
from src.parser import Parser
from src.evaluator import Evaluator, FluxRuntimeError

class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator()

    def run_program(self, code):
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()
        return self.evaluator.interpret(ast)

    # Test basic function definition and call
    def test_basic_function(self):
        code = """
        func add(a, b) {
            return a + b
        }
        print add(3, 4)
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("7")

    # Test recursive function (factorial)
    def test_recursive_function(self):
        code = """
        func factorial(n) {
            if (n <= 1) {
                return 1
            }
            return n * factorial(n - 1)
        }
        print factorial(5)
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("120")

    # Test first-class functions (assigning function to variable)
    def test_first_class_function(self):
        code = """
        func multiply(a, b) {
            return a * b
        }
        let mult = multiply
        print mult(6, 7)
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("42")

    # Test first-class functions (passing function as argument)
    def test_function_as_argument(self):
        code = """
        func apply(f, x, y) {
            return f(x, y)
        }
        func add(a, b) {
            return a + b
        }
        print apply(add, 10, 20)
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("30")

    # Test proper closures (counter example)
    def test_closure(self):
        code = """
        func counter() {
            let count = 0
            return func() {
                count assign count + 1
                return count
            }
        }
        let c = counter()
        print c()
        print c()
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_any_call("1")
            mock_print.assert_any_call("2")

    # Test "Man or Boy" test for proper closures and call stack handling
    def test_man_or_boy(self):
        code = """
        func A(k, x1, x2, x3, x4, x5) {
            func B() {
                k assign k - 1
                return A(k, B, x1, x2, x3, x4)
            }
            if (k <= 0) {
                return x4() + x5()
            }
            return B()
        }
        func K(n) {
            return func() { return n }
        }
        print A(10, K(1), K(-1), K(-1), K(0), K(0))
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("67")  # Expected result for k=10

    # Test tail-call elimination (large recursion without stack overflow)
    def test_tail_call_elimination(self):
        code = """
        func tail_sum(n, acc) {
            if (n <= 0) {
                return acc
            }
            return tail_sum(n - 1, acc + n)
        }
        print tail_sum(10000, 0)
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("50005000")  # Sum of 1 to 10000

    # Test error: undefined function call
    def test_undefined_function(self):
        code = """
        print unknown_func(42)
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Undefined function", str(cm.exception))

    # Test error: wrong number of arguments
    def test_wrong_number_of_arguments(self):
        code = """
        func add(a, b) {
            return a + b
        }
        print add(1)
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Expected 2 arguments, got 1", str(cm.exception))

if __name__ == "__main__":
    unittest.main()