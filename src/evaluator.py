from lexer import Lexer, Token, PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, QUOT, LT, GT, LTE, GTE, EQEQ, NOTEQ, AND, OR, NOT
from parser import Parser
from ast_1 import (
    AST, BinOp, UnaryOp, Integer, Float, String, Boolean, Var, VarAssign, VarReassign, Block,
    If, While, For, RepeatUntil, Match, MatchCase, FuncDef, FuncCall, Return, Lambda,
    Array, Dict, ConditionalExpr, Print
)
import sys
import traceback
from typing import Any, Dict, List, Optional

class FluxRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = f"[line {token.line}] Error at '{token.value}': {message}"
        super().__init__(self.message)

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}

    def define(self, name: str, value: Any):
        self.variables[name] = value

    def get(self, name: str, token: Token) -> Any:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name, token)
        raise FluxRuntimeError(token, f"Undefined variable '{name}'")

    def assign(self, name: str, value: Any, token: Token):
        if name in self.variables:
            self.variables[name] = value
            return value
        if self.parent:
            return self.parent.assign(name, value, token)
        raise FluxRuntimeError(token, f"Cannot reassign undefined variable '{name}'")

class TailCall(Exception):
    """Exception used for tail call optimization"""
    pass

class Return(Exception):
    def __init__(self, value: Any):
        self.value = value
        super().__init__()

class Function:
    def __init__(self, declaration, closure: 'Environment', is_anonymous: bool = False):
        self.declaration = declaration
        self.closure = closure
        self.is_anonymous = is_anonymous
        self.name = '<anonymous>' if is_anonymous else declaration.name
        self.params = declaration.params

    def __str__(self):
        params_str = ", ".join(self.params)
        if self.is_anonymous:
            return f"<anonymous function({params_str})>"
        return f"<function {self.name}({params_str})>"

    def call(self, evaluator: 'Evaluator', arguments: List[Any], token: Token) -> Any:
        # Ensure we have the right number of arguments
        if len(arguments) != len(self.params):
            raise FluxRuntimeError(token, 
                f"Expected {len(self.params)} arguments, got {len(arguments)}")
        
        # Create a new environment within the function's closure
        env = Environment(self.closure)
        
        # Bind parameters to arguments
        for param, arg in zip(self.params, arguments):
            env.define(param, arg)
        
        try:
            # Execute the function body in the new environment
            result = evaluator.execute_block(self.declaration.body, env)
            return result
        except Return as r:
            # Handle return statements
            return r.value

