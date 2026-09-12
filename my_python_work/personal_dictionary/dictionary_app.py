# difflib helps us find close words and rank search results.
import difflib

# json lets us save Python data, like lists and dictionaries, into a file.
import json

# Path helps us build file paths that work nicely on Windows.
from pathlib import Path

# These functions live in file_dialogs.py.
# They open the normal Windows Save/Open popup windows.
from file_dialogs import choose_open_file, choose_save_file


AUTOSAVE_FILE = Path(__file__).resolve().parent / "autosave_dictionary.json"


class PersonalDictionaryApp:
    def __init__(self, autosave_file=None, load_autosave=True):
        # self.entries stores all words while the app runs.
        # Meaning, example, and category are optional.
        self.entries = []

        if autosave_file is None:
            self.autosave_file = AUTOSAVE_FILE
        else:
            self.autosave_file = Path(autosave_file)

        if load_autosave:
            self.load_autosave()

    def show_menu(self):
        print("\nPersonal Dictionary")
        print("1. Add word")
        print("2. Show all words")
        print("3. Search")
        print("4. Edit word")
        print("5. Remove word")
        print("6. Save dictionary copy")
        print("7. Open dictionary")
        print("8. Show autosave file")
        print("9. Quit")

    def make_entry(self, word, meaning="", example="", category=""):
        # One entry is one dictionary with the same keys every time.
        return {
            "word": word.strip(),
            "meaning": meaning.strip(),
            "example": example.strip(),
            "category": category.strip(),
        }

    def clean_entries(self, loaded_entries):
        # Only a list can be a valid dictionary file for this app.
        if not isinstance(loaded_entries, list):
            return None

        clean_entries = []

        for entry in loaded_entries:
            if not isinstance(entry, dict):
                continue

            word = str(entry.get("word", "")).strip()
            meaning = str(entry.get("meaning", "")).strip()
            example = str(entry.get("example", "")).strip()
            category = str(entry.get("category", "")).strip()

            # Word is required. Meaning is allowed to be blank.
            if word == "":
                continue

            already_exists = False

            for clean_entry in clean_entries:
                if clean_entry["word"].lower() == word.lower():
                    already_exists = True
                    break

            if already_exists:
                continue

            clean_entries.append(self.make_entry(word, meaning, example, category))

        return clean_entries

    def save_entries_to_file(self, filename):
        filename = Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.entries, file, indent=4)

    def load_entries_from_file(self, filename):
        with open(filename, "r", encoding="utf-8") as file:
            loaded_entries = json.load(file)

        return self.clean_entries(loaded_entries)

    def autosave_dictionary(self):
        try:
            self.save_entries_to_file(self.autosave_file)
        except OSError:
            print("Warning: autosave failed.")

    def load_autosave(self):
        if not self.autosave_file.exists():
            return

        try:
            clean_entries = self.load_entries_from_file(self.autosave_file)
        except (OSError, json.JSONDecodeError):
            print("Autosave file exists, but it could not be loaded.")
            return

        if clean_entries is None:
            print("Autosave file does not contain a valid dictionary list.")
            return

        self.entries = clean_entries

        if len(self.entries) > 0:
            print(f"Autosaved dictionary loaded from {self.autosave_file}.")

    def find_word_index(self, word):
        for index, entry in enumerate(self.entries):
            if entry["word"].lower() == word.lower():
                return index

        return -1

    def show_entry(self, entry, number=None):
        prefix = ""

        if number is not None:
            prefix = f"{number}. "

        print(f"{prefix}{entry['word']}")

        if entry["meaning"] == "":
            print("   Meaning: (not added yet)")
        else:
            print(f"   Meaning: {entry['meaning']}")

        if entry["example"] != "":
            print(f"   Example: {entry['example']}")

        if entry["category"] != "":
            print(f"   Category: {entry['category']}")

    def show_all_words(self):
        if len(self.entries) == 0:
            print("Your dictionary is empty.")
            return

        print("Your saved words:")

        for number, entry in enumerate(self.entries, start=1):
            self.show_entry(entry, number)

        print(f"You have {len(self.entries)} words.")

    def add_word(self):
        word = input("Enter word: ").strip()

        if word == "":
            print("Please enter a word.")
            return

        if self.find_word_index(word) != -1:
            print(f"{word} is already in your dictionary.")
            return

        meaning = input("Enter meaning (optional): ").strip()
        example = input("Enter example sentence (optional): ").strip()
        category = input("Enter category (optional): ").strip()

        self.entries.append(self.make_entry(word, meaning, example, category))
        self.autosave_dictionary()
        print(f"{word} added.")

    def get_search_score(self, entry, search_text):
        word = entry["word"].lower()
        meaning = entry["meaning"].lower()
        example = entry["example"].lower()
        category = entry["category"].lower()
        score = 0

        if word == search_text:
            score = score + 100
        elif word.startswith(search_text):
            score = score + 80
        elif search_text in word:
            score = score + 60

        if search_text in meaning:
            score = score + 35

        if search_text in category:
            score = score + 30

        if search_text in example:
            score = score + 15

        close_score = difflib.SequenceMatcher(None, search_text, word).ratio()

        if close_score >= 0.6:
            score = score + int(close_score * 40)

        return score

    def search_entries(self, search_text):
        search_text = search_text.strip().lower()
        scored_matches = []

        for entry in self.entries:
            score = self.get_search_score(entry, search_text)

            if score > 0:
                scored_matches.append((score, entry))

        # Higher score comes first. If scores tie, sort by word.
        scored_matches.sort(key=lambda item: (-item[0], item[1]["word"].lower()))

        matches = []

        for score, entry in scored_matches:
            matches.append(entry)

        return matches

    def get_close_word_suggestions(self, search_text):
        words = []

        for entry in self.entries:
            words.append(entry["word"])

        return difflib.get_close_matches(search_text, words, n=5, cutoff=0.6)

    def search_word(self):
        search_text = input("Search for: ").strip()

        if search_text == "":
            print("Please enter something to search.")
            return

        matches = self.search_entries(search_text)

        if len(matches) == 0:
            close_words = self.get_close_word_suggestions(search_text)

            if len(close_words) == 0:
                print("No matching words found.")
                return

            print("No match found. Did you mean:")

            for number, word in enumerate(close_words, start=1):
                print(f"{number}. {word}")

            return

        print("Search results, best matches first:")

        for number, entry in enumerate(matches, start=1):
            self.show_entry(entry, number)

    def ask_updated_optional_value(self, label, old_value):
        old_text = old_value

        if old_text == "":
            old_text = "empty"

        new_value = input(f"{label} [{old_text}] (Enter keeps, - clears): ").strip()

        if new_value == "":
            return old_value

        if new_value == "-":
            return ""

        return new_value

    def edit_word(self):
        if len(self.entries) == 0:
            print("Your dictionary is empty.")
            return

        self.show_all_words()
        item_number = input("Enter the number to edit: ").strip()

        if not item_number.isdigit():
            print("Please enter a valid number.")
            return

        index = int(item_number) - 1

        if index < 0 or index >= len(self.entries):
            print("That word number does not exist.")
            return

        entry = self.entries[index]

        print("Press Enter to keep the old value.")
        print("For optional fields, type - to clear the value.")
        new_word = input(f"Word [{entry['word']}]: ").strip()

        if new_word != "":
            existing_index = self.find_word_index(new_word)

            if existing_index != -1 and existing_index != index:
                print(f"{new_word} is already in your dictionary.")
                return

            entry["word"] = new_word

        entry["meaning"] = self.ask_updated_optional_value("Meaning", entry["meaning"])
        entry["example"] = self.ask_updated_optional_value("Example", entry["example"])
        entry["category"] = self.ask_updated_optional_value("Category", entry["category"])

        self.autosave_dictionary()
        print("Word updated.")

    def remove_word(self):
        if len(self.entries) == 0:
            print("Your dictionary is empty.")
            return

        self.show_all_words()
        item_number = input("Enter the number to remove: ").strip()

        if not item_number.isdigit():
            print("Please enter a valid number.")
            return

        index = int(item_number) - 1

        if index < 0 or index >= len(self.entries):
            print("That word number does not exist.")
            return

        removed_entry = self.entries.pop(index)
        self.autosave_dictionary()
        print(f"{removed_entry['word']} removed.")

    def save_dictionary(self):
        filename = choose_save_file()

        if filename == "":
            print("Save cancelled.")
            return

        try:
            self.save_entries_to_file(filename)
            print(f"Dictionary saved to {filename}.")
        except OSError:
            print("Sorry, the dictionary could not be saved.")

    def open_dictionary(self):
        filename = choose_open_file()

        if filename == "":
            print("Open cancelled.")
            return

        try:
            clean_entries = self.load_entries_from_file(filename)
        except OSError:
            print("Sorry, the dictionary could not be opened.")
            return
        except json.JSONDecodeError:
            print("Sorry, this file is not valid JSON.")
            return

        if clean_entries is None:
            print("Sorry, this JSON file does not contain a dictionary list.")
            return

        self.entries = clean_entries
        self.autosave_dictionary()
        print(f"Dictionary loaded from {filename}.")
        self.show_all_words()

    def show_autosave_file(self):
        print(f"Autosave file: {self.autosave_file}")

        if self.autosave_file.exists():
            print("Autosave is active.")
        else:
            print("Autosave file will be created after your first change.")

    def run(self):
        while True:
            self.show_menu()
            choice = input("Choose 1-9: ").strip()

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
                self.show_autosave_file()
            elif choice == "9":
                print("Goodbye.")
                break
            else:
                print("Invalid choice.")
