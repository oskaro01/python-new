(function (root) {
    "use strict";

    const STORAGE_KEY = "daynotes.v1"; // Only used to import the old localStorage records.
    const DB_NAME = "daynotes-images"; // Preserve the existing screenshot database.
    const DB_VERSION = 2;
    const MAX_NOTES = 100, MAX_TITLE = 120, MAX_BODY = 80000, MAX_TOTAL_CHARS = 1000000;
    let databasePromise = null;

    function makeNoteId() {
        if (typeof root.crypto.randomUUID === "function") return root.crypto.randomUUID();
        const bytes = root.crypto.getRandomValues(new Uint8Array(16));
        return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
    }
    class DeletedNoteError extends Error {
        constructor() { super("This note was deleted."); this.name = "DeletedNoteError"; }
    }
    function liveNotes(notes) {
        // Ignore deadlines written by older versions; existing notes now stay too.
        return notes.map(({ expiresAt, ...note }) => note).sort((a, b) => b.updatedAt - a.updatedAt);
    }
    function checkLimits(notes) {
        if (notes.length > MAX_NOTES) throw new Error("You have 100 notes. Delete or download one before adding another.");
        if (notes.reduce((total, note) => total + note.title.length + note.body.length, 0) > MAX_TOTAL_CHARS) {
            throw new Error("Local note storage is full. Download or delete some notes first.");
        }
    }
    function parseLegacy(raw) {
        if (raw === null) return [];
        let data;
        try { data = JSON.parse(raw); } catch {
            throw new Error("Old notes could not be read. The original browser data has not been changed.");
        }
        if (!data || data.version !== 1 || !Array.isArray(data.notes)) throw new Error("The old notes format is not supported; the original data is unchanged.");
        const ids = new Set();
        for (const note of data.notes) {
            if (!note || typeof note.id !== "string" || !note.id || ids.has(note.id)
                || typeof note.title !== "string" || typeof note.body !== "string"
                || !Number.isFinite(note.createdAt) || !Number.isFinite(note.updatedAt)
                || note.title.length > MAX_TITLE || note.body.length > MAX_BODY) {
                throw new Error("An old note is invalid. Migration stopped without removing the original data.");
            }
            ids.add(note.id);
        }
        const notes = liveNotes(data.notes);
        checkLimits(notes);
        return notes;
    }
    function prepareNote(notes, { id = null, title, body }, { now, makeId = makeNoteId }) {
        if (typeof title !== "string" || typeof body !== "string" || title.length > MAX_TITLE || body.length > MAX_BODY) {
            throw new Error("This note is too long. Download it and start another note.");
        }
        const live = liveNotes(notes);
        const existing = id ? live.find((note) => note.id === id) : null;
        if (id && !existing) throw new DeletedNoteError();
        const createdAt = existing ? existing.createdAt : now;
        const note = { id: existing ? id : makeId(), title, body, createdAt, updatedAt: now };
        checkLimits([note, ...live.filter((item) => item.id !== note.id)]);
        return note;
    }
    function openDatabase() {
        if (!databasePromise) {
            databasePromise = new Promise((resolve, reject) => {
                let rejected = false;
                const request = root.indexedDB.open(DB_NAME, DB_VERSION);
                request.onupgradeneeded = () => {
                    const database = request.result;
                    if (!database.objectStoreNames.contains("images")) {
                        const images = database.createObjectStore("images", { keyPath: "id" });
                        images.createIndex("noteId", "noteId");
                    }
                    if (!database.objectStoreNames.contains("notes")) database.createObjectStore("notes", { keyPath: "id" });
                    if (!database.objectStoreNames.contains("meta")) database.createObjectStore("meta", { keyPath: "key" });
                };
                request.onblocked = () => {
                    rejected = true;
                    reject(new Error("Close other Daynotes tabs, then reload to finish upgrading browser storage."));
                };
                request.onerror = () => reject(new Error("Browser database is unavailable. Download any unsaved text before leaving."));
                request.onsuccess = () => {
                    const database = request.result;
                    if (rejected) { database.close(); return; }
                    database.onversionchange = () => { database.close(); databasePromise = null; };
                    resolve(database);
                };
            }).catch((error) => { databasePromise = null; throw error; });
        }
        return databasePromise;
    }
    async function transaction(names, mode, action) {
        const database = await openDatabase();
        return new Promise((resolve, reject) => {
            const tx = database.transaction(names, mode);
            let result, failure;
            tx.oncomplete = () => resolve(result);
            tx.onabort = () => reject(failure || new Error("Cannot save to the browser database. It may be unavailable or full. Download your note."));
            const fail = (error) => { failure = error; tx.abort(); };
            try { action(tx, (value) => { result = value; }, fail); } catch (error) { fail(error); }
        });
    }
    function deleteImages(tx, noteId) {
        const images = tx.objectStore("images");
        const request = images.index("noteId").openKeyCursor(noteId);
        request.onsuccess = () => {
            const cursor = request.result;
            if (cursor) { images.delete(cursor.primaryKey); cursor.continue(); }
        };
    }
    class NotesStore {
        constructor({ legacyStorage = root.localStorage, now = Date.now, makeId = makeNoteId } = {}) {
            this.legacyStorage = legacyStorage;
            this.now = now;
            this.makeId = makeId;
            this.initialized = null;
            this.events = typeof root.BroadcastChannel === "function" ? new root.BroadcastChannel("daynotes.changes.v2") : null;
            if (this.events) this.events.onmessage = () => { if (this.onchange) this.onchange(); };
        }
        announce() { if (this.events) this.events.postMessage({ type: "changed" }); }
        init() {
            if (!this.initialized) this.initialized = this.migrate().catch((error) => { this.initialized = null; throw error; });
            return this.initialized;
        }
        async migrate() {
            // Commit a marker before removing the source: a leftover old copy cannot
            // resurrect an IndexedDB note that was subsequently deleted.
            const raw = this.legacyStorage.getItem(STORAGE_KEY);
            const imported = await transaction(["notes", "images", "meta"], "readwrite", (tx, done, fail) => {
                const marker = tx.objectStore("meta").get("legacy-notes-migrated");
                marker.onsuccess = () => {
                    if (marker.result) { done(false); return; }
                    let legacy;
                    try { legacy = parseLegacy(raw); } catch (error) { fail(error); return; }
                    const notes = tx.objectStore("notes");
                    const request = notes.getAll();
                    request.onsuccess = () => {
                        const current = request.result;
                        const existingIds = new Set(current.map((note) => note.id));
                        const additions = legacy.filter((note) => !existingIds.has(note.id));
                        const combined = liveNotes([...current, ...additions]);
                        try { checkLimits(combined); } catch (error) { fail(error); return; }
                        additions.forEach((note) => notes.put(note));
                        const parents = new Map(combined.map((note) => [note.id, note]));
                        const cursorRequest = tx.objectStore("images").openCursor();
                        cursorRequest.onsuccess = () => {
                            const cursor = cursorRequest.result;
                            if (!cursor) return;
                            const parent = parents.get(cursor.value.noteId);
                            if (!parent) cursor.delete();
                            cursor.continue();
                        };
                        tx.objectStore("meta").put({ key: "legacy-notes-migrated", completedAt: this.now() });
                        done(true);
                    };
                };
            });
            if (imported && raw !== null) {
                try {
                    if (this.legacyStorage.getItem(STORAGE_KEY) === raw) this.legacyStorage.removeItem(STORAGE_KEY);
                } catch { /* The committed marker prevents duplicate imports. */ }
            }
            if (imported) this.announce();
        }
        async read() {
            await this.init();
            return transaction(["notes"], "readonly", (tx, done) => {
                const request = tx.objectStore("notes").getAll();
                request.onsuccess = () => done(liveNotes(request.result));
            });
        }
        async save(draft) {
            await this.init();
            const note = await transaction(["notes", "images"], "readwrite", (tx, done, fail) => {
                const notes = tx.objectStore("notes");
                const request = notes.getAll();
                request.onsuccess = () => {
                    let saved;
                    try { saved = prepareNote(request.result, draft, { now: this.now(), makeId: this.makeId }); }
                    catch (error) { fail(error); return; }
                    notes.put(saved);
                    done(saved);
                };
            });
            this.announce();
            return note;
        }
        async remove(id) {
            await this.init();
            await transaction(["notes", "images"], "readwrite", (tx) => {
                tx.objectStore("notes").delete(id);
                deleteImages(tx, id);
            });
            this.announce();
        }
        close() { if (this.events) this.events.close(); }
    }
    const api = { NotesStore, DeletedNoteError, STORAGE_KEY, DB_NAME, openDatabase, makeNoteId, liveNotes, prepareNote, parseLegacy };
    root.DaynotesStorage = api;
    if (typeof module !== "undefined" && module.exports) module.exports = api;
})(globalThis);
