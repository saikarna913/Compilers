from dataclasses import dataclass
from typing import Optional, Any

# Token types (removed QUOT)
INTEGER = 'INTEGER'
FLOAT = 'FLOAT'
STRING = 'STRING'
TRUE = 'TRUE'
FALSE = 'FALSE'
PLUS = 'PLUS'
MINUS = 'MINUS'
MULTIPLY = 'MULTIPLY'
DIVIDE = 'DIVIDE'
EXPONENT = 'EXPONENT'
REM = 'REM'
LT = 'LT'
GT = 'GT'
LTE = 'LTE'
GTE = 'GTE'
EQEQ = 'EQEQ'
NOTEQ = 'NOTEQ'
AND = 'AND'
OR = 'OR'
NOT = 'NOT'
EQUALS = 'EQUALS'
LET = 'LET'
ASSIGN = 'ASSIGN'
IDENTIFIER = 'IDENTIFIER'
IF = 'IF'
ELSE  = 'ELSE'
WHILE = 'WHILE'
FOR = 'FOR'
IN = 'IN'
TO         = 'TO'
REPEAT     = 'REPEAT'
UNTIL      = 'UNTIL'
MATCH      = 'MATCH'
ARROW      = 'ARROW'
FUNC       = 'FUNC'
RETURN     = 'RETURN'
PRINT      = 'PRINT'
LPAREN     = 'LPAREN'
RPAREN     = 'RPAREN'
LBRACE     = 'LBRACE'
RBRACE     = 'RBRACE'
LBRACKET   = 'LBRACKET'
RBRACKET   = 'RBRACKET'
COMMA      = 'COMMA'
COLON      = 'COLON'
QUESTION_MARK = 'QUESTION_MARK'  
EOF = 'EOF'
STEP = 'STEP'

@dataclass
class Token:
    type: str
    value: Optional[Any]
    line: int

class LexerError(Exception):
    def __init__(self, line: int, message: str):
        self.line = line
        self.message = message
        super().__init__(f"[line {line}] Lexer Error: {message}")

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.current_char = self.text[0] if text else None

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char and self.current_char != '\n':
                self.advance()
            if self.current_char == '\n':
                self.advance()
        elif self.current_char == '/' and self.peek() == '*':
            start_line = self.line
            self.advance()  # Skip '/'
            self.advance()  # Skip '*'
            while self.current_char and not (self.current_char == '*' and self.peek() == '/'):
                self.advance()
            if not self.current_char:
                raise LexerError(start_line, "Unterminated block comment")
            self.advance()  # Skip '*'
            self.advance()  # Skip '/'
            # If a newline immediately follows a block comment, skip it to match expected line numbering.
            if self.current_char == '\n':
                self.advance()

    def string(self):
        result = ''
        start_line = self.line
        self.advance()  # Skip opening quote
        while self.current_char and self.current_char != '"':
            result += self.current_char
            self.advance()
        if not self.current_char:
            raise LexerError(start_line, "Unterminated string")
        self.advance()  # Skip closing quote
        return Token(STRING, result, start_line)

    def number(self):
        result = ''
        start_line = self.line
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if self.current_char == '.' and self.peek() and self.peek().isdigit():
            result += '.'
            self.advance()
            while self.current_char and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return Token(FLOAT, float(result), start_line)
        return Token(INTEGER, int(result), start_line)

    def identifier(self):
        result = ''
        start_line = self.line
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        keywords = {
            "let": LET, "assign": ASSIGN, "True": TRUE, "False": FALSE, "rem": REM,
            "and": AND, "or": OR, "not": NOT, "if": IF, "else": ELSE, "while": WHILE, "for": FOR,
            "in": IN, "to": TO, "repeat": REPEAT, "until": UNTIL, "match": MATCH, "func": FUNC,
            "return": RETURN, "print": PRINT, "step": STEP
        }
        token_type = keywords.get(result, IDENTIFIER)
        if token_type == TRUE:
            return Token(TRUE, True, start_line)
        elif token_type == FALSE:
            return Token(FALSE, False, start_line)
        return Token(token_type, result, start_line)

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char == '/' and self.peek() in ['/', '*']:
                self.skip_comment()
                continue
            if self.current_char == '"':
                return self.string()
            if self.current_char.isdigit():
                return self.number()
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            start_line = self.line
            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+', start_line)
            if self.current_char == '-':
                self.advance()
                if self.current_char == '>':
                    self.advance()
                    return Token(ARROW, '->', start_line)
                return Token(MINUS, '-', start_line)
            if self.current_char == '*':
                self.advance()
                if self.current_char == '*':
                    self.advance()
                    return Token(EXPONENT, '**', start_line)
                return Token(MULTIPLY, '*', start_line)
            if self.current_char == '/':
                self.advance()
                return Token(DIVIDE, '/', start_line)
            if self.current_char == '%':     
                self.advance()
                return Token(REM, '%', start_line)
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LTE, '<=', start_line)
                return Token(LT, '<', start_line)
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(GTE, '>=', start_line)
                return Token(GT, '>', start_line)
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(EQEQ, '==', start_line)
                return Token(EQUALS, '=', start_line)
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(NOTEQ, '!=', start_line)
                raise LexerError(start_line, "Unexpected '!' without '='")
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(', start_line)
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')', start_line)
            if self.current_char == '{':
                self.advance()
                return Token(LBRACE, '{', start_line)
            if self.current_char == '}':
                self.advance()
                return Token(RBRACE, '}', start_line)
            if self.current_char == '[':
                self.advance()
                return Token(LBRACKET, '[', start_line)
            if self.current_char == ']':
                self.advance()
                return Token(RBRACKET, ']', start_line)
            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',', start_line)
            if self.current_char == ':':
                self.advance()
                return Token(COLON, ':', start_line)
            if self.current_char == '?':  
                self.advance()
                return Token(QUESTION_MARK, '?', start_line)
            print(f"[line {start_line}] Lexer Warning: Skipping unexpected character: '{self.current_char}'")
            self.advance()
            continue
        return Token(EOF, None, self.line)

if __name__ == "__main__":
    lexer = Lexer('let x = 1 // Comment\n/* Multi\nline */ 2.5 ? 3 : 4')
    token = lexer.get_next_token()
    while token.type != EOF:
        print(f"{token.type}: {token.value} (line {token.line})")
        token = lexer.get_next_token()
    print(f"{token.type}: {token.value} (line {token.line})")