"""
Task 10: Sorting With Custom Keys

Sorting means putting things in order.

Python gives us two common tools:

1. sorted(items)   -> returns a new sorted list
2. items.sort()    -> changes the original list

The most powerful idea:
key=...

key tells Python what to sort by.
"""


print("=== BASIC SORTING ===")

numbers = [5, 2, 9, 1, 7]

sorted_numbers = sorted(numbers)

print(f"Original numbers: {numbers}")
print(f"Sorted numbers:   {sorted_numbers}")


print("\n=== REVERSE SORTING ===")

high_to_low = sorted(numbers, reverse=True)

print(f"High to low: {high_to_low}")


print("\n=== SORT STRINGS ===")

names = ["ayzal", "jene", "rose", "diagdigan"]

print(sorted(names))


print("\n=== SORT BY LENGTH ===")

words = ["python", "js", "javascript", "go", "typescript"]

# key=len means:
# sort using the length of each word.
short_to_long = sorted(words, key=len)
long_to_short = sorted(words, key=len, reverse=True)

print(f"Short to long: {short_to_long}")
print(f"Long to short: {long_to_short}")


print("\n=== SORT DICTIONARIES ===")

students = [
    {"name": "Ayzal", "score": 88},
    {"name": "Jene", "score": 95},
    {"name": "Rose", "score": 72},
]


def get_score(student):
    return student["score"]


# key=get_score means:
# for each student dictionary, use its score for sorting.
students_by_score = sorted(students, key=get_score)

print(students_by_score)


print("\n=== SORT DICTIONARIES WITH LAMBDA ===")

# lambda is a tiny one-line function.
# This means the same thing as get_score above.
students_high_to_low = sorted(
    students,
    key=lambda student: student["score"],
    reverse=True,
)

print(students_high_to_low)


print("\n=== PRACTICAL EXAMPLE: PERSONAL DICTIONARY WORDS ===")

entries = [
    {"word": "serene", "meaning": "calm and peaceful"},
    {"word": "algorithm", "meaning": "step-by-step problem solving method"},
    {"word": "bug", "meaning": "a mistake in code"},
]

entries_by_word = sorted(entries, key=lambda entry: entry["word"])
entries_by_word_length = sorted(entries, key=lambda entry: len(entry["word"]))

print("Sorted alphabetically:")

for entry in entries_by_word:
    print(entry["word"])

print("Sorted by word length:")

for entry in entries_by_word_length:
    print(entry["word"])


print("\n=== MINI CHALLENGE ===")

# Your task:
# 1. Make a list of products.
# 2. Each product should be a dictionary with "name" and "price".
# 3. Sort products from cheapest to most expensive.
# 4. Sort products from most expensive to cheapest.
# 5. Print both results.
#
# Example product:
# {"name": "keyboard", "price": 1200}
#
# Do it below this line next time.
