"""
Web Foundations 08: Database Search, Filter, And Pagination

This file teaches:

- SQLite search with LIKE
- category filtering
- counting matching rows
- LIMIT and OFFSET pagination
- keeping filters in the URL

Run:

    python -B my_python_work/web_practice/01_web_foundations/08_database_search_pagination/app.py

Open:

    http://127.0.0.1:8000/products
"""

import math
import sqlite3
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse


HOST = "127.0.0.1"
PORT = 8000
PER_PAGE = 4
DB_FILE = Path(__file__).with_name("products.db")


STARTER_PRODUCTS = [
    ("Python Basics Book", "Books", 18, "A gentle book for learning Python."),
    ("Django Starter Course", "Courses", 49, "A practical course for web apps."),
    ("Study Notebook", "Tools", 8, "A notebook for coding notes."),
    ("Python Automation Course", "Courses", 35, "Automate files, CSVs, and daily tasks."),
    ("Algorithm Practice Book", "Books", 22, "Practice common coding patterns."),
    ("Mechanical Keyboard", "Tools", 75, "A comfortable keyboard for long sessions."),
    ("Django Deployment Guide", "Books", 27, "Learn deployment basics."),
    ("SQLite Pocket Reference", "Books", 14, "Small guide for SQL queries."),
    ("Debugging Checklist", "Tools", 6, "A checklist for finding code bugs."),
    ("Full Stack Python Path", "Courses", 59, "A roadmap from scripts to web apps."),
    ("Template Design Pack", "Tools", 19, "Simple page layout examples."),
    ("Web Security Basics", "Courses", 42, "Learn forms, cookies, and safer inputs."),
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
            connection.executemany("""
                INSERT INTO products (name, category, price, description)
                VALUES (?, ?, ?, ?)
            """, STARTER_PRODUCTS)


def build_where_clause(search, category):
    clauses = []
    params = []

    if search != "":
        clauses.append("(name LIKE ? OR description LIKE ?)")
        search_pattern = f"%{search}%"
        params.append(search_pattern)
        params.append(search_pattern)

    if category != "":
        clauses.append("category = ?")
        params.append(category)

    if len(clauses) == 0:
        return "", params

    return "WHERE " + " AND ".join(clauses), params


def count_products(search, category):
    where_clause, params = build_where_clause(search, category)

    with get_connection() as connection:
        row = connection.execute(f"""
            SELECT COUNT(*) AS total
            FROM products
            {where_clause}
        """, params).fetchone()

    return row["total"]


def search_products(search, category, page_number):
    where_clause, params = build_where_clause(search, category)
    offset = (page_number - 1) * PER_PAGE

    with get_connection() as connection:
        return connection.execute(f"""
            SELECT id, name, category, price, description
            FROM products
            {where_clause}
            ORDER BY id DESC
            LIMIT ?
            OFFSET ?
        """, params + [PER_PAGE, offset]).fetchall()


def categories():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT DISTINCT category
            FROM products
            ORDER BY category
        """).fetchall()

    return [row["category"] for row in rows]


def find_product(product_id):
    with get_connection() as connection:
        return connection.execute("""
            SELECT id, name, category, price, description
            FROM products
            WHERE id = ?
        """, (product_id,)).fetchone()


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
            max-width: 960px;
            margin: 40px auto;
            line-height: 1.5;
            padding: 0 18px;
            color: #20242c;
        }}

        input, select, button {{
            padding: 10px;
            font: inherit;
        }}

        button {{
            cursor: pointer;
        }}

        form {{
            display: grid;
            grid-template-columns: 1fr 180px auto;
            gap: 10px;
            align-items: end;
            margin: 18px 0;
        }}

        label {{
            display: block;
            font-weight: 700;
            margin-bottom: 4px;
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

        .pagination {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
            align-items: center;
        }}

        .button {{
            display: inline-block;
            padding: 8px 12px;
            background: #2563eb;
            color: #ffffff;
            border-radius: 6px;
            text-decoration: none;
        }}

        @media (max-width: 700px) {{
            form {{
                grid-template-columns: 1fr;
            }}
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


def get_query_value(query, name, default=""):
    return query.get(name, [default])[0].strip()


def positive_int(text, default=1):
    try:
        number = int(text)
    except ValueError:
        return default

    if number < 1:
        return default

    return number


def category_options(selected_category):
    options = ['<option value="">All categories</option>']

    for category in categories():
        selected = ""

        if category == selected_category:
            selected = " selected"

        safe_category = escape(category)
        options.append(f'<option value="{safe_category}"{selected}>{safe_category}</option>')

    return "\n".join(options)


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


def page_link(label, page_number, search, category):
    query = urlencode({
        "search": search,
        "category": category,
        "page": page_number,
    })
    return f'<a class="button" href="/products?{query}">{label}</a>'


def products_page(query):
    search = get_query_value(query, "search")
    category = get_query_value(query, "category")
    page_number = positive_int(get_query_value(query, "page", "1"))
    total = count_products(search, category)
    total_pages = max(1, math.ceil(total / PER_PAGE))

    if page_number > total_pages:
        page_number = total_pages

    products = search_products(search, category, page_number)
    cards = ""

    if len(products) == 0:
        cards = "<p>No products found.</p>"
    else:
        for product in products:
            cards += product_card(product)

    previous_link = ""
    next_link = ""

    if page_number > 1:
        previous_link = page_link("Previous", page_number - 1, search, category)

    if page_number < total_pages:
        next_link = page_link("Next", page_number + 1, search, category)

    body = f"""
    <h1>Database Product Search</h1>
    <p class="muted">Search and filter products from SQLite using query parameters.</p>

    <section class="panel">
        <form method="GET" action="/products">
            <div>
                <label for="search">Search</label>
                <input id="search" name="search" value="{escape(search)}" placeholder="python, django, notebook">
            </div>

            <div>
                <label for="category">Category</label>
                <select id="category" name="category">
                    {category_options(category)}
                </select>
            </div>

            <button type="submit">Apply</button>
        </form>
    </section>

    <p>{total} result(s). Page {page_number} of {total_pages}.</p>

    <section class="grid">
        {cards}
    </section>

    <nav class="pagination">
        {previous_link}
        {next_link}
    </nav>
    """
    return page("Products", body)


def product_detail_page(product):
    body = f"""
    <article class="panel">
        <p class="muted">{escape(product["category"])}</p>
        <h1>{escape(product["name"])}</h1>
        <p>{escape(product["description"])}</p>
        <p class="price">${product["price"]}</p>
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


class SearchHandler(BaseHTTPRequestHandler):
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


def main():
    initialize_database()
    server = ThreadingHTTPServer((HOST, PORT), SearchHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("Open http://127.0.0.1:8000/products")
    print("Press Ctrl+C to stop.")
    print(f"Saving products to: {DB_FILE}")
    server.serve_forever()


if __name__ == "__main__":
    main()

