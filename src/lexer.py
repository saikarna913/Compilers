import sys

class TokenType:
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    ARRAY = "ARRAY"
    LET = "LET"
    ASSIGN = "ASSIGN"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    REPEAT = "REPEAT"
    UNTIL = "UNTIL"
    PRINT = "PRINT"
    FUNC = "FUNC"
    RETURN = "RETURN"
    IDENTIFIER = "IDENTIFIER"
    OPERATOR = "OPERATOR"
    COMPARISON = "COMPARISON"
    LOGICAL = "LOGICAL"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    PRODUCT_TYPE = "PRODUCT_TYPE"
    SUM_TYPE = "SUM_TYPE"

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.tokens = []

    def tokenize(self):
        try:
            keywords = {"let": TokenType.LET, "assign": TokenType.ASSIGN, "if": TokenType.IF, "else": TokenType.ELSE,
                        "while": TokenType.WHILE, "for": TokenType.FOR, "repeat": TokenType.REPEAT, "until": TokenType.UNTIL,
                        "print": TokenType.PRINT, "func": TokenType.FUNC, "return": TokenType.RETURN, "True": TokenType.BOOLEAN,
                        "False": TokenType.BOOLEAN, "and": TokenType.LOGICAL, "or": TokenType.LOGICAL, "not": TokenType.LOGICAL,
                        "product": TokenType.PRODUCT_TYPE, "sum": TokenType.SUM_TYPE}
            operators = {"+": TokenType.OPERATOR, "-": TokenType.OPERATOR, "*": TokenType.OPERATOR, "/": TokenType.OPERATOR,
                         "**": TokenType.OPERATOR, "rem": TokenType.OPERATOR, "quot": TokenType.OPERATOR}
            comparisons = {"<": TokenType.COMPARISON, ">": TokenType.COMPARISON, "<=": TokenType.COMPARISON,
                           ">=": TokenType.COMPARISON, "==": TokenType.COMPARISON, "!=": TokenType.COMPARISON}
            symbols = {"(": TokenType.LPAREN, ")": TokenType.RPAREN, "{": TokenType.LBRACE, "}": TokenType.RBRACE, 
                       "[": TokenType.LBRACKET, "]": TokenType.RBRACKET, ",": TokenType.COMMA, ";": TokenType.SEMICOLON}
            
            while self.position < len(self.source_code):
                char = self.source_code[self.position]
                
                if char.isspace():
                    self.position += 1
                    continue
                
                if char.isdigit() or (char == '.' and self.position + 1 < len(self.source_code) and self.source_code[self.position + 1].isdigit()):
                    self.tokens.append(Token(TokenType.NUMBER, self.extract_number()))
                    continue
                
                if char.isalpha() or char == '_':
                    word = self.extract_identifier()
                    self.tokens.append(Token(keywords.get(word, TokenType.IDENTIFIER), word))
                    continue
                
                if char in operators or self.peek_two_chars() in operators:
                    self.tokens.append(Token(TokenType.OPERATOR, self.extract_operator()))
                    continue
                
                if char in comparisons or self.peek_two_chars() in comparisons:
                    self.tokens.append(Token(TokenType.COMPARISON, self.extract_comparison()))
                    continue
                
                if char == '"':
                    self.tokens.append(Token(TokenType.STRING, self.extract_string()))
                    continue
                
                if char == '[':
                    self.tokens.append(Token(TokenType.ARRAY, self.extract_array()))
                    continue
                
                if char in symbols:
                    self.tokens.append(Token(symbols[char], char))
                    self.position += 1
                    continue
                
                raise SyntaxError(f'Unexpected token: {char}')
        
        except Exception as e:
            print(f"Lexer Error: {e}")
            sys.exit(1)
        
        return self.tokens
    
    def peek_two_chars(self):
        return self.source_code[self.position:self.position+2]
    
    def extract_number(self):
        num = ""
        while self.position < len(self.source_code) and (self.source_code[self.position].isdigit() or self.source_code[self.position] == '.'):
            num += self.source_code[self.position]
            self.position += 1
        return num
    
    def extract_identifier(self):
        word = ""
        while self.position < len(self.source_code) and (self.source_code[self.position].isalnum() or self.source_code[self.position] == '_'):
            word += self.source_code[self.position]
            self.position += 1
        return word
    
    def extract_operator(self):
        op = self.peek_two_chars() if self.peek_two_chars() in {"**", "rem", "quot"} else self.source_code[self.position]
        self.position += len(op)
        return op
    
    def extract_comparison(self):
        comp = self.peek_two_chars() if self.peek_two_chars() in {"<=", ">=", "==", "!="} else self.source_code[self.position]
        self.position += len(comp)
        return comp
    
    def extract_string(self):
        start = self.position + 1
        self.position = self.source_code.find('"', start)
        if self.position == -1:
            raise SyntaxError("Unterminated string literal")
        string_value = self.source_code[start:self.position]
        self.position += 1
        return string_value
    
    def extract_array(self):
        start = self.position
        self.position = self.source_code.find(']', start)
        if self.position == -1:
            raise SyntaxError("Unterminated array declaration")
        self.position += 1
        return self.source_code[start:self.position]

#if __name__ == "__main__":
    #if len(sys.argv) < 2:
       # print("Usage: python lexer.py <filename>")
       # sys.exit(1)
    
    #filename = sys.argv[1]
   # try:
        #with open(filename, 'r') as file:
           # source_code = file.read()
        #lexer = Lexer(source_code)
       # tokens = lexer.tokenize()
        #print(tokens)
    #except FileNotFoundError:
     #   print(f"Error: File '{filename}' not found.")
      #  sys.exit(1)
