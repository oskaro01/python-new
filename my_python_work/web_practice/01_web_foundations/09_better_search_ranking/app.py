"""
Web Foundations 09: Better Search And Ranking

This file teaches:

- strict search
- fuzzy spelling search
- ranking results
- category filtering with SQL
- Python-side scoring

Run:

    python -B my_python_work/web_practice/01_web_foundations/09_better_search_ranking/app.py

Open the URL printed in the terminal.
"""

import re
import socket
import sqlite3
from difflib import SequenceMatcher
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse


HOST = "127.0.0.1"
PORT_CHOICES = [8000, 8001, 8002, 8003]
PER_PAGE = 5
DB_FILE = Path(__file__).with_name("products.db")


STARTER_PRODUCTS = [
    ("Python Basics Book", "Books", 18, "A gentle book for learning Python."),
    ("Django Starter Course", "Courses", 49, "A practical course for Django web apps."),
    ("Study Notebook", "Tools", 8, "A notebook for daily coding notes."),
    ("Python Automation Course", "Courses", 35, "Automate files, CSVs, and daily tasks."),
    ("Algorithm Practice Book", "Books", 22, "Practice common coding patterns."),
    ("Mechanical Keyboard", "Tools", 75, "A comfortable keyboard for long coding sessions."),
    ("Django Deployment Guide", "Books", 27, "Learn Django deployment basics."),
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


def all_categories():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT DISTINCT category
            FROM products
            ORDER BY category
        """).fetchall()

    return [row["category"] for row in rows]


def products_for_category(category):
    with get_connection() as connection:
        if category == "":
            return connection.execute("""
                SELECT id, name, category, price, description
                FROM products
            """).fetchall()

        return connection.execute("""
            SELECT id, name, category, price, description
            FROM products
            WHERE category = ?
        """, (category,)).fetchall()


def find_product(product_id):
    with get_connection() as connection:
        return connection.execute("""
            SELECT id, name, category, price, description
            FROM products
            WHERE id = ?
        """, (product_id,)).fetchone()


def words_from(text):
    # Turn text into simple lowercase words.
    # "Python Basics Book!" becomes ["python", "basics", "book"].
    return re.findall(r"[a-z0-9]+", text.lower())


def close_word_score(search_word, product_words):
    # SequenceMatcher gives a number from 0.0 to 1.0.
    # 1.0 means the words are exactly the same.
    best_score = 0

    for product_word in product_words:
        ratio = SequenceMatcher(None, search_word, product_word).ratio()

        if ratio > best_score:
            best_score = ratio

    if best_score >= 0.86:
        return 24

    if best_score >= 0.76:
        return 14

    return 0


def score_product(product, search):
    # This function answers: "How good is this product for this search?"
    # Bigger score means better result.
    search = search.strip().lower()

    if search == "":
        return 1, ["all products"]

    search_words = words_from(search)
    name = product["name"].lower()
    category = product["category"].lower()
    description = product["description"].lower()
    product_words = words_from(f"{name} {category} {description}")
    score = 0
    reasons = []

    # Whole-search checks are strong matches.
    # Example: searching "python basics book" should strongly match the full name.
    if search == name:
        score += 100
        reasons.append("exact name")
    elif search in name:
        score += 60
        reasons.append("name contains search")

    if search in category:
        score += 40
        reasons.append("category contains search")

    if search in description:
        score += 25
        reasons.append("description contains search")

    # Word-by-word checks help when the user searches more than one word.
    # Example: "python course" can match words in the name and description.
    for word in search_words:
        if word in name:
            score += 35
            reasons.append(f"name has '{word}'")

        if word in category:
            score += 25
            reasons.append(f"category has '{word}'")

        if word in description:
            score += 12
            reasons.append(f"description has '{word}'")

        fuzzy_score = close_word_score(word, product_words)

        if fuzzy_score > 0:
            score += fuzzy_score
            reasons.append(f"close spelling for '{word}'")

    # Keep the explanation readable by removing repeated reasons.
    unique_reasons = []

    for reason in reasons:
        if reason not in unique_reasons:
            unique_reasons.append(reason)

    return score, unique_reasons


def ranked_products(search, category):
    # First filter by category in SQL, then rank the remaining products in Python.
    rows = products_for_category(category)
    ranked = []

    for product in rows:
        score, reasons = score_product(product, search)

        if score > 0:
            ranked.append({
                "product": product,
                "score": score,
                "reasons": reasons,
            })

    ranked.sort(key=lambda item: (-item["score"], item["product"]["name"].lower()))
    return ranked


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

        .score {{
            color: #047857;
            font-weight: 700;
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

    for category in all_categories():
        selected = ""

        if category == selected_category:
            selected = " selected"

        safe_category = escape(category)
        options.append(f'<option value="{safe_category}"{selected}>{safe_category}</option>')

    return "\n".join(options)


def product_card(item):
    product = item["product"]
    product_id = product["id"]
    reasons = ", ".join(item["reasons"])

    return f"""
    <article class="card">
        <p class="muted">{escape(product["category"])}</p>
        <h2>{escape(product["name"])}</h2>
        <p>{escape(product["description"])}</p>
        <p class="price">${product["price"]}</p>
        <p class="score">Score: {item["score"]}</p>
        <p class="muted">Why: {escape(reasons)}</p>
        <a href="/products/{product_id}">View details</a>
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
    ranked = ranked_products(search, category)
    total = len(ranked)
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

    # If someone manually types a page that is too high, show the last page.
    if page_number > total_pages:
        page_number = total_pages

    start = (page_number - 1) * PER_PAGE
    end = start + PER_PAGE
    page_items = ranked[start:end]
    cards = ""

    if len(page_items) == 0:
        cards = "<p>No products found.</p>"
    else:
        for item in page_items:
            cards += product_card(item)

    previous_link = ""
    next_link = ""

    if page_number > 1:
        previous_link = page_link("Previous", page_number - 1, search, category)

    if page_number < total_pages:
        next_link = page_link("Next", page_number + 1, search, category)

    body = f"""
    <h1>Better Search And Ranking</h1>
    <p class="muted">Try typo searches like <code>pyton</code>, <code>djngo</code>, or <code>notebok</code>.</p>

    <section class="panel">
        <form method="GET" action="/products">
            <div>
                <label for="search">Search</label>
                <input id="search" name="search" value="{escape(search)}" placeholder="pyton, djngo, security">
            </div>

            <div>
                <label for="category">Category</label>
                <select id="category" name="category">
                    {category_options(category)}
                </select>
            </div>

            <button type="submit">Search</button>
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


class RankingHandler(BaseHTTPRequestHandler):
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


def create_server():
    for port in PORT_CHOICES:
        if port_is_busy(port):
            continue

        try:
            server = ThreadingHTTPServer((HOST, port), RankingHandler)
            return server, port
        except OSError:
            continue

    raise OSError("No available lesson port found.")


def port_is_busy(port):
    # On Windows, a second Python process can sometimes bind to a port that is
    # already answering. This small connection test helps us skip that port.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
        test_socket.settimeout(0.2)
        return test_socket.connect_ex((HOST, port)) == 0


def main():
    initialize_database()
    server, port = create_server()
    print(f"Server running at http://{HOST}:{port}")
    print(f"Open http://{HOST}:{port}/products")
    print("Press Ctrl+C to stop.")
    print(f"Saving products to: {DB_FILE}")
    server.serve_forever()


if __name__ == "__main__":
    main()
