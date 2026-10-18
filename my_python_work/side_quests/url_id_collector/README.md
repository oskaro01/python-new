# Bookmark Metadata Collector

Small Python side quest for reading pasted links or Edge/Chrome bookmark HTML
exports. It extracts the bookmark title, code, and URL without visiting the
site. A bookmark like this:

```text
https://missav.ws/dm26/id/nuka-073
https://missav.ws/en/roe-070-english-subtitle
```

becomes a compact editable Markdown table. It accepts one link, many links,
or a browser bookmark export. Duplicate URLs are removed. Results can be
saved as CSV, TXT, or Markdown. Markdown uses clickable links in a table, and
the CSV URL column uses Excel's `HYPERLINK` formula.

## Run it

From the repository root:

```powershell
python my_python_work/side_quests/url_id_collector/app.py
```

Paste links into the input box, or click `Open bookmarks HTML` and select the
file exported by Edge. Click `Extract metadata`, edit the preview if needed,
then save it as CSV, TXT, or MD.

## Accepted shape

```text
https://missav.ws/dm26/id/nuka-073
https://missav.ws/dm26/id/abc-123?source=list
```

The tool supports both `/id/nuka-073` paths and code-prefixed slugs such as
`/en/roe-070-english-subtitle`. It also checks the beginning of the bookmark
title when the URL itself does not contain a code. The query string and
trailing slash are ignored. Records are saved once per unique URL, in the
order they first appear.

TXT uses this format:

```text
title: i decided to sleep
code: ROE-070
url: https://example.com/id/ROE-070
```

The separate browser-assisted experiment lives in
`my_python_work/side_quests/browser_metadata_collector/`.
