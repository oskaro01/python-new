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

print(f"Name: {name} | Age: {age} | Height: {height} | Is student: {is_student}")

# ===========================================
# You can check the type of any variable
# ===========================================
print(f"""type(age):        {type(age)}
type(name):       {type(name)}
type(height):     {type(height)}
type(is_student): {type(is_student)}""")

# ===========================================
# Dynamic typing: a variable can change type!
# ===========================================
x = 10
print(f"x = {x} -> type: {type(x)}")

x = "Now I'm a string!"
print(f"x = {x} -> type: {type(x)}")

x = 3.14
print(f"x = {x} -> type: {type(x)}")

# ===========================================
# Multiple assignment
# ===========================================
a, b, c = 1, 2, 3
print(f"a = {a} | b = {b} | c = {c}")

# Same value to multiple variables
x = y = z = 0
print(f"x = {x} | y = {y} | z = {z}")

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