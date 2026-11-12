"""Local HTML and MHTML printing using an isolated Chromium browser."""

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from email import encoders, policy
from email.parser import BytesParser
from math import isfinite
from pathlib import Path
import os
import sys
import tempfile
import time
import webbrowser


PAPERS = {"css": "A4", "a4": "A4", "a5": "A5", "letter": "Letter", "legal": "Legal"}
BROWSERS = {"auto", "edge", "chrome", "chromium"}
LAYOUTS = {"auto": "Auto", "original": "Original webpage", "chat": "Chat transcript"}
SOURCE_FORMATS = {
    "html": ("HTML", (".html", ".htm")),
    "mhtml": ("MHTML", (".mhtml", ".mht")),
}


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
    layout: str = "auto"

    def validate(self):
        if self.paper not in PAPERS or self.browser not in BROWSERS:
            raise ValueError("Choose a supported paper size and browser.")
        if self.layout not in LAYOUTS:
            raise ValueError("Choose Auto, Original webpage, or Chat transcript layout.")
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
    layout: str = "original"
    message_count: int = 0


def validate_paths(source_path, pdf_path=None, *, overwrite=False, source_format="html"):
    label, extensions = SOURCE_FORMATS[source_format]
    source = Path(source_path).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"The {label} source file does not exist.")
    if source.suffix.lower() not in extensions:
        raise ValueError(f"Choose a {' or '.join(extensions)} source file.")
    if not source.stat().st_size:
        raise ValueError(f"The {label} source file is empty.")
    if source_format == "mhtml":
        validate_archive(source)
    target = Path(pdf_path).expanduser().resolve() if pdf_path else source.with_suffix(".pdf")
    if target == source or target.suffix.lower() != ".pdf":
        raise ValueError("The output must be a different file with a .pdf extension.")
    if target.exists() and (not target.is_file() or not overwrite):
        raise FileExistsError("The output already exists. Choose another name or explicitly allow replacement.")
    return source, target


def validate_archive(source):
    # Validate MIME structure only; Chromium resolves the archived resources itself.
    with source.open("rb") as handle:
        archive = BytesParser(policy=policy.default).parse(handle)
    parts = list(archive.walk())
    if (archive.get_content_type() != "multipart/related" or not archive.is_multipart()
            or any(part.defects for part in parts)):
        raise ValueError("This is not a complete multipart MHTML archive. Save the webpage as .mhtml again.")
    if not any(part.get_content_type() == "text/html" and not part.is_multipart()
               and (part.get_payload(decode=True) or b"").strip() for part in parts):
        raise ValueError("The MHTML archive does not contain an HTML document.")
    return archive


@contextmanager
def archive_input(source):
    with source.open("rb") as handle:
        native_line_endings = handle.readline(8192).endswith(b"\r\n")
    if native_line_endings:
        yield source
        return
    archive = validate_archive(source)
    # Chromium's MIME loader requires CRLF. Re-encode decoded parts before MIME
    # serialization so normalizing the container cannot alter binary image bytes.
    for part in archive.walk():
        if not part.is_multipart():
            payload = part.get_payload(decode=True) or b""
            del part["Content-Transfer-Encoding"]
            part.set_payload(payload)
            encoders.encode_base64(part)
    with tempfile.TemporaryDirectory(prefix="mhtml-to-pdf-") as folder:
        prepared = Path(folder) / source.name
        prepared.write_bytes(archive.as_bytes(policy=policy.SMTP.clone(max_line_length=0)))
        yield prepared


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
    return convert_document(html_path, pdf_path, options, overwrite=overwrite)


def convert_mhtml(archive_path, pdf_path=None, options=None, *, overwrite=False):
    return convert_document(archive_path, pdf_path, options, overwrite=overwrite, source_format="mhtml")


def convert_document(source_path, pdf_path=None, options=None, *, overwrite=False, source_format="html"):
    options = options or PdfOptions()
    options.validate()
    source, target = validate_paths(source_path, pdf_path, overwrite=overwrite, source_format=source_format)
    archived = source_format == "mhtml"
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
        with ExitStack() as resources, sync_playwright() as playwright:
            render_source = resources.enter_context(archive_input(source)) if archived else source
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
                context = browser.new_context(
                    viewport={"width": 1280, "height": 900}, reduced_motion="reduce", accept_downloads=False,
                    offline=archived, java_script_enabled=not archived,
                    service_workers="block" if archived else "allow",
                )
                page = context.new_page()
                failures = set()
                asset_types = {"image", "font", "stylesheet"}
                page.on("requestfailed", lambda request: failures.add(request.url) if request.resource_type in asset_types else None)
                page.on("response", lambda response: failures.add(response.url)
                        if response.status >= 400 and response.request.resource_type in asset_types else None)
                page.on("pageerror", lambda _error: warnings.append("The HTML reported a JavaScript error; check dynamic content."))
                page.emulate_media(media="print")
                page.goto(render_source.as_uri(), wait_until="load", timeout=remaining_ms())
                if archived and not page.evaluate("() => Boolean(document.body && document.body.innerHTML.trim())"):
                    raise RuntimeError("The browser loaded an empty archive. Re-save the webpage as MHTML or try another browser.")
                layout_info = {"layout": "original", "message_count": 0}
                if options.layout == "chat" or (archived and options.layout == "auto"):
                    layout_info = page.evaluate(Path(__file__).with_name("chat_print.js").read_text(encoding="utf-8"))
                    if options.layout == "chat" and layout_info["layout"] != "chat":
                        raise ValueError("No saved chat messages were found. Choose Auto or Original webpage layout.")
                    if layout_info["layout"] == "chat":
                        # Discard asset failures belonging to app controls removed from the printable content.
                        failures.clear()
                overrides = print_overrides(options)
                if overrides:
                    remaining_ms()
                    if archived:
                        # add_style_tag waits for an event that does not fire with page scripts disabled.
                        page.evaluate("""css => {
                            const style = document.createElement('style');
                            style.textContent = css;
                            document.head.appendChild(style);
                        }""", overrides)
                    else:
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
                    warning = ("Some images, fonts, or stylesheets could not load from this archive. They may be missing or blocked by browser security."
                               if archived else "Some images, fonts, or stylesheets could not load. Check their paths and network access.")
                    if not options.allow_missing_assets:
                        raise RuntimeError(warning + " Enable 'Allow missing assets' only to export anyway.")
                    warnings.append(warning)
                target.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(prefix=f".{source_format}-to-pdf-", suffix=".pdf", dir=target.parent, delete=False) as handle:
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
                return PdfResult(target, target.stat().st_size, channel, tuple(dict.fromkeys(warnings)), **layout_info)
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
