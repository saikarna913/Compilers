from src.AST.ast_1 import *
from .opcodes import *

class BytecodeCompiler(Visitor):
    def __init__(self):
        self.instructions = []  # List of (opcode, *args)
        self.constants = []     # Constants table
        self.var_names = {}     # Variable name to index
        self.var_count = 0
        self.labels = []        # For jumps
        self.break_stack = []   # For break/continue
        self.continue_stack = []

    def compile(self, node):
        self.instructions = []
        self.constants = []
        self.var_names = {}
        self.var_count = 0
        self.labels = []
        self.break_stack = []
        self.continue_stack = []
        node.accept(self)
        self.instructions.append((HALT,))
        return self.instructions, self.constants

    def add_const(self, value):
        if value in self.constants:
            return self.constants.index(value)
        self.constants.append(value)
        return len(self.constants) - 1

    def visit_integer(self, node):
        idx = self.add_const(node.value)
        self.instructions.append((LOAD_CONST, idx))

    def visit_float(self, node):
        idx = self.add_const(node.value)
        self.instructions.append((LOAD_CONST, idx))

    def visit_string(self, node):
        idx = self.add_const(node.value)
        self.instructions.append((LOAD_CONST, idx))

    def visit_boolean(self, node):
        self.instructions.append((LOAD_TRUE if node.value else LOAD_FALSE,))

    def visit_var(self, node):
        self.instructions.append((LOAD_VAR, node.name))

    def visit_var_assign(self, node):
        node.value.accept(self)
        # Push the value back onto the stack after storing
        self.instructions.append((DUP,))  # Duplicate the value
        self.instructions.append((STORE_VAR, node.name))

    def visit_var_reassign(self, node):
        node.value.accept(self)
        # No need for DUP here, since REASSIGN_VAR now pushes the value back onto the stack
        self.instructions.append((REASSIGN_VAR, node.name))

    def visit_bin_op(self, node):
        node.left.accept(self)
        node.right.accept(self)
        op = node.operator.value
        if op == '+':
            self.instructions.append((ADD,))
        elif op == '-':
            self.instructions.append((SUBTRACT,))
        elif op == '*':
            self.instructions.append((MULTIPLY,))
        elif op == '/':
            self.instructions.append((DIVIDE,))
        elif op == '**':
            self.instructions.append((EXPONENT,))
        elif op == '%':
            self.instructions.append((MODULO,))
        elif op == '==':
            self.instructions.append((EQUAL,))
        elif op == '!=':
            self.instructions.append((NOT_EQUAL,))
        elif op == '<':
            self.instructions.append((LESS_THAN,))
        elif op == '>':
            self.instructions.append((GREATER_THAN,))
        elif op == '<=':
            self.instructions.append((LESS_EQUAL,))
        elif op == '>=':
            self.instructions.append((GREATER_EQUAL,))
        elif op == 'and':
            self.instructions.append((AND,))
        elif op == 'or':
            self.instructions.append((OR,))
        else:
            raise Exception(f"Unknown binary operator: {op}")

    def visit_unary_op(self, node):
        node.right.accept(self)
        op = node.operator.value
        if op == '-':
            self.instructions.append((NEGATE,))
        elif op == 'not':
            self.instructions.append((NOT,))
        else:
            raise Exception(f"Unknown unary operator: {op}")

    def visit_lambda(self, node):
        # Create a new compiler instance for the lambda body
        compiler = BytecodeCompiler()
        
        # Compile the lambda body separately
        body_instructions, body_constants = compiler.compile(node.body)
        
        # Add RETURN instruction if not present (to ensure lambda always returns a value)
        if not body_instructions or body_instructions[-1][0] != RETURN:
            # If the last instruction isn't a return, add one that returns the top of the stack
            if body_instructions and body_instructions[-1][0] != HALT:
                # There are instructions, but the last one is not a return - add DUP and RETURN
                body_instructions.append((DUP,))
                body_instructions.append((RETURN,))
            else:
                # Empty body or just HALT - return None
                body_instructions.append((LOAD_CONST, compiler.add_const(None)))
                body_instructions.append((RETURN,))
        
        # Store lambda data as a constant
        idx = self.add_const({
            'name': 'lambda',  # Anonymous function
            'params': node.params,
            'code': body_instructions,
            'consts': body_constants,
            'free_vars': []  # Will be captured from the closure's env at runtime
        })
        
        # Create a closure for this lambda
        self.instructions.append((LOAD_LAMBDA, idx))

    def visit_block(self, node):
        for stmt in node.statements:
            stmt.accept(self)

    def visit_if(self, node):
        node.condition.accept(self)
        jmp_false_idx = len(self.instructions)
        self.instructions.append((JUMP_IF_FALSE, None))
        node.then_branch.accept(self)
        if node.else_branch:
            jmp_end_idx = len(self.instructions)
            self.instructions.append((JUMP, None))
            self.instructions[jmp_false_idx] = (JUMP_IF_FALSE, len(self.instructions))
            node.else_branch.accept(self)
            self.instructions[jmp_end_idx] = (JUMP, len(self.instructions))
        else:
            self.instructions[jmp_false_idx] = (JUMP_IF_FALSE, len(self.instructions))

    def visit_while(self, node):
        start_idx = len(self.instructions)
        node.condition.accept(self)
        jmp_false_idx = len(self.instructions)
        self.instructions.append((JUMP_IF_FALSE, None))
        self.continue_stack.append(start_idx)
        self.break_stack.append([])
        node.body.accept(self)
        self.instructions.append((JUMP, start_idx))
        self.instructions[jmp_false_idx] = (JUMP_IF_FALSE, len(self.instructions))
        for idx in self.break_stack.pop():
            self.instructions[idx] = (JUMP, len(self.instructions))
        self.continue_stack.pop()

    def visit_for(self, node):
        # for (let i = start to end step step) { body }
        node.start.accept(self)
        self.instructions.append((STORE_VAR, node.variable))
        start_idx = len(self.instructions)
        self.instructions.append((LOAD_VAR, node.variable))
        node.end.accept(self)
        self.instructions.append((GREATER_THAN,))
        jmp_false_idx = len(self.instructions)
        self.instructions.append((JUMP_IF_TRUE, None))
        self.continue_stack.append(start_idx)
        self.break_stack.append([])
        node.body.accept(self)
        self.instructions.append((LOAD_VAR, node.variable))
        if node.step:
            node.step.accept(self)
        else:
            self.instructions.append((LOAD_CONST, self.add_const(1)))
        self.instructions.append((ADD,))
        self.instructions.append((STORE_VAR, node.variable))
        self.instructions.append((JUMP, start_idx))
        self.instructions[jmp_false_idx] = (JUMP_IF_TRUE, len(self.instructions))
        for idx in self.break_stack.pop():
            self.instructions[idx] = (JUMP, len(self.instructions))
        self.continue_stack.pop()

    def visit_break(self, node):
        self.break_stack[-1].append(len(self.instructions))
        self.instructions.append((JUMP, None))

    def visit_continue(self, node):
        self.instructions.append((JUMP, self.continue_stack[-1]))

    def visit_func_def(self, node):
        # Create a new compiler instance for the function body
        compiler = BytecodeCompiler()
        
        # Compile the function body separately
        body_instructions, body_constants = compiler.compile(node.body)
        
        # Store function data as a constant
        idx = self.add_const({
            'name': node.name,
            'params': node.params,
            'code': body_instructions,
            'consts': body_constants,
            'free_vars': node.free_vars or []
        })
        
        # Add instruction to define the function
        self.instructions.append((DEFINE_FUNC, node.name, idx))

    def visit_func_call(self, node):
        # Check if this is a dictionary access function call (e.g., dict["key"]())
        if isinstance(node.callee, ArrayAccess):
            # First put the dictionary on the stack
            node.callee.array.accept(self)
            
            # Then put the key on the stack
            node.callee.index.accept(self)
            
            # Push all arguments first
            for arg in node.args:
                arg.accept(self)
                
            # Special opcode for dictionary function call with number of arguments
            self.instructions.append((DICT_FUNC_CALL, len(node.args)))
        else:
            # Standard function call
            # First put the function reference on the stack
            node.callee.accept(self)
            
            # Then push all arguments onto the stack in order
            for arg in node.args:
                arg.accept(self)
                
            # Finally call the function with the number of arguments
            self.instructions.append((CALL_FUNC, len(node.args)))

    def visit_return(self, node):
        node.value.accept(self)
        self.instructions.append((RETURN,))

    def visit_array(self, node):
        for elem in node.elements:
            elem.accept(self)
        self.instructions.append((BUILD_ARRAY, len(node.elements)))

    def visit_dict(self, node):
        for key, value in node.pairs:
            key.accept(self)
            
            # If the value is a lambda function, we need special handling to ensure proper closure capture
            if isinstance(value, Lambda):
                # Create a new compiler instance for the lambda body
                lambda_compiler = BytecodeCompiler()
                
                # Compile the lambda body separately
                body_instructions, body_constants = lambda_compiler.compile(value.body)
                
                # Add RETURN instruction if not present
                if not body_instructions or body_instructions[-1][0] != RETURN:
                    if body_instructions and body_instructions[-1][0] != HALT:
                        body_instructions.append((DUP,))
                        body_instructions.append((RETURN,))
                    else:
                        body_instructions.append((LOAD_CONST, lambda_compiler.add_const(None)))
                        body_instructions.append((RETURN,))
                
                # Store lambda data as a constant
                idx = self.add_const({
                    'name': 'lambda',  # Anonymous function
                    'params': value.params,
                    'code': body_instructions,
                    'consts': body_constants,
                    'free_vars': []  # Will be captured from the closure's env at runtime
                })
                
                # Load the lambda onto the stack
                self.instructions.append((LOAD_LAMBDA, idx))
            else:
                # For non-lambda values, process normally
                value.accept(self)
        
        self.instructions.append((BUILD_DICT, len(node.pairs)))

    def visit_print(self, node):
        node.expression.accept(self)
        self.instructions.append((PRINT,))

    def visit_array_access(self, node):
        # First compile the array expression
        node.array.accept(self)
        
        # Then compile the index expression
        node.index.accept(self)
        
        # This will push the accessed element on the stack
        self.instructions.append((ARRAY_ACCESS,))
        
    def visit_array_assign(self, node):
        # First compile the array expression
        node.array.accept(self)
        
        # Then compile the index expression
        node.index.accept(self)
        
        # Then compile the value to be assigned
        node.value.accept(self)
        
        # This will assign the value to the array at the specified index
        self.instructions.append((ARRAY_ASSIGN,))
    
    def visit_multi_dim_array_access(self, node):
        # First compile the base array expression
        node.array.accept(self)
        
        # Then compile each index expression
        for index in node.indices:
            index.accept(self)
        
        # Use the multi-dimensional array access opcode with number of dimensions
        self.instructions.append((MULTI_DIM_ACCESS, len(node.indices)))
    
    def visit_multi_dim_array_assign(self, node):
        # First compile the base array expression
        node.array.accept(self)
        
        # Then compile each index expression
        for index in node.indices:
            index.accept(self)
        
        # Then compile the value to be assigned
        node.value.accept(self)
        
        # Use the multi-dimensional array assign opcode with number of dimensions
        self.instructions.append((MULTI_DIM_ASSIGN, len(node.indices)))
    
    def visit_size_of(self, node):
        # Compile the expression whose size we want to get
        node.expression.accept(self)
        
        # Add the GET_SIZE opcode
        self.instructions.append((GET_SIZE,))

    # Optionally, add support for more AST nodes as needed

# Usage example:
# from parser.parser import Parser
# ast = Parser(Lexer(source_code)).parse()
# compiler = BytecodeCompiler()
# instructions, consts = compiler.compile(ast)
# print(instructions)
# print(consts)
