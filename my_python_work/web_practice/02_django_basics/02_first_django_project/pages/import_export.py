"""Helpers for moving a user's dictionary data between files and Django."""

import csv
import io
import json
from pathlib import Path

from django.http import HttpResponse


EXPORT_FIELDS = ("word", "meaning", "example", "category")
ALLOWED_EXTENSIONS = {".csv", ".json"}
MAX_FILE_SIZE = 1_000_000
MAX_IMPORT_ROWS = 5_000


def word_rows(words):
    for word in words:
        yield {
            "word": word.word,
            "meaning": word.meaning,
            "example": word.example,
            "category": word.category.name if word.category else "",
        }


def csv_response(words):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="dictionary_words.csv"'

    writer = csv.DictWriter(response, fieldnames=EXPORT_FIELDS)
    writer.writeheader()
    writer.writerows(word_rows(words))
    return response


def json_response(words):
    data = list(word_rows(words))
    response = HttpResponse(
        json.dumps(data, indent=2, ensure_ascii=False),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = 'attachment; filename="dictionary_words.json"'
    return response


def read_import_rows(uploaded_file):
    extension = Path(uploaded_file.name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Choose a .csv or .json file.")

    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValueError("The import file must be smaller than 1 MB.")

    try:
        text = uploaded_file.read().decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("The file must use UTF-8 text encoding.") from error

    if extension == ".csv":
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames or "word" not in reader.fieldnames:
            raise ValueError("CSV files need a 'word' column.")
        rows = list(reader)
    else:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError("The JSON file is not valid.") from error

        if not isinstance(data, list):
            raise ValueError("JSON must contain a list of word objects.")

        if not all(isinstance(row, dict) for row in data):
            raise ValueError("Every JSON item must be an object.")

        rows = data

    if len(rows) > MAX_IMPORT_ROWS:
        raise ValueError(f"Import files cannot contain more than {MAX_IMPORT_ROWS} rows.")

    return rows


def row_text(row, *keys):
    for key in keys:
        value = row.get(key)
        if value is not None:
            return str(value).strip()
    return ""
