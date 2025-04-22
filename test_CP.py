#!/usr/bin/env python3
"""
FluxScript Interpreter Test Suite
---------------------------------
This test suite verifies the functionality of a FluxScript interpreter
by testing features needed for competitive programming problems.
"""

import unittest
import subprocess
import os
import tempfile
import time
import sys
import importlib.util

# Attempt to directly import the interpreter modules
try:
    # Add the parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.evaluator import Evaluator
    from src.lexer import Lexer
    from src.parser import Parser
    DIRECT_IMPORT = True
except ImportError:
    # If import fails, we'll use subprocess to run the flux.py
    DIRECT_IMPORT = False
    print("Could not import interpreter modules directly. Using subprocess method.")

class FluxScriptInterpreterTest(unittest.TestCase):
    """Test cases for FluxScript interpreter functionality."""
    
    def setUp(self):
        if DIRECT_IMPORT:
            self.evaluator = Evaluator()
    
    def run_fluxscript(self, code):
        """Run FluxScript code and return the output."""
        with tempfile.NamedTemporaryFile(suffix='.fs', delete=False) as temp:
            temp.write(code.encode('utf-8'))
            temp_name = temp.name
        
        try:
            if DIRECT_IMPORT:
                # Use direct module import method
                output_lines = []
                error_message = None
                returncode = 0
                
                # Redirect stdout to capture output
                import io
                from contextlib import redirect_stdout
                
                f = io.StringIO()
                with redirect_stdout(f):
                    try:
                        with open(temp_name, 'r') as file:
                            source = file.read()
                        
                        lexer = Lexer(source)
                        parser = Parser(lexer)
                        tree = parser.parse()
                        result = self.evaluator.interpret(tree)
                        
                        if result is not None:
                            print(self.evaluator.stringify(result))
                    except Exception as e:
                        error_message = str(e)
                        returncode = 1
                
                output = f.getvalue().strip()
                return output, error_message or "", returncode
            else:
                # Use subprocess method with flux.py
                # Find the flux.py script location relative to this test file
                flux_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "flux.py")
                result = subprocess.run([sys.executable, flux_script, temp_name], 
                                       capture_output=True, text=True)
                return result.stdout.strip(), result.stderr.strip(), result.returncode
        finally:
            os.unlink(temp_name)
    
    
    
    
    def test_loops(self):
        """Test while and for loops."""
        code = """
        // While loop
        let i = 0
        let sum1 = 0
        while (i < 5) {
            sum1 assign sum1 + i
            i assign i + 1
        }
        print sum1  // Should be 0+1+2+3+4 = 10
        
        // For loop
        let sum2 = 0
        for (let j = 0 to 5) {
            sum2 assign sum2 + j
        }
        print sum2  // Should be 0+1+2+3+4 = 10
        
        // For loop with step
        let sum3 = 0
        for (let k = 0 to 10 step 2) {
            sum3 assign sum3 + k
        }
        print sum3  // Should be 0+2+4+6+8 = 20
        """
        output, errors, returncode = self.run_fluxscript(code)
        expected_lines = ["10", "10", "20"]
        
        actual_lines = output.replace('\r\n', '\n').split('\n')
        self.assertEqual(len(actual_lines), len(expected_lines))
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            self.assertEqual(actual, expected)
        
        self.assertEqual(returncode, 0)
    
    def test_functions(self):
        """Test function definition and calling."""
        code = """
        func add(a, b) {
            return a + b
        }
        
        func factorial(n) {
            if (n <= 1) {
                return 1
            }
            let a = n * factorial(n-1)
            return a
        }
        
        print add(5, 3)       // Should be 8
        print factorial(5)    // Should be 120
        """
        output, errors, returncode = self.run_fluxscript(code)
        expected_lines = ["8", "120"]
        
        actual_lines = output.replace('\r\n', '\n').split('\n')
        self.assertEqual(len(actual_lines), len(expected_lines))
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            self.assertEqual(actual, expected)
        
        self.assertEqual(returncode, 0)
    
    def test_closures(self):
        """Test closures and first-class functions."""
        code = """
        func makeCounter() {
            let count = 0
            return func() {
                count assign count + 1
                return count
            }
        }
        
        let counter = makeCounter()
        print counter()  // Should be 1
        print counter()  // Should be 2
        print counter()  // Should be 3
        
        // Higher-order function
        func applyTwice(f, x) {
            return f(f(x))
        }
        
        func double(x) {
            return x * 2
        }
        
        print applyTwice(double, 3)  // Should be 12 (double(double(3)))
        """
        output, errors, returncode = self.run_fluxscript(code)
        expected_lines = ["1", "2", "3", "12"]
        
        actual_lines = output.replace('\r\n', '\n').split('\n')
        self.assertEqual(len(actual_lines), len(expected_lines))
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            self.assertEqual(actual, expected)
        
        self.assertEqual(returncode, 0)
    
    def test_data_structures(self):
        """Test arrays and dictionaries."""
        code = """
        // Arrays
        let arr = [1, 2, 3, 4, 5]
        print arr[2]        // Should be 3 (zero-indexed)
        
        // Dictionary
        let dict = {"name": "Alice", "age": 30}
        print dict["name"]  // Should be Alice
        """
        output, errors, returncode = self.run_fluxscript(code)
        expected_lines = ["3", "Alice"]
        
        actual_lines = output.replace('\r\n', '\n').split('\n')
        self.assertEqual(len(actual_lines), len(expected_lines))
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            self.assertEqual(actual, expected)
        
        self.assertEqual(returncode, 0)
    
    def test_error_handling(self):
        """Test error handling for common errors."""
        # Division by zero
        code = "print 10 / 0"
        output, errors, returncode = self.run_fluxscript(code)
        self.assertNotEqual(returncode, 0)
        
        # Different implementations might have different error messages
        self.assertTrue("division by zero" in errors.lower() or 
                        "zero division" in errors.lower() or
                        "division" in errors.lower(),
                        f"Expected division by zero error, got: {errors}")
        
        # Undefined variable
        code = "print undefinedVar"
        output, errors, returncode = self.run_fluxscript(code)
        self.assertNotEqual(returncode, 0)
        self.assertTrue("undefined" in errors.lower() or 
                        "not defined" in errors.lower() or
                        "unknown" in errors.lower(),
                        f"Expected undefined variable error, got: {errors}")
    
    # Competitive Programming problem tests
    def test_cp_fibonacci(self):
        """Test solving Fibonacci sequence problem."""
        code = """
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
        """
        output, errors, returncode = self.run_fluxscript(code)
        expected_lines = ["0", "1", "1", "2", "3", "5", "8", "13", "21", "34"]
        
        actual_lines = output.replace('\r\n', '\n').split('\n')
        self.assertEqual(len(actual_lines), len(expected_lines))
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            self.assertEqual(actual, expected)
        
        self.assertEqual(returncode, 0)
    
    def test_cp_prime_check(self):
        """Test solving prime number check problem."""
        code = """
        func isPrime(n) {
            if (n <= 1) {
                return False
            }
            if (n <= 3) {
                return True
            }
            if (n rem 2 == 0 or n rem 3 == 0) {
                return False
            }
            
            let i = 5
            while (i * i <= n) {
                if (n rem i == 0 or n rem (i + 2) == 0) {
                    return False
                }
                i assign i + 6
            }
            return True
        }
        
        // Test with some numbers
        let testNums = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        for (let i = 0 to 10) {
            let num = testNums[i]
            print num + " is prime: " + isPrime(num)
        }
        """
        output, errors, returncode = self.run_fluxscript(code)
        expected_lines = [
            "2 is prime: True",
            "3 is prime: True",
            "4 is prime: False",
            "5 is prime: True",
            "6 is prime: False",
            "7 is prime: True",
            "8 is prime: False",
            "9 is prime: False",
            "10 is prime: False",
            "11 is prime: True"
        ]
        
        actual_lines = output.replace('\r\n', '\n').split('\n')
        self.assertEqual(len(actual_lines), len(expected_lines))
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            self.assertEqual(actual, expected)
        
        self.assertEqual(returncode, 0)
    
    def test_cp_gcd_lcm(self):
        """Test solving GCD and LCM problems."""
        code = """
        func gcd(a, b) {
            while (b != 0) {
                let temp = b
                b assign a rem b
                a assign temp
            }
            return a
        }
        
        func lcm(a, b) {
            return (a * b) / gcd(a, b)
        }
        
        print "GCD of 48 and 18: " + gcd(48, 18)  // Should be 6
        print "LCM of 48 and 18: " + lcm(48, 18)  // Should be 144
        """
        output, errors, returncode = self.run_fluxscript(code)
        expected_lines = [
            "GCD of 48 and 18: 6",
            "LCM of 48 and 18: 144"
        ]
        
        actual_lines = output.replace('\r\n', '\n').split('\n')
        self.assertEqual(len(actual_lines), len(expected_lines))
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            self.assertEqual(actual, expected)
        
        self.assertEqual(returncode, 0)
    
    def test_cp_sorting(self):
        """Test sorting algorithm implementation."""
        code = """
        func bubbleSort(arr) {
    let n = 5  // Length of arr
    for (let i = 0 to n - 1) {
        for (let j = 0 to n - i - 2) {
            if (arr[j] > arr[j + 1]) {
                // Swap elements
                let temp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = temp
            }
        }
    }
    return arr
}

let numbers = [5, 3, 8, 4, 2]
let sorted = bubbleSort(numbers)

// Print sorted array
for (let i = 0 to 4) {
    print(sorted[i])
}
        """
        output, errors, returncode = self.run_fluxscript(code)
        expected_lines = ["2", "3", "4", "5", "8"]
        
        actual_lines = output.replace('\r\n', '\n').split('\n')
        self.assertEqual(len(actual_lines), len(expected_lines))
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            self.assertEqual(actual, expected)
        
        self.assertEqual(returncode, 0)
    
    def test_cp_dynamic_programming(self):
        """Test dynamic programming solution for a knapsack problem."""
        code = """
// Simplified Dynamic Programming approach for 0/1 Knapsack problem
func knapsack(weights, values, capacity) {
    // Create a single array to track the best value so far
    let dp = []
    let i = 0
    let a = [0]
    while (i <= capacity) {
        dp assign dp + a  // Add zeros one by one
        i assign i + 1
    }
    
    // Process each item
    i assign 0
    while (i < 5) {  // 5 items (weights.length)
        // For each capacity value (from highest to lowest)
        let newDp = []
        let j = 0
        while (j <= capacity) {
            newDp assign newDp + [dp[j]]  // Copy old values
            j assign j + 1
        }
        
        let capIndex = capacity
        while (capIndex >= weights[i]) {
            // Check if including this item would be better
            let oldVal = newDp[capIndex]
            let newVal = values[i] + dp[capIndex - weights[i]]
            
            // Update if better
            if (newVal > oldVal) {
                // Create a new array with the updated value
                let temp = []
                let k = 0
                while (k <= capacity) {
                    if (k == capIndex) {
                        temp assign temp + [newVal]  // Add the new value
                    } else {
                        temp assign temp + [newDp[k]]  // Copy old value
                    }
                    k assign k + 1
                }
                newDp assign temp
            }
            
            // Move to next capacity
            capIndex assign capIndex - 1
        }
        
        // Update DP with the new values
        dp assign newDp
        i assign i + 1
    }
    
    // Return the maximum value
    return dp[capacity]
}

// Test data
let weights = [2, 3, 4, 5, 1]
let values = [3, 4, 5, 6, 1]
let capacity = 10

print("Maximum value: " + knapsack(weights, values, capacity))  // Should output 13

        """
        output, errors, returncode = self.run_fluxscript(code)
        expected = "Maximum value: 13"
        
        self.assertTrue(expected in output.replace('\r\n', '\n'))
        self.assertEqual(returncode, 0)
    
    def test_cp_binary_search(self):
        """Test binary search implementation."""
        code = """
func binarySearch(arr, target) {
    let left = 0
    let right = len(arr) - 1
    
    while (left <= right) {
        let mid = left + (right - left) / 2
        let mid_floor = floor(mid)  // Ensure integer
        
        if (arr[mid_floor] == target) {
            return mid_floor  // Found target at index mid
        }
        
        if (arr[mid_floor] < target) {
            left assign mid_floor + 1  // Search right half
        } else {
            right assign mid_floor - 1  // Search left half
        }
    }
    
    return -1  // Target not found
}

let sortedArr = [1, 3, 5, 7, 9, 11, 13, 15]

// Search for various elements
print("Index of 1: " + binarySearch(sortedArr, 1))   // Should be 0
print("Index of 7: " + binarySearch(sortedArr, 7))   // Should be 3
print("Index of 15: " + binarySearch(sortedArr, 15))  // Should be 7
print("Index of 6: " + binarySearch(sortedArr, 6))   // Should be -1 (not found)

        """
        output, errors, returncode = self.run_fluxscript(code)
        expected_lines = ["0", "3", "7", "-1"]
        
        actual_lines = output.replace('\r\n', '\n').split('\n')
        self.assertEqual(len(actual_lines), len(expected_lines))
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            self.assertEqual(actual, expected)
        
        self.assertEqual(returncode, 0)
    
    def test_cp_string_manipulation(self):
        """Test string manipulation functions."""
        code = """
// String manipulation functions for FluxScript

func isPalindrome(str) {
    let n = len(str)
    let half = n / 2
    half assign floor(half)
    
    for (let i = 0 to half) {
        if (str[i] != str[n - 1 - i]) {
            return False
        }
    }
    return True
}

func countOccurrences(str, target) {
    let count = 0
    let n = len(str)
    let i = 0
    
    while (i < n) {
        if (str[i] == target) {
            count assign count + 1
        }
        i assign i + 1
    }
    return count
}

// Test the functions
print("radar is palindrome: " + isPalindrome("radar"))    // Should be True
print("hello is palindrome: " + isPalindrome("hello"))    // Should be False
print("'a' occurs in 'banana': " + countOccurrences("banana", "a"))  // Should be 3
        """
        output, errors, returncode = self.run_fluxscript(code)
        expected_lines = ["True", "False", "3"]
        
        actual_lines = output.replace('\r\n', '\n').split('\n')
        self.assertEqual(len(actual_lines), len(expected_lines))
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            self.assertEqual(actual, expected)
        
        self.assertEqual(returncode, 0)
    
    def test_small_performance(self):
        """Test with a small performance benchmark."""
        code = """
        func sum_to_n(n) {
            let sum = 0
            for (let i = 1 to n + 1) {
                sum assign sum + i
            }
            return sum
        }
        
        print sum_to_n(1000)  // Should be 500500
        """
        start_time = time.time()
        output, errors, returncode = self.run_fluxscript(code)
        execution_time = time.time() - start_time
        
        expected = "500500"
        self.assertTrue(expected in output.replace('\r\n', '\n'))
        self.assertEqual(returncode, 0)
        print(f"Small performance test took {execution_time:.2f} seconds")
    
    def test_cp_compound(self):
        """Test a compound competitive programming problem."""
        code = """
        // Find all prime numbers up to n using the Sieve of Eratosthenes
        func sieveOfEratosthenes(n) {
            // Initialize the sieve array
            let sieve = []
            for (let i = 0 to n + 1) {
                sieve assign sieve + [True]
            }
            
            // 0 and 1 are not prime
            sieve[0] assign False
            sieve[1] assign False
            
            // Mark non-primes
            let p = 2
            while (p * p <= n) {
                // If p is prime, mark all its multiples
                if (sieve[p] == True) {
                    for (let i = p * p to n + 1 step p) {
                        sieve[i] assign False
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
            for (let i = 0 to primes.length) {
                sum assign sum + primes[i]
            }
            return sum
        }
        
        print "Primes up to 30: " + sieveOfEratosthenes(30)
        print "Sum of primes below 100: " + sumOfPrimes(100)  // Should be 1060
        """
        output, errors, returncode = self.run_fluxscript(code)
        
        # Check for the sum of primes below 100
        self.assertTrue("Sum of primes below 100: 1060" in output.replace('\r\n', '\n'))
        self.assertEqual(returncode, 0)

if __name__ == "__main__":
    unittest.main()