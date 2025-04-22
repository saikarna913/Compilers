from src.lexer import Lexer, Token, PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, LT, GT, LTE, GTE, EQEQ, NOTEQ, AND, OR, NOT
from src.parser import Parser
from src.ast_1 import (
    AST, BinOp, UnaryOp, Integer, Float, String, Boolean, Var, VarAssign, VarReassign, Block,
    If, While, For, RepeatUntil, Match, MatchCase, FuncDef, FuncCall, Return, Lambda,
    Array, Dict, ConditionalExpr, Print, ArrayAssign, ArrayAccess
)
import sys
import traceback
import re
from typing import Any, Dict, List, Optional
sys.setrecursionlimit(3000)

class FluxRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        if token is None:
            self.message = f"Error: {message}"
        else:
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

    def ancestor(self, distance: int) -> 'Environment':
        env = self
        for _ in range(distance):
            if env.parent is None:
                return env
            env = env.parent
        return env

    def get_at(self, distance: int, name: str) -> Any:
        return self.ancestor(distance).variables.get(name)

    def assign_at(self, distance: int, name: str, value: Any) -> Any:
        self.ancestor(distance).variables[name] = value
        return value

class BuiltinFunction:
    """Wrapper class for built-in functions"""
    def __init__(self, func, name):
        self.func = func
        self.name = name
        
    def __str__(self):
        return f"<built-in function {self.name}>"
    
    def call(self, evaluator, arguments, token):
        # Remove the evaluator parameter since it's not needed in the builtin_len method
        return self.func(arguments, token)  # Only pass arguments and token

class TailCall(Exception):
    """Exception used for tail call optimization"""
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

class Return(Exception):
    def __init__(self, value: Any):
        self.value = value
        super().__init__()

class Function:
    def __init__(self, declaration, closure: Environment, is_anonymous: bool = False):
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
        if isinstance(self, BuiltinFunction):  # Handle built-in functions
            return self.call(evaluator, arguments, token)
            
        if len(arguments) != len(self.params):
            raise FluxRuntimeError(token, 
                f"Expected {len(self.params)} arguments, got {len(arguments)}")
        
        env = Environment(self.closure)
        for param, arg in zip(self.params, arguments):
            env.define(param, arg)
        
        try:
            prev_function = evaluator.current_function
            prev_env = evaluator.env
            evaluator.current_function = self
            evaluator.env = env
            
            while True:
                try:
                    result = evaluator.execute_block(self.declaration.body, env)
                    evaluator.current_function = prev_function
                    evaluator.env = prev_env
                    return result
                except TailCall as tail_call:
                    if tail_call.function != self:
                        evaluator.current_function = prev_function
                        evaluator.env = prev_env
                        return tail_call.function.call(evaluator, tail_call.arguments, token)
                    
                    if len(tail_call.arguments) != len(self.params):
                        raise FluxRuntimeError(token, 
                            f"Expected {len(self.params)} arguments, got {len(tail_call.arguments)}")
                    
                    for param, arg in zip(self.params, tail_call.arguments):
                        env.assign(param, arg, token)
        except Return as r:
            evaluator.current_function = prev_function
            evaluator.env = prev_env
            return r.value

class BreakException(Exception):
    """Exception raised when a break statement is executed."""
    pass

class ContinueException(Exception):
    """Exception raised when a continue statement is executed."""
    pass

