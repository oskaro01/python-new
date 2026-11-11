"""Run in an isolated Edge profile; never opens the user's actual notes."""

from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def paste_screenshot(page, count=1):
    return page.evaluate("""async (count) => {
        const canvas = document.createElement('canvas');
        canvas.width = 80;
        canvas.height = 40;
        canvas.getContext('2d').fillRect(0, 0, 80, 40);
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
        const clipboard = new DataTransfer();
        for (let i = 0; i < count; i++) {
            clipboard.items.add(new File([blob], 'screenshot.png', {type: 'image/png'}));
        }
        const event = new ClipboardEvent('paste', {
            clipboardData: clipboard, bubbles: true, cancelable: true,
        });
        document.querySelector('#note-body').dispatchEvent(event);
        return event.defaultPrevented;
    }""", count)


def expect_no_stored_images(page):
    page.wait_for_function("""async () => {
        const count = await new DaynotesImages.ScreenshotStore().transaction(
            'readonly', (images, done) => {
                const request = images.count();
                request.onsuccess = () => done(request.result);
            });
        return count === 0;
    }""")


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        try:
            page = browser.new_page(accept_downloads=True)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.add_init_script("""const originalNow = Date.now.bind(Date);
                window.testClockOffset = 0;
                Date.now = () => originalNow() + window.testClockOffset;
            """)
            page.goto((Path(__file__).resolve().parents[1] / "index.html").as_uri())
            assert paste_screenshot(page)
            expect(page.locator(".screenshot")).to_have_count(1)
            expect(page.locator("#save-status")).to_have_text("Saved")
            expect(page.locator("#download-note")).to_be_disabled()
            images = page.evaluate("""async () => {
                const note = JSON.parse(localStorage.getItem('daynotes.v1')).notes[0];
                const images = await new DaynotesImages.ScreenshotStore().list(note.id);
                return images.map(image => ({sameExpiry: image.expiresAt === note.expiresAt}));
            }""")
            assert images == [{"sameExpiry": True}]
            page.reload()
            expect(page.locator(".screenshot")).to_have_count(1)
            page.get_by_role("button", name="View screenshot 1", exact=True).click()
            expect(page.get_by_role("dialog", name="Screenshot preview", exact=True)).to_be_visible()
            page.get_by_role("button", name="Close", exact=True).click()
            with page.expect_download() as download:
                page.get_by_role("button", name="Download screenshot", exact=True).click()
            assert download.value.suggested_filename == "screenshot-1.png"
            paste_screenshot(page, 4)
            expect(page.locator(".screenshot")).to_have_count(5)
            paste_screenshot(page)
            expect(page.locator("#toast")).to_have_text("You can attach up to 5 screenshots per note.")
            expect(page.locator(".screenshot")).to_have_count(5)
            page.locator("#delete-note").click()
            page.locator("#confirm-delete").click()
            expect(page.locator(".screenshot")).to_have_count(0)
            expect_no_stored_images(page)
            paste_screenshot(page)
            expect(page.locator(".screenshot")).to_have_count(1)
            page.evaluate("window.testClockOffset = 86401000; window.dispatchEvent(new Event('focus'));")
            expect(page.locator(".screenshot")).to_have_count(0)
            expect_no_stored_images(page)
            assert page.evaluate("localStorage.getItem('daynotes.v1')") is None
            assert not errors, errors
            print("PASS: screenshot paste, persistence, preview, download, limits, deletion, and expiry.")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
