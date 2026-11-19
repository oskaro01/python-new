# Daynotes

A small personal notes side quest with a charcoal background, soft gray text,
and a plain-text editor based on your screenshot. Markdown stays as text:
`## headings`, lists, and `**bold**` markers are not reformatted.

## Open It

Open [index.html](index.html) in your browser. No installation, external database,
API key, or server is needed. The browser supplies IndexedDB. All icons are
bundled locally. Nothing is uploaded
or published by this app.

- Use the plus button for a new note; typing saves automatically.
- Editing a long note preserves the editor's scroll position while its text
  area resizes. Opening a different note still starts at the top.
- Use the upload icon to open a UTF-8 `.md` file as a new editable note. The
  filename becomes its title, and the Markdown stays as plain text. This does
  not overwrite the open note, modify the original file, or upload anything to
  a server. Imported notes get their own 3-day lifetime starting at import.
  Files must be at most 320 KB and contain at most 80,000 characters.
- The side panel lists notes and searches their titles and text.
- Use the download icon, choose **Plain text (.txt)** or **Markdown (.md)**,
  then press **Download** to keep a copy before a note expires. Both formats
  preserve the note's text and Markdown markers, with the title on the first
  line when present. **Cancel** closes the dialog without saving a file.
- The trash icon deletes a note after confirmation.
- Paste a screenshot into the note with `Ctrl+V` (or `Cmd+V`). It appears below
  the text. Click/tap the image to enlarge it; its download and trash buttons
  save or remove that screenshot. Image-only notes work too.
- The panel icon opens the note list on phones or hides it on desktop.
- The sliders icon opens **Appearance**: adjust note text from 14 to 28 px,
  sidebar width from 160 to 320 px, and outer note spacing from 0 to 40 px.
  Note spacing controls the gap around the rounded note, not its inner text
  padding. Changes apply immediately; **Reset** returns to 18 px text, a 210 px
  sidebar, and 16 px note spacing. On phones the sidebar is capped at 86% of
  the screen so there is still room to close it.

Appearance preferences are saved separately under `daynotes.preferences.v1`
in this browser. They do not reset a note's expiry or disappear when it expires.

## Pasted Screenshots

Copy the actual image to the clipboard, not its file path or a link. The browser
must expose image data in its paste event; mobile clipboard support depends on
the browser and keyboard. Ordinary text pasting is unchanged.

Screenshots are attachments below the text, not inline rich-text content.
PNG, JPEG, and WebP are supported, with limits of 5 MB and 16 megapixels per
image, 5 images per note, and 25 MB of screenshots across the app.

Image blobs and text notes are stored in separate object stores in the same
browser IndexedDB database, `daynotes-images`. This is NOT a server
database or cloud sync. Screenshots survive refreshes in the same browser
profile, subject to browser storage availability/eviction. They expire with
their parent note, not 3 days after each paste. Cleanup removes the image
blobs, not just their previews, when the app runs. The same closed-browser
cleanup limitation described below applies.

Text and Markdown downloads contain only the note's text; use the image's own
download button to save each screenshot separately. Downloaded copies do not
expire. Clearing browser/site data can remove both notes and screenshots.

## Get a Phone and PC URL with Render

Use the same Render workspace and GitHub repository as Addition Practice.
Create a separate **Static Site**, not a Web Service. No database, API keys,
start command, or changes to the repository's existing `render.yaml` are needed.

1. In VS Code Source Control, commit the new `daynotes` folder and this README,
   then push/sync to GitHub. Suggested message: `Move Daynotes to IndexedDB with 3-day expiry`.
