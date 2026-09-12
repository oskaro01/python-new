"""
Task 25: Hashing Deeper

In Python, hashing shows up mostly as:
- dict
- set

You already used these, but deeper hashing patterns are very practical:

1. frequency map: count things
2. lookup table: find details quickly by key
3. reverse index: search records by word/category
4. cache: remember expensive function results
5. grouping: collect related items together
"""


def count_frequencies(items):
    counts = {}

    for item in items:
        if item in counts:
            counts[item] = counts[item] + 1
        else:
            counts[item] = 1

    return counts


def build_lookup_by_word(entries):
    lookup = {}

    for entry in entries:
        word = entry["word"].lower()
        lookup[word] = entry

    return lookup


def build_category_index(entries):
    index = {}

    for entry in entries:
        category = entry["category"].lower()

        if category not in index:
            index[category] = []

        index[category].append(entry)

    return index


def build_word_index(entries):
    index = {}

    for entry in entries:
        searchable_text = (
            entry["word"] + " " +
            entry["meaning"] + " " +
            entry["category"]
        ).lower()

        for word in searchable_text.split():
            if word not in index:
                index[word] = []

            index[word].append(entry)

    return index


def expensive_square(number, cache):
    if number in cache:
        print(f"Cache hit for {number}")
        return cache[number]

    print(f"Calculating square for {number}")
    result = number * number
    cache[number] = result
    return result


print("=== FREQUENCY MAP ===")

words = ["python", "bug", "python", "loop", "bug", "python"]
counts = count_frequencies(words)

print(counts)


print("\n=== LOOKUP TABLE ===")

entries = [
    {"word": "serene", "meaning": "calm and peaceful", "category": "vocabulary"},
    {"word": "algorithm", "meaning": "step by step method", "category": "programming"},
    {"word": "variable", "meaning": "a name that stores value", "category": "python"},
]

lookup = build_lookup_by_word(entries)
print(lookup["serene"])


print("\n=== CATEGORY INDEX ===")

category_index = build_category_index(entries)
print(category_index["python"])


print("\n=== WORD INDEX ===")

word_index = build_word_index(entries)
print("Entries matching 'calm':")

for entry in word_index.get("calm", []):
    print(entry["word"])

print("Entries matching 'programming':")

for entry in word_index.get("programming", []):
    print(entry["word"])


print("\n=== CACHE ===")

cache = {}

print(expensive_square(8, cache))
print(expensive_square(8, cache))
print(expensive_square(9, cache))


print("\n=== PRACTICAL EXAMPLE: DUPLICATE DETECTION ===")

saved_words = ["serene", "python", "Serene", "algorithm", "PYTHON"]
seen = set()
duplicates = []

for word in saved_words:
    key = word.lower()

    if key in seen:
        duplicates.append(word)
    else:
        seen.add(key)

print(f"Duplicates: {duplicates}")


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Make a list of expenses with categories.
# 2. Count how many expenses are in each category.
# 3. Build a lookup table by expense name.
# 4. Make a cache for a function that doubles a number.
# 5. Use a set to detect duplicate words.
