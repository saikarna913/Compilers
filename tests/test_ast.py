import unittest
import sys
import os

# Add the parent directory to the path so we can import lexer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.lexer.lexer import Token, PLUS, LET, ASSIGN, IDENTIFIER, FUNC, MINUS
from src.AST.ast_1 import (AST, BinOp, UnaryOp, Integer, Float, Boolean, String, Array, Dict, Var, VarAssign,
                           VarReassign, Block, If, While, For, Break, Continue, FuncDef, FuncCall, Return, Print,
                           AstPrinter)

class TestAST(unittest.TestCase):
    def test_integer_node(self):
        node = Integer(42)
        self.assertEqual(node.value, 42)
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "42")

    def test_float_node(self):
        node = Float(3.14)
        self.assertEqual(node.value, 3.14)
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "3.14")

    def test_boolean_node(self):
        node = Boolean(True)
        self.assertEqual(node.value, True)
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "True")

    def test_string_node(self):
        node = String("hello")
        self.assertEqual(node.value, "hello")
        printer = AstPrinter()
        self.assertEqual(printer.print(node), '"hello"')

    def test_array_node(self):
        node = Array([Integer(1), Integer(2)])
        self.assertEqual(len(node.elements), 2)
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(array 1 2)")

    def test_dict_node(self):
        node = Dict([(String("key"), Integer(42))])
        self.assertEqual(len(node.pairs), 1)
        printer = AstPrinter()
        self.assertEqual(printer.print(node), '(dict (pair "key" 42))')

    def test_bin_op_node(self):
        token = Token(PLUS, '+', 1)
        node = BinOp(Integer(5), token, Integer(3))
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(+ 5 3)")

    def test_unary_op_node(self):
        token = Token(MINUS, '-', 1)
        node = UnaryOp(token, Integer(5))
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(- 5)")

    def test_var_assign_node(self):
        token = Token(LET, 'let', 1)
        node = VarAssign("x", Integer(5), token)
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(let x 5)")

    def test_var_reassign_node(self):
        token = Token(ASSIGN, 'assign', 1)
        node = VarReassign("x", Integer(10), token)
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(assign x 10)")

    def test_block_node(self):
        node = Block([VarAssign("x", Integer(5), Token(LET, 'let', 1))])
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(block (let x 5))")

    def test_if_node(self):
        node = If(Boolean(True), Block([]), Block([]))
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(if True (block) (block))")

    def test_while_node(self):
        node = While(Boolean(True), Block([]))
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(while True (block))")

    def test_for_node(self):
        node = For("i", Integer(1), Integer(5), Block([]), Integer(2))
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(for i 1 5 (block)) 2")

    def test_func_def_node(self):
        token = Token(FUNC, 'func', 1)
        node = FuncDef("counter", [], Block([]), token=token)
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(func counter  (block))")

    def test_func_call_node(self):
        token = Token(IDENTIFIER, 'add', 1)
        node = FuncCall(Var("add", token), [Integer(1), Integer(2)], token)
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(call add 1 2)")

    def test_return_node(self):
        node = Return(Integer(5))
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(return 5)")

    def test_print_node(self):
        node = Print(Integer(5))
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(print 5)")

    def test_break_node(self):
        node = Break()
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(break)")

    def test_continue_node(self):
        node = Continue()
        printer = AstPrinter()
        self.assertEqual(printer.print(node), "(continue)")

if __name__ == "__main__":
    unittest.main()