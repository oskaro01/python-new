# Web Practice

This folder starts the Python full-stack path.

We are not jumping straight into Django yet. First we learn what Django will later do for us:

- receive a browser request
- choose what page to show
- send back HTML
- handle a form
- read GET and POST data

## Study Order

1. `01_web_foundations/simple_server.py`
2. Later: first Django project

## Run The First Server

```powershell
python -B my_python_work/web_practice/01_web_foundations/simple_server.py
```

Then open:

```text
http://127.0.0.1:8000
```

## What To Notice

- A URL points to a route.
- The browser sends a request.
- Python sends back a response.
- The response can be HTML.
- A form can send data back to Python.
- `GET` usually reads data.
- `POST` usually changes/submits data.

