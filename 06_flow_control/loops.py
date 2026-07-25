"""
=============================================
  17 - LOOPS
=============================================
  From: quickref.me/python
  for loops, while loops, break, continue.
=============================================
"""

# ===========================================
# Basic for Loop
# ===========================================
print("=== BASIC FOR LOOP ===")
primes = [2, 3, 5, 7]
for prime in primes:
    print(f"  Prime: {prime}")

# ===========================================
# Looping with index (enumerate)
# ===========================================
print("\n=== ENUMERATE (WITH INDEX) ===")
animals = ["dog", "cat", "mouse"]
for i, value in enumerate(animals):
    print(f"  Index {i}: {value}")

# Custom start index
for i, value in enumerate(animals, start=1):
    print(f"  Animal #{i}: {value}")

# ===========================================
# range() — generate number sequences
# ===========================================
print("\n=== RANGE ===")
# range(stop)
for i in range(4):
    print(f"  range(4) -> {i}")  # 0, 1, 2, 3

print()
# range(start, stop)
for i in range(4, 8):
    print(f"  range(4,8) -> {i}")  # 4, 5, 6, 7

print()
# range(start, stop, step)
for i in range(4, 10, 2):
    print(f"  range(4,10,2) -> {i}")  # 4, 6, 8

print()
# Backwards with negative step
for i in range(5, 0, -1):
    print(f"  range(5,0,-1) -> {i}")  # 5, 4, 3, 2, 1

# ===========================================
# Looping with zip() — parallel iteration
# ===========================================
print("\n=== ZIP (PARALLEL) ===")
words = ['Mon', 'Tue', 'Wed']
nums = [1, 2, 3]
for w, n in zip(words, nums):
    print(f"  Day {n}: {w}")

# ===========================================
# Looping over a dictionary
# ===========================================
print("\n=== DICT LOOPING ===")
d = {"name": "Alice", "age": 25, "city": "Paris"}
for key in d:
    print(f"  {key}: {d[key]}")

for key, value in d.items():
    print(f"  {key} = {value}")

# ===========================================
# While Loop
# ===========================================
print("\n=== WHILE LOOP ===")
x = 0
while x < 4:
    print(f"  x = {x}")
    x += 1  # Don't forget this, or it'll loop forever!

# ===========================================
# break — exit loop immediately
# ===========================================
print("\n=== BREAK ===")
for index in range(10):
    x = index * 10
    if index == 5:
        break  # Stop the loop when index is 5
    print(f"  index={index}, x={x}")
print("  --- Loop ended via break ---")

# ===========================================
# continue — skip to next iteration
# ===========================================
print("\n=== CONTINUE ===")
for index in range(3, 8):
    x = index * 10
    if index == 5:
        continue  # Skip the rest when index is 5
    print(f"  index={index}, x={x}")
print("  --- Index 5 was skipped ---")

# ===========================================
# for/else — else runs if NO break occurred
# ===========================================
print("\n=== FOR/ELSE ===")
nums = [60, 70, 30, 110, 90]
for n in nums:
    if n > 100:
        print(f"  {n} is bigger than 100 — breaking!")
        break
else:
    print("  Not found!")  # This runs only if NO break happened

# Let's try without a break:
nums = [60, 70, 30, 80, 90]
for n in nums:
    if n > 100:
        print(f"  {n} is bigger than 100 — breaking!")
        break
else:
    print("  All numbers are ≤ 100 (else runs)")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Loop through numbers 1 to 10 and print only the even ones
#   2. Use zip() to pair two lists and print them together
#   3. Write a while loop that counts down from 5 to 1
# ===========================================
