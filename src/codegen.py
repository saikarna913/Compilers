from enum import Enum, auto
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
import sys
import traceback
import math
import re
from lexer import (Lexer, Token, LET, IF, WHILE, FOR, FUNC, RETURN, PRINT, ELSE, ASSIGN, EQUALS,
                  PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, LPAREN, RPAREN, LBRACE, RBRACE,
                  LT, GT, LTE, GTE, EQEQ, NOTEQ, AND, OR, NOT, COMMA, LBRACKET, RBRACKET, COLON,
                  IDENTIFIER, INTEGER, FLOAT, STRING, TRUE, FALSE, EOF, TO, IN, REPEAT, UNTIL, MATCH, ARROW, QUESTION_MARK, STEP)
from ast_1 import (AST, BinOp, UnaryOp, Integer, Float, String, Boolean, Var, VarAssign, VarReassign, Block,
                  If, While, For, FuncDef, Return, FuncCall, Print, Array, Dict, ConditionalExpr,
                  RepeatUntil, Match, MatchCase, AstPrinter, Lambda,ArrayAccess,ArrayAssign)
from parser import Parser

class OpCode(Enum):
    # Stack operations
    PUSH = auto()      
    POP = auto()          
    DUP = auto()          # Duplicate top of stack
    SWAP = auto()         # Swap top two stack items
    
    # Variable operations
    LOAD = auto()         # Load variable onto stack
    STORE = auto()        # Store top of stack in variable
    REASSIGN = auto()     # Reassign existing variable
    
    # Arithmetic operations
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    POW = auto()
    NEG = auto()          # Unary negation
    INC = auto()          # Increment (optimization)
    DEC = auto()          # Decrement (optimization)
    
    # Comparison operations
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    
    # Logical operations
    NOT = auto()
    AND = auto()
    OR = auto()
    
    # Control flow
    JUMP = auto()         # Unconditional jump
    JUMP_IF_FALSE = auto() # Conditional jump if top of stack is false
    CALL = auto()         # Call function
    RETURN = auto()       # Return from function
    TAIL_CALL = auto()    # Tail call optimization
    
    # Data structures
    BUILD_ARRAY = auto()  # Build array from stack values
    BUILD_DICT = auto()   # Build dictionary from stack key-value pairs
    INDEX = auto()        # Array/dict index access
    STORE_INDEX = auto()  # Array/dict index assignment
    LEN = auto()          # Length of array/dict/string
    SLICE = auto()        # Array/string slice
    
    # Built-ins
    PRINT = auto()        # Print top of stack
    RANGE = auto()        # Built-in range function
    
    # Math operations
    MATH_SQRT = auto()
    MATH_SIN = auto()
    MATH_COS = auto()
    MATH_TAN = auto()
    
    # Special
    NOP = auto()          # No operation
    HALT = auto()         # Stop execution

@dataclass
class Instruction:
    opcode: OpCode
    operand: Any = None  # Can be value, variable name, jump target, etc.
    lineno: int = 0      # Source line number for debugging

class BytecodeFunction:
    def __init__(self, name: str, params: List[str], instructions: List[Instruction], 
                 constants: List[Any], locals_count: int = 0, is_tail_recursive: bool = False):
        self.name = name
        self.params = params
        self.instructions = instructions
        self.constants = constants
        self.locals_count = locals_count  # Number of local variables
        self.is_tail_recursive = is_tail_recursive
    
    def __str__(self):
        return f"<BytecodeFunction {self.name} params={self.params} locals={self.locals_count}>"

class Bytecode:
    def __init__(self, main: BytecodeFunction, functions: List[BytecodeFunction] = None):
        self.main = main
        self.functions = functions or []
        self.global_constants = []  # Constants shared across all functions
    
    def add_function(self, func: BytecodeFunction):
        self.functions.append(func)
    
    def find_function(self, name: str) -> Optional[BytecodeFunction]:
        for func in self.functions:
            if func.name == name:
                return func
        return None

