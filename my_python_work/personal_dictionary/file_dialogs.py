# tkinter is Python's built-in tool for simple windows.
# We use it here only for Windows file picker popups.
import tkinter as tk
from tkinter import filedialog


def choose_save_file():
    # Tk() creates a tiny app window in the background.
    root = tk.Tk()

    # withdraw() hides that tiny window.
    # We only want the Save popup, not a full window.
    root.withdraw()

    # topmost helps the popup appear in front of VS Code.
    root.attributes("-topmost", True)

    # asksaveasfilename opens the normal Windows "Save As" popup.
    # It returns the full file path the user chose.
    # If the user cancels, it returns an empty string: "".
    filename = filedialog.asksaveasfilename(
        title="Save personal dictionary",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )

    # Close the hidden Tk window after the popup is done.
    root.destroy()

    # Give the chosen file path back to dictionary_app.py.
    return filename


def choose_open_file():
    # This function is almost the same as choose_save_file,
    # but it opens a file instead of choosing where to save.
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    # askopenfilename opens the normal Windows "Open File" popup.
    # It returns the full file path the user picked.
    filename = filedialog.askopenfilename(
        title="Open personal dictionary",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )

    root.destroy()
    return filename
