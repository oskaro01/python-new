from pathlib import Path

from config import CATEGORIES_FILE, DEFAULT_TARGET_DIR
from organizer import (
    build_plan,
    get_safety_problem,
    load_categories,
    organize_files,
    undo_last_move,
)


def ask_custom_folder():
    folder_text = input("Folder path: ").strip().strip('"')

    if folder_text == "":
        print("Please enter a folder path.")
        return None

    folder = Path(folder_text).expanduser()

    if not folder.exists():
        print("That folder does not exist.")
        return None

    if not folder.is_dir():
        print("That path is not a folder.")
        return None

    safety_problem = get_safety_problem(folder)

    if safety_problem is not None:
        print(f"Unsafe folder: {safety_problem}")
        return None

    return folder.resolve()


def ask_recursive():
    answer = input("Include subfolders? Type yes for recursive mode: ").strip().lower()
    return answer == "yes"


def show_categories():
    categories = load_categories()

    print(f"\nCategory rules from {CATEGORIES_FILE}:")

    for category, extensions in categories.items():
        extensions_text = ", ".join(extensions)
        print(f"{category}: {extensions_text}")


def show_plan(plan, folder=None):
    if len(plan) == 0:
        print("No files to organize.")
        return

    if folder is not None:
        print(f"Folder: {folder}")

    print("Organization plan:")

    for item in plan:
        source = item["source"]
        destination = item["destination"]
        category = item["category"]

        if folder is None:
            source_text = source.name
        else:
            source_text = source.relative_to(folder)

        print(f"{source_text} -> {category}/{destination.name}")


def preview_folder(folder, recursive=False):
    plan = build_plan(folder, recursive)
    show_plan(plan, folder)


def organize_folder(folder, recursive=False):
    plan = build_plan(folder, recursive)
    show_plan(plan, folder)

    if len(plan) == 0:
        return

    if recursive:
        print("Recursive mode includes subfolders.")
        print("Already organized category folders are skipped.")
    else:
        print("Only top-level files are moved. Subfolders are ignored.")

    confirm = input("Move these files? Type yes: ").strip().lower()

    if confirm == "yes":
        organize_files(plan)
    else:
        print("Cancelled.")


def show_menu():
    print("\nFile Organizer")
    print("1. Preview sample folder")
    print("2. Organize sample folder")
    print("3. Preview custom folder")
    print("4. Organize custom folder")
    print("5. Show category rules")
    print("6. Undo last organization")
    print("7. Quit")


def run():
    DEFAULT_TARGET_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        show_menu()
        choice = input("Choose 1-7: ").strip()

        if choice == "1":
            recursive = ask_recursive()
            preview_folder(DEFAULT_TARGET_DIR, recursive)
        elif choice == "2":
            recursive = ask_recursive()
            organize_folder(DEFAULT_TARGET_DIR, recursive)
        elif choice == "3":
            folder = ask_custom_folder()

            if folder is not None:
                recursive = ask_recursive()
                preview_folder(folder, recursive)
        elif choice == "4":
            folder = ask_custom_folder()

            if folder is not None:
                recursive = ask_recursive()
                organize_folder(folder, recursive)
        elif choice == "5":
            show_categories()
        elif choice == "6":
            undo_last_move()
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    run()
