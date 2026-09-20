# Lesson 01: Request And Response

This lesson shows the simplest web idea:

```text
Browser asks for a URL.
Python receives the request.
Python sends back HTML.
Browser shows the page.
```

## Run

From the project root:

```powershell
python -B my_python_work/web_practice/01_web_foundations/01_request_response/simple_server.py
```

Open:

```text
http://127.0.0.1:8000
```

Stop:

```text
Ctrl+C
```

## What This Teaches

- A server waits for browser requests.
- A route is a URL path like `/`, `/about`, or `/form`.
- `GET` usually asks to view/read something.
- `POST` usually submits/changes something.
- Python can send HTML as the response.
- Redirecting after POST helps avoid duplicate form submit on refresh.

## Try This

1. Open `/`.
2. Open `/about`.
3. Open `/form`.
4. Submit one message.
5. Read the terminal logs.

Notice how each browser action becomes a request in the terminal.

