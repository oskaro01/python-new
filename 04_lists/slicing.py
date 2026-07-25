"""
=============================================
  11 - LIST SLICING
=============================================
  From: quickref.me/python
  Same slicing syntax as strings: [start:stop:step]
=============================================
"""

# ===========================================
# Basic List Slicing
# ===========================================
a = ['spam', 'egg', 'bacon', 'tomato', 'ham', 'lobster']
print(f"Original list: {a}")
print(f"length: {len(a)}")

print("\n=== BASIC SLICING ===")
print(f"a[2:5]     = {a[2:5]}")   # ['bacon', 'tomato', 'ham']
print(f"a[-5:-2]   = {a[-5:-2]}") # ['egg', 'bacon', 'tomato']
print(f"a[1:4]     = {a[1:4]}")   # ['egg', 'bacon', 'tomato']

# ===========================================
# Omitting Indices
# ===========================================
print("\n=== OMITTING INDICES ===")
print(f"a[:4]      = {a[:4]}")      # ['spam', 'egg', 'bacon', 'tomato']
print(f"a[0:4]     = {a[0:4]}")     # Same as above
print(f"a[2:]      = {a[2:]}")      # ['bacon', 'tomato', 'ham', 'lobster']
print(f"a[2:len(a)]= {a[2:len(a)]}") # Same as above
print(f"a[:]       = {a[:]}")       # Full copy of the list

# ===========================================
# With a Stride
# ===========================================
print("\n=== WITH STRIDE ===")
print(f"a[0:6:2]   = {a[0:6:2]}")   # ['spam', 'bacon', 'ham'] (every 2nd)
print(f"a[1:6:2]   = {a[1:6:2]}")   # ['egg', 'tomato', 'lobster']
print(f"a[6:0:-2]  = {a[6:0:-2]}")  # ['lobster', 'tomato', 'egg'] (backwards)

# ===========================================
# Reversing with Slicing
# ===========================================
print("\n=== REVERSING ===")
print(f"a[::-1]    = {a[::-1]}")    # Reversed copy!

# ===========================================
# Slicing to Modify Parts of a List
# ===========================================
print("\n=== MODIFYING WITH SLICES ===")
nums = [0, 1, 2, 3, 4, 5]
print(f"Before: {nums}")

nums[1:4] = [10, 20, 30]  # Replace elements at index 1,2,3
print(f"After replacement: {nums}")

nums[1:4] = [100]  # Can replace a slice with a different size
print(f"After replacing 3 elements with 1: {nums}")

# ===========================================
# Visual Index Reference
# ===========================================
# ['spam', 'egg', 'bacon', 'tomato', 'ham', 'lobster']
#    0       1       2        3        4       5
#   -6      -5      -4       -3       -2      -1

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create [10, 20, 30, 40, 50] and get the last 3 elements
#   2. Get every other element from [1,2,3,4,5,6,7,8]
#   3. Reverse the list using slicing
# ===========================================
