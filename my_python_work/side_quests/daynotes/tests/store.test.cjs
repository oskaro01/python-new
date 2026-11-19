const assert = require("node:assert/strict");
const { test } = require("node:test");
const { readFileSync } = require("node:fs");
const { join } = require("node:path");
const { runInNewContext } = require("node:vm");
const { ExpiredNoteError, DAY_MS, NOTE_TTL_MS, prepareNote, parseLegacy, liveNotes } = require("../storage.js");

const NOW = 1700000000000;
const create = (draft = {}, notes = [], now = NOW) => prepareNote(notes,
    { title: "A note", body: "Some text", ...draft }, { now, makeId: () => "new-id" });

test("notes last 72 hours and edits preserve the original creation and expiry", () => {
    assert.equal(NOTE_TTL_MS, 3 * DAY_MS);
    const note = create();
    const edited = create({ id: note.id, body: "Changed" }, [note], NOW + 2 * DAY_MS);
    assert.equal(edited.createdAt, NOW);
    assert.equal(edited.expiresAt, NOW + NOTE_TTL_MS);
    assert.equal(edited.updatedAt, NOW + 2 * DAY_MS);
    assert.equal(note.body, "Some text");
});

test("expiry is exact, cannot be extended by stored expiresAt, and cannot revive a deleted note", () => {
    const note = create();
    assert.equal(liveNotes([note], NOW + NOTE_TTL_MS - 1).length, 1);
    assert.deepEqual(liveNotes([{ ...note, expiresAt: Infinity }], NOW + NOTE_TTL_MS), []);
    assert.throws(() => create({ id: note.id }, [note], NOW + NOTE_TTL_MS), ExpiredNoteError);
    assert.throws(() => create({ id: note.id }), ExpiredNoteError);
});

test("legacy migration keeps IDs and clocks, extends remaining records to three days, and drops expired ones", () => {
    const old = create({}, [], NOW - 2 * DAY_MS);
    const expired = { ...old, id: "expired", createdAt: NOW - 4 * DAY_MS };
    const migrated = parseLegacy(JSON.stringify({ version: 1, notes: [
        { ...old, expiresAt: old.createdAt + DAY_MS }, expired,
    ] }), NOW);
    assert.deepEqual(migrated, [{ ...old, expiresAt: old.createdAt + NOTE_TTL_MS }]);
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
