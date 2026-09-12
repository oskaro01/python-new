"""
Task 12: CSV Expense Reader

CSV means Comma-Separated Values.

CSV files are very common in real life:
- expenses
- products
- reports
- exported spreadsheets

In this lesson, we will:
1. read a CSV file
2. convert amount from text to int
3. filter expenses
4. sort expenses
5. total by category
"""

import csv


filename = "my_python_work/dsa_practice/expenses.csv"


def read_expenses(filename):
    expenses = []

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            expense = {
                "name": row["name"],
                "category": row["category"],
                "amount": int(row["amount"]),
            }

            expenses.append(expense)

    return expenses


def show_expenses(expenses):
    for expense in expenses:
        print(
            f"{expense['name']} | "
            f"{expense['category']} | "
            f"{expense['amount']} taka"
        )


expenses = read_expenses(filename)


print("=== ALL EXPENSES ===")
show_expenses(expenses)


print("\n=== FOOD EXPENSES ===")

food_expenses = []

for expense in expenses:
    if expense["category"] == "food":
        food_expenses.append(expense)

show_expenses(food_expenses)


print("\n=== HIGHEST TO LOWEST ===")

highest_to_lowest = sorted(
    expenses,
    key=lambda expense: expense["amount"],
    reverse=True,
)

show_expenses(highest_to_lowest)


print("\n=== TOTAL BY CATEGORY ===")

total_by_category = {}

for expense in expenses:
    category = expense["category"]
    amount = expense["amount"]

    if category in total_by_category:
        total_by_category[category] = total_by_category[category] + amount
    else:
        total_by_category[category] = amount

print(total_by_category)


print("\n=== MINI CHALLENGE ===")

# Your task:
# 1. Add 3 more rows to expenses.csv.
# 2. Run this file again.
# 3. Add a section that prints only expenses above 100 taka.
# 4. Add a section that prints the total amount spent overall.
