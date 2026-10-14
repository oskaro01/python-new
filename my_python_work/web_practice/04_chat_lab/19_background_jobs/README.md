# Chat Lab Lesson 19: Background Cleanup And Disappearing Messages

Messages now live for 24 hours by default, including messages sent to yourself.
The timestamp is saved when the message is created; reading it does not reset
the clock. Accounts, friendships, and conversations remain available.

## How expiry works

1. `Message.expires_at` is stored in the database with an index for cleanup.
2. Conversation history and unread counts query only unexpired messages.
3. The private image endpoint checks both message and attachment expiry.
4. A small browser timer removes rendered messages at their deadlines.
5. `run_chat_cleanup` deletes expired messages, attachment rows, and image files.

The worker runs separately from `runserver`, so browser requests never wait for
file deletion. It is a simple periodic process: scheduling and execution share
one process for now. There is no job queue or Redis dependency yet. A later
queue can separate those responsibilities when the app needs more workers.

Rows and files are removed on the next cleanup pass after expiry. If cleanup
is stopped, the server still hides expired messages and denies their image URLs;
physical deletion resumes when cleanup restarts. File removal happens before
database removal so an interrupted job can be retried. Cleanup uses batches of
100 instead of loading all expired messages into memory.

## Extra checkpoint: sending without a page reload

Previously, clicking **Send** submitted the entire form through the browser's
normal navigation flow:

```text
Click Send -> POST to Django -> save -> redirect -> GET the whole conversation
```

That worked, but the browser loaded the page again after every message. Now
JavaScript sends the same HTTP request and updates only the message list:

```text
Click Send
    -> JavaScript collects text, image, and CSRF token
    -> fetch() sends a POST to the same conversation URL
    -> Django validates permissions and saves the message
    -> Django returns JSON containing one rendered message bubble
    -> JavaScript adds the bubble to the existing page
```

### 1. Stop the browser from navigating

In [message_send.js](../chat/static/chat/message_send.js), we listen for the
composer's `submit` event. This happens when the form is submitted:

```javascript
composer.addEventListener("submit", async (event) => {
    event.preventDefault();
    // Send the request ourselves and handle its response.
});
```

`preventDefault()` stops the normal form navigation. It does not save anything;
our JavaScript must send the request. The Send button is disabled while that
request is pending so it cannot be repeatedly clicked.

### 2. Understand async and await

`fetch()` starts a network request and returns a **Promise**, an object
representing a result that will be available later. `async` lets this function
use `await` to wait for that result:

```javascript
const response = await fetch(composer.action || window.location.href, {
    method: "POST",
    body: new FormData(composer),
    headers: { "X-Chat-Async": "1" },
});
const payload = await response.json();
```

The first `await` pauses this function until the response is available. The
second waits for the response body to be read and parsed as JSON. While this
function waits, the browser can still respond to scrolling and other events.
`async` does not create a Python worker or make the Django view asynchronous.

### 3. Send text and images together

`FormData(composer)` collects the form fields, including the selected image
and Django's hidden `csrfmiddlewaretoken` field. The browser supplies the
multipart Content-Type and boundary automatically, so we do not set that header
ourselves. This allows text-only, image-only, and text-plus-image messages to
follow the same validation rules.

The same-origin request also carries the login session cookie. The custom
`X-Chat-Async: 1` header asks Django for a JSON response; it is not a permission
check. The server still checks login, conversation membership, CSRF, and form
validation before saving.

### 4. Django returns a bubble instead of a redirect

In [views.py](../chat/views.py), `conversation_detail()` checks that header.
For a valid asynchronous submission, it saves the message and any attachment,
then renders [_message.html](../chat/templates/chat/_message.html). It returns
a response shaped like this:

```json
{
    "ok": true,
    "html": "<article class=\"message message-own\">...</article>"
}
```

The regular conversation page uses the same small template, so both paths
produce the same bubble design. Django's template escaping also applies to
message text and filenames. A submission without the custom header still uses
the original POST-and-redirect flow, including when JavaScript is unavailable.