# Custom class for arrays to support length property
class FluxArray(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    @property
    def length(self):
        return len(self)
        
    def floor(self):
        """For numeric values, return the floor"""
        if len(self) != 1 or not isinstance(self[0], (int, float)):
            raise ValueError("floor() can only be called on a numeric value")
        return int(self[0])

class Evaluator:
    def __init__(self):
        self.global_env = Environment()
        self.env = self.global_env
        self.current_function = None
        self.in_tail_position = False
        self.add_builtins()

    def add_builtins(self):
        """Add built-in functions to the global environment"""
        # Add len() function
        self.global_env.define("len", BuiltinFunction(self.builtin_len, "len"))
        self.global_env.define("floor", BuiltinFunction(self.builtin_floor, "floor"))

    def builtin_len(self, arguments, token):
        """Handles len(array), len(string), and len(dict)."""
        if len(arguments) != 1:
            raise FluxRuntimeError(token, f"'len' expected 1 argument, got {len(arguments)}")
        
        arg = arguments[0]

        if arg is None:
            raise FluxRuntimeError(token, "'len' cannot be applied to 'None'")

        if isinstance(arg, (list, str, dict)):
            return len(arg)

        if hasattr(arg, '__len__'):
            return arg.__len__()

        raise FluxRuntimeError(token, f"'len' expects an array, string, or dictionary, but got {type(arg).__name__}")

    def builtin_floor(self, arguments, token):
        """Handles floor(number) function."""
        if len(arguments) != 1:
            raise FluxRuntimeError(token, f"'floor' expected 1 argument, got {len(arguments)}")
        
        arg = arguments[0]
        
        if not isinstance(arg, (int, float)):
            raise FluxRuntimeError(token, f"'floor' expects a number, but got {type(arg).__name__}")
            
        return int(arg)

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
            last_idx = len(block.statements) - 1
            
            for i, stmt in enumerate(block.statements):
                is_last = (i == last_idx)
                old_tail_pos = self.in_tail_position
                
                if is_last:
                    self.in_tail_position = self.in_tail_position or (self.current_function is not None)
                
                if isinstance(stmt, Return):
                    value = self.evaluate(stmt.value)
                    if isinstance(stmt.value, FuncCall) and self.in_tail_position:
                        callee = self.evaluate(stmt.value.callee)
                        arguments = [self.evaluate(arg) for arg in stmt.value.args]
                        if isinstance(callee, Function) and callee == self.current_function:
                            raise TailCall(callee, arguments)
                    raise Return(value)
                
                result = self.evaluate(stmt)
                self.in_tail_position = old_tail_pos
            
            return result
        finally:
            self.env = previous_env

    def visit_integer(self, node: Integer) -> Any:
        return node.value

    def visit_float(self, node: Float) -> Any:
        return node.value

    def visit_string(self, node: String) -> str:
        return node.value

    def visit_boolean(self, node: Boolean) -> bool:
        return node.value

    def visit_var(self, node: Var) -> Any:
        # Special handling for property access like arr.length
        if '.' in node.name:
            parts = node.name.split('.')
            if len(parts) == 2:
                obj_name, prop_name = parts
                obj = self.env.get(obj_name, node.token)
                
                # Handle array length
                if prop_name == 'length' and isinstance(obj, list):
                    return len(obj)
                    
                # Handle numeric methods like floor()
                elif prop_name == 'floor' and isinstance(obj, (int, float)):
                    return int(obj)
                    
                # Handle accessing object properties
                elif hasattr(obj, prop_name):
                    return getattr(obj, prop_name)
                    
                raise FluxRuntimeError(node.token, f"Property '{prop_name}' does not exist on {type(obj).__name__}")
        
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
            if isinstance(left, list) and isinstance(right, list):
                return left + right  # Support array concatenation
            raise FluxRuntimeError(node.operator, "Operands must be two numbers, two strings, two arrays, or a string and another type for '+'")
        
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
    
        try:
            while self.is_truthy(self.evaluate(node.condition)):
                try:
                    # Execute the body of the loop
                    result = self.execute_block(node.body, self.env)
                except BreakException:
                    break
                except ContinueException:
                    # Just skip to the next iteration
                    continue
        except Exception as e:
            if not isinstance(e, (BreakException, ContinueException)):
                raise e
                
        return result

    def visit_for(self, node):
        """Execute a for loop with support for break and continue."""
        # Evaluate start and end expressions
        start = self.evaluate(node.start)
        end = self.evaluate(node.end)
        
        # Get step value (default to 1 if not provided)
        step = 1
        if node.step:
            step = self.evaluate(node.step)
        
        # Create a new environment for the loop scope
        loop_env = Environment(self.env)
        
        # Token for variable access
        var_token = getattr(node, 'token', None)
        
        # Initialize loop variable
        loop_env.define(node.variable, start)
        
        # Execute loop
        result = None
        
        try:
            # Loop logic based on step direction
            if step > 0:
                while loop_env.get(node.variable, var_token) < end:
                    try:
                        # Execute loop body with the loop environment
                        old_env = self.env
                        self.env = loop_env
                        result = self.execute_block(node.body, loop_env)
                        self.env = old_env
                    except BreakException:
                        break
                    except ContinueException:
                        # Skip to the next iteration
                        pass
                    
                    # Increment loop variable
                    current = loop_env.get(node.variable, var_token)
                    loop_env.assign(node.variable, current + step, var_token)
            else:
                while loop_env.get(node.variable, var_token) > end:
                    try:
                        # Execute loop body with the loop environment
                        old_env = self.env
                        self.env = loop_env
                        result = self.execute_block(node.body, loop_env)
                        self.env = old_env
                    except BreakException:
                        break
                    except ContinueException:
                        # Skip to the next iteration
                        pass
                    
                    # Decrement loop variable
                    current = loop_env.get(node.variable, var_token)
                    loop_env.assign(node.variable, current + step, var_token)
        except Exception as e:
            if not isinstance(e, (BreakException, ContinueException)):
                raise e
        
        return result

    def visit_repeat_until(self, node: RepeatUntil) -> Any:
        result = None
    
        try:
            while True:
                try:
                    # Execute the body
                    result = self.execute_block(node.body, self.env)
                except BreakException:
                    break
                except ContinueException:
                    # Just continue to the condition check
                    pass
                    
                # Check if we should exit the loop
                if self.is_truthy(self.evaluate(node.condition)):
                    break
        except Exception as e:
            if not isinstance(e, (BreakException, ContinueException)):
                raise e
                
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
        
        # Special handling for method calls like arr.length or num.floor()
        if hasattr(node.callee, 'name') and '.' in node.callee.name:
            parts = node.callee.name.split('.')
            if len(parts) == 2:
                obj_name, method_name = parts
                obj = self.env.get(obj_name, node.token)
                
                # Handle floor method for numbers
                if method_name == 'floor' and isinstance(obj, (int, float)):
                    return int(obj)
        
        if not isinstance(callee, (Function, BuiltinFunction)):
            raise FluxRuntimeError(
                node.token or Token("IDENTIFIER", str(node.callee), 0), 
                f"Can only call functions, got: {type(callee).__name__}"
            )
        
        arguments = [self.evaluate(arg) for arg in node.args]
        
        if self.in_tail_position and isinstance(callee, Function) and callee == self.current_function:
            raise TailCall(callee, arguments)
        
        return callee.call(self, arguments, node.token or Token("IDENTIFIER", "function call", 0))

    def visit_return(self, node: Return) -> Any:
        was_tail = self.in_tail_position
        self.in_tail_position = self.current_function is not None
        
        try:
            value = self.evaluate(node.value)
            
            if isinstance(node.value, FuncCall) and self.in_tail_position:
                callee = self.evaluate(node.value.callee)
                arguments = [self.evaluate(arg) for arg in node.value.args]
                
                if isinstance(callee, Function) and callee == self.current_function:
                    raise TailCall(callee, arguments)
            
            raise Return(value)
        finally:
            self.in_tail_position = was_tail

    def visit_array(self, node: Array) -> List[Any]:
        return [self.evaluate(element) for element in node.elements]

    def visit_array_assign(self, node: ArrayAssign) -> Any:
        # Get the array object
        if hasattr(node.array, 'name'):
            array_name = node.array.name
            array = self.env.get(array_name, node.token)
        else:
            array_name = node.array
            array = self.env.get(array_name, node.token)
        
        # Get the index and value
        index = self.evaluate(node.index)
        value = self.evaluate(node.value)

        if not isinstance(array, list):
            raise FluxRuntimeError(node.token, f"Cannot assign to non-array type: {type(array).__name__}")
        if not isinstance(index, int):
            raise FluxRuntimeError(node.token, f"Array index must be an integer, got {type(index).__name__}")
        if index < 0 or index >= len(array):
            raise FluxRuntimeError(node.token, f"Array index {index} out of bounds")

        # Create a new array with the updated value
        new_array = array.copy()
        new_array[index] = value
        
        # Update the environment with the new array
        self.env.assign(array_name, new_array, node.token)
        return value
    
    def visit_array_access(self, node: ArrayAccess) -> Any:
        # Get the array or dictionary
        if hasattr(node.array, 'name'):
            array_name = node.array.name
            array = self.env.get(array_name, node.token)
        else:
            array_name = node.array
            array = self.env.get(array_name, node.token)
        
        index = self.evaluate(node.index)

        # Handle different indexable types
        if isinstance(array, list):
            if not isinstance(index, int):
                raise FluxRuntimeError(node.token, f"Array index must be an integer, got {type(index).__name__}")
            if index < 0 or index >= len(array):
                raise FluxRuntimeError(node.token, f"Array index {index} out of bounds")
            return array[index]
        elif isinstance(array, str):  # Add support for string indexing
            if not isinstance(index, int):
                raise FluxRuntimeError(node.token, f"String index must be an integer, got {type(index).__name__}")
            if index < 0 or index >= len(array):
                raise FluxRuntimeError(node.token, f"String index {index} out of bounds")
            return array[index]
        elif isinstance(array, dict):
            return array.get(index)
        else:
            raise FluxRuntimeError(node.token, f"Cannot index non-array/dictionary type: {type(array).__name__}")

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

    def visit_break(self, node):
        """Handle a break statement by raising a BreakException."""
        raise BreakException()

    def visit_continue(self, node):
        """Handle a continue statement by raising a ContinueException."""
        raise ContinueException()

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
            return False
        if isinstance(value, str) and value == "":
            return False
        return True

    def stringify(self, value: Any) -> str:
        if value is None:
            return "nil"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        if isinstance(value, (Function, BuiltinFunction)):
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
    run_file(filename)
