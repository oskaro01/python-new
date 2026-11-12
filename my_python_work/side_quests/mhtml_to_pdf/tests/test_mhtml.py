from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest
from urllib.parse import urlsplit

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR.parent))

from html_to_pdf.converter import PdfOptions, archive_input, convert_mhtml, validate_paths

EXAMPLE = APP_DIR / "examples" / "archived_notes.mhtml"


class ArchiveValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_mhtml_and_mht_paths_with_spaces(self):
        for name in ("saved page.MHTML", "another saved page.mht"):
            source = self.root / name
            source.write_bytes(EXAMPLE.read_bytes())
            validated, target = validate_paths(source, source_format="mhtml")
            self.assertEqual(validated, source.resolve())
            self.assertEqual(target, source.with_suffix(".pdf"))
            target.write_bytes(b"original output")
            with self.assertRaises(FileExistsError):
                validate_paths(source, source_format="mhtml")
            validate_paths(source, source_format="mhtml", overwrite=True)
            self.assertEqual(target.read_bytes(), b"original output")

    def test_lf_normalization_preserves_payloads_and_removes_temporary_copy(self):
        from email import policy
        from email.parser import BytesParser

        source = self.root / "lf-only.mhtml"
        long_url = b"https://example.invalid/" + b"saved-resources/" * 12 + b"style.css"
        source.write_bytes(EXAMPLE.read_bytes().replace(b"\r\n", b"\n").replace(b"https://example.invalid/style.css", long_url))
        original = source.read_bytes()
        before = BytesParser(policy=policy.default).parsebytes(original)
        with archive_input(source) as prepared:
            self.assertNotEqual(prepared, source)
            self.assertIn(b"\r\n", prepared.read_bytes())
            self.assertIn(b"Content-Location: " + long_url + b"\r\n", prepared.read_bytes())
            after = BytesParser(policy=policy.default).parsebytes(prepared.read_bytes())
            self.assertEqual([part.get_payload(decode=True) for part in before.walk() if not part.is_multipart()],
                             [part.get_payload(decode=True) for part in after.walk() if not part.is_multipart()])
        self.assertFalse(prepared.exists())
        self.assertEqual(source.read_bytes(), original)

    def test_standard_crlf_archive_is_loaded_without_reserialization(self):
        source = self.root / "standard.mhtml"
        source.write_bytes(EXAMPLE.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        with archive_input(source) as prepared:
            self.assertEqual(prepared, source)

    def test_renamed_html_empty_and_truncated_archives_are_rejected(self):
        valid = EXAMPLE.read_bytes()
        for content in (b"", b"<html><body>Not an archive</body></html>", valid.split(b"--mhtml-example-boundary--")[0]):
            source = self.root / "bad.mhtml"
            source.write_bytes(content)
            with self.subTest(content=content[:60]), self.assertRaises(ValueError):
                convert_mhtml(source)
            self.assertFalse(source.with_suffix(".pdf").exists())

    def test_archives_without_html_and_wrong_extensions_are_rejected(self):
        source = self.root / "no-html.mhtml"
        source.write_bytes(EXAMPLE.read_bytes().replace(b"Content-Type: text/html", b"Content-Type: text/plain"))
        with self.assertRaisesRegex(ValueError, "does not contain an HTML"):
            validate_paths(source, source_format="mhtml")
        source = self.root / "page.html"
        source.write_bytes(EXAMPLE.read_bytes())
        with self.assertRaises(ValueError):
            validate_paths(source, source_format="mhtml")
        with self.assertRaises(ValueError):
            validate_paths(self.root / "missing.mhtml", source_format="mhtml")
        with self.assertRaises(ValueError):
            validate_paths(EXAMPLE, self.root / "wrong.txt", source_format="mhtml")

    def test_cli_help_and_validation(self):
        help_result = subprocess.run(
            [sys.executable, str(APP_DIR / "app.py"), "--help"],
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(help_result.returncode, 0)
        self.assertIn(".mhtml or .mht", help_result.stdout)
        result = subprocess.run(
            [sys.executable, str(APP_DIR / "app.py"), str(self.root / "missing.mhtml")],
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("MHTML source file does not exist", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


@unittest.skipUnless(os.environ.get("MHTML_PDF_BROWSER"), "Set MHTML_PDF_BROWSER=edge, chrome, or chromium for PDF tests")
class ArchiveBrowserTests(unittest.TestCase):
    def setUp(self):
        import pymupdf
        self.pdf = pymupdf
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.options = PdfOptions(browser=os.environ["MHTML_PDF_BROWSER"], delay_ms=0)

    def test_embedded_styles_image_print_rules_and_page_break(self):
        result = convert_mhtml(EXAMPLE, self.root / "nested" / "notes.pdf", self.options)
        self.assertFalse(result.warnings)
        with self.pdf.open(result.path) as document:
            self.assertEqual(len(document), 2)
            self.assertAlmostEqual(document[0].rect.width, 595.3, delta=2)
            self.assertIn("Archived Field Notes", document[0].get_text())
            self.assertIn("The Next Page", document[1].get_text())
            self.assertNotIn("screen-only sentence", "".join(page.get_text() for page in document))
            self.assertAlmostEqual(document[0].search_for("Archived Field Notes")[0].x0, 18 / 25.4 * 72, delta=2)
            spans = [span for block in document[0].get_text("dict")["blocks"] if "lines" in block
                     for line in block["lines"] for span in line["spans"]]
            self.assertTrue(any(span["color"] == 0x26715A for span in spans))
            # The embedded SVG is retained as vector drawing commands.
            self.assertGreater(len(document[0].get_drawings()), 0)

    def test_paper_override_and_mht_extension(self):
        source = self.root / "saved page.MHT"
        source.write_bytes(EXAMPLE.read_bytes())
        result = convert_mhtml(source, options=replace(self.options, paper="letter", landscape=True, margin_mm=10))
        with self.pdf.open(result.path) as document:
            self.assertGreaterEqual(len(document), 2)
            self.assertAlmostEqual(document[0].rect.width, 792, delta=2)
            self.assertAlmostEqual(document[0].rect.height, 612, delta=2)
            self.assertAlmostEqual(document[0].search_for("Archived Field Notes")[0].x0, 10 / 25.4 * 72, delta=2)

    def test_real_browser_snapshot_keeps_all_long_content_and_image(self):
        from playwright.sync_api import sync_playwright

        original = self.root / "source files"
        original.mkdir()
        image = self.pdf.Pixmap(self.pdf.csRGB, self.pdf.IRect(0, 0, 40, 40), False)
        image.clear_with(60)
        image.save(str(original / "photo.png"))
        (original / "style.css").write_text(
            "@page {size: A4; margin:18mm;} body {font:12pt/1.5 Arial;} h1 {color:#26715a;}", encoding="utf-8",
        )
        paragraphs = "".join(f"<p>Archive paragraph {number:03d}: Saved text flows naturally across printed pages.</p>"
                             for number in range(100))
        html = original / "long page.html"
        html.write_text('<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="style.css">'
                        '<h1>Long Archived Report</h1><img src="photo.png"><p>Saved caf\u00e9 notes.</p>'
                        + paragraphs + '<p>Final saved paragraph.</p>', encoding="utf-8")
        source = self.root / "browser snapshot.mhtml"
        with sync_playwright() as playwright:
            channel = {"edge": "msedge", "chrome": "chrome", "chromium": "chromium"}[self.options.browser]
            browser = playwright.chromium.launch(channel=channel, headless=True, chromium_sandbox=True, timeout=20000)
            try:
                context = browser.new_context()
                files = {"/long-page.html": html, "/style.css": original / "style.css", "/photo.png": original / "photo.png"}

                def website_response(route):
                    asset = files.get(urlsplit(route.request.url).path)
                    if asset is None:
                        route.fulfill(status=404, body="Not found")
                    else:
                        content_type = {".html": "text/html", ".css": "text/css", ".png": "image/png"}[asset.suffix]
                        route.fulfill(path=str(asset), content_type=content_type)

                # Simulate a web origin without a server or any external network traffic.
                context.route("**/*", website_response)
                page = context.new_page()
                page.goto("https://archive.example.invalid/long-page.html", wait_until="load", timeout=20000)
                snapshot = page.context.new_cdp_session(page).send("Page.captureSnapshot", {"format": "mhtml"})
                source.write_bytes(snapshot["data"].encode("utf-8"))
            finally:
                browser.close()
        # Remove every original asset: only the single archive remains available.
        for asset in original.iterdir():
            asset.unlink()
        original.rmdir()
        result = convert_mhtml(source, options=self.options)
        self.assertFalse(result.warnings)
        with self.pdf.open(result.path) as document:
            self.assertGreaterEqual(len(document), 3)
            text = "\n".join(page.get_text() for page in document)
            for number in range(100):
                self.assertIn(f"Archive paragraph {number:03d}", text)
            self.assertIn("Saved caf\u00e9 notes.", text)
            self.assertIn("Final saved paragraph.", document[-1].get_text())
            self.assertGreater(sum(len(page.get_images()) for page in document), 0)

    def test_missing_archived_asset_preserves_existing_output(self):
        source = self.root / "missing asset.mhtml"
        source.write_bytes(EXAMPLE.read_bytes().replace(b"<body>", b'<body><img src="https://example.invalid/not-saved.png">'))
        target = self.root / "existing.pdf"
        target.write_bytes(b"keep the original output")
        with self.assertRaisesRegex(RuntimeError, "could not load from this archive"):
            convert_mhtml(source, target, self.options, overwrite=True)
        self.assertEqual(target.read_bytes(), b"keep the original output")
        self.assertFalse(list(self.root.glob(".mhtml-to-pdf-*.pdf")))
        result = convert_mhtml(source, target, replace(self.options, allow_missing_assets=True), overwrite=True)
        self.assertTrue(result.warnings)
        with self.pdf.open(result.path) as document:
            self.assertIn("Archived Field Notes", document[0].get_text())

    def test_empty_render_is_an_error_not_a_successful_blank_pdf(self):
        source = self.root / "empty.mhtml"
        source.write_bytes(b'MIME-Version: 1.0\r\nContent-Type: multipart/related; boundary="test"\r\n\r\n'
                           b'--test\r\nContent-Type: text/html\r\nContent-Location: https://example.invalid/empty\r\n\r\n'
                           b'<html><head></head><body></body></html>\r\n--test--\r\n')
        with self.assertRaisesRegex(RuntimeError, "empty archive"):
            convert_mhtml(source, options=self.options)
        self.assertFalse(source.with_suffix(".pdf").exists())


if __name__ == "__main__":
    unittest.main()
