"""
Web Foundations 05: Templates And Static Files

This file teaches:

- loading HTML from template files
- replacing simple placeholders
- serving CSS from /static/
- keeping Python, HTML, and CSS separate

Run:

    python -B my_python_work/web_practice/01_web_foundations/05_templates_static_files/app.py

Open:

    http://127.0.0.1:8000
"""

import mimetypes
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = 8000
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


PRODUCTS = [
    {
        "name": "Python Basics Book",
        "category": "Books",
        "price": 18,
    },
    {
        "name": "Django Starter Course",
        "category": "Courses",
        "price": 49,
    },
    {
        "name": "Study Notebook",
        "category": "Tools",
        "price": 8,
    },
]


def render_template(template_name, context):
    template_path = TEMPLATES_DIR / template_name
    html = template_path.read_text(encoding="utf-8")

    for key, value in context.items():
        placeholder = "{{ " + key + " }}"
        html = html.replace(placeholder, str(value))

    return html


def render_page(title, body):
    return render_template("base.html", {
        "title": escape(title),
        "body": body,
    })


def product_cards():
    cards = ""

    for product in PRODUCTS:
        cards += f"""
        <article class="card">
            <p class="eyebrow">{escape(product["category"])}</p>
            <h2>{escape(product["name"])}</h2>
            <p class="price">${product["price"]}</p>
        </article>
        """

    return cards


def home_page():
    body = render_template("home.html", {})
    return render_page("Home", body)


def products_page():
    body = render_template("products.html", {
        "products": product_cards(),
    })
    return render_page("Products", body)


class TemplateHandler(BaseHTTPRequestHandler):
    def send_html(self, html, status=200):
        html_bytes = html.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html_bytes)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(html_bytes)

    def send_bytes(self, data, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(data)

    def send_empty(self, status=204):
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

    def send_static(self, path):
        relative_path = path.removeprefix("/static/")
        static_root = STATIC_DIR.resolve()
        file_path = (STATIC_DIR / relative_path).resolve()

        if not str(file_path).startswith(str(static_root)):
            self.send_html(render_page("Forbidden", "<h1>403 - Forbidden</h1>"), 403)
            return

        if not file_path.is_file():
            self.send_html(render_page("Not Found", "<h1>404 - File not found</h1>"), 404)
            return

        content_type = mimetypes.guess_type(file_path.name)[0]

        if content_type is None:
            content_type = "application/octet-stream"

        self.send_bytes(file_path.read_bytes(), content_type)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/":
            self.send_html(home_page())
        elif path == "/products":
            self.send_html(products_page())
        elif path.startswith("/static/"):
            self.send_static(path)
        elif path == "/favicon.ico":
            self.send_empty()
        else:
            self.send_html(render_page("Not Found", "<h1>404 - Page not found</h1>"), 404)


def main():
    server = ThreadingHTTPServer((HOST, PORT), TemplateHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("Open http://127.0.0.1:8000")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()

