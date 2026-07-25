"""
=============================================
  09 - TYPE CASTING
=============================================
  From: quickref.me/python
  Converting between different data types.
=============================================
"""

# ===========================================
# Casting to Integer (int)
# ===========================================
print("=== CASTING TO INTEGER ===")
x = int(1)      # From integer     = 1
y = int(2.8)    # From float       = 2  (truncates, doesn't round!)
z = int("3")    # From string      = 3

print(f"int(1)     = {x} (type: {type(x)})")
print(f"int(2.8)   = {y} (type: {type(y)})")
print(f"int('3')   = {z} (type: {type(z)})")

# Note: int() truncates toward zero
print(f"\nint(3.9)   = {int(3.9)}")   # 3
print(f"int(-3.9)  = {int(-3.9)}")    # -3

# ===========================================
# Casting to Float (float)
# ===========================================
print("\n=== CASTING TO FLOAT ===")
x = float(1)      # From integer     = 1.0
y = float(2.8)    # From float       = 2.8
z = float("3")    # From string      = 3.0
w = float("4.2")  # From string      = 4.2

print(f"float(1)     = {x}")
print(f"float(2.8)   = {y}")
print(f"float('3')   = {z}")
print(f"float('4.2') = {w}")

# ===========================================
# Casting to String (str)
# ===========================================
print("\n=== CASTING TO STRING ===")
x = str("s1")     # From string      = 's1'
y = str(2)        # From integer     = '2'
z = str(3.0)      # From float       = '3.0'

print(f"str('s1')  = '{x}'")
print(f"str(2)     = '{y}'")
print(f"str(3.0)   = '{z}'")

# ===========================================
# Casting to Boolean (bool)
# ===========================================
print("\n=== CASTING TO BOOLEAN ===")
# Falsy values (evaluate to False):
print(f"bool(0)      = {bool(0)}")
print(f"bool(0.0)    = {bool(0.0)}")
print(f"bool('')     = {bool('')}")
print(f"bool([])     = {bool([])}")
print(f"bool(None)   = {bool(None)}")

# Truthy values (everything else):
print(f"\nbool(1)      = {bool(1)}")
print(f"bool(-1)     = {bool(-1)}")
print(f"bool('Hi')   = {bool('Hi')}")
print(f"bool([0])    = {bool([0])}")  # non-empty list

# ===========================================
# Casting to List (list) from other sequences
# ===========================================
print("\n=== CASTING TO LIST ===")
print(f"list('hello') = {list('hello')}")     # ['h','e','l','l','o']
print(f"list((1,2,3)) = {list((1,2,3))}")     # [1,2,3]
print(f"list(range(5)) = {list(range(5))}")    # [0,1,2,3,4]

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Convert your age (as a string) to an integer
#   2. What happens with int("3.14") — will it work?
#   3. Convert a list to a string using str()
# ===========================================
