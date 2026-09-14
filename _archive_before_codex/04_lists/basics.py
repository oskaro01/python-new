"""
=============================================
  10 - LISTS - BASICS
=============================================
  From: quickref.me/python
  Lists are ordered, mutable collections.
=============================================
"""

# ===========================================
# Creating Lists
# ===========================================
print("=== CREATING LISTS ===")

# Empty list
li1 = []
print(f"Empty list: {li1}")

# With values
li2 = [4, 5, 6]
print(f"[4, 5, 6]: {li2}")

# From a tuple
li3 = list((1, 2, 3))
print(f"list((1,2,3)): {li3}")

# From range
li4 = list(range(1, 11))
print(f"list(range(1,11)): {li4}")

# Mixed types
mixed = [1, "hello", 3.14, True]
print(f"Mixed types: {mixed}")

# ===========================================
# Accessing Elements
# ===========================================
print("\n=== ACCESSING ELEMENTS ===")
li = ['a', 'b', 'c', 'd']
print(f"List: {li}")
print(f"li[0]  = '{li[0]}'")    # First element
print(f"li[-1] = '{li[-1]}'")   # Last element
print(f"li[-2] = '{li[-2]}'")   # Second to last

# IndexError if out of range
# print(li[4])  # Would raise: IndexError: list index out of range

# ===========================================
# Adding Elements
# ===========================================
print("\n=== ADDING ELEMENTS ===")
li = []
li.append(1)   # Add to the end
li.append(2)
li.append(4)
li.append(3)

print(f"After appending: {li}")

# Insert at specific position
li.insert(0, 0)  # Insert 0 at index 0
print(f"After insert(0, 0): {li}")

# ===========================================
# Removing Elements
# ===========================================
print("\n=== REMOVING ELEMENTS ===")
li = ['bread', 'butter', 'milk']
print(f"Original: {li}")

popped = li.pop()  # Remove and return last item
print(f"pop()    => removed '{popped}', remaining: {li}")

del li[0]  # Delete by index
print(f"del li[0] => remaining: {li}")

# Remove specific value
li = ['a', 'b', 'c', 'b']
li.remove('b')  # Removes the FIRST occurrence
print(f"remove('b'): {li}")

# Clear all elements
li.clear()
print(f"clear(): {li}")

# ===========================================
# Concatenating Lists
# ===========================================
print("\n=== CONCATENATING ===")
odd = [1, 3, 5]

# Using extend()
odd.extend([9, 11, 13])
print(f"Using extend(): {odd}")

# Using + (creates a new list)
odd = [1, 3, 5]
result = odd + [9, 11, 13]
print(f"Using +: {result}")
print(f"Original unchanged: {odd}")

# Repeating
repeated = ["re"] * 3
print(f"Repeated ['re'] * 3: {repeated}")

# ===========================================
# Sorting & Reversing
# ===========================================
print("\n=== SORTING & REVERSING ===")
li = [3, 1, 3, 2, 5]
print(f"Original: {li}")

li.sort()  # Sort in-place (ascending)
print(f"sort(): {li}")

li.reverse()  # Reverse in-place
print(f"reverse(): {li}")

# ===========================================
# Other Useful Methods
# ===========================================
print("\n=== OTHER METHODS ===")
li = [3, 1, 3, 2, 5, 3]
print(f"List: {li}")
print(f"count(3): {li.count(3)}")  # How many times 3 appears
print(f"index(2): {li.index(2)}")  # Index of first occurrence of 2

# Check if element exists
print(f"Is 3 in list?: {3 in li}")
print(f"Is 99 in list?: {99 in li}")

# Length
print(f"len(list): {len(li)}")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a list of your 5 favorite foods
#   2. Add one more, remove the third item
#   3. Sort the list alphabetically
# ===========================================
