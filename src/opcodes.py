"""
Bytecode Operation Codes (Opcodes) for the FluxScript Virtual Machine

This module defines the operation codes (opcodes) that the FluxScript 
virtual machine understands. Each opcode corresponds to a specific 
operation that can be performed by the VM.
"""

# Constants and Literals
LOAD_CONST = 1   # Load a constant onto the stack
LOAD_TRUE = 2    # Load boolean True onto the stack
LOAD_FALSE = 3   # Load boolean False onto the stack

# Variables
LOAD_VAR = 10    # Load a variable value onto the stack
STORE_VAR = 11   # Store top of stack in a variable
REASSIGN_VAR = 12 # Reassign a value to an existing variable

# Arithmetic Operations
ADD = 20         # Add top two values on stack
SUBTRACT = 21    # Subtract top value from second top value
MULTIPLY = 22    # Multiply top two values on stack
DIVIDE = 23      # Divide second top value by top value
EXPONENT = 24    # Raise second top value to power of top value
MODULO = 25      # Modulo operation (remainder)
NEGATE = 26      # Negate top value on stack

# Comparison Operations
EQUAL = 30       # Check if top two values are equal
NOT_EQUAL = 31   # Check if top two values are not equal
LESS_THAN = 32   # Check if second top value is less than top value
GREATER_THAN = 33 # Check if second top value is greater than top value
LESS_EQUAL = 34  # Check if second top value is less than or equal to top value
GREATER_EQUAL = 35 # Check if second top value is greater than or equal to top value

# Logical Operations
AND = 40         # Logical AND of top two values
OR = 41          # Logical OR of top two values
NOT = 42         # Logical NOT of top value

# Control Flow
JUMP = 50        # Unconditional jump to instruction
JUMP_IF_FALSE = 51 # Jump to instruction if top of stack is false
JUMP_IF_TRUE = 52  # Jump to instruction if top of stack is true

# Loop control opcodes
LOOP_START = 53
LOOP_END = 54
BREAK = 55
CONTINUE = 56
FOR_SETUP = 57
FOR_ITER = 58
FOR_ITER_END = 59

# Functions
DEFINE_FUNC = 60    # Define a function
LOAD_LAMBDA = 63    # Load an anonymous function (lambda)
CALL_FUNC = 61      # Call a function
DICT_FUNC_CALL = 64 # Call a function stored in a dictionary
RETURN = 62         # Return from function call

# Data Structures
BUILD_ARRAY = 70  # Build array from n items on stack
BUILD_DICT = 71   # Build dictionary from n key-value pairs on stack
ARRAY_ACCESS = 72 # Access an element in an array or dict
ARRAY_ASSIGN = 73 # Assign a value to an array or dict element
GET_SIZE = 74     # Get the size of a string, array, or dictionary
MULTI_DIM_ACCESS = 75  # Access a multi-dimensional array element 
MULTI_DIM_ASSIGN = 76  # Assign a value to a multi-dimensional array element

# I/O Operations
PRINT = 80        # Print top of stack

# Miscellaneous
POP = 90          # Pop top value from stack and discard it
DUP = 91          # Duplicate top value on stack

# End of program
HALT = 99         # Halt execution

# Map of opcode values to their names for easier debugging
OPCODE_NAMES = {
    LOAD_CONST: "LOAD_CONST",
    LOAD_TRUE: "LOAD_TRUE",
    LOAD_FALSE: "LOAD_FALSE",
    LOAD_VAR: "LOAD_VAR",
    STORE_VAR: "STORE_VAR",
    REASSIGN_VAR: "REASSIGN_VAR",
    ADD: "ADD",
    SUBTRACT: "SUBTRACT",
    MULTIPLY: "MULTIPLY",
    DIVIDE: "DIVIDE",
    EXPONENT: "EXPONENT",
    MODULO: "MODULO",
    NEGATE: "NEGATE",
    EQUAL: "EQUAL",
    NOT_EQUAL: "NOT_EQUAL",
    LESS_THAN: "LESS_THAN",
    GREATER_THAN: "GREATER_THAN",
    LESS_EQUAL: "LESS_EQUAL",
    GREATER_EQUAL: "GREATER_EQUAL",
    AND: "AND",
    OR: "OR",
    NOT: "NOT",
    JUMP: "JUMP",
    JUMP_IF_FALSE: "JUMP_IF_FALSE",
    JUMP_IF_TRUE: "JUMP_IF_TRUE",
    LOOP_START: 'LOOP_START',
    LOOP_END: 'LOOP_END',
    BREAK: 'BREAK',
    CONTINUE: 'CONTINUE',
    FOR_SETUP: 'FOR_SETUP',
    FOR_ITER: 'FOR_ITER',
    FOR_ITER_END: 'FOR_ITER_END',
    DEFINE_FUNC: "DEFINE_FUNC",
    LOAD_LAMBDA: "LOAD_LAMBDA",
    CALL_FUNC: "CALL_FUNC",
    DICT_FUNC_CALL: "DICT_FUNC_CALL",
    RETURN: "RETURN",
    BUILD_ARRAY: "BUILD_ARRAY",
    BUILD_DICT: "BUILD_DICT",
    ARRAY_ACCESS: "ARRAY_ACCESS",
    ARRAY_ASSIGN: "ARRAY_ASSIGN",
    GET_SIZE: "GET_SIZE",
    MULTI_DIM_ACCESS: "MULTI_DIM_ACCESS",
    MULTI_DIM_ASSIGN: "MULTI_DIM_ASSIGN",
    PRINT: "PRINT",
    POP: "POP",
    DUP: "DUP",
    HALT: "HALT"
}