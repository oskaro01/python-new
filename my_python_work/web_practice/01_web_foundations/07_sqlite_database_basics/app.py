"""
Web Foundations 07: SQLite Database Basics

This file teaches:

- creating a SQLite table
- inserting products
- selecting products
- finding one product by ID
- deleting products
- using SQL parameters safely

Run:

    python -B my_python_work/web_practice/01_web_foundations/07_sqlite_database_basics/app.py

Open:

    http://127.0.0.1:8000/products
"""

import sqlite3
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse


HOST = "127.0.0.1"
PORT = 8000
DB_FILE = Path(__file__).with_name("products.db")


STARTER_PRODUCTS = [
    {
        "name": "Python Basics Book",
        "category": "Books",
        "price": 18,
        "description": "A gentle book for building Python confidence.",
    },
    {
        "name": "Django Starter Course",
        "category": "Courses",
        "price": 49,
        "description": "A focused course for learning Django web development.",
    },
    {
        "name": "Study Notebook",
        "category": "Tools",
        "price": 8,
        "description": "A notebook for daily coding notes.",
    },
]


def get_connection():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price INTEGER NOT NULL,
                description TEXT NOT NULL
            )
        """)

        row = connection.execute("SELECT COUNT(*) AS total FROM products").fetchone()

        if row["total"] == 0:
            for product in STARTER_PRODUCTS:
                connection.execute("""
                    INSERT INTO products (name, category, price, description)
                    VALUES (?, ?, ?, ?)
                """, (
                    product["name"],
                    product["category"],
                    product["price"],
                    product["description"],
                ))


def all_products():
    with get_connection() as connection:
        return connection.execute("""
            SELECT id, name, category, price, description
            FROM products
            ORDER BY id DESC
        """).fetchall()


def find_product(product_id):
    with get_connection() as connection:
        return connection.execute("""
            SELECT id, name, category, price, description
            FROM products
            WHERE id = ?
        """, (product_id,)).fetchone()


def add_product(name, category, price, description):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO products (name, category, price, description)
            VALUES (?, ?, ?, ?)
        """, (name, category, price, description))


def delete_product(product_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM products WHERE id = ?", (product_id,))


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
            max-width: 920px;
            margin: 40px auto;
            line-height: 1.5;
            padding: 0 18px;
            color: #20242c;
        }}

        nav a {{
            margin-right: 12px;
        }}

        input, textarea, button {{
            display: block;
            width: 100%;
            margin: 7px 0 14px;
            padding: 10px;
            font: inherit;
        }}

        button {{
            cursor: pointer;
            width: auto;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 14px;
        }}

        .card, .panel {{
            border: 1px solid #dddddd;
            border-radius: 8px;
            padding: 16px;
        }}

        .muted {{
            color: #666666;
        }}

        .price {{
            font-weight: 700;
            font-size: 1.2rem;
        }}

        .alert {{
            border-radius: 8px;
            padding: 12px;
            font-weight: 700;
        }}

        .success {{
            background: #ecfdf5;
            border: 1px solid #10b981;
            color: #065f46;
        }}

        .error {{
            background: #fef2f2;
            border: 1px solid #ef4444;
            color: #991b1b;
        }}
    </style>
</head>
<body>
    <nav>
        <a href="/products">Products</a>
    </nav>
    <hr>
    {body}
