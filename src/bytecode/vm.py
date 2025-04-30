from .opcodes import *

class VMError(Exception):
    """Base class for VM errors"""
    pass

class StackUnderflowError(VMError):
    """Raised when trying to pop from an empty stack"""
    pass

class UndefinedVariableError(VMError):
    """Raised when trying to access an undefined variable"""
    pass

class DivisionByZeroError(VMError):
    """Raised when trying to divide by zero"""
    pass

class InvalidOperationError(VMError):
    """Raised when an operation is invalid for the given operands"""
    pass

class ReturnException(Exception):
    """Used to handle return statements in functions"""
    def __init__(self, value):
        self.value = value

class Closure:
    """Represents a closure (function with captured environment)"""
    def __init__(self, name, params, code, consts, env=None):
        self.name = name
        self.params = params
        self.code = code
        self.consts = consts
        self.env = env or {}
    
    def __repr__(self):
        return f"<Closure {self.name}>"

class Frame:
    """Execution frame for function calls"""
    def __init__(self, ip=0, closure=None, args=None, parent=None):
        self.ip = ip                  # Instruction pointer
        self.closure = closure        # Current function closure
        self.locals = {}              # Local variables
        self.stack = []               # Operand stack
        self.parent = parent          # Parent frame
        
        # Set up arguments in local variables if this is a function frame
        if closure and args:
            for i, param in enumerate(closure.params):
                if i < len(args):
                    self.locals[param] = args[i]
                else:
                    self.locals[param] = None  # Optional parameters default to None

    def lookup_var(self, name):
        """Look up a variable in the current scope or parent scopes"""
        # First check locals
        if name in self.locals:
            return self.locals[name]
        
        # Then check closure environment
        if self.closure and name in self.closure.env:
            return self.closure.env[name]
        
        # Finally check parent frame
        if self.parent:
            try:
                return self.parent.lookup_var(name)
            except UndefinedVariableError:
                # If not found in parent, check if we have a closure
                if self.closure and self.closure.env:
                    # Try to find the variable in the closure's environment
                    if name in self.closure.env:
                        return self.closure.env[name]
                raise UndefinedVariableError(f"Undefined variable: {name}")
        
        raise UndefinedVariableError(f"Undefined variable: {name}")
    
    def assign_var(self, name, value):
        """Assign a value to a variable in the appropriate scope"""
        # First try locals
        if name in self.locals:
            self.locals[name] = value
            return
        
        # Then check closure environment
        if self.closure and name in self.closure.env:
            self.closure.env[name] = value
            return
        
        # Then try parent frame
        if self.parent:
            try:
                self.parent.assign_var(name, value)
                return
            except UndefinedVariableError:
                # If not found in parent, define it in the current scope
                self.locals[name] = value
                return
        
        # If not found anywhere, define it in the current scope
        self.locals[name] = value