class Compiler:
    def __init__(self):
        self.current_function = BytecodeFunction("main", [], [], [])
        self.bytecode = Bytecode(self.current_function)
        self.loop_stack = []
        self.function_stack = []
        self.scopes = [{}]
        self.tail_call_positions = set()
        self.match_labels = {}

    def compile(self, node: AST) -> Bytecode:
        if isinstance(node, Block):
            for stmt in node.statements:
                stmt.accept(self)
        else:
            node.accept(self)
        self.emit(OpCode.HALT)
        return self.bytecode

    def emit(self, opcode: OpCode, operand=None, lineno=0):
        if self.current_function is None:
            raise RuntimeError("Cannot emit instruction - no current function")
        self.current_function.instructions.append(Instruction(opcode, operand, lineno))

    def add_constant(self, value: Any) -> int:
        # Use current_function.constants instead of self.constants
        if isinstance(value, (int, float, str, bool)) and value in self.current_function.constants:
            return self.current_function.constants.index(value)
        self.current_function.constants.append(value)
        return len(self.current_function.constants) - 1

    def add_global_constant(self, value: Any) -> int:
        if value in self.bytecode.global_constants:
            return self.bytecode.global_constants.index(value)
        self.bytecode.global_constants.append(value)
        return len(self.bytecode.global_constants) - 1

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare_variable(self, name: str):
        self.scopes[-1][name] = True

    def is_local(self, name: str) -> bool:
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False

    def visit_bin_op(self, node: BinOp) -> None:
        node.left.accept(self)
        node.right.accept(self)
        
        op_map = {
            PLUS: OpCode.ADD,
            MINUS: OpCode.SUB,
            MULTIPLY: OpCode.MUL,
            DIVIDE: OpCode.DIV,
            REM: OpCode.MOD,
            EXPONENT: OpCode.POW,
            LT: OpCode.LT,
            GT: OpCode.GT,
            LTE: OpCode.LTE,
            GTE: OpCode.GTE,
            EQEQ: OpCode.EQ,
            NOTEQ: OpCode.NEQ,
            AND: OpCode.AND,
            OR: OpCode.OR
        }
        
        if node.operator.type not in op_map:
            raise ValueError(f"Unknown binary operator: {node.operator.type}")
        self.emit(op_map[node.operator.type], lineno=node.operator.line if hasattr(node.operator, 'line') else 0)

    def visit_unary_op(self, node: UnaryOp) -> None:
        if node.operator.type == MINUS and isinstance(node.right, (Integer, Float)):
            const_idx = self.add_constant(-node.right.value)
            self.emit(OpCode.PUSH, const_idx)
            return
        
        node.right.accept(self)
        
        if node.operator.type == MINUS:
            # UnaryOp has no token, use operator.line
            self.emit(OpCode.NEG, lineno=node.operator.line if hasattr(node.operator, 'line') else 0)
        elif node.operator.type == NOT:
            self.emit(OpCode.NOT, lineno=node.operator.line if hasattr(node.operator, 'line') else 0)
        else:
            raise ValueError(f"Unknown unary operator: {node.operator.type}")

    def visit_integer(self, node: Integer) -> None:
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.PUSH, const_idx)  # No token, no lineno needed

    def visit_float(self, node: Float) -> None:
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.PUSH, const_idx)  # No token, no lineno needed

    def visit_boolean(self, node: Boolean) -> None:
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.PUSH, const_idx)  # No token, no lineno needed

    def visit_string(self, node: String) -> None:
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.PUSH, const_idx)  # No token, no lineno needed

    def visit_var(self, node: Var) -> None:
        self.emit(OpCode.LOAD, node.name, lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)

    def visit_var_assign(self, node: VarAssign) -> None:
        node.value.accept(self)
        self.declare_variable(node.name)
        self.emit(OpCode.STORE, node.name, lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)

    def visit_var_reassign(self, node: VarReassign) -> None:
        node.value.accept(self)
        self.emit(OpCode.REASSIGN, node.name, lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)

    def visit_block(self, node: Block) -> None:
        self.enter_scope()
        for stmt in node.statements:
            stmt.accept(self)
        self.exit_scope()

    def visit_if(self, node: If) -> None:
        node.condition.accept(self)
        self.emit(OpCode.JUMP_IF_FALSE, None)  # No token, no lineno
        false_jump_idx = len(self.current_function.instructions) - 1
        node.then_branch.accept(self)
        
        if node.else_branch:
            self.emit(OpCode.JUMP, None)
            jump_idx = len(self.current_function.instructions) - 1
            self.current_function.instructions[false_jump_idx].operand = len(self.current_function.instructions)
            node.else_branch.accept(self)
            self.current_function.instructions[jump_idx].operand = len(self.current_function.instructions)
        else:
            self.current_function.instructions[false_jump_idx].operand = len(self.current_function.instructions)

    def visit_while(self, node: While) -> None:
        loop_start = len(self.current_function.instructions)
        self.loop_stack.append(('while', loop_start))
        node.condition.accept(self)
        self.emit(OpCode.JUMP_IF_FALSE, None)  # No token, no lineno
        exit_jump_idx = len(self.current_function.instructions) - 1
        node.body.accept(self)
        self.emit(OpCode.JUMP, loop_start)
        self.current_function.instructions[exit_jump_idx].operand = len(self.current_function.instructions)
        self.loop_stack.pop()

    def visit_for(self, node: For) -> None:
        node.start.accept(self)
        self.declare_variable(node.var_name)
        self.emit(OpCode.STORE, node.var_name)  # No token in For, no lineno
        loop_start = len(self.current_function.instructions)
        self.loop_stack.append(('for', loop_start))
        self.emit(OpCode.LOAD, node.var_name)
        node.end.accept(self)
        
        if node.step:
            node.step.accept(self)
            self.emit(OpCode.PUSH, 0)
            self.emit(OpCode.GT)
            self.emit(OpCode.JUMP_IF_FALSE, None)
            step_positive_jump = len(self.current_function.instructions) - 1
            self.emit(OpCode.LT)
            self.emit(OpCode.JUMP, None)
            skip_negative_jump = len(self.current_function.instructions) - 1
            self.current_function.instructions[step_positive_jump].operand = len(self.current_function.instructions)
            self.emit(OpCode.LOAD, node.var_name)
            node.end.accept(self)
            self.emit(OpCode.GT)
            self.current_function.instructions[skip_negative_jump].operand = len(self.current_function.instructions)
        else:
            self.emit(OpCode.LT)
        
        self.emit(OpCode.JUMP_IF_FALSE, None)
        exit_jump_idx = len(self.current_function.instructions) - 1
        node.body.accept(self)
        self.emit(OpCode.LOAD, node.var_name)
        if node.step:
            node.step.accept(self)
        else:
            self.emit(OpCode.PUSH, self.add_constant(1))
        self.emit(OpCode.ADD)
        self.emit(OpCode.STORE, node.var_name)
        self.emit(OpCode.JUMP, loop_start)
        self.current_function.instructions[exit_jump_idx].operand = len(self.current_function.instructions)
        self.loop_stack.pop()

    def visit_repeat_until(self, node: RepeatUntil) -> None:
        loop_start = len(self.current_function.instructions)
        self.loop_stack.append(('repeat_until', loop_start))
        node.body.accept(self)
        node.condition.accept(self)
        self.emit(OpCode.JUMP_IF_FALSE, loop_start)  # No token, no lineno

    def visit_match(self, node: Match) -> None:
        node.expression.accept(self)
        end_jumps = []
        for case in node.cases:
            self.emit(OpCode.DUP)
            case.pattern.accept(self)
            self.emit(OpCode.EQ)
            self.emit(OpCode.JUMP_IF_FALSE, None)
            false_jump_idx = len(self.current_function.instructions) - 1
            self.emit(OpCode.POP)
            case.body.accept(self)
            self.emit(OpCode.JUMP, None)
            end_jumps.append(len(self.current_function.instructions) - 1)
            self.current_function.instructions[false_jump_idx].operand = len(self.current_function.instructions)
        self.emit(OpCode.POP)
        for jump_idx in end_jumps:
            self.current_function.instructions[jump_idx].operand = len(self.current_function.instructions)

    def visit_func_def(self, node: FuncDef) -> None:
        parent_function = self.current_function
        func = BytecodeFunction(node.name, node.params, [], [])
        self.current_function = func
        self.function_stack.append(func)
        self.enter_scope()
        for param in node.params:
            self.declare_variable(param)
        node.body.accept(self)
        if not func.instructions or func.instructions[-1].opcode != OpCode.RETURN:
            self.emit(OpCode.PUSH, self.add_constant(None))
            self.emit(OpCode.RETURN)
        self.exit_scope()
        self.current_function = parent_function
        self.function_stack.pop()
        self.bytecode.add_function(func)
        const_idx = self.add_constant(func)
        self.emit(OpCode.PUSH, const_idx)
        self.emit(OpCode.STORE, node.name, lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)
        print(f"Stored {node.name} at constant index {const_idx}") 

    def visit_lambda(self, node: Lambda) -> None:
        func = BytecodeFunction(f"lambda_{len(self.bytecode.functions)}", node.params, [], [])
        parent_function = self.current_function
        self.current_function = func
        self.function_stack.append(func)
        self.enter_scope()
        for param in node.params:
            self.declare_variable(param)
        node.body.accept(self)
        if not func.instructions or func.instructions[-1].opcode != OpCode.RETURN:
            self.emit(OpCode.PUSH, self.add_constant(None))
            self.emit(OpCode.RETURN)
        self.exit_scope()
        self.current_function = parent_function
        self.function_stack.pop()
        self.bytecode.add_function(func)
        self.emit(OpCode.PUSH, self.add_constant(func))

    def visit_func_call(self, node: FuncCall) -> None:
        is_tail_call = False
        if (self.function_stack and 
            isinstance(node.callee, Var) and 
            node.callee.name == self.function_stack[-1].name and
            len(self.current_function.instructions) > 0 and
            self.current_function.instructions[-1].opcode == OpCode.RETURN):
            is_tail_call = True
        node.callee.accept(self)  # Push function first
        for arg in node.args:
            arg.accept(self)  # Push args after
        if is_tail_call:
            self.emit(OpCode.TAIL_CALL, len(node.args), lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)
        else:
            self.emit(OpCode.CALL, len(node.args), lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)
        def visit_return(self, node: Return) -> None:
            if node.value:
                node.value.accept(self)
            else:
                self.emit(OpCode.PUSH, self.add_constant(None))
            self.emit(OpCode.RETURN, lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)

    def visit_return(self, node: Return) -> None:
        if node.value:
            node.value.accept(self)  # Compile the return expression
        else:
            self.emit(OpCode.PUSH, self.add_constant(None))  # Default to None if no value
        self.emit(OpCode.RETURN, lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)

    def visit_array(self, node: Array) -> None:
        for element in node.elements:
            element.accept(self)
        self.emit(OpCode.BUILD_ARRAY, len(node.elements))  # No token, no lineno

    def visit_array_access(self, node: ArrayAccess) -> None:
        node.array.accept(self)
        node.index.accept(self)
        self.emit(OpCode.INDEX, lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)

    def visit_array_assign(self, node: ArrayAssign) -> None:
        node.array.accept(self)
        node.index.accept(self)
        node.value.accept(self)
        self.emit(OpCode.STORE_INDEX, lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)

    def visit_dict(self, node: Dict) -> None:
        for key, value in node.pairs:
            key.accept(self)
            value.accept(self)
        self.emit(OpCode.BUILD_DICT, len(node.pairs))  # No token, no lineno

    def visit_print(self, node: Print) -> None:
        node.expression.accept(self)
        self.emit(OpCode.PRINT, lineno=node.token.line if node.token and hasattr(node.token, 'line') else 0)

    def visit_conditional_expr(self, node: ConditionalExpr) -> None:
        node.condition.accept(self)
        self.emit(OpCode.JUMP_IF_FALSE, None)  # No token, no lineno
        false_jump_idx = len(self.current_function.instructions) - 1
        node.then_expr.accept(self)
        self.emit(OpCode.JUMP, None)
        jump_idx = len(self.current_function.instructions) - 1
        self.current_function.instructions[false_jump_idx].operand = len(self.current_function.instructions)
        node.else_expr.accept(self)
        self.current_function.instructions[jump_idx].operand = len(self.current_function.instructions)

