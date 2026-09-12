"""
Task 20: Fuzzy Search Deeper

Fuzzy search means forgiving search.

It helps when:
- spelling is not exact
- user remembers only part of a word
- search should check meaning and category too

Tools used here:
- difflib.SequenceMatcher for similarity score
- text normalization
- ranked results

fuzzy = forgiving search when spelling is messy.
fuzzy search: spelling similarity, meaning/category matching, ranked results
"""

import difflib


def normalize_text(text):
    clean_characters = []

    for character in text.lower():
        if character.isalnum():
            clean_characters.append(character)
        else:
            clean_characters.append(" ")

    return " ".join("".join(clean_characters).split())


def text_words(text):
    normalized = normalize_text(text)

    if normalized == "":
        return set()

    return set(normalized.split())


def similarity(first, second):
    first = normalize_text(first)
    second = normalize_text(second)
    return difflib.SequenceMatcher(None, first, second).ratio()


def score_entry(entry, query):
    query = normalize_text(query)
    query_words = text_words(query)

    word = normalize_text(entry["word"])
    meaning = normalize_text(entry.get("meaning", ""))
    category = normalize_text(entry.get("category", ""))
    example = normalize_text(entry.get("example", ""))

    score = 0
    reasons = []

    if word == query:
        score = score + 100
        reasons.append("exact word")
    elif word.startswith(query):
        score = score + 80
        reasons.append("word starts with query")
    elif query in word:
        score = score + 60
        reasons.append("query inside word")

    word_similarity = similarity(word, query)

    if word_similarity >= 0.6:
        fuzzy_points = int(word_similarity * 50)
        score = score + fuzzy_points
        reasons.append("similar spelling")

    if query != "" and query in meaning:
        score = score + 35
        reasons.append("meaning match")

    if query != "" and query in category:
        score = score + 30
        reasons.append("category match")

    if query != "" and query in example:
        score = score + 15
        reasons.append("example match")

    entry_words = text_words(word + " " + meaning + " " + category + " " + example)
    overlap = query_words.intersection(entry_words)

    if len(overlap) > 0:
        score = score + (len(overlap) * 10)
        reasons.append("shared words")

    return score, reasons


def ranked_search(entries, query, limit=5):
    results = []

    for entry in entries:
        score, reasons = score_entry(entry, query)

        if score > 0:
            results.append(
                {
                    "entry": entry,
                    "score": score,
                    "reasons": reasons,
                }
            )

    results.sort(
        key=lambda result: (
            -result["score"],
            result["entry"]["word"].lower(),
        )
    )

    return results[:limit]


entries = [
    {
        "word": "serene",
        "meaning": "calm and peaceful",
        "example": "The lake was serene.",
        "category": "vocabulary",
    },
    {
        "word": "algorithm",
        "meaning": "step by step method for solving a problem",
        "example": "Binary search is an algorithm.",
        "category": "programming",
    },
    {
        "word": "function",
        "meaning": "reusable block of code",
        "example": "A function can return a value.",
        "category": "python",
    },
    {
        "word": "variable",
        "meaning": "a name that stores a value",
        "example": "age is a variable.",
        "category": "python",
    },
]


print("=== NORMALIZE TEXT ===")

messy_text = "  Serene!!! Peaceful??  "
print(normalize_text(messy_text))


print("\n=== SIMILARITY ===")

print(f"serene vs srene: {similarity('serene', 'srene')}")
print(f"python vs coffee: {similarity('python', 'coffee')}")


print("\n=== RANKED SEARCH ===")

queries = ["srene", "calm", "python", "problem solving"]

for query in queries:
    print(f"\nQuery: {query}")
    results = ranked_search(entries, query)

    if len(results) == 0:
        print("No results.")
        continue

    for result in results:
        entry = result["entry"]
        reasons = ", ".join(result["reasons"])
        print(f"{entry['word']} | score={result['score']} | {reasons}")


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Add 5 of your own dictionary entries.
# 2. Search with one misspelled word.
# 3. Search with a meaning word.
# 4. Search with a category.
# 5. Print the score and reasons for each result.
