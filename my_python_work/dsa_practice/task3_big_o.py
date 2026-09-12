"""
Task 3: Big O basics

Big O means:
How much slower does code get when the input gets bigger?

We do not care about exact seconds first.
We care about the shape:

O(1)      = constant time
O(n)      = linear time
O(n^2)    = nested-loop time
O(log n)  = cutting the problem in half
"""

import time


def search_list(items, target):
    # O(n)
    # In the worst case, Python may check every item one by one.
    return target in items


def search_set(items, target):
    # O(1) average
    # A set is built for very fast "is this inside?" checks.
    return target in items


small_numbers = [1, 2, 3, 4, 5]

print("=== SMALL EXAMPLE ===")
print(search_list(small_numbers, 3))
print(search_list(small_numbers, 99))


print("\n=== LIST VS SET SEARCH ===")

numbers_list = list(range(1_000_000))
numbers_set = set(numbers_list)
target = 999_999

start_time = time.perf_counter()
print(search_list(numbers_list, target))
end_time = time.perf_counter()
print(f"List search took: {end_time - start_time:.8f} seconds")

start_time = time.perf_counter()
print(search_set(numbers_set, target))
end_time = time.perf_counter()
print(f"Set search took:  {end_time - start_time:.8f} seconds")


print("\n=== MINI CHALLENGE ===")

# Your task:
# 1. Change target to a number that does not exist, like 2_000_000.
# 2. Run the file again.
# 3. Notice how list search changes.
# 4. Notice how set search stays very fast.


print("\n=== LIST VS SET SEARCH 2 ===")

numbers_list = list(range(1_000_000))
numbers_set = set(numbers_list)
target = 2_000_000

start_time = time.perf_counter()
print(search_list(numbers_list, target))
end_time = time.perf_counter()
print(f"List search took: {end_time - start_time:.8f} seconds")

start_time = time.perf_counter()
print(search_set(numbers_set, target))
end_time = time.perf_counter()
print(f"Set search took:  {end_time - start_time:.8f} seconds")

print("\n=== CHALLENGE done ===")

# Use list when order matters.
# Use set when you only care “does this exist?”
# Use dict when you want “find value by key.”