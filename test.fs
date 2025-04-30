
    // Nested function definitions with multiple levels of variable capture
    func outerFunction(x) {
        let y = x * 2
        
        func middleFunction(z) {
            // This function can access both x and y from parent scopes
            let w = x + y + z
            
            func innerFunction() {
                // This function can access all variables from all parent scopes
                return x + y + z + w
            }
            
            return innerFunction
        }
        
        return middleFunction
    }
    
    let middleFn = outerFunction(5)    // x=5, y=10
    let innerFn = middleFn(3)          // z=3, w=18
    
    print "Result of innerFunction (should be 5+10+3+18=36):"
    print innerFn()
    
    // Create another instance to ensure closures work properly
    let anotherMiddleFn = outerFunction(2)   // x=2, y=4
    let anotherInnerFn = anotherMiddleFn(1)  // z=1, w=7
    
    print "Result of another innerFunction (should be 2+4+1+7=14):"
    print anotherInnerFn()