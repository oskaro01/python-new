"""
Task 28: Hash Map, Prefix Sum, and Sliding Window Patterns

This file covers:

1. Two Sum with a hash map
2. Subarray Sum Equals K with prefix sum + hash map
3. Longest substring without repeating characters
4. Minimum window substring
5. Longest subarray with at most K distinct values
"""

from collections import Counter


def two_sum(numbers, target):
    seen = {}

    for index, number in enumerate(numbers):
        needed = target - number

        if needed in seen:
            return [seen[needed], index]

        seen[number] = index

    return None


def subarray_sum_equals_k(numbers, target):
    prefix_counts = {0: 1}
    current_sum = 0
    total_matches = 0

    for number in numbers:
        current_sum = current_sum + number
        needed = current_sum - target
        total_matches = total_matches + prefix_counts.get(needed, 0)
        prefix_counts[current_sum] = prefix_counts.get(current_sum, 0) + 1

    return total_matches


def longest_substring_without_repeating(text):
    last_seen = {}
    left = 0
    best_length = 0
    best_text = ""

    for right, character in enumerate(text):
        if character in last_seen and last_seen[character] >= left:
            left = last_seen[character] + 1

        last_seen[character] = right
        current_length = right - left + 1

        if current_length > best_length:
            best_length = current_length
            best_text = text[left : right + 1]

    return best_length, best_text


def minimum_window_substring(text, required_text):
    if required_text == "":
        return ""

    required_counts = Counter(required_text)
    window_counts = {}
    have = 0
    need = len(required_counts)
    left = 0
    best = None

    for right, character in enumerate(text):
        window_counts[character] = window_counts.get(character, 0) + 1

        if character in required_counts:
            if window_counts[character] == required_counts[character]:
                have = have + 1

        while have == need:
            current_window = text[left : right + 1]

            if best is None or len(current_window) < len(best):
                best = current_window

            left_character = text[left]
            window_counts[left_character] = window_counts[left_character] - 1

            if left_character in required_counts:
                if window_counts[left_character] < required_counts[left_character]:
                    have = have - 1

            left = left + 1

    if best is None:
        return ""

    return best


def longest_subarray_at_most_k_distinct(items, k):
    counts = {}
    left = 0
    best_length = 0
    best_items = []

    for right, item in enumerate(items):
        counts[item] = counts.get(item, 0) + 1

        while len(counts) > k:
            left_item = items[left]
            counts[left_item] = counts[left_item] - 1

            if counts[left_item] == 0:
                del counts[left_item]

            left = left + 1

        current_length = right - left + 1

        if current_length > best_length:
            best_length = current_length
            best_items = items[left : right + 1]

    return best_length, best_items


print("=== TWO SUM ===")

print(two_sum([2, 7, 11, 15], 9))


print("\n=== SUBARRAY SUM EQUALS K ===")

print(subarray_sum_equals_k([1, 1, 1], 2))
print(subarray_sum_equals_k([1, 2, 3], 3))


print("\n=== LONGEST SUBSTRING WITHOUT REPEATING ===")

print(longest_substring_without_repeating("abcabcbb"))


print("\n=== MINIMUM WINDOW SUBSTRING ===")

print(minimum_window_substring("ADOBECODEBANC", "ABC"))


print("\n=== LONGEST SUBARRAY WITH AT MOST K DISTINCT ===")

items = ["food", "food", "tech", "food", "travel", "travel", "food"]
print(longest_subarray_at_most_k_distinct(items, 2))


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Use two_sum() with your own numbers.
# 2. Count subarrays that equal 5.
# 3. Find the longest substring without repeats in "pwwkew".
# 4. Find the minimum window in "aaabcbc" that contains "abc".
# 5. Try at most 2 distinct categories on your own category list.