class VM:
    def __init__(self, bytecode: Bytecode):
        self.bytecode = bytecode
        self.stack = []
        self.globals = { 
            'len': lambda x: len(x)  # Add built-in len function
        }
        self.frames = []
        self.current_frame = None
        self.pc = 0  # Program counter
        self.halted = False
        self.call_stack_size = 0
        self.max_call_stack_size = 10000  # Prevent stack overflow
    
    def run(self):
        # Initialize with main function
        self.call_function(self.bytecode.main, [])
        
        while not self.halted:
            self.step()
    
    def step(self):
        if not self.current_frame or self.pc >= len(self.current_frame.func.instructions):
            self.halted = True
            return
        instr = self.current_frame.func.instructions[self.pc]
        #print(f"PC: {self.pc}, Instr: {instr}, Stack: {self.stack}, Globals: {self.globals}, Locals: {self.current_frame.locals if self.current_frame else {}}")
        self.pc += 1
        
        try:
            if instr.opcode == OpCode.PUSH:
                # Push constant onto stack
                if isinstance(instr.operand, int) and instr.operand < len(self.current_frame.func.constants):
                    self.stack.append(self.current_frame.func.constants[instr.operand])
                else:
                    self.stack.append(instr.operand)
            
            elif instr.opcode == OpCode.POP:
                self.stack.pop()
            
            elif instr.opcode == OpCode.DUP:
                if len(self.stack) < 1:
                    raise RuntimeError("Stack underflow")
                self.stack.append(self.stack[-1])
            
            elif instr.opcode == OpCode.SWAP:
                if len(self.stack) < 2:
                    raise RuntimeError("Stack underflow")
                self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
            
            elif instr.opcode == OpCode.LOAD:
                # Look up variable in current frame or globals
                if instr.operand in self.current_frame.locals:
                    self.stack.append(self.current_frame.locals[instr.operand])
                elif instr.operand in self.globals:
                    self.stack.append(self.globals[instr.operand])
                else:
                    raise RuntimeError(f"Undefined variable: {instr.operand}")
            
            elif instr.opcode == OpCode.STORE:
                if len(self.stack) == 0:
                    raise RuntimeError("Stack underflow")
                value = self.stack.pop()
                if self.is_local(instr.operand):
                    self.current_frame.locals[instr.operand] = value
                else:
                    self.globals[instr.operand] = value
            
            elif instr.opcode == OpCode.REASSIGN:
                if len(self.stack) == 0:
                    raise RuntimeError("Stack underflow")
                value = self.stack[-1]
                if instr.operand in self.current_frame.locals:
                    self.current_frame.locals[instr.operand] = value
                elif instr.operand in self.globals:
                    self.globals[instr.operand] = value
                else:
                    raise RuntimeError(f"Cannot reassign undefined variable: {instr.operand}")
            
            # Arithmetic operations
            elif instr.opcode == OpCode.ADD:
                self.binary_op(lambda a, b: a + b)
            elif instr.opcode == OpCode.SUB:
                self.binary_op(lambda a, b: a - b)
            elif instr.opcode == OpCode.MUL:
                self.binary_op(lambda a, b: a * b)
            elif instr.opcode == OpCode.DIV:
                self.binary_op(lambda a, b: a / b)
            elif instr.opcode == OpCode.MOD:
                self.binary_op(lambda a, b: a % b)
            elif instr.opcode == OpCode.POW:
                self.binary_op(lambda a, b: a ** b)
            elif instr.opcode == OpCode.NEG:
                self.unary_op(lambda a: -a)
            elif instr.opcode == OpCode.INC:
                self.unary_op(lambda a: a + 1)
            elif instr.opcode == OpCode.DEC:
                self.unary_op(lambda a: a - 1)
            
            # Comparison operations
            elif instr.opcode == OpCode.EQ:
                self.binary_op(lambda a, b: a == b)
            elif instr.opcode == OpCode.NEQ:
                self.binary_op(lambda a, b: a != b)
            elif instr.opcode == OpCode.LT:
                self.binary_op(lambda a, b: a < b)
            elif instr.opcode == OpCode.GT:
                self.binary_op(lambda a, b: a > b)
            elif instr.opcode == OpCode.LTE:
                self.binary_op(lambda a, b: a <= b)
            elif instr.opcode == OpCode.GTE:
                self.binary_op(lambda a, b: a >= b)
            
            # Logical operations
            elif instr.opcode == OpCode.NOT:
                self.unary_op(lambda a: not a)
            elif instr.opcode == OpCode.AND:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a and b)
            elif instr.opcode == OpCode.OR:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a or b)
            
            # Control flow
            elif instr.opcode == OpCode.JUMP:
                self.pc = instr.operand
            
            elif instr.opcode == OpCode.JUMP_IF_FALSE:
                if len(self.stack) == 0:
                    raise RuntimeError("Stack underflow")
                if not self.stack.pop():
                    self.pc = instr.operand
            
            elif instr.opcode == OpCode.CALL:
                if len(self.stack) < instr.operand + 1:
                    raise RuntimeError("Not enough arguments on stack")
                
                # Get function and arguments
                args = []
                for _ in range(instr.operand):
                    args.insert(0, self.stack.pop())
                func = self.stack.pop()
                
                # Handle both direct function objects and constant references
                if isinstance(func, int) and func < len(self.bytecode.global_constants):
                    func = self.bytecode.global_constants[func]
                
                if isinstance(func, BytecodeFunction):
                    self.call_function(func, args)
                elif callable(func):
                    result = func(*args)
                    self.stack.append(result)
                else:
                    raise RuntimeError(f"Cannot call non-function: {type(func).__name__}")
            
            elif instr.opcode == OpCode.TAIL_CALL:
                if len(self.stack) < instr.operand + 1:
                    raise RuntimeError("Not enough arguments on stack")
                
                # Get function and arguments
                args = []
                for _ in range(instr.operand):
                    args.insert(0, self.stack.pop())
                func = self.stack.pop()
                
                if isinstance(func, BytecodeFunction):
                    # For tail calls, we reuse the current frame
                    if len(self.frames) == 0:
                        raise RuntimeError("No frame to reuse for tail call")
                    
                    # Reuse current frame
                    frame = self.frames[-1]
                    frame.pc = 0
                    
                    # Update arguments
                    for param, arg in zip(func.params, args):
                        frame.locals[param] = arg
                elif callable(func):
                    # Native function
                    result = func(*args)
                    self.stack.append(result)
                else:
                    raise RuntimeError(f"Cannot call non-function: {type(func).__name__}")
            
            elif instr.opcode == OpCode.RETURN:
                if len(self.stack) == 0:
                    retval = None
                else:
                    retval = self.stack.pop()
                
                if len(self.frames) > 0:
                    # Pop frame and restore PC
                    old_frame = self.frames.pop()
                    self.call_stack_size -= 1
                    
                    if len(self.frames) > 0:
                        self.current_frame = self.frames[-1]
                        self.pc = old_frame.return_pc
                    else:
                        self.current_frame = None
                        self.pc = 0
                    
                    # Push return value
                    if retval is not None:
                        self.stack.append(retval)
                else:
                    self.halted = True
            
            # Data structures
            elif instr.opcode == OpCode.BUILD_ARRAY:
                elements = []
                for _ in range(instr.operand):
                    elements.insert(0, self.stack.pop())
                self.stack.append(elements)
            
            elif instr.opcode == OpCode.BUILD_DICT:
                pairs = {}
                for _ in range(instr.operand):
                    value = self.stack.pop()
                    key = self.stack.pop()
                    if not isinstance(key, (str, int, float, bool)):
                        raise RuntimeError("Dictionary keys must be immutable types")
                    pairs[key] = value
                self.stack.append(pairs)
            
            elif instr.opcode == OpCode.INDEX:
                index = self.stack.pop()
                container = self.stack.pop()
                
                if isinstance(container, (list, tuple)) and isinstance(index, int):
                    if index < 0 or index >= len(container):
                        raise RuntimeError("Array index out of bounds")
                    self.stack.append(container[index])
                elif isinstance(container, dict):
                    if index not in container:
                        raise RuntimeError(f"Key not found in dictionary: {index}")
                    self.stack.append(container[index])
                elif isinstance(container, str):
                    if not isinstance(index, int):
                        raise RuntimeError("String index must be integer")
                    if index < 0 or index >= len(container):
                        raise RuntimeError("String index out of bounds")
                    self.stack.append(container[index])
                else:
                    raise RuntimeError(f"Cannot index type {type(container).__name__}")
            
            elif instr.opcode == OpCode.STORE_INDEX:
                value = self.stack.pop()
                index = self.stack.pop()
                container = self.stack.pop()
                
                if isinstance(container, list) and isinstance(index, int):
                    if index < 0 or index >= len(container):
                        raise RuntimeError("Array index out of bounds")
                    container[index] = value
                elif isinstance(container, dict):
                    if not isinstance(index, (str, int, float, bool)):
                        raise RuntimeError("Dictionary keys must be immutable types")
                    container[index] = value
                else:
                    raise RuntimeError(f"Cannot index assign to type {type(container).__name__}")
                
                self.stack.append(value)
            
            elif instr.opcode == OpCode.LEN:
                obj = self.stack.pop()
                if isinstance(obj, (list, dict, str)):
                    self.stack.append(len(obj))
                else:
                    raise RuntimeError(f"Cannot get length of type {type(obj).__name__}")
            
            elif instr.opcode == OpCode.PRINT:
                if len(self.stack) == 0:
                    raise RuntimeError("Stack underflow")
                print(self.stack.pop())
            
            elif instr.opcode == OpCode.RANGE:
                step = self.stack.pop()
                end = self.stack.pop()
                start = self.stack.pop()
                self.stack.append(list(range(start, end, step)))
            
            # Math operations
            elif instr.opcode == OpCode.MATH_SQRT:
                self.unary_op(math.sqrt)
            elif instr.opcode == OpCode.MATH_SIN:
                self.unary_op(math.sin)
            elif instr.opcode == OpCode.MATH_COS:
                self.unary_op(math.cos)
            elif instr.opcode == OpCode.MATH_TAN:
                self.unary_op(math.tan)
            
            elif instr.opcode == OpCode.HALT:
                self.halted = True
            
            elif instr.opcode == OpCode.NOP:
                pass
            
            else:
                raise RuntimeError(f"Unknown opcode: {instr.opcode}")
        
        except Exception as e:
            raise RuntimeError(f"Runtime error at instruction {self.pc-1} ({instr.opcode}): {str(e)}")
    
    def call_function(self, func: BytecodeFunction, args: list):
        if self.call_stack_size >= self.max_call_stack_size:
            raise RuntimeError("Maximum call stack size exceeded")
        
        # Create new frame
        frame = Frame(func, self.pc)
        
        # Set up locals with parameters
        for param, arg in zip(func.params, args):
            frame.locals[param] = arg
        
        # Push frame onto call stack
        self.frames.append(frame)
        self.current_frame = frame
        self.pc = 0  # Start at beginning of function
        self.call_stack_size += 1
    
    def is_local(self, name: str) -> bool:
        """Check if a variable name refers to a local in the current frame"""
        return name in self.current_frame.locals if self.current_frame else False
    
    def binary_op(self, op):
        if len(self.stack) < 2:
            raise RuntimeError("Stack underflow")
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(op(a, b))
    
    def unary_op(self, op):
        if len(self.stack) < 1:
            raise RuntimeError("Stack underflow")
        a = self.stack.pop()
        self.stack.append(op(a))

@dataclass
class Frame:
    """Call frame for function execution"""
    func: 'BytecodeFunction'
    return_pc: int
    locals: 'Dict[str, Any]' = None
    
    def __post_init__(self):
        if self.locals is None:
            self.locals = {}

def run_file(filename: str):
    try:
        with open(filename, 'r') as file:
            program = file.read()
        
        # Parse to AST
        lexer = Lexer(program)
        parser = Parser(lexer)
        tree = parser.parse()
        
        # Compile to bytecode
        compiler = Compiler()
        bytecode = compiler.compile(tree)
        
        # Execute bytecode
        vm = VM(bytecode)
        vm.run()
        
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
