# Django Basics 27: Deploying With Render And Neon

This guide explains the complete deployment process for our Personal
Dictionary, from the database to the live website.

## The Big Picture

```text
GitHub  ->  Render web service  ->  Neon PostgreSQL
              runs Django           stores the data
```

Each service has one job:

| Service | Job |
| --- | --- |
| GitHub | Stores our project code |
| Render | Runs the Django website |
| Neon | Stores the online PostgreSQL data |
| Browser | Opens the public Render URL |

Render is the website server. Neon is the database. They are separate on
purpose.

## What We Have

Our project repository is named:

```text
python-new
```

Our Render web service is named:

```text
personal-dictionary
```

The Django project is inside:

```text
my_python_work/web_practice/02_django_basics/02_first_django_project/
```

The deployment files are:

```text
requirements.txt
build.sh
.python-version
render.yaml
```

## Local And Online Databases

When `DATABASE_URL` is missing, Django uses local SQLite:

```text
local computer -> db.sqlite3
```

When `DATABASE_URL` contains the Neon connection string, Django uses Neon:

```text
local command or Render -> Neon PostgreSQL
```

These are two different databases. Words saved locally do not automatically
appear online, and online words do not automatically appear locally.

## Part A: Prepare The Repository

Before deploying, make sure the deployment files are committed and pushed to
the GitHub branch that Render will use.

From the repository root:

```powershell
git status
git add render.yaml my_python_work/web_practice/02_django_basics/27_render_deployment/README.md
git commit -m "prepare Render deployment with Neon PostgreSQL"
git push
```

Never commit:

```text
.env files
Neon connection strings
database passwords
DJANGO_SECRET_KEY values
db.sqlite3
```

## Part B: Create The Neon Database

1. Open the Neon dashboard.
2. Create a project.
3. Keep the `production` branch selected.
4. Click **Connect**.
5. Select **Pooled connection** if Neon shows that option.
6. Copy the complete PostgreSQL connection string.

It normally looks similar to this:

```text
postgresql://username:password@host/database?sslmode=require
```

Your real string contains a real password. Keep it private.

The pooled hostname often contains:

```text
-pooler
```

The pooled connection is useful because it manages database connections for
the web service.

## Part C: Create The Render Web Service

Use a **Blueprint**, because our repository already contains `render.yaml`.

1. Open the Render dashboard.
2. Choose **Blueprints**.
3. Choose **New Blueprint Instance**.
4. Select the GitHub repository `python-new`.
5. Let Render read the root `render.yaml`.
6. Confirm that it will create:

```text
personal-dictionary
```

It should create one web service. It should not create a Render PostgreSQL
database. Neon is our database.

Choose the free web-service plan for learning.

## Part D: Fill In Render Environment Variables

During the first Blueprint setup, Render asks for the variables marked
`sync: false`.

### `DATABASE_URL`

Paste the private connection string copied from Neon.

```text
postgresql://your-private-neon-connection-string
```

Do not paste this value into a code file, commit, screenshot, or chat.

### `DATABASE_CONN_MAX_AGE`

Keep this value at:

```text
0
```

Neon can pause idle compute and close idle SSL connections. A value of `0`
makes Django open a fresh database connection for each request instead of
reusing a stale one. This is a good tradeoff for our small learning app.

### `DJANGO_ALLOWED_HOSTS`

Render gives every web service a free address ending in `onrender.com`.

Use the service address, without `https://`:

```text
personal-dictionary.onrender.com
```

If Render later shows a slightly different address, copy the exact hostname
from the service's **Open** link and update this value.

### `DJANGO_CSRF_TRUSTED_ORIGINS`

Use the same hostname, but include `https://`:

```text
https://personal-dictionary.onrender.com
```

### `DEFAULT_FROM_EMAIL`

This is okay for our first deployment:

```text
webmaster@localhost
```

Password-reset email is not truly configured for production yet. The live
site will need an email provider later.

### Values Created Automatically

Render generates this value:

```text
DJANGO_SECRET_KEY
```

Our Blueprint also sets these production values:

```text
DJANGO_DEBUG=False
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

## Part E: Deploy

After checking the variables, click **Deploy Blueprint**.

Render reads `render.yaml`, enters the Django project folder, and runs the
build command from `build.sh`.

The build does this:

```text
1. Install requirements.txt
2. Collect static files
3. Run database migrations
4. Start Gunicorn
```

The production start command is:

```bash
gunicorn mini_site.wsgi:application
```

Do not use `python manage.py runserver` on Render. That command is for local
learning only.

## Part F: Check The Deployment

Open the URL shown by Render. Then check these pages:

```text
/
/words/
/accounts/login/
/about/
/admin/
```

The admin page should load, but it will reject login until a superuser exists.

Check that:

- the home page loads
- CSS appears
- the words page loads
- registration works
- login works
- the admin page opens
- the database is Neon, not local SQLite

If the free Render service has been sleeping, the first request may take a
little longer while it wakes up.

## Part G: Create A Superuser Without Render Shell

The Render Shell may require a paid plan. We can create the superuser from
our own Windows computer by temporarily pointing one local Django command at
Neon.

This does not change the local database. It connects only to the database
whose URL we provide in the current terminal.

### 1. Open PowerShell At The Repository Root

```powershell
cd C:\Users\ASUS\Desktop\python-new
```

### 2. Install The Project Dependencies If Needed

Run this if a command reports a missing package:

```powershell
.\.venv\Scripts\python.exe -m pip install -r my_python_work\web_practice\02_django_basics\02_first_django_project\requirements.txt
```

### 3. Store The Neon URL Temporarily

This asks for the URL in the terminal and stores it only in the current
PowerShell session:

```powershell
$env:DATABASE_URL = Read-Host "Paste the Neon DATABASE_URL"
```

Paste the Neon string when prompted. Do not include extra quotes.

For this one local management command, keep Django's local-friendly settings:

```powershell
$env:DJANGO_DEBUG = "True"
```

### 4. Confirm The Database Connection

Run:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py showmigrations
```

