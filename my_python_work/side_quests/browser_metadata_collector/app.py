"""Visible Edge experiment for reading metadata from rendered web pages.

This is intentionally separate from the bookmark-only collector. It uses
Playwright to open a normal Edge window, visit each URL, and read the rendered
DOM. It does not download videos or images.
"""

from dataclasses import dataclass, field
from html.parser import HTMLParser
import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import unquote, urljoin, urlsplit


CODE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*-\d{2,8})(?=-|$|\s)",
    re.IGNORECASE,
)
URL_PATTERN = re.compile(r"https?://[^\s,<>\"']+", re.IGNORECASE)
MARKDOWN_URL_PATTERN = re.compile(r"\]\(<([^>]+)>\)")


@dataclass
class PageRecord:
    url: str
    code: str = ""
    title: str = ""
    description: str = ""
    actresses: list[dict[str, str]] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    error: str = ""


def extract_code(url: str) -> str:
    parsed = urlsplit(url)
    slug = unquote(parsed.path.rstrip("/").rsplit("/", 1)[-1])
    match = CODE_PATTERN.search(slug)
    return match.group(1) if match else ""


def clean_title(title: str, code: str) -> str:
    if not code:
        return title.strip()
    prefix = re.compile(rf"^\s*{re.escape(code)}\s*(?:[-:|–—]\s*)?", re.IGNORECASE)
    return prefix.sub("", title, count=1).strip()


