"""
OOP 05: Composition

Composition means:

One object is built using other objects.

Memory hook:
Inheritance = "is a"
Composition = "has a"

Example:
PersonalDictionary has a WordStore.
PersonalDictionary has a SearchEngine.
"""


class WordStore:
    def __init__(self):
        self.words = []

    def add(self, word):
        self.words.append(word)

    def all_words(self):
        return self.words


class SearchEngine:
    def search(self, words, search_text):
        results = []
        search_text = search_text.lower()

        for word in words:
            if search_text in word.lower():
                results.append(word)

        return results


class PersonalDictionary:
    def __init__(self):
        # This object owns/uses two smaller objects.
        self.store = WordStore()
        self.search_engine = SearchEngine()

    def add_word(self, word):
        self.store.add(word)

    def search(self, search_text):
        return self.search_engine.search(self.store.all_words(), search_text)


def main():
    dictionary = PersonalDictionary()

    dictionary.add_word("serene")
    dictionary.add_word("vivid")
    dictionary.add_word("resilient")

    print("=== COMPOSITION ===")
    print(dictionary.search("vi"))
    print(dictionary.search("re"))


if __name__ == "__main__":
    main()

