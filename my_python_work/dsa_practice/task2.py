"""
Task 2: Turn counting into a function

Goal:
Learn how to use return.

Why this matters:
If you can turn repeated logic into a function,
you can reuse it in bigger scripts and DSA problems.
"""

def count_items(items):
    counts = {}

    for item in items:
        if item in counts:
            counts[item] = counts[item] + 1
        else:
            counts[item] = 1

    return counts


foods = ["apple", "orange", "blue berry", "apple", "mango", "orange", "apple", "grape"]
food_counts = count_items(foods)
print(food_counts)


numbers = [1, 2, 3, 1, 2, 1, 5]
number_counts = count_items(numbers)
print(number_counts)
