"""
=============================================
  29 - GENERATORS
=============================================
  From: quickref.me/python
  Functions that produce values on-demand
  (lazy evaluation) — great for large datasets!
=============================================
"""

# ===========================================
# What is a Generator?
# ===========================================
# A generator is like a function, but instead
# of "return", it uses "yield" — and it remembers
# its state between calls!

# ===========================================
# A Simple Generator
# ===========================================
print("=== BASIC GENERATOR ===")

def double_numbers(iterable):
    """Generator that yields each value doubled."""
    for i in iterable:
        yield i + i  # Yield one value at a time

# Using the generator
gen = double_numbers([1, 2, 3, 4, 5])
print(f"Generator object: {gen}")

# Get values one at a time
print(f"next(gen) = {next(gen)}")  # 2
print(f"next(gen) = {next(gen)}")  # 4
print(f"next(gen) = {next(gen)}")  # 6

# ===========================================
# Converting Generator to List
# ===========================================
print("\n=== GENERATOR TO LIST ===")

values = (-x for x in [1, 2, 3, 4, 5])  # Generator expression
print(f"Generator: {values}")

gen_to_list = list(values)  # Materialize all values at once
print(f"Converted to list: {gen_to_list}")

# ===========================================
# Generator Expression vs List Comprehension
# ===========================================
print("\n=== GENERATOR vs LIST ===")

# List comprehension — creates ALL values in memory
list_squares = [x ** 2 for x in range(10)]
print(f"List comprehension: {list_squares}")

# Generator expression — lazy, yields one at a time
gen_squares = (x ** 2 for x in range(10))
print(f"Generator expression: {gen_squares}")
print(f"Next from generator: {next(gen_squares)}")  # 0
print(f"Next from generator: {next(gen_squares)}")  # 1

# ===========================================
# Why Generators Are Useful
# ===========================================
print("\n=== WHY GENERATORS? ===")

# Memory efficiency!
# Try this with a list and a 10 million item range:
#   list(range(10_000_000))  # Uses ~80 MB of RAM!
#   range(10_000_000)        # Uses almost no RAM!

# Process a large file line by line:
def read_large_file(file_path):
    """Generator that reads one line at a time."""
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

# Practical: infinite sequence
def fibonacci():
    """Generate an infinite Fibonacci sequence."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Get first 10 Fibonacci numbers
fib = fibonacci()
first_10 = [next(fib) for _ in range(10)]
print(f"First 10 Fibonacci numbers: {first_10}")

# ===========================================
# Generator with send()
# ===========================================
print("\n=== SEND VALUES INTO A GENERATOR ===")

def echo():
    """Generator that echoes what you send it."""
    while True:
        received = yield
        print(f"Generator received: {received}")

gen = echo()
next(gen)          # Start the generator
gen.send("Hello")  # Send a value
gen.send("World")  # Send another
gen.close()        # Stop the generator

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a generator that yields even numbers up to n
#   2. Use a generator expression to create squares of 1-10
#   3. Create an infinite counter generator and get the first 5 values
# ===========================================
