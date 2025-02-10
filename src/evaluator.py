# evaluator.py
from lexer import Lexer
from parser import Parser
from ast_1 import BinOp, Number, UnaryOp, Boolean, Var, VarAssign
import traceback

class Interpreter:
    def __init__(self):
        self.env = {}  # Environment for variable storage

    def visit_BinOp(self, node: BinOp):
        if node.op == '+':
            return self.visit(node.left) + self.visit(node.right)
        elif node.op == '-':
            return self.visit(node.left) - self.visit(node.right)
        elif node.op == '*':
            return self.visit(node.left) * self.visit(node.right)
        elif node.op == '/':
            right = self.visit(node.right)
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return self.visit(node.left) / right

    def visit_Number(self, node: Number):
        return node.value

    def visit_UnaryOp(self, node: UnaryOp):
        if node.op == '+':
            return +self.visit(node.expr)
        elif node.op == '-':
            return -self.visit(node.expr)

    def visit_Boolean(self, node: Boolean):
        return node.value

    def visit_Var(self, node: Var):
        if node.name in self.env:
            return self.env[node.name]
        else:
            raise Exception(f"Undefined variable '{node.name}'")

    def visit_VarAssign(self, node: VarAssign):
        value = self.visit(node.value)
        self.env[node.name] = value
        return value

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, None)
        if visitor is None:
            raise Exception(f'No visitor found for {type(node).__name__}')
        return visitor(node)

    def interpret(self, tree):
        return self.visit(tree)

class Calculator:
    def calculate(self, expression: str):
        try:
            lexer = Lexer(expression)
            parser = Parser(lexer)
            tree = parser.parse()
            interpreter = Interpreter()
            result = interpreter.interpret(tree)
            return result
        except Exception as e:
            # Print the full traceback for debugging purposes
            traceback.print_exc()
            raise

def main():
    calculator = Calculator()
    while True:
        try:
            expression = input('calc> ')
            if expression.lower() in ['exit', 'quit']:
                break
            result = calculator.calculate(expression)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()
