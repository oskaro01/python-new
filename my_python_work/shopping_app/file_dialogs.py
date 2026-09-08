import tkinter as tk
from tkinter import filedialog


def choose_save_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filename = filedialog.asksaveasfilename(
        title="Save shopping list",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )

    root.destroy()
    return filename


def choose_open_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filename = filedialog.askopenfilename(
        title="Open shopping list",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )

    root.destroy()
    return filename
