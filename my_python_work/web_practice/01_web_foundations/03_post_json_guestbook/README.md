# Lesson 03: POST Form And JSON Save

This lesson shows how submitted form data can be saved to a file.

This is not a database yet. It is a stepping stone:

```text
Browser form -> POST request -> Python -> JSON file
```

Later Django will replace this hand-written saving with models and a database.

## Run

From the project root:

```powershell
python -B my_python_work/web_practice/01_web_foundations/03_post_json_guestbook/app.py
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

- `POST` sends form data to the server.
- Python can read form data.
- Python can validate simple input.
- Python can save submitted data to JSON.
- Python can load old data when the server restarts.
- Redirect after POST avoids accidental duplicate submits.
- Escaping user text helps prevent unsafe HTML output.

## Files

- `app.py`
- `messages.json` is generated when you submit messages.

## Try This

1. Submit a message.
2. Stop the server.
3. Start it again.
4. Open the page.

Your message should still be there because it was saved to JSON.

