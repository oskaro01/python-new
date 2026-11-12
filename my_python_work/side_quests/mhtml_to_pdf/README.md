# MHTML to PDF

A Python desktop and command-line converter for saved `.mhtml` / `.mht`
webpages. Long documents flow across normal PDF pages, not one very tall
screenshot. Text stays selectable where the source contains real text.

This side quest shares the browser print engine and controls with
[`html_to_pdf`](../html_to_pdf/README.md). Keep both folders together.
There is no server, database, upload service, or API key to configure.

## Setup

From the repository root, using Python 3.10+:

```powershell
.\.venv\Scripts\python.exe -m pip install -r my_python_work/side_quests/mhtml_to_pdf/requirements.txt
```

An installed Chrome or Edge browser works. Auto checks their usual Windows
installation locations, then installed Playwright Chromium. To install a
separate Chromium instead:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

The desktop window uses Tkinter, normally included with Python on Windows.

## Desktop App

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/mhtml_to_pdf/app.py
```

1. Browse for your `.mhtml` or `.mht` file.
2. Choose the output PDF location.
3. Leave **Layout** on **Auto**. Recognized saved ChatGPT conversations become
   a readable transcript with normal message spacing and multiple pages.
   **Original webpage** preserves the site's own print layout; **Chat transcript**
   explicitly requires recognizable saved messages.
4. Keep **HTML print CSS** to honor the document's print rules, or select
   **A4**, **A5**, **Letter**, or **Legal** explicitly.
5. Leave the margin blank to preserve the source rules, or enter millimeters.
6. Click **Convert to PDF**. The completion dialog offers to open the result.

Landscape becomes available after choosing an explicit paper size. Background
graphics are included by default. Existing PDFs require confirmation before
replacement, and failed conversions leave the original output intact.

## Command Line

The default output is beside the archive with the same name and `.pdf`:

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/mhtml_to_pdf/app.py "C:\path to\saved webpage.mhtml"
```

Choose your paper, margins, browser, and destination:

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/mhtml_to_pdf/app.py "C:\path to\saved webpage.mhtml" --output "C:\path to\report.pdf" --paper a4 --margin-mm 12 --browser edge --open
```

Try the included self-contained two-page archive:

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/mhtml_to_pdf/app.py my_python_work/side_quests/mhtml_to_pdf/examples/archived_notes.mhtml --open
```

Other flags: `--landscape`, `--no-background`, `--timeout 60`, `--delay-ms 500`,
`--allow-missing-assets`, and `--force` to permit replacing an existing output.
Use `--help` for all options. No arguments opens the desktop window.

For saved chats, **Auto** detects both message role attributes and newer
conversation role headings. It removes the sidebar, composer, message action
buttons, hidden duplicates, and fixed/scrolling app containers from the print
view. Message order, paragraphs, emphasis, links, code, tables, and saved images
are retained with readable system fonts. The default transcript uses A4 with
16 mm margins; explicit paper/margin controls still apply. Long messages can
continue across pages. This changes the printable layout, not the archive file.

To deliberately use a site's original layout:

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/mhtml_to_pdf/app.py "C:\path to\saved chat.mhtml" --layout original
```

Use `--layout chat` to require transcript conversion, or `--layout auto` for
automatic detection. Ordinary documents keep their original print layout in
Auto mode. A transcript's typography is standardized rather than a visual
copy of the chat app. Interactive widgets may need the original layout.

## How It Works

1. Python checks the input path and MIME multipart structure. A renamed HTML
   file or a truncated archive is rejected before launching the browser.
2. Chrome, Edge, or Chromium opens the archive directly. Its native
   MHTML loader resolves embedded HTML, CSS, images, and fonts; we do not
   extract and rewrite them into a fragile replacement webpage.
   Nonstandard LF-only archives receive a temporary standards-compliant MIME
   copy; decoded resource bytes are preserved and the copy is removed afterward.
3. The page context uses offline mode, disables page JavaScript, and blocks
   service workers. Saved resources can render without contacting the
   original website; missing resources are not fetched to repair the archive.
4. Auto reformats recognized chats, then the engine waits for the retained
   fonts/images, applies optional print overrides, and
   uses browser PDF printing to paginate the content.
5. It writes a temporary PDF, checks its signature, and then places it at the
   destination. Your archive is never modified.

An archive that the browser loads as an empty document is reported as an error
instead of silently producing a blank PDF.

The browser profile is temporary and separate from your signed-in browser.
Chromium sandboxing stays enabled. Only open trusted archives: this desktop
utility is not an untrusted-file processing service. Offline mode applies to
the page context, not a system-wide firewall around the browser process.

## What To Expect

- A saved article with text longer than a page naturally continues onto the
  next page. Existing print CSS and explicit page breaks are respected.
- Embedded images/styles/fonts work if they were actually saved in the
  archive. Missing assets normally stop conversion with a helpful message.
  **Allow missing assets** deliberately accepts an incomplete result instead.
- Chromium may block embedded resources whose original addresses use
  `file://`, even when they are included in an archive made from a local HTML
  file. We do not disable that security restriction. Convert the original
  HTML with the HTML side quest when available; normal HTTP(S) website
  archives do not have that particular local-file-origin restriction.
- Load all wanted content before saving a webpage. Infinite scrolling, hidden
  sections, video, unsaved lazy images, and interactive app data are not
  recreated from the original website.
- A virtualized chat can omit older messages from its saved HTML. Transcript
  mode prints all recognizable messages actually present in the archive; it
  cannot restore turns that the browser did not save.
- Print CSS may hide navigation, change colors, or use a different layout
  than the screen view. Very wide tables, fixed-height scroll containers,
  unbreakable elements, and complex named-page rules can need source changes.
  No converter can promise perfect pagination for every saved website.
- The load timeout covers browser launch and readiness waits, not a hard kill
  of native PDF printing or browser shutdown. Large archives use more RAM.
- Tagged PDF and outlines are requested, but this does not certify PDF/A or
  accessibility compliance. Batch conversion and a hosted service are not
  part of this version.

## Checks

Fast archive/CLI validation, without launching a browser:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s my_python_work/side_quests/mhtml_to_pdf/tests -v
```

Real-browser tests additionally inspect the PDFs with PyMuPDF. They verify
page breaks, selectable text, CSS, embedded images, paper overrides, missing
asset handling, and a long Chromium-generated snapshot after deleting its
original HTML/assets. Test data and output live in temporary directories.
Chat regression tests cover fixed-height scrolling layouts, current/older
role markup, long replies, message order, links, code, tables, embedded images,
and choosing the original layout.

```powershell
.\.venv\Scripts\python.exe -m pip install -r my_python_work/side_quests/mhtml_to_pdf/requirements-dev.txt
$env:MHTML_PDF_BROWSER="edge"
.\.venv\Scripts\python.exe -m unittest discover -s my_python_work/side_quests/mhtml_to_pdf/tests -v
Remove-Item Env:MHTML_PDF_BROWSER
```

References: [Playwright PDF printing](https://playwright.dev/python/docs/api/class-page#page-pdf),
[offline and script settings](https://playwright.dev/python/docs/api/class-browser#browser-new-context),
and [Chromium MHTML snapshots](https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-captureSnapshot).
