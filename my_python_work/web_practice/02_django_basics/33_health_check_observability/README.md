# Django Basics 33: Health Checks And Deployment Observability

The app is live now, so we need a quick answer to:

```text
Is the web process alive, and can it reach the database?
```

This lesson adds a small public health endpoint for Render and simple
production-friendly failure logging.

## The Endpoint

Open this URL locally:

```text
http://127.0.0.1:8000/health/
```

When Django and the database are available, it returns:

```json
{"status": "ok", "database": "ok"}
```

The endpoint runs:

```sql
SELECT 1
```

That is a tiny database query used only to confirm the connection works.

## Why It Is Public

Render needs to reach the endpoint without logging in. The response contains
only a status, never usernames, database URLs, exception details, or secrets.

## Unhealthy Response

If the database query fails, the endpoint returns HTTP `503`:

```json
{"status": "unavailable"}
```

The technical exception is written to the server logs, while the browser gets
the safe response.

```text
200 -> healthy
503 -> service should be investigated
```

## Render Configuration

File:

```text
render.yaml
```

The web service now contains:

```yaml
healthCheckPath: /health/
```

Render requests this path to help decide whether the deployed service is
healthy.

After pushing the change:

1. Wait for Render to finish deploying.
2. Open `https://your-render-url.onrender.com/health/`.
3. Confirm the response is JSON with `"status": "ok"`.
4. Check Render logs for the deployment and request.

## Local Verification

Run Django's checks:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py check
```

Run the project tests:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\02_django_basics\02_first_django_project\manage.py test pages accounts
```

The tests cover both:

```text
database available -> 200
database failure   -> 503
```

## What We Learned

```text
health check       -> small machine-readable status endpoint
503                -> service is temporarily unavailable
observability      -> making failures visible in logs and checks
safe errors        -> log details privately, expose little publicly
```

## Next Lesson

Next: review the complete deployment path and clean up the learning project
before starting the next application phase.
