"""
=============================================
  02 - VARIABLES IN PYTHON
=============================================
  From: quickref.me/python
  Python is dynamically typed — variables don't
  need explicit type declarations.
=============================================
"""

# ===========================================
# Variables are created when you assign a value
# No 'let', 'const', or 'var' needed!
# ===========================================
age = 18          # age is automatically 'int'
name = "John"     # name is automatically 'str'
height = 5.9      # height is automatically 'float'
is_student = True # is_student is automatically 'bool'

print("Name:", name)
print("Age:", age)
print("Height:", height)
print("Is student:", is_student)

# ===========================================
# You can check the type of any variable
# ===========================================
print("\n--- Type Checking ---")
print("type(age):", type(age))       # <class 'int'>
print("type(name):", type(name))     # <class 'str'>
print("type(height):", type(height))  # <class 'float'>
print("type(is_student):", type(is_student))  # <class 'bool'>

# ===========================================
# Dynamic typing: a variable can change type!
# ===========================================
x = 10
print("\n--- Dynamic Typing ---")
print("x =", x, "-> type:", type(x))

x = "Now I'm a string!"
print("x =", x, "-> type:", type(x))

x = 3.14
print("x =", x, "-> type:", type(x))

# ===========================================
# Multiple assignment
# ===========================================
a, b, c = 1, 2, 3
print("\n--- Multiple Assignment ---")
print("a =", a, "b =", b, "c =", c)

# Same value to multiple variables
x = y = z = 0
print("x =", x, "y =", y, "z =", z)

# ===========================================
# Variable naming rules
# ===========================================
# ✅ Valid names:
my_var = 1
myVar = 2
MY_CONSTANT = 3
my_variable_2 = 4
_camelCase = 5

# ❌ Invalid names (try uncommenting to see errors):
# 2myvar = 1    # Can't START with a number
# my-var = 1    # No hyphens allowed
# my var = 1    # No spaces allowed
# class = 1     # Can't use reserved keywords

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a variable called 'city' with your city name
#   2. Create two variables and swap their values
#   3. Check the type of True/False
# ===========================================