</body>
</html>
"""


def product_card(product):
    return f"""
    <article class="card">
        <p class="muted">{escape(product["category"])}</p>
        <h2>{escape(product["name"])}</h2>
        <p>{escape(product["description"])}</p>
        <p class="price">${product["price"]}</p>
        <a href="/products/{product["id"]}">View details</a>
    </article>
    """


def alert_html(message, kind):
    if message == "":
        return ""

    return f'<p class="alert {kind}">{escape(message)}</p>'


def get_query_value(query, name):
    return query.get(name, [""])[0].strip()


def products_page(query=None):
    if query is None:
        query = {}

    error = get_query_value(query, "error")
    success = get_query_value(query, "success")
    message = alert_html(error, "error") + alert_html(success, "success")
    cards = ""

    for product in all_products():
        cards += product_card(product)

    body = f"""
    <h1>Products From SQLite</h1>
    <p class="muted">These products are stored in a real SQLite database file.</p>
    {message}

    <section class="panel">
        <h2>Add Product</h2>
        <form method="POST" action="/products/add">
            <label for="name">Name</label>
            <input id="name" name="name" placeholder="Product name" required>

            <label for="category">Category</label>
            <input id="category" name="category" placeholder="Books, Courses, Tools" required>

            <label for="price">Price</label>
            <input id="price" name="price" type="number" min="0" step="1" placeholder="25" required>
            <p class="muted">Use a whole number for now, like 25.</p>

            <label for="description">Description</label>
            <textarea id="description" name="description" placeholder="Short description" required></textarea>

            <button type="submit">Save product</button>
        </form>
    </section>

    <h2>Saved Products</h2>
    <section class="grid">
        {cards}
    </section>
    """
    return page("Products", body)


def product_detail_page(product):
    body = f"""
    <article class="panel">
        <p class="muted">{escape(product["category"])}</p>
        <h1>{escape(product["name"])}</h1>
        <p>{escape(product["description"])}</p>
        <p class="price">${product["price"]}</p>

        <form method="POST" action="/products/delete">
            <input type="hidden" name="product_id" value="{product["id"]}">
            <button type="submit">Delete product</button>
        </form>

        <p><a href="/products">Back to products</a></p>
    </article>
    """
    return page(product["name"], body)


def not_found_page(message):
    body = f"""
    <h1>404 - Not Found</h1>
    <p>{escape(message)}</p>
    <p><a href="/products">Back to products</a></p>
    """
    return page("Not Found", body)


def path_parts(path):
    clean_path = path.strip("/")

    if clean_path == "":
        return []

    return clean_path.split("/")


class DatabaseHandler(BaseHTTPRequestHandler):
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

    def read_form_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        return parse_qs(raw_body)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        parts = path_parts(path)

        if path == "/" or path == "/products":
            self.send_html(products_page(query))
        elif len(parts) == 2 and parts[0] == "products":
            product = find_product(parts[1])

            if product is None:
                self.send_html(not_found_page("Product does not exist."), 404)
            else:
                self.send_html(product_detail_page(product))
        elif path == "/favicon.ico":
            self.send_empty()
        else:
            self.send_html(not_found_page("No page matches this URL."), 404)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        form_data = self.read_form_data()

        if path == "/products/add":
            name = form_data.get("name", [""])[0].strip()
            category = form_data.get("category", [""])[0].strip()
            price_text = form_data.get("price", [""])[0].strip()
            description = form_data.get("description", [""])[0].strip()

            try:
                price = int(price_text)
            except ValueError:
                price = -1

            if name == "" or category == "" or description == "" or price < 0:
                query = urlencode({
                    "error": "Fill every field and use a whole number price.",
                })
                self.redirect(f"/products?{query}")
                return

            add_product(name, category, price, description)
            query = urlencode({"success": "Product saved."})
            self.redirect(f"/products?{query}")
        elif path == "/products/delete":
            product_id = form_data.get("product_id", [""])[0].strip()

            if product_id != "":
                delete_product(product_id)

            query = urlencode({"success": "Product deleted."})
            self.redirect(f"/products?{query}")
        else:
            self.send_html(not_found_page("No POST route matches this URL."), 404)


def main():
    initialize_database()
    server = ThreadingHTTPServer((HOST, PORT), DatabaseHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("Open http://127.0.0.1:8000/products")
    print("Press Ctrl+C to stop.")
    print(f"Saving products to: {DB_FILE}")
    server.serve_forever()


if __name__ == "__main__":
    main()
