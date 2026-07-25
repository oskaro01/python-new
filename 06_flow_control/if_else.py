"""
=============================================
  16 - IF / ELIF / ELSE
=============================================
  From: quickref.me/python
  Making decisions in your code.
=============================================
"""

# ===========================================
# Basic if/elif/else
# ===========================================
print("=== BASIC IF/ELIF/ELSE ===")

num = 200
if num > 0:
    print("num is greater than 0")
else:
    print("num is not greater than 0")

# ===========================================
# Full if/elif/else chain
# ===========================================
print("\n=== FULL CHAIN ===")
num = 5
if num > 10:
    print("num is totally bigger than 10.")
elif num < 10:
    print("num is smaller than 10.")
else:
    print("num is indeed 10.")

# ===========================================
# Multiple Conditions
# ===========================================
print("\n=== MULTIPLE CONDITIONS ===")
age = 25
has_license = True

if age >= 18 and has_license:
    print("You can drive!")
else:
    print("You cannot drive.")

# Using 'or'
day = "Saturday"
if day == "Saturday" or day == "Sunday":
    print("It's the weekend!")
else:
    print("It's a weekday.")

# Using 'not'
value = True
if not value:
    print("Value is False")
elif value is None:
    print("Value is None")
else:
    print("Value is True")

# ===========================================
# One-liner (Ternary Operator)
# ===========================================
print("\n=== TERNARY OPERATOR ===")
a = 330
b = 200
r = "a" if a > b else "b"
print(f"r = '{r}' because {a} > {b} is {a > b}")

# Practical example
num = 7
result = "even" if num % 2 == 0 else "odd"
print(f"{num} is {result}")

# ===========================================
# Checking Multiple Values (in operator)
# ===========================================
print("\n=== CHECK MULTIPLE VALUES ===")
fruit = "apple"
if fruit in ["apple", "banana", "orange"]:
    print(f"{fruit} is in the list!")

# ===========================================
# Nested Conditions
# ===========================================
print("\n=== NESTED CONDITIONS ===")
x = 15
if x > 0:
    if x % 2 == 0:
        print("Positive and even")
    else:
        print("Positive and odd")
else:
    print("Negative or zero")

# ===========================================
# Truthy/Falsy Values in Conditions
# ===========================================
print("\n=== TRUTHY/FALSY ===")
# These are all considered False:
print(f"bool(0)     = {bool(0)}")
print(f"bool('')    = {bool('')}")
print(f"bool([])    = {bool([])}")
print(f"bool(None)  = {bool(None)}")

# So you can write:
name = ""
if name:  # Same as: if name != "":
    print(f"Hello, {name}")
else:
    print("Name is empty!")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Write code that checks if a number is positive, negative, or zero
#   2. Check if a year is a leap year (divisible by 4 and not 100, unless 400)
#   3. Use a ternary to assign "pass" or "fail" based on a score >= 50
# ===========================================
