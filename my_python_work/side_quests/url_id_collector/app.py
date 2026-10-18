"""Tkinter utility for extracting bookmark metadata and IDs from URLs."""

from dataclasses import dataclass
import csv
from html.parser import HTMLParser
from pathlib import Path
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import unquote, urlsplit


ID_PATH_PATTERN = re.compile(r"/id/([^/?#]+)", re.IGNORECASE)
CODE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*-\d{2,8})(?=-|$|\s)",
    re.IGNORECASE,
)
URL_PATTERN = re.compile(r"https?://[^\s,<>\"']+", re.IGNORECASE)
CSV_FIELDS = ["title", "code", "url"]


@dataclass
class BookmarkRecord:
    title: str
    url: str
    code: str


def extract_id(value: str) -> str | None:
    """Return a code from /id/code or a code-prefixed page slug."""

    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    id_match = ID_PATH_PATTERN.search(parsed.path)
    if id_match:
        return unquote(id_match.group(1))
    slug = unquote(parsed.path.rstrip("/").rsplit("/", 1)[-1])
    code_match = CODE_PATTERN.search(slug)
    return code_match.group(1) if code_match else None


def extract_code_from_title(title: str) -> str | None:
    match = CODE_PATTERN.search(title.strip())
    return match.group(1) if match else None


def clean_title(title: str, code: str) -> str:
    if not code:
        return title
    prefix = re.compile(rf"^\s*{re.escape(code)}\s*(?:[-:|–—]\s*)?", re.IGNORECASE)
    return prefix.sub("", title, count=1).strip()


