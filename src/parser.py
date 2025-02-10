# parser.py
from lexer import Lexer, Token, LET, IDENTIFIER, EQUALS, TRUE, FALSE, PLUS, MINUS, MULTIPLY, DIVIDE, LPAREN, RPAREN, INTEGER, FLOAT, EOF
from ast_1 import AST, BinOp, Number, UnaryOp, Boolean, Var, VarAssign, print_ast

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type: str):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def let_statement(self) -> AST:
        """let_statement : LET IDENTIFIER EQUALS expr"""
        self.eat(LET)
        token = self.current_token
        if token.type != IDENTIFIER:
            self.error()
        var_name = token.value
        self.eat(IDENTIFIER)
        self.eat(EQUALS)
        expr_node = self.expr()
        return VarAssign(var_name, expr_node)

    def factor(self) -> AST:
        """
        factor : NUMBER
               | BOOLEAN
               | IDENTIFIER
               | LPAREN expr RPAREN
               | (PLUS | MINUS) factor
        """
        token = self.current_token

        if token.type == INTEGER:
            self.eat(INTEGER)
            return Number(int(token.value))
        elif token.type == FLOAT:
            self.eat(FLOAT)
            return Number(float(token.value))
        elif token.type == TRUE:
            self.eat(TRUE)
            return Boolean(True)
        elif token.type == FALSE:
            self.eat(FALSE)
            return Boolean(False)
        elif token.type == IDENTIFIER:
            self.eat(IDENTIFIER)
            return Var(token.value)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        elif token.type in (PLUS, MINUS):
            self.eat(token.type)
            return UnaryOp(token.value, self.factor())
        else:
            self.error()

    def term(self) -> AST:
        """term : factor ((MULTIPLY | DIVIDE) factor)*"""
        node = self.factor()

        while self.current_token.type in (MULTIPLY, DIVIDE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token.value, right=self.factor())

        return node

    def expr(self) -> AST:
        """expr : term ((PLUS | MINUS) term)*"""
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token.value, right=self.term())

        return node

    def parse(self) -> AST:
        """Main entry point for parsing."""
        if self.current_token.type == LET:
            return self.let_statement()
        else:
            return self.expr()

if __name__ == '__main__':
    # Example: parse a let statement
    text = "let x = 10 + 20"
    lexer = Lexer(text)
    parser = Parser(lexer)
    ast = parser.parse()
    print_ast(ast)
