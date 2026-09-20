# Lesson 04: Cookies, Sessions, And A Tiny Cart

This lesson shows how a website remembers a visitor.

It builds a tiny ecommerce-style cart:

```text
Browser stores a session_id cookie.
Python uses that session_id to find the cart on the server.
Cart data is saved in sessions.json.
```

This is still not Django. It is the simple hand-built version so the idea makes sense first.

## Run

From the project root:

```powershell
python -B my_python_work/web_practice/01_web_foundations/04_cookies_sessions_cart/app.py
```

Open:

```text
http://127.0.0.1:8000/products
```

Stop:

```text
Ctrl+C
```

## What This Teaches

- A cookie is small text stored by the browser.
- A session is server-side data connected to that cookie.
- A cart usually belongs to a session or a logged-in user.
- `POST` is used to add/remove/clear cart items.
- Redirect after POST keeps refresh from repeating an action.
- Server-side cart data can survive a restart if saved to JSON.

## Files

- `app.py`
- `sessions.json` is generated when a cart is created.

## Try This

1. Open `/products`.
2. Add a product to cart.
3. Add the same product again.
4. Open `/cart`.
5. Stop the server.
6. Start it again.
7. Refresh `/cart`.

Your cart should still be there because the browser has the cookie and the server has `sessions.json`.

## Key Memory Hook

```text
Cookie = tiny browser memory
Session = server memory connected to the cookie
Cart = data stored in the session
```

