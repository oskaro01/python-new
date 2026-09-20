# Django Basics 01: Setup Django Environment

We finished the tiny pure-Python web foundations.

Now Django begins.

Before building a Django project, we need Django installed in the Python environment we are using.

## Why This Step Matters

In Node/Next.js you used:

```text
npm install
npm run dev
```

In Python/Django the similar idea is:

```text
python -m venv .venv
python -m pip install ...
python manage.py runserver
```

The `.venv` folder keeps project packages separate from your whole computer.

## Check Your Current Setup

From the project root:

```powershell
python -B my_python_work/web_practice/02_django_basics/01_setup_django_environment/check_setup.py
```

If Django is missing, that is okay. Install it with the steps below.

## Create A Virtual Environment

From the project root:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the no-activation commands in the next section.

## Install Django

With activation:

```powershell
python -m pip install --upgrade pip
python -m pip install -r my_python_work/web_practice/02_django_basics/01_setup_django_environment/requirements.txt
python -m django --version
```

Without activation:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r my_python_work/web_practice/02_django_basics/01_setup_django_environment/requirements.txt
.\.venv\Scripts\python.exe -m django --version
```

## Key Memory Hook

```text
requirements.txt = package list
.venv = isolated package folder
django-admin = create Django projects
manage.py = run/manage one Django project
```

## Next Lesson

After Django is installed, we will create the first tiny Django project and run:

```powershell
python manage.py runserver
```

