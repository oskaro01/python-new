"""Command-line helper for the mini checkout lab."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mini_checkout_lab.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
