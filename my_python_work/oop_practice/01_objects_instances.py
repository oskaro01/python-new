"""
OOP 01: Objects and Instances

Class = blueprint.
Object/instance = real thing made from the blueprint.
Attribute = data stored inside the object.
Method = function that belongs to the object.
"""


class VocabularyWord:
    def __init__(self, word, meaning, example):
        # These are attributes.
        # Every VocabularyWord object gets its own values.
        self.word = word
        self.meaning = meaning
        self.example = example

    def show(self):
        # This is a method.
        # It uses the data stored inside this object.
        print(f"Word: {self.word}")
        print(f"Meaning: {self.meaning}")
        print(f"Example: {self.example}")

    def matches(self, search_text):
        search_text = search_text.lower()
        return search_text in self.word.lower()


def main():
    serene = VocabularyWord(
        "serene",
        "calm and peaceful",
        "The lake was serene in the morning.",
    )

    vivid = VocabularyWord(
        "vivid",
        "bright, clear, or detailed",
        "She gave a vivid description of the city.",
    )

    print("=== OBJECTS / INSTANCES ===")
    serene.show()

    print("\n=== EACH OBJECT HAS ITS OWN DATA ===")
    print(serene.word)
    print(vivid.word)

    print("\n=== METHODS CAN ANSWER QUESTIONS ===")
    print(serene.matches("ser"))
    print(vivid.matches("ser"))


if __name__ == "__main__":
    main()

