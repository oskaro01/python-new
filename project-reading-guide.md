# Understand an Unfamiliar Website Project

The fast route is not to read every file. Build a small map of the system,
then trace one real user action from start to finish. Budget roughly
20-30 minutes for a first map, not a complete understanding of every feature.

## 1. Find the Actual App Root

A repository can contain several applications. The Git root is not always the
folder you run. In this repository, Dictionary, Checkout, Chat Lab and Daynotes
have different application roots.

From the handed-over repository, first inspect its file list:

```powershell
Get-ChildItem -Force
rg --files -g '!**/node_modules/**' -g '!**/.venv/**' -g '!**/vendor/**' -g '!**/dist/**' -g '!**/build/**'
```

Then narrow the list to useful clues:

```powershell
rg --files -g 'README*' -g 'package.json' -g 'pyproject.toml' -g 'requirements*.txt' -g 'manage.py' -g 'composer.json' -g 'Dockerfile*' -g '*compose*.yml' -g '*compose*.yaml' -g '!**/node_modules/**' -g '!**/.venv/**' -g '!**/vendor/**'
```

Read the README closest to the actual application. Ask which folders are
running applications and which are examples, old versions or generated output.

## 2. Identify the Stack and How It Starts

| Clue | What to investigate |
| --- | --- |
| `package.json` | JavaScript/TypeScript dependencies and `scripts`; which framework and build/start commands are actually used? |
| `pyproject.toml` or `requirements.txt` | Python dependencies; look for the web framework and server packages. |
| `manage.py` | A Django project; follow settings, URLs, views, models and templates. |
| `composer.json` | PHP dependencies and framework clues. |
| `index.html` with local scripts/styles | Possibly a static browser app; inspect what its scripts do before assuming it needs a backend. |
| `Dockerfile`, Compose files, `render.yaml` | Build/start commands and required processes: web app, worker, database or cache. |
| `.env.example` | Configuration variable names and placeholder values, not real production secrets. |
| Lockfiles | The dependency versions used for reproducible installation. |

A dependency file is a clue, not proof that every listed technology is used.
Cross-check imports, entry points and deployment commands. Python test files
do not necessarily mean the website has a Python backend.

Read scripts before running them in an unfamiliar repository. Installation,
build scripts and container startup can execute code. Use a disposable local
environment and test database, not production credentials. Never paste real
`.env` values, tokens or customer data into a handover note.

At this point, write down: app folder, frontend, backend, storage, external
services, startup command and required environment variable names.

## 3. Find Entry Points and Draw a Small Map

Start with the files the browser or server loads first:

- Static site: `index.html`, its `<script>` tags and the event listeners in those scripts.
- Frontend framework: the main entry, page/router definitions, components and API client calls.
- Django: project settings and `urls.py`, then the view for the URL you are investigating.
- Other backend: the server entry/startup command, router registration and endpoint handlers.
- Background work: worker startup, scheduled tasks and webhook endpoints, if present.

Useful searches from the relevant app folder:

```powershell
rg -n 'addEventListener|fetch\(|axios|WebSocket|localStorage|indexedDB' -g '*.js' -g '*.ts' -g '*.jsx' -g '*.tsx' -g '!**/node_modules/**' -g '!**/vendor/**'
rg -n 'urlpatterns|INSTALLED_APPS|DATABASES|def |class ' -g '*.py' -g '!**/.venv/**'
```

Do not read all matches. Follow the ones involved in the feature you chose.
The framework's routing/configuration files are more reliable than assuming
that every project uses folders named `controllers`, `services` or `models`.

Your first map can be as small as:

```text
Browser UI -> HTTP API -> business rules -> database
                         -> external provider
                         -> queued job -> worker
```

Some applications have no server at all. Verify that instead of inventing an
API/database layer that does not exist.

## 4. Trace One User Action End to End

Choose something concrete: save a note, send a message, add an item to a cart
or log in. Do not start with "understand the whole app."

For a typical server-backed feature, follow:

```text
User action
-> component or form
-> browser event/request (URL, method and payload)
-> server route and authentication/permissions
-> validation
-> business logic
-> database, file storage or external API
-> response, redirect or real-time event
-> UI state, loading/error/success feedback
```

Record the actual filenames and function names at each step. A useful trace
also answers: what can fail, where does that error appear, and does the user
action save something immediately or merely schedule later work?

When it is safe to run the app locally, browser DevTools helps confirm the map:

- **Network:** request URL, payload, status code, response and Initiator.
- **Console:** runtime errors and relevant application logs.
- **Sources:** breakpoints in the event handler or API client.
- **Application:** localStorage, IndexedDB and cookies when browser storage matters.
- **Server/worker logs:** backend processing, queued jobs and failures.

Typing will not necessarily create a Network request. A browser-only app can
save locally. Conversely, one HTTP success response does not prove that an
email, payment event or worker job has finished. Trace that second process
and its completion/failure path separately.

## 5. Worked Example: Daynotes

Application root: `my_python_work/side_quests/daynotes`.

**Stack:** HTML, CSS and browser JavaScript. Text notes and preferences live in
localStorage; screenshot blobs live in IndexedDB. There is no application
backend or cloud database. Python is used for optional browser tests only.

The text-editing flow is:

```text
index.html loads storage.js, image-storage.js and app.js
-> app.js finds #note-title and #note-body
-> user types; the input listener marks the draft dirty
-> updateMeta() updates counts and controls
-> sizeBody() fits the textarea to its text
-> a 250 ms debounce schedules flush()
-> flush() calls NotesStore.save() in storage.js
-> save() validates limits and the original expiry, then writes localStorage
-> the UI reports Saved and refreshes the note list
```

Saving is synchronous when `flush()` runs. The delay before it is a debounce,
not a background server or worker. The 24-hour expiry remains based on the
original creation time, not on the most recent edit.

The screenshot flow is separate:

```text
Image paste event
-> flush text and ensure a note exists
-> ScreenshotStore validates and stores image blobs in IndexedDB
-> loadImages() rebuilds previews
-> expiry/deletion cleanup removes the blobs
```

### How This Exposes the Scroll Bug

The symptom was a long note jumping while pressing Space or Backspace.
Following the input listener points to `sizeBody()` before even investigating
the storage adapter. That function temporarily sets the textarea height to
zero to measure it. Shrinking the layout can clamp the outer editor's scroll
position, even if the final height is restored immediately afterward.

The fix remembers the writing surface's scroll position before measurement
and restores it afterward. It does not replace the note text, reset its expiry
or change the persistence format.

Read [app.js](my_python_work/side_quests/daynotes/app.js) for the UI flow and
[storage.js](my_python_work/side_quests/daynotes/storage.js) for text persistence.
This is the same investigation pattern you can apply to a larger application.

## 6. Finish With a One-Page Handover Map

Before claiming you understand the project, fill in:

```text
Purpose and main user workflows:
Actual app root(s):
Frontend/backend and dependency versions:
Entry point(s) and local start command(s):
Required config names (no secret values):
Storage: tables/models, files, browser storage:
External services and test environments:
One traced feature: UI -> handler -> storage/provider -> response -> UI:
Authentication/authorization boundaries:
Workers, scheduled tasks and webhooks:
Where errors and job results are logged:
Focused tests and commands:
Deployment/build/start processes:
Unverified assumptions and questions for the previous developer:
```

You do not need every implementation detail on day one. You need enough of a
verified map to know where to look when a feature needs changing or breaks.
