"""
OOP 06: Class Methods and Static Methods

Instance method:
Uses one object. First parameter is self.

Class method:
Works with the class itself. First parameter is cls.
Often used as an alternative constructor.

Static method:
Helper function stored inside the class.
Does not need self or cls.
"""


class VocabularyEntry:
    def __init__(self, word, meaning=""):
        self.word = word
        self.meaning = meaning

    def show(self):
        if self.meaning:
            print(f"{self.word}: {self.meaning}")
        else:
            print(self.word)

    @classmethod
    def from_text(cls, text):
        # Alternative way to create an object from one string.
        parts = text.split("-", 1)

        word = parts[0].strip()
        meaning = ""

        if len(parts) == 2:
            meaning = parts[1].strip()

        return cls(word, meaning)

    @staticmethod
    def is_valid_word(word):
        return len(word.strip()) > 0


def main():
    print("=== CLASS METHOD ===")
    entry = VocabularyEntry.from_text("serene - calm and peaceful")
    entry.show()

    print("\n=== STATIC METHOD ===")
    print(VocabularyEntry.is_valid_word("python"))
    print(VocabularyEntry.is_valid_word("   "))


if __name__ == "__main__":
    main()

