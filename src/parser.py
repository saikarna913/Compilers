import sys
from lexer import Lexer, TokenType

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def parse(self):
        ast = []
        try:
            while self.position < len(self.tokens):
                ast.append(self.parse_statement())
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            sys.exit(1)
        return ast

    def parse_statement(self):
        try:
            token = self.tokens[self.position]
            if token.type == TokenType.LET:
                return self.parse_assignment()
            elif token.type == TokenType.IF:
                return self.parse_if()
            elif token.type == TokenType.WHILE:
                return self.parse_while()
            elif token.type == TokenType.FOR:
                return self.parse_for()
            elif token.type == TokenType.REPEAT:
                return self.parse_repeat_until()
            elif token.type == TokenType.PRINT:
                return self.parse_print()
            else:
                raise SyntaxError(f'Unexpected statement: {token.value}')
        except IndexError:
            raise SyntaxError("Unexpected end of input")

    def parse_assignment(self):
        try:
            self.position += 1
            var_name = self.tokens[self.position].value
            self.position += 1
            self.position += 1  # Skipping '='
            expr = self.parse_expression()
            return ('assign', var_name, expr)
        except IndexError:
            raise SyntaxError("Invalid assignment statement")

    def parse_if(self):
        try:
            self.position += 1
            condition = self.parse_expression()
            self.position += 1
            body = []
            while self.tokens[self.position].type != TokenType.RBRACE:
                body.append(self.parse_statement())
            self.position += 1
            return ('if', condition, body)
        except IndexError:
            raise SyntaxError("Invalid if statement structure")

    def parse_while(self):
        try:
            self.position += 1
            condition = self.parse_expression()
            self.position += 1
            body = []
            while self.tokens[self.position].type != TokenType.RBRACE:
                body.append(self.parse_statement())
            self.position += 1
            return ('while', condition, body)
        except IndexError:
            raise SyntaxError("Invalid while statement structure")

    def parse_for(self):
        try:
            self.position += 1
            initialization = self.parse_statement()
            condition = self.parse_expression()
            self.position += 1
            increment = self.parse_statement()
            self.position += 1
            body = []
            while self.tokens[self.position].type != TokenType.RBRACE:
                body.append(self.parse_statement())
            self.position += 1
            return ('for', initialization, condition, increment, body)
        except IndexError:
            raise SyntaxError("Invalid for loop structure")

    def parse_repeat_until(self):
        try:
            self.position += 1
            body = []
            while self.tokens[self.position].type != TokenType.UNTIL:
                body.append(self.parse_statement())
            self.position += 1
            condition = self.parse_expression()
            return ('repeat_until', body, condition)
        except IndexError:
            raise SyntaxError("Invalid repeat-until structure")

    def parse_print(self):
        try:
            self.position += 1
            expr = self.parse_expression()
            return ('print', expr)
        except IndexError:
            raise SyntaxError("Invalid print statement")

    def parse_expression(self):
        try:
            token = self.tokens[self.position]
            if token.type == TokenType.STRING:
                self.position += 1
                return ('string', token.value)
            elif token.type == TokenType.ARRAY:
                return self.parse_array()
            elif token.type == TokenType.PRODUCT_TYPE:
                return self.parse_product()
            elif token.type == TokenType.SUM_TYPE:
                return self.parse_sum()
            else:
                self.position += 1
                return token.value
        except IndexError:
            raise SyntaxError("Invalid expression")

    def parse_array(self):
        try:
            self.position += 1
            elements = []
            while self.tokens[self.position].type != TokenType.RBRACKET:
                elements.append(self.parse_expression())
                if self.tokens[self.position].type == TokenType.COMMA:
                    self.position += 1
            self.position += 1
            return ('array', elements)
        except IndexError:
            raise SyntaxError("Invalid array syntax")

    def parse_product(self):
        try:
            self.position += 1
            components = []
            while self.tokens[self.position].type != TokenType.RPAREN:
                components.append(self.parse_expression())
                if self.tokens[self.position].type == TokenType.COMMA:
                    self.position += 1
            self.position += 1
            return ('product', components)
        except IndexError:
            raise SyntaxError("Invalid product syntax")

    def parse_sum(self):
        try:
            self.position += 1
            options = []
            while self.tokens[self.position].type != TokenType.RPAREN:
                options.append(self.parse_expression())
                if self.tokens[self.position].type == TokenType.COMMA:
                    self.position += 1
            self.position += 1
            return ('sum', options)
        except IndexError:
            raise SyntaxError("Invalid sum syntax")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as file:
            source_code = file.read()
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        print(ast)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
