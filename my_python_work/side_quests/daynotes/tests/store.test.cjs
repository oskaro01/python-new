const assert = require("node:assert/strict");
const { test } = require("node:test");
const { readFileSync } = require("node:fs");
const { join } = require("node:path");
const { runInNewContext } = require("node:vm");
const { NotesStore, ExpiredNoteError, DAY_MS, STORAGE_KEY } = require("../storage.js");

function fixture() {
    const data = new Map();
    let time = 1700000000000;
    let nextId = 0;
    const storage = {
        getItem: (key) => data.has(key) ? data.get(key) : null,
        setItem: (key, value) => data.set(key, value),
        removeItem: (key) => data.delete(key),
    };
    const store = new NotesStore(storage, { now: () => time, makeId: () => `note-${++nextId}` });
    return { store, storage, advance: (milliseconds) => { time += milliseconds; } };
}

test("notes persist and editing never extends the original expiry", () => {
    const { store, storage, advance } = fixture();
    const note = store.save({ title: "A note", body: "## Raw Markdown\nA little text." });
    advance(DAY_MS / 2);
    const changed = store.save({ ...note, body: "Edited" });
    assert.equal(changed.expiresAt, note.createdAt + DAY_MS);
    assert.equal(changed.createdAt, note.createdAt);
    assert.equal(store.prune()[0].body, "Edited");
    assert.equal(JSON.parse(storage.getItem(STORAGE_KEY)).notes.length, 1);
});

test("expired notes are physically removed at the boundary and cannot be revived", () => {
    const { store, storage, advance } = fixture();
    const note = store.save({ title: "Temporary", body: "Gone tomorrow" });
    advance(DAY_MS - 1);
    assert.equal(store.prune().length, 1);
    advance(1);
    assert.deepEqual(store.prune(), []);
    assert.equal(storage.getItem(STORAGE_KEY), null);
    assert.throws(() => store.save({ ...note, body: "Late edit" }), ExpiredNoteError);
});

test("a later note survives cleanup and deletion does not affect other notes", () => {
    const { store, advance } = fixture();
    const first = store.save({ title: "First", body: "One" });
    advance(1000);
    const second = store.save({ title: "Second", body: "Two" });
    advance(DAY_MS - 1000);
    assert.deepEqual(store.prune().map((note) => note.id), [second.id]);
    store.remove(first.id);
    assert.equal(store.prune().length, 1);
    store.remove(second.id);
    assert.deepEqual(store.prune(), []);
});

test("expired records are cleaned up after closing and reopening", () => {
    const { store, storage, advance } = fixture();
    store.save({ title: "Old", body: "Something" });
    advance(DAY_MS);
    const reopened = new NotesStore(storage, { now: () => 1700000000000 + DAY_MS });
    assert.deepEqual(reopened.prune(), []);
    assert.equal(storage.getItem(STORAGE_KEY), null);
});

test("the store preserves raw text, Unicode, and HTML without rendering", () => {
    const { store } = fixture();
    const body = "<script>alert('text only')</script>\n## Notes\n\u09ac\u09be\u0982\u09b2\u09be";
    store.save({ title: "Text", body });
    assert.equal(store.prune()[0].body, body);
});

test("new saves reread storage so other notes from another tab are not overwritten", () => {
    const { store, storage } = fixture();
    store.save({ title: "First tab", body: "A" });
    const other = new NotesStore(storage, { now: () => 1700000000000, makeId: () => "other-tab" });
    other.save({ title: "Second tab", body: "B" });
    store.save({ title: "Back to first", body: "C" });
    assert.equal(store.prune().length, 3);
});

test("corrupt storage is not silently overwritten", () => {
    const { store, storage } = fixture();
    storage.setItem(STORAGE_KEY, "not json");
    assert.throws(() => store.prune(), /could not be read/);
    assert.throws(() => store.save({ title: "Draft", body: "Text" }));
    assert.equal(storage.getItem(STORAGE_KEY), "not json");
});

test("quota errors are reported without pretending a note was saved", () => {
    const { store, storage } = fixture();
    storage.setItem = () => { throw new Error("QuotaExceededError"); };
    assert.throws(() => store.save({ title: "Draft", body: "Keep me" }), /Cannot save/);
});

test("limits prevent unlimited growth", () => {
    const { store } = fixture();
    assert.throws(() => store.save({ title: "Long", body: "x".repeat(80001) }), /too long/);
    for (let index = 0; index < 100; index += 1) store.save({ title: String(index), body: "Text" });
    assert.throws(() => store.save({ title: "101", body: "Text" }), /100 notes/);
    const note = store.prune()[0];
    assert.doesNotThrow(() => store.save({ ...note, body: "Edit existing" }));
});

test("notes can be created over LAN HTTP without crypto.randomUUID", () => {
    const { storage } = fixture();
    const browser = { crypto: { getRandomValues: (bytes) => bytes.fill(7) } };
    runInNewContext(readFileSync(join(__dirname, "../storage.js"), "utf8"), browser);
    const store = new browser.DaynotesStorage.NotesStore(storage);
    const note = store.save({ title: "From a phone", body: "Saved on the local network" });
    assert.equal(note.id, "07".repeat(16));
    assert.equal(store.prune()[0].body, "Saved on the local network");
});
