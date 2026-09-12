from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_TARGET_DIR = PROJECT_DIR / "sample_files"
LOG_FILE = PROJECT_DIR / "last_move_log.json"

# file_organizer -> practical_projects -> my_python_work -> python-new
WORKSPACE_DIR = PROJECT_DIR.parents[2]

CATEGORIES = {
    "images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "documents": [".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx"],
    "videos": [".mp4", ".mov", ".mkv"],
    "archives": [".zip", ".rar", ".7z"],
    "python": [".py"],
}
