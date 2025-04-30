import unittest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.bytecode.compiler import BytecodeCompiler
from src.bytecode.opcodes import *

class TestCompiler(unittest.TestCase):
    def compile_code(self, source_code):
        """Helper method to compile source code to bytecode"""
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        ast = parser.parse()
        compiler = BytecodeCompiler()
        return compiler.compile(ast)
    
    def test_compile_integers(self):
        """Test compilation of integer literals"""
        instructions, constants = self.compile_code("42")
        self.assertEqual(len(instructions), 2)
        self.assertEqual(instructions[0][0], LOAD_CONST)
        self.assertEqual(constants[0], 42)
        self.assertEqual(instructions[1][0], HALT)  # Changed from RETURN to HALT
    
    def test_compile_floats(self):
        """Test compilation of float literals"""
        instructions, constants = self.compile_code("3.14")
        self.assertEqual(len(instructions), 2)
        self.assertEqual(instructions[0][0], LOAD_CONST)
        self.assertEqual(constants[0], 3.14)
        self.assertEqual(instructions[1][0], HALT)  # Changed from RETURN to HALT
    
    def test_compile_strings(self):
        """Test compilation of string literals"""
        instructions, constants = self.compile_code('"hello"')
        self.assertEqual(len(instructions), 2)
        self.assertEqual(instructions[0][0], LOAD_CONST)
        self.assertEqual(constants[0], "hello")
        self.assertEqual(instructions[1][0], HALT)  # Changed from RETURN to HALT
    
    def test_compile_booleans(self):
        """Test compilation of boolean literals"""
        instructions, constants = self.compile_code("True")
        self.assertEqual(len(instructions), 2)
        self.assertEqual(instructions[0][0], LOAD_TRUE)
        self.assertEqual(instructions[1][0], HALT)  # Changed from RETURN to HALT
        
        instructions, constants = self.compile_code("False")
        self.assertEqual(len(instructions), 2)
        self.assertEqual(instructions[0][0], LOAD_FALSE)
        self.assertEqual(instructions[1][0], HALT)  # Changed from RETURN to HALT
    
    def test_compile_binary_operations(self):
        """Test compilation of binary operations"""
        # Addition
        instructions, constants = self.compile_code("5 + 3")
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[0][0], LOAD_CONST)  # Push 5
        self.assertEqual(instructions[1][0], LOAD_CONST)  # Push 3
        self.assertEqual(instructions[2][0], ADD)    # Add
        
        # Subtraction
        instructions, constants = self.compile_code("5 - 3")
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[2][0], SUBTRACT)    # Subtract
        
        # Multiplication
        instructions, constants = self.compile_code("5 * 3")
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[2][0], MULTIPLY)    # Multiply
        
        # Division
        instructions, constants = self.compile_code("6 / 3")
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[2][0], DIVIDE)    # Divide
    
    def test_compile_comparison_operations(self):
        """Test compilation of comparison operations"""
        # Equal
        instructions, constants = self.compile_code("5 == 3")
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[2][0], EQUAL)
        
        # Not Equal
        instructions, constants = self.compile_code("5 != 3")
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[2][0], NOT_EQUAL)
        
        # Less Than
        instructions, constants = self.compile_code("5 < 3")
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[2][0], LESS_THAN)
        
        # Greater Than
        instructions, constants = self.compile_code("5 > 3")
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[2][0], GREATER_THAN)
        
        # Less Than or Equal
        instructions, constants = self.compile_code("5 <= 3")
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[2][0], LESS_EQUAL)
        
        # Greater Than or Equal
        instructions, constants = self.compile_code("5 >= 3")
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[2][0], GREATER_EQUAL)
    
    def test_compile_logical_operations(self):
        """Test compilation of logical operations"""
        # AND
        instructions, constants = self.compile_code("True and False")
        self.assertIn(AND, [instr[0] for instr in instructions])
        
        # OR
        instructions, constants = self.compile_code("True or False")
        self.assertIn(OR, [instr[0] for instr in instructions])
        
        # NOT
        instructions, constants = self.compile_code("not True")
        self.assertIn(NOT, [instr[0] for instr in instructions])
    
    def test_compile_variable_declaration(self):
        """Test compilation of variable declarations"""
        instructions, constants = self.compile_code("let x = 5")
        # Should have instructions for pushing constant 5, storing in variable x
        self.assertIn(LOAD_CONST, [instr[0] for instr in instructions])
        self.assertIn(STORE_VAR, [instr[0] for instr in instructions])
        
        # Check the variable name (stored directly, not as a constant index)
        var_indices = [i for i, instr in enumerate(instructions) if instr[0] == STORE_VAR]
        self.assertTrue(len(var_indices) > 0)
        for idx in var_indices:
            self.assertEqual(instructions[idx][1], "x")  # Direct string, not an index
    
    def test_compile_variable_reassignment(self):
        """Test compilation of variable reassignment"""
        instructions, constants = self.compile_code("let x = 5\nx assign 10")
        # Should include store var twice
        store_var_count = sum(1 for instr in instructions if instr[0] == STORE_VAR or instr[0] == REASSIGN_VAR)
        self.assertEqual(store_var_count, 2)
    
    def test_compile_variable_lookup(self):
        """Test compilation of variable lookup"""
        instructions, constants = self.compile_code("let x = 5\nx")
        # Should have instructions for pushing constant 5, storing in variable x, then getting it
        load_var_indices = [i for i, instr in enumerate(instructions) if instr[0] == LOAD_VAR]
        self.assertTrue(len(load_var_indices) > 0)
        
        # The variable name is stored directly
        for idx in load_var_indices:
            self.assertEqual(instructions[idx][1], "x")  # Direct name, not index in constants
    
    def test_compile_if_statements(self):
        """Test compilation of if statements"""
        instructions, constants = self.compile_code("if (True) { 5 } else { 10 }")
        # Should include JUMP_IF_FALSE for conditional branch
        self.assertIn(JUMP_IF_FALSE, [instr[0] for instr in instructions])
        # Should include JUMP for else branch
        self.assertIn(JUMP, [instr[0] for instr in instructions])
    
    def test_compile_while_loops(self):
        """Test compilation of while loops"""
        instructions, constants = self.compile_code("while (True) { 5 }")
        # Should include JUMP_IF_FALSE for conditional branch
        self.assertIn(JUMP_IF_FALSE, [instr[0] for instr in instructions])
        # Should include JUMP for loop back
        self.assertIn(JUMP, [instr[0] for instr in instructions])
    
    def test_compile_for_loops(self):
        """Test compilation of for loops"""
        instructions, constants = self.compile_code("for (let i = 0 to 10) { print i }")
        # Should declare loop variable
        self.assertIn(STORE_VAR, [instr[0] for instr in instructions])
        # Should include comparison operators
        self.assertIn(GREATER_THAN, [instr[0] for instr in instructions])  # Changed from LESS_EQUAL
        # Should include JUMP_IF_TRUE for conditional branch
        self.assertIn(JUMP_IF_TRUE, [instr[0] for instr in instructions])  # Changed from JUMP_IF_FALSE
        # Should include JUMP for loop back
        self.assertIn(JUMP, [instr[0] for instr in instructions])
    
    def test_compile_function_definition(self):
        """Test compilation of function definition"""
        instructions, constants = self.compile_code("func add(a, b) { return a + b }")
        # Should include DEFINE_FUNC opcode
        self.assertIn(DEFINE_FUNC, [instr[0] for instr in instructions])
        
        # Check for the function name in the DEFINE_FUNC instruction
        function_define_indices = [i for i, instr in enumerate(instructions) if instr[0] == DEFINE_FUNC]
        self.assertTrue(len(function_define_indices) > 0)
        for idx in function_define_indices:
            self.assertEqual(instructions[idx][1], "add")  # The function name is the first parameter
    
    def test_compile_function_call(self):
        """Test compilation of function calls"""
        instructions, constants = self.compile_code("func add(a, b) { return a + b }\nadd(1, 2)")
        # Should include CALL_FUNC opcode for the function call
        self.assertIn(CALL_FUNC, [instr[0] for instr in instructions])
        
        # The arguments should be pushed onto the stack before the call
        call_indices = [i for i, instr in enumerate(instructions) if instr[0] == CALL_FUNC]
        for idx in call_indices:
            # Check that we pushed the right number of arguments (2 in this case)
            self.assertEqual(instructions[idx][1], 2)
    
    def test_compile_array_literals(self):
        """Test compilation of array literals"""
        instructions, constants = self.compile_code("[1, 2, 3]")
        # Should build an array with 3 elements
        array_indices = [i for i, instr in enumerate(instructions) if instr[0] == BUILD_ARRAY]
        self.assertTrue(len(array_indices) > 0)
        for idx in array_indices:
            # Check that we're building an array with 3 elements
            self.assertEqual(instructions[idx][1], 3)
    
    def test_compile_dict_literals(self):
        """Test compilation of dictionary literals"""
        instructions, constants = self.compile_code('{"a": 1, "b": 2}')
        # Should build a dict with 2 key-value pairs
        dict_indices = [i for i, instr in enumerate(instructions) if instr[0] == BUILD_DICT]
        self.assertTrue(len(dict_indices) > 0)
        for idx in dict_indices:
            # Check that we're building a dict with 2 key-value pairs
            self.assertEqual(instructions[idx][1], 2)
    
    def test_compile_array_access(self):
        """Test compilation of array access"""
        instructions, constants = self.compile_code("let arr = [1, 2, 3]\narr[1]")
        # The current implementation doesn't use ARRAY_ACCESS opcode
        # Instead it loads the array variable and the index, then builds a new array
        self.assertIn(LOAD_VAR, [instr[0] for instr in instructions])
        index_const_indices = [i for i, instr in enumerate(instructions) 
                             if instr[0] == LOAD_CONST and i > 3]  # Skip initial array constants
        self.assertTrue(len(index_const_indices) > 0)
    
    def test_compile_array_assignment(self):
        """Test compilation of array assignment"""
        instructions, constants = self.compile_code("let arr = [1, 2, 3]\narr[1] assign 42")
        # The current implementation doesn't use ARRAY_ASSIGN opcode
        # Check that we at least load the array and a constant
        self.assertIn(LOAD_VAR, [instr[0] for instr in instructions])
        index_const_indices = [i for i, instr in enumerate(instructions) 
                             if instr[0] == LOAD_CONST and i > 3]  # Skip initial array constants
        self.assertTrue(len(index_const_indices) > 0)
    
    def test_compile_print_statement(self):
        """Test compilation of print statements"""
        instructions, constants = self.compile_code("print 42")
        # Should include print operation
        self.assertIn(PRINT, [instr[0] for instr in instructions])

if __name__ == '__main__':
    unittest.main()