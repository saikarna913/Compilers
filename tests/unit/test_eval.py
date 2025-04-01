import unittest
from unittest.mock import patch  # Import mock explicitly
from src.lexer import Lexer, Token, PLUS, MINUS, MULTIPLY, DIVIDE, INTEGER, IDENTIFIER, LET, PRINT, IF, RETURN, EQUALS, TRUE, FALSE, LBRACKET, RBRACKET
from src.parser import Parser
from src.ast_1 import (Block, Integer, BinOp, UnaryOp, VarAssign, Var, Print, If, VarReassign, Return, FuncDef, FuncCall, Array, ArrayAccess, ArrayAssign, Boolean, ConditionalExpr)
from src.evaluator import Evaluator, FluxRuntimeError, Environment, Function, BuiltinFunction

class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator()

    def parse_and_evaluate(self, code):
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()
        return self.evaluator.interpret(ast)

    def test_integer(self):
        node = Integer(42)
        result = self.evaluator.evaluate(node)
        self.assertEqual(result, 42)

    def test_bin_op(self):
        node = BinOp(Integer(5), Token(PLUS, '+', 1), Integer(3))
        result = self.evaluator.evaluate(node)
        self.assertEqual(result, 8)

        node = BinOp(Integer(10), Token(MINUS, '-', 1), Integer(4))
        result = self.evaluator.evaluate(node)
        self.assertEqual(result, 6)

        node = BinOp(Integer(2), Token(MULTIPLY, '*', 1), Integer(3))
        result = self.evaluator.evaluate(node)
        self.assertEqual(result, 6)

        node = BinOp(Integer(6), Token(DIVIDE, '/', 1), Integer(2))
        result = self.evaluator.evaluate(node)
        self.assertEqual(result, 3.0)

    def test_bin_op_division_by_zero(self):
        node = BinOp(Integer(5), Token(DIVIDE, '/', 1), Integer(0))
        with self.assertRaises(FluxRuntimeError) as cm:
            self.evaluator.evaluate(node)
        self.assertIn("Division by zero", str(cm.exception))

    def test_unary_op(self):
        node = UnaryOp(Token(MINUS, '-', 1), Integer(5))
        result = self.evaluator.evaluate(node)
        self.assertEqual(result, -5)

    def test_var_assign_and_access(self):
        code = "let x = 5\nx"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 5)

    def test_var_reassign(self):
        code = "let x = 5\nx = 10\nx"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 10)

    def test_undefined_variable(self):
        node = Var("x", Token(IDENTIFIER, "x", 1))
        with self.assertRaises(FluxRuntimeError) as cm:
            self.evaluator.evaluate(node)
        self.assertIn("Undefined variable 'x'", str(cm.exception))

    def test_print(self):
        with patch('builtins.print') as mock_print:
            code = "print 42"
            self.parse_and_evaluate(code)
            mock_print.assert_called_with("42")

    def test_if(self):
        with patch('builtins.print') as mock_print:
            code = "if (True) { print 1 } else { print 0 }"
            self.parse_and_evaluate(code)
            mock_print.assert_called_with("1")

        with patch('builtins.print') as mock_print:
            code = "if (False) { print 1 } else { print 0 }"
            self.parse_and_evaluate(code)
            mock_print.assert_called_with("0")

    def test_while(self):
        code = "let x = 0\nwhile (x < 3) { x = x + 1 }\nx"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 3)

    def test_for(self):
        code = "let sum = 0\nfor (let i = 0 to 3) { sum = sum + i }\nsum"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 6)  # 0 + 1 + 2 + 3

    def test_function_definition_and_call(self):
        code = "func add(x, y) { return x + y }\nadd(2, 3)"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 5)

    def test_function_wrong_args(self):
        code = "func add(x, y) { return x + y }\nadd(2)"
        with self.assertRaises(FluxRuntimeError) as cm:
            self.parse_and_evaluate(code)
        self.assertIn("Expected 2 arguments, got 1", str(cm.exception))

    def test_array(self):
        code = "let arr = [1, 2, 3]\narr"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, [1, 2, 3])

    def test_array_access(self):
        code = "let arr = [1, 2, 3]\narr[1]"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 2)

    def test_array_assign(self):
        code = "let arr = [1, 2, 3]\narr[1] = 5\narr[1]"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 5)

    def test_array_out_of_bounds(self):
        code = "let arr = [1, 2, 3]\narr[5]"
        with self.assertRaises(FluxRuntimeError) as cm:
            self.parse_and_evaluate(code)
        self.assertIn("Array index 5 out of bounds", str(cm.exception))

    def test_conditional_expr(self):
        code = "True ? 1 : 0"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 1)

        code = "False ? 1 : 0"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 0)

    def test_builtin_len(self):
        code = "let arr = [1, 2, 3]\nlen(arr)"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 3)

        code = 'len("abc")'
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 3)

    def test_environment_scoping(self):
        code = "let x = 1\n{ let x = 2 }\nx"
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 1)

    def test_tail_call_optimization(self):
        code = """
        func fact(n, acc) { 
            if (n <= 1) { return acc } 
            else { return fact(n - 1, n * acc) } 
        }
        fact(5, 1)
        """
        result = self.parse_and_evaluate(code)
        self.assertEqual(result, 120)

if __name__ == "__main__":
    unittest.main()