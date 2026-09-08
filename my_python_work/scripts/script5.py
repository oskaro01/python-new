import tkinter as tk
from tkinter import filedialog


class ShoppingListApp: # The idea
    def __init__(self):
        self.items = [] # This creates a blueprint for your app    # DATA

    def choose_save_file(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        filename = filedialog.asksaveasfilename(
            title="Save shopping list",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        root.destroy()
        return filename

    def choose_open_file(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        filename = filedialog.askopenfilename(
            title="Open shopping list",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        root.destroy()
        return filename

    def show_menu(self):
        print("\nShopping List Menu")
        print("1. Add item")
        print("2. Show list")
        print("3. Remove item")
        print("4. Save list")
        print("5. Open list")
        print("6. Edit item")
        print("7. Quit")

    def show_list(self):
        if len(self.items) == 0:
            print("Your shopping list is empty.")
            return

        print("Your shopping list:")

        for number, item in enumerate(self.items, start=1):
            print(f"{number}. {item}")

        print(f"You have {len(self.items)} items.")

    def add_items(self):
        while True:
            item = input("Enter item, or type done: ").strip()

            if item.lower() == "done":
                break

            if item == "":
                print("Please enter an item.")
                continue

            if item in self.items:
                print(f"{item} is already in your list.")
                continue

            self.items.append(item)
            print(f"{item} added.")

    def edit_item(self):
        if len(self.items) == 0:
            print("Your shopping list is empty.")
            return

        self.show_list()

        item_number = input("Enter the number to edit: ").strip()

        if not item_number.isdigit():
            print("Please enter a valid number.")
            return

        index = int(item_number) - 1

        if index < 0 or index >= len(self.items):
            print("That item number does not exist.")
            return

        new_item = input("Enter the new item name: ").strip()

        if new_item == "":
            print("Please enter an item.")
            return

        old_item = self.items[index]
        self.items[index] = new_item

        print(f"{old_item} changed to {new_item}.")

    def remove_item(self):
        if len(self.items) == 0:
            print("Your shopping list is empty.")
            return

        self.show_list()
        item_number = input("Enter the number to remove: ").strip()

        if not item_number.isdigit():
            print("Please enter a valid number.")
            return

        index = int(item_number) - 1

        if index < 0 or index >= len(self.items):
            print("That item number does not exist.")
            return

        removed_item = self.items.pop(index)
        print(f"{removed_item} removed.")

    def save_list(self):
        filename = self.choose_save_file()

        if filename == "":
            print("Save cancelled.")
            return

        with open(filename, "w", encoding="utf-8") as file:
            for item in self.items:
                file.write(item + "\n")

        print(f"Shopping list saved to {filename}.")

    def open_list(self):
        filename = self.choose_open_file()

        if filename == "":
            print("Open cancelled.")
            return

        self.items = []

        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                item = line.strip()

                if item != "" and item not in self.items:
                    self.items.append(item)

        print(f"Shopping list loaded from {filename}.")
        self.show_list()

    def run(self):
        while True:
            self.show_menu()
            choice = input("Choose 1, 2, 3, 4, 5, 6, or 7: ").strip()

            if choice == "1":
                self.add_items() # actions = methods like self.add_items()
            elif choice == "2":
                self.show_list()
            elif choice == "3":
                self.remove_item()
            elif choice == "4":
                self.save_list()
            elif choice == "5":
                self.open_list()
            elif choice == "6":
                self.edit_item()
            elif choice == "7":
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")


app = ShoppingListApp()
app.run()