### 5. Update the existing page

After Django confirms success, JavaScript:

- removes the initial `No messages yet.` placeholder if present
- inserts the returned bubble into the message list
- scrolls the list to the bottom
- clears the submitted form
- registers the new bubble's expiry timer

We display the saved message after confirmation from Django. If the form is
invalid, Django returns a JSON error with status `400`; JavaScript shows it
beside the composer and keeps the draft. The `finally` block re-enables Send
whether the request succeeds or fails. A network failure can leave the save
outcome uncertain, so this code does not automatically retry the POST.

### How this differs from background jobs and WebSockets

| Mechanism | What it does in this app |
| --- | --- |
| Async form submission | Sends one HTTP request and adds your saved message without page navigation. |
| Background cleanup | A separate Python process periodically deletes expired rows and files. |
| WebSockets, later | A persistent connection lets the server push new-message events to recipients. |

The recipient's open page does not receive new messages automatically yet;
they still need to refresh. This checkpoint improves sending. Lesson 23 adds
live receiving, typing indicators, and the other real-time features.

Memory hook: **send with fetch -> save in Django -> return one bubble -> append
it to the current page**.

Before moving on, explain why `preventDefault()` alone cannot send a message,
what `await` pauses, and why the custom header cannot grant conversation access.

Commit message for this checkpoint: `add async chat composer`.

## One-minute local demonstration

Run these from the repository root. Apply the migration first:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py migrate
```

Existing messages receive 24 hours from their original creation time, so older
ones will become expired after this migration. The 60-second override below
applies to newly sent messages only; it does not rewrite existing deadlines.

In terminal 1, set the short lifetime and start Django:

```powershell
$env:CHAT_MESSAGE_TTL_SECONDS = "60"
.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py runserver 8003
```

In terminal 2 (also at the repository root), start one cleanup process:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py run_chat_cleanup --interval 2
```

Send a new message, optionally with an image. Its bubble disappears after
approximately 60 seconds. With the cleanup process running, its row and image
file are removed on the next pass, normally within about two further seconds
under light local load. Logs report deletion counts; refresh the admin message
list if you want to see that the row has gone. The conversation itself stays.

Expiry is deletion on this app's database and storage. Copies already downloaded
by recipients are outside this lifecycle.

Stop both commands with Ctrl+C. In terminal 1, return to normal mode:

```powershell
Remove-Item Env:CHAT_MESSAGE_TTL_SECONDS -ErrorAction SilentlyContinue
```

The cleanup process is not a permanent system service in this local exercise.
Stop it after the demonstration. Leaving it running is harmless during local
development, but it is unnecessary when you are not testing expiry.

Restart Django for new messages to use the default 86400 seconds (24 hours).
You can also configure `CHAT_MESSAGE_TTL_SECONDS` in the project's `.env`.
Environment variables in the terminal override that file. Changing the setting
affects new messages only. An attachment's seven-day timer from Lesson 18 is
an upper limit: its parent message's earlier expiry always wins.

## Normal cleanup and one-off jobs

For normal operation, leave a separate cleanup process running:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py run_chat_cleanup
```

The default interval is 30 seconds. A scheduler can invoke a single pass instead:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py run_chat_cleanup --once
```

Run one cleanup process locally. If it encounters a storage or database error,
it exits with that error; fix the cause and restart it. A deployment needs a
worker service or scheduler to keep cleanup running while your terminal is closed.

## Why the SQL database stays

Redis can persist data and expire keys, but expiration alone does not replace
our Django account and relationship models. We keep SQLite locally and plan
PostgreSQL for deployment. Redis can later support job queues and Channels.

## Balanced-mode verification

Python compile check only. Migrations, cleanup, and the server are run manually
by you. No runtime verification is claimed for this checkpoint.

Commit message: `add 24-hour messages and background cleanup`

Next: Lesson 20, pagination and message search.
