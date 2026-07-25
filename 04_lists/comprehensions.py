"""
=============================================
  12 - LIST COMPREHENSIONS
=============================================
  From: quickref.me/python
  One of Python's most powerful features!
  Create lists in a single, readable line.
=============================================
"""

# ===========================================
# Basic List Comprehension
# ===========================================
print("=== BASIC LIST COMPREHENSION ===")
# Syntax: [expression for item in iterable]

# Traditional way
squares = []
for x in range(1, 6):
    squares.append(x ** 2)
print(f"Traditional loop: {squares}")

# Comprehension way (same result!)
squares = [x ** 2 for x in range(1, 6)]
print(f"Comprehension:   {squares}")

# ===========================================
# With a Condition
# ===========================================
print("\n=== WITH CONDITION (if) ===")
# Syntax: [expression for item in iterable if condition]

# Get odd numbers
odds = [x for x in range(1, 20) if x % 2 == 1]
print(f"Odd numbers 1-19: {odds}")

# Get squares of odd numbers
odd_squares = [x ** 2 for x in range(1, 11) if x % 2 == 1]
print(f"Squares of odd numbers 1-10: {odd_squares}")

# Filter a list
items = [3, 4, 5, 6, 7]
greater_than_5 = [x for x in items if x > 5]
print(f"Items > 5: {greater_than_5}")

# ===========================================
# Using Conditions to Transform
# ===========================================
print("\n=== TRANSFORMING WITH CONDITIONS ===")

# Categorize numbers
numbers = [1, 2, 3, 4, 5, 6]
even_odd = ["even" if n % 2 == 0 else "odd" for n in numbers]
print(f"Even/Odd labels: {even_odd}")

# ===========================================
# Nested Loops in Comprehensions
# ===========================================
print("\n=== NESTED LOOPS ===")
# Flatten a matrix
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [num for row in matrix for num in row]
print(f"Flattened matrix: {flat}")

# Cartesian product
colors = ["red", "green"]
sizes = ["S", "M", "L"]
combos = [(c, s) for c in colors for s in sizes]
print(f"Color/size combos: {combos}")

# ===========================================
# Using Functions in Comprehensions
# ===========================================
print("\n=== USING FUNCTIONS ===")

names = ["  Alice ", "BOB", "  Charlie"]
clean = [name.strip().title() for name in names]
print(f"Cleaned names: {clean}")

# ===========================================
# filter() with lambda — alternative approach
# ===========================================
print("\n=== filter() ALTERNATIVE ===")
# Same as: [x for x in range(1, 20) if x % 2 == 1]
filtered = list(filter(lambda x: x % 2 == 1, range(1, 20)))
print(f"Using filter(): {filtered}")

# ===========================================
# Dictionary & Set Comprehensions
# ===========================================
print("\n=== DICT & SET COMPREHENSIONS ===")

# Dict comprehension: {key: value for item in iterable}
square_dict = {x: x ** 2 for x in range(1, 6)}
print(f"Dict comprehension: {square_dict}")

# Set comprehension: {expression for item in iterable}
numbers_list = [1, 2, 2, 3, 3, 3, 4]
unique_squares = {x ** 2 for x in numbers_list}
print(f"Set comprehension (unique): {unique_squares}")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a list of even numbers from 1 to 20 using comprehension
#   2. Convert ["hello", "world", "python"] to uppercase
#   3. Create a dict mapping numbers 1-5 to their cubes (n³)
# ===========================================
