"""
Task 15: Sliding Window

Sliding window means looking at a small section of data,
then moving that section one step at a time.

It is useful when you need:
- highest spending over 3 days
- average of the last 7 days
- longest streak
- best score in a moving range

The window is the current chunk.
"""


def highest_window_sum(numbers, window_size):
    if window_size <= 0 or window_size > len(numbers):
        return None

    current_sum = 0

    for index in range(window_size):
        current_sum = current_sum + numbers[index]

    best_sum = current_sum

    for right_index in range(window_size, len(numbers)):
        left_index = right_index - window_size
        current_sum = current_sum - numbers[left_index]
        current_sum = current_sum + numbers[right_index]

        if current_sum > best_sum:
            best_sum = current_sum

    return best_sum


def highest_window_sum_with_days(expenses, window_size):
    if window_size <= 0 or window_size > len(expenses):
        return None

    current_sum = 0

    for index in range(window_size):
        current_sum = current_sum + expenses[index]["amount"]

    best_sum = current_sum
    best_start_index = 0

    for right_index in range(window_size, len(expenses)):
        left_index = right_index - window_size
        current_sum = current_sum - expenses[left_index]["amount"]
        current_sum = current_sum + expenses[right_index]["amount"]

        if current_sum > best_sum:
            best_sum = current_sum
            best_start_index = left_index + 1

    best_window = expenses[best_start_index : best_start_index + window_size]

    return {
        "total": best_sum,
        "days": best_window,
    }


def moving_average(numbers, window_size):
    if window_size <= 0 or window_size > len(numbers):
        return []

    averages = []
    current_sum = 0

    for index in range(window_size):
        current_sum = current_sum + numbers[index]

    averages.append(current_sum / window_size)

    for right_index in range(window_size, len(numbers)):
        left_index = right_index - window_size
        current_sum = current_sum - numbers[left_index]
        current_sum = current_sum + numbers[right_index]
        averages.append(current_sum / window_size)

    return averages


def longest_streak_at_least(numbers, minimum):
    best_streak = 0
    current_streak = 0

    for number in numbers:
        if number >= minimum:
            current_streak = current_streak + 1

            if current_streak > best_streak:
                best_streak = current_streak
        else:
            current_streak = 0

    return best_streak


print("=== HIGHEST WINDOW SUM ===")

daily_spending = [100, 250, 80, 400, 120, 90, 300]
best_three_day_total = highest_window_sum(daily_spending, 3)

print(f"Daily spending: {daily_spending}")
print(f"Highest 3-day total: {best_three_day_total}")


print("\n=== MOVING AVERAGE ===")

temperatures = [30, 31, 33, 35, 34, 32, 31]
three_day_averages = moving_average(temperatures, 3)

print(f"Temperatures: {temperatures}")
print(f"3-day averages: {three_day_averages}")


print("\n=== PRACTICAL EXAMPLE: EXPENSE DAYS ===")

expenses = [
    {"date": "2026-09-01", "amount": 100},
    {"date": "2026-09-02", "amount": 250},
    {"date": "2026-09-03", "amount": 80},
    {"date": "2026-09-04", "amount": 400},
    {"date": "2026-09-05", "amount": 120},
    {"date": "2026-09-06", "amount": 90},
    {"date": "2026-09-07", "amount": 300},
]

best_result = highest_window_sum_with_days(expenses, 3)

print(f"Highest 3-day expense total: {best_result['total']}")
print("Days:")

for expense in best_result["days"]:
    print(f"{expense['date']}: {expense['amount']} taka")


print("\n=== LONGEST STREAK ===")

study_minutes = [20, 45, 60, 15, 40, 50, 55, 10]
best_study_streak = longest_streak_at_least(study_minutes, 40)

print(f"Study minutes: {study_minutes}")
print(f"Longest streak of at least 40 minutes: {best_study_streak}")

"""
 This teaches:
- highest total in a moving window
- moving averages
- highest 3-day expense period
- longest streak above a minimum
This one is very practical for expenses, habits, study tracking, sales, activity logs, and “last N days” style scripts.

"""

print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Make a list of daily expenses.
# 2. Find the highest 4-day spending total.
# 3. Make a list of daily study minutes.
# 4. Find the longest streak where you studied at least 30 minutes.
# 5. Try changing the window size and see how the result changes.
