"""
Web Foundations 10: File Uploads And Media

This file teaches:

- upload forms
- multipart/form-data
- reading uploaded file bytes
- safer file names
- allowed file extensions
- upload size limits
- serving uploaded files back to the browser

Run:

    python -B my_python_work/web_practice/01_web_foundations/10_file_uploads_media/app.py

Open the URL printed in the terminal.
"""

import mimetypes
import socket
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse


HOST = "127.0.0.1"
PORT_CHOICES = [8000, 8001, 8002, 8003]
MAX_UPLOAD_SIZE = 2 * 1024 * 1024
UPLOAD_DIR = Path(__file__).with_name("uploads")
SAFE_FILENAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
ALLOWED_EXTENSIONS = {".txt", ".md", ".csv", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def page(title, body):
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            line-height: 1.5;
            padding: 0 18px;
            color: #20242c;
        }}

        input, button {{
            padding: 10px;
            font: inherit;
        }}

        button {{
            cursor: pointer;
        }}

        form {{
            display: grid;
            gap: 12px;
            margin: 18px 0;
        }}

        .panel, .file {{
            border: 1px solid #dddddd;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 14px;
        }}

        .muted {{
            color: #666666;
        }}

        .success {{
            border-color: #86efac;
            background: #f0fdf4;
        }}

        .error {{
            border-color: #fca5a5;
            background: #fef2f2;
        }}

        .preview {{
            display: block;
            max-width: 220px;
            max-height: 160px;
            object-fit: contain;
            margin-top: 8px;
            border: 1px solid #eeeeee;
        }}
    </style>
</head>
<body>
    <nav>
        <a href="/">Upload</a>
    </nav>
    <hr>
    {body}
