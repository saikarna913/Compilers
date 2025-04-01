# Compilers - CS327

## FluxScript(.fs)

#### Overview
This language is designed to be high-level (Python-like), dynamically typed, and functional, suitable for solving competitive programming problems and writing ai scripts. It emphasizes usability, expressive power, and functional programming principles like immutability where practical, while supporting a REPL for interactive development.

---

### Data Types
The language supports a minimal yet expressive set of built-in data types.

#### Primitive Data Types
- **Numbers**: Integers or floating-point values in decimal notation.
  - Examples: `10`, `3.14`, `-42.5`
- **Booleans**: Logical values.
  - Examples: `True`, `False`
- **Strings**: Sequences of characters enclosed in double quotes.
  - Examples: `"Hello, world!"`, `""`
- **Arrays**: Ordered, mutable collections enclosed in square brackets.
  - Examples: `[1, 2, 3]`, `["a", 2, True]`
- **Dictionaries**: Key-value mappings enclosed in curly braces.
  - Examples: `{ "key": 42, "flag": True }`

---

### Variables
Variables are dynamically typed and lexically scoped. They are declared with `let` and can be reassigned with `assign`.

- **Declaration**: `let <name> = <expression>`
  - Example: `let x = 10`
- **Reassignment**: `<name> assign <expression>`
  - Example: `x assign 20`
- **Scope**: Variables are lexically scoped within their enclosing block or function.

---

### Operators

#### Arithmetic Operators
Supported operators follow standard mathematical precedence:
- `+` (addition), `-` (subtraction), `*` (multiplication), `/` (division), `**` (exponentiation), `rem` (remainder), `quot` (integer division)
- Example: `10 + 5 * 2` evaluates to `20` (multiplication precedes addition).
- Precedence: `()` > `**` (right-associative) > `* / rem` (left-associative) > `+ -` (left-associative)

#### Comparison Operators
- `<`, `>`, `<=`, `>=`, `==`, `!=`
- Example: `10 < 20` evaluates to `True`

#### Logical Operators
- `and`, `or`, `not`
- Example: `True and not False` evaluates to `True`

#### Assignment Operators
- `let` (declaration), `assign` (reassignment)
- Example: `let x = 10`
 `x assign x + 1`

---

### Control Flow
Control flow constructs use `{}` blocks for clarity and consistency.

#### If Statements
- Syntax: `if (<condition>) { <block> } [else { <block> }]`
- Example:
  ```
  if (x < 0) {
      print "Negative"
  } else {
      print "Non-negative"
  }
  ```

#### While Loops
- Syntax: `while (<condition>) { <block> }`
- Example:
  ```
  let x = 0
  while (x < 5) {
      print x
      x assign x + 1
  }
  ```

#### For Loops
- Syntax: `for (let i = start to end [step s]) {
    <block>}`
- Example:
  ```
  for (let i = 1 to 5) {
      print i
  }
  ```
---

### Print Statements
- Syntax: `print <expression>`
- Example: `print "Hello, world!"`
- Outputs to the console; supports all data types.

---

### Functions
Support for first-class functions, proper closures, and included tail-call elimination for recursion.

#### Function Definition
- Syntax: `func <name>(<param1>, <param2>, ...) { <block> }`
- Example:
  ```
  func add(a, b) {
      return a + b
  }
  ```

#### Return Statement
- Syntax: `return <expression>`
- Example:
  ```
  func square(x) {
      return x * x
  }
  ```

#### First-Class Functions
Functions can be assigned to variables or passed as arguments.
- Example:
  ```
  let double = func(x) { return x * 2 }
  print double(5)  // Outputs: 10
  ```

#### Closures
Functions capture their lexical environment.
- Example:
  ```
  func counter() {
      let count = 0
      return func() {
          count assign count + 1
          return count
      }
  }
  let c = counter()
  print c()  // Outputs: 1
  print c()  // Outputs: 2
  ```

---


### Error Handling
The language provides error messages with line location and a REPL that doesn’t crash on errors.
- Division by zero: Raises `ZeroDivisionError` with line number and suggestion (e.g., "Check divisor").
- Syntax errors: Flags malformed expressions with location (e.g., `5 +` → "SyntaxError at line 1: incomplete expression").
- Example REPL session:
  ```
  > let x = 10 / 0
  [line 1] Error at '/': Division by zero
  > print x
  [line 1] Error at 'x': Undefined variable 'x'
  ```

---


### Example Program
```
func fib(n) {
    if (n <= 1) {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

let x = 10
print "Fibonacci of " + x + " is " + fib(x)
```

---

