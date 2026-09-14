"""
=============================================
  06 - F-STRINGS (Python 3.6+)
=============================================
  From: quickref.me/python
  The modern, preferred way to format strings.
=============================================
"""

# ===========================================
# Basic f-strings
# ===========================================
print("=== BASIC F-STRINGS ===")

website = 'Quickref.ME'
print(f"Hello, {website}")

num = 10
print(f"{num} + 10 = {num + 10}")

name = 'Eric'
age = 27
print(f"Hello!\nI'm {name}.\nI'm {age}.")

# ===========================================
# Expressions inside f-strings
# ===========================================
print("\n=== EXPRESSIONS ===")
print(f"2 + 2 = {2 + 2}")
print(f"Uppercase: {website.upper()}")
print(f"Length of '{website}': {len(website)}")

# ===========================================
# Width and Alignment
# ===========================================
print("\n=== WIDTH & ALIGNMENT ===")
print(f'{"text":10}')        # Right-aligned (default), width 10    print(f'{"test":*>10}')      # Left fill ('*')       => '******test'
    print(f'{"test":*<10}')      # Right fill ('*')      => 'test******'
    print(f'{"test":*^10}')      # Center fill ('*')     => '***test***'
    print(f'{12345:0>10}')       # Pad with zeros (left) => '0000012345'

# ===========================================
# Number Formatting
# ===========================================
print("\n=== NUMBER FORMATTING ===")
print(f'{10:b}')      # Binary:       '1010'
print(f'{10:o}')      # Octal:        '12'
print(f'{255:x}')     # Hex (lower):  'ff'
print(f'{255:X}')     # Hex (upper):  'FF'
print(f'{345600000000:e}')  # Scientific: '3.456000e+11'

# With base notation
print(f'{10:#b}')     # '0b1010'
print(f'{10:#o}')     # '0o12'
print(f'{255:#x}')    # '0xff'

# Character
print(f'Character 65: {65:c}')  # 'A'

# ===========================================
# Precision and Grouping
# ===========================================
print("\n=== PRECISION & GROUPING ===")
import math
print(f"pi = {math.pi}")
print(f"pi to 2 decimals: {math.pi:.2f}")
print(f"pi to 5 decimals: {math.pi:.5f}")

# Comma separator
print(f"{1000000:,}")       # '1,000,000'
print(f"{1000000:,.2f}")    # '1,000,000.00'

# Underscore separator
print(f"{1000000:_}")       # '1_000_000'
print(f"{1000000:_.2f}")    # '1_000_000.00'

# ===========================================
# Percentages
# ===========================================
print("\n=== PERCENTAGES ===")
print(f"{0.25:0%}")   # '25.000000%'
print(f"{0.25:.0%}")  # '25%'
print(f"{1/3:.1%}")   # '33.3%'

# ===========================================
# Signs
# ===========================================
print("\n=== SIGNS ===")
print(f"{12345:+}")      # '+12345'    (always show sign)
print(f"{-12345:+}")     # '-12345'    (negative sign kept)
print(f"{-12345:+10}")   # '    -12345' (right-aligned)
print(f"{-12345:+010}")  # '-000012345' (zero-padded)

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Print your name centered in a 20-char wide field with '=' fill
#   2. Print the number 1234.5678 with 2 decimal places and commas
#   3. Print 0.85 as a percentage
# ===========================================
