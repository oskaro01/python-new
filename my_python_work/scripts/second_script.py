shopping_list = []

while True:  # while True means keep repeating

    item = input("Enter an item, or type done: ")

    if item.lower() == "done":
        break
    # .lower() makes "DONE", "Done", and "done" all work the same way

    if item == "":
        print("Please enter an item.")
        continue
    # continue means go back to the top of the loop and ask for input again

    shopping_list.append(item)

print("Your shopping list:")

for item in shopping_list:
    print(f"- {item}")

print(f"You have {len(shopping_list)} items in your list.")