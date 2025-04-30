import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bytecode.compiler import BytecodeCompiler
from src.bytecode.vm import BytecodeVM
from src.bytecode.opcodes import OPCODE_NAMES
from src.lexer.lexer import Lexer
from src.parser.parser import Parser

def run_code(source_code, debug=False):
    """
    Run the provided source code using the language pipeline:
    1. Lexer -> Tokenize the source
    2. Parser -> Parse tokens into AST
    3. Compiler -> Compile AST to bytecode
    4. VM -> Execute bytecode
    """
    print("==== SOURCE CODE ====")
    print(source_code)
    print("====================")
    
    # Create lexer
    lexer = Lexer(source_code)
    
    # Parse the code
    parser = Parser(lexer)
    ast = parser.parse()
    if debug:
        print("==== AST ====")
        print(ast)
        print("=============")
    
    # Compile to bytecode
    compiler = BytecodeCompiler()
    instructions, constants = compiler.compile(ast)
    
    if debug:
        print("==== BYTECODE ====")
        for i, instr in enumerate(instructions):
            opcode = instr[0]
            args = instr[1:] if len(instr) > 1 else []
            print(f"{i}: {OPCODE_NAMES.get(opcode, opcode)} {args}")
        print("==== CONSTANTS ====")
        for i, const in enumerate(constants):
            print(f"{i}: {const}")
        print("==================")
    
    # Execute the bytecode
    vm = BytecodeVM(debug=debug)
    result = vm.run_program(instructions, constants)
    
    print("==== RESULT ====")
    print(result)
    print("================")
    
    return result

