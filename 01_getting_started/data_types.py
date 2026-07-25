"""
=============================================
  03 - PYTHON DATA TYPES
=============================================
  From: quickref.me/python
  Covers all the built-in data types with examples.
=============================================
"""

# ===========================================
# TEXT TYPE: str
# ===========================================
print("=== STRING (str) ===")
text = "Hello, Python!"
print(f"text = '{text}' -> type: {type(text)}")

# ===========================================
# NUMERIC TYPES: int, float, complex
# ===========================================
print("\n=== NUMERIC TYPES ===")
integer_num = 42
float_num = 3.14159
complex_num = 1 + 2j  # 'j' is used instead of 'i' for imaginary

print(f"integer = {integer_num} -> type: {type(integer_num)}")
print(f"float   = {float_num} -> type: {type(float_num)}")
print(f"complex = {complex_num} -> type: {type(complex_num)}")
print(f"Real part: {complex_num.real}, Imaginary part: {complex_num.imag}")

# ===========================================
# SEQUENCE TYPES: list, tuple, range
# ===========================================
print("\n=== SEQUENCE TYPES ===")
my_list = [1, 2, 3, 4, 5]        # Mutable - can be changed
my_tuple = (1, 2, 3, 4, 5)       # Immutable - cannot be changed
my_range = range(1, 6)            # Generates numbers on demand

print(f"list   = {my_list} -> type: {type(my_list)}")
print(f"tuple  = {my_tuple} -> type: {type(my_tuple)}")
print(f"range  = {list(my_range)} -> type: {type(my_range)}")

# ===========================================
# MAPPING TYPE: dict
# ===========================================
print("\n=== MAPPING TYPE (dict) ===")
my_dict = {"name": "Alice", "age": 30, "city": "London"}
print(f"dict   = {my_dict} -> type: {type(my_dict)}")
print(f"Name: {my_dict['name']}")

# ===========================================
# SET TYPES: set, frozenset
# ===========================================
print("\n=== SET TYPES ===")
my_set = {1, 2, 3, 3, 2}  # Duplicates are automatically removed!
my_frozenset = frozenset([1, 2, 3, 3, 2])

print(f"set        = {my_set} -> type: {type(my_set)}")
print(f"frozenset  = {my_frozenset} -> type: {type(my_frozenset)}")

# ===========================================
# BOOLEAN TYPE: bool
# ===========================================
print("\n=== BOOLEAN TYPE ===")
true_value = True
false_value = False

print(f"true  = {true_value} -> type: {type(true_value)}")
print(f"false = {false_value} -> type: {type(false_value)}")
print(f"bool(0) = {bool(0)}")     # False
print(f"bool(1) = {bool(1)}")     # True
print(f"bool('') = {bool('')}")   # False (empty string)
print(f"bool('Hi') = {bool('Hi')}")  # True (non-empty string)

# ===========================================
# BINARY TYPES: bytes, bytearray, memoryview
# ===========================================
print("\n=== BINARY TYPES ===")
my_bytes = b"Hello"
my_bytearray = bytearray(b"Hello")
my_memoryview = memoryview(b"Hello")

print(f"bytes      = {my_bytes} -> type: {type(my_bytes)}")
print(f"bytearray  = {my_bytearray} -> type: {type(my_bytearray)}")
print(f"memoryview = {my_memoryview} -> type: {type(my_memoryview)}")

# ===========================================
# NONE TYPE: NoneType
# ===========================================
print("\n=== NONE TYPE ===")
nothing = None
print(f"nothing = {nothing} -> type: {type(nothing)}")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a list with mixed data types (int, str, float)
#   2. Try creating a frozenset from a list with duplicates
#   3. Check: what does bool([]) return? bool([1])?
# ===========================================
