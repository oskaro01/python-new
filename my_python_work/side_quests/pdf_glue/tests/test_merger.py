from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import os
import subprocess
import sys
import time
import unittest

import pymupdf
from pypdf import PdfReader, PdfWriter

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))
from merger import merge_pdfs, validate_paths


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.one = self.make_pdf("pdf 1.pdf", ["ONE A", "ONE B"])
        self.three = self.make_pdf("pdf 3.pdf", ["THREE"], rotation=90)
        self.eight = self.make_pdf("pdf 8.pdf", ["EIGHT"])

    def make_pdf(self, name, labels, *, rotation=0, field_value=None):
        path = self.root / name
        with pymupdf.open() as document:
            for label in labels:
                page = document.new_page(width=595, height=842)
                page.insert_text((72, 72), label, fontsize=20)
                page.insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(70, 90, 180, 110),
                                  "uri": "https://example.com/reference"})
                image = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 20, 20), False)
                image.clear_with(100)
                page.insert_image(pymupdf.Rect(72, 120, 112, 160), stream=image.tobytes("png"))
                if field_value is not None:
                    widget = pymupdf.Widget()
                    widget.field_name = "shared_name"
                    widget.field_type = pymupdf.PDF_WIDGET_TYPE_TEXT
                    widget.field_value = field_value
                    widget.rect = pymupdf.Rect(72, 180, 250, 205)
                    page.add_widget(widget)
                page.set_rotation(rotation)
            document.set_toc([[1, f"Inside {name}", 1]])
            document.save(path)
        return path

    def test_exact_order_repeats_quality_rotation_links_and_bookmarks(self):
        sources = [self.one, self.three, self.eight, self.three]
        originals = {path: path.read_bytes() for path in sources}
        progress = []
        result = merge_pdfs(sources, self.root / "nested" / "combined.pdf",
                            progress=lambda index, total, path: progress.append((index, total, path)))
        self.assertEqual((result.file_count, result.page_count), (4, 5))
        self.assertGreater(result.size_bytes, 0)
        self.assertEqual([item[2] for item in progress], sources)
        with pymupdf.open(result.path) as document:
            expected = ["ONE A", "ONE B", "THREE", "EIGHT", "THREE"]
            for page, label in zip(document, expected):
                self.assertIn(label, page.get_text())
                self.assertEqual(len(page.get_images()), 1)
                self.assertTrue(any(link.get("uri") == "https://example.com/reference" for link in page.get_links()))
                self.assertAlmostEqual(page.mediabox.width, 595)
                self.assertAlmostEqual(page.mediabox.height, 842)
            self.assertEqual([page.rotation for page in document], [0, 0, 90, 0, 90])
            roots = [(entry[1], entry[2]) for entry in document.get_toc() if entry[0] == 1]
            self.assertEqual(roots, [("1. pdf 1", 1), ("2. pdf 3", 3), ("3. pdf 8", 4), ("4. pdf 3", 5)])
        for source, content in originals.items():
            self.assertEqual(source.read_bytes(), content)

    def test_repeated_forms_get_independent_field_names(self):
        first = self.make_pdf("form one.pdf", ["FIRST FORM"], field_value="Alice")
        second = self.make_pdf("form two.pdf", ["SECOND FORM"], field_value="Bob")
        result = merge_pdfs([first, second, first], self.root / "forms.pdf")
        with result.path.open("rb") as handle:
            fields = PdfReader(handle).get_form_text_fields(True)
        self.assertEqual(fields, {"document_1.shared_name": "Alice", "document_2.shared_name": "Bob",
                                  "document_3.shared_name": "Alice"})

    def test_bad_paths_and_source_replacement_are_rejected(self):
        for sources, target in (
            ([self.one], self.root / "out.pdf"), ([self.one, self.root / "missing.pdf"], self.root / "out.pdf"),
            ([self.one, self.three], self.root / "wrong.txt"), ([self.one, self.three], self.one),
            ([self.one, self.three], ""),
        ):
            with self.subTest(sources=sources, target=target), self.assertRaises(ValueError):
                validate_paths(sources, target, overwrite=True)
        empty = self.root / "empty.pdf"
        empty.touch()
        with self.assertRaisesRegex(ValueError, "empty"):
            merge_pdfs([self.one, empty], self.root / "out.pdf")

    def test_existing_output_needs_permission_and_is_replaced_only_after_success(self):
        output = self.root / "existing.pdf"
        output.write_bytes(b"original output")
        with self.assertRaises(FileExistsError):
            merge_pdfs([self.one, self.three], output)
        bad = self.root / "bad.pdf"
        bad.write_bytes(b"%PDF-1.7\nnot actually a PDF")
        with self.assertRaises(ValueError):
            merge_pdfs([self.one, bad], output, overwrite=True)
        self.assertEqual(output.read_bytes(), b"original output")
        result = merge_pdfs([self.one, self.three], output, overwrite=True)
        with result.path.open("rb") as handle:
            self.assertEqual(len(PdfReader(handle).pages), 3)

    def test_write_failure_cleans_temporary_file_and_preserves_existing_output(self):
        output = self.root / "existing.pdf"
        output.write_bytes(b"original output")

        def broken_write(writer, stream):
            stream.write(b"partial output")
            raise OSError("Simulated disk write failure")

        with patch.object(PdfWriter, "write", broken_write):
            with self.assertRaisesRegex(OSError, "disk write failure"):
                merge_pdfs([self.one, self.three], output, overwrite=True)
        self.assertEqual(output.read_bytes(), b"original output")
        self.assertFalse(list(self.root.glob(".pdf-glue-*.pdf")))

    def test_new_output_created_during_merge_is_not_overwritten(self):
        output = self.root / "race.pdf"

        def competing_output(index, _total, _source):
            if index == 1:
                output.write_bytes(b"another program's output")

        with self.assertRaises(FileExistsError):
            merge_pdfs([self.one, self.three], output, progress=competing_output)
        self.assertEqual(output.read_bytes(), b"another program's output")
        self.assertFalse(list(self.root.glob(".pdf-glue-*.pdf")))

    def test_encrypted_and_zero_page_inputs_have_clear_errors(self):
        encrypted = self.root / "locked.pdf"
        with PdfWriter() as writer:
            writer.add_blank_page(width=100, height=100)
            writer.encrypt("test-password")
            writer.write(encrypted)
        with self.assertRaisesRegex(ValueError, "unlocked PDF"):
            merge_pdfs([self.one, encrypted], self.root / "out.pdf")
        no_pages = self.root / "no pages.pdf"
        with PdfWriter() as writer:
            writer.write(no_pages)
        with self.assertRaisesRegex(ValueError, "no pages"):
            merge_pdfs([self.one, no_pages], self.root / "out.pdf")

    def test_cli_keeps_argument_order_and_reports_invalid_input(self):
        output = self.root / "cli.pdf"
        result = subprocess.run([sys.executable, str(APP_DIR / "app.py"), str(self.eight), str(self.one),
                                 str(self.eight), "--output", str(output)], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        with pymupdf.open(output) as document:
            self.assertEqual(len(document), 4)
            self.assertEqual([page.get_text().strip() for page in document], ["EIGHT", "ONE A", "ONE B", "EIGHT"])
        invalid = subprocess.run([sys.executable, str(APP_DIR / "app.py"), str(self.one), "-o", str(self.root / "bad.pdf")],
                                 capture_output=True, text=True, timeout=20)
        self.assertEqual(invalid.returncode, 1)
        self.assertIn("at least two", invalid.stderr)
        self.assertNotIn("Traceback", invalid.stderr)


@unittest.skipUnless(os.environ.get("PDF_GLUE_GUI"), "Set PDF_GLUE_GUI=1 to check native desktop controls")
class DesktopQueueTests(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        from gui import PdfGlueApp
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.app = PdfGlueApp(self.root)

    def test_reorder_duplicate_sort_remove_and_empty_clear(self):
        app = self.app
        app.clear()
        app.add_files(["pdf 1.pdf", "pdf 3.pdf", "pdf 8.pdf", "pdf 3.pdf"])
        names = lambda: [path.name for path in app.ordered_paths()]
        self.assertEqual(names(), ["pdf 1.pdf", "pdf 3.pdf", "pdf 8.pdf", "pdf 3.pdf"])
        items = app.tree.get_children()
        app.tree.selection_set((items[2], items[3]))
        app.move(-1)
        self.assertEqual(names(), ["pdf 1.pdf", "pdf 8.pdf", "pdf 3.pdf", "pdf 3.pdf"])
        app.move(1)
        self.assertEqual(names(), ["pdf 1.pdf", "pdf 3.pdf", "pdf 8.pdf", "pdf 3.pdf"])
        app.tree.selection_set(app.tree.get_children()[0])
        app.duplicate()
        self.assertEqual(names(), ["pdf 1.pdf", "pdf 1.pdf", "pdf 3.pdf", "pdf 8.pdf", "pdf 3.pdf"])
        app.remove()
        self.assertEqual(len(app.ordered_paths()), 4)
        app.add_files(["pdf 10.pdf", "pdf 2.pdf"])
        app.sort_by_name()
        self.assertEqual(names(), ["pdf 1.pdf", "pdf 2.pdf", "pdf 3.pdf", "pdf 3.pdf", "pdf 8.pdf", "pdf 10.pdf"])
        app.busy = True
        snapshot = app.ordered_paths()
        app.clear()
        self.assertEqual(app.ordered_paths(), snapshot)
        app.busy = False
        app.clear()
        self.assertEqual(app.ordered_paths(), ())
        self.assertEqual(str(app.merge_button["state"]), "disabled")
        self.root.update_idletasks()
        self.assertLessEqual(self.root.winfo_reqwidth(), self.root.minsize()[0])

    def test_desktop_merge_completes_and_restores_controls(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "source.pdf"
            target = Path(folder) / "merged.pdf"
            with PdfWriter() as writer:
                writer.add_blank_page(width=300, height=400)
                writer.write(source)
            self.app.add_files([source, source])
            self.app.output.set(str(target))
            with patch("gui.messagebox.askyesno", return_value=False), patch("gui.messagebox.showerror") as errors:
                self.app.start()
                self.assertTrue(self.app.busy)
                self.assertEqual(str(self.app.merge_button["state"]), "disabled")
                deadline = time.monotonic() + 15
                while self.app.busy and time.monotonic() < deadline:
                    self.root.update()
                    time.sleep(0.01)
                self.assertFalse(self.app.busy)
                errors.assert_not_called()
            with target.open("rb") as handle:
                self.assertEqual(len(PdfReader(handle).pages), 2)
            self.assertEqual(str(self.app.merge_button["state"]), "normal")
            self.assertIn("Saved 2 pages from 2 PDFs", self.app.status.get())


if __name__ == "__main__":
    unittest.main()
