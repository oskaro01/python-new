# File Organizer

Run:

```powershell
python my_python_work/practical_projects/file_organizer/main.py
```

Run tests:

```powershell
python my_python_work/practical_projects/file_organizer/test_organizer.py
```

This project practices:

- `pathlib`
- reading files in a folder
- checking file extensions
- creating folders
- moving files safely
- previewing before changing files
- splitting a project into multiple Python files
- writing simple tests with `assert`
- loading category rules from JSON
- organizing files inside subfolders with recursive mode

The script uses `sample_files/` by default so you can practice safely.

Category rules live in:

```text
my_python_work/practical_projects/file_organizer/categories.json
```

To add a custom category, edit `categories.json`:

```json
{
    "audio": [".mp3", ".wav"]
}
```

Use simple category names like `audio`, `ebooks`, or `school_notes`.

Menu options:

- Preview sample folder
- Organize sample folder
- Preview custom folder
- Organize custom folder
- Show category rules
- Undo last organization

Preview and organize options ask if you want recursive mode. Recursive mode includes files inside subfolders, but skips already organized category folders like `images/` and `documents/`.

Custom folders are checked before organizing. The script blocks risky locations like your home folder, Desktop root, project workspace, and Windows system folder.

Project files:

- `main.py`: menu, user input, and screen output
- `organizer.py`: file organizing logic, move log, and undo
- `config.py`: category rules and important folder paths
- `categories.json`: editable category names and file extensions
- `test_organizer.py`: small checks that prove important functions still work
