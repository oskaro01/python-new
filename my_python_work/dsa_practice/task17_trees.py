"""
Task 17: Trees

A tree is parent-child data.

Real examples:
- folders and files
- menus and submenus
- categories and subcategories
- comments and replies
- nested JSON

Tree words:
- root: the top item
- child: item under another item
- leaf: item with no children
"""


file_tree = {
    "name": "my_python_work",
    "type": "folder",
    "children": [
        {
            "name": "personal_dictionary",
            "type": "folder",
            "children": [
                {"name": "main.py", "type": "file"},
                {"name": "dictionary_app.py", "type": "file"},
            ],
        },
        {
            "name": "practical_projects",
            "type": "folder",
            "children": [
                {
                    "name": "expense_tracker",
                    "type": "folder",
                    "children": [
                        {"name": "main.py", "type": "file"},
                        {"name": "expenses.csv", "type": "file"},
                    ],
                },
                {
                    "name": "file_organizer",
                    "type": "folder",
                    "children": [
                        {"name": "main.py", "type": "file"},
                        {"name": "organizer.py", "type": "file"},
                        {"name": "categories.json", "type": "file"},
                    ],
                },
            ],
        },
    ],
}


def print_tree(node, indent=0):
    spaces = "  " * indent
    print(f"{spaces}- {node['name']} ({node['type']})")

    children = node.get("children", [])

    for child in children:
        print_tree(child, indent + 1)


def count_files(node):
    if node["type"] == "file":
        return 1

    total = 0
    children = node.get("children", [])

    for child in children:
        total = total + count_files(child)

    return total


def find_node(node, target_name):
    if node["name"] == target_name:
        return node

    children = node.get("children", [])

    for child in children:
        result = find_node(child, target_name)

        if result is not None:
            return result

    return None


def collect_file_paths(node, current_path=""):
    if current_path == "":
        path = node["name"]
    else:
        path = current_path + "/" + node["name"]

    if node["type"] == "file":
        return [path]

    paths = []
    children = node.get("children", [])

    for child in children:
        child_paths = collect_file_paths(child, path)
        paths.extend(child_paths)

    return paths


print("=== PRINT TREE ===")
print_tree(file_tree)


print("\n=== COUNT FILES ===")
print(f"Total files: {count_files(file_tree)}")


print("\n=== FIND NODE ===")
target = "categories.json"
result = find_node(file_tree, target)

if result is None:
    print(f"{target} not found.")
else:
    print(f"Found {result['name']} ({result['type']})")


print("\n=== COLLECT FILE PATHS ===")
paths = collect_file_paths(file_tree)

for path in paths:
    print(path)


print("\n=== PRACTICAL EXAMPLE: CATEGORY TREE ===")

category_tree = {
    "name": "dictionary",
    "type": "category",
    "children": [
        {
            "name": "english",
            "type": "category",
            "children": [
                {"name": "vocabulary", "type": "category"},
                {"name": "phrases", "type": "category"},
            ],
        },
        {
            "name": "programming",
            "type": "category",
            "children": [
                {"name": "python", "type": "category"},
                {"name": "algorithms", "type": "category"},
            ],
        },
    ],
}

print_tree(category_tree)

"""
It teaches trees through practical examples:
- folder/file tree
- printing a tree
- counting files
- finding a node
- collecting full file paths
- category tree for dictionary/notes apps
Key idea: a tree is just parent-child data. Once that clicks, folders, menus, categories, and nested JSON become much less scary.

"""

print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Make your own tree called notes_tree.
# 2. Add categories like "study", "personal", and "projects".
# 3. Add child notes under each category.
# 4. Use print_tree() to show it.
# 5. Use find_node() to search for one note.
