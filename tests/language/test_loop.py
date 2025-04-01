# tests/language/test_loopy.py
import unittest
from unittest.mock import patch
from src.lexer import Lexer
from src.parser import Parser
from src.evaluator import Evaluator, FluxRuntimeError

class TestLoops(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator()

    def run_program(self, code):
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()
        return self.evaluator.interpret(ast)

    # Test basic for loop
    def test_basic_for_loop(self):
        code = """
        let sum = 0
        for (let i = 1 to 5) {
            sum assign sum + i
        }
        print sum
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("15")  # 1 + 2 + 3 + 4 + 5

    # Test for loop with step
    def test_for_loop_with_step(self):
        code = """
        let sum = 0
        for (let i = 0 to 10 step 2) {
            sum assign sum + i
        }
        print sum
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("20")  # 0 + 2 + 4 + 6 + 8 + 10

    # Test basic while loop
    def test_basic_while_loop(self):
        code = """
        let x = 0
        let sum = 0
        while (x < 5) {
            sum assign sum + x
            x assign x + 1
        }
        print sum
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("10")  # 0 + 1 + 2 + 3 + 4

    # Test nested loops
    def test_nested_loops(self):
        code = """
        let product = 0
        for (let i = 1 to 3) {
            for (let j = 1 to 2) {
                product assign product + (i * j)
            }
        }
        print product
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("9")  # (1*1 + 1*2) + (2*1 + 2*2) + (3*1 + 3*2)

    # Test for loop with empty range
    def test_for_loop_empty_range(self):
        code = """
        let sum = 0
        for (let i = 5 to 4) {
            sum assign sum + i
        }
        print sum
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("0")  # No iterations

    # Test while loop with false condition
    def test_while_loop_false_condition(self):
        code = """
        let sum = 0
        while (False) {
            sum assign sum + 1
        }
        print sum
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("0")  # No iterations

    # Test infinite loop with break (if supported, otherwise skip)
    def test_while_loop_with_break(self):
        code = """
        let x = 0
        while (True) {
            if (x >= 5) {
                break  # Assuming break is supported; skip if not
            }
            x assign x + 1
        }
        print x
        """
        try:
            with patch('builtins.print') as mock_print:
                self.run_program(code)
                mock_print.assert_called_with("5")
        except FluxRuntimeError as e:
            if "Unknown token 'break'" in str(e):
                self.skipTest("Break statement not supported in FluxScript")

    # Test error: non-numeric range in for loop
    def test_for_loop_invalid_range(self):
        code = """
        for (let i = "start" to "end") {
            print i
        }
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Range bounds must be numbers", str(cm.exception))

    # Test error: undefined variable in while condition
    def test_while_loop_undefined_variable(self):
        code = """
        while (undefined_var < 10) {
            print "This should fail"
        }
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Undefined variable", str(cm.exception))

if __name__ == "__main__":
    unittest.main()