</body>
</html>
"""


def get_query_value(query, name, default=""):
    return query.get(name, [default])[0]


def format_size(size):
    if size < 1024:
        return f"{size} bytes"

    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"

    return f"{size / (1024 * 1024):.1f} MB"


def safe_filename(original_filename):
    # Never trust the file name that came from the user's computer.
    # Path(...).name removes folders like C:\fakepath\photo.png or ../../secret.txt.
    base_name = Path(original_filename).name.replace(" ", "_")
    cleaned = ""

    for character in base_name:
        if character in SAFE_FILENAME_CHARS:
            cleaned += character

    cleaned = cleaned.strip("._")

    if cleaned == "":
        return "upload.bin"

    path = Path(cleaned)
    stem = path.stem[:50] or "upload"
    suffix = path.suffix.lower()[:10]
    return f"{stem}{suffix}"


def is_allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def unique_upload_path(filename):
    UPLOAD_DIR.mkdir(exist_ok=True)
    target = UPLOAD_DIR / filename

    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix

    for number in range(1, 1000):
        candidate = UPLOAD_DIR / f"{stem}_{number}{suffix}"

        if not candidate.exists():
            return candidate

    raise ValueError("Too many files with the same name.")


def uploaded_files():
    if not UPLOAD_DIR.exists():
        return []

    files = []

    for path in UPLOAD_DIR.iterdir():
        if path.is_file():
            files.append(path)

    return sorted(files, key=lambda path: path.name.lower())


def parse_header_params(header_value):
    params = {}
    parts = header_value.split(";")

    for part in parts[1:]:
        if "=" in part:
            key, value = part.strip().split("=", 1)
            params[key.lower()] = value.strip().strip('"')

    return params


def extract_uploaded_file(body, boundary):
    # This is a small beginner parser for one upload field.
    # Real frameworks like Django handle this parsing for us.
    boundary_marker = f"--{boundary}".encode("utf-8")

    for raw_part in body.split(boundary_marker):
        part = raw_part

        if part in (b"", b"--", b"--\r\n"):
            continue

        if part.startswith(b"--"):
            continue

        if part.startswith(b"\r\n"):
            part = part[2:]

        if part.endswith(b"\r\n"):
            part = part[:-2]

        if b"\r\n\r\n" not in part:
            continue

        header_bytes, content = part.split(b"\r\n\r\n", 1)
        headers = header_bytes.decode("utf-8", errors="replace")

        for line in headers.splitlines():
            if line.lower().startswith("content-disposition:"):
                disposition = line.split(":", 1)[1].strip()
                params = parse_header_params(disposition)

                if params.get("name") == "upload":
                    return {
                        "filename": params.get("filename", ""),
                        "content": content,
                    }

    return None


def upload_alert(query):
    message = get_query_value(query, "message")
    status = get_query_value(query, "status")

    if message == "":
        return ""

    css_class = "success"

    if status == "error":
        css_class = "error"

    return f'<p class="panel {css_class}">{escape(message)}</p>'


def file_card(path):
    file_url = f"/uploads/{quote(path.name)}"
    preview = ""

    if path.suffix.lower() in IMAGE_EXTENSIONS:
        preview = f'<img class="preview" src="{file_url}" alt="{escape(path.name)}">'

    return f"""
    <article class="file">
        <strong>{escape(path.name)}</strong>
        <p class="muted">{format_size(path.stat().st_size)}</p>
        <a href="{file_url}">Open file</a>
        {preview}
    </article>
    """


def uploaded_file_list():
    files = uploaded_files()

    if len(files) == 0:
        return '<p class="muted">No uploads yet.</p>'

    html = ""

    for path in files:
        html += file_card(path)

    return html


def upload_page(query):
    allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
    body = f"""
    <h1>File Uploads And Media</h1>
    <p class="muted">Upload a small file, then Python saves it into the lesson's uploads folder.</p>

    {upload_alert(query)}

    <section class="panel">
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <label for="upload">Choose a file</label>
            <input id="upload" name="upload" type="file" required>
            <button type="submit">Upload</button>
        </form>
        <p class="muted">Allowed: {escape(allowed)}</p>
        <p class="muted">Max size: {format_size(MAX_UPLOAD_SIZE)}</p>
    </section>

    <h2>Uploaded Files</h2>
    {uploaded_file_list()}
    """
    return page("File Uploads", body)


def not_found_page(message):
    body = f"""
    <h1>404 - Not Found</h1>
    <p>{escape(message)}</p>
    <p><a href="/">Back to upload page</a></p>
    """
    return page("Not Found", body)


def redirect_location(status, message):
    query = urlencode({
        "status": status,
        "message": message,
    })
    return f"/?{query}"


def safe_upload_lookup(filename):
    decoded_name = unquote(filename)

    if decoded_name != safe_filename(decoded_name):
        return None

    target = UPLOAD_DIR / decoded_name
    upload_root = UPLOAD_DIR.resolve()

    try:
        resolved_target = target.resolve()
    except OSError:
        return None

    if resolved_target.parent != upload_root:
        return None

    if not resolved_target.is_file():
        return None

    return resolved_target


def port_is_busy(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
        test_socket.settimeout(0.2)
        return test_socket.connect_ex((HOST, port)) == 0


def create_server():
    for port in PORT_CHOICES:
        if port_is_busy(port):
            continue

        try:
            server = ThreadingHTTPServer((HOST, port), UploadHandler)
            return server, port
        except OSError:
            continue

    raise OSError("No available lesson port found.")


class UploadHandler(BaseHTTPRequestHandler):
    def send_html(self, html, status=200):
        html_bytes = html.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html_bytes)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(html_bytes)

    def send_empty(self, status=204):
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

    def redirect(self, location):
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

    def send_uploaded_file(self, path):
        content = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)

        if path == "/":
            self.send_html(upload_page(query))
        elif path.startswith("/uploads/"):
            filename = path.removeprefix("/uploads/")
            upload_path = safe_upload_lookup(filename)

            if upload_path is None:
                self.send_html(not_found_page("Uploaded file does not exist."), 404)
            else:
                self.send_uploaded_file(upload_path)
        elif path == "/favicon.ico":
            self.send_empty()
        else:
            self.send_html(not_found_page("No page matches this URL."), 404)

    def do_POST(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path != "/upload":
            self.send_html(not_found_page("No page matches this URL."), 404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.redirect(redirect_location("error", "Invalid upload size."))
            return

        if content_length <= 0:
            self.redirect(redirect_location("error", "Choose a file first."))
            return

        if content_length > MAX_UPLOAD_SIZE:
            self.redirect(redirect_location("error", "File is too large for this lesson."))
            return

        boundary = self.headers.get_boundary()

        if boundary is None:
            self.redirect(redirect_location("error", "Upload form data was not understood."))
            return

        body = self.rfile.read(content_length)
        upload = extract_uploaded_file(body, boundary)

        if upload is None or upload["filename"] == "":
            self.redirect(redirect_location("error", "No file was uploaded."))
            return

        filename = safe_filename(upload["filename"])

        if not is_allowed_file(filename):
            self.redirect(redirect_location("error", "That file type is not allowed here."))
            return

        target = unique_upload_path(filename)
        target.write_bytes(upload["content"])
        self.redirect(redirect_location("ok", f"Saved {target.name}."))


def main():
    server, port = create_server()
    print(f"Server running at http://{HOST}:{port}")
    print(f"Open http://{HOST}:{port}/")
    print("Press Ctrl+C to stop.")
    print(f"Saving uploads to: {UPLOAD_DIR}")
    server.serve_forever()


if __name__ == "__main__":
    main()