If the command lists Django migrations, the connection works.

### 5. Apply Migrations If Needed

Render normally runs this during deployment. Running it again is safe and
ensures the Neon database has the current schema:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py migrate
```

### 6. Create The Superuser

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py createsuperuser
```

Enter the username, email, and password when Django asks.

### 7. Remove The Temporary Variables

Do this when finished:

```powershell
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:DJANGO_DEBUG -ErrorAction SilentlyContinue
```

Closing that PowerShell window also removes the temporary variables.

### 8. Log In Online

Open:

```text
https://your-real-render-hostname.onrender.com/admin/
```

Use the superuser details created in the previous step.

## Important Warning About The Superuser Command

The command in Part G changes the Neon database, which is the live database.
Check the following before running it:

- `DATABASE_URL` is the Neon URL.
- The URL is not a local SQLite path.
- The URL belongs to the correct Neon project and `production` branch.
- You are not accidentally using an old database password.

Never share the full URL. If it was accidentally exposed, rotate the Neon
database password.

## Part H: Why The Database Is Not In Render

Render runs the website. Neon stores the data.

This separation means:

```text
Render service restarts -> Neon data remains
Render service sleeps    -> Neon data remains
Render code redeploys    -> Neon data remains
```

The free Render web service can sleep when idle. That affects response time,
not the database contents.

Neon can also pause idle compute. When the next request arrives, it wakes
again. Keep CSV or JSON backups of important dictionary data.

## Part I: Password Reset Email

Locally, password-reset emails print in the terminal because the project uses
Django's console email backend.

That is useful for learning, but it does not deliver real email online.

Before relying on password reset in production, configure an email provider
and add its credentials as Render environment variables. Never put those
credentials in Git.

## Part J: Common Problems

### `ModuleNotFoundError: dj_database_url`

Install the requirements:

```powershell
.\.venv\Scripts\python.exe -m pip install -r my_python_work\web_practice\02_django_basics\02_first_django_project\requirements.txt
```

### `ModuleNotFoundError: psycopg`

The PostgreSQL driver is missing. Run the same requirements command.

### `DisallowedHost`

Set `DJANGO_ALLOWED_HOSTS` to the exact Render hostname, without
`https://`. Save the variable and redeploy.

### `CSRF verification failed`

Set `DJANGO_CSRF_TRUSTED_ORIGINS` to the exact URL with `https://`:

```text
https://your-real-render-hostname.onrender.com
```

### `no such table`

The database migrations did not run against Neon. Read the Render deploy
logs, then run the migration command from Part G with the Neon URL.

### `SSL connection has been closed unexpectedly`

This usually means Django tried to reuse a database connection that Neon
already closed after being idle. Confirm:

```text
DATABASE_CONN_MAX_AGE=0
```

Then redeploy the Render service. Django also enables connection health checks
for the Neon configuration.

### Static CSS is missing

Check the Render deploy logs for `collectstatic`. Confirm that WhiteNoise is
installed from `requirements.txt`, then redeploy.

### Render Shell is unavailable

That is okay. Use Part G. Render Shell is only one way to run a management
command; it is not required.

### The local app shows old data

That is expected if local Django is using SQLite. Local and online databases
are separate.

## Part K: Future Code Changes

After the first deployment:

1. Edit code locally.
2. Run local checks.
3. Commit the change.
4. Push to the connected Git branch.
5. Render builds and deploys the new commit.

Database migrations in `build.sh` run during each deployment.

You do not need to create the superuser again after every code deployment.

## Local Checks

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py check
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py test pages
```

The deployment checklist is:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py check --deploy
```

Local development settings can produce deployment warnings. That is normal
until the production environment supplies its real secret, HTTPS, and domain.

## Deployment Checklist

```text
[ ] Neon project exists
[ ] Neon production branch selected
[ ] Pooled Neon connection copied
[ ] DATABASE_URL entered only in Render
[ ] GitHub contains the latest render.yaml
[ ] Render Blueprint creates personal-dictionary
[ ] No Render PostgreSQL database is being created
[ ] DJANGO_DEBUG is False on Render
[ ] Render hostname is correct
[ ] CSRF trusted origin uses https://
[ ] Deployment logs show successful migrations
[ ] Live home page loads
[ ] CSS loads
[ ] Superuser created against Neon
[ ] /admin/ login works
[ ] Neon data is backed up
```

## Official References

- Render web services: https://render.com/docs/web-services
- Render Blueprint YAML: https://render.com/docs/blueprint-spec
- Render environment variables: https://render.com/docs/configure-environment-variables
- Neon connection pooling: https://neon.com/docs/manage/endpoints/
- Django deployment checklist: https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

## Key Memory Hook

```text
Local SQLite
    -> GitHub
    -> Render runs Django
    -> Neon stores online data
    -> Gunicorn serves the app
    -> HTTPS protects the connection
```

## Next Lesson

Next: production performance and maintenance.
