"""
OOP 04: Abstraction

Abstraction means:

"Give me a simple method to call. I do not need to know every detail inside."

Example:
The outside code calls .build().
Each report decides how .build() works internally.
"""

from abc import ABC, abstractmethod


class Report(ABC):
    @abstractmethod
    def build(self):
        # Any child report must create its own build() method.
        pass


class ExpenseReport(Report):
    def __init__(self, expenses):
        self.expenses = expenses

    def build(self):
        total = 0

        for expense in self.expenses:
            total += expense["amount"]

        return f"Expense report total: {total}"


class WordReport(Report):
    def __init__(self, words):
        self.words = words

    def build(self):
        return f"Dictionary has {len(self.words)} words."


def print_report(report):
    # This function does not care what exact report type it gets.
    # It only cares that the object has a build() method.
    print(report.build())


def main():
    expense_report = ExpenseReport([
        {"name": "Food", "amount": 120},
        {"name": "Book", "amount": 300},
    ])

    word_report = WordReport(["serene", "vivid", "resilient"])

    print("=== ABSTRACTION ===")
    print_report(expense_report)
    print_report(word_report)


if __name__ == "__main__":
    main()

