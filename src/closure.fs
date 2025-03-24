
func A(k, x1, x2, x3, x4, x5) {
    # B is defined inside A and captures k in its closure
    func B() {
        k = k - 1
        return A(k, B, x1, x2, x3, x4)
    }
    
    # The return value depends on k
    if k <= 0 {
        return x4() + x5()
    } else {
        return B()
    }
}


func one() { return 1 }
func minus_one() { return -1 }
func zero() { return 0 }


print("Running man-or-boy test...")
result = A(10, one, minus_one, minus_one, one, zero)
print("Result: " + result)
print("Expected: -67")
print("Test " + (result == -67 ? "PASSED" : "FAILED"))