# Django Basics 27: Render Deployment Preparation

This lesson prepares the Personal Dictionary for deployment on Render.
Deployment files are ready, but we do not publish the app automatically.

## Why Render?

Render gives this project the pieces Django needs:

```text
Django web service
PostgreSQL database
environment variables
automatic builds from Git
HTTPS
```

Vercel can run Python functions, but Render is a more natural first home for
this full Django project because we need a persistent web service, migrations,
admin, authentication, and PostgreSQL.

## Files Added

### `requirements.txt`

Production packages:

```text
Django
dj-database-url
Gunicorn
psycopg
WhiteNoise
```

### `build.sh`

Render runs this during a deployment:

```text
install packages
collect static files
apply migrations
```

### `.python-version`

Keeps the deployment on Python `3.12.10`, matching our local environment.

### `render.yaml`

Describes the web service and PostgreSQL database. Its `rootDir` points to
the nested Django project folder.

## Local Vs Production

Locally, without `DATABASE_URL`, Django uses:

```text
SQLite -> db.sqlite3
```

On Render, `DATABASE_URL` is provided by the PostgreSQL service, so Django
uses:

```text
PostgreSQL -> Render database
```

Static files use the same idea:

```text
local: Django development static serving
production: collectstatic + WhiteNoise
```

## Deployment Steps

### 1. Commit And Push

Commit these deployment files and push the repository to GitHub.

Do not commit:

- `.env`
- database passwords
- secret keys
- your local `db.sqlite3`

### 2. Create The Render Blueprint

1. Open Render.
2. Choose **New Blueprint Instance**.
3. Connect the GitHub repository.
4. Let Render read the root `render.yaml`.
5. Apply the blueprint.

Render creates the web service and PostgreSQL database described there.

### 3. Set The Two Domain Values

After Render gives the service its `onrender.com` hostname, set:

```text
DJANGO_ALLOWED_HOSTS=your-app.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
```

The `RENDER_EXTERNAL_HOSTNAME` fallback also helps Django recognize the
Render hostname automatically, but explicit values make the configuration
clear.

### 4. Create The First Admin User

After deployment, open the Render Shell and run:

```bash
python manage.py createsuperuser
```

Then open:

```text
https://your-app.onrender.com/admin/
```

### 5. Check The Live App

Verify:

- the home page loads
- CSS appears
- registration works
- login works
- words save to PostgreSQL
- admin opens
- password reset email configuration is set before relying on it

## Production Start Command

Render does not use Django's development server. It runs:

```bash
gunicorn mini_site.wsgi:application
```

`mini_site/wsgi.py` exposes the `application` object Gunicorn needs.

## Important Database Rule

Do not upload the local SQLite database to Render. The local database is
ignored by Git and is only for learning. Render's PostgreSQL database is the
production source of truth.

## Useful Checks

Local checks:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py check
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py test pages
```

Deployment checklist:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py check --deploy
```

Some deployment warnings remain locally until real HTTPS, domain, and secret
values exist.

## Key Memory Hook

```text
Git code -> Render build -> PostgreSQL -> Gunicorn -> HTTPS
```

## Next Lesson

Next: production performance and maintenance.
