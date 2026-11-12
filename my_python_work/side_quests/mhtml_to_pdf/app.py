"""Desktop and CLI entry point for printing saved MHTML webpages."""

from pathlib import Path
import sys

# Both side quests share the same print engine and desktop controls.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from html_to_pdf.app import main


if __name__ == "__main__":
    raise SystemExit(main(source_format="mhtml"))
