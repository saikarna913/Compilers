# parser.py
from lexer import (Lexer, Token, LET, ASSIGN, IDENTIFIER, EQUALS, TRUE, FALSE,
                   PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, QUOT, LPAREN, RPAREN,
                   LT, LTE, GT, GTE, EQEQ, NOTEQ, AND, OR, NOT, EOF, INTEGER, FLOAT)
from ast_1 import (AST, BinOp, Number, UnaryOp, Boolean, Var, VarAssign, VarReassign,
                   print_ast)

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
        """let_statement : LET IDENTIFIER EQUALS assignment"""
        self.eat(LET)
        if self.current_token.type != IDENTIFIER:
            self.error()
        var_name = self.current_token.value
        self.eat(IDENTIFIER)
        self.eat(EQUALS)
        expr_node = self.assignment()
        return VarAssign(var_name, expr_node)

    def assignment(self) -> AST:
        """
        assignment : logical_or ( ASSIGN assignment )?
        (Reassignment is right‑associative; only allowed if the left is a variable.)
        """
        node = self.logical_or()
        if self.current_token.type == ASSIGN:
            if not isinstance(node, Var):
                self.error()
            self.eat(ASSIGN)
            node = VarReassign(name=node.name, value=self.assignment())
        return node

    def logical_or(self) -> AST:
        node = self.logical_and()
        while self.current_token.type == OR:
            token = self.current_token
            self.eat(OR)
            node = BinOp(left=node, op=token.value, right=self.logical_and())
        return node

    def logical_and(self) -> AST:
        node = self.logical_not()
        while self.current_token.type == AND:
            token = self.current_token
            self.eat(AND)
            node = BinOp(left=node, op=token.value, right=self.logical_not())
        return node

    def logical_not(self) -> AST:
        if self.current_token.type == NOT:
            token = self.current_token
            self.eat(NOT)
            return UnaryOp(token.value, self.logical_not())
        else:
            return self.comparison()

    def comparison(self) -> AST:
        node = self.arithmetic()
        if self.current_token.type in (EQEQ, NOTEQ, LT, LTE, GT, GTE):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token.value, right=self.arithmetic())
        return node

    def arithmetic(self) -> AST:
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token.value, right=self.term())
        return node

    def term(self) -> AST:
        node = self.power()
        while self.current_token.type in (MULTIPLY, DIVIDE, REM, QUOT):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token.value, right=self.power())
        return node

    def power(self) -> AST:
        node = self.factor()
        if self.current_token.type == EXPONENT:
            token = self.current_token
            self.eat(EXPONENT)
            node = BinOp(left=node, op=token.value, right=self.power())
        return node

    def factor(self) -> AST:
        token = self.current_token
        if token.type in (PLUS, MINUS):
            self.eat(token.type)
            return UnaryOp(token.value, self.factor())
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Number(token.value)
        elif token.type == FLOAT:
            self.eat(FLOAT)
            return Number(token.value)
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
            node = self.assignment()  # allow assignment inside parentheses
            self.eat(RPAREN)
            return node
        else:
            self.error()

    def parse(self) -> AST:
        if self.current_token.type == LET:
            return self.let_statement()
        else:
            return self.assignment()

if __name__ == '__main__':
    text = "let x = 10\nx assign 20\n10 < 20 and not False"
    lexer = Lexer(text)
    parser = Parser(lexer)
    ast = parser.parse()
    print_ast(ast)
