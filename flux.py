import sys
from src.evaluator import run_file, Evaluator
from src.lexer import Lexer
from src.parser import Parser

def run_repl():
    """Starts an interactive Flux REPL."""
    evaluator = Evaluator()
    print("Flux REPL (Type 'exit' or 'quit' to end)")
    while True:
        try:
            line = input("> ")
            if line.lower() in ("exit", "quit"):
                break
            if not line.strip():
                continue
            # Wrap input in a block for parsing
            lexer = Lexer(line)
            parser = Parser(lexer)
            tree = parser.parse()
            result = evaluator.interpret(tree)
            if result is not None:
                print(evaluator.stringify(result))
        except Exception as e:
            print(f"Error: {e}")

def main():
    if len(sys.argv) == 1:
        run_repl()  # No filename → REPL mode
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
        if not filename.endswith('.fs'):
            print("Error: File must have a .fs extension")
            sys.exit(1)
        run_file(filename)  # Run the file
    else:
        print("Usage: flux [filename.fs]")
        print("If no filename is provided, launches REPL mode.")
        sys.exit(1)

if __name__ == "__main__":
    main()