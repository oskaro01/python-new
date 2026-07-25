"""
=============================================
  04 - STRING BASICS
=============================================
  From: quickref.me/python
  Strings are sequences of characters.
=============================================
"""

# ===========================================
# Creating strings
# ===========================================
print("=== CREATING STRINGS ===")

# Single quotes
hello1 = 'Hello, World!'
print(f"Single quotes: {hello1}")

# Double quotes (most common)
hello2 = "Hello, World!"
print(f"Double quotes: {hello2}")

# Triple quotes (multi-line strings)
multi_string = """Multiline Strings
Lorem ipsum dolor sit amet,
consectetur adipiscing elit"""
print(f"\nTriple quotes (multi-line):\n{multi_string}")

# ===========================================
# Accessing characters (like arrays)
# ===========================================
print("\n=== ACCESSING CHARACTERS ===")
hello = "Hello, World"
print(f"String: '{hello}'")
print(f"Index  0: '{hello[0]}'")   # First character
print(f"Index  1: '{hello[1]}'")   # 'e'
print(f"Index -1: '{hello[-1]}'")  # Last character ('d')

# ===========================================
# Looping through a string
# ===========================================
print("\n=== LOOPING THROUGH CHARACTERS ===")
for char in "foo":
    print(f"  '{char}'")

# ===========================================
# Common string operations
# ===========================================
print("\n=== COMMON OPERATIONS ===")

text = "Hello, World!"
print(f"Original: '{text}'")
print(f"Length (len): {len(text)}")  # 13

# Check if substring exists
print(f"'World' in text: {'World' in text}")     # True
print(f"'Python' not in text: {'Python' not in text}")  # True

# Concatenation
s1 = "spam"
s2 = "egg"
print(f"Concatenation: '{s1 + s2}'")        # 'spamegg'
print(f"Adjacent literals: {'spam' 'egg'}")  # 'spamegg'

# Repetition
print(f"Repetition: {'===+' * 8}")

# Case conversion
print(f"Upper: '{text.upper()}'")
print(f"Lower: '{text.lower()}'")
print(f"Title: '{text.title()}'")
print(f"Capitalize: '{text.capitalize()}'")

# Checking
print(f"endswith('!'): {text.endswith('!')}")  # True
print(f"startswith('He'): {text.startswith('He')}")  # True

# Searching
print(f"find('World'): {text.find('World')}")  # 7 (index where 'World' starts)
print(f"count('l'): {text.count('l')}")        # 3

# Joining
words = ["John", "Peter", "Vicky"]
print(f"Join with '#': {'#'.join(words)}")  # 'John#Peter#Vicky'

# Splitting
csv = "apple,banana,cherry"
print(f"Split on ',': {csv.split(',')}")  # ['apple', 'banana', 'cherry']

# Stripping whitespace
messy = "  Hello, World!  \n"
print(f"Strip: '{messy.strip()}'")
print(f"Left strip: '{messy.lstrip()}'")
print(f"Right strip: '{messy.rstrip()}'")

# Replacing
print(f"Replace: '{text.replace('World', 'Python')}'")

# ===========================================
# Getting user input
# ===========================================
print("\n=== USER INPUT ===")
# Uncomment to try:
# name = input("Enter your name: ")
# print(f"Hello, {name}!")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a string with your full name and print the length
#   2. Use split() to break a sentence into words
#   3. Use ".join()" to combine a list back into a string
# ===========================================
