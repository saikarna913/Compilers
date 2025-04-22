// Test break and continue in loops

// For loop with break
let sum1 = 0
for (let i = 0 to 10) {
    if (i > 5) {
        break
    }
    sum1 = sum1 + i
}
print "Sum with break (should be 0+1+2+3+4+5=15): " + sum1

// For loop with continue
let sum2 = 0
for (let i = 0 to 10) {
    if (i % 2 == 0) {
        continue
    }
    sum2 = sum2 + i
}
print "Sum with continue (odd numbers only, should be 1+3+5+7+9=25): " + sum2

// While loop with break
let count = 0
let sum3 = 0
while (count < 10) {
    if (count > 5) {
        break
    }
    sum3 = sum3 + count
    count = count + 1
}
print "While loop with break (should be 0+1+2+3+4+5=15): " + sum3

// Nested loops with break and continue
let outer_sum = 0
for (let i = 0 to 5) {
    for (let j = 0 to 5) {
        if (j == 2) {
            continue
        }
        if (j == 4) {
            break
        }
        outer_sum = outer_sum + (i * 10 + j)
    }
}
print "Nested loops with break/continue: " + outer_sum