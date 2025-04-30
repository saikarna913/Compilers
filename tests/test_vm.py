import unittest
import sys
import os
import io
from unittest.mock import patch

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bytecode.vm import BytecodeVM
from src.bytecode.opcodes import *

class TestVM(unittest.TestCase):
    def setUp(self):
        """Set up a new VM instance for each test"""
        self.vm = BytecodeVM()
    
    def test_execute_constants(self):
        """Test execution of constant operations"""
        # Test integer constant
        instructions = [(LOAD_CONST, 0), (RETURN, 0)]
        constants = [42]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 42)
        
        # Test float constant
        instructions = [(LOAD_CONST, 0), (RETURN, 0)]
        constants = [3.14]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 3.14)
        
        # Test string constant
        instructions = [(LOAD_CONST, 0), (RETURN, 0)]
        constants = ["hello"]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, "hello")
    
    def test_execute_boolean_constants(self):
        """Test execution of boolean constants"""
        # Test True
        instructions = [(LOAD_TRUE, 0), (RETURN, 0)]
        constants = []
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, True)
        
        # Test False
        instructions = [(LOAD_FALSE, 0), (RETURN, 0)]
        constants = []
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, False)
    
    def test_execute_binary_operations(self):
        """Test execution of binary operations"""
        # Addition
        instructions = [
            (LOAD_CONST, 0),  # Push 5
            (LOAD_CONST, 1),  # Push 3
            (ADD, 0),         # Add
            (RETURN, 0)       # Return
        ]
        constants = [5, 3]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 8)
        
        # Subtraction
        instructions = [
            (LOAD_CONST, 0),  # Push 5
            (LOAD_CONST, 1),  # Push 3
            (SUBTRACT, 0),    # Subtract
            (RETURN, 0)       # Return
        ]
        constants = [5, 3]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 2)
        
        # Multiplication
        instructions = [
            (LOAD_CONST, 0),  # Push 5
            (LOAD_CONST, 1),  # Push 3
            (MULTIPLY, 0),    # Multiply
            (RETURN, 0)       # Return
        ]
        constants = [5, 3]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 15)
        
        # Division
        instructions = [
            (LOAD_CONST, 0),  # Push 6
            (LOAD_CONST, 1),  # Push 3
            (DIVIDE, 0),      # Divide
            (RETURN, 0)       # Return
        ]
        constants = [6, 3]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 2)
    
    def test_execute_comparison_operations(self):
        """Test execution of comparison operations"""
        # Equal (true case)
        instructions = [
            (LOAD_CONST, 0),  # Push 5
            (LOAD_CONST, 0),  # Push 5
            (EQUAL, 0),       # Compare equals
            (RETURN, 0)       # Return
        ]
        constants = [5]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, True)
        
        # Equal (false case)
        instructions = [
            (LOAD_CONST, 0),  # Push 5
            (LOAD_CONST, 1),  # Push 3
            (EQUAL, 0),       # Compare equals
            (RETURN, 0)       # Return
        ]
        constants = [5, 3]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, False)
        
        # Not Equal
        instructions = [
            (LOAD_CONST, 0),  # Push 5
            (LOAD_CONST, 1),  # Push 3
            (NOT_EQUAL, 0),   # Compare not equals
            (RETURN, 0)       # Return
        ]
        constants = [5, 3]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, True)
        
        # Less Than
        instructions = [
            (LOAD_CONST, 0),  # Push 3
            (LOAD_CONST, 1),  # Push 5
            (LESS_THAN, 0),   # Compare less than
            (RETURN, 0)       # Return
        ]
        constants = [3, 5]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, True)
        
        # Greater Than
        instructions = [
            (LOAD_CONST, 0),  # Push 5
            (LOAD_CONST, 1),  # Push 3
            (GREATER_THAN, 0), # Compare greater than
            (RETURN, 0)       # Return
        ]
        constants = [5, 3]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, True)
    
    def test_execute_logical_operations(self):
        """Test execution of logical operations"""
        # AND (true case)
        instructions = [
            (LOAD_TRUE, 0),   # Push True
            (LOAD_TRUE, 0),   # Push True
            (AND, 0),         # Logical AND
            (RETURN, 0)       # Return
        ]
        constants = []
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, True)
        
        # AND (false case)
        instructions = [
            (LOAD_TRUE, 0),   # Push True
            (LOAD_FALSE, 0),  # Push False
            (AND, 0),         # Logical AND
            (RETURN, 0)       # Return
        ]
        constants = []
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, False)
        
        # OR (true case)
        instructions = [
            (LOAD_TRUE, 0),   # Push True
            (LOAD_FALSE, 0),  # Push False
            (OR, 0),          # Logical OR
            (RETURN, 0)       # Return
        ]
        constants = []
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, True)
        
        # OR (false case)
        instructions = [
            (LOAD_FALSE, 0),  # Push False
            (LOAD_FALSE, 0),  # Push False
            (OR, 0),          # Logical OR
            (RETURN, 0)       # Return
        ]
        constants = []
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, False)
        
        # NOT (true case)
        instructions = [
            (LOAD_TRUE, 0),   # Push True
            (NOT, 0),         # Logical NOT
            (RETURN, 0)       # Return
        ]
        constants = []
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, False)
        
        # NOT (false case)
        instructions = [
            (LOAD_FALSE, 0),  # Push False
            (NOT, 0),         # Logical NOT
            (RETURN, 0)       # Return
        ]
        constants = []
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, True)
    
    def test_execute_variables(self):
        """Test execution of variable operations"""
        # Set and get global variable
        instructions = [
            (LOAD_CONST, 0),       # Push 42
            (STORE_VAR, 1),        # Set global 'x' to 42
            (LOAD_VAR, 1),         # Get global 'x'
            (RETURN, 0)            # Return
        ]
        constants = [42, "x"]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 42)
        
        # Test variable reassignment
        instructions = [
            (LOAD_CONST, 0),       # Push 42
            (STORE_VAR, 1),        # Set global 'x' to 42
            (LOAD_CONST, 2),       # Push 100
            (STORE_VAR, 1),        # Set global 'x' to 100
            (LOAD_VAR, 1),         # Get global 'x'
            (RETURN, 0)            # Return
        ]
        constants = [42, "x", 100]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 100)
    
    def test_execute_conditionals(self):
        """Test execution of conditional operations (if/else)"""
        # If with true condition
        instructions = [
            (LOAD_TRUE, 0),           # Push True
            (JUMP_IF_FALSE, 4),       # Jump to else branch (instruction 4) if false
            (LOAD_CONST, 0),          # Push 42 (then branch)
            (JUMP, 5),                # Jump to return (instruction 5)
            (LOAD_CONST, 1),          # Push 100 (else branch)
            (RETURN, 0)               # Return
        ]
        constants = [42, 100]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 42)
        
        # If with false condition
        instructions = [
            (LOAD_FALSE, 0),          # Push False
            (JUMP_IF_FALSE, 4),       # Jump to else branch (instruction 4) if false
            (LOAD_CONST, 0),          # Push 42 (then branch)
            (JUMP, 5),                # Jump to return (instruction 5)
            (LOAD_CONST, 1),          # Push 100 (else branch)
            (RETURN, 0)               # Return
        ]
        constants = [42, 100]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 100)
    
    def test_execute_loops(self):
        """Test execution of loop operations"""
        # Simple while loop (sum 1 to 5)
        instructions = [
            # Initialize counter and sum
            (LOAD_CONST, 0),        # Push 1 (i = 1)
            (STORE_VAR, 1),         # Set global 'i' to 1
            (LOAD_CONST, 2),        # Push 0 (sum = 0)
            (STORE_VAR, 3),         # Set global 'sum' to 0
            
            # Loop condition (instruction 4): i <= 5
            (LOAD_VAR, 1),          # Get global 'i'
            (LOAD_CONST, 4),        # Push 5
            (LESS_EQUAL, 0),        # Compare i <= 5
            (JUMP_IF_FALSE, 17),    # Jump to instruction 17 (return) if false
            
            # Loop body: sum += i, i++
            (LOAD_VAR, 3),          # Get global 'sum'
            (LOAD_VAR, 1),          # Get global 'i'
            (ADD, 0),               # Add sum + i
            (STORE_VAR, 3),         # Set global 'sum' to sum + i
            
            (LOAD_VAR, 1),          # Get global 'i'
            (LOAD_CONST, 5),        # Push 1
            (ADD, 0),               # Add i + 1
            (STORE_VAR, 1),         # Set global 'i' to i + 1
            
            (JUMP, 4),              # Jump back to condition (instruction 4)
            
            # Return sum (instruction 17)
            (LOAD_VAR, 3),          # Get global 'sum'
            (RETURN, 0)             # Return
        ]
        constants = [1, "i", 0, "sum", 5, 1]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 15)  # 1 + 2 + 3 + 4 + 5 = 15
    
    def test_execute_functions(self):
        """Test execution of function operations"""
        # Simple function call: func add(a, b) { return a + b }
        # First we need to define a function object
        function_instructions = [
            (LOAD_VAR, "a"),    # Get parameter 'a'
            (LOAD_VAR, "b"),    # Get parameter 'b'
            (ADD, 0),           # Add a + b
            (RETURN, 0)         # Return
        ]
        
        # Now set up instructions to create and call the function
        instructions = [
            # Create function
            (LOAD_CONST, 0),           # Push function object
            (DEFINE_FUNC, "add", 0),   # Define function with name "add" from constants[0]
            
            # Call function with arguments 5 and 3
            (LOAD_VAR, "add"),         # Get function
            (LOAD_CONST, 1),           # Push 5
            (LOAD_CONST, 2),           # Push 3
            (CALL_FUNC, 2),            # Call with 2 arguments
            (RETURN, 0)                # Return
        ]
        
        # Create a function object (normally created by the compiler)
        function_obj = {
            'name': 'add',
            'params': ['a', 'b'],
            'code': function_instructions,
            'consts': []
        }
        
        constants = [function_obj, 5, 3]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 8)  # 5 + 3 = 8
    
    def test_execute_arrays(self):
        """Test execution of array operations"""
        # Create array and access element
        instructions = [
            # Create array [10, 20, 30]
            (LOAD_CONST, 0),          # Push 10
            (LOAD_CONST, 1),          # Push 20
            (LOAD_CONST, 2),          # Push 30
            (BUILD_ARRAY, 3),         # Build array with 3 elements
            (STORE_VAR, 3),           # Set global 'arr' to array
            
            # Access arr[1] (should be 20)
            (LOAD_VAR, 3),            # Get global 'arr'
            (LOAD_CONST, 4),          # Push index 1
            (ARRAY_ACCESS, 0),        # Get arr[1]
            (RETURN, 0)               # Return
        ]
        constants = [10, 20, 30, "arr", 1]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 20)
        
        # Test array assignment
        instructions = [
            # Create array [10, 20, 30]
            (LOAD_CONST, 0),          # Push 10
            (LOAD_CONST, 1),          # Push 20
            (LOAD_CONST, 2),          # Push 30
            (BUILD_ARRAY, 3),         # Build array with 3 elements
            (STORE_VAR, 3),           # Set global 'arr' to array
            
            # Set arr[1] = 42
            (LOAD_VAR, 3),            # Get global 'arr'
            (LOAD_CONST, 4),          # Push index 1
            (LOAD_CONST, 5),          # Push value 42
            (ARRAY_ASSIGN, 0),        # Set arr[1] = 42
            
            # Access arr[1] (should now be 42)
            (LOAD_VAR, 3),            # Get global 'arr'
            (LOAD_CONST, 4),          # Push index 1
            (ARRAY_ACCESS, 0),        # Get arr[1]
            (RETURN, 0)               # Return
        ]
        constants = [10, 20, 30, "arr", 1, 42]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 42)
    
    def test_execute_dictionaries(self):
        """Test execution of dictionary operations"""
        # Create dictionary and access key
        instructions = [
            # Create dict {"a": 10, "b": 20}
            (LOAD_CONST, 0),          # Push "a"
            (LOAD_CONST, 1),          # Push 10
            (LOAD_CONST, 2),          # Push "b"
            (LOAD_CONST, 3),          # Push 20
            (BUILD_DICT, 2),          # Build dict with 2 key-value pairs
            (STORE_VAR, 4),           # Set global 'dict' to dictionary
            
            # Access dict["b"] (should be 20)
            (LOAD_VAR, 4),            # Get global 'dict'
            (LOAD_CONST, 2),          # Push key "b"
            (ARRAY_ACCESS, 0),        # Get dict["b"]
            (RETURN, 0)               # Return
        ]
        constants = ["a", 10, "b", 20, "dict"]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 20)
        
        # Test dictionary assignment
        instructions = [
            # Create dict {"a": 10, "b": 20}
            (LOAD_CONST, 0),          # Push "a"
            (LOAD_CONST, 1),          # Push 10
            (LOAD_CONST, 2),          # Push "b"
            (LOAD_CONST, 3),          # Push 20
            (BUILD_DICT, 2),          # Build dict with 2 key-value pairs
            (STORE_VAR, 4),           # Set global 'dict' to dictionary
            
            # Set dict["b"] = 42
            (LOAD_VAR, 4),            # Get global 'dict'
            (LOAD_CONST, 2),          # Push key "b"
            (LOAD_CONST, 5),          # Push value 42
            (ARRAY_ASSIGN, 0),        # Set dict["b"] = 42
            
            # Access dict["b"] (should now be 42)
            (LOAD_VAR, 4),            # Get global 'dict'
            (LOAD_CONST, 2),          # Push key "b"
            (ARRAY_ACCESS, 0),        # Get dict["b"]
            (RETURN, 0)               # Return
        ]
        constants = ["a", 10, "b", 20, "dict", 42]
        result = self.vm.run_program(instructions, constants)
        self.assertEqual(result, 42)
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_operation(self, mock_stdout):
        """Test the print operation"""
        instructions = [
            (LOAD_CONST, 0),   # Push "Hello, World!"
            (PRINT, 0),        # Print it
            (LOAD_CONST, 1),   # Push 42 (as the result)
            (RETURN, 0)        # Return
        ]
        constants = ["Hello, World!", 42]
        result = self.vm.run_program(instructions, constants)
        
        # Check the result
        self.assertEqual(result, 42)
        
        # Check that the correct string was printed
        self.assertEqual(mock_stdout.getvalue().strip(), "Hello, World!")

if __name__ == '__main__':
    unittest.main()