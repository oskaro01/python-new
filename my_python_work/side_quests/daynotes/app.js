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
    let preferences = { ...DEFAULT_PREFERENCES };
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
            preview.textContent = note.body.trim().replace(/\s+/g, " ").slice(0, 100) || "Empty note";
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
    }

    function refresh() {
        if (!store) return;
        notes = store.prune();
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
    byId("new-note").addEventListener("click", () => {
        if (!flush()) return;
        search.value = "";
        openNote();
        if (mobile.matches) showSidebar(false);
        title.focus();
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
        const url = URL.createObjectURL(new Blob([text], {
            type: markdown ? "text/markdown;charset=utf-8" : "text/plain;charset=utf-8",
        }));
        const link = document.createElement("a");
        const name = title.value.trim().replace(/[<>:"/\\|?*\x00-\x1f]/g, "-").slice(0, 70) || "untitled";
        link.href = url;
        link.download = `${name}.${extension}`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
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
        if (!flush()) { event.preventDefault(); event.returnValue = ""; }
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
})();
