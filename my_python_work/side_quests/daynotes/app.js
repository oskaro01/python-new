window.DaynotesReady = (async function () {
    "use strict";

    const { NotesStore, DeletedNoteError, STORAGE_KEY } = window.DaynotesStorage;
    const byId = (id) => document.getElementById(id);
    const title = byId("note-title");
    const body = byId("note-body");
    const status = byId("save-status");
    const search = byId("search-notes");
    const workspace = byId("workspace");
    const mobile = window.matchMedia("(max-width: 700px)");
    const PREFERENCES_KEY = "daynotes.preferences.v1";
    const DEFAULT_PREFERENCES = { fontSize: 18, sidebarWidth: 210, noteSpacing: 16 };
    const imageStore = new window.DaynotesImages.ScreenshotStore();
    let preferences = { ...DEFAULT_PREFERENCES };
    let imageUrls = [];
    let imageVersion = 0;
    let imageWarningShown = false;
    let pendingPastes = 0;
    let store;
    let notes = [];
    let active = null;
    let dirty = false;
    let saveTimer;
    let toastTimer;
    let pendingSave = null;
    let editRevision = 0;
    let editorVersion = 0;
    let refreshVersion = 0;
    let editorBusy = true;

    function notify(message) {
        window.clearTimeout(toastTimer);
        byId("toast").textContent = message;
        byId("toast").hidden = false;
        toastTimer = window.setTimeout(() => { byId("toast").hidden = true; }, 5000);
    }

    function setStatus(message, error = false) {
        status.textContent = message;
        status.dataset.state = error ? "error" : "saved";
    }

    function downloadBlob(blob, name) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = name;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    function imageError(error) {
        if (!imageWarningShown) notify(error.message || "Screenshot storage is unavailable. Text notes still work.");
        imageWarningShown = true;
    }

    async function loadImages() {
        const note = active;
        const version = ++imageVersion;
        if (byId("image-dialog").open) byId("image-dialog").close();
        byId("image-preview").removeAttribute("src");
        imageUrls.forEach((url) => URL.revokeObjectURL(url));
        imageUrls = [];
        byId("note-images").replaceChildren();
        byId("note-images").hidden = true;
        byId("image-export-warning").hidden = true;
        document.querySelector(".paper").classList.remove("has-images");
        sizeBody();
        if (!note) return;
        try {
            const images = await imageStore.list(note.id);
            if (version !== imageVersion || active?.id !== note.id) return;
            const list = byId("note-images");
            images.forEach((image, index) => {
                const url = URL.createObjectURL(image.blob);
                imageUrls.push(url);
                const figure = document.createElement("figure");
                figure.className = "screenshot";
                const preview = document.createElement("button");
                preview.type = "button";
                preview.className = "screenshot-preview";
                preview.setAttribute("aria-label", `View screenshot ${index + 1}`);
                const picture = document.createElement("img");
                picture.src = url;
                picture.alt = `Pasted screenshot ${index + 1}`;
                if (image.width && image.height) { picture.width = image.width; picture.height = image.height; }
                preview.appendChild(picture);
                const stillLive = () => active?.id === note.id;
                preview.addEventListener("click", () => {
                    if (!stillLive()) { safeRefresh(); return; }
                    byId("image-preview").src = url;
                    byId("image-dialog").showModal();
                });
                const caption = document.createElement("figcaption");
                const name = document.createElement("span");
                name.textContent = `Screenshot ${index + 1}`;
                caption.appendChild(name);
                for (const [label, icon, action] of [
                    ["Download screenshot", "download", () => {
                        if (!stillLive()) { safeRefresh(); return; }
                        const extension = { "image/png": "png", "image/jpeg": "jpg", "image/webp": "webp" }[image.blob.type];
                        downloadBlob(image.blob, `screenshot-${index + 1}.${extension}`);
                    }],
                    ["Remove screenshot", "trash", async () => {
                        try {
                            await imageStore.remove(image.id);
                            store.announce();
                            if (active?.id === note.id) await loadImages();
                        } catch (error) { notify(error.message); }
                    }],
                ]) {
                    const button = document.createElement("button");
                    button.type = "button";
                    button.className = "icon-button";
                    button.title = label;
                    button.setAttribute("aria-label", label);
                    const symbol = document.createElement("span");
                    symbol.className = `icon icon-${icon}`;
                    symbol.setAttribute("aria-hidden", "true");
                    button.appendChild(symbol);
                    button.addEventListener("click", action);
                    caption.appendChild(button);
                }
                figure.append(preview, caption);
                list.appendChild(figure);
            });
            list.hidden = !images.length;
            byId("image-export-warning").hidden = !images.length;
            document.querySelector(".paper").classList.toggle("has-images", images.length > 0);
            sizeBody();
        } catch (error) { imageError(error); }
    }

    function sizeBody() {
        const surface = byId("writing-surface");
        const scrollTop = surface.scrollTop;
        const scrollLeft = surface.scrollLeft;
        body.style.height = "0px";
        body.style.height = `${body.scrollHeight}px`;
        // Measuring briefly collapses the scroll range of a long note.
        surface.scrollTop = scrollTop;
        surface.scrollLeft = scrollLeft;
    }

    function loadPreferences() {
        preferences = { ...DEFAULT_PREFERENCES };
        try {
            const saved = JSON.parse(window.localStorage.getItem(PREFERENCES_KEY));
            if (saved && Number.isFinite(saved.fontSize)) {
                preferences.fontSize = Math.max(14, Math.min(28, Math.round(saved.fontSize)));
            }
            if (saved && Number.isFinite(saved.sidebarWidth)) {
                preferences.sidebarWidth = Math.max(160, Math.min(320, Math.round(saved.sidebarWidth / 10) * 10));
            }
            if (saved && Number.isFinite(saved.noteSpacing)) {
                preferences.noteSpacing = Math.max(0, Math.min(40, Math.round(saved.noteSpacing / 2) * 2));
            }
        } catch {
            // A broken or blocked preferences entry must not prevent note editing.
        }
        applyPreferences();
    }

    function applyPreferences() {
        document.documentElement.style.setProperty("--note-font-size", `${preferences.fontSize}px`);
        document.documentElement.style.setProperty("--sidebar-width", `${preferences.sidebarWidth}px`);
        document.documentElement.style.setProperty("--note-spacing", `${preferences.noteSpacing}px`);
        byId("text-size").value = String(preferences.fontSize);
        byId("sidebar-width").value = String(preferences.sidebarWidth);
        byId("note-spacing").value = String(preferences.noteSpacing);
        byId("text-size-value").textContent = `${preferences.fontSize} px`;
        byId("sidebar-width-value").textContent = `${preferences.sidebarWidth} px`;
        byId("note-spacing-value").textContent = `${preferences.noteSpacing} px`;
        sizeBody();
    }

    function savePreferences() {
        applyPreferences();
        try {
            window.localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences));
        } catch {
            notify("Appearance applied for this session; browser storage is unavailable.");
        }
    }

    function updateMeta() {
        const hasContent = Boolean(title.value.trim() || body.value.trim());
        byId("download-note").disabled = !hasContent;
        byId("delete-note").disabled = editorBusy || (!active && !hasContent);
        byId("character-count").textContent = `${body.value.length.toLocaleString()} characters`;
        byId("created-at").textContent = active ? new Date(active.createdAt).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) : "";
        document.title = `${title.value.trim() || "Untitled"} | Daynotes`;
    }

    function renderList() {
        const query = search.value.trim().toLocaleLowerCase();
        const matches = notes.filter((note) => `${note.title}\n${note.body}`.toLocaleLowerCase().includes(query));
        const fragment = document.createDocumentFragment();
        matches.forEach((note) => {
            const row = document.createElement("button");
            row.className = "note-row";
            row.type = "button";
            row.disabled = editorBusy;
            row.setAttribute("aria-pressed", String(active?.id === note.id));
            const name = document.createElement("span");
            name.className = "note-row-title";
            name.textContent = note.title.trim() || "Untitled";
            const preview = document.createElement("span");
            preview.className = "note-row-preview";
            preview.textContent = note.body.trim().replace(/\s+/g, " ").slice(0, 100) || "No text";
            const time = document.createElement("span");
            time.className = "note-row-time";
            time.textContent = new Date(note.updatedAt).toLocaleDateString();
            row.append(name, preview, time);
            row.addEventListener("click", () => withSavedDraft(async () => {
                await refresh();
                const selected = notes.find((item) => item.id === note.id);
                if (selected) openNote(selected);
                else notify("That note was deleted.");
                if (mobile.matches) showSidebar(false);
            }));
            fragment.appendChild(row);
        });
        byId("note-list").replaceChildren(fragment);
        byId("note-count").textContent = String(notes.length);
        byId("list-empty").hidden = matches.length > 0;
        byId("list-empty").textContent = query ? "No matching notes." : "No notes yet.";
    }

    function openNote(note = null, preservePosition = false) {
        const surface = byId("writing-surface");
        const position = surface.scrollTop;
        const selection = [body.selectionStart, body.selectionEnd];
        editorVersion += 1;
        active = note;
        dirty = false;
        title.value = note?.title || "";
        body.value = note?.body || "";
        setStatus(note ? "Saved" : "New note");
        surface.scrollTop = 0;
        updateMeta();
        renderList();
        sizeBody();
        if (preservePosition) {
            body.setSelectionRange(Math.min(selection[0], body.value.length), Math.min(selection[1], body.value.length));
            surface.scrollTop = position;
        }
        loadImages();
    }

    async function refresh(reloadActive = false) {
        if (!store) return;
        const request = ++refreshVersion;
        const version = editorVersion;
        const next = await store.read();
        if (request !== refreshVersion || version !== editorVersion) return;
        notes = next;
        if (active && !notes.some((note) => note.id === active.id)) {
            window.clearTimeout(saveTimer);
            openNote();
            notify("The open note was deleted.");
        } else if (reloadActive && active && !dirty && !pendingSave) {
            const latest = notes.find((note) => note.id === active.id);
            if (latest.updatedAt !== active.updatedAt || latest.body !== body.value || latest.title !== title.value) openNote(latest, true);
            else await loadImages();
        }
        renderList();
        updateMeta();
    }

    async function flush() {
        window.clearTimeout(saveTimer);
        if (pendingSave) {
            if (!await pendingSave) return false;
            return dirty ? flush() : true;
        }
        if (!dirty) return true;
        if (!store) { setStatus("Browser storage unavailable. Download this note before leaving.", true); return false; }
        if (!active && !title.value.trim() && !body.value.trim()) {
            dirty = false;
            setStatus("New note");
            return true;
        }
        const revision = editRevision;
        const version = editorVersion;
        const draft = { id: active?.id, title: title.value, body: body.value };
        pendingSave = (async () => {
            try {
                const saved = await store.save(draft);
                if (version !== editorVersion) return true;
                active = saved;
                dirty = editRevision !== revision;
                setStatus(dirty ? "Saving..." : "Saved");
                await refresh();
                return true;
            } catch (error) {
                if (error instanceof DeletedNoteError) await refresh();
                setStatus(error.message, true);
                return false;
            }
        })().finally(() => { pendingSave = null; });
        return pendingSave;
    }

    function lockEditor(locked) {
        title.readOnly = locked;
        body.readOnly = locked;
        byId("new-note").disabled = locked;
        byId("import-note").disabled = locked;
        document.querySelectorAll(".note-row").forEach((row) => { row.disabled = locked; });
        updateMeta();
    }

    async function withSavedDraft(action) {
        if (editorBusy) return false;
        editorBusy = true;
        lockEditor(true);
        try {
            if (!await flush()) return false;
            await action();
            return true;
        } catch (error) { setStatus(error.message, true); notify(error.message); return false; }
        finally { editorBusy = false; lockEditor(false); renderList(); }
    }

    function safeRefresh(reloadActive = false) {
        if (!editorBusy) refresh(reloadActive).catch((error) => setStatus(error.message, true));
    }

    function showSidebar(show) {
        if (mobile.matches) {
            workspace.classList.toggle("sidebar-open", show);
            workspace.classList.remove("sidebar-hidden");
            byId("sidebar-backdrop").hidden = !show;
        } else {
            workspace.classList.toggle("sidebar-hidden", !show);
            workspace.classList.remove("sidebar-open");
            byId("sidebar-backdrop").hidden = true;
        }
        byId("toggle-notes").setAttribute("aria-expanded", String(show));
        sizeBody();
    }

    [title, body].forEach((input) => input.addEventListener("input", () => {
        editRevision += 1;
        dirty = true;
        setStatus("Saving...");
        updateMeta();
        sizeBody();
        window.clearTimeout(saveTimer);
        saveTimer = window.setTimeout(flush, 250);
    }));
    search.addEventListener("input", renderList);
    byId("writing-surface").addEventListener("paste", async (event) => {
        const files = Array.from(event.clipboardData?.files || []).filter((file) => file.type.startsWith("image/"));
        if (!files.length) return;
        event.preventDefault();
        if (editorBusy) { notify("Please wait for the current operation to finish."); return; }
        pendingPastes += 1;
        let note;
        let saved = false;
        try {
            saved = await withSavedDraft(async () => {
                if (!store) throw new Error("Browser storage is unavailable. The screenshot was not saved.");
                if (!active) {
                    active = await store.save({ title: title.value, body: body.value });
                    await refresh();
                }
                note = active;
                setStatus("Saving screenshot...");
                await imageStore.add(note, files);
                store.announce();
                // The note may have been deleted in another tab while the image was being decoded.
                if (!(await store.read()).some((item) => item.id === note.id)) {
                    await imageStore.removeNote(note.id);
                    await refresh();
                    throw new Error("The note was deleted before the screenshot was saved.");
                }
                if (active?.id === note.id) {
                    await loadImages();
                    byId("note-images").lastElementChild?.scrollIntoView({ block: "nearest" });
                }
                notify(files.length === 1 ? "Screenshot saved." : "Screenshots saved.");
            });
        } catch (error) {
            notify(error.message || "The screenshot could not be saved.");
        } finally {
            pendingPastes -= 1;
            if (saved && note && active?.id === note.id) setStatus(dirty ? "Saving..." : "Saved");
        }
    });
    byId("new-note").addEventListener("click", () => withSavedDraft(async () => {
        search.value = "";
        openNote();
        if (mobile.matches) showSidebar(false);
        title.focus();
    }));
    byId("import-note").addEventListener("click", () => {
        if (!editorBusy) byId("import-file").click();
    });
    byId("import-file").addEventListener("change", async (event) => {
        const input = event.target;
        const file = input.files[0];
        if (!file) return;
        if (editorBusy) { input.value = ""; return; }
        try {
            await withSavedDraft(async () => {
                if (!/\.md$/i.test(file.name)) throw new Error("Choose a Markdown (.md) file.");
                if (file.size > 320 * 1024) throw new Error("Choose a Markdown file no larger than 320 KB.");
                let text;
                try {
                    text = new TextDecoder("utf-8", { fatal: true }).decode(await file.arrayBuffer());
                } catch {
                    throw new Error("This file could not be read as UTF-8 text.");
                }
                if (text.includes("\0")) throw new Error("Choose a text Markdown file, not a binary file.");
                if (text.length > body.maxLength) throw new Error("Markdown files must contain 80,000 characters or fewer.");
                if (!store) throw new Error("Browser storage is unavailable. The file was not imported.");
                // Save a separate note before switching the editor, so failure cannot replace a draft.
                const imported = await store.save({
                    title: file.name.replace(/\.md$/i, "").trim().slice(0, title.maxLength) || "Untitled",
                    body: text,
                });
                notes = await store.read();
                search.value = "";
                openNote(imported);
                if (mobile.matches) showSidebar(false);
                notify(`Opened ${file.name}.`);
            });
        } catch (error) {
            notify(error.message || "The file could not be opened. Your current note is unchanged.");
        } finally {
            input.value = "";
            byId("import-note").disabled = editorBusy;
        }
    });
    byId("toggle-notes").addEventListener("click", () => {
        showSidebar(byId("toggle-notes").getAttribute("aria-expanded") !== "true");
    });
    byId("sidebar-backdrop").addEventListener("click", () => showSidebar(false));
    byId("open-appearance").addEventListener("click", () => byId("appearance-dialog").showModal());
    byId("text-size").addEventListener("input", (event) => {
        preferences.fontSize = Number(event.target.value);
        savePreferences();
    });
    byId("sidebar-width").addEventListener("input", (event) => {
        preferences.sidebarWidth = Number(event.target.value);
        savePreferences();
    });
    byId("note-spacing").addEventListener("input", (event) => {
        preferences.noteSpacing = Number(event.target.value);
        savePreferences();
    });
    byId("reset-appearance").addEventListener("click", () => {
        preferences = { ...DEFAULT_PREFERENCES };
        savePreferences();
    });
    byId("delete-note").addEventListener("click", () => withSavedDraft(async () => byId("delete-dialog").showModal()));
    byId("delete-dialog").addEventListener("close", async () => {
        if (byId("delete-dialog").returnValue !== "delete") return;
        await withSavedDraft(async () => {
            if (active) await store.remove(active.id);
            openNote();
            await refresh();
            notify("Note deleted.");
        });
    });
    byId("download-note").addEventListener("click", () => {
        byId("download-dialog").showModal();
    });
    byId("download-form").addEventListener("submit", (event) => {
        if (event.submitter?.value !== "download") return;
        if (!title.value.trim() && !body.value.trim()) return;
        const markdown = byId("download-format").value === "md";
        const extension = markdown ? "md" : "txt";
        const text = title.value.trim() ? `${title.value.trim()}\n\n${body.value}` : body.value;
        const blob = new Blob([text], {
            type: markdown ? "text/markdown;charset=utf-8" : "text/plain;charset=utf-8",
        });
        const name = title.value.trim().replace(/[<>:"/\\|?*\x00-\x1f]/g, "-").slice(0, 70) || "untitled";
        downloadBlob(blob, `${name}.${extension}`);
    });

    // Refresh changes from other tabs, including browsers without BroadcastChannel.
    window.setInterval(() => safeRefresh(), 15000);
    window.addEventListener("focus", () => safeRefresh(true));
    window.addEventListener("pagehide", () => { void flush(); });
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) void flush();
        else safeRefresh(true);
    });
    window.addEventListener("beforeunload", (event) => {
        if (dirty || pendingSave || pendingPastes || editorBusy) {
            void flush(); event.preventDefault(); event.returnValue = "";
        }
    });
    window.addEventListener("storage", (event) => {
        if (event.key === PREFERENCES_KEY || event.key === null) loadPreferences();
        if (event.key === STORAGE_KEY && event.newValue) notify("Another tab is using old Daynotes storage. Close it and use this version.");
    });
    window.addEventListener("resize", sizeBody);
    mobile.addEventListener("change", () => showSidebar(!mobile.matches));
    document.addEventListener("keydown", (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
            event.preventDefault();
            void flush();
        }
        if (event.key === "Escape" && mobile.matches) showSidebar(false);
    });

    loadPreferences();
    lockEditor(true);
    setStatus("Opening browser database...");
    try {
        store = new NotesStore();
        await store.init();
        notes = await store.read();
        openNote(notes[0]);
        store.onchange = () => safeRefresh(true);
    } catch (error) {
        if (store) store.close();
        store = null;
        openNote();
        setStatus(error.message || "Browser storage unavailable. Download before leaving.", true);
    }
    editorBusy = false;
    lockEditor(false);
    renderList();
    showSidebar(!mobile.matches);
})();
