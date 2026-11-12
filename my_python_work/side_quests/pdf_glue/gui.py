"""Ordered PDF queue with native file dialogs and a background merge worker."""

from itertools import count
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

if __package__:
    from .merger import merge_pdfs, open_pdf, validate_paths
else:
    from merger import merge_pdfs, open_pdf, validate_paths


class Tooltip:
    def __init__(self, widget, text):
        self.widget, self.text = widget, text
        self.window = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
        widget.bind("<ButtonPress>", self.hide, add=True)

    def show(self, _event=None):
        if self.window:
            return
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"+{self.widget.winfo_rootx()}+{self.widget.winfo_rooty() + self.widget.winfo_height() + 4}")
        ttk.Label(self.window, text=self.text, padding=5, relief="solid").pack()

    def hide(self, _event=None):
        if self.window:
            self.window.destroy()
            self.window = None


class PdfGlueApp:
    def __init__(self, root):
        self.root = root
        root.title("PDF Glue")
        root.geometry("840x510")
        root.minsize(720, 430)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.paths = {}
        self.identifiers = count()
        self.queue = Queue()
        self.busy = False
        self.controls = []
        self.output = tk.StringVar()
        self.status = tk.StringVar(value="0 PDFs")
        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        ttk.Label(frame, text="PDF Glue", font=("Segoe UI", 18)).grid(row=0, column=0, sticky="w", pady=(0, 14))
        toolbar = ttk.Frame(frame)
        toolbar.grid(row=1, column=0, sticky="w", pady=(0, 10))
        for label, command, tooltip in (
            ("Add PDFs...", self.add_files, None), ("Duplicate", self.duplicate, None),
            ("\u2191", lambda: self.move(-1), "Move selected PDFs up"),
            ("\u2193", lambda: self.move(1), "Move selected PDFs down"),
            ("Remove", self.remove, None), ("Sort by name", self.sort_by_name, None), ("Clear", self.clear, None),
        ):
            button = ttk.Button(toolbar, text=label, command=command, width=3 if tooltip else None)
            button.pack(side="left", padx=(0, 5))
            self.controls.append(button)
            if tooltip:
                Tooltip(button, tooltip)
        listing = ttk.Frame(frame)
        listing.grid(row=2, column=0, sticky="nsew")
        listing.columnconfigure(0, weight=1)
        listing.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(listing, columns=("order", "name", "folder"), show="headings", selectmode="extended")
        for column, title, width, stretch in (("order", "#", 45, False), ("name", "PDF", 260, False), ("folder", "Folder", 350, True)):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, minwidth=35 if column == "order" else 100, stretch=stretch,
                             anchor="center" if column == "order" else "w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(listing, orient="vertical", command=self.tree.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(listing, orient="horizontal", command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tree.bind("<Delete>", lambda _event: self.remove())
        destination = ttk.Frame(frame)
        destination.grid(row=3, column=0, sticky="ew", pady=(12, 8))
        destination.columnconfigure(1, weight=1)
        ttk.Label(destination, text="Output PDF").grid(row=0, column=0, padx=(0, 10))
        entry = ttk.Entry(destination, textvariable=self.output)
        entry.grid(row=0, column=1, sticky="ew")
        browse = ttk.Button(destination, text="Browse...", command=self.browse_output)
        browse.grid(row=0, column=2, padx=(8, 0))
        self.controls.extend([entry, browse])
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.grid(row=4, column=0, sticky="ew", pady=(4, 6))
        ttk.Label(frame, textvariable=self.status, wraplength=620).grid(row=5, column=0, sticky="w")
        self.merge_button = ttk.Button(frame, text="Merge PDFs", command=self.start, state="disabled")
        self.merge_button.grid(row=6, column=0, sticky="e", pady=(10, 0))

    def ordered_paths(self):
        return tuple(self.paths[item] for item in self.tree.get_children())

    def refresh(self):
        for position, item in enumerate(self.tree.get_children(), start=1):
            path = self.paths[item]
            self.tree.item(item, values=(position, path.name, str(path.parent)))
        total = len(self.paths)
        self.status.set(f"{total} PDF{'s' if total != 1 else ''}")
        self.merge_button.configure(state="normal" if total >= 2 and not self.busy else "disabled")

    def add_files(self, paths=None):
        if self.busy:
            return
        if paths is None:
            paths = filedialog.askopenfilenames(title="Add PDFs", filetypes=[("PDF files", "*.pdf")])
        for path in paths:
            path = Path(path).expanduser().resolve()
            item = str(next(self.identifiers))
            self.paths[item] = path
            self.tree.insert("", "end", iid=item)
            if not self.output.get():
                self.output.set(str(path.parent / "merged.pdf"))
        self.refresh()

    def duplicate(self):
        if self.busy:
            return
        selected = set(self.tree.selection())
        copies = []
        for item in self.tree.get_children():
            if item in selected:
                duplicate = str(next(self.identifiers))
                self.paths[duplicate] = self.paths[item]
                self.tree.insert("", self.tree.index(item) + 1, iid=duplicate)
                copies.append(duplicate)
        self.tree.selection_set(copies)
        self.refresh()

    def move(self, direction):
        if self.busy:
            return
        selected = set(self.tree.selection())
        items = list(self.tree.get_children())
        for item in items if direction < 0 else reversed(items):
            if item not in selected:
                continue
            position = self.tree.index(item)
            neighbor = position + direction
            current = self.tree.get_children()
            if 0 <= neighbor < len(current) and current[neighbor] not in selected:
                self.tree.move(item, "", neighbor)
        self.refresh()

    def remove(self):
        if self.busy:
            return
        for item in self.tree.selection():
            del self.paths[item]
            self.tree.delete(item)
        self.refresh()

    def sort_by_name(self):
        if self.busy:
            return
        def key(item):
            return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", self.paths[item].name.casefold())]
        for position, item in enumerate(sorted(self.tree.get_children(), key=key)):
            self.tree.move(item, "", position)
        self.refresh()

    def clear(self):
        if self.busy:
            return
        self.tree.delete(*self.tree.get_children())
        self.paths.clear()
        self.refresh()

    def browse_output(self):
        if self.busy:
            return
        current = Path(self.output.get()) if self.output.get() else None
        path = filedialog.asksaveasfilename(title="Save merged PDF", defaultextension=".pdf",
                                          filetypes=[("PDF files", "*.pdf")],
                                          initialfile=current.name if current else "merged.pdf",
                                          initialdir=str(current.parent) if current else None)
        if path:
            self.output.set(path)

    def start(self):
        if self.busy:
            return
        try:
            sources, target = validate_paths(self.ordered_paths(), self.output.get(), overwrite=True)
            overwrite = target.exists()
            if overwrite and not messagebox.askyesno("Replace PDF?", f"Replace this existing file?\n\n{target}"):
                return
        except (ValueError, OSError) as error:
            messagebox.showerror("Cannot merge", str(error))
            return
        self.output.set(str(target))
        self.busy = True
        for control in self.controls + [self.merge_button]:
            control.configure(state="disabled")
        self.status.set("Merging PDFs...")
        self.progress.start(12)
        Thread(target=self.worker, args=(sources, target, overwrite), daemon=True).start()
        self.root.after(100, self.poll)

    def worker(self, sources, target, overwrite):
        try:
            result = merge_pdfs(sources, target, overwrite=overwrite,
                                progress=lambda index, total, path: self.queue.put(("progress", f"Merging {index}/{total}: {path.name}")))
            self.queue.put(("done", result))
        except Exception as error:
            self.queue.put(("error", str(error)))

    def poll(self):
        try:
            while True:
                kind, value = self.queue.get_nowait()
                if kind == "progress":
                    self.status.set(value)
                    continue
                self.busy = False
                self.progress.stop()
                for control in self.controls:
                    control.configure(state="normal")
                self.refresh()
                if kind == "error":
                    self.status.set("Merge failed")
                    messagebox.showerror("Merge failed", value)
                else:
                    self.status.set(f"Saved {value.page_count} pages from {value.file_count} PDFs / {value.size_bytes:,} bytes")
                    if messagebox.askyesno("PDF ready", f"Saved {value.page_count} pages:\n{value.path}\n\nOpen it now?"):
                        try:
                            open_pdf(value.path)
                        except OSError as error:
                            messagebox.showwarning("PDF saved", f"The viewer could not open: {error}")
                return
        except Empty:
            self.root.after(100, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo("Merge in progress", "Please wait for the current merge to finish.")
        else:
            self.root.destroy()


def launch():
    root = tk.Tk()
    PdfGlueApp(root)
    root.mainloop()
