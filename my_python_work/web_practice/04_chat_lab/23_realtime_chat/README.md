# Chat Lab Lesson 23: Real-Time Chat With Django Channels

The Chat Lab now has a WebSocket path for short text messages. The existing
HTTP composer remains the fallback and still handles image attachments.

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
```

WebSockets keep one connection open instead of opening one request for every
incoming event. They improve instant delivery; they do not replace the database
or permission checks.

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

The web service now starts with an ASGI worker:

```text
gunicorn chat_project.asgi:application -k uvicorn.workers.UvicornWorker
```

Add a Redis-compatible Render Key Value service and set its connection URL as:

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
