"""
=============================================
  07 - OLD STRING FORMATTING STYLES
=============================================
  From: quickref.me/python
  Older formatting styles you'll encounter in
  existing code. Use f-strings for new code!
=============================================
"""

# ===========================================
# %-formatting (old style - like C printf)
# ===========================================
print("=== %-FORMATTING ===")
name = "John"
age = 23

# %s = string, %d = integer, %f = float
print("Hello, %s!" % name)
print("%s is %d years old." % (name, age))
print("Pi is approximately %.2f" % 3.14159)  # .2f = 2 decimal places

# ===========================================
# .format() Method (Python 3+)
# ===========================================
print("\n=== .format() METHOD ===")

# Positional arguments
txt1 = "My name is {0}, I'm {1}".format("John", 36)
print(txt1)

# Keyword arguments
txt2 = "My name is {fname}, I'm {age}".format(fname="John", age=36)
print(txt2)

# Implicit order
txt3 = "My name is {}, I'm {}".format("John", 36)
print(txt3)

# Format specifiers with .format()
print("\n--- Format Specifiers ---")
print("{:.2f}".format(3.14159))    # 2 decimal places: '3.14'
print("{:,}".format(1000000))      # comma separator: '1,000,000'
print("{:<10}".format("left"))     # left align
print("{:>10}".format("right"))    # right align
print("{:^10}".format("center"))   # center

# ===========================================
# 🧪 Which one should YOU use?
# ===========================================
# [OK] F-strings (f"...")  =  BEST for Python 3.6+
# [OK] .format()           =  Good for Python 3+
# [NO] %-formatting        =  Legacy (avoid in new code)

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Use %-formatting to print "My name is X, I'm Y years old"
#   2. Use .format() to format pi to 3 decimal places
#   3. Try .format() with named placeholders
# ===========================================
