"""Exercise real IndexedDB in an isolated Edge profile, never personal notes."""

from pathlib import Path

from playwright.sync_api import expect, sync_playwright


URL = (Path(__file__).resolve().parents[1] / "index.html").as_uri()
DAY_MS = 86400000


def ready(page):
    page.evaluate("window.DaynotesReady")


def records(page):
    return page.evaluate("""async () => {
        const store = new DaynotesStorage.NotesStore();
        try { return await store.read(); } finally { store.close(); }
    }""")


def seed_old_database(page, corrupt=False):
    # Rebuild only this test profile's database in the old screenshot-only format.
    return page.evaluate("""async (corrupt) => {
        const now = Date.now(), day = 86400000;
        const note = {id: 'legacy-note', title: 'Keep this', body: 'Old Markdown',
            createdAt: now - 2 * day, updatedAt: now - day, expiresAt: now - day};
        const expired = {...note, id: 'expired-note', createdAt: now - 4 * day};
        const raw = corrupt ? 'broken json' : JSON.stringify({version: 1, notes: [note, expired]});
        const canvas = document.createElement('canvas'); canvas.width = 8; canvas.height = 8;
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
        (await DaynotesStorage.openDatabase()).close();
        await new Promise((resolve, reject) => {
            const request = indexedDB.deleteDatabase(DaynotesStorage.DB_NAME);
            request.onsuccess = resolve; request.onerror = reject; request.onblocked = reject;
        });
        await new Promise((resolve, reject) => {
            const request = indexedDB.open(DaynotesStorage.DB_NAME, 1);
            request.onupgradeneeded = () => {
                const images = request.result.createObjectStore('images', {keyPath: 'id'});
                images.createIndex('noteId', 'noteId'); images.createIndex('expiresAt', 'expiresAt');
            };
            request.onerror = reject;
            request.onsuccess = () => {
                const db = request.result, tx = db.transaction('images', 'readwrite');
                for (const noteId of [note.id, expired.id, 'missing-parent']) {
                    tx.objectStore('images').add({id: noteId, noteId, blob, name: 'old.png',
                        createdAt: note.createdAt, expiresAt: note.expiresAt, width: 8, height: 8});
                }
                tx.oncomplete = () => {db.close(); resolve();}; tx.onabort = reject;
            };
        });
        localStorage.setItem('daynotes.v1', raw);
        localStorage.setItem('daynotes.preferences.v1', JSON.stringify({fontSize: 20}));
        return {note, raw};
    }""", corrupt)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=True, chromium_sandbox=True)
        try:
            context = browser.new_context()
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(URL)
            ready(page)
            legacy = seed_old_database(page)
            page.reload()
            ready(page)
            expect(page.locator("#note-body")).to_have_value("Old Markdown")
            expect(page.locator(".screenshot")).to_have_count(1)
            note = records(page)[0]
            assert note["id"] == legacy["note"]["id"]
            assert note["createdAt"] == legacy["note"]["createdAt"]
            assert note["expiresAt"] == note["createdAt"] + 3 * DAY_MS
            assert page.evaluate("localStorage.getItem('daynotes.v1')") is None
            assert page.evaluate("""async (expiry) => {
                const images = await new DaynotesImages.ScreenshotStore().list('legacy-note');
                const db = await DaynotesStorage.openDatabase();
                return new Promise(resolve => {
                    const tx = db.transaction('images'), request = tx.objectStore('images').getAll();
                    request.onsuccess = () => resolve(request.result.length === 1 &&
                        images[0].expiresAt === expiry);
                });
            }""", note["expiresAt"])
            print("PASS: old database upgrade, text migration, screenshot lifetime, expired/orphan cleanup", flush=True)

            # Simulated failed writes must keep the draft, report failure, and allow retry.
            page.evaluate("""() => {
                window.originalSave = DaynotesStorage.NotesStore.prototype.save;
                DaynotesStorage.NotesStore.prototype.save = async () => {throw new Error('Test write failure');};
            }""")
            body = page.locator("#note-body")
            body.fill("Keep this unsaved draft")
            expect(page.locator("#save-status")).to_have_text("Test write failure")
            expect(body).to_have_value("Keep this unsaved draft")
            assert records(page)[0]["body"] == "Old Markdown"
            page.evaluate("() => { DaynotesStorage.NotesStore.prototype.save = window.originalSave; }")
            page.keyboard.press("Control+s")
            expect(page.locator("#save-status")).to_have_text("Saved")
            assert records(page)[0]["body"] == "Keep this unsaved draft"

            # Edits made during an asynchronous save must not be lost or create duplicate notes.
            page.evaluate("""() => {
                DaynotesStorage.NotesStore.prototype.save = function (draft) {
                    DaynotesStorage.NotesStore.prototype.save = window.originalSave;
                    return new Promise((resolve, reject) => {
                        window.releaseSave = () => window.originalSave.call(this, draft).then(resolve, reject);
                    });
                };
            }""")
            body.fill("First edit")
            page.wait_for_function("typeof window.releaseSave === 'function'")
            body.fill("Latest edit during save")
            page.evaluate("window.releaseSave()")
            expect(page.locator("#save-status")).to_have_text("Saved")
            page.wait_for_function("""async () => {
                const s = new DaynotesStorage.NotesStore();
                try { return (await s.read())[0].body === 'Latest edit during save'; } finally {s.close();}
            }""")
            assert len(records(page)) == 1
            assert records(page)[0]["expiresAt"] == note["expiresAt"]

            other = context.new_page()
            other.goto(URL)
            ready(other)
            body.fill("Visible in the other tab")
            expect(page.locator("#save-status")).to_have_text("Saved")
            expect(other.locator("#note-body")).to_have_value("Visible in the other tab")
            other.close()
            page.evaluate("""async () => {
                const a = new DaynotesStorage.NotesStore(), b = new DaynotesStorage.NotesStore();
                try {
                    await Promise.all([a.save({title: 'Tab A', body: 'A'}), b.save({title: 'Tab B', body: 'B'})]);
                } finally {a.close(); b.close();}
            }""")
            assert len(records(page)) == 3
            print("PASS: async save failure/retry, overlapping edits, concurrent writes, and tab refresh", flush=True)

            # A retained legacy copy must never resurrect a note deleted after migration.
            page.evaluate("""async (raw) => {
                localStorage.setItem('daynotes.v1', raw);
                const s = new DaynotesStorage.NotesStore();
                try {await s.remove('legacy-note');} finally {s.close();}
            }""", legacy["raw"])
            page.reload()
            ready(page)
            assert "legacy-note" not in [item["id"] for item in records(page)]
            assert page.evaluate("localStorage.getItem('daynotes.v1')") == legacy["raw"]

            seed_old_database(page, corrupt=True)
            page.reload()
            ready(page)
            expect(page.locator("#save-status")).to_have_attribute("data-state", "error")
            assert page.evaluate("localStorage.getItem('daynotes.v1')") == "broken json"
            assert page.evaluate("""async () => {
                const db = await DaynotesStorage.openDatabase();
                return new Promise(resolve => {
                    const tx = db.transaction('images'), req = tx.objectStore('images').count();
                    req.onsuccess = () => resolve(req.result);
                });
            }""") == 3
            page.evaluate("raw => localStorage.setItem('daynotes.v1', raw)", legacy["raw"])
            page.reload()
            ready(page)
            assert len(records(page)) == 1

            body.fill("Draft before import")
            page.locator("#import-file").set_input_files({
                "name": "quick.md", "mimeType": "text/markdown", "buffer": b"## Shopping\n- Milk",
            })
            expect(body).to_have_value("## Shopping\n- Milk")
            expect(page.locator("#save-status")).to_have_text("Saved")
            imported = records(page)
            assert len(imported) == 2
            assert next(item for item in imported if item["id"] == "legacy-note")["body"] == "Draft before import"
            page.locator("#download-note").click()
            page.locator("#download-format").select_option("md")
            with page.expect_download() as download:
                page.get_by_role("button", name="Download", exact=True).click()
            assert download.value.suggested_filename == "quick.md"
            assert download.value.path().read_text(encoding="utf-8") == "quick\n\n## Shopping\n- Milk"
            page.locator("#import-file").set_input_files({
                "name": "bad.txt", "mimeType": "text/plain", "buffer": b"Not Markdown",
            })
            expect(page.locator("#toast")).to_have_text("Choose a Markdown (.md) file.")
            expect(body).to_have_value("## Shopping\n- Milk")
            assert len(records(page)) == 2
            assert not errors, errors
            print("PASS: idempotent migration, no resurrection, and corrupt source retained for recovery", flush=True)
            print("PASS: import flushes the current draft, Markdown download, and failed import preserves the note", flush=True)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
