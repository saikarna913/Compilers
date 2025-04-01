# FluxScript

## Introduction
**FluxScript (.fs)** is a high-level, dynamically typed, functional programming language designed for competitive programming and AI scripting. It prioritizes usability, expressive power, and functional programming principles like immutability where practical. With a robust REPL, FluxScript supports interactive development, making it perfect for rapid prototyping and experimentation.
---

## Language Design
### Design Choices
- **High-level (Python-like)**: Simple, readable syntax to boost productivity.
- **Dynamically typed**: No type declarations required, providing flexibility for quick scripting.
- **Functional**: Includes first-class functions, proper closures, and tail-call elimination for efficient recursion.

### Motivation
FluxScript aims to strike a balance between power and ease of use, catering to competitive programmers and AI developers. Its interactive REPL enhances the coding experience, ensuring a seamless workflow for users.


## Implementation 
### Progress So Far
FluxScript’s implementation is complete and reliable:
- **Core Components**:
  - Lexer, parser, and evaluator fully implemented to process all language constructs.
  - Bytecode compilation for efficient execution(pending)
- **MUST Features**:
  - Primitive data types: numbers, booleans, strings, arrays
  - Control flow: `if-else`, `while`, `for`, and recursion
  - Functions: First-class citizens with proper closure support, tail-call optimization(pending)
- **DESIRABLE Features**:
  - Lexically-scoped variables for better organization
  - Dictionaries for key-value data storage
  - Detailed error messages with line numbers
- **Testing**: Aim to achieve 100% automated test coverage for all features.(Current 81%)

## Documentation
### User-Friendly Documentation
FluxScript’s documentation is crafted for accessibility:
- **Language Reference**: Detailed syntax rules and examples for all constructs.[README.md](README.md)
- **Tutorial**: Step-by-step guide for new users, covering REPL usage and basic programming task.[getting_started.md](getting_started.md)
- **Example**:
  ```fluxscript
  func square(x) {
      return x * x
  }
  let x = 5
  print "Square of " + x + " is " + square(x)
  ```
  This snippet showcases variable declaration, function definition, and string concatenation.


## Test Coverage
### Ease of Running Tests
- **Single Command**: Run `python run_coverage.py` to execute the full test suite.
- **Test Suite Breakdown**:
  - Unit tests for lexer, parser, evaluator, and AST.
  - Feature tests covering all language constructs.
  - Real-world tests using Euler problems to validate usability.

### Codebase Coverage
- **Aim 100% Coverage**: Every line of code is tested, ensuring robustness and correctness.

## Teamwork
### Work Distribution
- **Collaborative Effort**: Tasks were assigned based on team members strengths
- **Even Contribution**: Regular meetings kept the team aligned, with all members contributing equally.

---

### Code Demonstration 

#### REPL Basics
```fluxscript
> let x = 10
> print x + 5
15
```
Demonstrates variable declaration and basic arithmetic

#### Function and Recursion
```fluxscript
func fib(n) {
    if (n <= 1) {
        return n
    }
    let a = fib(n - 1)
    let b = fib(n - 2)
    print "Calculating fib(" + n + "): " + a + " + " + b
    return a + b
}

print "Fibonacci of 6 is: " + fib(6)
```

#### Error Handling
```fluxscript
> let y = 10 / 0
[line 1] Error at '/': Division by zero
> print y
[line 1] Error at 'y': Undefined variable 'y'
```
Shows how the REPL provides clear error messages without crashing.

---
