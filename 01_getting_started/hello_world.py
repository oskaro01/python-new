"""
=============================================
  01 - HELLO WORLD & BASIC PRINT
=============================================
  From: quickref.me/python
  Your very first Python program!
=============================================
"""

# ===========================================
# The famous "Hello, World!" program
# ===========================================
# print() is a built-in function that outputs text to the console
print("Hello, World!")

# ===========================================
# You can print multiple items at once
# ===========================================
print("Hello", "world", "from", "Python!")

# ===========================================
# Print with a custom separator and end character
# ===========================================
print("apple", "banana", "cherry", sep=", ")  # Separator between items
print("Loading", end="...")  # Custom ending instead of newline
print(" Done!")  # This continues on the same line

# ===========================================
# Print variables
# ===========================================
name = "Alice"
age = 25
print("Name:", name, "Age:", age)

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Change the message above to your own name
#   2. Add a new print() statement with your age
#   3. Try using sep=" | " to separate items with a pipe
# ===========================================

# Expected output:
# Hello, World!
# Hello world from Python!
# apple, banana, cherry
# Loading... Done!
# Name: Alice Age: 25
