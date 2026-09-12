"""
Task 19: Trie / Autocomplete

A trie is a tree made for text.

It is useful when you need:
- autocomplete
- prefix search
- dictionary word suggestions
- search boxes

Normal search:
- check every word

Trie search:
- walk letter by letter
- if the prefix exists, collect words below it

trie = fast prefix search, 
trie: autocomplete and prefix search
"""


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root

        for character in word.lower():
            if character not in node.children:
                node.children[character] = TrieNode()

            node = node.children[character]

        node.is_word = True

    def contains(self, word):
        node = self.root

        for character in word.lower():
            if character not in node.children:
                return False

            node = node.children[character]

        return node.is_word

    def starts_with(self, prefix):
        node = self.root

        for character in prefix.lower():
            if character not in node.children:
                return False

            node = node.children[character]

        return True

    def find_prefix_node(self, prefix):
        node = self.root

        for character in prefix.lower():
            if character not in node.children:
                return None

            node = node.children[character]

        return node

    def collect_words(self, node, prefix, words):
        if node.is_word:
            words.append(prefix)

        for character in sorted(node.children):
            child = node.children[character]
            self.collect_words(child, prefix + character, words)

    def autocomplete(self, prefix, limit=5):
        node = self.find_prefix_node(prefix)

        if node is None:
            return []

        words = []
        self.collect_words(node, prefix.lower(), words)
        return words[:limit]


print("=== BUILD A TRIE ===")

words = [
    "algorithm",
    "also",
    "always",
    "bug",
    "binary",
    "bit",
    "python",
    "print",
    "program",
    "serene",
]

trie = Trie()

for word in words:
    trie.insert(word)

print(f"Contains python: {trie.contains('python')}")
print(f"Contains py: {trie.contains('py')}")
print(f"Starts with py: {trie.starts_with('py')}")


print("\n=== AUTOCOMPLETE ===")

prefixes = ["al", "bi", "pr", "z"]

for prefix in prefixes:
    suggestions = trie.autocomplete(prefix)
    print(f"{prefix}: {suggestions}")


print("\n=== PRACTICAL EXAMPLE: PERSONAL DICTIONARY WORDS ===")

dictionary_words = ["serene", "search", "score", "script", "save", "sort"]
dictionary_trie = Trie()

for word in dictionary_words:
    dictionary_trie.insert(word)

user_text = "se"
print(f"Autocomplete for {user_text}: {dictionary_trie.autocomplete(user_text)}")


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Add 10 of your own words to a trie.
# 2. Try autocomplete with 3 different prefixes.
# 3. Try contains() with a full word.
# 4. Try starts_with() with a prefix.
