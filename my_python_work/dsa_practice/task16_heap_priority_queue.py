"""
Task 16: Heap / Priority Queue

A heap is useful when you often need the smallest item first.

Python gives us heapq.

Important idea:
- normal list: keeps items in the order you put them
- sorted list: everything is fully sorted
- heap: not fully sorted, but the smallest item is always easy to get

This is useful for:
- top 3 highest expenses
- cheapest products
- most important tasks
- scores and rankings
"""

import heapq


print("=== BASIC MIN HEAP ===")

numbers = [40, 10, 90, 30, 20]
heapq.heapify(numbers)

print(f"Heap shape: {numbers}")
print(f"Smallest: {heapq.heappop(numbers)}")
print(f"Next smallest: {heapq.heappop(numbers)}")
print(f"Remaining heap: {numbers}")


print("\n=== PUSH NEW ITEMS ===")

scores = []

heapq.heappush(scores, 80)
heapq.heappush(scores, 50)
heapq.heappush(scores, 95)
heapq.heappush(scores, 60)

print(f"Scores heap: {scores}")
print(f"Lowest score: {heapq.heappop(scores)}")


print("\n=== TOP EXPENSES ===")

expenses = [
    {"name": "Lunch", "amount": 120},
    {"name": "Keyboard", "amount": 1800},
    {"name": "Bus", "amount": 40},
    {"name": "Coffee", "amount": 90},
    {"name": "Headphones", "amount": 2200},
]

# nlargest means "give me the biggest N items".
top_three_expenses = heapq.nlargest(
    3,
    expenses,
    key=lambda expense: expense["amount"],
)

for expense in top_three_expenses:
    print(f"{expense['name']}: {expense['amount']} taka")


print("\n=== CHEAPEST PRODUCTS ===")

products = [
    {"name": "keyboard", "price": 1200},
    {"name": "mouse", "price": 500},
    {"name": "notebook", "price": 80},
    {"name": "pen", "price": 20},
    {"name": "headphones", "price": 2200},
]

cheapest_two = heapq.nsmallest(
    2,
    products,
    key=lambda product: product["price"],
)

for product in cheapest_two:
    print(f"{product['name']}: {product['price']} taka")


print("\n=== PRIORITY QUEUE ===")

# Lower priority number means more important.
# Tuple shape:
# (priority, task_name)
tasks = []

heapq.heappush(tasks, (3, "clean old files"))
heapq.heappush(tasks, (1, "pay bill"))
heapq.heappush(tasks, (2, "reply to message"))
heapq.heappush(tasks, (1, "submit assignment"))

while len(tasks) > 0:
    priority, task_name = heapq.heappop(tasks)
    print(f"Priority {priority}: {task_name}")


print("\n=== PRACTICAL EXAMPLE: TOP WORD SCORES ===")

word_scores = [
    {"word": "serene", "score": 85},
    {"word": "algorithm", "score": 98},
    {"word": "variable", "score": 70},
    {"word": "function", "score": 92},
]

best_words = heapq.nlargest(
    2,
    word_scores,
    key=lambda item: item["score"],
)

for item in best_words:
    print(f"{item['word']}: {item['score']}")

"""

This teaches:
- heapq.heapify()
- heappush()
- heappop()
- top expenses with heapq.nlargest()
- cheapest products with heapq.nsmallest()
- priority queue for tasks
Practical meaning: heaps are for “give me the most important / biggest / smallest few things quickly.”

"""


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Make a list of expenses with name and amount.
# 2. Use heapq.nlargest() to show the top 3 expenses.
# 3. Make a list of products with name and price.
# 4. Use heapq.nsmallest() to show the cheapest 2 products.
# 5. Make a priority queue of your own tasks.
