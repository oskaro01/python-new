"""
Task 13: Binary Search

Binary search is a faster way to search, but it has one rule:

The list must already be sorted.

Normal search checks items one by one.
Binary search jumps to the middle and removes half the list each step.

Example:
- 1,000 items can take about 10 checks
- 1,000,000 items can take about 20 checks
"""

from bisect import bisect_left, insort
# bisect_left() says where a new item should go.
# insort() inserts it while keeping the list sorted.

def linear_search(items, target):
    for index, item in enumerate(items):
        if item == target:
            return index

    return -1


def binary_search(items, target):
    low = 0
    high = len(items) - 1

    while low <= high:
        middle = (low + high) // 2
        middle_value = items[middle]

        if middle_value == target:
            return middle

        if target > middle_value:
            low = middle + 1
        else:
            high = middle - 1

    return -1


def binary_search_with_steps(items, target):
    low = 0
    high = len(items) - 1
    step = 1

    while low <= high:
        middle = (low + high) // 2
        middle_value = items[middle]

        print(
            f"Step {step}: "
            f"low={low}, middle={middle}, high={high}, "
            f"checking={middle_value}"
        )

        if middle_value == target:
            return middle

        if target > middle_value:
            low = middle + 1
        else:
            high = middle - 1

        step = step + 1

    return -1


print("=== LINEAR SEARCH VS BINARY SEARCH ===")

numbers = [2, 5, 8, 11, 14, 18, 22, 29, 35, 40, 50, 61]
target = 35

print(f"Numbers: {numbers}")
print(f"Target: {target}")
print(f"Linear search index: {linear_search(numbers, target)}")
print(f"Binary search index: {binary_search(numbers, target)}")


print("\n=== BINARY SEARCH STEPS ===")

found_index = binary_search_with_steps(numbers, target)
print(f"Found at index: {found_index}")


print("\n=== WHEN TARGET DOES NOT EXIST ===")

missing_target = 37
missing_index = binary_search_with_steps(numbers, missing_target)
print(f"{missing_target} index: {missing_index}")


print("\n=== PRACTICAL EXAMPLE: SEARCH SORTED WORDS ===")

words = ["algorithm", "bug", "loop", "python", "serene", "variable"]
search_word = "python"

word_index = binary_search(words, search_word)

if word_index == -1:
    print(f"{search_word} was not found.")
else:
    print(f"{search_word} found at index {word_index}.")


print("\n=== PRACTICAL EXAMPLE: DICTIONARY ENTRIES ===")

entries = [
    {"word": "serene", "meaning": "calm and peaceful"},
    {"word": "bug", "meaning": "a mistake in code"},
    {"word": "algorithm", "meaning": "step-by-step problem solving method"},
    {"word": "loop", "meaning": "repeat code"},
]

# Binary search needs sorted data first.
entries = sorted(entries, key=lambda entry: entry["word"])


def binary_search_entry_by_word(entries, target_word):
    low = 0
    high = len(entries) - 1
    target_word = target_word.lower()

    while low <= high:
        middle = (low + high) // 2
        middle_word = entries[middle]["word"].lower()

        if middle_word == target_word:
            return entries[middle]

        if target_word > middle_word:
            low = middle + 1
        else:
            high = middle - 1

    return None


result = binary_search_entry_by_word(entries, "serene")

if result is None:
    print("Word not found.")
else:
    print(f"{result['word']}: {result['meaning']}")


print("\n=== PYTHON'S BUILT-IN HELPER: BISECT ===")

sorted_scores = [40, 55, 70, 85, 95]
new_score = 75

# bisect_left tells us where a value belongs in sorted order.
insert_position = bisect_left(sorted_scores, new_score)
print(f"{new_score} belongs at index {insert_position}")

# insort inserts the value and keeps the list sorted.
insort(sorted_scores, new_score)
print(sorted_scores)


print("\n=== MINI CHALLENGE ===")

# Your task:
# 1. Make a sorted list of prices.
# 2. Search for one price using binary_search().
# 3. Search for one price that does not exist.
# 4. Use bisect_left() to find where a new price should be inserted.
# 5. Use insort() to insert it.
#
# Example:
# prices = [100, 250, 300, 450, 900]
#
# Do it below this line next time.
