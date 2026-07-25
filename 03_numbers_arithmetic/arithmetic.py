"""
=============================================
  08 - ARITHMETIC OPERATORS
=============================================
  From: quickref.me/python
  All the math operations you can do in Python.
=============================================
"""

# ===========================================
# Basic Arithmetic
# ===========================================
print("=== BASIC ARITHMETIC ===")
a, b = 10, 3

print(f"a = {a}, b = {b}")
print(f"Addition (+)       : {a} + {b} = {a + b}")       # 13
print(f"Subtraction (-)    : {a} - {b} = {a - b}")       # 7
print(f"Multiplication (*) : {a} * {b} = {a * b}")       # 30

# ===========================================
# Division - Important!
# ===========================================
print("\n=== DIVISION ===")
print(f"Normal division (/)    : {a} / {b} = {a / b}")   # 3.333... (ALWAYS float!)
print(f"Integer division (//) : {a} // {b} = {a // b}")  # 3 (floor division)
print(f"Modulo (%)            : {a} % {b} = {a % b}")    # 1 (remainder)
print(f"Exponentiation (**)   : {a} ** {b} = {a ** b}")  # 1000 (10^3)

# ===========================================
# Key difference: / vs //
# ===========================================
print("\n=== / vs // (DETAILED) ===")
print(f"7 / 2  = {7 / 2}")    # 3.5  (float division)
print(f"7 // 2 = {7 // 2}")   # 3    (integer division, truncates down)
print(f"-7 / 2  = {-7 / 2}")   # -3.5
print(f"-7 // 2 = {-7 // 2}")  # -4   (floor division goes DOWN)

# ===========================================
# Plus-Equals (shorthand)
# ===========================================
print("\n=== PLUS-EQUALS ===")
counter = 0
counter += 10  # Same as: counter = counter + 10
print(f"counter += 10  = {counter}")  # 10

counter = 0
counter = counter + 10
print(f"counter = counter + 10  = {counter}")  # Same result

# Works with strings too!
message = "Part 1."
message += " Part 2."
print(f"\nString += : '{message}'")  # 'Part 1. Part 2.'

# ===========================================
# All shorthand operators
# ===========================================
print("\n=== ALL SHORTHAND OPERATORS ===")
x = 10
x += 5   # x = x + 5   => 15
print(f"x += 5:  {x}")

x -= 3   # x = x - 3   => 12
print(f"x -= 3:  {x}")

x *= 2   # x = x * 2   => 24
print(f"x *= 2:  {x}")

x /= 4   # x = x / 4   => 6.0
print(f"x /= 4:  {x}")

x //= 2  # x = x // 2  => 3.0
print(f"x //= 2: {x}")

x = 10
x %= 3   # x = x % 3   => 1
print(f"x %= 3:  {x}")

x **= 2  # x = x ** 2  => 1
print(f"x **= 2: {x}")

# ===========================================
# Order of Operations (PEMDAS)
# ===========================================
print("\n=== ORDER OF OPERATIONS ===")
print(f"2 + 3 * 4 = {2 + 3 * 4}")       # 14  (multiplication first)
print(f"(2 + 3) * 4 = {(2 + 3) * 4}")   # 20  (parentheses first)
print(f"2 ** 3 * 4 = {2 ** 3 * 4}")     # 32  (exponent first: 8*4)

# ===========================================
# TRY IT YOURSELF:
#   1. Calculate the area of a circle with radius 5 (pi * r^2)
#   2. What's the remainder when 17 is divided by 5?
#   3. Convert 100 degrees Fahrenheit to Celsius: (F - 32) * 5/9
# ===========================================
