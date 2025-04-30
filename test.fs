
        func is_palindrome_number(n) {
            // Check if a number is a palindrome by using arithmetic operations
            let original = n
            let reversed = 0
            
            while (n > 0) {
                let digit = n % 10
                reversed assign reversed * 10 + digit
                n assign (n - digit) / 10
            }
            
            return original == reversed
        }
        
        func largest_palindrome_product() {
            let max_pal = 0
            for (let i = 100 to 999) {
                for (let j = i to 999) {
                    let prod = i * j
                    if (is_palindrome_number(prod) and prod > max_pal) {
                        max_pal assign prod
                    }
                }
            }
            return max_pal
        }
        largest_palindrome_product()