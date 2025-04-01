import unittest
from src.lexer import Token, INTEGER, PLUS, MINUS, LET, RETURN, PRINT, IF, WHILE, FOR, IDENTIFIER, EQUALS, STRING, TRUE, FALSE, QUESTION_MARK, COLON, LBRACKET, RBRACKET, LPAREN, FUNC, RPAREN
from src.ast_1 import (AST, BinOp, UnaryOp, Integer, Float, String, Boolean, Var, VarAssign, VarReassign, Block,
                  If, While, For, FuncDef, Return, FuncCall, Print, Array, Dict, ConditionalExpr,
                  RepeatUntil, Match, MatchCase, Lambda, ArrayAccess, ArrayAssign, AstPrinter)

class TestAST(unittest.TestCase):
    def setUp(self):
        self.printer = AstPrinter()

    def assertPrint(self, node, expected_output):
        result = self.printer.print(node)
        self.assertEqual(result, expected_output)

    # Base AST and Visitor
    def test_ast_base(self):
        node = AST()
        with self.assertRaises(AttributeError):  # No specific visitor method for base AST
            node.accept(self.printer)

    # Binary Operation
    def test_bin_op(self):
        left = Integer(5)
        right = Integer(3)
        op = Token(PLUS, '+', 1)
        node = BinOp(left, op, right)
        self.assertPrint(node, "(+ 5 3)")

    # Unary Operation
    def test_unary_op(self):
        right = Integer(5)
        op = Token(MINUS, '-', 1)
        node = UnaryOp(op, right)
        self.assertPrint(node, "(- 5)")

    # Literals
    def test_integer(self):
        node = Integer(42)
        self.assertPrint(node, "42")

    def test_float(self):
        node = Float(3.14)
        self.assertPrint(node, "3.14")

    def test_string(self):
        node = String("hello")
        self.assertPrint(node, '"hello"')

    def test_boolean(self):
        node = Boolean(True)
        self.assertPrint(node, "True")
        node = Boolean(False)
        self.assertPrint(node, "False")

    # Variable Nodes
    def test_var(self):
        token = Token(IDENTIFIER, "x", 1)
        node = Var("x", token)
        self.assertPrint(node, "x")

    def test_var_assign(self):
        token = Token(LET, "let", 1)
        node = VarAssign("x", Integer(5), token)
        self.assertPrint(node, "(let x 5)")

    def test_var_reassign(self):
        token = Token(EQUALS, '=', 1)
        node = VarReassign("x", Integer(10), token)
        self.assertPrint(node, "(assign x 10)")

    # Block
    def test_block(self):
        node = Block([VarAssign("x", Integer(5), Token(LET, "let", 1)),
                      Print(Integer(5), Token(PRINT, "print", 1))])
        self.assertPrint(node, "(block (let x 5) (print 5))")

    # Control Flow
    def test_if(self):
        condition = BinOp(Var("x", Token(IDENTIFIER, "x", 1)), Token(PLUS, '+', 1), Integer(1))
        then_branch = Block([Print(String("yes"), Token(PRINT, "print", 1))])
        else_branch = Block([Print(String("no"), Token(PRINT, "print", 1))])
        node = If(condition, then_branch, else_branch)
        self.assertPrint(node, "(if (+ x 1) (block (print \"yes\")) (block (print \"no\")))")

    def test_if_no_else(self):
        node = If(Integer(1), Block([Print(String("yes"), Token(PRINT, "print", 1))]))
        self.assertPrint(node, "(if 1 (block (print \"yes\")))")

    def test_while(self):
        node = While(Boolean(True), Block([Print(Integer(1), Token(PRINT, "print", 1))]))
        self.assertPrint(node, "(while True (block (print 1)))")

    def test_for(self):
        node = For("i", Integer(0), Integer(5), Block([Print(Var("i", Token(IDENTIFIER, "i", 1)), Token(PRINT, "print", 1))]))
        self.assertPrint(node, "(for i 0 5 (block (print i)))")

    # Function Nodes
    def test_func_def(self):
        node = FuncDef("add", ["x", "y"], Block([Return(BinOp(Var("x", Token(IDENTIFIER, "x", 1)), Token(PLUS, '+', 1), Var("y", Token(IDENTIFIER, "y", 1))), Token(RETURN, "return", 1))]), token=Token(FUNC, "func", 1))
        self.assertPrint(node, "(func add x y (block (return (+ x y))))")

    def test_func_call(self):
        node = FuncCall(Var("add", Token(IDENTIFIER, "add", 1)), [Integer(2), Integer(3)], Token(RPAREN, ')', 1))
        self.assertPrint(node, "(call add 2 3)")

    def test_return(self):
        node = Return(Integer(42), Token(RETURN, "return", 1))
        self.assertPrint(node, "(return 42)")

    # Print
    def test_print(self):
        node = Print(String("hello"), Token(PRINT, "print", 1))
        self.assertPrint(node, "(print \"hello\")")

    # Array and Dictionary
    def test_array(self):
        node = Array([Integer(1), Integer(2), Integer(3)])
        self.assertPrint(node, "(array 1 2 3)")

    def test_array_access(self):
        node = ArrayAccess(Var("arr", Token(IDENTIFIER, "arr", 1)), Integer(0))
        self.assertPrint(node, "(array-access arr 0)")

    def test_array_assign(self):
        node = ArrayAssign(Var("arr", Token(IDENTIFIER, "arr", 1)), Integer(0), Integer(5))
        self.assertPrint(node, "(array-assign arr 0 5)")

    def test_dict(self):
        node = Dict([(String("a"), Integer(1)), (String("b"), Integer(2))])
        self.assertPrint(node, "(dict (pair \"a\" 1) (pair \"b\" 2))")

    # Conditional Expression
    def test_conditional_expr(self):
        node = ConditionalExpr(Boolean(True), Integer(1), Integer(0))
        self.assertPrint(node, "(if-else 1 True 0)")

    # Repeat Until
    def test_repeat_until(self):
        node = RepeatUntil(Block([Print(Integer(1), Token(PRINT, "print", 1))]), Boolean(False))
        self.assertPrint(node, "(repeat-until (block (print 1)) False)")

    # Match
    def test_match(self):
        cases = [MatchCase(Integer(1), Print(String("one"), Token(PRINT, "print", 1))),
                 MatchCase(Integer(2), Print(String("two"), Token(PRINT, "print", 1)))]
        node = Match(Integer(5), cases)
        self.assertPrint(node, "(match 5 (case 1 (print \"one\")) (case 2 (print \"two\")))")

    # Lambda
    def test_lambda(self):
        node = Lambda(["x"], Block([Return(Var("x", Token(IDENTIFIER, "x", 1)), Token(RETURN, "return", 1))]), Token(FUNC, "func", 1))
        self.assertPrint(node, "(lambda (x) (block (return x)))")

if __name__ == "__main__":
    unittest.main()