class BytecodeVM:
    """Virtual Machine for executing bytecode instructions"""
    
    def __init__(self, debug=False):
        self.global_frame = Frame()   # Global execution frame
        self.current_frame = self.global_frame
        self.functions = {}           # Global function definitions
        self.debug = debug
        self.running = False
        
        # Add built-in functions
        self._add_builtins()
    
    def _add_builtins(self):
        """Add built-in functions to the global environment"""
        # to_string function: converts any value to a string
        def to_string_func(args):
            if len(args) != 1:
                raise InvalidOperationError("to_string requires exactly one argument")
            return str(args[0])
        
        # to_number function: converts a string to a number
        def to_number_func(args):
            if len(args) != 1:
                raise InvalidOperationError("to_number requires exactly one argument")
            try:
                # Try converting to int first
                return int(args[0])
            except ValueError:
                try:
                    # Try converting to float if int fails
                    return float(args[0])
                except ValueError:
                    raise InvalidOperationError(f"Cannot convert '{args[0]}' to a number")
        
        # split function: splits a string by a delimiter
        def split_func(args):
            if len(args) != 2:
                raise InvalidOperationError("split requires exactly two arguments: string and delimiter")
            if not isinstance(args[0], str):
                raise InvalidOperationError(f"First argument to split must be a string, got {type(args[0])}")
            return args[0].split(args[1])
        
        # substring function: extracts a substring
        def substring_func(args):
            if len(args) < 2 or len(args) > 3:
                raise InvalidOperationError("substring requires 2 or 3 arguments: string, start, [end]")
            string = args[0]
            start = args[1]
            end = args[2] if len(args) > 2 else None
            
            if not isinstance(string, str):
                raise InvalidOperationError(f"First argument to substring must be a string, got {type(string)}")
            if not isinstance(start, int):
                raise InvalidOperationError(f"Second argument to substring must be an integer, got {type(start)}")
            if end is not None and not isinstance(end, int):
                raise InvalidOperationError(f"Third argument to substring must be an integer, got {type(end)}")
            
            return string[start:end] if end is not None else string[start:]
        
        # __append function: appends a value to an array (internal implementation)
        def append_func(args):
            if len(args) != 2:
                raise InvalidOperationError("__append requires exactly two arguments: array and value")
            array = args[0]
            value = args[1]
            
            if not isinstance(array, list):
                raise InvalidOperationError(f"First argument to __append must be an array, got {type(array)}")
            
            # Append the value to the array and return the array
            array.append(value)
            return array
        
        # size/length function: returns the size or length of a collection
        def size_func(args):
            if len(args) != 1:
                raise InvalidOperationError("size requires exactly one argument")
            collection = args[0]
            
            if collection is None:
                return 0
            elif isinstance(collection, (list, tuple, dict, str)):
                return len(collection)
            else:
                raise InvalidOperationError(f"Cannot get size of {type(collection)}")
        
        # word function for the number-to-words conversion used in Problem 17
        def word_func(args):
            if len(args) != 1:
                raise InvalidOperationError("word requires exactly one argument: number")
            n = args[0]
            
            if not isinstance(n, int):
                raise InvalidOperationError(f"Argument to word must be an integer, got {type(n)}")
            
            # Implementation of number to words conversion
            ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
            teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
            tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
            
            if n == 1000:
                return "onethousand"
            
            result = ""
            if n >= 100:
                result += ones[n // 100] + "hundred"
                if n % 100 != 0:
                    result += "and"
            
            rem = n % 100
            if rem >= 20:
                result += tens[rem // 10] + ones[rem % 10]
            elif rem >= 10:
                result += teens[rem - 10]
            elif rem > 0 or n < 100:
                result += ones[rem]
                
            return result
        
        # Create closure wrappers for the Python functions
        builtins = {
            "to_string": (to_string_func, ["value"]),
            "to_number": (to_number_func, ["value"]),
            "split": (split_func, ["string", "delimiter"]),
            "substring": (substring_func, ["string", "start", "end"]),
            "__append": (append_func, ["array", "value"]),
            "size": (size_func, ["collection"]),  # New size function
            "word": (word_func, ["number"])
        }
        
        # Add the built-ins to the global frame
        for name, (func, params) in builtins.items():
            closure = Closure(
                name=name,
                params=params,
                code=[],  # Empty code as this is a built-in function
                consts={},
                env={}
            )
            
            # Override the execute method
            closure.execute = func
            
            # Add it to the global frame
            self.global_frame.locals[name] = closure
    
    def execute(self, instructions, constants):
        """Execute a bytecode program"""
        self.running = True
        last_value = None
        
        if self.current_frame.ip == 0:  # Only reset the frame if we're starting from the beginning
            self.current_frame.ip = 0
        
        while self.running and self.current_frame.ip < len(instructions):
            instruction = instructions[self.current_frame.ip]
            opcode = instruction[0]
            
            if self.debug:
                stack_repr = ", ".join(str(x) for x in self.current_frame.stack)
                print(f"IP: {self.current_frame.ip}, Opcode: {OPCODE_NAMES.get(opcode, opcode)}, Stack: [{stack_repr}]")
                if len(self.current_frame.locals) > 0:
                    print(f"Current locals: {self.current_frame.locals}")
                if self.current_frame.closure and self.current_frame.closure.env:
                    print(f"Current closure env: {self.current_frame.closure.env}")
            
            self.current_frame.ip += 1
            
            try:
                # Execute the instruction
                if opcode == LOAD_CONST:
                    self.current_frame.stack.append(constants[instruction[1]])
                
                elif opcode == LOAD_TRUE:
                    self.current_frame.stack.append(True)
                
                elif opcode == LOAD_FALSE:
                    self.current_frame.stack.append(False)
                
                elif opcode == LOAD_VAR:
                    name = instruction[1]
                    try:
                        value = self.current_frame.lookup_var(name)
                        self.current_frame.stack.append(value)
                    except UndefinedVariableError as e:
                        raise e
                
                elif opcode == STORE_VAR:
                    name = instruction[1]
                    value = self.current_frame.stack.pop()
                    # Store the variable in the current scope
                    self.current_frame.locals[name] = value
                    # Push the value back onto the stack so it's available for later use
                    self.current_frame.stack.append(value)
                
                elif opcode == REASSIGN_VAR:
                    name = instruction[1]
                    value = self.current_frame.stack.pop()
                    try:
                        self.current_frame.assign_var(name, value)
                    except UndefinedVariableError as e:
                        raise e
                    # Push the value back on the stack for further use
                    self.current_frame.stack.append(value)
                
                elif opcode == ADD:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    try:
                        result = left + right
                        self.current_frame.stack.append(result)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot add {left} and {right}: {e}")
                
                elif opcode == SUBTRACT:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    try:
                        self.current_frame.stack.append(left - right)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot subtract {right} from {left}: {e}")
                
                elif opcode == MULTIPLY:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    try:
                        self.current_frame.stack.append(left * right)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot multiply {left} and {right}: {e}")
                
                elif opcode == DIVIDE:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    if right == 0:
                        raise DivisionByZeroError("Division by zero")
                    try:
                        self.current_frame.stack.append(left / right)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot divide {left} by {right}: {e}")
                
                elif opcode == EXPONENT:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    try:
                        self.current_frame.stack.append(left ** right)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot raise {left} to the power of {right}: {e}")
                
                elif opcode == MODULO:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    if right == 0:
                        raise DivisionByZeroError("Modulo by zero")
                    try:
                        self.current_frame.stack.append(left % right)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot compute {left} modulo {right}: {e}")
                
                elif opcode == NEGATE:
                    value = self.current_frame.stack.pop()
                    try:
                        self.current_frame.stack.append(-value)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot negate {value}: {e}")
                
                elif opcode == EQUAL:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    self.current_frame.stack.append(left == right)
                
                elif opcode == NOT_EQUAL:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    self.current_frame.stack.append(left != right)
                
                elif opcode == LESS_THAN:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    try:
                        self.current_frame.stack.append(left < right)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot compare {left} < {right}: {e}")
                
                elif opcode == GREATER_THAN:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    try:
                        self.current_frame.stack.append(left > right)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot compare {left} > {right}: {e}")
                
                elif opcode == LESS_EQUAL:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    try:
                        self.current_frame.stack.append(left <= right)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot compare {left} <= {right}: {e}")
                
                elif opcode == GREATER_EQUAL:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    try:
                        self.current_frame.stack.append(left >= right)
                    except (TypeError, ValueError) as e:
                        raise InvalidOperationError(f"Cannot compare {left} >= {right}: {e}")
                
                elif opcode == AND:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    self.current_frame.stack.append(left and right)
                
                elif opcode == OR:
                    right = self.current_frame.stack.pop()
                    left = self.current_frame.stack.pop()
                    self.current_frame.stack.append(left or right)
                
                elif opcode == NOT:
                    value = self.current_frame.stack.pop()
                    self.current_frame.stack.append(not value)
                
                elif opcode == JUMP:
                    self.current_frame.ip = instruction[1]
                
                elif opcode == JUMP_IF_FALSE:
                    condition = self.current_frame.stack.pop()
                    if not condition:
                        self.current_frame.ip = instruction[1]
                
                elif opcode == JUMP_IF_TRUE:
                    condition = self.current_frame.stack.pop()
                    if condition:
                        self.current_frame.ip = instruction[1]
                
                elif opcode == DEFINE_FUNC:
                    name = instruction[1]
                    func_data = constants[instruction[2]]
                    
                    # Create a snapshot of the current environment for the closure
                    captured_env = {}
                    
                    # First capture parameters and local variables from the current scope
                    for var_name, var_value in self.current_frame.locals.items():
                        captured_env[var_name] = var_value
                    
                    # Also include variables from parent environments
                    if self.current_frame.closure and self.current_frame.closure.env:
                        captured_env.update(self.current_frame.closure.env)
                    
                    # Also include current locals
                    for var_name, var_value in self.current_frame.locals.items():
                        if var_name not in captured_env:  # Don't overwrite existing values
                            captured_env[var_name] = var_value
                    
                    if self.debug:
                        print(f"DEFINE_FUNC: {name} capturing env: {captured_env}")
                    
                    # Create the closure with the captured environment
                    closure = Closure(
                        name=func_data['name'],
                        params=func_data['params'],
                        code=func_data['code'],
                        consts=func_data['consts'],
                        env=captured_env  # Use the original environment, not a copy
                    )
                    
                    # Store the function in the current scope
                    self.current_frame.locals[name] = closure
                
                elif opcode == DICT_FUNC_CALL:
                    num_args = instruction[1]
                    args = []
                    
                    # Pop arguments from the stack in reverse order
                    for _ in range(num_args):
                        args.insert(0, self.current_frame.stack.pop())
                    
                    # Get the key and dictionary from the stack
                    key = self.current_frame.stack.pop()
                    dictionary = self.current_frame.stack.pop()
                    
                    if self.debug:
                        print(f"DICT_FUNC_CALL: dict={dictionary}, key={key}, args={args}")
                    
                    if not isinstance(dictionary, dict):
                        raise InvalidOperationError(f"Cannot access key {key} of non-dictionary {dictionary}")
                    
                    if key not in dictionary:
                        raise UndefinedVariableError(f"Dictionary key not found: {key}")
                    
                    func = dictionary[key]
                    
                    if not isinstance(func, Closure):
                        raise InvalidOperationError(f"Cannot call {key} as a function")
                    
                    # Create a new frame for the function execution
                    new_frame = Frame(
                        ip=0,
                        closure=func,
                        args=args,  # Arguments are already in the correct order
                        parent=self.current_frame  # Link to the parent frame
                    )
                    
                    # Add the environment from the function's closure
                    if func.env:
                        for var_name, var_value in func.env.items():
                            if var_name not in new_frame.locals:
                                new_frame.locals[var_name] = var_value
                    
                    # If the function needs to reference itself (for recursion)
                    # add it to its own environment
                    if func.name != 'lambda' and func.name not in new_frame.locals:
                        new_frame.locals[func.name] = func
                    
                    # Save the current frame as parent
                    old_frame = self.current_frame
                    
                    # Switch to the new frame
                    self.current_frame = new_frame
                    
                    try:
                        # Execute the function's code
                        result = self.execute(func.code, func.consts)
                        
                        # Propagate changes from closure variables back to the original environment
                        if func.env:
                            for var_name, var_value in new_frame.locals.items():
                                # Update the closure environment with any variable changes
                                if var_name in func.env:
                                    func.env[var_name] = var_value
                        
                        # Restore the parent frame and push the result
                        self.current_frame = old_frame
                        self.current_frame.stack.append(result)
                    except ReturnException as e:
                        # Handle return statement
                        
                        # Propagate changes from closure variables back to the original environment
                        if func.env:
                            for var_name, var_value in new_frame.locals.items():
                                # Update the closure environment with any variable changes
                                if var_name in func.env:
                                    func.env[var_name] = var_value
                        
                        # Restore the parent frame
                        self.current_frame = old_frame
                        self.current_frame.stack.append(e.value)
                
                elif opcode == LOAD_LAMBDA:
                    func_data = constants[instruction[1]]
                    
                    # Create a snapshot of the current environment for the closure
                    captured_env = {}
                    
                    # First capture local variables from the current scope
                    for var_name, var_value in self.current_frame.locals.items():
                        captured_env[var_name] = var_value
                    
                    # Also include variables from parent environments
                    if self.current_frame.closure and self.current_frame.closure.env:
                        for var_name, var_value in self.current_frame.closure.env.items():
                            if var_name not in captured_env:
                                captured_env[var_name] = var_value
                    
                    if self.debug:
                        print(f"LOAD_LAMBDA capturing env: {captured_env}")
                    
                    # Create the closure with the captured environment
                    closure = Closure(
                        name=func_data['name'],
                        params=func_data['params'],
                        code=func_data['code'],
                        consts=func_data['consts'],
                        env=captured_env.copy()  # Create a deep copy to prevent reference issues
                    )
                    
                    # Push the closure onto the stack
                    self.current_frame.stack.append(closure)
                
                elif opcode == CALL_FUNC:
                    num_args = instruction[1]
                    args = []
                    
                    # Pop arguments from the stack in the correct order
                    for _ in range(num_args):
                        args.insert(0, self.current_frame.stack.pop())
                    
                    # Normal function call
                    func = self.current_frame.stack.pop()
                    
                    if self.debug:
                        print(f"CALL_FUNC: {func}, args: {args}")
                    
                    if not isinstance(func, Closure):
                        raise InvalidOperationError(f"Cannot call {func} as a function")
                    
                    # Create a new frame for the function execution
                    new_frame = Frame(
                        ip=0,
                        closure=func,
                        args=args,  # Arguments are already in the correct order
                        parent=self.current_frame  # Link to the parent frame
                    )
                    
                    # Add the environment from the function's closure
                    if func.env:
                        for var_name, var_value in func.env.items():
                            if var_name not in new_frame.locals:
                                new_frame.locals[var_name] = var_value
                    
                    # If the function needs to reference itself (for recursion)
                    # add it to its own environment
                    if func.name != 'lambda' and func.name not in new_frame.locals:
                        new_frame.locals[func.name] = func
                    
                    # Save the current frame as parent
                    
                    old_frame = self.current_frame
                    
                    # Switch to the new frame
                    self.current_frame = new_frame
                    
                    try:
                        # Execute the function's code
                        result = self.execute(func.code, func.consts)
                        
                        # Propagate changes from closure variables back to the original environment
                        if func.env:
                            for var_name, var_value in new_frame.locals.items():
                                # Update the closure environment with any variable changes
                                if var_name in func.env:
                                    func.env[var_name] = var_value
                        
                        # Restore the parent frame and push the result
                        self.current_frame = old_frame
                        self.current_frame.stack.append(result)
                    except ReturnException as e:
                        # Handle return statement
                        
                        # Propagate changes from closure variables back to the original environment
                        if func.env:
                            for var_name, var_value in new_frame.locals.items():
                                # Update the closure environment with any variable changes
                                if var_name in func.env:
                                    func.env[var_name] = var_value
                        
                        # Restore the parent frame
                        self.current_frame = old_frame
                        self.current_frame.stack.append(e.value)
                
                # Ensure RETURN always pushes a value:
                elif opcode == RETURN:
                    if not self.current_frame.stack:
                        value = None
                    else:
                        value = self.current_frame.stack.pop()
                    if self.current_frame.parent is not None:
                        raise ReturnException(value)
                    return value
                
                elif opcode == BUILD_ARRAY:
                    num_elements = instruction[1]
                    elements = []
                    for _ in range(num_elements):
                        elements.insert(0, self.current_frame.stack.pop())
                    self.current_frame.stack.append(elements)
                
                elif opcode == BUILD_DICT:
                    num_pairs = instruction[1]
                    dictionary = {}
                    for _ in range(num_pairs):
                        value = self.current_frame.stack.pop()
                        key = self.current_frame.stack.pop()

                        # If the value is a Closure, capture the current environment
                        if isinstance(value, Closure):
                            captured_env = {}
                            # Capture current locals
                            for var_name, var_value in self.current_frame.locals.items():
                                captured_env[var_name] = var_value
                            # Capture parent closure env
                            if self.current_frame.closure and self.current_frame.closure.env:
                                for var_name, var_value in self.current_frame.closure.env.items():
                                    if var_name not in captured_env:
                                        captured_env[var_name] = var_value
                            # Assign a new env to the closure (deep copy)
                            value.env = captured_env.copy()
                        # Ensure the key is hashable
                        try:
                            dictionary[key] = value
                        except (TypeError, ValueError) as e:
                            raise InvalidOperationError(f"Invalid dictionary key {key}: {e}")
                    self.current_frame.stack.append(dictionary)
                
                elif opcode == ARRAY_ACCESS:
                    index = self.current_frame.stack.pop()
                    array_or_dict = self.current_frame.stack.pop()
                    
                    if self.debug:
                        print(f"ARRAY_ACCESS: array/dict={array_or_dict}, index={index}")
                    
                    if isinstance(array_or_dict, (list, tuple)):
                        if isinstance(index, int):
                            if 0 <= index < len(array_or_dict):
                                self.current_frame.stack.append(array_or_dict[index])
                            else:
                                raise InvalidOperationError(f"Index {index} out of bounds for array of length {len(array_or_dict)}")
                        else:
                            raise InvalidOperationError(f"Array index must be an integer, got {type(index)}")
                    elif isinstance(array_or_dict, dict):
                        if index in array_or_dict:
                            self.current_frame.stack.append(array_or_dict[index])
                        else:
                            raise InvalidOperationError(f"Key {index} not found in dictionary")
                    else:
                        raise InvalidOperationError(f"Cannot access index {index} of {type(array_or_dict)}")
                
                elif opcode == ARRAY_ASSIGN:
                    value = self.current_frame.stack.pop()
                    index = self.current_frame.stack.pop()
                    array_or_dict = self.current_frame.stack.pop()
                    
                    if self.debug:
                        print(f"ARRAY_ASSIGN: array/dict={array_or_dict}, index={index}, value={value}")
                    
                    if isinstance(array_or_dict, list):
                        if isinstance(index, int):
                            if 0 <= index < len(array_or_dict):
                                array_or_dict[index] = value
                                self.current_frame.stack.append(value)
                            else:
                                raise InvalidOperationError(f"Index {index} out of bounds for array of length {len(array_or_dict)}")
                        else:
                            raise InvalidOperationError(f"Array index must be an integer, got {type(index)}")
                    elif isinstance(array_or_dict, dict):
                        array_or_dict[index] = value
                        self.current_frame.stack.append(value)
                    else:
                        raise InvalidOperationError(f"Cannot assign to index {index} of {type(array_or_dict)}")
                
                elif opcode == GET_SIZE:
                    # Get the size/length of a collection (string, array, or dictionary)
                    collection = self.current_frame.stack.pop()
                    
                    if self.debug:
                        print(f"GET_SIZE: collection={collection}")
                    
                    if collection is None:
                        # None has a size of 0
                        self.current_frame.stack.append(0)
                    elif isinstance(collection, (list, tuple)):
                        # For arrays/lists
                        self.current_frame.stack.append(len(collection))
                    elif isinstance(collection, dict):
                        # For dictionaries
                        self.current_frame.stack.append(len(collection))
                    elif isinstance(collection, str):
                        # For strings
                        self.current_frame.stack.append(len(collection))
                    else:
                        # For unsupported types
                        raise InvalidOperationError(f"Cannot get size of {type(collection)}")
                
                elif opcode == MULTI_DIM_ACCESS:
                    # For accessing multi-dimensional arrays (e.g., arr[i][j])
                    # The number of dimensions is stored in the instruction
                    num_dims = instruction[1]
                    
                    # Pop all indices from the stack
                    indices = []
                    for _ in range(num_dims):
                        indices.insert(0, self.current_frame.stack.pop())
                    
                    # Get the base array
                    array = self.current_frame.stack.pop()
                    
                    if self.debug:
                        print(f"MULTI_DIM_ACCESS: array={array}, indices={indices}")
                    
                    # Navigate through the dimensions
                    current = array
                    for i, index in enumerate(indices):
                        if isinstance(current, (list, tuple)):
                            if isinstance(index, int):
                                if 0 <= index < len(current):
                                    current = current[index]
                                else:
                                    raise InvalidOperationError(f"Index {index} out of bounds for array of length {len(current)} at dimension {i+1}")
                            else:
                                raise InvalidOperationError(f"Array index must be an integer, got {type(index)} at dimension {i+1}")
                        elif isinstance(current, dict):
                            if index in current:
                                current = current[index]
                            else:
                                raise InvalidOperationError(f"Key {index} not found in dictionary at dimension {i+1}")
                        else:
                            raise InvalidOperationError(f"Cannot access index {index} of {type(current)} at dimension {i+1}")
                    
                    # Push the final result onto the stack
                    self.current_frame.stack.append(current)
                
                elif opcode == MULTI_DIM_ASSIGN:
                    # For assigning to multi-dimensional arrays (e.g., arr[i][j] = value)
                    # The number of dimensions is stored in the instruction
                    num_dims = instruction[1]
                    
                    # Get the value to assign
                    value = self.current_frame.stack.pop()
                    
                    # Pop all indices from the stack
                    indices = []
                    for _ in range(num_dims):
                        indices.insert(0, self.current_frame.stack.pop())
                    
                    # Get the base array
                    array = self.current_frame.stack.pop()
                    
                    if self.debug:
                        print(f"MULTI_DIM_ASSIGN: array={array}, indices={indices}, value={value}")
                    
                    # Navigate to the second-to-last dimension
                    current = array
                    for i, index in enumerate(indices[:-1]):
                        if isinstance(current, (list, tuple)):
                            if isinstance(index, int):
                                if 0 <= index < len(current):
                                    # Convert tuple to list if needed
                                    if isinstance(current, tuple):
                                        # This is just for completeness, tuples are immutable
                                        raise InvalidOperationError("Cannot modify a tuple")
                                    current = current[index]
                                else:
                                    raise InvalidOperationError(f"Index {index} out of bounds for array of length {len(current)} at dimension {i+1}")
                            else:
                                raise InvalidOperationError(f"Array index must be an integer, got {type(index)} at dimension {i+1}")
                        elif isinstance(current, dict):
                            if index in current:
                                current = current[index]
                            else:
                                # Create a new dictionary or list for this key
                                if i < len(indices) - 2:
                                    current[index] = {} if isinstance(indices[i+1], (str, bool, float)) else []
                                else:
                                    current[index] = []
                                current = current[index]
                        else:
                            raise InvalidOperationError(f"Cannot access index {index} of {type(current)} at dimension {i+1}")
                    
                    # Assign to the last dimension
                    last_index = indices[-1]
                    if isinstance(current, list):
                        if isinstance(last_index, int):
                            if 0 <= last_index < len(current):
                                current[last_index] = value
                            else:
                                # Auto-expand the list if needed (up to a reasonable limit)
                                if last_index < 1000:  # Arbitrary limit to prevent huge allocations
                                    while len(current) <= last_index:
                                        current.append(None)
                                    current[last_index] = value
                                else:
                                    raise InvalidOperationError(f"Index {last_index} too large for automatic array expansion (limit: 1000)")
                        else:
                            raise InvalidOperationError(f"Array index must be an integer, got {type(last_index)}")
                    elif isinstance(current, dict):
                        current[last_index] = value
                    else:
                        raise InvalidOperationError(f"Cannot assign to index {last_index} of {type(current)}")
                    
                    # Push the assigned value onto the stack
                    self.current_frame.stack.append(value)
                
                elif opcode == PRINT:
                    value = self.current_frame.stack.pop()
                    print(value)
                
                elif opcode == POP:
                    self.current_frame.stack.pop()
                
                elif opcode == DUP:
                    value = self.current_frame.stack[-1]
                    self.current_frame.stack.append(value)
                
                elif opcode == HALT:
                    self.running = False
                    # Return the top value on the stack (if any)
                    if self.current_frame.stack:
                        return self.current_frame.stack[-1]
                    # If in the global frame and no stack value, return all global variables
                    if self.current_frame == self.global_frame:
                        return self.global_frame.locals
                    return last_value
                
                else:
                    raise InvalidOperationError(f"Unknown opcode: {opcode}")
                
                # Update last_value after each instruction that modifies the stack
                if self.current_frame.stack:
                    last_value = self.current_frame.stack[-1]
                
            except UndefinedVariableError as e:
                print(f"Runtime Error: {e}")
                self.running = False
                return None
            except Exception as e:
                if isinstance(e, ReturnException):
                    raise e
                print(f"Runtime Error: {e}")
                self.running = False
                return None
        
        # Return the top value on the stack (if any)
        if self.current_frame.stack:
            return self.current_frame.stack[-1]
        # If in the global frame and no stack value, return all global variables
        if self.current_frame == self.global_frame:
            return self.global_frame.locals.copy()
        return None
    
    def run_program(self, instructions, constants):
        """Run a complete program from the beginning"""
        # Reset the VM state
        self.global_frame = Frame()
        self.current_frame = self.global_frame
        self.functions = {}
        self.running = True
        
        # Execute the program
        result = self.execute(instructions, constants)
        
        # Return the result
        return result

# Example usage
def run_example():
    # This is a simple example of how to use the VM
    from .compiler import BytecodeCompiler
    from AST.ast_1 import Integer, BinOp, Token
    
    # Create a simple AST: 2 + 3
    ast = BinOp(
        Integer(2),
        Token('PLUS', '+', 0, 0),
        Integer(3)
    )
    
    # Compile the AST to bytecode
    compiler = BytecodeCompiler()
    instructions, constants = compiler.compile(ast)
    
    # Run the bytecode in the VM
    vm = BytecodeVM(debug=True)
    result = vm.run_program(instructions, constants)
    
    print(f"Result: {result}")

if __name__ == "__main__":
    run_example()