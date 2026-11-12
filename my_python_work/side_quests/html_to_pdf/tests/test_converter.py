from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from converter import PdfOptions, convert_html, print_overrides, validate_paths


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "my report.HTML"
        self.source.write_text("<!doctype html><h1>Report</h1>", encoding="utf-8")

    def test_default_and_explicit_output_paths(self):
        source, target = validate_paths(self.source)
        self.assertEqual(source, self.source.resolve())
        self.assertEqual(target, source.with_suffix(".pdf"))
        _, target = validate_paths(source, self.root / "nested" / "report.pdf")
        self.assertEqual(target.name, "report.pdf")

    def test_bad_input_and_output_paths_are_rejected(self):
        for path in [self.root / "missing.html", self.root]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_paths(path)
        text = self.root / "note.txt"
        text.write_text("hello", encoding="utf-8")
        with self.assertRaises(ValueError):
            validate_paths(text)
        with self.assertRaises(ValueError):
            validate_paths(self.source, self.source)
        with self.assertRaises(ValueError):
            validate_paths(self.source, self.root / "result.txt")

    def test_overwrite_requires_explicit_permission(self):
        target = self.source.with_suffix(".pdf")
        target.write_bytes(b"existing file")
        with self.assertRaises(FileExistsError):
            validate_paths(self.source)
        self.assertEqual(validate_paths(self.source, overwrite=True)[1], target)
        self.assertEqual(target.read_bytes(), b"existing file")

    def test_invalid_options_are_rejected(self):
        for options in [
            PdfOptions(paper="unknown"), PdfOptions(browser="unknown"),
            PdfOptions(landscape=True), PdfOptions(margin_mm=-1), PdfOptions(margin_mm=float("nan")),
            PdfOptions(timeout_seconds=0), PdfOptions(timeout_seconds=float("inf")),
            PdfOptions(delay_ms=-1), PdfOptions(delay_ms=30000),
        ]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                options.validate()

    def test_print_overrides_are_explicit(self):
        self.assertEqual(print_overrides(PdfOptions()), "")
        css = print_overrides(PdfOptions(paper="letter", landscape=True, margin_mm=12))
        self.assertIn("size: Letter landscape !important", css)
        self.assertIn("margin: 12mm !important", css)

    def test_cli_reports_bad_input_without_a_traceback(self):
        result = subprocess.run(
            [sys.executable, str(APP_DIR / "app.py"), str(self.root / "missing.html")],
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


@unittest.skipUnless(os.environ.get("HTML_PDF_BROWSER"), "Set HTML_PDF_BROWSER=edge, chrome, or chromium for real PDF tests")
class BrowserPdfTests(unittest.TestCase):
    def setUp(self):
        try:
            import pymupdf
        except ImportError:
            self.skipTest("Install requirements-dev.txt for PDF inspection")
        self.pdf = pymupdf
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.options = PdfOptions(browser=os.environ["HTML_PDF_BROWSER"], delay_ms=0)

    def test_real_print_css_text_page_breaks_and_paper_override(self):
        source = APP_DIR / "examples" / "print_demo.html"
        result = convert_html(source, self.root / "nested" / "demo.pdf", self.options)
        with self.pdf.open(result.path) as document:
            self.assertEqual(len(document), 2)
            self.assertAlmostEqual(document[0].rect.width, 595.3, delta=2)
            text = "\n".join(page.get_text() for page in document)
            self.assertIn("Project Notes", text)
            self.assertNotIn("This line is visible on screen", text)
            self.assertIn("Next Steps", document[1].get_text())
            positions = document[0].search_for("Project Notes")
            self.assertTrue(positions)
            self.assertAlmostEqual(positions[0].x0, 18 / 25.4 * 72, delta=2)
        forced = convert_html(source, self.root / "letter.pdf", replace(self.options, paper="letter", landscape=True, margin_mm=10))
        with self.pdf.open(forced.path) as document:
            self.assertAlmostEqual(document[0].rect.width, 792, delta=2)
            self.assertAlmostEqual(document[0].rect.height, 612, delta=2)
            self.assertAlmostEqual(document[0].search_for("Project Notes")[0].x0, 10 / 25.4 * 72, delta=2)

    def test_relative_assets_lazy_image_and_dynamic_ready_marker(self):
        image = self.pdf.Pixmap(self.pdf.csRGB, self.pdf.IRect(0, 0, 30, 30), False)
        image.clear_with(0)
        image.save(str(self.root / "image.png"))
        (self.root / "style.css").write_text("@page {size: A4;} h1 {color: #246333;}", encoding="utf-8")
        source = self.root / "relative assets.html"
        source.write_text('''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="style.css">
            <h1>Local assets</h1><div style="height:1200px"></div><img src="image.png" loading="lazy">
            <div id="ready"></div><script>setTimeout(() => {
                const ready = document.getElementById('ready');
                ready.textContent = 'Dynamic content ready'; ready.dataset.loaded = 'yes';
            }, 300);</script>''', encoding="utf-8")
        result = convert_html(source, self.root / "assets.pdf", replace(self.options, wait_selector="#ready[data-loaded='yes']"))
        with self.pdf.open(result.path) as document:
            self.assertIn("Dynamic content ready", "\n".join(page.get_text() for page in document))
            self.assertGreater(sum(len(page.get_images()) for page in document), 0)

    def test_broken_assets_do_not_replace_an_existing_pdf(self):
        source = self.root / "missing.html"
        source.write_text('<h1>Missing image</h1><img src="missing.png">', encoding="utf-8")
        output = self.root / "existing.pdf"
        output.write_bytes(b"keep this original file")
        with self.assertRaises(RuntimeError):
            convert_html(source, output, self.options, overwrite=True)
        self.assertEqual(output.read_bytes(), b"keep this original file")
        self.assertFalse(list(self.root.glob(".html-to-pdf-*.pdf")))
        result = convert_html(source, output, replace(self.options, allow_missing_assets=True), overwrite=True)
        self.assertTrue(result.warnings)
        with self.pdf.open(result.path) as document:
            self.assertIn("Missing image", document[0].get_text())

    def test_readiness_timeout_leaves_no_output(self):
        source = self.root / "not-ready.html"
        source.write_text("<h1>Not ready</h1>", encoding="utf-8")
        output = self.root / "not-created.pdf"
        with self.assertRaises((RuntimeError, TimeoutError)):
            convert_html(source, output, replace(self.options, timeout_seconds=5, wait_selector="#never"))
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
