"""
=============================================
  19 - FUNCTIONS: *args AND **kwargs
=============================================
  From: quickref.me/python
  Functions that accept any number of arguments.
=============================================
"""

# ===========================================
# *args — Variable Positional Arguments
# ===========================================
print("=== *args (POSITIONAL) ===")

def varargs(*args):
    """Accepts any number of positional arguments."""
    print(f"args = {args}  (type: {type(args)})")
    return args

result = varargs(1, 2, 3)
print(f"returned: {result}")

# Practical example: summing any number of values
def sum_all(*numbers):
    """Sum any number of values."""
    total = sum(numbers)
    print(f"Sum of {numbers} = {total}")
    return total

sum_all(1, 2, 3)
sum_all(10, 20, 30, 40, 50)

# ===========================================
# **kwargs — Variable Keyword Arguments
# ===========================================
print("\n=== **kwargs (KEYWORD) ===")

def keyword_args(**kwargs):
    """Accepts any number of keyword arguments."""
    print(f"kwargs = {kwargs}  (type: {type(kwargs)})")
    return kwargs

result = keyword_args(big="foot", loch="ness")
print(f"returned: {result}")

# Practical example: build a profile
def build_profile(**info):
    """Build a user profile from keyword arguments."""
    print("--- User Profile ---")
    for key, value in info.items():
        print(f"  {key}: {value}")
    print("--------------------")
    return info

build_profile(name="Alice", age=30, city="NYC")

# ===========================================
# Mixing Regular Args, *args, and **kwargs
# ===========================================
print("\n=== MIXING ARGUMENTS ===")

def mixed(a, b, *args, **kwargs):
    print(f"a        = {a}")
    print(f"b        = {b}")
    print(f"*args    = {args}")
    print(f"**kwargs = {kwargs}")

mixed(1, 2, 3, 4, 5, name="Alice", age=30)
# Output:
#   a = 1
#   b = 2
#   *args = (3, 4, 5)
#   **kwargs = {'name': 'Alice', 'age': 30}

# ===========================================
# Unpacking Lists/Dicts into Function Args
# ===========================================
print("\n=== UNPACKING INTO FUNCTION CALLS ===")

# Unpacking a list into *args
numbers = [1, 2, 3, 4, 5]
print(f"sum_all with packed list: ", end="")
sum_all(*numbers)  # Same as: sum_all(1, 2, 3, 4, 5)

# Unpacking a dict into **kwargs
def show_info(name, age, city):
    print(f"Name: {name}, Age: {age}, City: {city}")

person = {"name": "Bob", "age": 25, "city": "London"}
show_info(**person)  # Same as: show_info(name="Bob", age=25, city="London")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Write a function that concatenates any number of strings
#   2. Write a function that prints all **kwargs in a formatted way
#   3. Try unpacking a list into a function using *list
# ===========================================
