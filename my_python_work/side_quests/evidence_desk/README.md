# Evidence Desk

A side quest for turning Markdown evidence packs into editable workbooks with screenshots and Excel exports. It runs locally in your browser, without Python, an API key, a server or a build step.

## Open It

Open [index.html](index.html) in Edge or Chrome. Choose **Import Markdown** and select your `.md` file, or open the sample workbook first.

1. Choose a section in the left sidebar.
2. Fill in the answer fields. Prefilled country names and search phrases remain editable.
3. Click the **Screenshot clipboard** box beside an entry, then press **Ctrl+V** to paste a screenshot. The border highlights when the box is focused; it stays focused after pasting so you can add another image. You can still paste while an answer field is focused, or use **Add screenshot** to choose a file. The section-level box attaches evidence to the whole section.
4. Add a caption and source reference under the screenshot. Click its preview to enlarge it, or its download icon to retrieve it.
5. Set the section status when appropriate. Completion is your decision, not a claim that the app verified your research.
6. Choose **Export Excel** to download the filled `.xlsx` workbook.

The original Markdown file is never modified. Instructions inside an imported pack are displayed as document content; the app does not perform the research, call those links or follow those instructions automatically.

## What Becomes Editable?

The parser uses the Marked Markdown library rather than splitting table text by hand. It supports:

- Two-column tables such as `Required input | Your answer`.
- Record tables with blank cells, such as country, language, search phrase and observations.
- Transposed tables such as `Field | Video 1 | Video 2 | Video 3`, presented as one form per video.
- Markdown task checkboxes and a standalone `[Write here]` observations placeholder.
- Headings, prose, links and filled reference tables, displayed as reference content.

These conventions fit the supplied GCC evidence capture pack. Arbitrary Markdown is not a formal form schema; review the result after importing a differently structured document.

To explicitly make the next table editable, place this on its own line before the table:

```markdown
<!-- evidence:form -->
```

Use `<!-- evidence:reference -->` to keep the next table read-only, even if it has blank cells.

## Updating a Template

Choose **Update template** to select a revised `.md` file for the current workbook. Import Markdown instead creates a separate workbook.

Answers are matched by heading path, table headers, entry labels and field labels, not by line numbers. Renumbering a section alone does not reset its answers. Renaming headings, questions, table headers or identifying row labels may create new fields. Duplicate labels are distinguished by occurrence; reordering identical entries is ambiguous.

Unmatched answers are retained in a review panel and an Excel review sheet. Screenshots from changed entries also remain available for review and export. Updating a template does not silently throw them away. Download a backup before major structural revisions.

Updates are explicit: browsers cannot continuously watch an arbitrary file on your computer. Select the revised file again after changing it.

## Excel and Other Exports

**Export Excel** creates a real `.xlsx` file using ExcelJS:

- A workbook overview with metadata and section statuses.
- A worksheet per section, preserving filled tables, checklists and notes.
- Evidence IDs beside the matching answers.
- An Evidence worksheet with captions, source references and embedded PNG/JPEG screenshots. Images are fitted to their cells without overlapping the next row; the full image bytes are embedded.
- A review worksheet for answers no longer matched to the current template.

Answer text is exported as text, not as executable Excel formulas. Very long answers may require expanding cells in Excel. Workbooks with many full-size screenshots can be large.

**Backup** downloads a ZIP containing `project.json`, `template.md`, `report.md` and the original screenshot files. **Restore** imports that ZIP as a separate workbook without replacing the existing one. Restore recognizes Evidence Desk backups, not arbitrary `.xlsx` edits; Excel is an output format, not the editing source of truth.

**Print** includes the complete filled report and its evidence images, not only the section currently open. Your browser can save it as PDF.

For a ChatGPT handoff, start with the Excel workbook or the filled `report.md`. Keep the original screenshots available for direct upload when visual inspection matters. Do not assume every application or upload workflow will read images embedded in Excel. The app itself has no ChatGPT connection.

## Storage and Limits

Drafts and image blobs are stored in IndexedDB on this browser profile. There is **no 24-hour expiry**, cloud sync or database service. Refreshing or closing the page normally keeps saved work, but clearing site data, private browsing, browser eviction or moving to another browser/device can lose access. A backup ZIP is the portable copy. Browser storage is not encrypted application storage; use a trusted device. Edit a workbook in one tab at a time; simultaneous edits in multiple tabs can overwrite each other.

- Markdown: 500 KB maximum.
- Screenshots: PNG, JPEG or WebP; 5 MB and 16 megapixels maximum each.
- WebP is converted to PNG for Excel compatibility; its converted PNG must also fit the limit.
- Per workbook: 100 screenshots, 60 MB total image data.
- Per answer: 30,000 characters.

File bytes are stored separately from answer metadata. Deleting a screenshot or workbook removes its associated image records. Imported scripts and remote images are not rendered; links open only when clicked. A public deployment would still need a separate privacy/access design before sharing sensitive evidence.

## Source Files

`model.js` parses templates, identifies fields and preserves answers across revisions. `storage.js` owns IndexedDB transactions. `app.js` connects forms, pasted images and autosave. `exports.js` builds Excel and backup files. The UI is plain HTML/CSS/JavaScript with local Lucide icons.

Third-party browser libraries and their licenses are checked into `vendor/` so the app works offline. The npm dependencies are only needed when refreshing those copies or running the model tests:

```powershell
cd my_python_work/side_quests/evidence_desk
npm ci --ignore-scripts
npm run vendor
npm test
```

From the repository root, the optional browser smoke test requires Playwright and installed Edge:

```powershell
.\.venv\Scripts\python.exe my_python_work/side_quests/evidence_desk/tests/browser_smoke.py
```

It uses an isolated browser profile and writes ignored screenshots and exports to `output/`. Add `--template "C:\path\to\pack.md"` to exercise a large real template without modifying it.

Library references: [ExcelJS images](https://github.com/exceljs/exceljs#images), [Marked lexer](https://marked.js.org/using_advanced#the-lexer), [DOMPurify](https://github.com/cure53/DOMPurify), [fflate](https://github.com/101arrowz/fflate).

Dependency audit note: the current lockfile has no high/critical advisories, but npm reports a moderate `uuid` advisory through ExcelJS. It concerns v3/v5/v6 calls with a caller-supplied buffer; ExcelJS's dependency call sites use v4. This app writes new workbooks and does not import Excel files. Keep the advisory under review when updating dependencies; do not blindly force npm's suggested ExcelJS downgrade. See [the uuid advisory](https://github.com/advisories/GHSA-w5hq-g745-h8pq).
