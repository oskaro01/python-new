# Chat Lab Lesson 23: Real-Time Chat With Django Channels

The Chat Lab now has a WebSocket path for short text messages. Image bytes still
travel through the validated multipart HTTP upload, then the saved message
metadata is broadcast over the same WebSocket channel so other participants see
the attachment without refreshing.

## Two kinds of delivery

```text
HTTP form + fetch()
    -> save text or image
    -> return one rendered bubble

WebSocket text
    -> consumer validates participant and block rules
    -> save Message
    -> broadcast event to the conversation group
    -> every connected participant appends the bubble

HTTP image upload
    -> validate and store image outside the database
    -> save MessageAttachment
    -> broadcast attachment URL metadata
    -> every connected participant fetches the protected image URL
```

WebSockets keep one connection open instead of opening one request for every
incoming event. They improve instant delivery; they do not replace the database,
file storage, or permission checks. Binary image data stays on the HTTP upload
path; the socket carries only safe metadata and a protected attachment URL.

## The connection path

```text
browser /ws/chat/conversations/12/
    -> ASGI ProtocolTypeRouter
    -> AuthMiddlewareStack
    -> URLRouter
    -> ConversationConsumer
    -> channel layer group: chat_conversation_12
```

`ConversationConsumer.connect()` checks authentication, membership, and both
directions of `UserBlock` before accepting the socket. `receive_json()` validates
the text, creates a durable `Message`, and broadcasts a small JSON event. The
consumer checks access again before writing, because a user could be blocked
after the socket was opened.

## Redis and the local fallback

Settings choose the channel layer from `REDIS_URL`:

```text
REDIS_URL present -> channels_redis RedisChannelLayer
REDIS_URL empty   -> InMemoryChannelLayer
```

The in-memory layer is useful for learning on one local process. It is not a
shared production bus: a second web process would have a separate memory space.
For Render, provide a Redis-compatible Key Value connection URL as `REDIS_URL`
when you want WebSocket broadcasts to work across processes.

Redis carries transient channel events; PostgreSQL continues to store users,
conversations, and messages. A reconnect or missed event is repaired by normal
HTTP history pagination, not by treating Redis as the source of truth.

## Browser behavior

`message_realtime.js` opens:

```text
ws://127.0.0.1:8003/ws/chat/conversations/<id>/
```

or `wss://` on HTTPS. Text-only sends use the socket when it is open. Image
uploads continue through the multipart HTTP endpoint because a file upload needs
the existing attachment validation and private storage path. If the socket is
closed, text falls back to the earlier `fetch()` submission.

On a search or older-history page, a new event is not inserted into the wrong
result set. The page shows a notice and **Latest messages** opens the correct
page. The visible page remains capped at 20 bubbles.

## Install and run locally

Install the new dependencies in the shared virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r my_python_work\web_practice\04_chat_lab\requirements.txt
```

The requirement uses `uvicorn[standard]`, rather than plain `uvicorn`. The
standard extra installs a WebSocket implementation such as `websockets`. Without
it, Uvicorn can serve normal HTTP but reports `No supported WebSocket library
detected`; the browser request then appears as a normal `/ws/...` HTTP request
and Django returns `404`.

    The problem is this warning:
    No supported WebSocket library detected
    Your deployment had plain uvicorn, but WebSockets require an additional protocol library. I updated [requirements.txt](C:/Users/ASUS/Desktop/python-new/my_python_work/web_practice/04_chat_lab/requirements.txt) to:
    uvicorn[standard]>=0.30,<1
    That installs the required WebSocket support. The 404 happened because Uvicorn treated the WebSocket request as normal HTTP.
    Now run locally:
    cd "C:\Users\ASUS\Desktop\python-new\my_python_work\web_practice\04_chat_lab"

    python -m pip install -r requirements.txt
    python manage.py check

Apply the current migrations and start the ASGI development server:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py migrate
.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py runserver 8003
```

With no `REDIS_URL`, the local in-memory channel layer is used. Open the same
conversation in two browser windows, sign in as two participants, and send a
text message. The other window should receive it without a page reload.

For a Redis-backed local run, set `REDIS_URL` to your Redis server connection
string before starting Django. Do not put real Redis credentials in Git.

## Render connection

The web service now starts with an ASGI worker. In the Render web service,
change the previous start command to:

```text
gunicorn chat_project.asgi:application -k uvicorn.workers.UvicornWorker
```

Add a Redis-compatible Render Key Value service and set its connection URL as:

        im in chat-lab > new > key value >

        Create it with:
        - Name: chat-lab
        - Region: the same region as your chat-lab web service
        - Plan: choose the available starter/free option if shown
        - Leave the other settings at their defaults.
        After creation:
        1. Open the new Key Value service.
        2. Click Connect.
        3. Copy the Internal URL, such as:
        redis://red-xxxxxxxx:6379
        4. Return to your chat-lab web service.
        5. Open Environment.
        6. Add:
        REDIS_URL=redis://red-xxxxxxxx:6379
        7. Save and redeploy.
        Use the Internal URL, not the external URL. Then Render will use Redis for the deployed WebSocket channel layer.

```text
REDIS_URL=<private Redis/Key Value connection URL>
```

Do not replace `DATABASE_URL`; the two services have different purposes. Keep
the web service's PostgreSQL database as the durable source of truth. A separate
cleanup worker still needs its own Render process if expired files and rows must
be physically removed automatically.

## Balanced-mode verification

This lesson changes ASGI, dependencies, routing, the consumer, and browser
fallback behavior. Python compile check and migration-state check are run
locally. Install dependencies and perform the two-window WebSocket demonstration
manually; no Redis server is started automatically.

Commit message: `add Channels real-time chat foundation`

The next work can harden reconnect behavior, typing indicators, online status,
and read receipts without changing the durable message model.
