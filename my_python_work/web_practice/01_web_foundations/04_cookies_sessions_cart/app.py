"""
Web Foundations 04: Cookies, Sessions, And A Tiny Cart

This file teaches:

- cookies
- sessions
- server-side cart data
- POST actions for add/remove/clear
- saving session data to JSON

Run:

    python -B my_python_work/web_practice/01_web_foundations/04_cookies_sessions_cart/app.py

Open:

    http://127.0.0.1:8000/products
"""

import json
from html import escape
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from uuid import uuid4


HOST = "127.0.0.1"
PORT = 8000
SESSION_COOKIE_NAME = "session_id"
SESSIONS_FILE = Path(__file__).with_name("sessions.json")


PRODUCTS = [
    {
        "id": "1",
        "name": "Python Basics Book",
        "price": 18,
    },
    {
        "id": "2",
        "name": "Django Starter Course",
        "price": 49,
    },
    {
        "id": "3",
        "name": "Study Notebook",
        "price": 8,
    },
]


def product_by_id(product_id):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product

    return None


def load_sessions():
    if not SESSIONS_FILE.exists():
        return {}

    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(data, dict):
        return {}

    cleaned_sessions = {}

    for session_id, session_data in data.items():
        if not isinstance(session_id, str):
            continue

        if not isinstance(session_data, dict):
            continue

        raw_cart = session_data.get("cart", {})

        if not isinstance(raw_cart, dict):
            raw_cart = {}

        cart = {}

        for product_id, quantity in raw_cart.items():
            if product_by_id(str(product_id)) is None:
                continue

            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                continue

            if quantity > 0:
                cart[str(product_id)] = quantity

        cleaned_sessions[session_id] = {"cart": cart}

    return cleaned_sessions


def save_sessions(sessions):
    with open(SESSIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(sessions, file, indent=4)


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

        button {{
            cursor: pointer;
            padding: 9px 12px;
            font: inherit;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            border-bottom: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}

        .muted {{
            color: #666;
        }}
    </style>
</head>
<body>
    <nav>
        <a href="/products">Products</a>
        <a href="/cart">Cart</a>
    </nav>
    <hr>
    {body}
</body>
</html>
"""


def cart_total(cart):
    total = 0

    for product_id, quantity in cart.items():
        product = product_by_id(product_id)

        if product is not None:
            total += product["price"] * quantity

    return total


def cart_count(cart):
    total = 0

    for quantity in cart.values():
        total += quantity

    return total


def product_card(product):
    return f"""
    <article class="card">
        <h2>{escape(product["name"])}</h2>
        <p>${product["price"]}</p>
        <form method="POST" action="/cart/add">
            <input type="hidden" name="product_id" value="{escape(product["id"])}">
            <button type="submit">Add to cart</button>
        </form>
    </article>
    """


def products_page(cart):
    cards = ""

    for product in PRODUCTS:
        cards += product_card(product)

    body = f"""
    <h1>Products</h1>
    <p class="muted">Cart items in this session: {cart_count(cart)}</p>
    <div class="grid">
        {cards}
    </div>
    """
    return page("Products", body)


def cart_page(cart):
    if len(cart) == 0:
        body = """
        <h1>Your Cart</h1>
        <p>Your cart is empty.</p>
        <p><a href="/products">Back to products</a></p>
        """
        return page("Cart", body)

    rows = ""

    for product_id, quantity in cart.items():
        product = product_by_id(product_id)

        if product is None:
            continue

        line_total = product["price"] * quantity
        rows += f"""
        <tr>
            <td>{escape(product["name"])}</td>
            <td>{quantity}</td>
            <td>${product["price"]}</td>
            <td>${line_total}</td>
            <td>
                <form method="POST" action="/cart/remove">
                    <input type="hidden" name="product_id" value="{escape(product_id)}">
                    <button type="submit">Remove one</button>
                </form>
            </td>
        </tr>
        """

    body = f"""
    <h1>Your Cart</h1>
    <table>
        <thead>
            <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Total</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>

    <h2>Total: ${cart_total(cart)}</h2>

    <form method="POST" action="/cart/clear">
        <button type="submit">Clear cart</button>
    </form>

    <p><a href="/products">Back to products</a></p>
    """
    return page("Cart", body)


class CartHandler(BaseHTTPRequestHandler):
    def get_session_id(self):
        cookie_header = self.headers.get("Cookie", "")
        cookie = SimpleCookie(cookie_header)

        if SESSION_COOKIE_NAME in cookie:
            session_id = cookie[SESSION_COOKIE_NAME].value.strip()

            if session_id != "":
                return session_id, False

        return uuid4().hex, True

    def get_cart(self, session_id):
        sessions = load_sessions()

        if session_id not in sessions:
            sessions[session_id] = {"cart": {}}
            save_sessions(sessions)

        return sessions[session_id]["cart"]

    def set_session_cookie(self, session_id):
        cookie_value = (
            f"{SESSION_COOKIE_NAME}={session_id}; "
            "Path=/; HttpOnly; SameSite=Lax"
        )
        self.send_header("Set-Cookie", cookie_value)

    def send_html(self, html, session_id=None, status=200):
        html_bytes = html.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html_bytes)))
        self.send_header("Connection", "close")

        if session_id is not None:
            self.set_session_cookie(session_id)

        self.end_headers()
        self.wfile.write(html_bytes)

    def send_empty(self, status=204):
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()

    def redirect(self, location, session_id=None):
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Connection", "close")

        if session_id is not None:
            self.set_session_cookie(session_id)

        self.end_headers()

    def read_form_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        return parse_qs(raw_body)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        session_id, is_new_session = self.get_session_id()
        cart = self.get_cart(session_id)
        cookie_to_send = session_id if is_new_session else None

        if path == "/" or path == "/products":
            self.send_html(products_page(cart), cookie_to_send)
        elif path == "/cart":
            self.send_html(cart_page(cart), cookie_to_send)
        elif path == "/favicon.ico":
            self.send_empty()
        else:
            self.send_html(page("Not Found", "<h1>404 - Page not found</h1>"), None, 404)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        session_id, is_new_session = self.get_session_id()
        sessions = load_sessions()

        if session_id not in sessions:
            sessions[session_id] = {"cart": {}}

        cart = sessions[session_id]["cart"]
        form_data = self.read_form_data()

        if path == "/cart/add":
            product_id = form_data.get("product_id", [""])[0]

            if product_by_id(product_id) is not None:
                cart[product_id] = cart.get(product_id, 0) + 1

            save_sessions(sessions)
            self.redirect("/cart", session_id if is_new_session else None)
        elif path == "/cart/remove":
            product_id = form_data.get("product_id", [""])[0]

            if product_id in cart:
                cart[product_id] -= 1

                if cart[product_id] <= 0:
                    del cart[product_id]

            save_sessions(sessions)
            self.redirect("/cart", session_id if is_new_session else None)
        elif path == "/cart/clear":
            sessions[session_id]["cart"] = {}
            save_sessions(sessions)
            self.redirect("/cart", session_id if is_new_session else None)
        else:
            self.send_html(page("Not Found", "<h1>404 - Page not found</h1>"), None, 404)


def main():
    server = ThreadingHTTPServer((HOST, PORT), CartHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("Open http://127.0.0.1:8000/products")
    print("Press Ctrl+C to stop.")
    print(f"Saving sessions to: {SESSIONS_FILE}")
    server.serve_forever()


if __name__ == "__main__":
    main()