class BookmarkHTMLParser(HTMLParser):
    """Read Netscape-style Edge/Chrome bookmark exports."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.records: list[BookmarkRecord] = []
        self._link_attrs: dict[str, str] | None = None
        self._link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "a" and values.get("href"):
            self._link_attrs = values
            self._link_text = []

    def handle_data(self, data: str):
        if self._link_attrs is not None:
            self._link_text.append(data)

    def handle_endtag(self, tag: str):
        if tag.lower() == "a" and self._link_attrs is not None:
            url = self._link_attrs["href"].strip()
            raw_title = " ".join("".join(self._link_text).split())
            code = extract_code_from_title(raw_title) or extract_id(url) or ""
            self.records.append(BookmarkRecord(clean_title(raw_title, code), url, code))
            self._link_attrs = None
            self._link_text = []


def records_from_html(source: str) -> list[BookmarkRecord]:
    parser = BookmarkHTMLParser()
    parser.feed(source)
    return deduplicate(parser.records)


def records_from_text(source: str) -> list[BookmarkRecord]:
    return deduplicate(
        [BookmarkRecord("", url, extract_id(url) or "") for url in URL_PATTERN.findall(source)]
    )


def deduplicate(records: list[BookmarkRecord]) -> list[BookmarkRecord]:
    unique: list[BookmarkRecord] = []
    seen: set[str] = set()
    for record in records:
        if record.url.casefold() not in seen:
            seen.add(record.url.casefold())
            unique.append(record)
    return unique


def markdown_text(records: list[BookmarkRecord]) -> str:
    lines = ["| Title | Code | URL |", "|---|---|---|"]
    lines.extend(
        f"| {record.title or '-'} | {record.code or '-'} | [Open link](<{record.url}>) |"
        for record in records
    )
    return "\n".join(lines) + "\n"


def records_from_preview(source: str) -> list[BookmarkRecord]:
    records: list[BookmarkRecord] = []
    for line in source.splitlines():
        if not line.strip().startswith("|") or line.lower().startswith("| title") or "|---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        url_match = re.search(r"\]\(<([^>]+)>\)", cells[2])
        url = url_match.group(1) if url_match else cells[2]
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        records.append(BookmarkRecord("" if cells[0] == "-" else cells[0], url, "" if cells[1] == "-" else cells[1]))
    return deduplicate(records)


def excel_link_formula(url: str) -> str:
    return f'=HYPERLINK("{url.replace(chr(34), chr(34) * 2)}","Open link")'


class UrlIdCollectorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bookmark Metadata Collector")
        self.root.geometry("920x650")
        self.root.minsize(680, 500)
        self.root.configure(bg="#d8dde5")
        self.loaded_source = ""
        self.records: list[BookmarkRecord] = []
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self.root, bg="#4267a9")
        header.pack(fill="x")
        tk.Label(header, text="Bookmark Metadata Collector", bg="#4267a9", fg="white", font=("Segoe UI", 16, "bold"), padx=18, pady=12).pack(anchor="w")
        shell = tk.Frame(self.root, bg="#d8dde5", padx=18, pady=18)
        shell.pack(fill="both", expand=True)
        ttk.Label(shell, text="Paste links or open an Edge/Chrome bookmarks HTML export. The output keeps title, code, and URL.", wraplength=850).pack(anchor="w", pady=(0, 6))
        self.input_box = tk.Text(shell, height=7, wrap="word")
        self.input_box.pack(fill="x", pady=(0, 8))
        buttons = tk.Frame(shell, bg="#d8dde5")
        buttons.pack(fill="x", pady=(0, 8))
        ttk.Button(buttons, text="Open bookmarks HTML", command=self.open_html).pack(side="left")
        ttk.Button(buttons, text="Extract metadata", command=self.extract).pack(side="left", padx=8)
        ttk.Button(buttons, text="Save CSV", command=self.save_csv).pack(side="left")
        ttk.Button(buttons, text="Save TXT", command=self.save_txt).pack(side="left", padx=8)
        ttk.Button(buttons, text="Save MD", command=self.save_md).pack(side="left")
        ttk.Button(buttons, text="Clear", command=self.clear).pack(side="left")
        ttk.Label(shell, text="Editable preview (Markdown table)").pack(anchor="w")
        self.output_box = tk.Text(shell, height=14, wrap="none")
        self.output_box.pack(fill="both", expand=True, pady=(6, 0))
        self.status = tk.StringVar(value="Ready.")
        ttk.Label(shell, textvariable=self.status).pack(anchor="w", pady=(8, 0))

    def open_html(self):
        path = filedialog.askopenfilename(title="Open bookmarks HTML export", filetypes=[("HTML files", "*.html *.htm"), ("All files", "*.*")])
        if not path:
            return
        try:
            self.loaded_source = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError as error:
            messagebox.showerror("Could not open file", str(error))
            return
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", f"Loaded bookmark file: {path}")
        self.status.set("Bookmarks loaded. Click Extract metadata.")

    def source_records(self) -> list[BookmarkRecord]:
        pasted = self.input_box.get("1.0", "end").strip()
        source = self.loaded_source if self.loaded_source and pasted.startswith("Loaded bookmark file:") else pasted
        if not source:
            return []
        return records_from_html(source) if "<a" in source.lower() else records_from_text(source)

    def extract(self):
        self.records = self.source_records()
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", markdown_text(self.records))
        with_code = sum(bool(record.code) for record in self.records)
        self.status.set(f"Found {len(self.records)} unique link(s); {with_code} contained a code.")

    def save_csv(self):
        if not self.records and not self.output_box.get("1.0", "end").strip():
            self.extract()
        records = records_from_preview(self.output_box.get("1.0", "end"))
        if not records:
            messagebox.showwarning("Nothing to save", "Open a bookmark file or paste at least one link first.")
            return
        path = filedialog.asksaveasfilename(title="Save bookmark metadata as CSV", initialfile="bookmark_metadata.csv", defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        with Path(path).open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows({"title": record.title, "code": record.code, "url": excel_link_formula(record.url)} for record in records)
        self.status.set(f"Saved {len(records)} record(s) to {path}")
        messagebox.showinfo("Saved", f"Saved {len(records)} record(s).")

    def save_md(self):
        if not self.records and not self.output_box.get("1.0", "end").strip():
            self.extract()
        content = self.output_box.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("Nothing to save", "Open a bookmark file or paste at least one link first.")
            return
        path = filedialog.asksaveasfilename(title="Save bookmark metadata as Markdown", initialfile="bookmark_metadata.md", defaultextension=".md", filetypes=[("Markdown files", "*.md"), ("All files", "*.*")])
        if not path:
            return
        Path(path).write_text(content + "\n", encoding="utf-8")
        self.status.set(f"Saved edited preview to {path}")
        messagebox.showinfo("Saved", "Saved the edited preview.")

    def save_txt(self):
        if not self.records and not self.output_box.get("1.0", "end").strip():
            self.extract()
        content = self.output_box.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("Nothing to save", "Open a bookmark file or paste at least one link first.")
            return
        path = filedialog.asksaveasfilename(title="Save bookmark metadata as text", initialfile="bookmark_metadata.txt", defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        Path(path).write_text(content + "\n", encoding="utf-8")
        self.status.set(f"Saved edited preview to {path}")
        messagebox.showinfo("Saved", "Saved the edited preview.")

    def clear(self):
        self.loaded_source = ""
        self.records = []
        self.input_box.delete("1.0", "end")
        self.output_box.delete("1.0", "end")
        self.status.set("Ready.")


if __name__ == "__main__":
    app_root = tk.Tk()
    UrlIdCollectorApp(app_root)
    app_root.mainloop()
