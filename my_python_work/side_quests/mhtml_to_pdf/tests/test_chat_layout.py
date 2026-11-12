from dataclasses import replace
from email import policy
from email.message import EmailMessage
from pathlib import Path
from tempfile import TemporaryDirectory
import base64
import os
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from html_to_pdf.converter import PdfOptions, convert_mhtml


@unittest.skipUnless(os.environ.get("MHTML_PDF_BROWSER"), "Set MHTML_PDF_BROWSER for chat PDF regression tests")
class ChatLayoutTests(unittest.TestCase):
    def setUp(self):
        import pymupdf
        self.pdf = pymupdf
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.options = PdfOptions(browser=os.environ["MHTML_PDF_BROWSER"], delay_ms=0)

    def archive(self, html, name="chat.mhtml"):
        message = EmailMessage()
        message.make_related()
        document = EmailMessage()
        document.set_content(html, subtype="html", charset="utf-8", cte="quoted-printable")
        document["Content-Location"] = "https://chatgpt.com/c/saved-test"
        message.attach(document)
        source = self.root / name
        source.write_bytes(message.as_bytes(policy=policy.SMTP))
        return source

    def test_auto_reflows_fixed_height_chat_preserves_content_and_formatting(self):
        image = self.pdf.Pixmap(self.pdf.csRGB, self.pdf.IRect(0, 0, 30, 30), False)
        image.clear_with(120)
        image_data = base64.b64encode(image.tobytes("png")).decode("ascii")
        paragraphs = "".join(f"<p>Saved paragraph {number:03d}: All of this message must appear in the PDF.</p>"
                             for number in range(80))
        source = self.archive(f'''<!doctype html><meta charset="utf-8"><title>Saved conversation</title>
            <style>html,body{{height:720px;overflow:hidden}} main{{height:650px;overflow:auto}}
            .sr-only{{position:absolute;width:1px;height:1px;clip:rect(0,0,0,0)}}
            .message{{position:relative;min-height:100px}} .hidden{{display:none}}</style>
            <aside>Sidebar private history</aside><main>
            <div class="message"><h4 class="sr-only" data-conversation-role="user">You said:</h4>
                <div data-user-message-bubble style="white-space:pre-wrap">Opening question\nA separate user line</div><button>Edit message</button></div>
            <div class="message"><h4 class="sr-only" data-conversation-role="assistant">ChatGPT said:</h4>
                <div>{paragraphs}<p><strong>Bold saved text</strong> with <em>emphasis</em>.</p>
                <pre><code>print('saved code')</code></pre><a href="https://example.com/reference">Reference link</a>
                <table><thead><tr><th>Column title</th></tr></thead><tbody><tr><td>Saved cell</td></tr></tbody></table>
                <img src="data:image/png;base64,{image_data}">
                <span class="hidden">Hidden duplicate</span></div></div>
            <div><h4 data-conversation-role="user">You said:</h4><p>Closing question</p></div>
            <div><h4 data-conversation-role="assistant">ChatGPT said:</h4><p>Final saved answer.</p></div>
            <form>Message composer controls</form></main>''')
        original_bytes = source.read_bytes()
        result = convert_mhtml(source, options=self.options)
        self.assertEqual((result.layout, result.message_count), ("chat", 4))
        self.assertEqual(source.read_bytes(), original_bytes)
        with self.pdf.open(result.path) as document:
            self.assertGreaterEqual(len(document), 3)
            opening = document[0].search_for("Opening question")[0]
            separate = document[0].search_for("A separate user line")[0]
            self.assertGreater(separate.y0 - opening.y0, 12)
            text = "\n".join(page.get_text() for page in document)
            for number in range(80):
                self.assertIn(f"Saved paragraph {number:03d}", text)
            for expected in ("Opening question", "Bold saved text", "print('saved code')", "Saved cell", "Closing question"):
                self.assertIn(expected, text)
            self.assertIn("Final saved answer.", document[-1].get_text())
            for excluded in ("Sidebar private history", "Edit message", "Message composer controls", "Hidden duplicate", "You said:"):
                self.assertNotIn(excluded, text)
            self.assertGreater(sum(len(page.get_images()) for page in document), 0)
            self.assertTrue(any(link.get("uri") == "https://example.com/reference"
                                for page in document for link in page.get_links()))
            for page in document:
                for word in page.get_text("words"):
                    self.assertGreaterEqual(word[0], 0)
                    self.assertLessEqual(word[2], page.rect.width + 1)
                    self.assertGreaterEqual(word[1], 0)
                    self.assertLessEqual(word[3], page.rect.height + 1)

    def test_legacy_role_markup_and_original_layout_opt_out(self):
        source = self.archive('''<!doctype html><title>Legacy chat</title><aside>Original sidebar</aside><main>
            <article data-testid="conversation-turn-1"><div data-message-author-role="user">
            <h4 data-conversation-role="user">You said:</h4><p>One saved prompt</p></div></article>
            <article data-testid="conversation-turn-2"><div data-message-author-role="assistant">
            <h4 data-conversation-role="assistant">ChatGPT said:</h4><p>One saved answer</p></div></article></main>''')
        result = convert_mhtml(source, self.root / "chat.pdf", replace(self.options, paper="letter", margin_mm=12))
        self.assertEqual(result.message_count, 2)
        with self.pdf.open(result.path) as document:
            self.assertAlmostEqual(document[0].rect.width, 612, delta=2)
            self.assertNotIn("Original sidebar", document[0].get_text())
            self.assertIn("One saved answer", document[0].get_text())
        original = convert_mhtml(source, self.root / "original.pdf", replace(self.options, layout="original"))
        self.assertEqual(original.layout, "original")
        with self.pdf.open(original.path) as document:
            self.assertIn("Original sidebar", document[0].get_text())

    def test_explicit_chat_layout_rejects_non_chat_document(self):
        source = self.archive("<!doctype html><h1>Ordinary article</h1><p>Content</p>")
        with self.assertRaisesRegex(ValueError, "No saved chat messages"):
            convert_mhtml(source, options=replace(self.options, layout="chat"))
        self.assertFalse(source.with_suffix(".pdf").exists())


if __name__ == "__main__":
    unittest.main()
