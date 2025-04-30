import unittest
from src.lexer.lexer import Lexer, Token, LexerError, INTEGER, FLOAT, STRING, TRUE, FALSE, PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, LT, GT, LTE, GTE, EQEQ, NOTEQ, AND, OR, NOT, EQUALS, LET, ASSIGN, IDENTIFIER, IF, ELSE, WHILE, FOR, TO, STEP, BREAK, CONTINUE, FUNC, RETURN, PRINT, LPAREN, RPAREN, LBRACE, RBRACE, LBRACKET, RBRACKET, COMMA, COLON, EOF

class TestLexer(unittest.TestCase):
    def test_numbers(self):
        lexer = Lexer('42 -42 3.14 -3.14')
        tokens = []
        while True:
            token = lexer.get_next_token()
            tokens.append(token)
            if token.type == EOF:
                break
        expected = [
            Token(INTEGER, 42, 1),
            Token(INTEGER, -42, 1),
            Token(FLOAT, 3.14, 1),
            Token(FLOAT, -3.14, 1),
            Token(EOF, None, 1)
        ]
        self.assertEqual(tokens, expected)

    def test_strings(self):
        lexer = Lexer('"hello" "hello\\nworld"')
        tokens = []
        while True:
            token = lexer.get_next_token()
            tokens.append(token)
            if token.type == EOF:
                break
        expected = [
            Token(STRING, "hello", 1),
            Token(STRING, "hello\nworld", 1),
            Token(EOF, None, 1)
        ]
        self.assertEqual(tokens, expected)

    def test_booleans(self):
        lexer = Lexer('True False')
        tokens = []
        while True:
            token = lexer.get_next_token()
            tokens.append(token)
            if token.type == EOF:
                break
        expected = [
            Token(TRUE, True, 1),
            Token(FALSE, False, 1),
            Token(EOF, None, 1)
        ]
        self.assertEqual(tokens, expected)

    def test_operators(self):
        lexer = Lexer('+ - * / ** % < > <= >= == != and or not')
        tokens = []
        while True:
            token = lexer.get_next_token()
            tokens.append(token)
            if token.type == EOF:
                break
        expected = [
            Token(PLUS, '+', 1),
            Token(MINUS, '-', 1),
            Token(MULTIPLY, '*', 1),
            Token(DIVIDE, '/', 1),
            Token(EXPONENT, '**', 1),
            Token(REM, '%', 1),
            Token(LT, '<', 1),
            Token(GT, '>', 1),
            Token(LTE, '<=', 1),
            Token(GTE, '>=', 1),
            Token(EQEQ, '==', 1),
            Token(NOTEQ, '!=', 1),
            Token(AND, 'and', 1),
            Token(OR, 'or', 1),
            Token(NOT, 'not', 1),
            Token(EOF, None, 1)
        ]
        self.assertEqual(tokens, expected)

    def test_keywords(self):
        lexer = Lexer('let assign if else while for to step break continue func return print')
        tokens = []
        while True:
            token = lexer.get_next_token()
            tokens.append(token)
            if token.type == EOF:
                break
        expected = [
            Token(LET, 'let', 1),
            Token(ASSIGN, 'assign', 1),
            Token(IF, 'if', 1),
            Token(ELSE, 'else', 1),
            Token(WHILE, 'while', 1),
            Token(FOR, 'for', 1),
            Token(TO, 'to', 1),
            Token(STEP, 'step', 1),
            Token(BREAK, 'break', 1),
            Token(CONTINUE, 'continue', 1),
            Token(FUNC, 'func', 1),
            Token(RETURN, 'return', 1),
            Token(PRINT, 'print', 1),
            Token(EOF, None, 1)
        ]
        self.assertEqual(tokens, expected)

    def test_identifiers(self):
        lexer = Lexer('x y_1 add')
        tokens = []
        while True:
            token = lexer.get_next_token()
            tokens.append(token)
            if token.type == EOF:
                break
        expected = [
            Token(IDENTIFIER, 'x', 1),
            Token(IDENTIFIER, 'y_1', 1),
            Token(IDENTIFIER, 'add', 1),
            Token(EOF, None, 1)
        ]
        self.assertEqual(tokens, expected)

    def test_punctuation(self):
        lexer = Lexer('= ( ) { } [ ] , :')
        tokens = []
        while True:
            token = lexer.get_next_token()
            tokens.append(token)
            if token.type == EOF:
                break
        expected = [
            Token(EQUALS, '=', 1),
            Token(LPAREN, '(', 1),
            Token(RPAREN, ')', 1),
            Token(LBRACE, '{', 1),
            Token(RBRACE, '}', 1),
            Token(LBRACKET, '[', 1),
            Token(RBRACKET, ']', 1),
            Token(COMMA, ',', 1),
            Token(COLON, ':', 1),
            Token(EOF, None, 1)
        ]
        self.assertEqual(tokens, expected)

    def test_comments(self):
        lexer = Lexer('// Single line\n/* Multi\nline */')
        tokens = []
        while True:
            token = lexer.get_next_token()
            tokens.append(token)
            if token.type == EOF:
                break
        expected = [Token(EOF, None, 3)]
        self.assertEqual(tokens, expected)

    def test_line_numbers(self):
        lexer = Lexer('let x = 5\ny = 10\n// Comment\nz = 3.14')
        tokens = []
        while True:
            token = lexer.get_next_token()
            tokens.append(token)
            if token.type == EOF:
                break
        expected = [
            Token(LET, 'let', 1),
            Token(IDENTIFIER, 'x', 1),
            Token(EQUALS, '=', 1),
            Token(INTEGER, 5, 1),
            Token(IDENTIFIER, 'y', 2),
            Token(EQUALS, '=', 2),
            Token(INTEGER, 10, 2),
            Token(IDENTIFIER, 'z', 4),
            Token(EQUALS, '=', 4),
            Token(FLOAT, 3.14, 4),
            Token(EOF, None, 4)
        ]
        self.assertEqual(tokens, expected)

    def test_error_unterminated_string(self):
        lexer = Lexer('"hello')
        with self.assertRaises(LexerError) as cm:
            lexer.get_next_token()
        self.assertEqual(str(cm.exception), "[line 1] Lexer Error: Unterminated string")

    def test_error_unterminated_comment(self):
        lexer = Lexer('/* comment')
        with self.assertRaises(LexerError) as cm:
            while lexer.get_next_token().type != EOF:
                pass
        self.assertEqual(str(cm.exception), "[line 1] Lexer Error: Unterminated block comment")

    def test_error_invalid_char(self):
        lexer = Lexer('@')
        with self.assertRaises(LexerError) as cm:
            lexer.get_next_token()
        self.assertEqual(str(cm.exception), "[line 1] Lexer Error: Unexpected character: '@'")

    def test_error_invalid_number(self):
        lexer = Lexer('-')
        with self.assertRaises(LexerError) as cm:
            lexer.get_next_token()
        self.assertEqual(str(cm.exception), "[line 1] Lexer Error: Invalid number")

if __name__ == "__main__":
    unittest.main()