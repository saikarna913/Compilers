import unittest
from src.lexer import Lexer, Token, EOF, INTEGER, FLOAT, STRING, PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, LT, GT, LTE, GTE, EQEQ, NOTEQ, AND, OR, NOT, EQUALS, LET, ASSIGN, IDENTIFIER, IF, ELSE, WHILE, FOR, IN, TO, REPEAT, UNTIL, MATCH, ARROW, FUNC, RETURN, PRINT, LPAREN, RPAREN, LBRACE, RBRACE, LBRACKET, RBRACKET, COMMA, COLON, QUESTION_MARK, TRUE, FALSE, STEP
from src.parser import Parser, ParseError
from src.ast_1 import (AST, BinOp, UnaryOp, Integer, Float, String, Boolean, Var, VarAssign, 
                      VarReassign, Block, If, While, For, FuncDef, Return, FuncCall, Print, 
                      Array, Dict, ConditionalExpr, RepeatUntil, Match, MatchCase, ArrayAccess,
                      ArrayAssign)

class TestParser(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def assertAST(self, node, expected_type, **kwargs):
        self.assertIsInstance(node, expected_type)
        for attr, value in kwargs.items():
            self.assertEqual(getattr(node, attr), value)

    def test_let_statement(self):
        parser = Parser(Lexer("let x = 5"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], VarAssign, name="x")
        self.assertAST(ast.statements[0].value, Integer, value=5)

    def test_let_missing_equals(self):
        parser = Parser(Lexer("let x 5"))
        with self.assertRaises(ParseError):
            parser.parse()

    def test_if_statement(self):
        parser = Parser(Lexer("if (x > 0) { print x } else { print 0 }"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], If)
        self.assertAST(ast.statements[0].condition, BinOp)
        self.assertAST(ast.statements[0].then_branch, Block)
        self.assertAST(ast.statements[0].else_branch, Block)

    def test_if_no_else(self):
        parser = Parser(Lexer("if (x > 0) { print x }"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], If)
        self.assertIsNone(ast.statements[0].else_branch)

    def test_while_statement(self):
        parser = Parser(Lexer("while (x > 0) { print x }"))
        ast = parser.parse()
        self.assertTrue(len(ast.statements) > 0)
        if len(ast.statements) > 0:
            self.assertAST(ast.statements[0], While)
            self.assertAST(ast.statements[0].condition, BinOp)
            self.assertAST(ast.statements[0].body, Block)

    def test_for_statement(self):
        parser = Parser(Lexer("for (let i = 0 to 10) { print i }"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], For)
        self.assertEqual(ast.statements[0].var_name, "i")
        self.assertAST(ast.statements[0].start, Integer, value=0)
        self.assertAST(ast.statements[0].end, Integer, value=10)
        self.assertIsNone(ast.statements[0].step)

    def test_for_with_step(self):
        parser = Parser(Lexer("for (let i = 0 to 10 step 2) { print i }"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], For)
        self.assertEqual(ast.statements[0].var_name, "i")
        self.assertAST(ast.statements[0].step, Integer, value=2)

    def test_function_definition(self):
        parser = Parser(Lexer("func add(a, b) { return a + b }"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], FuncDef)
        self.assertEqual(ast.statements[0].name, "add")
        self.assertEqual(ast.statements[0].params, ["a", "b"])
        self.assertAST(ast.statements[0].body, Block)

    def test_return_statement(self):
        parser = Parser(Lexer("return 5"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], Return)
        self.assertAST(ast.statements[0].value, Integer, value=5)

    def test_print_statement(self):
        parser = Parser(Lexer("print \"Hello\""))
        ast = parser.parse()
        self.assertAST(ast.statements[0], Print)
        self.assertAST(ast.statements[0].expression, String, value="Hello")

    def test_variable_reassign(self):
        parser = Parser(Lexer("x = 5"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], VarReassign, name="x")
        self.assertAST(ast.statements[0].value, Integer, value=5)

    def test_conditional_expression(self):
        parser = Parser(Lexer("x > 0 ? 1 : 0"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], ConditionalExpr)
        self.assertAST(ast.statements[0].condition, BinOp)
        self.assertAST(ast.statements[0].then_expr, Integer, value=1)
        self.assertAST(ast.statements[0].else_expr, Integer, value=0)

    def test_array_literal(self):
        parser = Parser(Lexer("[1, 2, 3]"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], Array)
        self.assertEqual(len(ast.statements[0].elements), 3)

    def test_array_access(self):
        parser = Parser(Lexer("arr[0]"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], ArrayAccess)
        self.assertAST(ast.statements[0].array, Var)
        self.assertAST(ast.statements[0].index, Integer, value=0)

    def test_array_assign(self):
        parser = Parser(Lexer("arr[0] = 5"))
        ast = parser.parse()
        self.assertAST(ast.statements[0], ArrayAssign)
        self.assertAST(ast.statements[0].array, Var)
        self.assertAST(ast.statements[0].index, Integer, value=0)
        self.assertAST(ast.statements[0].value, Integer, value=5)

    def test_parse_error_recovery(self):
        parser = Parser(Lexer("let x = 5\nlet y =\nlet z = 10"))
        ast = parser.parse()
        self.assertEqual(len(ast.statements), 2)
        self.assertAST(ast.statements[0], VarAssign, name="x")
        self.assertAST(ast.statements[1], VarAssign, name="z")

    def test_missing_closing_brace(self):
        parser = Parser(Lexer("if (x > 0) { print x"))
        with self.assertRaises(ParseError):
            parser.parse()

if __name__ == "__main__":
    unittest.main()