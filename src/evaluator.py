from lexer import Token, TokenType, Lexer
from parser import Parser
class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}
    
    def execute(self):
        for statement in self.ast:
            self.execute_statement(statement)
    
    def execute_statement(self, statement):
        if statement[0] == 'assign':
            _, var_name, expr = statement
            self.variables[var_name] = self.evaluate_expression(expr)
        elif statement[0] == 'if':
            _, condition, body = statement
            if self.evaluate_expression(condition):
                for stmt in body:
                    self.execute_statement(stmt)
        elif statement[0] == 'while':
            _, condition, body = statement
            while self.evaluate_expression(condition):
                for stmt in body:
                    self.execute_statement(stmt)
        elif statement[0] == 'for':
            _, initialization, condition, increment, body = statement
            self.execute_statement(initialization)
            while self.evaluate_expression(condition):
                for stmt in body:
                    self.execute_statement(stmt)
                self.execute_statement(increment)
        elif statement[0] == 'repeat_until':
            _, body, condition = statement
            while True:
                for stmt in body:
                    self.execute_statement(stmt)
                if self.evaluate_expression(condition):
                    break
        elif statement[0] == 'print':
            _, expr = statement
            print(self.evaluate_expression(expr))
    
    def evaluate_expression(self, expr):
        if expr[0] == 'string':
            return expr[1]
        elif expr[0] == 'array':
            return [self.evaluate_expression(e) for e in expr[1]]
        elif expr[0] == 'product':
            return tuple(self.evaluate_expression(e) for e in expr[1])
        elif expr[0] == 'sum':
            return [self.evaluate_expression(e) for e in expr[1]]
        else:
            return eval(expr, {}, self.variables)

if __name__ == "__main__":
    code = "let x = 10 + 5 * 2; if (x > 10) { print(x); }"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter(ast)
    interpreter.execute()
