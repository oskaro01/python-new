"""
=============================================
  20 - LAMBDA FUNCTIONS
=============================================
  From: quickref.me/python
  Small anonymous functions — one-liners!
=============================================
"""

# ===========================================
# Basic Lambda Syntax
# ===========================================
print("=== BASIC LAMBDA ===")
# Syntax:  lambda parameters: expression

# Traditional function
def is_positive(x):
    return x > 2

print(f"Traditional: is_positive(3) = {is_positive(3)}")

# Same thing as a lambda
print(f"Lambda:      (lambda x: x > 2)(3) = {(lambda x: x > 2)(3)}")

# Lambda with multiple parameters
result = (lambda x, y: x ** 2 + y ** 2)(2, 1)
print(f"lambda x,y: x²+y²: (2,1) = {result}")

# ===========================================
# Lambda with map()
# ===========================================
print("\n=== LAMBDA WITH MAP() ===")
# map() applies a function to every item in an iterable
numbers = [1, 2, 3, 4, 5]

# Square each number
squared = list(map(lambda x: x ** 2, numbers))
print(f"Original: {numbers}")
print(f"Squared:  {squared}")

# Convert to uppercase
names = ["alice", "bob", "charlie"]
upper_names = list(map(lambda n: n.upper(), names))
print(f"Upper: {upper_names}")

# ===========================================
# Lambda with filter()
# ===========================================
print("\n=== LAMBDA WITH FILTER() ===")
# filter() keeps items where the function returns True

# Keep even numbers
evens = list(filter(lambda x: x % 2 == 0, range(1, 11)))
print(f"Even numbers 1-10: {evens}")

# Keep strings longer than 3 chars
words = ["hi", "hello", "hey", "greetings"]
long_words = list(filter(lambda w: len(w) > 3, words))
print(f"Words longer than 3: {long_words}")

# ===========================================
# Lambda with sorted()
# ===========================================
print("\n=== LAMBDA WITH SORTED() ===")

# Sort by a custom key
students = [
    {"name": "Alice", "grade": 85},
    {"name": "Bob", "grade": 72},
    {"name": "Charlie", "grade": 93},
]

# Sort by grade
sorted_students = sorted(students, key=lambda s: s["grade"])
print(f"Sorted by grade: {sorted_students}")

# Sort by name (descending)
sorted_names = sorted(students, key=lambda s: s["name"], reverse=True)
print(f"Sorted by name (reverse): {sorted_names}")

# Sort a list of tuples by the second element
pairs = [(1, 5), (3, 2), (2, 8)]
sorted_pairs = sorted(pairs, key=lambda p: p[1])
print(f"Pairs sorted by second value: {sorted_pairs}")

# ===========================================
# Lambda with reduce()
# ===========================================
print("\n=== LAMBDA WITH REDUCE() ===")
from functools import reduce

# Sum all numbers
sum = reduce(lambda a, b: a + b, [1, 2, 3, 4, 5])
print(f"Sum using reduce: {sum}")

# Find the maximum
max_val = reduce(lambda a, b: a if a > b else b, [3, 7, 2, 9, 5])
print(f"Max using reduce: {max_val}")

# ===========================================
# When to Use Lambda vs Regular Functions
# ===========================================
print("\n=== LAMBDA vs REGULAR ===")

# ✅ Use lambda for simple, one-time operations
# ✅ Use lambda inside map(), filter(), sorted()
# ✅ Use lambda when you need a quick function
#
# ❌ Don't use lambda for complex logic
# ❌ Don't use lambda if you need to use it multiple times
#    (just define a regular function instead)

# GOOD use of lambda:
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))

# BETTER as a named function if reused:
def double(x):
    return x * 2
doubled = list(map(double, numbers))

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Use lambda with filter() to get only odd numbers from 1-20
#   2. Sort a list of strings by their length using sorted(..., key=...)
#   3. Map a list of temperatures in Celsius to Fahrenheit
# ===========================================
