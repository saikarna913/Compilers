import unittest
from lexer import Lexer, Token, TokenType

class TestLexer(unittest.TestCase):
    def test_keywords(self):
        source_code = "let x = 10; if (x > 5) { print x; }"
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        expected_tokens = [
            Token(TokenType.LET, "let"),
            Token(TokenType.IDENTIFIER, "x"),
            Token(TokenType.ASSIGN, "="),
            Token(TokenType.NUMBER, "10"),
            Token(TokenType.SEMICOLON, ";"),
            Token(TokenType.IF, "if"),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.IDENTIFIER, "x"),
            Token(TokenType.COMPARISON, ">"),
            Token(TokenType.NUMBER, "5"),
            Token(TokenType.RPAREN, ")"),
            Token(TokenType.LBRACE, "{"),
            Token(TokenType.PRINT, "print"),
            Token(TokenType.IDENTIFIER, "x"),
            Token(TokenType.SEMICOLON, ";"),
            Token(TokenType.RBRACE, "}"),
        ]
        self.assertEqual(tokens, expected_tokens)
    
    def test_numbers_and_operators(self):
        source_code = "5 + 10 * 2 - 3 / 1"
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        expected_tokens = [
            Token(TokenType.NUMBER, "5"),
            Token(TokenType.OPERATOR, "+"),
            Token(TokenType.NUMBER, "10"),
            Token(TokenType.OPERATOR, "*"),
            Token(TokenType.NUMBER, "2"),
            Token(TokenType.OPERATOR, "-"),
            Token(TokenType.NUMBER, "3"),
            Token(TokenType.OPERATOR, "/"),
            Token(TokenType.NUMBER, "1"),
        ]
        self.assertEqual(tokens, expected_tokens)

    def test_strings(self):
        source_code = 'print "Hello, world!"'
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        expected_tokens = [
            Token(TokenType.PRINT, "print"),
            Token(TokenType.STRING, "Hello, world!"),
        ]
        self.assertEqual(tokens, expected_tokens)

    def test_arrays(self):
        source_code = "let arr = [1, 2, 3];"
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        expected_tokens = [
            Token(TokenType.LET, "let"),
            Token(TokenType.IDENTIFIER, "arr"),
            Token(TokenType.ASSIGN, "="),
            Token(TokenType.ARRAY, "[1, 2, 3]"),
            Token(TokenType.SEMICOLON, ";"),
        ]
        self.assertEqual(tokens, expected_tokens)
    
    def test_unexpected_token(self):
        source_code = "@invalid"
        lexer = Lexer(source_code)
        with self.assertRaises(SyntaxError):
            lexer.tokenize()

if __name__ == "__main__":
    unittest.main()
