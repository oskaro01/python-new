# PDF Glue

A Python desktop and command-line tool for joining whole PDFs in any order.
Repeated files stay in the list. For example:

```text
pdf 1, pdf 3, pdf 8, pdf 3
          |
          v
one PDF with every page from those four entries, in that order
```

No server, browser, account, or API key is needed. Merging runs locally.

## Setup

From the repository root, using Python 3.10+:

```powershell
.\.venv\Scripts\python.exe -m pip install -r my_python_work/side_quests/pdf_glue/requirements.txt
```

The desktop window uses Tkinter, normally included with Python on Windows.

## Desktop App

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/pdf_glue/app.py
```

1. Click **Add PDFs...** and select your files. You can add more afterward.
2. Select entries and use the up/down arrows to arrange them. Multiple
   selected entries move together and retain their relative order.
3. Use **Duplicate** to include selected PDFs again. Adding the same file
   again also works. **Remove** deletes selected entries from the queue.
4. Keep the current order, or click **Sort by name** for numeric filename
   ordering: `pdf 2.pdf` comes before `pdf 10.pdf`. Duplicates are retained.
5. Choose your output filename, then click **Merge PDFs**.
6. The completion dialog shows the page count and offers to open the result.

The numbered list is the final merge order. The system file picker may sort
the initial selection; rearrange the list afterward when needed. Pages
inside each source PDF retain their existing order. **Clear** empties the
queue. Removing entries never deletes source files from disk.

## Command Line

List files in the exact order you want, including repeats:

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/pdf_glue/app.py "C:\PDFs\pdf 1.pdf" "C:\PDFs\pdf 3.pdf" "C:\PDFs\pdf 8.pdf" "C:\PDFs\pdf 3.pdf" --output "C:\PDFs\combined.pdf" --open
```

At least two entries and an explicit `--output` are required. The CLI never
sorts or removes duplicates. `--force` permits replacing an existing output;
without it, an existing filename is rejected. CLI errors return exit code 1,
invalid arguments return 2, and no arguments opens the desktop app.

## What Is Preserved

- Pages are copied with pypdf, without screenshots or reprinting. Existing
  text, images, page sizes, page rotation, and ordinary links are retained.
- Each entry gets a filename bookmark; existing source bookmarks are
  imported underneath it. Repeated documents have separate numbered entries.
- Ordinary PDF form fields are given a unique prefix for each occurrence,
  keeping repeated field names separate across documents and duplicates.
- Source PDFs are opened for reading. The output cannot be any source file,
  including when replacement is permitted.
- A temporary output is written and reopened to verify its page count before
  publication. A failed merge preserves an existing destination. New output
  names are published exclusively using Windows rename semantics or a hard
  link on other systems. Non-Windows destinations therefore need hard-link
  support. Temporary output is removed after a failure.

This version combines whole documents. Selecting page ranges, splitting PDFs,
OCR, password entry, and repairing corrupted PDFs are outside this version.
Encrypted inputs are rejected with a message requesting an unlocked copy.
Combining PDFs creates a new document; source digital signatures and special
document-level behavior are not preserved as signed originals. Large files
need more memory. Output PDFs in this side quest are ignored by Git.

## Checks

The tests use temporary PDFs and verify order, duplicates, selectable text,
images, links, rotation, bookmarks, repeated form fields, invalid files, and
output protection on failures:

```powershell
.\.venv\Scripts\python.exe -m pip install -r my_python_work/side_quests/pdf_glue/requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s my_python_work/side_quests/pdf_glue/tests -v
```

Optional native desktop queue check:

```powershell
$env:PDF_GLUE_GUI="1"
.\.venv\Scripts\python.exe -m unittest discover -s my_python_work/side_quests/pdf_glue/tests -v
Remove-Item Env:PDF_GLUE_GUI
```

Reference: [pypdf merging documentation](https://pypdf.readthedocs.io/en/stable/user/merging-pdfs.html).