2. Open the [Render dashboard](https://dashboard.render.com/) and choose
   **New > Static Site**.
3. Connect the existing `python-new` repository.
4. Enter these settings (use forward slashes for the root directory):

| Setting | Value |
| --- | --- |
| Name | `daynotes` or another available name |
| Branch | `main` |
| Root Directory | `my_python_work/side_quests/daynotes` |
| Build Command | `echo "No build required"` |
| Publish Directory | `.` |

The build command is a harmless no-op because these HTML, CSS, and JavaScript
files do not need compiling. The publish directory `.` means this app's root
directory, not the entire repository.

5. Click **Create Static Site** and wait for a successful deploy.
6. Copy the site's `https://...onrender.com` URL from its Render service page.
   Open that exact URL on your phone or PC and bookmark it. Your computer does
   not need to stay running for the hosted site to work.

The actual URL is assigned by Render; an example would be
`https://daynotes-example.onrender.com` (not an already-created site).

The website is public, but notes are not sent to Render or shared with other
visitors. Each browser/device keeps its own notes. Notes written using the
local file or a different URL will NOT automatically appear at the hosted
URL: download anything important before switching. Keep using the same HTTPS
URL and normal browser profile for persistent local notes.

After deployment, try a short note and refresh the page to confirm it stays.
Close and reopen the same URL to check persistence. Future deploys at the
same URL do not intentionally clear notes or restart their 3-day clock.

References: [Render static sites](https://render.com/docs/static-sites) and
[root-directory settings](https://render.com/docs/monorepo-support).

## Optional: Phone Preview on the Same Wi-Fi

For a local preview before deploying, run this from the repository root:

```powershell
.\.venv\Scripts\python.exe -m http.server 8004 --directory my_python_work/side_quests/daynotes --bind 0.0.0.0
```

On your PC, open `http://127.0.0.1:8004/`. Run `ipconfig`, find your active
Wi-Fi adapter's IPv4 address, and open `http://YOUR-PC-IP:8004/` on your phone.
Use the real IP address, not the literal placeholder. Both devices must be
on the same trusted Wi-Fi. If Windows Firewall asks, allow access only on your
private network. The PC and terminal must stay running for this preview;
press `Ctrl+C` to stop it. This is not a public internet URL.

## The 3-Day Rule

Each note gets its creation timestamp on its first nonempty save.

```text
expiresAt = createdAt + 72 hours
```

Editing and pasting screenshots do not reset this clock. Expired notes and
their screenshot blobs are deleted from IndexedDB, not just hidden.
Cleanup runs when opening or returning to the app,
before saves, and every 15 seconds while the page is running.

A closed or suspended browser cannot run cleanup. Expired data can remain on
disk until the app next runs; it is then deleted before displaying the notes.
This is application-level expiry, not guaranteed secure erasure. It relies on
the device clock and is not a suitable retention guarantee for sensitive data.

## Storage and Privacy

Notes use the browser's IndexedDB database `daynotes-images` (version 2).
The existing database name is retained so old screenshots can migrate too:

| Object store | Contains |
| --- | --- |
| `notes` | Titles, bodies, IDs, creation/update times and expiry |
| `images` | Screenshot blobs and their parent note IDs/expiry |
| `meta` | A migration marker to prevent duplicate imports |

Appearance settings still use `localStorage`; note text no longer does.
IndexedDB writes are asynchronous. **Wait for Saved before closing the page.**
The app attempts to save when hidden/leaving and warns about pending work,
but a forced close or crash can interrupt an unfinished write.

This storage is only on this browser and device.
There is no account, cloud backup, sync, encryption, or backend database.
Clearing site/browser data, using private browsing, changing browsers, or
moving the app to a different origin may lose access to the notes.
Direct `file://` storage behavior depends on the browser; keep opening the
same file in the same normal browser profile. Download important notes.

There are limits of 100 notes, 80,000 characters per body, and one million
characters total to keep local storage bounded. If saving fails or storage
is blocked, the editor warns you and still lets you download your text.
Downloads are ordinary files and are NOT automatically deleted after 3 days.
In browsers supporting BroadcastChannel, other open tabs refresh after changes.
Writes use transactions so adding different notes from two tabs does not
overwrite the whole list. Simultaneous edits to the same note still use the
last successful save; this is not collaborative editing.

### Existing Notes

On first opening this version, the app imports old `daynotes.v1` text records
from localStorage and upgrades the screenshot database. It preserves IDs,
text and creation times. Records still present get a deadline of **original
creation + 3 days**; older records and their screenshots are removed. Screenshots
inherit the parent's deadline. Already-deleted notes cannot be recovered.

The old text copy is removed only after the migration transaction commits,
and only if that copy has not changed meanwhile. Invalid data stops migration
and leaves the source untouched. A committed marker prevents leftover old data
from re-importing deleted notes. If source removal failed or an older tab writes
again, its leftover copy is retained but not automatically re-imported. Close
old-version tabs before upgrading; export their drafts first.

## Code Map

- `index.html`: the editor and accessible controls.
- `styles.css`: screenshot-inspired colors and responsive layout.
- `app.js`: autosave, selection, search, downloads, and cleanup scheduling.
- `storage.js`: shared IndexedDB connection, atomic note writes, migration and expiry rules.
- `image-storage.js`: IndexedDB screenshot blobs, limits, and expiry cleanup.
- `tests/store.test.cjs`: expiry, validation and migration-policy unit tests using Node.
- `tests/database_smoke.py`: real IndexedDB migration, asynchronous saves and cross-tab checks.
- `tests/screenshots_smoke.py`: an optional isolated-browser screenshot check.
- `tests/editing_scroll_smoke.py`: long-note Space/Backspace, caret, autosave
  and auto-height regression checks on desktop and mobile sizes.

Run checks from the repository root:

```powershell
node --check my_python_work/side_quests/daynotes/app.js
node --check my_python_work/side_quests/daynotes/storage.js
node --check my_python_work/side_quests/daynotes/image-storage.js
node --test my_python_work/side_quests/daynotes/tests/store.test.cjs
```

For development, if Playwright and Microsoft Edge are already installed, run
the screenshot lifecycle check from the repository root. It uses a fresh,
temporary browser profile, not your saved notes. Neither dependency is needed
to use Daynotes itself.

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/daynotes/tests/screenshots_smoke.py
.\.venv\Scripts\python.exe my_python_work/side_quests/daynotes/tests/editing_scroll_smoke.py
.\.venv\Scripts\python.exe my_python_work/side_quests/daynotes/tests/database_smoke.py
```

The editing check writes ignored viewport screenshots to `output/`.

## Later: Server Database and Sync

Replace the storage adapter with authenticated API requests and a database
record containing `id`, `owner`, `title`, `body`, `created_at`, `updated_at`, and
`expires_at`. Make the retention period configurable for longer-lived notes.
Use server timestamps and a scheduled cleanup job so deletion also happens
when nobody has the app open. Importing existing unexpired local notes into
that database would be a separate, explicit step; adding a database will not
automatically back up the current local notes.

Lucide icons are included under the license in `assets/icons/LICENSE.txt`.
