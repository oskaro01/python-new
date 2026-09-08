# difflib helps us find words with close spelling.
# Example: "srene" can suggest "serene".
import difflib

# json lets us save Python data, like lists and dictionaries, into a file.
import json

# These functions live in file_dialogs.py.
# They open the normal Windows Save/Open popup windows.
from file_dialogs import choose_open_file, choose_save_file


# A class groups data and actions together.
# This class is the whole personal dictionary app.
class PersonalDictionaryApp:
    def __init__(self):
        # self.entries is where all dictionary words are stored while the app runs.
        # It starts empty.
        #
        # Later it will look like this:
        # [
        #     {
        #         "word": "serene",
        #         "meaning": "calm and peaceful",
        #         "example": "The lake was serene.",
        #         "category": "vocabulary",
        #     }
        # ]
        self.entries = []

    def show_menu(self):
        # This only prints the menu. It does not change any data.
        print("\nPersonal Dictionary")
        print("1. Add word")
        print("2. Show all words")
        print("3. Search word")
        print("4. Edit word")
        print("5. Remove word")
        print("6. Save dictionary")
        print("7. Open dictionary")
        print("8. Quit")

    def find_word_index(self, word):
        # This searches for an exact word and returns its position.
        # If the word is not found, it returns -1.
        for index, entry in enumerate(self.entries):
            # .lower() makes the check case-insensitive.
            # So "Python" and "python" count as the same word.
            if entry["word"].lower() == word.lower():
                return index

        return -1

    def show_entry(self, entry, number=None):
        # This prints one dictionary entry in a nice format.
        prefix = ""

        # If number is given, print "1. word".
        # If number is not given, print only "word".
        if number is not None:
            prefix = f"{number}. "

        print(f"{prefix}{entry['word']}")
        print(f"   Meaning: {entry['meaning']}")

        if entry["example"] != "":
            print(f"   Example: {entry['example']}")

        if entry["category"] != "":
            print(f"   Category: {entry['category']}")

    def show_all_words(self):
        # If there are no entries, stop this method early with return.
        if len(self.entries) == 0:
            print("Your dictionary is empty.")
            return

        print("Your saved words:")

        # enumerate gives us both the number and the entry.
        # start=1 makes the list display like normal human counting.
        for number, entry in enumerate(self.entries, start=1):
            self.show_entry(entry, number)

        print(f"You have {len(self.entries)} words.")

    def add_word(self):
        # .strip() removes extra spaces from the beginning and end.
        word = input("Enter word: ").strip()

        if word == "":
            print("Please enter a word.")
            return

        if self.find_word_index(word) != -1:
            print(f"{word} is already in your dictionary.")
            return

        meaning = input("Enter meaning: ").strip()

        if meaning == "":
            print("Please enter a meaning.")
            return

        example = input("Enter example sentence (optional): ").strip()
        category = input("Enter category (optional): ").strip()

        # This is one word entry.
        # It is a dictionary because it stores named values.
        entry = {
            "word": word,
            "meaning": meaning,
            "example": example,
            "category": category,
        }

        # Add the new word entry to the list.
        self.entries.append(entry)
        print(f"{word} added.")

    def search_word(self):
        # User may type part of a word.
        # Example: searching "py" can match "python".
        search_text = input("Search for: ").strip().lower()

        if search_text == "":
            print("Please enter a search word.")
            return

        matches = []

        # First search: normal partial search.
        for entry in self.entries:
            # "text in word" checks if the search text appears inside the word.
            if search_text in entry["word"].lower():
                matches.append(entry)

        if len(matches) == 0:
            # If normal search finds nothing, try fuzzy search.
            # Fuzzy search means "find words with close spelling".
            words = []

            for entry in self.entries:
                words.append(entry["word"])

            close_words = difflib.get_close_matches(
                search_text,
                words,
                n=5,        # Show up to 5 suggestions.
                cutoff=0.6, # Higher means stricter matching.
            )

            if len(close_words) == 0:
                print("No matching words found.")
                return

            print("No exact match found. Did you mean:")

            for number, word in enumerate(close_words, start=1):
                print(f"{number}. {word}")

            return

        print("Search results:")

        for number, entry in enumerate(matches, start=1):
            self.show_entry(entry, number)

    def edit_word(self):
        # You cannot edit if there is nothing saved.
        if len(self.entries) == 0:
            print("Your dictionary is empty.")
            return

        self.show_all_words()
        item_number = input("Enter the number to edit: ").strip()

        if not item_number.isdigit():
            print("Please enter a valid number.")
            return

        # User sees numbers starting from 1.
        # Python list indexes start from 0.
        # So we subtract 1.
        index = int(item_number) - 1

        if index < 0 or index >= len(self.entries):
            print("That word number does not exist.")
            return

        # Get the selected entry from the list.
        entry = self.entries[index]

        print("Press Enter to keep the old value.")
        new_word = input(f"Word [{entry['word']}]: ").strip()
        new_meaning = input(f"Meaning [{entry['meaning']}]: ").strip()
        new_example = input(f"Example [{entry['example']}]: ").strip()
        new_category = input(f"Category [{entry['category']}]: ").strip()

        if new_word != "":
            existing_index = self.find_word_index(new_word)

            # Stop the user from changing a word into a duplicate word.
            if existing_index != -1 and existing_index != index:
                print(f"{new_word} is already in your dictionary.")
                return

            # Change only the word value inside this entry dictionary.
            entry["word"] = new_word

        if new_meaning != "":
            entry["meaning"] = new_meaning

        if new_example != "":
            entry["example"] = new_example

        if new_category != "":
            entry["category"] = new_category

        print("Word updated.")

    def remove_word(self):
        # You cannot remove if there is nothing saved.
        if len(self.entries) == 0:
            print("Your dictionary is empty.")
            return

        self.show_all_words()
        item_number = input("Enter the number to remove: ").strip()

        if not item_number.isdigit():
            print("Please enter a valid number.")
            return

        # Convert the user's number into a Python list index.
        index = int(item_number) - 1

        if index < 0 or index >= len(self.entries):
            print("That word number does not exist.")
            return

        # pop(index) removes the item and also gives it back to us.
        removed_entry = self.entries.pop(index)
        print(f"{removed_entry['word']} removed.")

    def save_dictionary(self):
        # Ask Windows where the user wants to save the JSON file.
        filename = choose_save_file()

        if filename == "":
            print("Save cancelled.")
            return

        try:
            # "w" means write mode.
            # json.dump saves the whole list of dictionaries at once.
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(self.entries, file, indent=4)

            print(f"Dictionary saved to {filename}.")

        except OSError:
            # OSError can happen if Windows refuses to save the file.
            print("Sorry, the dictionary could not be saved.")

    def open_dictionary(self):
        # Ask Windows which JSON file the user wants to open.
        filename = choose_open_file()

        if filename == "":
            print("Open cancelled.")
            return

        try:
            # "r" means read mode.
            # json.load turns the JSON file back into Python data.
            with open(filename, "r", encoding="utf-8") as file:
                loaded_entries = json.load(file)

            # We expect the JSON file to contain a list.
            if not isinstance(loaded_entries, list):
                print("Sorry, this JSON file does not contain a dictionary list.")
                return

            # We clean the loaded data before trusting it.
            clean_entries = []

            for entry in loaded_entries:
                # Each entry should be a dictionary.
                if not isinstance(entry, dict):
                    continue

                # .get() safely reads a value from the dictionary.
                # str(...) makes sure the value becomes text.
                word = str(entry.get("word", "")).strip()
                meaning = str(entry.get("meaning", "")).strip()
                example = str(entry.get("example", "")).strip()
                category = str(entry.get("category", "")).strip()

                # A word must have at least a word and a meaning.
                if word == "" or meaning == "":
                    continue

                already_exists = False

                # Avoid duplicate words when loading from a file.
                for clean_entry in clean_entries:
                    if clean_entry["word"].lower() == word.lower():
                        already_exists = True
                        break

                if already_exists:
                    continue

                # Add the cleaned entry to the new list.
                clean_entries.append(
                    {
                        "word": word,
                        "meaning": meaning,
                        "example": example,
                        "category": category,
                    }
                )

            # Only replace self.entries after the file was loaded and cleaned.
            self.entries = clean_entries
            print(f"Dictionary loaded from {filename}.")
            self.show_all_words()

        except OSError:
            # This handles file problems, like missing permission or bad path.
            print("Sorry, the dictionary could not be opened.")

        except json.JSONDecodeError:
            # This handles broken JSON files.
            print("Sorry, this file is not valid JSON.")

    def run(self):
        # This is the main loop.
        # It keeps showing the menu until the user chooses Quit.
        while True:
            self.show_menu()
            choice = input("Choose 1, 2, 3, 4, 5, 6, 7, or 8: ").strip()

            # Each choice calls one method.
            if choice == "1":
                self.add_word()
            elif choice == "2":
                self.show_all_words()
            elif choice == "3":
                self.search_word()
            elif choice == "4":
                self.edit_word()
            elif choice == "5":
                self.remove_word()
            elif choice == "6":
                self.save_dictionary()
            elif choice == "7":
                self.open_dictionary()
            elif choice == "8":
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")
