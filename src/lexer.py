# lexer.py
from dataclasses import dataclass
from typing import Optional

# Token types for numbers and arithmetic operators
INTEGER    = 'INTEGER'
FLOAT      = 'FLOAT'
PLUS       = 'PLUS'
MINUS      = 'MINUS'
MULTIPLY   = 'MULTIPLY'
DIVIDE     = 'DIVIDE'
EXPONENT   = 'EXPONENT'
REM        = 'REM'
QUOT       = 'QUOT'
LPAREN     = 'LPAREN'
RPAREN     = 'RPAREN'
EQUALS     = 'EQUALS'   # Used only in 'let' declarations

# Assignment keywords
LET        = 'LET'
ASSIGN     = 'ASSIGN'   # For reassigning an existing variable

# Identifier and booleans
IDENTIFIER = 'IDENTIFIER'
TRUE       = 'TRUE'
FALSE      = 'FALSE'

# Comparison operators
LT         = 'LT'
GT         = 'GT'
LTE        = 'LTE'
GTE        = 'GTE'
EQEQ       = 'EQEQ'
NOTEQ      = 'NOTEQ'

# Logical operators
AND        = 'AND'
OR         = 'OR'
NOT        = 'NOT'

EOF        = 'EOF'

@dataclass
class Token:
    type: str
    value: Optional[any]

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the position pointer and set the current_char."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        """Peek at the next character without advancing."""
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def number(self):
        """Return a number token (integer or float)."""
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return Token(FLOAT, float(result))
        return Token(INTEGER, int(result))

    def identifier(self):
        """Handle identifiers and reserved keywords."""
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        # Reserved keywords:
        if result == 'let':
            return Token(LET, result)
        elif result == 'assign':
            return Token(ASSIGN, result)
        elif result == 'True':
            return Token(TRUE, True)
        elif result == 'False':
            return Token(FALSE, False)
        elif result == 'rem':
            return Token(REM, result)
        elif result == 'quot':
            return Token(QUOT, result)
        elif result == 'and':
            return Token(AND, result)
        elif result == 'or':
            return Token(OR, result)
        elif result == 'not':
            return Token(NOT, result)
        else:
            return Token(IDENTIFIER, result)

    def get_next_token(self):
        """Lexical analyzer (tokenizer) for the language."""
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.number()

            if self.current_char.isalpha():
                return self.identifier()

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')
            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')
            if self.current_char == '*':
                self.advance()
                if self.current_char == '*':
                    self.advance()
                    return Token(EXPONENT, '**')
                return Token(MULTIPLY, '*')
            if self.current_char == '/':
                self.advance()
                return Token(DIVIDE, '/')
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LTE, '<=')
                return Token(LT, '<')
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(GTE, '>=')
                return Token(GT, '>')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(EQEQ, '==')
                return Token(EQUALS, '=')
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(NOTEQ, '!=')
                self.error()

            self.error()
        return Token(EOF, None)

if __name__ == '__main__':
    # Example: Print tokens for a sample input
    text = "let x = 10\nx assign 20\n10 < 20 and not False"
    lexer = Lexer(text)
    token = lexer.get_next_token()
    while token.type != EOF:
        print(token)
        token = lexer.get_next_token()
