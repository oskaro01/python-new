"""Local HTML-to-PDF conversion using an isolated Chromium browser."""

from dataclasses import dataclass
from math import isfinite
from pathlib import Path
import os
import sys
import tempfile
import time
import webbrowser


PAPERS = {"css": "A4", "a4": "A4", "a5": "A5", "letter": "Letter", "legal": "Legal"}
BROWSERS = {"auto", "edge", "chrome", "chromium"}


@dataclass(frozen=True)
class PdfOptions:
    paper: str = "css"
    landscape: bool = False
    margin_mm: float | None = None
    background: bool = True
    browser: str = "auto"
    timeout_seconds: float = 30
    delay_ms: int = 250
    wait_selector: str = ""
    allow_missing_assets: bool = False

    def validate(self):
        if self.paper not in PAPERS or self.browser not in BROWSERS:
            raise ValueError("Choose a supported paper size and browser.")
        if self.paper == "css" and self.landscape:
            raise ValueError("Choose an explicit paper size to override orientation.")
        if self.margin_mm is not None and (not isfinite(self.margin_mm) or not 0 <= self.margin_mm <= 70):
            raise ValueError("Margin must be between 0 and 70 mm, or left blank.")
        if not isfinite(self.timeout_seconds) or not 1 <= self.timeout_seconds <= 300:
            raise ValueError("Timeout must be between 1 and 300 seconds.")
        if not 0 <= self.delay_ms <= 30000 or self.delay_ms >= self.timeout_seconds * 1000:
            raise ValueError("Extra wait must be 0-30000 ms and shorter than the timeout.")


@dataclass(frozen=True)
class PdfResult:
    path: Path
    size_bytes: int
    browser: str
    warnings: tuple[str, ...] = ()


def validate_paths(html_path, pdf_path=None, *, overwrite=False):
    source = Path(html_path).expanduser().resolve()
    if not source.is_file():
        raise ValueError("The HTML source file does not exist.")
    if source.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("Choose an .html or .htm source file.")
    if not source.stat().st_size:
        raise ValueError("The HTML source file is empty.")
    target = Path(pdf_path).expanduser().resolve() if pdf_path else source.with_suffix(".pdf")
    if target == source or target.suffix.lower() != ".pdf":
        raise ValueError("The output must be a different file with a .pdf extension.")
    if target.exists() and (not target.is_file() or not overwrite):
        raise FileExistsError("The output already exists. Choose another name or explicitly allow replacement.")
    return source, target


