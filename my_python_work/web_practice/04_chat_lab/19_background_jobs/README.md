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
