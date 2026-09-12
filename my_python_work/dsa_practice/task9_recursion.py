"""
Task 9: Recursion

Recursion means:
A function calls itself.

Every recursive function needs:
1. Base case    -> when to stop
2. Recursive case -> when to call itself again

If there is no base case, recursion never stops.
"""


print("=== COUNTDOWN ===")


def countdown(number):
    # Base case:
    # Stop when number reaches 0.
    if number == 0:
        print("Done")
        return

    print(number)

    # Recursive case:
    # Call the same function with a smaller number.
    countdown(number - 1)


countdown(5)


print("\n=== FACTORIAL ===")


def factorial(number):
    # factorial(1) is 1.
    # This is the base case.
    if number == 1:
        return 1

    # Example:
    # factorial(5) = 5 * factorial(4)
    return number * factorial(number - 1)


print(factorial(5))


print("\n=== SUM OF LIST ===")


def sum_list(numbers):
    # Base case:
    # An empty list has sum 0.
    if len(numbers) == 0:
        return 0

    first_number = numbers[0]
    remaining_numbers = numbers[1:]

    # Add the first number to the sum of the remaining numbers.
    return first_number + sum_list(remaining_numbers)


print(sum_list([10, 20, 30, 40]))


print("\n=== VISUAL RECURSION ===")


def show_recursion(number):
    if number == 0:
        print("Reached base case")
        return

    print(f"Going down: {number}")
    show_recursion(number - 1)
    print(f"Coming back up: {number}")


show_recursion(3)


print("\n=== MINI CHALLENGE ===")

# Your task:
# 1. Write a function called print_numbers(number).
# 2. It should print numbers from number down to 1.
# 3. Use recursion.
# 4. Call print_numbers(5).
#
# Do it below this line next time.
