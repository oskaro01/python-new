# Chat Lab: Production Deployment and Operations Flow

Chat Lab has four infrastructure boundaries:

```text
PostgreSQL -> durable users, conversations, messages, and metadata
Redis      -> transient channel-layer events
ASGI       -> HTTP and WebSocket traffic
worker     -> expired-message and attachment cleanup
```

Profile pictures and chat attachments also need private durable storage for a
real production launch.

## Local and production databases

When `DATABASE_URL` is empty, the project uses local `db.sqlite3`. When Render
provides `DATABASE_URL`, `dj-database-url` configures PostgreSQL.

The models and migrations are shared, but the data is separate:

```text
local SQLite      -> local users and messages
Render PostgreSQL -> deployed users and messages
```

Accidentally setting a production URL locally can write into the live database,
so the URL remains private and absent from normal local development.

## Render build and start

The service root is:

```text
my_python_work/web_practice/04_chat_lab
```

`build.sh` runs:

```text
pip install -r requirements.txt
  -> collectstatic --noinput
  -> migrate
```

The start command must be:

```text
gunicorn chat_project.asgi:application -k uvicorn.workers.UvicornWorker
```

The Uvicorn worker matters because `chat_project.asgi` accepts both HTTP and
WebSocket protocols. A WSGI-only command may serve pages while failing socket
upgrades.

Render checks `GET /health/`. That proves the process responds; it does not
prove Redis, private storage, or every database operation is healthy.

## Production environment

Production needs private values such as:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<random secret>
DJANGO_ALLOWED_HOSTS=<chat hostname>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<chat hostname>
DATABASE_URL=<private PostgreSQL URL>
DATABASE_CONN_MAX_AGE=0
REDIS_URL=<private Redis URL>
```

When DEBUG is false, settings reject startup without a secret key. Hostnames
and HTTPS trusted origins are configured separately. Secure redirects and
cookies protect the deployed session.

Sentry uses `SENTRY_DSN` and `SENTRY_ENVIRONMENT`. Secrets never belong in
source, templates, logs, or screenshots.

## Redis and WebSockets

With `REDIS_URL`, Channels uses a shared Redis channel layer:

```text
browser A -> ASGI process 1
browser B -> ASGI process 2
                 |
                 v
          shared Redis events
```

Without Redis, the in-memory layer is useful for one local process only. Redis
does not store the durable chat history. PostgreSQL does. A missed event is
recovered by normal HTTP history and unread queries.

Use Render's internal Redis/Key Value URL for services in the same region and
keep the connection URL private.

## Private media

```text
database -> file reference and metadata
private storage -> image bytes
protected Django view -> authorized stream
```

WhiteNoise serves collected static CSS and JavaScript. It does not make
profile pictures or attachments durable. A normal Render web-service
filesystem can disappear after restart or redeploy.

A real launch needs private object storage or a persistent disk. The storage
adapter must preserve participant checks, expiry checks, and no-store responses.

## Cleanup worker

Expired data becomes inaccessible through database and view filters immediately.
Physical deletion needs a separate process:

```powershell
.\.venv\Scripts\python.exe manage.py run_chat_cleanup --interval 30
```

One cleanup pass is:

```powershell
.\.venv\Scripts\python.exe manage.py run_chat_cleanup --once
```

The cleanup command must not replace the Gunicorn web start command. Run it as
a worker or scheduled job. If it stops, access remains denied but old files
remain until cleanup resumes.

## Verification sequence

Before deployment:

```powershell
.\.venv\Scripts\python.exe manage.py check --deploy
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test chat
```

After deployment, verify:

```text
/health/ returns OK
login/session cookies work over HTTPS
conversation pages load
WebSocket upgrades are accepted
Redis events reach another browser
PostgreSQL rows persist after restart
private media rejects unauthorized users
cleanup deletes expired rows and files
Sentry receives configured test events
```

## Failure diagnosis

```text
build fails              -> dependencies, static collection, or migration
service will not start   -> secret key, settings, or import error
health fails             -> Gunicorn/ASGI process or allowed host
HTTP works, WS 404       -> ASGI worker or WebSocket support
WS connects, no broadcast -> REDIS_URL/channel layer
messages disappear       -> wrong database or missing migration
images disappear         -> ephemeral filesystem/object storage
expiry never cleans      -> cleanup worker/scheduler
errors not visible       -> Sentry or logging configuration
```

## Files involved

- `chat_project/settings.py`: database, Redis, security, static, media, Sentry.
- `chat_project/asgi.py`: HTTP/WebSocket entry point.
- `build.sh`: dependency, static, and migration release steps.
- `requirements.txt`: ASGI, Channels, Redis, PostgreSQL, and deployment packages.
- `chat/storage.py`: private attachment storage.
- `chat/management/commands/run_chat_cleanup.py`: expiry worker.
