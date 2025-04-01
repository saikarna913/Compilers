import unittest
from src.lexer import Lexer, Token, LexerError, EOF, INTEGER, FLOAT, STRING, PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, LT, GT, LTE, GTE, EQEQ, NOTEQ, AND, OR, NOT, EQUALS, LET, ASSIGN, IDENTIFIER, IF, ELSE, WHILE, FOR, IN, TO, REPEAT, UNTIL, MATCH, ARROW, FUNC, RETURN, PRINT, LPAREN, RPAREN, LBRACE, RBRACE, LBRACKET, RBRACKET, COMMA, COLON, QUESTION_MARK, TRUE, FALSE, STEP

class TestLexer(unittest.TestCase):
    def assertToken(self, token, expected_type, expected_value, expected_line):
        self.assertEqual(token.type, expected_type)
        self.assertEqual(token.value, expected_value)
        self.assertEqual(token.line, expected_line)

    def test_empty_input(self):
        lexer = Lexer("")
        token = lexer.get_next_token()
        self.assertToken(token, EOF, None, 1)

    def test_whitespace(self):
        lexer = Lexer("   \n\t  ")
        token = lexer.get_next_token()
        self.assertToken(token, EOF, None, 2)

    def test_single_line_comment(self):
        lexer = Lexer("// This is a comment\n42")
        token = lexer.get_next_token()
        self.assertToken(token, INTEGER, 42, 2)

    def test_multi_line_comment(self):
        lexer = Lexer("/* Comment\nacross lines */ 3.14")
        token = lexer.get_next_token()
        self.assertToken(token, FLOAT, 3.14, 2)

    def test_unterminated_block_comment(self):
        lexer = Lexer("/* Unterminated comment")
        with self.assertRaises(LexerError) as cm:
            lexer.get_next_token()
        self.assertIn("Unterminated block comment", str(cm.exception))

    def test_string(self):
        lexer = Lexer('"Hello, world!"')
        token = lexer.get_next_token()
        self.assertToken(token, STRING, "Hello, world!", 1)
        token = lexer.get_next_token()
        self.assertToken(token, EOF, None, 1)

    def test_unterminated_string(self):
        lexer = Lexer('"Unterminated')
        with self.assertRaises(LexerError) as cm:
            lexer.get_next_token()
        self.assertIn("Unterminated string", str(cm.exception))

    def test_numbers(self):
        lexer = Lexer("123 45.67")
        token = lexer.get_next_token()
        self.assertToken(token, INTEGER, 123, 1)
        token = lexer.get_next_token()
        self.assertToken(token, FLOAT, 45.67, 1)

    def test_identifier_and_keywords(self):
        lexer = Lexer("let x if True False")
        token = lexer.get_next_token()
        self.assertToken(token, LET, "let", 1)
        token = lexer.get_next_token()
        self.assertToken(token, IDENTIFIER, "x", 1)
        token = lexer.get_next_token()
        self.assertToken(token, IF, "if", 1)
        token = lexer.get_next_token()
        self.assertToken(token, TRUE, True, 1)
        token = lexer.get_next_token()
        self.assertToken(token, FALSE, False, 1)

    def test_operators(self):
        lexer = Lexer("+ - * / ** % < > <= >= == != and or not =")
        operators = [
            (PLUS, '+'), (MINUS, '-'), (MULTIPLY, '*'), (DIVIDE, '/'),
            (EXPONENT, '**'), (REM, '%'), (LT, '<'),
            (GT, '>'), (LTE, '<='), (GTE, '>='), (EQEQ, '=='),
            (NOTEQ, '!='), (AND, 'and'), (OR, 'or'), (NOT, 'not'),
            (EQUALS, '=')
        ]
        for expected_type, expected_value in operators:
            token = lexer.get_next_token()
            self.assertToken(token, expected_type, expected_value, 1)

    def test_punctuation(self):
        lexer = Lexer("() {} [] , : ? ->")
        punctuation = [
            (LPAREN, '('), (RPAREN, ')'), (LBRACE, '{'), (RBRACE, '}'),
            (LBRACKET, '['), (RBRACKET, ']'), (COMMA, ','), (COLON, ':'),
            (QUESTION_MARK, '?'), (ARROW, '->')
        ]
        for expected_type, expected_value in punctuation:
            token = lexer.get_next_token()
            self.assertToken(token, expected_type, expected_value, 1)

    def test_invalid_not_equals(self):
        lexer = Lexer("!")
        with self.assertRaises(LexerError) as cm:
            lexer.get_next_token()
        self.assertIn("Unexpected '!' without '='", str(cm.exception))

    def test_complex_input(self):
        lexer = Lexer('let x = 42\nif (x > 0) {\n  print "positive"\n}')
        tokens = [
            (LET, "let", 1), (IDENTIFIER, "x", 1), (EQUALS, '=', 1), (INTEGER, 42, 1),
            (IF, "if", 2), (LPAREN, '(', 2), (IDENTIFIER, "x", 2), (GT, '>', 2),
            (INTEGER, 0, 2), (RPAREN, ')', 2), (LBRACE, '{', 2),
            (PRINT, "print", 3), (STRING, "positive", 3), (RBRACE, '}', 4),
            (EOF, None, 4)
        ]
        for expected_type, expected_value, expected_line in tokens:
            token = lexer.get_next_token()
            self.assertToken(token, expected_type, expected_value, expected_line)

    def test_peek(self):
        lexer = Lexer("12 34")
        self.assertEqual(lexer.peek(), '2')
        token = lexer.get_next_token()
        self.assertToken(token, INTEGER, 12, 1)
        self.assertEqual(lexer.peek(), '3')

    def test_step_keyword(self):
        lexer = Lexer("step")
        token = lexer.get_next_token()
        self.assertToken(token, STEP, "step", 1)

    def test_arrow_operator(self):
        lexer = Lexer("->")
        token = lexer.get_next_token()
        self.assertToken(token, ARROW, "->", 1)

if __name__ == "__main__":
    unittest.main()