shopping_list = []

while True:  # while True means keep repeating

    item = input("Enter an item, or type done: ").strip()
    # .strip() removes extra spaces from the beginning and end.

    if item.lower() == "done":
        break
    # .lower() makes "DONE", "Done", and "done" all work the same way

    if item == "":
        print("Please enter an item.")
        continue
    # continue means go back to the top of the loop and ask for input again

    if item in shopping_list:
        print(f"{item} is already in your list.")
        continue

    shopping_list.append(item)

print("Your shopping list:")

for number, item in enumerate(shopping_list, start=1):
    print(f"{number}. {item}")

    # teaches enumerate(), which gives you both:
    # the index (number) and the value (item) of each item in the list

print(f"You have {len(shopping_list)} items in your list.")