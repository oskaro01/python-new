import json
import os
import shutil
from pathlib import Path

from config import (
    CATEGORIES_FILE,
    DEFAULT_CATEGORIES,
    DEFAULT_TARGET_DIR,
    LOG_FILE,
    PROJECT_DIR,
    WORKSPACE_DIR,
)


def copy_categories(categories):
    copied_categories = {}

    for category, extensions in categories.items():
        copied_categories[category] = extensions.copy()

    return copied_categories


def normalize_extension(extension):
    extension = extension.strip().lower()

    if extension == "":
        return None

    if not extension.startswith("."):
        extension = "." + extension

    return extension


def normalize_category_name(category):
    category = category.strip().lower().replace(" ", "_")
    clean_characters = []

    for character in category:
        if character.isalnum() or character in ["_", "-"]:
            clean_characters.append(character)
        else:
            clean_characters.append("_")

    category = "".join(clean_characters).strip("_")

    if category == "":
        return None

    return category


def clean_categories(raw_categories):
    if not isinstance(raw_categories, dict):
        return copy_categories(DEFAULT_CATEGORIES)

    categories = {}

    for category, extensions in raw_categories.items():
        if not isinstance(category, str):
            continue

        category = normalize_category_name(category)

        if category is None or not isinstance(extensions, list):
            continue

        clean_extensions = []

        for extension in extensions:
            if not isinstance(extension, str):
                continue

            extension = normalize_extension(extension)

            if extension is not None and extension not in clean_extensions:
                clean_extensions.append(extension)

        if len(clean_extensions) > 0:
            categories[category] = clean_extensions

    if len(categories) == 0:
        return copy_categories(DEFAULT_CATEGORIES)

    return categories


def save_default_categories():
    with open(CATEGORIES_FILE, "w", encoding="utf-8") as file:
        json.dump(DEFAULT_CATEGORIES, file, indent=4)


def load_categories():
    if not CATEGORIES_FILE.exists():
        save_default_categories()
        return copy_categories(DEFAULT_CATEGORIES)

    try:
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as file:
            raw_categories = json.load(file)
    except (OSError, json.JSONDecodeError):
        print("Could not read categories.json. Using default categories.")
        return copy_categories(DEFAULT_CATEGORIES)

    return clean_categories(raw_categories)


def get_category(file_path, categories=None):
    if categories is None:
        categories = load_categories()

    extension = file_path.suffix.lower()

    for category, extensions in categories.items():
        if extension in extensions:
            return category

    return "others"


def is_inside(folder, parent):
    try:
        folder.relative_to(parent)
        return True
    except ValueError:
        return False


def get_safety_problem(folder):
    folder = folder.resolve()

    if folder == DEFAULT_TARGET_DIR.resolve():
        return None

    if folder.parent == folder:
        return "That is a drive/root folder."

    windows_folder = Path(os.environ.get("WINDIR", "C:/Windows")).resolve()

    if folder == windows_folder or is_inside(folder, windows_folder):
        return "That is inside the Windows system folder."

    blocked_folders = {
        Path.home().resolve(): "your user home folder",
        (Path.home() / "Desktop").resolve(): "your Desktop root",
        WORKSPACE_DIR.resolve(): "this project workspace",
        PROJECT_DIR.parent.parent.resolve(): "the my_python_work folder",
        PROJECT_DIR.parent.resolve(): "the practical_projects folder",
        PROJECT_DIR.resolve(): "the file_organizer project folder",
    }

    for blocked_folder, label in blocked_folders.items():
        if folder == blocked_folder:
            return f"That is {label}."

    return None


def get_unique_path(destination, reserved_paths=None):
    if reserved_paths is None:
        reserved_paths = set()

    if not destination.exists() and destination not in reserved_paths:
        return destination

    folder = destination.parent
    stem = destination.stem
    suffix = destination.suffix
    counter = 1

    while True:
        new_destination = folder / f"{stem}_{counter}{suffix}"

        if not new_destination.exists() and new_destination not in reserved_paths:
            return new_destination

        counter = counter + 1


def is_inside_any_folder(file_path, folders):
    for folder in folders:
        if is_inside(file_path, folder):
            return True

    return False


def get_output_folders(folder, categories):
    output_folders = []
    category_names = list(categories.keys()) + ["others"]

    for category in category_names:
        output_folders.append((folder / category).resolve())

    return output_folders


def get_files_to_organize(folder, recursive=False, categories=None):
    if categories is None:
        categories = load_categories()

    folder = folder.resolve()
    files = []

    if recursive:
        output_folders = get_output_folders(folder, categories)

        for item in folder.rglob("*"):
            if item.is_file() and not is_inside_any_folder(item.resolve(), output_folders):
                files.append(item)
    else:
        for item in folder.iterdir():
            if item.is_file():
                files.append(item)

    return files


def build_plan(folder, recursive=False):
    folder = folder.resolve()
    categories = load_categories()
    plan = []
    files = get_files_to_organize(folder, recursive, categories)
    reserved_destinations = set()

    for file_path in files:
        category = get_category(file_path, categories)
        target_folder = folder / category
        destination = get_unique_path(target_folder / file_path.name, reserved_destinations)
        reserved_destinations.add(destination)

        plan.append(
            {
                "source": file_path,
                "destination": destination,
                "category": category,
            }
        )

    return plan


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
