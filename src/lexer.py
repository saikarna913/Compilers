# lexer.py
from dataclasses import dataclass
from typing import Optional

# Token types
INTEGER    = 'INTEGER'
FLOAT      = 'FLOAT'
PLUS       = 'PLUS'
MINUS      = 'MINUS'
MULTIPLY   = 'MULTIPLY'
DIVIDE     = 'DIVIDE'
EXPONENT   = 'EXPONENT'   # For '**'
REM        = 'REM'        # For remainder operator
QUOT       = 'QUOT'       # For integer division
LPAREN     = 'LPAREN'
RPAREN     = 'RPAREN'
EQUALS     = 'EQUALS'
LET        = 'LET'
IDENTIFIER = 'IDENTIFIER'
TRUE       = 'TRUE'
FALSE      = 'FALSE'
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
        """Return the next character without advancing the position pointer."""
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        """Skip whitespace characters."""
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
        
        if result == 'let':
            return Token(LET, result)
        elif result == 'True':
            return Token(TRUE, True)
        elif result == 'False':
            return Token(FALSE, False)
        elif result == 'rem':
            return Token(REM, result)
        elif result == 'quot':
            return Token(QUOT, result)
        else:
            return Token(IDENTIFIER, result)

    def get_next_token(self):
        """Lexical analyzer (tokenizer)."""
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.number()

            if self.current_char.isalpha():
                return self.identifier()

            if self.current_char == '*':
                self.advance()
                if self.current_char == '*':
                    self.advance()
                    return Token(EXPONENT, '**')
                return Token(MULTIPLY, '*')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '/':
                self.advance()
                return Token(DIVIDE, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if self.current_char == '=':
                self.advance()
                return Token(EQUALS, '=')

            self.error()

        return Token(EOF, None)

if __name__ == '__main__':
    # Example input using the new operators:
    text = "3.14 + 2 * (4 - 1) ** 2 rem 3 quot 2"
    lexer = Lexer(text)
    token = lexer.get_next_token()
    while token.type != EOF:
        print(token)
        token = lexer.get_next_token()
