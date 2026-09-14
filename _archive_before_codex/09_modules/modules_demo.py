"""
=============================================
  23 - MODULES
=============================================
  From: quickref.me/python
  Importing and using modules (libraries).
=============================================
"""

# ===========================================
# Import Basics
# ===========================================
print("=== IMPORT BASICS ===")

# Import an entire module
import math
print(f"math.sqrt(16) = {math.sqrt(16)}")  # 4.0
print(f"math.pi = {math.pi}")

# Import specific functions from a module
from math import ceil, floor
print(f"ceil(3.7)  = {ceil(3.7)}")   # 4.0
print(f"floor(3.7) = {floor(3.7)}")  # 3.0

# Import everything (not recommended in production)
from math import *
print(f"sqrt(25)   = {sqrt(25)}")    # 5.0

# Import with alias
import math as m
print(f"m.sqrt(64) = {m.sqrt(64)}")  # 8.0

# Check if they're the same
print(f"Same function? {math.sqrt(16) == m.sqrt(16)}")

# ===========================================
# See what's in a module
# ===========================================
print("\n=== MODULE CONTENTS ===")
print("Functions/attributes in math:")
# dir() lists all names in a module
module_names = [n for n in dir(math) if not n.startswith('_')]
print(f"  {module_names[:10]}...")  # Show first 10

# ===========================================
# Useful built-in modules
# ===========================================
print("\n=== USEFUL BUILT-IN MODULES ===")

# random — for random numbers
import random
print(f"random.randint(1, 10) = {random.randint(1, 10)}")  # Random int
print(f"random.choice(['a','b','c']) = {random.choice(['a','b','c'])}")
print(f"random.shuffle example:")
items = [1, 2, 3, 4, 5]
random.shuffle(items)
print(f"  Shuffled: {items}")

# datetime — for dates and times
from datetime import datetime, timedelta
now = datetime.now()
print(f"\ndatetime.now() = {now}")
print(f"Today's date: {now.strftime('%Y-%m-%d')}")
print(f"Current time: {now.strftime('%H:%M:%S')}")

# os — operating system interface
import os
print(f"\nos.getcwd() = {os.getcwd()}")  # Current working directory

# sys — system-specific parameters
import sys
print(f"\nPython version: {sys.version}")

# json — for JSON data
import json
data = {"name": "Alice", "age": 30}
json_str = json.dumps(data)  # Convert dict to JSON string
print(f"\nJSON string: {json_str}")
parsed = json.loads(json_str)  # Convert JSON string back to dict
print(f"Parsed back: {parsed}")

# re — regular expressions
import re
text = "The rain in Spain"
matches = re.findall(r"\b\w+ain\b", text)  # Words ending with 'ain'
print(f"\nRegex matches in '{text}': {matches}")

# ===========================================
# Creating your own module
# ===========================================
print("\n=== YOUR OWN MODULES ===")
# Any .py file can be imported as a module!
# If you create "mymodule.py" with a function:
#
#   # mymodule.py
#   def greet(name):
#       return f"Hello, {name}!"
#
# Then you can import and use it:
#
#   import mymodule
#   print(mymodule.greet("Alice"))

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Import the 'statistics' module and calculate the mean of [10, 20, 30, 40]
#   2. Use random to pick a random item from your favorite colors list
#   3. Use datetime to print today's date in "Monday, January 1, 2024" format
# ===========================================
