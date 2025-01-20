from lexer import Lexer
from parser import Parser
from ast_1 import BinOp, Number, UnaryOp

class Interpreter:
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
            return self.visit(node.left) / self.visit(node.right)

    def visit_Number(self, node: Number):
        return node.value

    def visit_UnaryOp(self, node: UnaryOp):
        if node.op == '+':
            return +self.visit(node.expr)
        elif node.op == '-':
            return -self.visit(node.expr)

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, None)
        if visitor is None:
            raise Exception(f'No visitor found for {type(node).__name__}')
        return visitor(node)

    def interpret(self, tree):
        return self.visit(tree)

class Calculator:
    def calculate(self, expression: str) -> float:
        try:
            lexer = Lexer(expression)
            parser = Parser(lexer)
            tree = parser.parse()
            interpreter = Interpreter()
            result = interpreter.interpret(tree)
            return result
        except Exception as e:
            raise Exception(f"Error calculating expression: {str(e)}")

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