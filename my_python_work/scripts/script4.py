import tkinter as tk
from tkinter import filedialog


def choose_save_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filename = filedialog.asksaveasfilename(
        title="Save shopping list",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],

        # asks Windows to show the save-file popup and returns 
        # the file path you chose. Then Python uses that path
    )

    root.destroy()
    return filename


def choose_open_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filename = filedialog.askopenfilename(
        title="Open shopping list",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )

    root.destroy()
    return filename


def show_list(items):
    if len(items) == 0:
        print("Your shopping list is empty.")
        return

    print("Your shopping list:")

    for number, item in enumerate(items, start=1):
        print(f"{number}. {item}")

    print(f"You have {len(items)} items.")


shopping_list = []

while True:
    print("\nShopping List Menu")
    print("1. Add item")
    print("2. Show list")
    print("3. Remove item")
    print("4. Save list")
    print("5. Open list")
    print("6. Quit")

    choice = input("Choose 1, 2, 3, 4, 5, or 6: ").strip()

    if choice == "1":
        while True:
            item = input("Enter item, or type done: ").strip()

            if item.lower() == "done":
                break

            if item == "":
                print("Please enter an item.")
                continue

            if item in shopping_list:
                print(f"{item} is already in your list.")
                continue

            shopping_list.append(item)
            print(f"{item} added.")

    elif choice == "2":
        show_list(shopping_list)

    elif choice == "3":
        if len(shopping_list) == 0:
            print("Your shopping list is empty.")
            continue

        show_list(shopping_list)

        item_number = input("Enter the number to remove: ").strip()

        if not item_number.isdigit():
            # isdigit() checks if input is a number
            print("Please enter a valid number.")
            continue

        index = int(item_number) - 1
            # User types "3" as text
            # int(item_number) changes "3" into 3
            # 3 - 1 becomes 2
            # Python removes item at index 2

        if index < 0 or index >= len(shopping_list):
            print("That item number does not exist.")
            continue

        removed_item = shopping_list.pop(index) 
        # pop(index) removes an item from a list
        print(f"{removed_item} removed.")

    elif choice == "4":
        filename = choose_save_file()

        if filename == "":
            print("Save cancelled.")
            continue

        with open(filename, "w", encoding="utf-8") as file: # means: open a file for writing. # encoding="utf-8" ensures that the file can handle special characters.
            for item in shopping_list:
                file.write(item + "\n")
                # means: write each item on a new line.

        print(f"Shopping list saved to {filename}.")

    elif choice == "5":
        filename = choose_open_file()

        if filename == "":
            print("Open cancelled.")
            continue

        with open(filename, "r", encoding="utf-8") as file: # "r" means open the file for reading.
            shopping_list = []

            for line in file:
                item = line.strip()
                # This reads the file one line at a time 
                # and removes the newline at the end.

                if item != "" and item not in shopping_list:
                    shopping_list.append(item)

        print(f"Shopping list loaded from {filename}.")
        show_list(shopping_list)

    elif choice == "6":
        print("Goodbye.")
        break

    else:
        print("Invalid choice.")
