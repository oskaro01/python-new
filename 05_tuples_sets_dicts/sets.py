"""
=============================================
  14 - SETS
=============================================
  From: quickref.me/python
  Sets store UNIQUE items (no duplicates).
=============================================
"""

# ===========================================
# Creating Sets
# ===========================================
print("=== CREATING SETS ===")

set1 = {"a", "b", "c"}
print(f"set1 = {set1}")

# Using set() constructor
set2 = set(("a", "b", "c"))
print(f"set2 = {set2}")

# Empty set (note: {} creates an empty dict, not set!)
empty_set = set()
empty_dict = {}
print(f"empty_set  = {empty_set}  -> type: {type(empty_set)}")
print(f"empty_dict = {empty_dict} -> type: {type(empty_dict)}")

# ===========================================
# Key Feature: No Duplicates
# ===========================================
print("\n=== NO DUPLICATES ===")
numbers = {1, 2, 2, 3, 3, 3, 4, 4, 4, 4}
print(f"Set from duplicates: {numbers}")  # {1, 2, 3, 4}

# Great for removing duplicates from a list:
my_list = [1, 2, 2, 3, 3, 3, 4, 1]
unique_items = list(set(my_list))
print(f"Original list: {my_list}")
print(f"After set+list: {unique_items}")

# ===========================================
# Set Operations
# ===========================================
print("\n=== SET OPERATIONS ===")
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print(f"Set A: {a}")
print(f"Set B: {b}")

# Union — all items from both sets
print(f"A | B (union):        {a | b}")

# Intersection — items in BOTH sets
print(f"A & B (intersection): {a & b}")

# Difference — items in A but NOT in B
print(f"A - B (difference):   {a - b}")
print(f"B - A (difference):   {b - a}")

# Symmetric difference — items in EITHER set but not both
print(f"A ^ B (symmetric):    {a ^ b}")

# ===========================================
# Adding and Removing
# ===========================================
print("\n=== ADDING & REMOVING ===")
fruits = {"apple", "banana", "cherry"}
print(f"Original: {fruits}")

fruits.add("orange")  # Add one item
print(f"After add('orange'): {fruits}")

fruits.update(["grape", "mango"])  # Add multiple items
print(f"After update(): {fruits}")

fruits.remove("banana")  # Remove (raises error if not found)
print(f"After remove('banana'): {fruits}")

fruits.discard("kiwi")  # Remove if exists (NO error if not found)
print(f"After discard('kiwi'): {fruits}")

popped = fruits.pop()  # Remove and return an arbitrary item
print(f"pop() returned: '{popped}', remaining: {fruits}")

# ===========================================
# Checking Membership (sets are super fast!)
# ===========================================
print("\n=== MEMBERSHIP ===")
print(f"Is 'apple' in fruits?: {'apple' in fruits}")
print(f"Is 'kiwi' in fruits?: {'kiwi' in fruits}")

# ===========================================
# Frozen Set (immutable version of set)
# ===========================================
print("\n=== FROZEN SET ===")
fs = frozenset([1, 2, 3, 3, 2])
print(f"frozenset: {fs}")

# frozensets can be used as dictionary keys (sets cannot)
# fs.add(4)  # Would raise AttributeError

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Find the unique letters in "mississippi"
#   2. Create two sets and find their intersection
#   3. Check if 'x' is in your set using 'in'
# ===========================================