class HrefParser(HTMLParser):
    """Collect URLs from an Edge/Chrome bookmark HTML export."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() != "a":
            return
        values = {key.lower(): value or "" for key, value in attrs}
        if values.get("href"):
            self.urls.append(values["href"].strip())


def extract_urls(source: str) -> list[str]:
    """Extract only real HTTP(S) URLs from raw, Markdown, or bookmark HTML input."""

    candidates = URL_PATTERN.findall(source)
    candidates.extend(MARKDOWN_URL_PATTERN.findall(source))
    if "<a" in source.lower():
        parser = HrefParser()
        parser.feed(source)
        candidates.extend(parser.urls)

    urls: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        candidate = candidate.strip().rstrip(".,)")
        parsed = urlsplit(candidate)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        if candidate.casefold() not in seen:
            seen.add(candidate.casefold())
            urls.append(candidate)
    return urls


def unique_names(items: list[dict[str, str]] | list[str]):
    seen: set[str] = set()
    result = []
    for item in items:
        key = item["name"].casefold() if isinstance(item, dict) else item.casefold()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def read_page(page, url: str) -> PageRecord:
    """Read rendered DOM values from a page that Edge has loaded."""

    record = PageRecord(url=url, code=extract_code(url))
    record.title = clean_title(page.title(), record.code)
    description = page.locator('meta[name="description"], meta[property="og:description"]').first
    if description.count():
        record.description = (description.get_attribute("content") or "").strip()

    actress_links = page.locator('a[href*="/actress/"], a[href*="/actresses/"]').all()
    record.actresses = unique_names(
        [
            {
                "name": " ".join((awaitable.inner_text()).split()),
                "url": urljoin(url, awaitable.get_attribute("href") or ""),
            }
            for awaitable in actress_links
            if (awaitable.inner_text()).strip()
        ]
    )
    genre_links = page.locator('a[href*="/genre/"], a[href*="/genres/"]').all()
    record.genres = unique_names(
        [" ".join(item.inner_text().split()) for item in genre_links if item.inner_text().strip()]
    )

    if not record.description:
        body = " ".join(page.locator("body").inner_text().split())
        match = re.search(
            r"(?:description|synopsis)\s*:\s*(.*?)(?=\s+(?:actress|actor|genre|genres)\s*:|$)",
            body,
            re.IGNORECASE,
        )
        if match:
            record.description = match.group(1).strip()
    return record


def markdown_text(records: list[PageRecord]) -> str:
    lines: list[str] = []
    for index, record in enumerate(records):
        title = record.title or "Untitled"
        lines.extend(
            [
                f"## {title}",
                "",
                f"title: {title}",
                f"code: {record.code or '-'}",
                f"url: [Open link](<{record.url}>)",
                "",
                "descrip:",
                record.description or "-",
                "",
                "Actress:",
            ]
        )
        if record.actresses:
            lines.extend(f"- [{item['name']}](<{item['url']}>)" for item in record.actresses)
        else:
            lines.append("-")
        lines.extend(["", f"Genre: {', '.join(record.genres) or '-'}"])
        if record.error:
            lines.append(f"fetch_error: {record.error}")
        if index < len(records) - 1:
            lines.extend(["", "---", ""])
    return "\n".join(lines).rstrip() + "\n"


class BrowserMetadataApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Browser Metadata Collector")
        self.root.geometry("920x650")
        self.root.minsize(680, 500)
        self.records: list[PageRecord] = []
        self.build_ui()

    def build_ui(self):
        header = tk.Frame(self.root, bg="#4267a9")
        header.pack(fill="x")
        tk.Label(header, text="Browser Metadata Collector", bg="#4267a9", fg="white", font=("Segoe UI", 16, "bold"), padx=18, pady=12).pack(anchor="w")
        shell = tk.Frame(self.root, bg="#d8dde5", padx=18, pady=18)
        shell.pack(fill="both", expand=True)
        ttk.Label(shell, text="Paste one URL per line. Fetch pages opens Microsoft Edge and reads the rendered page.", wraplength=850).pack(anchor="w", pady=(0, 6))
        self.input_box = tk.Text(shell, height=7, wrap="word")
        self.input_box.pack(fill="x", pady=(0, 8))
        buttons = tk.Frame(shell, bg="#d8dde5")
        buttons.pack(fill="x", pady=(0, 8))
        ttk.Button(buttons, text="Open URL/bookmark file", command=self.open_file).pack(side="left")
        ttk.Button(buttons, text="Fetch pages in Edge", command=self.fetch_pages).pack(side="left", padx=8)
        ttk.Button(buttons, text="Save MD", command=self.save_md).pack(side="left", padx=8)
        ttk.Button(buttons, text="Save TXT", command=self.save_txt).pack(side="left")
        ttk.Button(buttons, text="Clear", command=self.clear).pack(side="left", padx=8)
        ttk.Label(shell, text="Editable preview").pack(anchor="w")
        self.output_box = tk.Text(shell, height=14, wrap="none")
        self.output_box.pack(fill="both", expand=True, pady=(6, 0))
        self.status = tk.StringVar(value="Ready. The browser opens only when Fetch pages in Edge is clicked.")
        ttk.Label(shell, textvariable=self.status).pack(anchor="w", pady=(8, 0))

    def urls(self) -> list[str]:
        return extract_urls(self.input_box.get("1.0", "end"))

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open bookmark HTML or metadata file",
            filetypes=[("HTML/Markdown/Text", "*.html *.htm *.md *.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            source = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError as error:
            messagebox.showerror("Could not open file", str(error))
            return
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", source)
        self.status.set(f"Loaded {path}. Click Fetch pages in Edge.")

    def fetch_pages(self):
        urls = self.urls()
        if not urls:
            messagebox.showwarning("No valid URLs", "Paste actual http(s) links, Markdown links, or a bookmark HTML export.")
            return
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            messagebox.showerror("Playwright is not installed", "Run: python -m pip install playwright")
            return

        self.records = []
        try:
            with sync_playwright() as playwright:
                profile = Path(__file__).with_name("edge_profile")
                context = playwright.chromium.launch_persistent_context(
                    user_data_dir=str(profile),
                    channel="msedge",
                    headless=False,
                    viewport=None,
                )
                page = context.pages[0] if context.pages else context.new_page()
                for index, url in enumerate(urls, start=1):
                    self.status.set(f"Edge: opening page {index} of {len(urls)}…")
                    self.root.update_idletasks()
                    record = PageRecord(url=url, code=extract_code(url))
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=45_000)
                        page.wait_for_timeout(1500)
                        record = read_page(page, url)
                    except Exception as error:  # Keep one blocked page from stopping the batch.
                        record.error = str(error)
                    self.records.append(record)
                context.close()
        except Exception as error:
            messagebox.showerror("Could not open Edge", str(error))
            return

        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", markdown_text(self.records))
        failed = sum(bool(record.error) for record in self.records)
        self.status.set(f"Read {len(self.records)} page(s) in Edge; {failed} failed. Review and save the preview.")

    def save_md(self):
        self.save_text("Markdown files", "bookmark_metadata.md", ".md")

    def save_txt(self):
        self.save_text("Text files", "bookmark_metadata.txt", ".txt")

    def save_text(self, label: str, initialfile: str, extension: str):
        content = self.output_box.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("Nothing to save", "Fetch at least one page first.")
            return
        path = filedialog.asksaveasfilename(title=f"Save metadata as {extension}", initialfile=initialfile, defaultextension=extension, filetypes=[(label, f"*{extension}"), ("All files", "*.*")])
        if path:
            Path(path).write_text(content + "\n", encoding="utf-8")
            self.status.set(f"Saved edited preview to {path}")
            messagebox.showinfo("Saved", "Saved the edited preview.")

    def clear(self):
        self.records = []
        self.input_box.delete("1.0", "end")
        self.output_box.delete("1.0", "end")
        self.status.set("Ready. The browser opens only when Fetch pages in Edge is clicked.")


if __name__ == "__main__":
    app_root = tk.Tk()
    BrowserMetadataApp(app_root)
    app_root.mainloop()
