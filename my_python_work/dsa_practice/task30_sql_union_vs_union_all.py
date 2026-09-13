"""
Task 30: SQL UNION vs UNION ALL

UNION and UNION ALL combine rows from two SELECT queries.

UNION:
- combines rows
- removes duplicates

UNION ALL:
- combines rows
- keeps duplicates

This file uses sqlite3, which is built into Python.
"""

import sqlite3


connection = sqlite3.connect(":memory:")
cursor = connection.cursor()

cursor.execute("CREATE TABLE saved_words (word TEXT)")
cursor.execute("CREATE TABLE new_words (word TEXT)")

cursor.executemany(
    "INSERT INTO saved_words (word) VALUES (?)",
    [
        ("python",),
        ("serene",),
        ("algorithm",),
    ],
)

cursor.executemany(
    "INSERT INTO new_words (word) VALUES (?)",
    [
        ("python",),
        ("function",),
        ("variable",),
    ],
)


print("=== UNION REMOVES DUPLICATES ===")

cursor.execute(
    """
    SELECT word FROM saved_words
    UNION
    SELECT word FROM new_words
    ORDER BY word
    """
)

for row in cursor.fetchall():
    print(row[0])


print("\n=== UNION ALL KEEPS DUPLICATES ===")

cursor.execute(
    """
    SELECT word FROM saved_words
    UNION ALL
    SELECT word FROM new_words
    ORDER BY word
    """
)

for row in cursor.fetchall():
    print(row[0])


connection.close()


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Add one duplicate word to both tables.
# 2. Run UNION and see it once.
# 3. Run UNION ALL and see it twice.
