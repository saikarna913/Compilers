# FluxScript Getting Started

Welcome to FluxScript, a high-level, dynamically typed, functional programming language designed for competitive programming and rapid prototyping. This guide will help you install and run FluxScript, and it includes some tutorial examples to get you started.

## Installation

**Clone the Repository**  
   Clone the project to your local machine:
   ```bash
   git clone https://github.com/AtalGupta/Compilers.git
   cd Compilers
   ```

## Running FluxScript

FluxScript comes with an entry point script named `flux.py`. You can run FluxScript programs by specifying the source file (with a `.fs` extension).

For example, to run a FluxScript program stored in `example.fs`, use:
```bash
python flux.py example.fs
```

Alternatively, the provided Bash script `test.sh` can be used to run your programs. Make sure it has execute permissions:
```bash
chmod +x test.sh
./test.sh example.fs
```

## Tutorial Examples

### Example 1: Hello World

Create a file named `hello.fs` with the following content:
```fluxscript
print "Hello, FluxScript!"
```
Run it using:
```bash
python flux.py hello.fs
```

### Example 2: Variables and Expressions

Create a file named `variables.fs`:
```fluxscript
let x = 10
let y = 20
print "Sum: " + (x + y)
```
Run it using:
```bash
python flux.py variables.fs
```

### Example 3: Functions & Closures

FluxScript supports first-class functions and closures. Create a file named `counter.fs`:
```fluxscript
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
Run it using:
```bash
python flux.py counter.fs
```

### Example 4: Conditional Statements with Elif

FluxScript supports if/else and extended elif clauses. Create a file named `condition.fs`:
```fluxscript
let x = 5
if (x > 3) {
    print "x is greater than 3"
} elif (x == 3) {
    print "x equals 3"
} else {
    print "x is less than 3"
}
```
Run it using:
```bash
python flux.py condition.fs
```

### Example 5: Loops with Break & Continue

Loops have their own lexical scope and can use `break` and `continue`. Create a file named `loop.fs`:
```fluxscript
for (let i = 1 to 5) {
    if (i == 3) {
        continue
    }
    print i
    if (i == 4) {
        break
    }
}
```
Run it using:
```bash
python flux.py loop.fs
```

## Conclusion

You have now installed FluxScript and seen several examples covering the basics such as printing, variables, functions, control flow with conditionals, and loops. As you explore the language further, consider experimenting with additional features like dictionaries and more advanced functional concepts.

Happy coding in FluxScript!