class Evaluator:
    def __init__(self):
        self.global_env = Environment()
        self.env = self.global_env
        self.current_function = None
        self.in_tail_position = False
        self.tail_call_args = None

    def interpret(self, tree: Block) -> Any:
        try:
            return self.execute_block(tree, self.global_env)
        except FluxRuntimeError as e:
            print(e.message)
            return None
        except Exception as e:
            print(f"Internal error: {e}")
            traceback.print_exc()
            return None

    def evaluate(self, node: AST) -> Any:
        if node is None:
            return None
        return node.accept(self)

    def execute_block(self, block: Block, env: Environment) -> Any:
        previous_env = self.env
        self.env = env
        try:
            result = None
            for stmt in block.statements:
                if isinstance(stmt, Return):
                    raise Return(self.evaluate(stmt.value))
                result = self.evaluate(stmt)
            return result
        finally:
            self.env = previous_env

    # Special method for handling tail-recursive calls
    def evaluate_tail_recursive(self, node: FuncCall) -> Any:
        """Special evaluation method for potentially tail-recursive functions"""
        # Evaluate the callee and arguments
        callee = self.evaluate(node.callee)
        
        if not isinstance(callee, Function):
            raise FluxRuntimeError(
                node.token or Token("IDENTIFIER", str(node.callee), 0), 
                f"'{node.callee}' is not a function"
            )
            
        # Mark that we're in a tail position
        self.in_tail_position = True
        self.current_function = callee
        
        # Initial set of arguments
        arguments = [self.evaluate(arg) for arg in node.args]
        
        # Loop instead of recursing
        while True:
            try:
                # Call the function with current arguments
                result = callee.call(self, arguments, node.token or Token("IDENTIFIER", str(node.callee), 0))
                return result
            except TailCall:
                # Update arguments for the next iteration
                arguments = self.tail_call_args
                self.tail_call_args = None
                # Continue looping (which reuses the stack frame)

    def visit_integer(self, node: Integer) -> Any:
        return node.value

    def visit_float(self, node: Float) -> Any:
        return node.value

    def visit_string(self, node: String) -> str:
        return node.value

    def visit_boolean(self, node: Boolean) -> bool:
        return node.value

    def visit_var(self, node: Var) -> Any:
        return self.env.get(node.name, node.token)

    def visit_var_assign(self, node: VarAssign) -> Any:
        value = self.evaluate(node.value)
        self.env.define(node.name, value)
        return value

    def visit_var_reassign(self, node: VarReassign) -> Any:
        value = self.evaluate(node.value)
        return self.env.assign(node.name, value, node.token)

    def visit_bin_op(self, node: BinOp) -> Any:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op_type = node.operator.type

        if op_type == PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, str) and isinstance(right, (int, float, bool, Function)):
                return left + self.stringify(right)
            if isinstance(left, (int, float, bool, Function)) and isinstance(right, str):
                return self.stringify(left) + right
            raise FluxRuntimeError(node.operator, "Operands must be two numbers, two strings, or a string and another type for '+'")
        
        if op_type == MINUS:
            self.check_number_operands(node.operator, left, right)
            return left - right
        
        if op_type == MULTIPLY:
            self.check_number_operands(node.operator, left, right)
            return left * right
        
        if op_type == DIVIDE:
            self.check_number_operands(node.operator, left, right)
            if right == 0:
                raise FluxRuntimeError(node.operator, "Division by zero")
            return left / right
        
        if op_type == EXPONENT:
            self.check_number_operands(node.operator, left, right)
            return left ** right
        
        if op_type == REM:
            self.check_number_operands(node.operator, left, right)
            if right == 0:
                raise FluxRuntimeError(node.operator, "Remainder by zero")
            return left % right
        
        if op_type == QUOT:
            self.check_number_operands(node.operator, left, right)
            if right == 0:
                raise FluxRuntimeError(node.operator, "Integer division by zero")
            return left // right
        
        if op_type in (LT, GT, LTE, GTE):
            self.check_number_operands(node.operator, left, right)
            if op_type == LT: return left < right
            if op_type == GT: return left > right
            if op_type == LTE: return left <= right
            if op_type == GTE: return left >= right
        
        if op_type == EQEQ:
            return left == right
        if op_type == NOTEQ:
            return left != right
        
        if op_type == AND:
            return self.is_truthy(left) and self.is_truthy(right)
        if op_type == OR:
            return self.is_truthy(left) or self.is_truthy(right)
        
        raise FluxRuntimeError(node.operator, f"Unknown binary operator '{node.operator.value}'")

    def visit_unary_op(self, node: UnaryOp) -> Any:
        value = self.evaluate(node.right)
        if node.operator.type == MINUS:
            self.check_number_operand(node.operator, value)
            return -value
        if node.operator.type == NOT:
            return not self.is_truthy(value)
        raise FluxRuntimeError(node.operator, f"Unknown unary operator '{node.operator.type}'")

    def visit_block(self, node: Block) -> Any:
        return self.execute_block(node, Environment(self.env))

    def visit_if(self, node: If) -> Any:
        condition = self.evaluate(node.condition)
        if self.is_truthy(condition):
            return self.evaluate(node.then_branch)
        elif node.else_branch:
            return self.evaluate(node.else_branch)
        return None

    def visit_while(self, node: While) -> Any:
        result = None
        while self.is_truthy(self.evaluate(node.condition)):
            result = self.evaluate(node.body)
        return result

    def visit_for(self, node: For) -> Any:
        # Evaluate start, end, and step expressions
        start = self.evaluate(node.start)
        end = self.evaluate(node.end)
        step = self.evaluate(node.step) if node.step else 1  # Use step if provided, else default to 1

        # Validate numeric values
        if not isinstance(start, (int, float)):
            raise FluxRuntimeError(Token("IDENTIFIER", node.var_name, 0), "Start value must be a number")
        if not isinstance(end, (int, float)):
            raise FluxRuntimeError(Token("IDENTIFIER", node.var_name, 0), "End value must be a number")
        if not isinstance(step, (int, float)):
            raise FluxRuntimeError(Token("IDENTIFIER", node.var_name, 0), "Step value must be a number")
        if step == 0:
            raise FluxRuntimeError(Token("IDENTIFIER", node.var_name, 0), "Step cannot be zero")

        # Create a new environment for the loop
        loop_env = Environment(self.env)
        loop_env.define(node.var_name, start)
        
        result = None
        current = start
        
        # Loop condition depends on step direction
        while (step > 0 and current <= end) or (step < 0 and current >= end):
            body_env = Environment(loop_env)
            result = self.execute_block(node.body, body_env)
            current += step
            loop_env.assign(node.var_name, current, Token("IDENTIFIER", node.var_name, 0))
        
        return result

    def visit_repeat_until(self, node: RepeatUntil) -> Any:
        result = None
        while True:
            result = self.evaluate(node.body)
            if self.is_truthy(self.evaluate(node.condition)):
                break
        return result

    def visit_match(self, node: Match) -> Any:
        value = self.evaluate(node.expression)
        for case in node.cases:
            pattern = self.evaluate(case.pattern)
            if value == pattern:
                return self.evaluate(case.body)
        raise FluxRuntimeError(Token("MATCH", "match", 0), "No matching case found")

    def visit_match_case(self, node: MatchCase) -> Any:
        return self.evaluate(node.body)

    def visit_lambda(self, node: Lambda) -> Any:
        """Create an anonymous function"""
        # Create a FuncDef-like object for the anonymous function
        lambda_def = type('AnonymousFunc', (), {
            'params': node.params,
            'body': node.body,
            'name': '<anonymous>'
        })
        return Function(lambda_def, self.env, is_anonymous=True)

    def visit_func_def(self, node: FuncDef) -> None:
        func = Function(node, self.env)
        self.env.define(node.name, func)
        return func

    def visit_func_call(self, node: FuncCall) -> Any:
        callee = self.evaluate(node.callee)
        
        # Make sure callee is a function
        if not isinstance(callee, Function):
            raise FluxRuntimeError(
                node.token or Token("IDENTIFIER", str(node.callee), 0), 
                f"Can only call functions, got: {type(callee).__name__}"
            )
        
        # Evaluate the arguments
        arguments = []
        for arg in node.args:
            arguments.append(self.evaluate(arg))
        
        # Call the function with the evaluated arguments
        return callee.call(self, arguments, node.token or Token("IDENTIFIER", "function call", 0))

    def visit_return(self, node: Return) -> Any:
        value = self.evaluate(node.value)
        
        # Check if this return contains a function call that could be tail-optimized
        if isinstance(node.value, FuncCall) and self.current_function:
            self.in_tail_position = True
            try:
                value = self.evaluate_tail_recursive(node.value)
            except TailCall:
                pass  # This shouldn't happen, but just in case
        
        # Propagate the return value
        raise Return(value)

    def visit_array(self, node: Array) -> List[Any]:
        return [self.evaluate(elem) for elem in node.elements]

    def visit_dict(self, node: Dict) -> Dict[Any, Any]:
        return {self.evaluate(k): self.evaluate(v) for k, v in node.pairs}

    def visit_conditional_expr(self, node: ConditionalExpr) -> Any:
        condition = self.evaluate(node.condition)
        if self.is_truthy(condition):
            return self.evaluate(node.then_expr)
        return self.evaluate(node.else_expr)

    def visit_print(self, node: Print) -> Any:
        value = self.evaluate(node.expression)
        print(self.stringify(value))
        return value

    def check_number_operand(self, operator: Token, operand: Any):
        if not isinstance(operand, (int, float)):
            raise FluxRuntimeError(operator, "Operand must be a number")

    def check_number_operands(self, operator: Token, left: Any, right: Any):
        if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
            raise FluxRuntimeError(operator, "Operands must be numbers")

    def is_truthy(self, value: Any) -> bool:
        if value is None or value is False:
            return False
        if isinstance(value, (int, float)) and value == 0:
            return False  # Treating 0 as falsy
        return True

    def stringify(self, value: Any) -> str:
        if value is None:
            return "nil"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        if isinstance(value, Function):
            return str(value)
        return str(value)

def run_file(filename: str):
    evaluator = Evaluator()
    try:
        with open(filename, 'r') as file:
            program = file.read()
        lexer = Lexer(program)
        parser = Parser(lexer)
        tree = parser.parse()
        result = evaluator.interpret(tree)
        if result is not None:
            print(f"Final result: {evaluator.stringify(result)}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python evaluator.py <filename.fs>")
        sys.exit(1)
    filename = sys.argv[1]
    if not filename.endswith('.fs'):
        print("Error: File must have a .fs extension.")
        sys.exit(1)
    run_file(filename)