"""
Web Foundations 01: Tiny Python Web Server

This file teaches the web basics before Django:

- browser request
- server response
- URL routes
- HTML pages
- GET
- POST
- form data

Run:

    python -B my_python_work/web_practice/01_web_foundations/simple_server.py

Open:

    http://127.0.0.1:8000
"""

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs


HOST = "127.0.0.1"
PORT = 8000


messages = []


def page(title, body):
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 760px;
            margin: 40px auto;
            line-height: 1.5;
            padding: 0 18px;
        }}

        nav a {{
            margin-right: 12px;
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

        .box {{
            border: 1px solid #ddd;
            padding: 14px;
            margin: 12px 0;
            border-radius: 6px;
        }}
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
        <a href="/form">Form</a>
    </nav>
    <hr>
    {body}
</body>
</html>
"""


def home_page():
    body = """
    <h1>Python Web Foundations</h1>
    <p>This page came from Python, not from opening an HTML file directly.</p>
    <p>Your browser asked for <strong>/</strong>, and the server returned this HTML.</p>
    """
    return page("Home", body)


def about_page():
    body = """
    <h1>About This Server</h1>
    <p>This tiny server is using Python's built-in <code>http.server</code> module.</p>
    <p>Django will later give us a cleaner and more powerful way to do this.</p>
    """
    return page("About", body)


def form_page():
    saved_messages = ""

    if len(messages) == 0:
        saved_messages = "<p>No messages yet.</p>"
    else:
        for message in messages:
            safe_name = escape(message["name"])
            safe_text = escape(message["text"])
            saved_messages += f"""
            <div class="box">
                <strong>{safe_name}</strong>
                <p>{safe_text}</p>
            </div>
            """

    body = f"""
    <h1>Send A Message</h1>

    <form method="POST" action="/submit">
        <label for="name">Name</label>
        <input id="name" name="name" placeholder="Your name">

        <label for="text">Message</label>
        <textarea id="text" name="text" placeholder="Write something"></textarea>

        <button type="submit">Send</button>
    </form>

    <h2>Saved Messages</h2>
    {saved_messages}
    """
    return page("Form", body)


class SimpleWebHandler(BaseHTTPRequestHandler):
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
        self.end_headers()

    def do_GET(self):
        # GET requests usually ask to read/view something.
        if self.path == "/":
            self.send_html(home_page())
        elif self.path == "/about":
            self.send_html(about_page())
        elif self.path == "/form":
            self.send_html(form_page())
        elif self.path == "/favicon.ico":
            self.send_empty()
        else:
            self.send_html(page("Not Found", "<h1>404 - Page not found</h1>"), 404)

    def do_POST(self):
        # POST requests usually submit/change something.
        if self.path != "/submit":
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
            messages.append({
                "name": name,
                "text": text,
            })

        # Redirect after POST prevents duplicate form submit on refresh.
        self.redirect("/form")


def main():
    server = ThreadingHTTPServer((HOST, PORT), SimpleWebHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
