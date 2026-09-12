"""
Task 24: Dynamic Programming Basics

Dynamic programming sounds scary, but the beginner idea is simple:

Remember answers you already solved.

This helps when a problem repeats the same smaller problems.

Two common styles:

1. Memoization:
   recursion + a dictionary cache

2. Tabulation:
   build answers from small to large using a list/table

DP = remember answers to smaller problems so you do not repeat work.
"""


def fibonacci_slow(number):
    if number <= 1:
        return number

    return fibonacci_slow(number - 1) + fibonacci_slow(number - 2)


def fibonacci_memo(number, cache=None):
    if cache is None:
        cache = {}

    if number in cache:
        return cache[number]

    if number <= 1:
        return number

    cache[number] = fibonacci_memo(number - 1, cache) + fibonacci_memo(number - 2, cache)
    return cache[number]


def fibonacci_table(number):
    if number <= 1:
        return number

    table = [0, 1]

    for index in range(2, number + 1):
        next_value = table[index - 1] + table[index - 2]
        table.append(next_value)

    return table[number]


def count_ways_to_climb(stairs):
    if stairs <= 1:
        return 1

    table = [0] * (stairs + 1)
    table[0] = 1
    table[1] = 1

    for step in range(2, stairs + 1):
        table[step] = table[step - 1] + table[step - 2]

    return table[stairs]


def best_value_with_budget(items, budget):
    table = [0] * (budget + 1)

    for item in items:
        cost = item["cost"]
        value = item["value"]

        # Go backward so each item is used at most once.
        for current_budget in range(budget, cost - 1, -1):
            old_value = table[current_budget]
            new_value = table[current_budget - cost] + value
            table[current_budget] = max(old_value, new_value)

    return table[budget]


def can_make_amount(numbers, target):
    table = [False] * (target + 1)
    table[0] = True

    for number in numbers:
        for amount in range(target, number - 1, -1):
            if table[amount - number]:
                table[amount] = True

    return table[target]


print("=== FIBONACCI ===")

number = 10

print(f"Slow recursion: {fibonacci_slow(number)}")
print(f"Memoization:    {fibonacci_memo(number)}")
print(f"Table:          {fibonacci_table(number)}")


print("\n=== COUNT WAYS TO CLIMB STAIRS ===")

# If you can climb 1 or 2 stairs at a time:
# stairs=3 has these ways:
# 1+1+1
# 1+2
# 2+1
for stairs in range(1, 6):
    print(f"{stairs} stairs: {count_ways_to_climb(stairs)} ways")


print("\n=== BEST VALUE WITH BUDGET ===")

study_items = [
    {"name": "Python course", "cost": 500, "value": 90},
    {"name": "Notebook", "cost": 80, "value": 30},
    {"name": "Practice book", "cost": 300, "value": 70},
    {"name": "Sticker pack", "cost": 100, "value": 10},
]

budget = 600
best_value = best_value_with_budget(study_items, budget)

print(f"Best value with {budget} taka: {best_value}")


print("\n=== CAN MAKE AMOUNT ===")

numbers = [3, 5, 9]
target = 8
missing_target = 7

print(f"Can make {target} from {numbers}: {can_make_amount(numbers, target)}")
print(f"Can make {missing_target} from {numbers}: {can_make_amount(numbers, missing_target)}")


print("\n=== GREEDY VS DP IDEA ===")

print("Greedy asks: what looks best right now?")
print("DP asks: what is the best answer after checking smaller possibilities?")


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Try fibonacci_memo(20).
# 2. Try count_ways_to_climb(7).
# 3. Make your own items with cost and value.
# 4. Use best_value_with_budget() with a budget.
# 5. Try can_make_amount() with your own numbers.
