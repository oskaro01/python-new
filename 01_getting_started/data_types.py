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
text = "Hello, Python!"
print(f"str:  text = '{text}' -> {type(text)}")

# ===========================================
# NUMERIC TYPES: int, float, complex
# ===========================================
integer_num = 42
float_num = 3.14159
complex_num = 1 + 2j  # 'j' is used instead of 'i' for imaginary

print(f"""integer: {integer_num} -> {type(integer_num)}
float:   {float_num} -> {type(float_num)}
complex: {complex_num} -> {type(complex_num)}  (real: {complex_num.real}, imag: {complex_num.imag})""")

# ===========================================
# SEQUENCE TYPES: list, tuple, range
# ===========================================
my_list = [1, 2, 3, 4, 5]      # Mutable - can be changed
my_tuple = (1, 2, 3, 4, 5)     # Immutable - cannot be changed
my_range = range(1, 6)         # Generates numbers on demand

print(f"""list:   {my_list} -> {type(my_list)}
tuple:  {my_tuple} -> {type(my_tuple)}
range:  {list(my_range)} -> {type(my_range)}""")

# ===========================================
# MAPPING TYPE: dict
# ===========================================
my_dict = {"name": "Alice", "age": 30, "city": "London"}
print(f"dict:  {my_dict} -> {type(my_dict)}")

# ===========================================
# SET TYPES: set, frozenset
# ===========================================
my_set = {1, 2, 3, 3, 2}        # Duplicates are automatically removed!
my_frozenset = frozenset([1, 2, 3, 3, 2])

print(f"""set:        {my_set} -> {type(my_set)}
frozenset:  {my_frozenset} -> {type(my_frozenset)}""")

# ===========================================
# BOOLEAN TYPE: bool
# ===========================================
true_value = True
false_value = False

print(f"""true:    {true_value} -> {type(true_value)}
false:   {false_value} -> {type(false_value)}
bool(0)  = {bool(0)}   |  bool(1)  = {bool(1)}
bool('') = {bool('')}  |  bool('Hi') = {bool('Hi')}""")

# ===========================================
# BINARY TYPES: bytes, bytearray, memoryview
# ===========================================
my_bytes = b"Hello"
my_bytearray = bytearray(b"Hello")
my_memoryview = memoryview(b"Hello")

print(f"""bytes:      {my_bytes} -> {type(my_bytes)}
bytearray:  {my_bytearray} -> {type(my_bytearray)}
memoryview: {my_memoryview} -> {type(my_memoryview)}""")

# ===========================================
# NONE TYPE: NoneType
# ===========================================
nothing = None
print(f"nothing: {nothing} -> {type(nothing)}")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a list with mixed data types (int, str, float)
#   2. Try creating a frozenset from a list with duplicates
#   3. Check: what does bool([]) return? bool([1])?
# ===========================================