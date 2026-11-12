"""Exercise a local workbook in a disposable browser profile, not personal drafts."""
import argparse
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"


def saved(page):
    expect(page.locator("#save-status")).to_have_text("Saved on this device")


def paste_image(page, document_target=False):
    page.evaluate("""async (documentTarget) => {
        const canvas = document.createElement('canvas');
        canvas.width = 640; canvas.height = 320;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#e2f1e9'; ctx.fillRect(0, 0, 640, 320);
        ctx.fillStyle = '#185c53'; ctx.font = '30px sans-serif';
        ctx.fillText('Evidence screenshot - TEST', 35, 70);
        ctx.fillStyle = '#337fb0'; ctx.fillRect(35, 110, 340, 150);
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
        const data = new DataTransfer(); data.items.add(new File([blob], 'test.png', {type: 'image/png'}));
        (documentTarget ? document.body : document.activeElement).dispatchEvent(new ClipboardEvent('paste', {
            clipboardData: data, bubbles: true, cancelable: true
        }));
    }""", document_target)


def check_layout(page):
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "Horizontal page overflow"
    assert page.evaluate("""[...document.querySelectorAll('button')].filter(node => node.getClientRects().length)
        .every(node => node.scrollWidth <= node.clientWidth + 2)"""), "Button text overflows"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, help="Optional real Markdown template to inspect without editing it")
    args = parser.parse_args()
    OUTPUT.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=True, chromium_sandbox=True)
        try:
            page = browser.new_page(viewport={"width": 1360, "height": 960}, accept_downloads=True)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto((ROOT / "index.html").as_uri())
            page.evaluate("EvidenceDesk.ready")
            page.locator("#load-example").click()
            expect(page.locator("#product-title")).to_have_text("Sample air duster")
            page.locator(".entry textarea").first.fill("=SUM(1,2) - AED 200")
            page.locator(".entry textarea").nth(1).fill("AED 25")
            saved(page)
            clipboard = page.locator(".entry .screenshot-input").first
            clipboard.click()
            expect(clipboard).to_be_focused()
            paste_image(page)
            expect(page.locator(".evidence-item")).to_have_count(1)
            expect(clipboard).to_be_focused()
            assert page.evaluate("EvidenceDesk.getState().images[0].contextId === EvidenceDesk.getState().schema.sections[1].items[0].id")
            page.get_by_role("textbox", name="E-001 Caption", exact=True).fill("Test price capture")
            page.get_by_role("textbox", name="E-001 Source URL or reference", exact=True).fill("https://example.com/product")
            saved(page)
            page.reload(); page.evaluate("EvidenceDesk.ready")
            expect(page.locator(".entry textarea").first).to_have_value("=SUM(1,2) - AED 200")
            expect(page.locator(".evidence-item img")).to_have_count(3)  # preview and two tool icons
            page.get_by_role("button", name="Preview E-001", exact=True).click()
            expect(page.locator("#image-preview")).to_be_visible()
            page.locator("#close-preview").click()
            old = page.evaluate("EvidenceDesk.getState().project.markdown")
            revised = old.replace("## Business inputs", "## 11. Business inputs").replace("| Shipping cost |", "| New shipping cost |")
            revised += '\n## Security check\n\n<script>window.importedScriptRan=true</script>\n\n<img src="https://example.invalid/leak" onerror="window.importedScriptRan=true">\n'
            page.locator("#update-md").click()
            page.locator("#md-file").set_input_files({"name": "Updated.md", "mimeType": "text/markdown", "buffer": revised.encode()})
            expect(page.locator("#review-banner")).to_be_visible()
            expect(page.locator(".entry textarea").first).to_have_value("=SUM(1,2) - AED 200")
            expect(page.locator(".entry textarea").nth(1)).to_have_value("")
            assert page.evaluate("EvidenceDesk.getState().images.length") == 1
            # A body-targeted paste still belongs to the focused entry, not the section.
            other_clipboard = page.locator(".entry .screenshot-input").nth(1)
            other_clipboard.click(); expect(other_clipboard).to_be_focused()
            paste_image(page, document_target=True)
            expect(page.locator(".evidence-item")).to_have_count(2)
            expect(other_clipboard).to_be_focused()
            assert page.evaluate("EvidenceDesk.getState().images[1].contextId === EvidenceDesk.getState().schema.sections[1].items[1].id")
            page.once("dialog", lambda dialog: dialog.accept())
            page.locator(".entry").nth(1).get_by_role("button", name="Remove screenshot", exact=True).click()
            expect(page.locator(".evidence-item")).to_have_count(1)
            # Section-level boxes use their own context and support keyboard focus too.
            section_clipboard = page.locator("#section-evidence .screenshot-input")
            section_clipboard.focus(); expect(section_clipboard).to_be_focused()
            paste_image(page)
            expect(page.locator("#section-evidence .evidence-item")).to_have_count(1)
            assert page.evaluate("EvidenceDesk.getState().images[1].contextId === EvidenceDesk.getState().schema.sections[1].id")
            page.once("dialog", lambda dialog: dialog.accept())
            page.locator("#section-evidence").get_by_role("button", name="Remove screenshot", exact=True).click()
            expect(page.locator(".evidence-item")).to_have_count(1)
            page.locator("#section-status").select_option("Complete"); saved(page)
            check_layout(page)
            page.screenshot(path=str(OUTPUT / "desktop.png"), full_page=True)
            page.set_viewport_size({"width": 390, "height": 844})
            check_layout(page)
            page.screenshot(path=str(OUTPUT / "mobile.png"), full_page=True)
            page.locator("#toggle-nav").click()
            expect(page.locator("#sidebar")).to_be_visible()
            page.locator("#sections button").filter(has_text="Security check").click()
            assert not page.evaluate("Boolean(window.importedScriptRan)")
            assert page.locator("#section-content img").count() == 0
            check_layout(page)
            page.set_viewport_size({"width": 1360, "height": 960})
            with page.expect_download() as downloaded:
                page.locator("#export-xlsx").click()
            xlsx = OUTPUT / "test-workbook.xlsx"; downloaded.value.save_as(xlsx)
            with zipfile.ZipFile(xlsx) as archive:
                media = [name for name in archive.namelist() if name.startswith("xl/media/") and not name.endswith("/")]
                assert len(media) == 1 and archive.read(media[0]).startswith(b"\x89PNG")
                strings = archive.read("xl/sharedStrings.xml").decode()
                assert "AED 200" in strings and "AED 25" in strings and "Test price capture" in strings
                assert "هواء" in strings
                for name in archive.namelist():
                    if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"):
                        assert not ET.fromstring(archive.read(name)).findall(".//{*}f"), "Answers became formulas"
                assert any(name.startswith("xl/drawings/drawing") for name in archive.namelist())
            with page.expect_download() as downloaded:
                page.locator("#backup").click()
            backup = OUTPUT / "test-backup.zip"; downloaded.value.save_as(backup)
            with zipfile.ZipFile(backup) as archive:
                assert {"report.md", "template.md", "project.json"}.issubset(archive.namelist())
                assert len([name for name in archive.namelist() if name.startswith("images/")]) == 1
            original_id = page.evaluate("EvidenceDesk.getState().project.id")
            page.locator("#backup-file").set_input_files(backup)
            page.wait_for_function("id => EvidenceDesk.getState().project.id !== id", arg=original_id)
            assert page.evaluate("async () => (await EvidenceStore.getProjects()).length") == 2
            assert page.evaluate("EvidenceDesk.getState().images.length") == 1
            # A restore must not overwrite the original workbook's image records.
            assert page.evaluate("async id => (await EvidenceStore.getImages(id)).length", original_id) == 1
            page.evaluate("() => { window.print = () => { window.printCheck = {images: document.querySelectorAll('#print-report figure img').length, text: document.querySelector('#print-report').textContent}; }; }")
            page.locator("#print").click()
            page.wait_for_function("window.printCheck")
            assert page.evaluate("printCheck.images") == 1
            assert "AED 200" in page.evaluate("printCheck.text")
            # Corrupt backups are rejected without adding any workbooks.
            assert page.evaluate("""async () => {
                try { await EvidenceExports.restore(new File(['no zip'], 'bad.zip')); return false; }
                catch (_) { return true; }
            }""")
            if args.template:
                page.locator("#import-md").click(); page.locator("#md-file").set_input_files(args.template)
                page.wait_for_function("EvidenceDesk.getState().project.filename !== 'Updated.md'")
                state = page.evaluate("({sections: EvidenceDesk.getState().schema.sections.length, fields: EvidenceDesk.getState().schema.fields.length})")
                assert state["fields"] > 100, state
                page.locator("#sections button").filter(has_text="UGC").last.click()
                check_layout(page)
                page.screenshot(path=str(OUTPUT / "actual-template.png"), full_page=True)
                print(f"Actual template: {state['sections']} sections, {state['fields']} editable cells")
            assert not errors, errors
            print("PASS: editing, pasted evidence, reload, template update, mobile layout, sanitization, embedded Excel image, ZIP restore and printing")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
