"""
=============================================
  25 - JSON FILE HANDLING
=============================================
  From: quickref.me/python
  Working with JSON data (like API responses).
=============================================
"""

import json
import os

# ===========================================
# Writing a Dictionary as JSON
# ===========================================
print("=== WRITING JSON ===")

data = {
    "name": "Alice",
    "age": 30,
    "city": "London",
    "hobbies": ["reading", "hiking", "coding"],
    "is_student": False,
    "grades": {
        "math": 95,
        "english": 88
    }
}

print(f"Original data: {data}")

# Write to JSON file
with open("data_output.json", "w+") as file:
    json.dump(data, file, indent=2)  # indent for pretty formatting

print("Written to 'data_output.json'")

# ===========================================
# Reading JSON Back
# ===========================================
print("\n=== READING JSON ===")

with open('data_output.json', "r+") as file:
    contents = json.load(file)  # Parse JSON -> Python dict

print(f"Read back: {contents}")
print(f"Name: {contents['name']}")
print(f"Hobbies: {', '.join(contents['hobbies'])}")

# ===========================================
# JSON String ↔ Python Object
# ===========================================
print("\n=== JSON STRING CONVERSION ===")

# Python dict -> JSON string
person = {"name": "Bob", "age": 25}
json_str = json.dumps(person, indent=2)
print(f"Python dict -> JSON string:\n{json_str}")
print(f"Type: {type(json_str)}")

# JSON string -> Python dict
parsed = json.loads(json_str)
print(f"\nJSON string -> Python dict:\n{parsed}")
print(f"Type: {type(parsed)}")
print(f"Name: {parsed['name']}")

# ===========================================
# Writing Objects as JSON Strings
# ===========================================
print("\n=== WRITING JSON STRING ===")

contents = {"aa": 12, "bb": 21}
with open("data_string.json", "w+") as file:
    file.write(json.dumps(contents))

# Read back
with open('data_string.json', "r+") as file:
    contents = json.load(file)
    print(f"Read from file: {contents}")

# ===========================================
# Cleanup
# ===========================================
os.remove("data_output.json")
os.remove("data_string.json")
print("\nCleanup done — temp files deleted.")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a dict about yourself and write it to 'me.json'
#   2. Read it back and print each key-value pair
#   3. Add a nested dict (like 'address') to the JSON
# ===========================================
