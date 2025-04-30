import unittest
import sys
import os
import io
from unittest.mock import patch

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.bytecode.compiler import BytecodeCompiler
from src.bytecode.vm import BytecodeVM

class TestEndToEnd(unittest.TestCase):
    """
    End-to-end tests for the entire compiler pipeline:
    Source Code -> Lexer -> Parser -> Compiler -> VM -> Result
    """
    
    def run_code(self, source_code, debug=False):
        """Helper method to run source code through the entire pipeline"""
        # Create lexer
        lexer = Lexer(source_code)
        
        # Parse the code
        parser = Parser(lexer)
        ast = parser.parse()
        
        # Compile to bytecode
        compiler = BytecodeCompiler()
        instructions, constants = compiler.compile(ast)
        
        if debug:
            print("Instructions:", instructions)
            print("Constants:", constants)
        
        # Execute the bytecode
        vm = BytecodeVM(debug=debug)
        result = vm.run_program(instructions, constants)
        
        return result
    
    def test_arithmetic(self):
        """Test arithmetic operations end-to-end"""
        self.assertEqual(self.run_code("5 + 3"), 8)
        self.assertEqual(self.run_code("5 - 3"), 2)
        self.assertEqual(self.run_code("5 * 3"), 15)
        self.assertEqual(self.run_code("6 / 3"), 2)
        self.assertEqual(self.run_code("2 ** 3"), 8)  # Exponentiation
        self.assertEqual(self.run_code("7 % 3"), 1)   # Modulo
        
        # Complex expression
        self.assertEqual(self.run_code("5 + 3 * 2"), 11)
        self.assertEqual(self.run_code("(5 + 3) * 2"), 16)
    
    def test_comparisons(self):
        """Test comparison operations end-to-end"""
        self.assertEqual(self.run_code("5 == 5"), True)
        self.assertEqual(self.run_code("5 != 3"), True)
        self.assertEqual(self.run_code("5 < 10"), True)
        self.assertEqual(self.run_code("5 > 3"), True)
        self.assertEqual(self.run_code("5 <= 5"), True)
        self.assertEqual(self.run_code("5 >= 3"), True)
        
        # Combinations
        self.assertEqual(self.run_code("5 > 3 and 10 < 20"), True)
        self.assertEqual(self.run_code("5 > 30 or 10 < 20"), True)
    
    def test_variables(self):
        """Test variable declarations and assignments end-to-end"""
        # Variable declaration
        self.assertEqual(self.run_code("let x = 5\nx"), 5)
        
        # Variable reassignment
        self.assertEqual(self.run_code("let x = 5\nx assign 10\nx"), 10)
        
        # Multiple variables
        result = self.run_code("""let x = 5
let y = 10
x + y""")
        print(f"Result of x + y: {result}")
        self.assertEqual(result, 15)
    
    def test_conditionals(self):
        """Test conditional statements end-to-end"""
        # Basic if statement
        self.assertEqual(self.run_code("if (True) { 42 } else { 100 }"), 42)
        self.assertEqual(self.run_code("if (False) { 42 } else { 100 }"), 100)
        
        # If statement with condition
        self.assertEqual(self.run_code("if (5 > 3) { 42 } else { 100 }"), 42)
        
        # If statement with variable
        code = """
        let x = 5
        if (x > 3) {
            42
        } else {
            100
        }
        """
        self.assertEqual(self.run_code(code), 42)
    
    def test_loops(self):
        """Test loop statements end-to-end"""
        # While loop
        code = """
        let i = 0
        let sum = 0
        while (i < 5) {
            sum assign sum + i
            i assign i + 1
        }
        sum
        """
        self.assertEqual(self.run_code(code), 10)  # 0 + 1 + 2 + 3 + 4 = 10
        
        # For loop
        code = """
        let sum = 0
        for (let i = 1 to 5) {
            sum assign sum + i
        }
        sum
        """
        # Manually calculating: 1 + 2 + 3 + 4 + 5 = 15
        self.assertEqual(self.run_code(code), 15)  
        
        # For loop with step
        code = """
        let sum = 0
        for (let i = 0 to 10 step 2) {
            sum assign sum + i
        }
        sum
        """
        # Manually calculating: 0 + 2 + 4 + 6 + 8 + 10 = 30
        self.assertEqual(self.run_code(code), 30)
    
    def test_functions(self):
        """Test function definitions and calls end-to-end"""
        # Simple function
        code = """
        func add(a, b) {
            return a + b
        }
        add(5, 3)
        """
        self.assertEqual(self.run_code(code), 8)
        
        # Function with conditional
        code = """
        func max(a, b) {
            if (a > b) {
                return a
            } else {
                return b
            }
        }
        max(5, 10)
        """
        self.assertEqual(self.run_code(code), 10)
        
        # Recursive function (factorial)
        code = """
        func factorial(n) {
            if (n <= 1) {
                return 1
            } else {
                return n * factorial(n - 1)
            }
        }
        factorial(5)
        """
        self.assertEqual(self.run_code(code), 120)  # 5! = 120
    
    def test_closures(self):
        """Test closures and nested functions end-to-end"""
        code = """
        // Simple counter implementation using closures
        func makeCounter() {
            let count = 0
            
            func increment() {
                count assign count + 1  // Must use 'assign' to update the variable
                return count
            }
            
            return increment
        }
        
        let counter = makeCounter()
        counter()  // Returns 1
        counter()  // Returns 2
        counter()  // Returns 3
        """
        result = self.run_code(code)
        print(f"Result of closures test: {result}")
        self.assertEqual(result, 3)
    
    def test_arrays(self):
        """Test array operations end-to-end"""
        # Array creation
        self.assertEqual(self.run_code("[1, 2, 3]")[1], 2)
        
        # Array indexing
        code = """
        let arr = [10, 20, 30]
        arr[1]
        """
        self.assertEqual(self.run_code(code), 20)
        
        # Array assignment
        code = """
        let arr = [10, 20, 30]
        arr[1] assign 42
        arr[1]
        """
        self.assertEqual(self.run_code(code), 42)
        
        # Array sum calculation
        code = """
        let arr = [1, 2, 3]
        arr[0] + arr[1] + arr[2]
        """
        self.assertEqual(self.run_code(code), 6)  # 1 + 2 + 3 = 6
    
    def test_dictionaries(self):
        """Test dictionary operations end-to-end"""
        # Dictionary creation
        code = """
        let dict = {"a": 10, "b": 20}
        dict["b"]
        """
        self.assertEqual(self.run_code(code), 20)
        
        # Dictionary assignment
        code = """
        let dict = {"a": 10, "b": 20}
        dict["b"] assign 42
        dict["b"]
        """
        self.assertEqual(self.run_code(code), 42)
        
        # Dictionary with expressions
        code = """
        let a = "key"
        let dict = {a: 10, "b": 20}
        dict[a]
        """
        self.assertEqual(self.run_code(code), 10)
    
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_statement(self, mock_stdout):
        """Test print statement end-to-end"""
        code = """
        print "Hello, World!"
        42  // Return value
        """
        result = self.run_code(code)
        
        # Check return value
        self.assertEqual(result, 42)
        
        # Check printed output
        self.assertEqual(mock_stdout.getvalue().strip(), "Hello, World!")
    
    def test_complex_program(self):
        """Test a more complex program that uses multiple language features"""
        code = """
        // Define a function to calculate fibonacci numbers
func fibonacci(n) {
    if (n <= 1) {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

// Calculate fibonacci(10)
let fib10 = fibonacci(10)

// Create a simple array
let list = [0, 1, 1, 2, 3, 5, 8]

// Calculate the sum manually
let sum = list[0] + list[1] + list[2] + list[3] + list[4] + list[5] + list[6]

// Return the results
{
    "fib10": fib10,
    "list": list,
    "sum": sum
}        """
        result = self.run_code(code)
        print(f"Result of complex program: {result}")
        
        # Check the result
        self.assertEqual(result["fib10"], 55)  # fibonacci(10) = 55
        self.assertEqual(len(result["list"]), 7)  # List of 7 fibonacci numbers
        self.assertEqual(result["sum"], 20)  # Sum of first 7 fibonacci numbers: 0+1+1+2+3+5+8 = 20

if __name__ == '__main__':
    unittest.main()