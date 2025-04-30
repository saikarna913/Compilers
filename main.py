import sys
import os
import traceback

# Try to set up readline support
try:
    # Try pyreadline3 for Windows
    try:
        import pyreadline3
    except ImportError:
        # If pyreadline3 is not available, try the Unix readline
        import readline
except ImportError:
    # If neither is available, continue without readline support
    pass

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.bytecode.compiler import BytecodeCompiler
from src.bytecode.vm import BytecodeVM
from src.bytecode.opcodes import OPCODE_NAMES

def run_code(source_code, debug=False):
    """
    Run the provided source code using the language pipeline:
    1. Lexer -> Tokenize the source
    2. Parser -> Parse tokens into AST
    3. Compiler -> Compile AST to bytecode
    4. VM -> Execute bytecode
    
    Returns the execution result or None if an error occurred
    """
    try:
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
        
        if debug:
            print("==== RESULT ====")
            print(result)
            print("================")
        
        return result
    
    except Exception as e:
        print(f"Error: {str(e)}")
        if debug:
            traceback.print_exc()
        return None

def run_file(file_path, debug=False):
    """Run code from a file"""
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        print(f"==== Running file: {file_path} ====")
        result = run_code(source_code, debug=debug)
        if result is not None:
            print(f"==== Execution Result ====")
            print(result)
        return True
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False
    except Exception as e:
        print(f"Error running file: {e}")
        if debug:
            traceback.print_exc()
        return False

def run_repl(debug=False):
    """Run in REPL (Read-Eval-Print Loop) mode"""
    print("==== Language Interpreter REPL ====")
    print("Type code to execute, 'exit' or 'quit' to exit, or 'debug on/off' to toggle debugging")
    print("Multi-line input is supported. End with an empty line.")
    
    while True:
        try:
            # Collect input (multi-line supported)
            lines = []
            line = input(">>> ")
            
            # Check for exit command
            if line.lower() in ('exit', 'quit'):
                print("Exiting REPL...")
                break
            
            # Check for debug toggle
            if line.lower() == 'debug on':
                debug = True
                print("Debug mode enabled")
                continue
            elif line.lower() == 'debug off':
                debug = False
                print("Debug mode disabled")
                continue
            
            # Handle multi-line input
            while line:
                lines.append(line)
                line = input("... ")
            
            # Skip empty inputs
            if not lines:
                continue
            
            # Run the code
            source_code = '\n'.join(lines)
            result = run_code(source_code, debug=debug)
            
            # Display result if not None
            if result is not None:
                print(f"Result: {result}")
                
        except KeyboardInterrupt:
            print("\nOperation cancelled")
        except EOFError:
            print("\nExiting REPL...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            if debug:
                traceback.print_exc()

def main():
    """Main entry point for the interpreter"""
    debug_mode = "--debug" in sys.argv
    
    # Remove debug flag from arguments
    args = [arg for arg in sys.argv[1:] if arg != "--debug"]
    
    if len(args) > 0:
        # First argument is the file path
        file_path = args[0]
        run_file(file_path, debug=debug_mode)
    else:
        # No file specified, run in REPL mode
        run_repl(debug=debug_mode)

if __name__ == "__main__":
    main()