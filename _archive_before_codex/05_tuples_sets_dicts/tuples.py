"""
=============================================
  13 - TUPLES
=============================================
  From: quickref.me/python
  Tuples are like lists but IMMUTABLE
  (cannot be changed after creation).
=============================================
"""

# ===========================================
# Creating Tuples
# ===========================================
print("=== CREATING TUPLES ===")

tuple1 = (1, 2, 3)
print(f"tuple1 = {tuple1}")

# Using tuple() constructor
tuple2 = tuple((1, 2, 3))
print(f"tuple2 = {tuple2}")

# Single element tuple (note the comma!)
single = (5,)  # Without the comma, it's just an int
not_a_tuple = (5)

print(f"single     = {single}  -> type: {type(single)}")
print(f"not_a_tuple = {not_a_tuple} -> type: {type(not_a_tuple)}")

# Empty tuple
empty = ()
print(f"empty = {empty}  -> type: {type(empty)}")

# ===========================================
# Tuple vs List — Key Difference
# ===========================================
print("\n=== TUPLE vs LIST ===")

my_list = [1, 2, 3]
my_tuple = (1, 2, 3)

print(f"List:  {my_list} — mutable (can change)")
print(f"Tuple: {my_tuple} — immutable (cannot change)")

# Lists can be modified:
my_list[0] = 99
print(f"List after modification: {my_list}")

# Tuples CANNOT be modified:
# my_tuple[0] = 99  # TypeError: 'tuple' object does not support item assignment

# ===========================================
# Tuple Operations (same as lists fro reading)
# ===========================================
print("\n=== TUPLE OPERATIONS ===")
t = (10, 20, 30, 40, 50)
print(f"Tuple: {t}")
print(f"t[0]      = {t[0]}")        # Access by index
print(f"t[-1]     = {t[-1]}")       # Last element
print(f"t[1:4]    = {t[1:4]}")      # Slicing
print(f"len(t)    = {len(t)}")      # Length
print(f"20 in t   = {20 in t}")     # Membership test

# Concatenation
t1 = (1, 2, 3)
t2 = (4, 5, 6)
print(f"Concatenated: {t1 + t2}")

# Repetition
print(f"Repeated: {t1 * 2}")

# ===========================================
# Why use tuples?
# ===========================================
print("\n=== WHY USE TUPLES? ===")
# 1. They are faster than lists
# 2. Data safety (can't accidentally modify)
# 3. Can be used as dictionary keys (lists can't!)
lookup = {(0, 0): "origin", (1, 2): "point A"}
print(f"Dict with tuple keys: {lookup}")

# 4. Unpacking (tuples are often used for multiple returns)
def min_max(items):
    return min(items), max(items)  # Returns a tuple

result = min_max([3, 1, 7, 2, 9])
print(f"min_max result: {result} (type: {type(result)})")

# ===========================================
# Tuple Unpacking
# ===========================================
print("\n=== TUPLE UNPACKING ===")
point = (3, 4)
x, y = point  # Unpack tuple into variables
print(f"point = {point}")
print(f"x = {x}, y = {y}")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a tuple with your name, age, and city
#   2. Try to change one element — what error do you get?
#   3. Unpack a tuple of 3 values into separate variables
# ===========================================
