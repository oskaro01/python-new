"""
Task 27: Array and String Patterns

This file covers common practical/interview patterns:

1. Rotate array right by K
2. Majority element with Boyer-Moore voting
3. Longest common prefix
4. Product of array except self
"""


def reverse_section(items, left, right):
    while left < right:
        items[left], items[right] = items[right], items[left]
        left = left + 1
        right = right - 1


def rotate_right_in_place(items, k):
    if len(items) == 0:
        return items

    k = k % len(items)

    reverse_section(items, 0, len(items) - 1)
    reverse_section(items, 0, k - 1)
    reverse_section(items, k, len(items) - 1)

    return items


def majority_element(numbers):
    candidate = None
    count = 0

    for number in numbers:
        if count == 0:
            candidate = number

        if number == candidate:
            count = count + 1
        else:
            count = count - 1

    return candidate


def longest_common_prefix(words):
    if len(words) == 0:
        return ""

    prefix = words[0]

    for word in words[1:]:
        while not word.startswith(prefix):
            prefix = prefix[:-1]

            if prefix == "":
                return ""

    return prefix


def product_except_self(numbers):
    result = [1] * len(numbers)

    prefix_product = 1

    for index in range(len(numbers)):
        result[index] = prefix_product
        prefix_product = prefix_product * numbers[index]

    suffix_product = 1

    for index in range(len(numbers) - 1, -1, -1):
        result[index] = result[index] * suffix_product
        suffix_product = suffix_product * numbers[index]

    return result


print("=== ROTATE ARRAY RIGHT BY K ===")

numbers = [1, 2, 3, 4, 5, 6, 7]
rotate_right_in_place(numbers, 3)
print(numbers)


print("\n=== MAJORITY ELEMENT ===")

votes = ["python", "js", "python", "python", "go"]
print(majority_element(votes))


print("\n=== LONGEST COMMON PREFIX ===")

words = ["flower", "flow", "flight"]
print(longest_common_prefix(words))

dictionary_words = ["program", "progress", "project"]
print(longest_common_prefix(dictionary_words))


print("\n=== PRODUCT EXCEPT SELF ===")

values = [1, 2, 3, 4]
print(product_except_self(values))


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Rotate [10, 20, 30, 40, 50] by 2.
# 2. Find the majority element in [1, 2, 1, 1, 3].
# 3. Find the common prefix of ["interview", "internet", "internal"].
# 4. Run product_except_self() on [2, 3, 4].
