"""
=============================================
  18 - ADVANCED LOOP PATTERNS
=============================================
  From: quickref.me/python - "Loops" section (extended)
  Nested loops, while/else, and more loop patterns.
=============================================
"""

# ===========================================
# Nested Loops
# ===========================================
print("=== NESTED LOOPS ===")

# Multiplication table (3x3)
print("Multiplication table:")
for i in range(1, 4):
    for j in range(1, 4):
        print(f"  {i} x {j} = {i * j}")
    print()  # Blank line between rows

# Nested loops with lists
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
print("Matrix:")
for row in matrix:
    for value in row:
        print(f"  {value}", end=" ")
    print()  # New line after each row

# ===========================================
# while/else — else runs if NO break occurred
# ===========================================
print("\n=== WHILE/ELSE ===")

# Example 1: Found the value
x = 0
while x < 5:
    print(f"  x = {x}")
    if x == 3:
        print("  Found 3! Breaking...")
        break
    x += 1
else:
    print("  Loop completed without break")
print("  (break happened, so else didn't run)")

print()

# Example 2: Never found, else runs
x = 0
while x < 5:
    print(f"  x = {x}")
    x += 1
else:
    print("  Loop completed without break (else ran)")

# ===========================================
# Looping over different data structures
# ===========================================
print("\n=== LOOPING DATA STRUCTURES ===")

# List of tuples
points = [(1, 2), (3, 4), (5, 6)]
print("Points:")
for x, y in points:  # Tuple unpacking in loop
    print(f"  ({x}, {y})")

# Dictionary with nested values
students = {
    "Alice": {"math": 90, "english": 85},
    "Bob": {"math": 75, "english": 80},
}
print("\nStudents:")
for name, grades in students.items():
    print(f"  {name}:")
    for subject, score in grades.items():
        print(f"    {subject}: {score}")

# enumerate with different start values
print("\nEnumerate examples:")
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits, start=100):
    print(f"  Item #{i}: {fruit}")

# ===========================================
# reversed() — loop backwards
# ===========================================
print("\n=== REVERSED() ===")
colors = ["red", "green", "blue"]
print("Forward:")
for color in colors:
    print(f"  {color}")

print("Backward (reversed):")
for color in reversed(colors):
    print(f"  {color}")

# Numbers reversed
for i in reversed(range(1, 6)):
    print(f"  Countdown: {i}")

# ===========================================
# sorted() — loop in sorted order
# ===========================================
print("\n=== SORTED() ===")
scores = [85, 92, 70, 88, 95]
print("Scores sorted ascending:")
for score in sorted(scores):
    print(f"  {score}")

print("Scores sorted descending:")
for score in sorted(scores, reverse=True):
    print(f"  {score}")

# Sort strings by length
words = ["python", "is", "awesome", "and", "fun"]
for word in sorted(words, key=len):
    print(f"  {word} ({len(word)} chars)")

# ===========================================
# Looping with a step (extended)
# ===========================================
print("\n=== STEP VALUES ===")

# Custom step patterns
print("Even numbers 0-10:")
for i in range(0, 11, 2):
    print(f"  {i}", end=" ")
print()

print("Multiples of 3 (0-30):")
for i in range(0, 31, 3):
    print(f"  {i}", end=" ")
print()

print("Backwards by 2:")
for i in range(10, 0, -2):
    print(f"  {i}", end=" ")
print()

# ===========================================
# TRY IT YOURSELF:
#   1. Create a nested loop that prints a triangle pattern of stars
#   2. Use while/else to search a list for a value
#   3. Loop through a dictionary and find the key with the highest value
# ===========================================
