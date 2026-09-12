"""
DSA Lesson 1: list vs dict vs set

Goal:
Understand when to use each one.
"""


print("=== LIST ===")

# A list stores items in order.
# Use a list when position/order matters.
foods = ["rice", "milk", "eggs"]

print(foods)
print(foods[0])  # first item

foods.append("chicken")
print(foods)


print("\n=== DICT ===")

# A dict stores key/value pairs.
# Use a dict when you want to look up something by name.
person = {
    "name": "Ayzal",
    "age": 27,
    "city": "Khulna",
}

print(person)
print(person["name"])
print(person["city"])

# Add a new key/value pair.
person["language"] = "Python"
print(person)


print("\n=== SET ===")

# A set stores unique items only.
# Use a set when you want to remove duplicates or check membership fast.
colors = {"red", "blue", "red", "green"}

print(colors)  # red appears only once

colors.add("black")
print(colors)

if "blue" in colors:
    print("blue exists")


print("\n=== SAME PROBLEM, THREE WAYS ===")

words = ["python", "java", "python", "html", "css", "java"]

# List keeps everything, including duplicates.
print(f"List: {words}")

# Set removes duplicates.
unique_words = set(words)
print(f"Set: {unique_words}")

# Dict can count how many times each word appears.
word_count = {}

for word in words:
    if word in word_count:
        word_count[word] = word_count[word] + 1
    else:
        word_count[word] = 1

print(f"Dict count: {word_count}")


print("\n=== MINI CHALLENGE ===")

# Your task:
# 1. Make a list called names with 5 names.
# 2. Make a set from that list to remove duplicates.
# 3. Make a dict that counts how many times each name appears.
#
# Do it below this line.
