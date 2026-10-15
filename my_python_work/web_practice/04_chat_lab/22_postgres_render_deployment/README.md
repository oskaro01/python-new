# Chat Lab Lesson 22: PostgreSQL And Render Deployment

The Chat Lab is now deployment-ready at the configuration boundary. Local
development still uses SQLite when `DATABASE_URL` is empty. A hosted instance
uses PostgreSQL when Render supplies `DATABASE_URL`.

## What changed

- `dj-database-url` reads a Render/PostgreSQL connection string
- `psycopg` supplies the PostgreSQL driver
- `gunicorn` provides the production WSGI server
- WhiteNoise serves collected static files when `DJANGO_DEBUG=false`
- `DJANGO_SECRET_KEY`, hosts, CSRF origins, and secure cookies are configurable
- `/health/` provides the Render health check endpoint
- `build.sh` collects static files and runs migrations
- `PRIVATE_MEDIA_ROOT` can be configured separately from public media

The database selection is explicit:

```text
DATABASE_URL present -> PostgreSQL
DATABASE_URL empty   -> local SQLite
```

The same Django models and migrations work in either database. PostgreSQL is
the durable production database; it does not replace private file storage.

## Local behavior

Do not add `DATABASE_URL` to your local `.env` unless you intentionally want to
connect this project to a remote database. With no URL, the project keeps using
`db.sqlite3`.

Check production configuration without exposing secrets:

```powershell
if ($env:DATABASE_URL) { "DATABASE_URL is configured" } else { "Using local SQLite" }
```

## Render service values

Create a separate Render Web Service for Chat Lab with this root directory:

```text
my_python_work/web_practice/04_chat_lab
```

Use:

```text
Build command: ./build.sh
Start command: gunicorn chat_project.wsgi:application
Health check: /health/
```

Set these environment variables in Render:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<generated secret>
DJANGO_ALLOWED_HOSTS=<your-chat-hostname>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-chat-hostname>
DATABASE_URL=<PostgreSQL external URL>
DATABASE_CONN_MAX_AGE=0
CHAT_MESSAGE_TTL_SECONDS=86400
CHAT_ATTACHMENT_TTL_DAYS=7
```

Render automatically supplies `RENDER_EXTERNAL_HOSTNAME`; the settings add it
to `ALLOWED_HOSTS` and trust its HTTPS origin. `build.sh` runs `migrate`, so the
database receives migrations during deployment.

## Private image storage warning

Chat attachments are protected files, not public static assets. The local
`private_media/` directory is suitable for learning. A normal Render web
service filesystem is not the durable production home for user uploads, so a
real launch still needs an object-storage adapter for private media, such as an
S3-compatible bucket with signed access. `PRIVATE_MEDIA_ROOT` only selects a
filesystem path; it does not make local disk durable.

This lesson stops at that boundary. Do not deploy real user images until private
durable storage and a backup policy are in place.

## Deployment sequence

```text
push code
    -> Render installs requirements
    -> collectstatic builds staticfiles/
    -> migrate applies 0001 through 0009
    -> Gunicorn starts chat_project.wsgi
    -> Render checks /health/
```

If deployment fails, inspect the first failing stage. A migration error is a
database/configuration issue; a static error is a build/storage issue; a health
failure means the process did not start or the host settings are wrong.

## Balanced-mode verification

This lesson adds configuration and documentation only. Compile check and
`makemigrations --check` are run locally; no Render deployment or remote
database connection is performed automatically.

Commit message: `prepare Chat Lab for PostgreSQL and Render`

Next: Lesson 23, real-time chat with Django Channels and WebSockets.
