## Overview
This programming language is designed for high-level, dynamically typed, and functional programming. It is particularly well-suited for solving competitive programming problems, emphasizing usability, expressive power, and functional programming principles such as immutability (where practical). A REPL (Read-Eval-Print Loop) is supported for interactive development.

## Key Features
- **High-Level**: Python-like syntax for ease of use.
- **Dynamically Typed**: Type errors are detected at runtime.
- **Functional Paradigm**: Supports first-class functions, closures, and tail-call elimination.
- **Compilation**: Generates bytecode for efficient execution.
- **Error Handling**: Provides clear, actionable error messages.
- **REPL Support**: Ensures resilience and usability during interactive execution.
- **Test Coverage**: 100% test coverage ensures correctness and reliability.

## Data Types
### Primitive Data Types
- **Numbers**: Integers and floating-point values.
  - Example: `10`, `3.14`, `-42.5`
- **Booleans**: Logical values.
  - Example: `True`, `False`
- **Strings**: Text enclosed in double quotes.
  - Example: `"Hello, world!"`, `""`
- **Arrays**: Ordered, mutable collections enclosed in square brackets.
  - Example: `[1, 2, 3]`, `["a", 2, True]`

### Desirable Data Types
- **Dictionaries**: Key-value mappings enclosed in curly braces.
  - Example: `{ "key": 42, "flag": True }`

## Variables
Variables are dynamically typed and lexically scoped.
- **Declaration**: `let <name> = <expression>`
  - Example: `let x = 10`
- **Reassignment**: `<name> assign <expression>`
  - Example: `x assign 20`
- **Scope**: Variables are lexically scoped within their enclosing block or function.

## Operators
### Arithmetic Operators
- `+`, `-`, `*`, `/`, `**` (exponentiation), `rem` (remainder), `quot` (integer division)
- Example: `10 + 5 * 2` evaluates to `20`

### Comparison Operators
- `<`, `>`, `<=`, `>=`, `==`, `!=`
- Example: `10 < 20` evaluates to `True`

### Logical Operators
- `and`, `or`, `not`
- Example: `True and not False` evaluates to `True`

## Control Flow
### If Statements
```plaintext
if (x < 0) {
    print "Negative"
} else {
    print "Non-negative"
}
```

### While Loops
```plaintext
let x = 0
while (x < 5) {
    print x
    x assign x + 1
}
```

### For Loops
```plaintext
for (let i = 1 to 5) {
    print i
}
```

### Repeat Loops
```plaintext
let x = 0
repeat {
    x assign x + 1
} until (x == 5)
```

### Match (Pattern Matching)
```plaintext
let arr = [1, 2, 3]
match arr {
    [] -> "Empty",
    [head, *tail] -> head + match tail { [] -> 0, [h, *t] -> h + match t }
}
```

## Functions
Functions are first-class citizens with closures and tail-call elimination.

### Function Definition
```plaintext
func add(a, b) {
    return a + b
}
```

### First-Class Functions
```plaintext
let double = func(x) { return x * 2 }
print double(5)  # Outputs: 10
```

### Closures
```plaintext
func counter() {
    let count = 0
    return func() {
        count assign count + 1
        return count
    }
}
let c = counter()
print c()  # Outputs: 1
print c()  # Outputs: 2
```

### Tail-Call Optimization
```plaintext
func factorial(n, acc = 1) {
    if (n <= 1) {
        return acc
    }
    return factorial(n - 1, n * acc)
}
print factorial(1000)  # Works without stack overflow
```

## Conditional Expressions
```plaintext
let max = a if a > b else b
```

## Error Handling
- **Division by zero**: Raises `ZeroDivisionError` with suggestions.
- **Syntax errors**: Clearly flagged with line numbers.
- **Undefined variables**: Identified with helpful messages.

### Example REPL Session
```plaintext
> let x = 10 / 0
ZeroDivisionError: Division by zero at line 1. Suggestion: Ensure divisor is non-zero.
> print x
Undefined variable 'x' at line 2. Suggestion: Define 'x' before use.
```

## Compilation
- Compiles to bytecode for optimized execution.
- Ensures 100% test coverage for correctness.

## Example Program
```plaintext
func fib(n) {
    if (n <= 1) {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

let x = 10
print "Fibonacci of " + x + " is " + fib(x)
```

## Summary
This language is designed for ease of use, performance, and functional programming paradigms. It provides interactive development support with a robust REPL and ensures error-free execution through clear debugging messages and full test coverage. The syntax is designed to be simple, expressive, and efficient for both beginners and experienced developers.

If you have any further suggestions or improvements, feel free to contribute!


