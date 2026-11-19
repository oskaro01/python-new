"""Check long-note editing in an isolated Edge profile, never personal notes."""

from pathlib import Path

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def settle(page):
    page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")


def position(page):
    return page.locator("#writing-surface").evaluate("surface => surface.scrollTop")


def exercise(page, width, height, name):
    page.set_viewport_size({"width": width, "height": height})
    page.goto((ROOT / "index.html").as_uri())
    page.locator("#new-note").click()
    lines = [f"Line {index:03}: keep this note." for index in range(240)]
    text = "\n".join(lines)
    body = page.locator("#note-body")
    body.fill(text)
    expect(page.locator("#save-status")).to_have_text("Saved")
    clock = page.evaluate("() => JSON.parse(localStorage.getItem('daynotes.v1')).notes[0].expiresAt")
    page.evaluate("""() => {
        const body = document.getElementById('note-body');
        const surface = document.getElementById('writing-surface');
        const caret = body.value.indexOf('Line 120') + 9;
        body.focus({preventScroll: true}); body.setSelectionRange(caret, caret);
        const lineHeight = parseFloat(getComputedStyle(body).lineHeight);
        const textTop = body.getBoundingClientRect().top - surface.getBoundingClientRect().top + surface.scrollTop;
        surface.scrollTop = textTop + 120 * lineHeight - surface.clientHeight / 2;
    }""")
    settle(page)
    before = position(page)
    assert before > 1000, f"{name}: the long note did not scroll"
    caret = body.evaluate("body => body.selectionStart")
    for key, expected_caret in [("Space", caret + 1), ("Backspace", caret)]:
        page.keyboard.press(key); settle(page)
        after = position(page)
        assert abs(after - before) <= 2, f"{name}: {key} moved the editor from {before} to {after}"
        assert body.evaluate("body => body.selectionStart") == expected_caret
        expect(page.locator("#save-status")).to_have_text("Saved")
        assert abs(position(page) - before) <= 2, f"{name}: autosave moved the editor"
    expect(body).to_have_value(text)
    assert page.evaluate("() => JSON.parse(localStorage.getItem('daynotes.v1')).notes[0].expiresAt") == clock
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    page.screenshot(path=str(output / f"editing-{name}.png"))
    # Auto-height must still shrink when a long note is replaced with short text.
    body.select_text(); page.keyboard.insert_text("Short note."); settle(page)
    assert body.evaluate("body => body.getBoundingClientRect().height") < height
    assert position(page) == 0
    expect(page.locator("#save-status")).to_have_text("Saved")


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=True, chromium_sandbox=True)
        try:
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            exercise(page, 1360, 900, "desktop")
            exercise(page, 390, 844, "mobile")
            assert not errors, errors
            print("PASS: space/backspace keep scroll and caret, autosave preserves expiry, and auto-height still shrinks (desktop/mobile)")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
