"""
=============================================
  24 - FILE HANDLING
=============================================
  From: quickref.me/python
  Reading from and writing to files.
=============================================
"""

import os

# ===========================================
# Writing to a File
# ===========================================
print("=== WRITING TO A FILE ===")

# 'w' = write mode (overwrites existing file)
with open("sample_output.txt", "w", encoding='utf8') as file:
    file.write("Hello, File!\n")
    file.write("This is line 2.\n")
    file.write("This is line 3.\n")

print("File 'sample_output.txt' created!")

# ===========================================
# Reading an Entire File
# ===========================================
print("\n=== READING ENTIRE FILE ===")

with open("sample_output.txt", "r", encoding='utf8') as file:
    contents = file.read()
    print(f"File contents:\n{contents}")

# ===========================================
# Reading Line by Line (Best for large files)
# ===========================================
print("\n=== READING LINE BY LINE ===")

with open("sample_output.txt", "r", encoding='utf8') as file:
    for line in file:
        print(f"  Line: {line.strip()}")  # strip() removes \n

# ===========================================
# Reading with Line Numbers
# ===========================================
print("\n=== READING WITH LINE NUMBERS ===")

file = open('sample_output.txt', 'r')
for i, line in enumerate(file, start=1):
    print(f"  Line #{i}: {line.strip()}")
file.close()  # Don't forget to close!

# ===========================================
# Appending to a File
# ===========================================
print("\n=== APPENDING TO A FILE ===")

# 'a' = append mode (adds to end)
with open("sample_output.txt", "a", encoding='utf8') as file:
    file.write("This line was appended!\n")

# Verify it was appended
with open("sample_output.txt", "r") as file:
    print(f"Full file now:\n{file.read()}")

# ===========================================
# Writing a List of Strings
# ===========================================
print("\n=== WRITING A LIST ===")

lines = ["First line\n", "Second line\n", "Third line\n"]
with open("sample_list.txt", "w") as file:
    file.writelines(lines)

# Read it back
with open("sample_list.txt", "r") as file:
    print(f"From list:\n{file.read()}")

# ===========================================
# Deleting a File
# ===========================================
print("\n=== DELETING FILES ===")

# Check if file exists, then delete
if os.path.exists("sample_output.txt"):
    os.remove("sample_output.txt")
    print("Deleted: sample_output.txt")

if os.path.exists("sample_list.txt"):
    os.remove("sample_list.txt")
    print("Deleted: sample_list.txt")

# ===========================================
# File Modes Quick Reference
# ===========================================
# "r"  — Read (default)
# "w"  — Write (overwrites)
# "a"  — Append (adds to end)
# "r+" — Read and Write
# "w+" — Read and Write (overwrites)
# "x"  — Create (fails if file exists)

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Write your name and favorite hobby to a file
#   2. Read it back and print it
#   3. Append another line and read the whole file again
# ===========================================