# Example programs to demonstrate language features
example_programs = {
    "arithmetic": """
    // Basic arithmetic operations
    let x = 10
    let y = 5
    let z = x + y * 2
    print z
    """,
    
    "conditionals": """
    // Conditional statements
    let x = 10
    if (x > 5) {
        print "x is greater than 5"
    } else {
        print "x is not greater than 5"
    }
    """,
    
    "loops": """
    // Loop example
    let sum = 0
    for (let i = 1 to 10) {
        // In this language, we need to use 'assign' for reassignment
        sum assign sum + i
    }
    print "Sum of numbers from 1 to 10 is:"
    print sum
    """,
    
    "variables": """
    // Variables and reassignment with 'assign'
    let counter = 0
    
    // Use 'assign' for changing existing variables
    counter assign counter + 1
    print "Counter after first increment:"
    print counter
    
    counter assign counter + 1
    print "Counter after second increment:"
    print counter
    """,
    
    "data_structures": """
    // Data structure examples
    
    // Arrays
    let arr = [1, 2, 3, 4, 5]
    print "Array example:"
    print arr
    
    // Dictionaries
    let dict = {"name": "John", "age": 30}
    print "Dictionary example:"
    print dict
    """,
    
    "expressions": """
    // Complex expressions
    let a = 5
    let b = 3
    let c = 2
    
    // Arithmetic with precedence
    let result1 = a + b * c
    print "5 + 3 * 2 ="
    print result1
    
    // Logical operators
    let hasPermission = True
    let isAdmin = False
    let canAccess = hasPermission and isAdmin
    
    print "Permission granted?"
    print canAccess
    """,
    
    "simple_closure": """
    // Simple closure example with explicit naming of anonymous function
    func makeCounter() {
        let count = 0
        
        // Define the inner function explicitly first
        func incrementer() {
            count assign count + 1
            return count
        }
        
        // Return the inner function
        return incrementer
    }
    
    let counter = makeCounter()
    print "First call:"
    print counter()
    
    print "Second call:"
    print counter()
    
    print "Third call:"
    print counter()
    """,
    
    "advanced_closure": """
    // Advanced closure example with named inner functions
    func makePowerFunction(exponent) {
        // Use named function instead of anonymous
        func powerFunc(base) {
            // Capture the 'exponent' parameter
            return base ** exponent
        }
        
        // Return the named function
        return powerFunc
    }
    
    let square = makePowerFunction(2)
    let cube = makePowerFunction(3)
    
    print "Square of 4:"
    print square(4)
    
    print "Cube of 3:"
    print cube(3)
    
    // Test both functions multiple times to ensure environment is properly captured
    print "Square of 5:"
    print square(5)
    
    print "Cube of 2:"
    print cube(2)
    """,
    
    "nested_functions": """
    // Nested function definitions with multiple levels of variable capture
    func outerFunction(x) {
        let y = x * 2
        
        func middleFunction(z) {
            // This function can access both x and y from parent scopes
            let w = x + y + z
            
            func innerFunction() {
                // This function can access all variables from all parent scopes
                return x + y + z + w
            }
            
            return innerFunction
        }
        
        return middleFunction
    }
    
    let middleFn = outerFunction(5)    // x=5, y=10
    let innerFn = middleFn(3)          // z=3, w=18
    
    print "Result of innerFunction (should be 5+10+3+18=36):"
    print innerFn()
    
    // Create another instance to ensure closures work properly
    let anotherMiddleFn = outerFunction(2)   // x=2, y=4
    let anotherInnerFn = anotherMiddleFn(1)  // z=1, w=7
    
    print "Result of another innerFunction (should be 2+4+1+7=14):"
    print anotherInnerFn()
    """,
    
    # "closure_with_multiple_vars": """
    # // Test closure with multiple captured variables
    # func makeAdder(x) {
    #     return func(y) {
    #         return x + y
    #     }
    # }
    
    # func makeMultiplier(factor) {
    #     return func(value) {
    #         return factor * value
    #     }
    # }
    
    # func createCalculator(initialValue) {
    #     let current = initialValue
        
    #     return {
    #         "add": func(x) {
    #             current assign current + x
    #             return current
    #         },
    #         "subtract": func(x) {
    #             current assign current - x
    #             return current
    #         },
    #         "multiply": func(x) {
    #             current assign current * x
    #             return current
    #         },
    #         "getValue": func() {
    #             return current
    #         }
    #     }
    # }
    
    # // Test the calculator
    # let calc = createCalculator(10)
    # print "Initial value: 10"
    
    # print "After adding 5:"
    # print calc["add"](5)
    
    # print "After multiplying by 2:"
    # print calc["multiply"](2)
    
    # print "After subtracting 7:"
    # print calc["subtract"](7)
    
    # print "Final value:"
    # print calc["getValue"]()
    # """,
    
    # "recursive_closure": """
    # // Test recursive function with closure
    # func createFactorial() {
    #     // Define a factorial function that can reference itself
    #     let factorial = func(n) {
    #         if (n <= 1) {
    #             return 1
    #         }
    #         return n * factorial(n - 1)
    #     }
        
    #     return factorial
    # }
    
    # let factorial = createFactorial()
    
    # print "Factorial of 5:"
    # print factorial(5)
    
    # print "Factorial of 10:"
    # print factorial(10)
    # """,
    
    # "closure_shared_env": """
    # // Test multiple closures sharing the same environment with named functions
    # func createCounter() {
    #     let count = 0
        
    #     // Define each function with a name first
    #     func incrementFn() {
    #         count assign count + 1
    #         return count
    #     }
        
    #     func decrementFn() {
    #         count assign count - 1
    #         return count
    #     }
        
    #     func resetFn() {
    #         count assign 0
    #         return count
    #     }
        
    #     func getCountFn() {
    #         return count
    #     }
        
    #     // Return a dictionary of named functions
    #     return {
    #         "increment": incrementFn,
    #         "decrement": decrementFn,
    #         "reset": resetFn,
    #         "getCount": getCountFn
    #     }
    # }
    
    # let counter = createCounter()
    
    # print "Initial count:"
    # print counter["getCount"]()
    
    # print "After incrementing:"
    # counter["increment"]()
    # counter["increment"]()
    # print counter["getCount"]()
    
    # print "After decrementing:"
    # counter["decrement"]()
    # print counter["getCount"]()
    
    # print "After reset:"
    # counter["reset"]()
    # print counter["getCount"]()
    # """
}

def main():
    if len(sys.argv) > 1:
        # Run a specific example if provided as argument
        example_name = sys.argv[1]
        debug_mode = "--debug" in sys.argv
        
        if example_name in example_programs:
            print(f"Running example: {example_name}")
            run_code(example_programs[example_name], debug=debug_mode)
        elif example_name == "all":
            # Run all examples
            for name, code in example_programs.items():
                print(f"\n\n===== RUNNING EXAMPLE: {name} =====")
                run_code(code, debug=debug_mode)
        else:
            # Assume it's a file path
            try:
                with open(example_name, 'r') as f:
                    source_code = f.read()
                run_code(source_code, debug=debug_mode)
            except FileNotFoundError:
                print(f"Example '{example_name}' not found and not a valid file path.")
                print("Available examples:")
                for name in example_programs.keys():
                    print(f"  - {name}")
    else:
        # Print usage information
        print("Usage: python run_examples.py [example_name | all | file_path] [--debug]")
        print("Available examples:")
        for name in example_programs.keys():
            print(f"  - {name}")

if __name__ == "__main__":
    main()