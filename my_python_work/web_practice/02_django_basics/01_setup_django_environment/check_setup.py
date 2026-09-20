"""
Django Basics 01: Setup Django Environment

This tiny script checks whether Django is installed for the Python you are using.

Run:

    python -B my_python_work/web_practice/02_django_basics/01_setup_django_environment/check_setup.py
"""

import importlib.util
import sys


REQUIREMENTS_FILE = (
    "my_python_work/web_practice/02_django_basics/"
    "01_setup_django_environment/requirements.txt"
)


def package_exists(package_name):
    return importlib.util.find_spec(package_name) is not None


def show_missing_django_help():
    print("Django is not installed for this Python yet.")
    print()
    print("From the project root, create a virtual environment:")
    print()
    print("    python -m venv .venv")
    print()
    print("Then install Django:")
    print()
    print(r"    .\.venv\Scripts\python.exe -m pip install --upgrade pip")
    print(rf"    .\.venv\Scripts\python.exe -m pip install -r {REQUIREMENTS_FILE}")
    print(r"    .\.venv\Scripts\python.exe -m django --version")


def main():
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Python path: {sys.executable}")
    print()

    if not package_exists("django"):
        show_missing_django_help()
        return

    import django

    print(f"Django version: {django.get_version()}")
    print("Django is ready. Next we can create the first Django project.")


if __name__ == "__main__":
    main()

