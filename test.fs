// Find all prime numbers up to n using the Sieve of Eratosthenes
func sieveOfEratosthenes(n) {
    // Initialize the sieve array
    let sieve = []
    for (let i = 0 to n + 1) {
        sieve assign sieve + [True]
    }
    
    // 0 and 1 are not prime
    sieve[0] = False
    sieve[1] = False
    
    // Mark non-primes
    let p = 2
    while (p * p <= n) {
        // If p is prime, mark all its multiples
        if (sieve[p] == True) {
            for (let i = p * p to n + 1 step p) {
                sieve[i] = False
            }
        }
        p assign p + 1
    }
    
    // Collect all prime numbers
    let primes = []
    for (let i = 2 to n + 1) {
        if (sieve[i] == True) {
            primes assign primes + [i]
        }
    }
    
    return primes
}

// Find the sum of all primes below n
func sumOfPrimes(n) {
    let primes = sieveOfEratosthenes(n)
    let sum = 0
    let primesLen = len(primes)
    for (let i = 0 to primesLen) {
        sum assign sum + primes[i]
    }
    return sum
}

print("Primes up to 30: ")
print(sieveOfEratosthenes(30))
print("Sum of primes below 100: ")
print(sumOfPrimes(100))  // Should be 1060