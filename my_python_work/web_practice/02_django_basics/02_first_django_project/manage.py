"""Command-line helper for this Django project."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mini_site.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

