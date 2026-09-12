import json
import shutil
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_TARGET_DIR = PROJECT_DIR / "sample_files"
LOG_FILE = PROJECT_DIR / "last_move_log.json"

CATEGORIES = {
    "images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "documents": [".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx"],
    "videos": [".mp4", ".mov", ".mkv"],
    "archives": [".zip", ".rar", ".7z"],
    "python": [".py"],
}


def get_category(file_path):
    extension = file_path.suffix.lower()

    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category

    return "others"


def get_unique_path(destination):
    if not destination.exists():
        return destination

    folder = destination.parent
    stem = destination.stem
    suffix = destination.suffix
    counter = 1

    while True:
        new_destination = folder / f"{stem}_{counter}{suffix}"

        if not new_destination.exists():
            return new_destination

        counter = counter + 1


def get_files_to_organize(folder):
    files = []

    for item in folder.iterdir():
        if item.is_file():
            files.append(item)

    return files


def build_plan(folder):
    plan = []
    files = get_files_to_organize(folder)

    for file_path in files:
        category = get_category(file_path)
        target_folder = folder / category
        destination = get_unique_path(target_folder / file_path.name)

        plan.append(
            {
                "source": file_path,
                "destination": destination,
                "category": category,
            }
        )

    return plan


def show_plan(plan):
    if len(plan) == 0:
        print("No files to organize.")
        return

    print("Organization plan:")

    for item in plan:
        source_name = item["source"].name
        destination = item["destination"]
        category = item["category"]

        print(f"{source_name} -> {category}/{destination.name}")


def organize_files(plan):
    if len(plan) == 0:
        print("No files to organize.")
        return

    move_log = []

    for item in plan:
        source = item["source"]
        destination = item["destination"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))

        move_log.append(
            {
                "source": str(source),
                "destination": str(destination),
            }
        )

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(move_log, file, indent=4)

    print(f"Moved {len(plan)} files.")
    print(f"Move log saved to {LOG_FILE}")


def undo_last_move():
    if not LOG_FILE.exists():
        print("No move log found. Nothing to undo.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        move_log = json.load(file)

    if len(move_log) == 0:
        print("Move log is empty. Nothing to undo.")
        return

    restored_count = 0

    for item in reversed(move_log):
        source = Path(item["source"])
        destination = Path(item["destination"])

        if not destination.exists():
            print(f"Missing file, cannot undo: {destination}")
            continue

        source.parent.mkdir(parents=True, exist_ok=True)
        final_source = get_unique_path(source)
        shutil.move(str(destination), str(final_source))
        restored_count = restored_count + 1

    LOG_FILE.unlink()
    print(f"Restored {restored_count} files.")
    print("Move log removed.")


def show_menu():
    print("\nFile Organizer")
    print("1. Preview organization")
    print("2. Organize sample folder")
    print("3. Undo last organization")
    print("4. Quit")


def run():
    DEFAULT_TARGET_DIR.mkdir(parents=True, exist_ok=True)

    while True:
        show_menu()
        choice = input("Choose 1, 2, 3, or 4: ").strip()

        if choice == "1":
            plan = build_plan(DEFAULT_TARGET_DIR)
            show_plan(plan)
        elif choice == "2":
            plan = build_plan(DEFAULT_TARGET_DIR)
            show_plan(plan)

            if len(plan) == 0:
                continue

            confirm = input("Move these files? Type yes: ").strip().lower()

            if confirm == "yes":
                organize_files(plan)
            else:
                print("Cancelled.")
        elif choice == "3":
            undo_last_move()
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    run()
