(function (root) {
    "use strict";

    const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
    const MAX_TOTAL_BYTES = 25 * 1024 * 1024;
    const TYPES = new Set(["image/png", "image/jpeg", "image/webp"]);

    class ScreenshotStore {
        constructor() {
            this.database = null;
        }

        open() {
            if (!this.database) {
                this.database = new Promise((resolve, reject) => {
                    const request = root.indexedDB.open("daynotes-images", 1);
                    request.onupgradeneeded = () => {
                        const images = request.result.createObjectStore("images", { keyPath: "id" });
                        images.createIndex("noteId", "noteId");
                        images.createIndex("expiresAt", "expiresAt");
                    };
                    request.onerror = () => {
                        this.database = null;
                        reject(new Error("Screenshot storage is unavailable in this browser."));
                    };
                    request.onsuccess = () => {
                        const database = request.result;
                        database.onversionchange = () => { database.close(); this.database = null; };
                        resolve(database);
                    };
                });
            }
            return this.database;
        }

        async transaction(mode, action) {
            const database = await this.open();
            return new Promise((resolve, reject) => {
                const transaction = database.transaction("images", mode);
                let result;
                let failure;
                transaction.oncomplete = () => resolve(result);
                transaction.onabort = () => reject(failure || new Error("Screenshot storage is unavailable or full."));
                try {
                    action(transaction.objectStore("images"), (value) => { result = value; }, (message) => {
                        failure = new Error(message);
                        transaction.abort();
                    });
                } catch (error) {
                    failure = error;
                    transaction.abort();
                }
            });
        }

        async add(note, files) {
            if (files.length > 5) throw new Error("You can attach up to 5 screenshots per note.");
            const dimensions = [];
            for (const file of files) {
                if (!TYPES.has(file.type)) throw new Error("Paste a PNG, JPEG, or WebP screenshot.");
                if (file.size > MAX_IMAGE_BYTES) throw new Error("Screenshots must be 5 MB or smaller.");
                let bitmap;
                try {
                    bitmap = await root.createImageBitmap(file);
                } catch {
                    throw new Error("The clipboard image could not be read.");
                }
                const tooLarge = bitmap.width * bitmap.height > 16000000;
                dimensions.push({ width: bitmap.width, height: bitmap.height });
                bitmap.close();
                if (tooLarge) throw new Error("Screenshots must be 16 megapixels or smaller.");
            }
            return this.transaction("readwrite", (images, done, fail) => {
                const request = images.getAll();
                request.onsuccess = () => {
                    const now = Date.now();
                    if (note.expiresAt <= now) { fail("This note expired before the screenshot was saved."); return; }
                    const live = request.result.filter((image) => image.expiresAt > now);
                    if (live.filter((image) => image.noteId === note.id).length + files.length > 5) {
                        fail("You can attach up to 5 screenshots per note."); return;
                    }
                    const bytes = live.reduce((total, image) => total + image.blob.size, 0)
                        + files.reduce((total, file) => total + file.size, 0);
                    if (bytes > MAX_TOTAL_BYTES) { fail("Screenshot storage is full (25 MB). Remove some images first."); return; }
                    const added = files.map((file, index) => ({
                        id: root.DaynotesStorage.makeNoteId(), noteId: note.id,
                        blob: file, name: file.name || "Screenshot", createdAt: now, expiresAt: note.expiresAt,
                        ...dimensions[index],
                    }));
                    added.forEach((image) => images.add(image));
                    done(added);
                };
            });
        }

        list(noteId) {
            return this.transaction("readonly", (images, done) => {
                const request = images.index("noteId").getAll(noteId);
                request.onsuccess = () => done(request.result.filter((image) => image.expiresAt > Date.now())
                    .sort((a, b) => a.createdAt - b.createdAt));
            });
        }

        remove(id) {
            return this.transaction("readwrite", (images) => { images.delete(id); });
        }

        removeNote(noteId) {
            return this.transaction("readwrite", (images) => {
                const request = images.index("noteId").openKeyCursor(noteId);
                request.onsuccess = () => {
                    const cursor = request.result;
                    if (cursor) { images.delete(cursor.primaryKey); cursor.continue(); }
                };
            });
        }

        prune() {
            return this.transaction("readwrite", (images) => {
                // Key cursors remove expired blobs without loading their image bytes.
                const request = images.index("expiresAt").openKeyCursor(root.IDBKeyRange.upperBound(Date.now()));
                request.onsuccess = () => {
                    const cursor = request.result;
                    if (cursor) { images.delete(cursor.primaryKey); cursor.continue(); }
                };
            });
        }
    }

    root.DaynotesImages = { ScreenshotStore };
})(globalThis);
