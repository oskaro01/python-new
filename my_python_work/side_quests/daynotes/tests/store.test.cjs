const assert = require("node:assert/strict");
const { test } = require("node:test");
const { readFileSync } = require("node:fs");
const { join } = require("node:path");
const { runInNewContext } = require("node:vm");
const { DeletedNoteError, prepareNote, parseLegacy, liveNotes } = require("../storage.js");
const DAY_MS = 86400000;

const NOW = 1700000000000;
const create = (draft = {}, notes = [], now = NOW) => prepareNote(notes,
    { title: "A note", body: "Some text", ...draft }, { now, makeId: () => "new-id" });

test("notes have no expiry and edits preserve their original creation time", () => {
    const note = create();
    const edited = create({ id: note.id, body: "Changed" }, [note], NOW + 2 * DAY_MS);
    assert.equal(edited.createdAt, NOW);
    assert.equal("expiresAt" in edited, false);
    assert.equal(edited.updatedAt, NOW + 2 * DAY_MS);
    assert.equal(note.body, "Some text");
});

test("old deadlines are ignored but deleted notes cannot be revived by an edit", () => {
    const note = create();
    assert.deepEqual(liveNotes([{ ...note, expiresAt: NOW - DAY_MS }]), [note]);
    const edited = create({ id: note.id }, [note], NOW + 365 * DAY_MS);
    assert.equal(edited.createdAt, note.createdAt);
    assert.equal("expiresAt" in edited, false);
    assert.throws(() => create({ id: note.id }), DeletedNoteError);
});

test("legacy migration preserves all remaining records regardless of age", () => {
    const old = create({}, [], NOW - 2 * DAY_MS);
    const expired = { ...old, id: "expired", createdAt: NOW - 4 * DAY_MS };
    const migrated = parseLegacy(JSON.stringify({ version: 1, notes: [
        { ...old, expiresAt: old.createdAt + DAY_MS }, expired,
    ] }), NOW);
    assert.deepEqual(migrated, [old, expired]);
    assert.deepEqual(parseLegacy(null, NOW), []);
});

test("malformed legacy data is rejected rather than silently discarded", () => {
    const note = create();
    for (const value of ["not json", "null", JSON.stringify({ version: 2, notes: [] }),
        JSON.stringify({ version: 1, notes: [note, note] }),
        JSON.stringify({ version: 1, notes: [{ ...note, createdAt: "yesterday" }] }),
        JSON.stringify({ version: 1, notes: [{ ...note, body: null }] })]) {
        assert.throws(() => parseLegacy(value, NOW));
    }
});

test("raw Markdown, Unicode, and HTML remain data", () => {
    const body = "<script>alert('text only')</script>\n## Notes\n\u09ac\u09be\u0982\u09b2\u09be";
    const note = create({ body });
    assert.equal(note.body, body);
    assert.equal(parseLegacy(JSON.stringify({ version: 1, notes: [note] }), NOW)[0].body, body);
});

test("limits bound individual notes, note count, and total text without blocking edits", () => {
    assert.throws(() => create({ body: "x".repeat(80001) }), /too long/);
    assert.throws(() => create({ title: "x".repeat(121) }), /too long/);
    const notes = Array.from({ length: 100 }, (_, index) => ({ ...create(), id: `note-${index}` }));
    assert.throws(() => create({}, notes), /100 notes/);
    assert.doesNotThrow(() => create({ id: notes[0].id, body: "Edit existing" }, notes));
    const full = notes.slice(0, 13).map(note => ({ ...note, body: "x".repeat(76000) }));
    assert.throws(() => create({ body: "x".repeat(20000) }, full), /storage is full/);
});

test("live notes are sorted without mutating their source", () => {
    const first = { ...create(), id: "first" };
    const second = { ...create(), id: "second", updatedAt: NOW + 1000 };
    const records = [first, second];
    assert.deepEqual(liveNotes(records, NOW).map(note => note.id), ["second", "first"]);
    assert.equal(records[0], first);
});

test("LAN HTTP can generate IDs without crypto.randomUUID", () => {
    const browser = { crypto: { getRandomValues: bytes => bytes.fill(7) } };
    runInNewContext(readFileSync(join(__dirname, "../storage.js"), "utf8"), browser);
    assert.equal(browser.DaynotesStorage.makeNoteId(), "07".repeat(16));
});
