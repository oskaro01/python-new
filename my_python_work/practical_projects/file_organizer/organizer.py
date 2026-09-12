import json
import os
import shutil
from pathlib import Path

from config import CATEGORIES, DEFAULT_TARGET_DIR, LOG_FILE, PROJECT_DIR, WORKSPACE_DIR


def get_category(file_path):
    extension = file_path.suffix.lower()

    for category, extensions in CATEGORIES.items():
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
