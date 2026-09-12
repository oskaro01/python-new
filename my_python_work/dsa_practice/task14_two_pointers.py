"""
Task 14: Two Pointers

Two pointers means using two positions to scan data.

Common patterns:

1. left and right move toward each other
2. one pointer reads, another pointer writes
3. two pointers walk through two sorted lists

This is useful for:
- checking palindromes
- finding two numbers that make a target
- removing duplicates
- merging sorted data
"""


def is_palindrome(text):
    text = text.lower()
    left = 0
    right = len(text) - 1

    while left < right:
        if text[left] != text[right]:
            return False

        left = left + 1
        right = right - 1

    return True


def two_sum_sorted(numbers, target):
    left = 0
    right = len(numbers) - 1

    while left < right:
        current_sum = numbers[left] + numbers[right]

        if current_sum == target:
            return [numbers[left], numbers[right]]

        if current_sum < target:
            left = left + 1
        else:
            right = right - 1

    return None


def remove_duplicates_sorted(items):
    if len(items) == 0:
        return []

    unique_items = [items[0]]

    for item in items:
        if item != unique_items[-1]:
            unique_items.append(item)

    return unique_items


def merge_sorted_lists(first, second):
    first_index = 0
    second_index = 0
    merged = []

    while first_index < len(first) and second_index < len(second):
        if first[first_index] <= second[second_index]:
            merged.append(first[first_index])
            first_index = first_index + 1
        else:
            merged.append(second[second_index])
            second_index = second_index + 1

    while first_index < len(first):
        merged.append(first[first_index])
        first_index = first_index + 1

    while second_index < len(second):
        merged.append(second[second_index])
        second_index = second_index + 1

    return merged


print("=== PALINDROME CHECK ===")

words = ["level", "python", "radar", "madam"]

for word in words:
    print(f"{word}: {is_palindrome(word)}")


print("\n=== TWO SUM IN SORTED LIST ===")

prices = [50, 100, 200, 350, 500, 900]
target = 700

pair = two_sum_sorted(prices, target)
print(f"Prices: {prices}")
print(f"Target: {target}")
print(f"Pair: {pair}")


print("\n=== REMOVE DUPLICATES FROM SORTED LIST ===")

names = ["ayzal", "ayzal", "jene", "rose", "rose", "zara"]
unique_names = remove_duplicates_sorted(names)

print(f"Original: {names}")
print(f"Unique:   {unique_names}")


print("\n=== MERGE SORTED LISTS ===")

old_scores = [50, 70, 90]
new_scores = [55, 80, 95]
all_scores = merge_sorted_lists(old_scores, new_scores)

print(f"Old scores: {old_scores}")
print(f"New scores: {new_scores}")
print(f"All scores: {all_scores}")


print("\n=== PRACTICAL EXAMPLE: MERGE EXPENSE AMOUNTS ===")

january_amounts = [100, 250, 500]
february_amounts = [80, 300, 450, 900]
combined_amounts = merge_sorted_lists(january_amounts, february_amounts)

print(combined_amounts)

# Why this matters: two pointers is one of those algorithms
# that quietly appears everywhere in real scripts 
# when you compare, clean, or combine data.

print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Make a sorted list of expenses.
# 2. Use two_sum_sorted() to find two expenses that equal a target.
# 3. Make a sorted list with duplicate words.
# 4. Use remove_duplicates_sorted() to clean it.
# 5. Make two sorted lists and merge them.
