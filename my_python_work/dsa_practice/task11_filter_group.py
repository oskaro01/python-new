"""
Task 11: Filter, Search, Sort, and Group

This is one of the most practical patterns in Python.

You will use this when working with:
- products
- expenses
- contacts
- notes
- dictionary words
- files
- CSV rows

The data pattern:
list of dictionaries
"""


products = [
    {"name": "keyboard", "category": "tech", "price": 1200, "stock": 5},
    {"name": "mouse", "category": "tech", "price": 500, "stock": 12},
    {"name": "notebook", "category": "stationery", "price": 80, "stock": 30},
    {"name": "pen", "category": "stationery", "price": 20, "stock": 100},
    {"name": "water bottle", "category": "home", "price": 350, "stock": 8},
    {"name": "headphones", "category": "tech", "price": 2200, "stock": 3},
]


def show_products(items):
    if len(items) == 0:
        print("No products found.")
        return

    for product in items:
        print(
            f"{product['name']} | "
            f"{product['category']} | "
            f"{product['price']} taka | "
            f"stock: {product['stock']}"
        )


print("=== ALL PRODUCTS ===")
show_products(products)


print("\n=== FILTER BY CATEGORY ===")

tech_products = []

for product in products:
    if product["category"] == "tech":
        tech_products.append(product)

show_products(tech_products)


print("\n=== FILTER BY PRICE ===")

cheap_products = []

for product in products:
    if product["price"] <= 500:
        cheap_products.append(product)

show_products(cheap_products)


print("\n=== SEARCH BY TEXT ===")

search_text = "pen"
matches = []

for product in products:
    if search_text.lower() in product["name"].lower():
        matches.append(product)

show_products(matches)


print("\n=== SORT CHEAPEST FIRST ===")

cheapest_first = sorted(products, key=lambda product: product["price"])
show_products(cheapest_first)


print("\n=== GROUP BY CATEGORY ===")

products_by_category = {}

for product in products:
    category = product["category"]

    if category not in products_by_category:
        products_by_category[category] = []

    products_by_category[category].append(product)

for category, category_products in products_by_category.items():
    print(f"\n{category.upper()}")
    show_products(category_products)


print("\n=== COUNT BY CATEGORY ===")

category_count = {}

for product in products:
    category = product["category"]

    if category in category_count:
        category_count[category] = category_count[category] + 1
    else:
        category_count[category] = 1

print(category_count)


print("\n=== MINI CHALLENGE ===")

# Your task:
# 1. Make a list called expenses.
# 2. Each expense should be a dictionary with:
#    "name", "category", and "amount".
# 3. Filter only food expenses.
# 4. Sort expenses from highest amount to lowest amount.
# 5. Group expenses by category.
#
# Example:
# {"name": "burger", "category": "food", "amount": 250}
#
# Do it below this line next time.
