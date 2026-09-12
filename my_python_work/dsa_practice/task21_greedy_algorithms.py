"""
Task 21: Greedy Algorithms

Greedy means:
choose the best-looking option right now,
then keep going.

Greedy is useful when a local best choice leads to a good final result.

Real examples:
- choose maximum meetings without overlap
- buy as many cheap items as possible within a budget
- choose high value items first
- make change with common coin systems

Warning:
Greedy is fast and simple, but it is not always perfect for every problem.
"""


def choose_max_meetings(meetings):
    sorted_meetings = sorted(meetings, key=lambda meeting: meeting["end"])
    chosen_meetings = []
    current_end = 0

    for meeting in sorted_meetings:
        if meeting["start"] >= current_end:
            chosen_meetings.append(meeting)
            current_end = meeting["end"]

    return chosen_meetings


def buy_max_items(products, budget):
    sorted_products = sorted(products, key=lambda product: product["price"])
    bought_items = []
    money_left = budget

    for product in sorted_products:
        if product["price"] <= money_left:
            bought_items.append(product)
            money_left = money_left - product["price"]

    return bought_items, money_left


def make_change(amount, coins):
    coins = sorted(coins, reverse=True)
    result = {}
    remaining = amount

    for coin in coins:
        count = remaining // coin

        if count > 0:
            result[coin] = count
            remaining = remaining - (coin * count)

    return result, remaining


def choose_best_value_items(items, budget):
    sorted_items = sorted(
        items,
        key=lambda item: item["value"] / item["cost"],
        reverse=True,
    )
    chosen_items = []
    money_left = budget

    for item in sorted_items:
        if item["cost"] <= money_left:
            chosen_items.append(item)
            money_left = money_left - item["cost"]

    return chosen_items, money_left


print("=== ACTIVITY SELECTION: MAX MEETINGS ===")

meetings = [
    {"name": "Study", "start": 1, "end": 3},
    {"name": "Workout", "start": 2, "end": 4},
    {"name": "Python", "start": 3, "end": 5},
    {"name": "Dinner", "start": 6, "end": 8},
    {"name": "Reading", "start": 5, "end": 7},
]

chosen_meetings = choose_max_meetings(meetings)

for meeting in chosen_meetings:
    print(f"{meeting['name']}: {meeting['start']} to {meeting['end']}")


print("\n=== BUY MAX ITEMS WITH BUDGET ===")

products = [
    {"name": "keyboard", "price": 1200},
    {"name": "mouse", "price": 500},
    {"name": "notebook", "price": 80},
    {"name": "pen", "price": 20},
    {"name": "water bottle", "price": 350},
]

bought_items, money_left = buy_max_items(products, 1000)

for item in bought_items:
    print(f"{item['name']}: {item['price']} taka")

print(f"Money left: {money_left} taka")


print("\n=== MAKE CHANGE ===")

coins = [100, 50, 20, 10, 5, 1]
change, remaining = make_change(286, coins)

print(f"Change: {change}")
print(f"Remaining: {remaining}")


print("\n=== BEST VALUE ITEMS ===")

study_items = [
    {"name": "Python course", "cost": 500, "value": 90},
    {"name": "Notebook", "cost": 80, "value": 30},
    {"name": "Practice book", "cost": 300, "value": 70},
    {"name": "Sticker pack", "cost": 100, "value": 10},
]

chosen_items, money_left = choose_best_value_items(study_items, 600)

for item in chosen_items:
    value_per_cost = item["value"] / item["cost"]
    print(f"{item['name']} | cost={item['cost']} | value/cost={value_per_cost}")

print(f"Money left: {money_left} taka")


print("\n=== WHEN GREEDY CAN FAIL ===")

# With these coins, greedy picks 4 + 1 + 1 for amount 6.
# But the best answer is 3 + 3.
bad_coins = [4, 3, 1]
bad_change, bad_remaining = make_change(6, bad_coins)

print(f"Greedy change for 6 using {bad_coins}: {bad_change}")
print("Best answer would be {3: 2}.")

"""
It teaches:
- choosing max non-overlapping meetings
- buying max items with a budget
- making change
- choosing best value items
- why greedy can sometimes fail

"""


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Make a list of tasks with start and end times.
# 2. Use choose_max_meetings() to pick the most non-overlapping tasks.
# 3. Make a list of products and a budget.
# 4. Use buy_max_items() to buy as many as possible.
# 5. Try changing the budget and see how the result changes.
