"""Small Tkinter front end; all browser work happens off the UI thread."""

from pathlib import Path
from queue import Empty, Queue
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from converter import PdfOptions, convert_html, open_pdf, validate_paths


class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML to PDF")
        self.root.geometry("680x430")
        self.root.minsize(560, 430)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.queue = Queue()
        self.busy = False
        self.source = tk.StringVar()
        self.output = tk.StringVar()
        self.paper = tk.StringVar(value="HTML print CSS")
        self.browser = tk.StringVar(value="Auto")
        self.margin = tk.StringVar()
        self.delay = tk.StringVar(value="250")
        self.timeout = tk.StringVar(value="30")
        self.landscape = tk.BooleanVar(value=False)
        self.background = tk.BooleanVar(value=True)
        self.allow_missing = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Ready")
        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="HTML to PDF", font=("Segoe UI", 17)).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 20))
        for row, label, value, command in (
            (1, "HTML file", self.source, self.browse_source),
            (2, "Save PDF", self.output, self.browse_output),
        ):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=6)
            ttk.Entry(frame, textvariable=value).grid(row=row, column=1, sticky="ew", pady=6)
            ttk.Button(frame, text="Browse...", command=command).grid(row=row, column=2, padx=(8, 0), pady=6)
        options = ttk.Frame(frame)
        options.grid(row=3, column=0, columnspan=3, sticky="ew", pady=16)
        options.columnconfigure(1, weight=1)
        options.columnconfigure(3, weight=1)
        for row, label, value, column in (
            (0, "Paper", self.paper, 0), (0, "Browser", self.browser, 2),
            (1, "Margin (mm)", self.margin, 0), (1, "Extra wait (ms)", self.delay, 2),
            (2, "Load timeout (s)", self.timeout, 0),
        ):
            ttk.Label(options, text=label).grid(row=row, column=column, sticky="w", padx=(0, 10), pady=6)
            if label in {"Paper", "Browser"}:
                values = ["HTML print CSS", "A4", "A5", "Letter", "Legal"] if label == "Paper" else ["Auto", "Chrome", "Edge", "Chromium"]
                widget = ttk.Combobox(options, textvariable=value, values=values, state="readonly", width=17)
                if label == "Paper":
                    widget.bind("<<ComboboxSelected>>", self.paper_changed)
            else:
                widget = ttk.Entry(options, textvariable=value, width=12)
            widget.grid(row=row, column=column + 1, sticky="ew", padx=(0, 14), pady=6)
        checks = ttk.Frame(frame)
        checks.grid(row=4, column=0, columnspan=3, sticky="w", pady=(0, 10))
        self.landscape_button = ttk.Checkbutton(checks, text="Landscape", variable=self.landscape, state="disabled")
        self.landscape_button.pack(side="left", padx=(0, 18))
        ttk.Checkbutton(checks, text="Background graphics", variable=self.background).pack(side="left", padx=(0, 18))
        ttk.Checkbutton(checks, text="Allow missing assets", variable=self.allow_missing).pack(side="left")
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(4, 10))
        ttk.Label(frame, textvariable=self.status, wraplength=580).grid(row=6, column=0, columnspan=3, sticky="w")
        self.convert_button = ttk.Button(frame, text="Convert to PDF", command=self.start)
        self.convert_button.grid(row=7, column=0, columnspan=3, sticky="e", pady=(16, 0))

    def paper_changed(self, _event=None):
        css = self.paper.get() == "HTML print CSS"
        self.landscape_button.configure(state="disabled" if css else "normal")
        if css:
            self.landscape.set(False)

    def browse_source(self):
        path = filedialog.askopenfilename(title="Choose HTML file", filetypes=[("HTML files", "*.html *.htm"), ("All files", "*.*")])
        if path:
            self.source.set(path)
            self.output.set(str(Path(path).with_suffix(".pdf")))

    def browse_output(self):
        source = Path(self.source.get()).expanduser() if self.source.get() else None
        path = filedialog.asksaveasfilename(
            title="Save PDF", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")],
            initialdir=str(source.parent) if source else None,
            initialfile=source.with_suffix(".pdf").name if source else "document.pdf",
        )
        if path:
            self.output.set(path)

    def start(self):
        if self.busy:
            return
        try:
            if not self.source.get().strip():
                raise ValueError("Choose an HTML file first.")
            paper = "css" if self.paper.get() == "HTML print CSS" else self.paper.get().lower()
            options = PdfOptions(
                paper=paper, browser=self.browser.get().lower(), landscape=self.landscape.get(),
                margin_mm=float(self.margin.get()) if self.margin.get().strip() else None,
                delay_ms=int(self.delay.get()), timeout_seconds=float(self.timeout.get()),
                background=self.background.get(), allow_missing_assets=self.allow_missing.get(),
            )
            options.validate()
            source, target = validate_paths(self.source.get(), self.output.get() or None, overwrite=True)
            overwrite = target.exists()
            if overwrite and not messagebox.askyesno("Replace PDF?", f"Replace this existing file?\n\n{target}"):
                return
        except (ValueError, OSError) as error:
            messagebox.showerror("Cannot convert", str(error))
            return
        self.output.set(str(target))
        self.busy = True
        self.convert_button.configure(state="disabled")
        self.progress.start(12)
        self.status.set("Rendering and checking assets...")
        Thread(target=self.worker, args=(source, target, options, overwrite), daemon=True).start()
        self.root.after(100, self.poll)

    def worker(self, source, target, options, overwrite):
        try:
            result = convert_html(source, target, options, overwrite=overwrite)
            self.queue.put((True, result))
        except Exception as error:
            self.queue.put((False, str(error)))

    def poll(self):
        try:
            success, value = self.queue.get_nowait()
        except Empty:
            self.root.after(100, self.poll)
            return
        self.busy = False
        self.progress.stop()
        self.convert_button.configure(state="normal")
        if not success:
            self.status.set("Conversion failed")
            messagebox.showerror("Conversion failed", value)
            return
        self.status.set(f"Saved {value.size_bytes:,} bytes using {value.browser}")
        details = f"PDF saved:\n{value.path}"
        if value.warnings:
            details += "\n\nWarnings:\n" + "\n".join(value.warnings)
        if messagebox.askyesno("PDF ready", details + "\n\nOpen it now?"):
            try:
                open_pdf(value.path)
            except OSError as error:
                messagebox.showwarning("PDF saved", f"The viewer could not open: {error}")

    def close(self):
        if self.busy:
            messagebox.showinfo("Conversion in progress", "Please wait for the current conversion to finish.")
        else:
            self.root.destroy()


def launch():
    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()
