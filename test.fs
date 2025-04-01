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