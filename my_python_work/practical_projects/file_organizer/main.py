from pathlib import Path

from config import DEFAULT_TARGET_DIR
from organizer import build_plan, get_safety_problem, organize_files, undo_last_move


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


def show_plan(plan, folder=None):
    if len(plan) == 0:
        print("No files to organize.")
        return

    if folder is not None:
        print(f"Folder: {folder}")

    print("Organization plan:")

    for item in plan:
        source_name = item["source"].name
        destination = item["destination"]
        category = item["category"]

        print(f"{source_name} -> {category}/{destination.name}")


def preview_folder(folder):
    plan = build_plan(folder)
    show_plan(plan, folder)


def organize_folder(folder):
    plan = build_plan(folder)
    show_plan(plan, folder)

    if len(plan) == 0:
        return

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
    print("5. Undo last organization")
    print("6. Quit")


def run():
    DEFAULT_TARGET_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        show_menu()
        choice = input("Choose 1-6: ").strip()

        if choice == "1":
            preview_folder(DEFAULT_TARGET_DIR)
        elif choice == "2":
            organize_folder(DEFAULT_TARGET_DIR)
        elif choice == "3":
            folder = ask_custom_folder()

            if folder is not None:
                preview_folder(folder)
        elif choice == "4":
            folder = ask_custom_folder()

            if folder is not None:
                organize_folder(folder)
        elif choice == "5":
            undo_last_move()
        elif choice == "6":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    run()
