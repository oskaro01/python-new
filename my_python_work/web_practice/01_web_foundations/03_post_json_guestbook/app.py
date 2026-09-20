"""
Web Foundations 03: POST Form And JSON Save

This file teaches:

- POST form submit
- reading form data
- simple validation
- saving data to JSON
- loading data again after restart
- redirect after POST

Run:

    python -B my_python_work/web_practice/01_web_foundations/03_post_json_guestbook/app.py

Open:

    http://127.0.0.1:8000
"""

import json
from datetime import datetime
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs


HOST = "127.0.0.1"
PORT = 8000
DATA_FILE = Path(__file__).with_name("messages.json")


def load_messages():
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    cleaned_messages = []

    for item in data:
        if not isinstance(item, dict):
            continue

        name = str(item.get("name", "")).strip()
        text = str(item.get("text", "")).strip()
        created_at = str(item.get("created_at", "")).strip()

        if text == "":
            continue

        if name == "":
            name = "Anonymous"

        cleaned_messages.append({
            "name": name,
            "text": text,
            "created_at": created_at,
        })

    return cleaned_messages


def save_messages(messages):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(messages, file, indent=4)


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
            max-width: 760px;
            margin: 40px auto;
            line-height: 1.5;
            padding: 0 18px;
        }}

        input, textarea, button {{
            display: block;
            width: 100%;
            margin: 8px 0 14px;
            padding: 10px;
            font: inherit;
        }}

        button {{
            width: auto;
            cursor: pointer;
        }}

        .message {{
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 14px;
            margin: 12px 0;
        }}

        .muted {{
            color: #666;
        }}
    </style>
</head>
<body>
    {body}
</body>
</html>
"""


def message_html(message):
    safe_name = escape(message["name"])
    safe_text = escape(message["text"])
    safe_created_at = escape(message["created_at"])

    return f"""
    <article class="message">
        <strong>{safe_name}</strong>
        <p>{safe_text}</p>
        <p class="muted">{safe_created_at}</p>
    </article>
    """


def home_page():
    messages = load_messages()

    if len(messages) == 0:
        saved_messages = "<p>No messages yet.</p>"
    else:
        saved_messages = ""

        for message in reversed(messages):
            saved_messages += message_html(message)

    body = f"""
    <h1>Guestbook</h1>
    <p>This page saves submitted messages to a JSON file.</p>

    <form method="POST" action="/messages">
        <label for="name">Name</label>
        <input id="name" name="name" placeholder="Your name">

        <label for="text">Message</label>
        <textarea id="text" name="text" placeholder="Write a message"></textarea>

        <button type="submit">Save message</button>
    </form>

    <h2>Saved Messages</h2>
    {saved_messages}
    """
    return page("Guestbook", body)


class GuestbookHandler(BaseHTTPRequestHandler):
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
        self.send_header("Connection", "close")
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_html(home_page())
        elif self.path == "/favicon.ico":
            self.send_empty()
        else:
            self.send_html(page("Not Found", "<h1>404 - Page not found</h1>"), 404)

    def do_POST(self):
        if self.path != "/messages":
            self.send_html(page("Not Found", "<h1>404 - Page not found</h1>"), 404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        form_data = parse_qs(raw_body)

        name = form_data.get("name", ["Anonymous"])[0].strip()
        text = form_data.get("text", [""])[0].strip()

        if name == "":
            name = "Anonymous"

        if text != "":
            messages = load_messages()
            messages.append({
                "name": name,
                "text": text,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            save_messages(messages)

        self.redirect("/")


def main():
    server = ThreadingHTTPServer((HOST, PORT), GuestbookHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    print(f"Saving messages to: {DATA_FILE}")
    server.serve_forever()


if __name__ == "__main__":
    main()

