"""
Web Foundations 06: Dynamic Routes And 404 Pages

This file teaches:

- dynamic URLs like /products/1
- reading part of the path as a product ID
- product detail pages
- custom 404 pages
- serving static CSS

Run:

    python -B my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/app.py

Open:

    http://127.0.0.1:8000/products
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
        "id": "1",
        "name": "Python Basics Book",
        "category": "Books",
        "price": 18,
        "description": "A gentle book for building Python confidence.",
    },
    {
        "id": "2",
        "name": "Django Starter Course",
        "category": "Courses",
        "price": 49,
        "description": "A focused course for learning Django web development.",
    },
    {
        "id": "3",
        "name": "Study Notebook",
        "category": "Tools",
        "price": 8,
        "description": "A simple notebook for daily coding notes.",
    },
]


def find_product(product_id):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product

    return None


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
            <p>{escape(product["description"])}</p>
            <p class="price">${product["price"]}</p>
            <a class="button" href="/products/{escape(product["id"])}">View details</a>
        </article>
        """

    return cards


def products_page():
    body = render_template("products.html", {
        "products": product_cards(),
    })
    return render_page("Products", body)


def product_detail_page(product):
    body = render_template("product_detail.html", {
        "name": escape(product["name"]),
        "category": escape(product["category"]),
        "description": escape(product["description"]),
        "price": product["price"],
    })
    return render_page(product["name"], body)


def not_found_page(message):
    body = render_template("not_found.html", {
        "message": escape(message),
    })
    return render_page("Not Found", body)


def path_parts(path):
    clean_path = path.strip("/")

    if clean_path == "":
        return []

    return clean_path.split("/")


class DynamicRouteHandler(BaseHTTPRequestHandler):
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

        try:
            file_path.relative_to(static_root)
        except ValueError:
            self.send_html(not_found_page("Static file is outside the allowed folder."), 404)
            return

        if not file_path.is_file():
            self.send_html(not_found_page("Static file not found."), 404)
            return

        content_type = mimetypes.guess_type(file_path.name)[0]

        if content_type is None:
            content_type = "application/octet-stream"

        self.send_bytes(file_path.read_bytes(), content_type)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        parts = path_parts(path)

        print(f"Path parts: {parts}")

        if path == "/":
            self.send_html(products_page())
        elif path == "/products":
            self.send_html(products_page())
        elif len(parts) == 2 and parts[0] == "products":
            product = find_product(parts[1])

            if product is None:
                self.send_html(not_found_page("That product does not exist."), 404)
            else:
                self.send_html(product_detail_page(product))
        elif path.startswith("/static/"):
            self.send_static(path)
        elif path == "/favicon.ico":
            self.send_empty()
        else:
            self.send_html(not_found_page("No page matches this URL."), 404)


def main():
    server = ThreadingHTTPServer((HOST, PORT), DynamicRouteHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("Open http://127.0.0.1:8000/products")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()

