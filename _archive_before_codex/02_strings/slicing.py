"""
=============================================
  05 - STRING SLICING
=============================================
  From: quickref.me/python
  Extract parts of a string using [start:stop:step].
=============================================
"""

# ===========================================
# String Index Reference
# ===========================================
# String:   m  y  b  a  c  o  n
# Index:    0  1  2  3  4  5  6
# Neg idx: -7 -6 -5 -4 -3 -2 -1

s = "mybacon"
print(f"String: '{s}'")
print(f"Length: {len(s)}")

# ===========================================
# Basic Slicing: string[start:end]
# NOTE: 'end' is EXCLUSIVE (stops before that index)
# ===========================================
print("\n=== BASIC SLICING ===")
print(f"s[2:5]   = '{s[2:5]}'")   # 'bac'  (indices 2,3,4)
print(f"s[0:2]   = '{s[0:2]}'")   # 'my'   (indices 0,1)
print(f"s[-5:-1] = '{s[-5:-1]}'") # 'baco' (negative indices)

# ===========================================
# Omitting Indices
# ===========================================
print("\n=== OMITTING INDICES ===")
print(f"s[:2]  = '{s[:2]}'")      # 'my'    (from start to index 2)
print(f"s[2:]  = '{s[2:]}'")      # 'bacon' (from index 2 to end)
print(f"s[:]   = '{s[:]}'")       # 'mybacon' (the whole string - creates a copy)

# Combining
assert s[:2] + s[2:] == s  # Always True!

# ===========================================
# With a Stride: string[start:stop:step]
# ===========================================
print("\n=== WITH A STRIDE ===")
s2 = "12345" * 5
print(f"String: '{s2}'")
print(f"Length: {len(s2)}")

print(f"s2[::5]   = '{s2[::5]}'")   # '11111'  (every 5th char from start)
print(f"s2[4::5]  = '{s2[4::5]}'")  # '55555' (every 5th char from index 4)
print(f"s2[::-5]  = '{s2[::-5]}'")   # '55555' (every 5th from the right)
print(f"s2[::-1]  = '{s2[::-1]}'")   # Reversed!

# ===========================================
# More step examples
# ===========================================
print("\n=== MORE STEP EXAMPLES ===")
s3 = "Hello, World!"
print(f"String: '{s3}'")

print(f"s3[::2]   = '{s3[::2]}'")   # Every other character
print(f"s3[1::2]  = '{s3[1::2]}'")  # Every other, starting at index 1
print(f"s3[::-1]  = '{s3[::-1]}'")  # Reverse
print(f"s3[7::]   = '{s3[7:]}'")    # Everything after index 7

# ===========================================
# Visual Index Map
# ===========================================
#   ┌───┬───┬───┬───┬───┬───┬───┐
#   | m | y | b | a | c | o | n |
#   └───┴───┴───┴───┴───┴───┴───┘
#   0   1   2   3   4   5   6   7
#  -7  -6  -5  -4  -3  -2  -1
#
# s[2:5] = 'bac'
# s[:2]  = 'my'
# s[2:]  = 'bacon'

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create your name and print the first 3 letters
#   2. Print your name in reverse
#   3. Print every other letter of a long word
#   4. Try s[-3:] - what does it give you?
# ===========================================
