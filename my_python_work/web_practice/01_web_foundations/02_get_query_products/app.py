"""
Web Foundations 02: GET Query Parameters

This file teaches:

- query parameters
- search forms with method="GET"
- filtering data from the URL 
- product listing pages

Run:

    python -B my_python_work/web_practice/01_web_foundations/02_get_query_products/app.py

Open:

    http://127.0.0.1:8000/products

Try:

    http://127.0.0.1:8000/products?search=python
    http://127.0.0.1:8000/products?category=books

Important:

GET is good for search/filter pages because the search lives in the URL.
That means you can bookmark it, refresh it, and share it.
"""

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse


HOST = "127.0.0.1"
PORT = 8000


PRODUCTS = [
    {
        "id": 1,
        "name": "Python Basics Book",
        "category": "books",
        "price": 18,
    },
    {
        "id": 2,
        "name": "Django Web Course",
        "category": "courses",
        "price": 49,
    },
    {
        "id": 3,
        "name": "Mechanical Keyboard",
        "category": "tools",
        "price": 75,
    },
    {
        "id": 4,
        "name": "Algorithm Practice Notebook",
        "category": "books",
        "price": 12,
    },
    {
        "id": 5,
        "name": "Python Automation Course",
        "category": "courses",
        "price": 35,
    },
]


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
        }}

        nav a {{
            margin-right: 12px;
        }}

        form {{
            display: grid;
            grid-template-columns: 1fr 180px auto;
            gap: 10px;
            align-items: end;
            margin: 22px 0;
        }}

        label {{
            display: block;
            font-weight: 700;
            margin-bottom: 4px;
        }}

        input, select, button {{
            width: 100%;
            padding: 10px;
            font: inherit;
        }}

        button {{
            cursor: pointer;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
        }}

        .card {{
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 14px;
        }}

        .muted {{
            color: #666;
        }}

        @media (max-width: 680px) {{
            form {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/products">Products</a>
    </nav>
    <hr>
    {body}
</body>
</html>
"""


def home_page():
    body = """
    <h1>GET Query Parameters</h1>
    <p>Today we are learning how search/filter data can live inside the URL.</p>
    <p>Open <a href="/products">Products</a> and try the search form.</p>
    """
    return page("Home", body)


def get_query_value(query, name, default=""):
    values = query.get(name, [default])
    return values[0].strip()


def product_matches(product, search, category):
    name = product["name"].lower()
    product_category = product["category"].lower()

    if search != "" and search.lower() not in name:
        return False

    if category != "" and category.lower() != product_category:
        return False

    return True


def filter_products(search, category):
    results = []

    for product in PRODUCTS:
        if product_matches(product, search, category):
            results.append(product)

    return results


def category_options(selected_category):
    categories = sorted({product["category"] for product in PRODUCTS})
    html = ['<option value="">All categories</option>']

    for category in categories:
        selected = ""

        if category == selected_category:
            selected = " selected"

        safe_category = escape(category)
        html.append(f'<option value="{safe_category}"{selected}>{safe_category}</option>')

    return "\n".join(html)


def product_card(product):
    query = urlencode({"id": product["id"]})

    return f"""
    <article class="card">
        <h2>{escape(product["name"])}</h2>
        <p class="muted">{escape(product["category"])}</p>
        <p>${product["price"]}</p>
        <a href="/product?{query}">View details</a>
    </article>
    """


def products_page(query):
    search = get_query_value(query, "search")
    category = get_query_value(query, "category")
    results = filter_products(search, category)

    cards = ""

    if len(results) == 0:
        cards = "<p>No products found.</p>"
    else:
        for product in results:
            cards += product_card(product)

    body = f"""
    <h1>Products</h1>
    <p class="muted">This form uses <code>method="GET"</code>, so the search appears in the URL.</p>

    <form method="GET" action="/products">
        <div>
            <label for="search">Search</label>
            <input id="search" name="search" value="{escape(search)}" placeholder="python, book, course">
        </div>

        <div>
            <label for="category">Category</label>
            <select id="category" name="category">
                {category_options(category)}
            </select>
        </div>

        <button type="submit">Filter</button>
    </form>

    <p>{len(results)} product(s) found.</p>

    <div class="grid">
        {cards}
    </div>
    """
    return page("Products", body)


def product_detail_page(query):
    product_id_text = get_query_value(query, "id")

    for product in PRODUCTS:
        if str(product["id"]) == product_id_text:
            body = f"""
            <h1>{escape(product["name"])}</h1>
            <p>Category: {escape(product["category"])}</p>
            <p>Price: ${product["price"]}</p>
            <p><a href="/products">Back to products</a></p>
            """
            return page(product["name"], body)

    return page("Not Found", "<h1>Product not found</h1><p><a href=\"/products\">Back</a></p>")


class QueryWebHandler(BaseHTTPRequestHandler):
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

        print(f"Path: {path}")
        print(f"Query: {query}")

        if path == "/":
            self.send_html(home_page())
        elif path == "/products":
            self.send_html(products_page(query))
        elif path == "/product":
            self.send_html(product_detail_page(query))
        elif path == "/favicon.ico":
            self.send_empty()
        else:
            self.send_html(page("Not Found", "<h1>404 - Page not found</h1>"), 404)


def main():
    server = ThreadingHTTPServer((HOST, PORT), QueryWebHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("Open http://127.0.0.1:8000/products")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
