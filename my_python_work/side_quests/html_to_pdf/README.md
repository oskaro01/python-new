# HTML to PDF

For saved `.mhtml` / `.mht` webpages, use the dedicated
[MHTML to PDF side quest](../mhtml_to_pdf/README.md). It shares this print
engine while adding archive validation and offline rendering.

A Python desktop and command-line converter inspired by
`HTML-to-PDF-Friendly.ps1`. It uses Playwright with Chrome, Edge, or Chromium
to print local HTML rather than rebuilding the document with a limited HTML
parser. Your original PowerShell script is unchanged.

## Setup

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r my_python_work/side_quests/html_to_pdf/requirements.txt
```

Chrome or Edge can be used if already installed. Auto mode checks their usual
Windows installation paths, then installed Playwright Chromium. You can choose
a browser explicitly. For a separate browser install instead of a system one:

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

Python 3.10+ is required. The desktop UI uses Tkinter, normally included with
Python on Windows. The converter does not upload your HTML or PDFs anywhere.

## Desktop App

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/html_to_pdf/app.py
```

1. Browse for an `.html` or `.htm` file.
2. Choose where to save the PDF.
3. Keep **HTML print CSS** to preserve the document's `@page` rules, or select
   an explicit paper size. Landscape is available with explicit paper sizes.
4. Leave **Margin (mm)** blank to preserve HTML margins, or enter 0-70 mm to
   request an override for all sides.
5. Click **Convert to PDF**. The UI remains responsive while the browser works.
6. The completion dialog offers to open the PDF in your usual viewer.

The program asks before replacing an existing output. A failed render does
not replace it. Close the app after the current conversion has finished.

## Command Line

The output defaults to the same folder/name as the input, with `.pdf`:

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/html_to_pdf/app.py "C:\path to\resume.html"
```

Choose the destination and print overrides explicitly:

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/html_to_pdf/app.py "C:\path to\report.html" --output "C:\path to\report.pdf" --paper a4 --margin-mm 12 --browser edge --open
```

For HTML that creates content with JavaScript, wait for a visible ready marker
or add an extra delay:

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/html_to_pdf/app.py report.html --wait-for "#ready" --delay-ms 1000 --timeout 60
```

Useful flags:

| Option | Behavior |
| --- | --- |
| `--paper css` | Preserve HTML `@page` size; A4 fallback when none is defined |
| `--paper a4/a5/letter/legal` | Select an explicit size using one of those values |
| `--landscape` | Landscape with an explicit paper size |
| `--margin-mm 12` | Request a 12 mm margin override |
| `--browser auto/edge/chrome/chromium` | Choose one value, or let Auto detect a browser |
| `--no-background` | Omit background graphics |
| `--allow-missing-assets` | Export despite missing images/fonts/styles, with a warning |
| `--force` | Explicitly permit replacement of an existing output |
| `--open` | Open the completed PDF |

Omit the slash-separated alternatives when typing a command: for example use
`--browser edge`, not `--browser auto/edge/chrome/chromium`.

The load timeout covers launch and readiness waits, including the optional
selector and delay. Native PDF printing and browser shutdown may take longer;
it is not a hard process-kill deadline. CLI failures return exit code 1 and
invalid command arguments return 2. No arguments opens the desktop app.

## Rendering Details

- Print CSS, page breaks, backgrounds, tables, links, and installed/web fonts
  are handled by the browser. Browser-generated date/URL headers are disabled.
- Relative CSS, images, and fonts resolve from the original HTML file's
  location. Keep that folder structure intact; the source is never rewritten.
- Used fonts and regular/lazy `<img>` elements are awaited before printing.
  Failed image/font/stylesheet requests normally stop the conversion.
- Output is generated in a temporary PDF next to the destination, checked for
  a PDF signature, then moved into place. Temporary output is cleaned up after
  a failure. Generated PDFs are ignored by Git in this side quest.
- Browser profiles are temporary and isolated from your usual signed-in
  browser. Chromium sandboxing stays enabled.
- Tagged PDF and document outlines are requested. This alone does not certify
  accessibility, PDF/UA, or archival PDF/A compliance.

For a predictable source document:

```css
@page { size: A4; margin: 18mm; }
@media print { .screen-only { display: none; } }
table, figure { break-inside: avoid; }
* { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
```

Explicit overrides target the normal `@page` rule. Complex named-page styles,
unbreakable content, and conflicting author `!important` rules may need source
CSS changes. A browser cannot guarantee perfect pagination for arbitrary HTML.

Only convert trusted HTML. Its scripts execute and its external assets may
make network requests; this is not an HTML sanitization service. Fully local
documents/assets work offline. Logged-in web apps, URLs as direct inputs,
batch jobs, and a hosted upload service are outside this first version.

## Example and Checks

Try the supplied two-page document:

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/html_to_pdf/app.py my_python_work/side_quests/html_to_pdf/examples/print_demo.html --open
```

Fast validation tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s my_python_work/side_quests/html_to_pdf/tests -v
```

Real-browser PDF tests additionally use PyMuPDF to inspect page sizes, text,
page breaks, margins, and embedded images. They run in temporary directories:

```powershell
.\.venv\Scripts\python.exe -m pip install -r my_python_work/side_quests/html_to_pdf/requirements-dev.txt
$env:HTML_PDF_BROWSER="edge"
.\.venv\Scripts\python.exe -m unittest discover -s my_python_work/side_quests/html_to_pdf/tests -v
Remove-Item Env:HTML_PDF_BROWSER
```

References: [Playwright PDF API](https://playwright.dev/python/docs/api/class-page#page-pdf)
and [browser selection](https://playwright.dev/python/docs/browsers).