def browser_candidates(playwright, choice):
    if choice != "auto":
        return [{"edge": "msedge", "chrome": "chrome", "chromium": "chromium"}[choice]]
    candidates = []
    roots = [os.environ.get(key, "") for key in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
    for channel, relative in (
        ("chrome", "Google/Chrome/Application/chrome.exe"),
        ("msedge", "Microsoft/Edge/Application/msedge.exe"),
    ):
        if any(root and (Path(root) / relative).is_file() for root in roots):
            candidates.append(channel)
    if Path(playwright.chromium.executable_path).is_file():
        candidates.append("chromium")
    if sys.platform == "darwin":
        for channel, path in (
            ("chrome", "/Applications/Google Chrome.app"),
            ("msedge", "/Applications/Microsoft Edge.app"),
        ):
            if Path(path).exists():
                candidates.append(channel)
    return candidates


def print_overrides(options):
    declarations = []
    if options.paper != "css":
        orientation = "landscape" if options.landscape else "portrait"
        declarations.append(f"size: {PAPERS[options.paper]} {orientation} !important")
    if options.margin_mm is not None:
        declarations.append(f"margin: {options.margin_mm:g}mm !important")
    return "@page { " + "; ".join(declarations) + "; }" if declarations else ""


def convert_html(html_path, pdf_path=None, options=None, *, overwrite=False):
    options = options or PdfOptions()
    options.validate()
    source, target = validate_paths(html_path, pdf_path, overwrite=overwrite)
    try:
        from playwright.sync_api import Error as BrowserError, sync_playwright
    except ImportError as error:
        raise RuntimeError("Install this side quest's requirements.txt with the Python interpreter you are using.") from error

    deadline = time.monotonic() + options.timeout_seconds

    def remaining_ms():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Conversion timed out. Check the page's assets or increase the timeout.")
        return max(1, int(remaining * 1000))

    temporary = None
    warnings = []
    try:
        with sync_playwright() as playwright:
            browser = None
            channel = ""
            for candidate in browser_candidates(playwright, options.browser):
                try:
                    browser = playwright.chromium.launch(
                        channel=candidate, headless=True, chromium_sandbox=True,
                        timeout=min(10000, remaining_ms()) if options.browser == "auto" else remaining_ms(),
                    )
                    channel = candidate
                    break
                except BrowserError:
                    if options.browser != "auto":
                        raise RuntimeError(f"Could not launch {candidate}. Install/repair that browser or choose another.")
            if browser is None:
                raise RuntimeError("No usable browser found. Install Chrome/Edge, or run: python -m playwright install chromium")
            try:
                context = browser.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce", accept_downloads=False)
                page = context.new_page()
                failures = set()
                asset_types = {"image", "font", "stylesheet"}
                page.on("requestfailed", lambda request: failures.add(request.url) if request.resource_type in asset_types else None)
                page.on("response", lambda response: failures.add(response.url)
                        if response.status >= 400 and response.request.resource_type in asset_types else None)
                page.on("pageerror", lambda _error: warnings.append("The HTML reported a JavaScript error; check dynamic content."))
                page.emulate_media(media="print")
                page.goto(source.as_uri(), wait_until="load", timeout=remaining_ms())
                overrides = print_overrides(options)
                if overrides:
                    remaining_ms()
                    page.add_style_tag(content=overrides)
                if options.wait_selector:
                    page.wait_for_selector(options.wait_selector, state="visible", timeout=remaining_ms())
                if options.delay_ms:
                    if options.delay_ms >= remaining_ms():
                        raise TimeoutError("Not enough time remains for the extra rendering wait.")
                    page.wait_for_timeout(options.delay_ms)
                # Print-visible fonts and below-the-fold lazy images must finish before export.
                page.eval_on_selector_all("img", "images => images.forEach(image => { image.loading = 'eager'; })")
                page.wait_for_function(
                    "() => document.fonts.status === 'loaded' && Array.from(document.images).every(image => image.complete)",
                    timeout=remaining_ms(),
                )
                broken = page.evaluate("() => Array.from(document.images).filter(image => !image.naturalWidth).length")
                failed_fonts = page.evaluate("() => Array.from(document.fonts).filter(font => font.status === 'error').length")
                if failures or broken or failed_fonts:
                    warning = "Some images, fonts, or stylesheets could not load. Check their paths and network access."
                    if not options.allow_missing_assets:
                        raise RuntimeError(warning + " Enable 'Allow missing assets' only to export anyway.")
                    warnings.append(warning)
                target.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(prefix=".html-to-pdf-", suffix=".pdf", dir=target.parent, delete=False) as handle:
                    temporary = Path(handle.name)
                # The original output stays intact until rendering and basic validation succeed.
                remaining_ms()
                page.pdf(
                    path=str(temporary), format=PAPERS[options.paper],
                    prefer_css_page_size=True, print_background=options.background,
                    display_header_footer=False, tagged=True, outline=True,
                )
                with temporary.open("rb") as handle:
                    if handle.read(5) != b"%PDF-":
                        raise RuntimeError("The browser did not produce a valid PDF file.")
                if target.exists() and not overwrite:
                    raise FileExistsError("The output was created by another operation. Choose a different name.")
                temporary.replace(target)
                temporary = None
                return PdfResult(target, target.stat().st_size, channel, tuple(dict.fromkeys(warnings)))
            finally:
                browser.close()
    except BrowserError as error:
        raise RuntimeError(f"Browser conversion failed: {error}") from error
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def open_pdf(path):
    path = Path(path).resolve()
    if sys.platform == "win32":
        os.startfile(str(path))
    else:
        webbrowser.open(path.as_uri())
