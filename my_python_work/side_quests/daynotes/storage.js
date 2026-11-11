(function (root) {
    "use strict";

    const DAY_MS = 24 * 60 * 60 * 1000;
    const STORAGE_KEY = "daynotes.v1";
    const MAX_NOTES = 100;
    const MAX_TITLE = 120;
    const MAX_BODY = 80000;
    const MAX_TOTAL_CHARS = 1000000;

    function makeNoteId() {
        if (typeof root.crypto.randomUUID === "function") return root.crypto.randomUUID();
        // Local-network HTTP previews lack randomUUID, but support getRandomValues.
        const bytes = root.crypto.getRandomValues(new Uint8Array(16));
        return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
    }

    class ExpiredNoteError extends Error {
        constructor() {
            super("This note expired or was deleted.");
            this.name = "ExpiredNoteError";
        }
    }

    // Only this adapter touches storage; a future API can replace it.
    class NotesStore {
        constructor(storage, { now = Date.now, makeId = makeNoteId } = {}) {
            this.storage = storage;
            this.now = now;
            this.makeId = makeId;
        }

        read() {
            const raw = this.storage.getItem(STORAGE_KEY);
            if (raw === null) return [];
            let data;
            try {
                data = JSON.parse(raw);
            } catch {
                throw new Error("Saved notes could not be read. Download your current text before resetting browser storage.");
            }
            if (data.version !== 1 || !Array.isArray(data.notes)) {
                throw new Error("The saved notes format is not supported.");
            }
            return data.notes.filter((note) =>
                note && typeof note.id === "string" && typeof note.title === "string"
                && typeof note.body === "string" && Number.isFinite(note.createdAt)
                && Number.isFinite(note.updatedAt) && note.title.length <= MAX_TITLE
                && note.body.length <= MAX_BODY
            ).map((note) => ({ ...note, expiresAt: note.createdAt + DAY_MS }));
        }

        write(notes) {
            try {
                if (notes.length) {
                    this.storage.setItem(STORAGE_KEY, JSON.stringify({ version: 1, notes }));
                } else {
                    this.storage.removeItem(STORAGE_KEY);
                }
            } catch {
                throw new Error("Cannot save to browser storage. Download this note before leaving.");
            }
        }

        prune() {
            const notes = this.read();
            const active = notes.filter((note) => note.expiresAt > this.now());
            if (active.length !== notes.length) this.write(active);
            return active.sort((a, b) => b.updatedAt - a.updatedAt);
        }

        save({ id = null, title, body }) {
            if (title.length > MAX_TITLE || body.length > MAX_BODY) {
                throw new Error("This note is too long. Download it and start another note.");
            }
            const notes = this.prune();
            const existing = id ? notes.find((note) => note.id === id) : null;
            if (id && !existing) throw new ExpiredNoteError();
            if (!existing && notes.length >= MAX_NOTES) {
                throw new Error("You have 100 notes. Delete or download one before adding another.");
            }
            const now = this.now();
            const createdAt = existing ? existing.createdAt : now;
            const note = { id: existing ? id : this.makeId(), title, body, createdAt, updatedAt: now, expiresAt: createdAt + DAY_MS };
            const next = [note, ...notes.filter((item) => item.id !== note.id)];
            if (next.reduce((total, item) => total + item.title.length + item.body.length, 0) > MAX_TOTAL_CHARS) {
                throw new Error("Local note storage is full. Download or delete some notes first.");
            }
            this.write(next);
            return note;
        }

        remove(id) {
            this.write(this.prune().filter((note) => note.id !== id));
        }
    }

    const api = { NotesStore, ExpiredNoteError, DAY_MS, STORAGE_KEY };
    root.DaynotesStorage = api;
    if (typeof module !== "undefined" && module.exports) module.exports = api;
})(globalThis);
