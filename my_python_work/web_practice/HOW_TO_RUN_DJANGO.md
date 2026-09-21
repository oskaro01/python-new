# How To Run Django Lessons

Use this helper when you forget the `.venv` and server commands.

## Activate `.venv`

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
```

If it worked, your terminal prompt usually starts with:

```text
(.venv)
```

## Run Django After Activating

```powershell
python my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Stop The Server

Press:

```text
Ctrl+C
```

## Deactivate `.venv`

```powershell
deactivate
```

## Reactivate Later

Run the same activate command again:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Run Without Activating

If activation is annoying, use the `.venv` Python directly:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py runserver
```

## Check Django Without Starting Server

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py check
```

## Common Routes

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/about/
```

## Memory Hook

```text
activate once per terminal
runserver starts Django
Ctrl+C stops Django
deactivate leaves the virtual environment
```

