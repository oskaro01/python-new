(function () {
    "use strict";

    const { NotesStore, ExpiredNoteError, STORAGE_KEY } = window.DaynotesStorage;
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
            if (version !== imageVersion || active?.id !== note.id || note.expiresAt <= Date.now()) return;
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
                const stillLive = () => active?.id === note.id && note.expiresAt > Date.now();
                preview.addEventListener("click", () => {
                    if (!stillLive()) { refresh(); return; }
                    byId("image-preview").src = url;
                    byId("image-dialog").showModal();
                });
                const caption = document.createElement("figcaption");
                const name = document.createElement("span");
                name.textContent = `Screenshot ${index + 1}`;
                caption.appendChild(name);
                for (const [label, icon, action] of [
                    ["Download screenshot", "download", () => {
                        if (!stillLive()) { refresh(); return; }
                        const extension = { "image/png": "png", "image/jpeg": "jpg", "image/webp": "webp" }[image.blob.type];
                        downloadBlob(image.blob, `screenshot-${index + 1}.${extension}`);
                    }],
                    ["Remove screenshot", "trash", async () => {
                        try {
                            await imageStore.remove(image.id);
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

    function remaining(note) {
        const minutes = Math.max(1, Math.ceil((note.expiresAt - Date.now()) / 60000));
        return `${Math.floor(minutes / 60)}h ${String(minutes % 60).padStart(2, "0")}m`;
    }

    function sizeBody() {
        body.style.height = "0px";
        body.style.height = `${body.scrollHeight}px`;
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
        byId("delete-note").disabled = !active && !hasContent;
        byId("character-count").textContent = `${body.value.length.toLocaleString()} characters`;
        byId("expiry-text").textContent = active ? `${remaining(active)} left` : "24h";
        byId("expires-in").title = active ? `Expires ${new Date(active.expiresAt).toLocaleString()}` : "24 hours from first save";
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
            row.setAttribute("aria-pressed", String(active?.id === note.id));
            const name = document.createElement("span");
            name.className = "note-row-title";
            name.textContent = note.title.trim() || "Untitled";
            const preview = document.createElement("span");
            preview.className = "note-row-preview";
            preview.textContent = note.body.trim().replace(/\s+/g, " ").slice(0, 100) || "No text";
            const time = document.createElement("span");
            time.className = "note-row-time";
            time.textContent = `${remaining(note)} left`;
            row.append(name, preview, time);
            row.addEventListener("click", () => {
                if (flush()) {
                    try {
                        refresh();
                        const selected = notes.find((item) => item.id === note.id);
                        if (selected) openNote(selected);
                        else notify("That note expired or was deleted.");
                        if (mobile.matches) showSidebar(false);
                    } catch (error) { setStatus(error.message, true); }
                }
            });
            fragment.appendChild(row);
        });
        byId("note-list").replaceChildren(fragment);
        byId("note-count").textContent = String(notes.length);
        byId("list-empty").hidden = matches.length > 0;
        byId("list-empty").textContent = query ? "No matching notes." : "No notes yet.";
    }

    function openNote(note = null) {
        active = note;
        dirty = false;
        title.value = note?.title || "";
        body.value = note?.body || "";
        setStatus(note ? "Saved" : "New note");
        byId("writing-surface").scrollTop = 0;
        updateMeta();
        renderList();
        sizeBody();
        loadImages();
    }

    function refresh() {
        if (!store) return;
        const previous = notes;
        notes = store.prune();
        const liveIds = new Set(notes.map((note) => note.id));
        previous.filter((note) => !liveIds.has(note.id)).forEach((note) => {
            imageStore.removeNote(note.id).catch(imageError);
        });
        imageStore.prune().catch(imageError);
        if (active && !notes.some((note) => note.id === active.id)) {
            window.clearTimeout(saveTimer);
            openNote();
            notify("The open note expired or was deleted.");
        }
        renderList();
        updateMeta();
    }

    function flush() {
        window.clearTimeout(saveTimer);
        if (!dirty) return true;
        if (!store) { setStatus("Browser storage unavailable. Download this note before leaving.", true); return false; }
        if (!active && !title.value.trim() && !body.value.trim()) {
            dirty = false;
            setStatus("New note");
            return true;
        }
        try {
            active = store.save({ id: active?.id, title: title.value, body: body.value });
            dirty = false;
            setStatus("Saved");
            refresh();
            return true;
        } catch (error) {
            if (error instanceof ExpiredNoteError) {
                refresh();
                return false;
            }
            setStatus(error.message, true);
            return false;
        }
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
        if (!flush()) return;
        pendingPastes += 1;
        let note;
        try {
            if (!store) throw new Error("Browser storage is unavailable. The screenshot was not saved.");
            if (!active) {
                active = store.save({ title: title.value, body: body.value });
                refresh();
            }
            note = active;
            setStatus("Saving screenshot...");
            await imageStore.prune();
            await imageStore.add(note, files);
            // The note may have been deleted in another tab while the image was being decoded.
            if (!store.prune().some((item) => item.id === note.id)) {
                await imageStore.removeNote(note.id);
                refresh();
                throw new Error("The note expired or was deleted before the screenshot was saved.");
            }
            if (active?.id === note.id) {
                await loadImages();
                byId("note-images").lastElementChild?.scrollIntoView({ block: "nearest" });
            }
            notify(files.length === 1 ? "Screenshot saved." : "Screenshots saved.");
        } catch (error) {
            notify(error.message || "The screenshot could not be saved.");
        } finally {
            pendingPastes -= 1;
            if (active?.id === note?.id) setStatus(dirty ? "Saving..." : "Saved");
        }
    });
    byId("new-note").addEventListener("click", () => {
        if (!flush()) return;
        search.value = "";
        openNote();
        if (mobile.matches) showSidebar(false);
        title.focus();
    });
    byId("import-note").addEventListener("click", () => {
        if (flush()) byId("import-file").click();
    });
    byId("import-file").addEventListener("change", async (event) => {
        const input = event.target;
        const file = input.files[0];
        if (!file) return;
        byId("import-note").disabled = true;
        try {
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
            if (!flush()) return;
            if (!store) throw new Error("Browser storage is unavailable. The file was not imported.");
            // Save a separate note before switching the editor, so failure cannot replace a draft.
            const imported = store.save({
                title: file.name.replace(/\.md$/i, "").trim().slice(0, title.maxLength) || "Untitled",
                body: text,
            });
            notes = store.prune();
            search.value = "";
            openNote(imported);
            if (mobile.matches) showSidebar(false);
            notify(`Opened ${file.name}.`);
        } catch (error) {
            notify(error.message || "The file could not be opened. Your current note is unchanged.");
        } finally {
            input.value = "";
            byId("import-note").disabled = false;
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
    byId("delete-note").addEventListener("click", () => {
        if (flush()) byId("delete-dialog").showModal();
    });
    byId("delete-dialog").addEventListener("close", () => {
        if (byId("delete-dialog").returnValue !== "delete") return;
        try {
            if (active) store.remove(active.id);
            openNote();
            refresh();
            notify("Note deleted.");
        } catch (error) { setStatus(error.message, true); }
    });
    byId("download-note").addEventListener("click", () => {
        if (active && active.expiresAt <= Date.now()) { refresh(); return; }
        byId("download-dialog").showModal();
    });
    byId("download-form").addEventListener("submit", (event) => {
        if (event.submitter?.value !== "download") return;
        if (active && active.expiresAt <= Date.now()) { refresh(); return; }
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

    // A browser cannot run timers while closed; prune on return as well as periodically.
    window.setInterval(() => { try { refresh(); } catch (error) { setStatus(error.message, true); } }, 15000);
    window.addEventListener("focus", () => { try { refresh(); } catch (error) { setStatus(error.message, true); } });
    window.addEventListener("pagehide", flush);
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) flush();
        else { try { refresh(); } catch (error) { setStatus(error.message, true); } }
    });
    window.addEventListener("beforeunload", (event) => {
        if (!flush() || pendingPastes) { event.preventDefault(); event.returnValue = ""; }
    });
    window.addEventListener("storage", (event) => {
        if (event.key === PREFERENCES_KEY || event.key === null) loadPreferences();
        if (event.key !== STORAGE_KEY && event.key !== null) return;
        try {
            const selectedId = active?.id;
            refresh();
            if (!dirty && selectedId && active) openNote(notes.find((note) => note.id === selectedId));
        } catch (error) { setStatus(error.message, true); }
    });
    window.addEventListener("resize", sizeBody);
    mobile.addEventListener("change", () => showSidebar(!mobile.matches));
    document.addEventListener("keydown", (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
            event.preventDefault();
            flush();
        }
        if (event.key === "Escape" && mobile.matches) showSidebar(false);
    });

    loadPreferences();
    try {
        store = new NotesStore(window.localStorage);
        notes = store.prune();
        openNote(notes[0]);
    } catch (error) {
        openNote();
        setStatus(error.message || "Browser storage unavailable. Download before leaving.", true);
    }
    showSidebar(!mobile.matches);
    imageStore.prune().catch(imageError);
})();
