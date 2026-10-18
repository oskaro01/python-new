# Browser Metadata Collector

This is a separate experiment from `url_id_collector`. The original tool
only reads bookmark files. This one opens a visible Microsoft Edge window and
reads the rendered page after Edge loads it.

## How Edge automation works

1. Paste one URL per line, a Markdown preview, or an exported bookmark HTML file into the app.
2. Click **Fetch pages in Edge**.
3. Playwright starts Microsoft Edge with a separate profile in this folder.
4. It visits each URL, waits for the page to render, and reads the DOM.
5. It collects the page title, description, actress links, and genre links.
6. The browser closes after the batch and the results appear in an editable preview.

The separate profile avoids changing your everyday Edge profile. If a page
shows a CAPTCHA or asks for an action, the browser remains visible so you can
see what happened. This tool does not download images or videos and does not
attempt to bypass access controls.

## Setup

From the repository root:

```powershell
python -m pip install playwright
```

Microsoft Edge must already be installed. Then run:

```powershell
python my_python_work/side_quests/browser_metadata_collector/app.py
```

The app uses Edge through Playwright's `channel="msedge"`; it does not need a
separate browser download. If Playwright reports that Edge cannot be found,
install or repair Microsoft Edge and try again.

The input parser keeps only valid `http://` and `https://` links. Titles,
`title:` lines, and other text are ignored, so a metadata file can be loaded
directly with **Open URL/bookmark file**.

## Notes

This is useful for many links because the app performs the repetitive opening
and copying work. It is not a guarantee that a site will permit automation.
The site may still return a block page or require you to interact manually.
