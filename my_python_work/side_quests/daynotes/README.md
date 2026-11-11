# Daynotes

A small personal notes side quest with a charcoal background, soft gray text,
and a plain-text editor based on your screenshot. Markdown stays as text:
`## headings`, lists, and `**bold**` markers are not reformatted.

## Open It

Open [index.html](index.html) in your browser. No installation, database, API
key, or server is needed. All icons are bundled locally. Nothing is uploaded
or published by this app.

- Use the plus button for a new note; typing saves automatically.
- The side panel lists notes and searches their titles and text.
- Use the download icon to keep a `.txt` copy before a note expires.
- The trash icon deletes a note after confirmation.
- The panel icon opens the note list on phones or hides it on desktop.

## Get a Phone and PC URL with Render

Use the same Render workspace and GitHub repository as Addition Practice.
Create a separate **Static Site**, not a Web Service. No database, API keys,
start command, or changes to the repository's existing `render.yaml` are needed.

1. In VS Code Source Control, commit the new `daynotes` folder and this README,
   then push/sync to GitHub. Suggested message: `Add Daynotes with 24-hour expiry`.
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
same URL do not intentionally clear notes or change their 24-hour clock.

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

## The 24-Hour Rule

Each note gets its creation timestamp on its first nonempty save.

```text
expiresAt = createdAt + 24 hours
```

Editing does not reset this clock. Expired notes are removed from the stored
JSON, not just hidden. Cleanup runs when opening or returning to the app,
before saves, and every 15 seconds while the page is running.

A closed or suspended browser cannot run cleanup. Expired data can remain on
disk until the app next runs; it is then deleted before displaying the notes.
This is application-level expiry, not guaranteed secure erasure. It relies on
the device clock and is not a suitable retention guarantee for sensitive data.

## Storage and Privacy

Notes use `localStorage` under `daynotes.v1`, only on this browser and device.
There is no account, cloud backup, sync, encryption, or backend database.
Clearing site/browser data, using private browsing, changing browsers, or
moving the app to a different origin may lose access to the notes.
Direct `file://` storage behavior depends on the browser; keep opening the
same file in the same normal browser profile. Download important notes.

There are limits of 100 notes, 80,000 characters per body, and one million
characters total to keep local storage bounded. If saving fails or storage
is blocked, the editor warns you and still lets you download your text.
Downloads are ordinary files and are NOT automatically deleted after 24 hours.
Multiple tabs share the list; simultaneous edits to the same note use the
last successful save.

## Code Map

- `index.html`: the editor and accessible controls.
- `styles.css`: screenshot-inspired colors and responsive layout.
- `app.js`: autosave, selection, search, downloads, and cleanup scheduling.
- `storage.js`: local persistence and expiry rules, isolated from the UI.
- `tests/store.test.cjs`: small storage tests using Node's built-in test runner.

Run checks from the repository root:

```powershell
node --check my_python_work/side_quests/daynotes/app.js
node --check my_python_work/side_quests/daynotes/storage.js
node --test my_python_work/side_quests/daynotes/tests/store.test.cjs
```

## Later: Database Storage

Replace the storage adapter with authenticated API requests and a database
record containing `id`, `owner`, `title`, `body`, `created_at`, `updated_at`, and
`expires_at`. Make the retention period configurable for longer-lived notes.
Use server timestamps and a scheduled cleanup job so deletion also happens
when nobody has the app open. Importing existing unexpired local notes into
that database would be a separate, explicit step; adding a database will not
automatically back up the current local notes.

Lucide icons are included under the license in `assets/icons/LICENSE.txt`.
