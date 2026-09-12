from pathlib import Path
from tempfile import TemporaryDirectory

from dictionary_app import PersonalDictionaryApp


def make_test_app(autosave_file):
    return PersonalDictionaryApp(autosave_file=autosave_file, load_autosave=False)


def test_optional_meaning_is_allowed():
    with TemporaryDirectory() as temp_text:
        autosave_file = Path(temp_text) / "autosave_dictionary.json"
        app = make_test_app(autosave_file)

        entries = app.clean_entries(
            [
                {
                    "word": "serene",
                    "meaning": "",
                    "example": "",
                    "category": "vocabulary",
                }
            ]
        )

        assert len(entries) == 1
        assert entries[0]["word"] == "serene"
        assert entries[0]["meaning"] == ""


def test_autosave_loads_entries():
    with TemporaryDirectory() as temp_text:
        autosave_file = Path(temp_text) / "autosave_dictionary.json"
        app = make_test_app(autosave_file)
        app.entries.append(app.make_entry("serene", category="vocabulary"))
        app.autosave_dictionary()

        new_app = PersonalDictionaryApp(autosave_file=autosave_file)

        assert len(new_app.entries) == 1
        assert new_app.entries[0]["word"] == "serene"
        assert new_app.entries[0]["meaning"] == ""


def test_search_checks_word_meaning_and_category():
    with TemporaryDirectory() as temp_text:
        autosave_file = Path(temp_text) / "autosave_dictionary.json"
        app = make_test_app(autosave_file)
        app.entries = [
            app.make_entry("serene", "calm and peaceful", category="vocabulary"),
            app.make_entry("python", "programming language", category="coding"),
            app.make_entry("calm", category="mood"),
        ]

        calm_matches = app.search_entries("calm")
        coding_matches = app.search_entries("coding")
        programming_matches = app.search_entries("programming")

        assert calm_matches[0]["word"] == "calm"
        assert coding_matches[0]["word"] == "python"
        assert programming_matches[0]["word"] == "python"


def test_fuzzy_search_finds_close_spelling():
    with TemporaryDirectory() as temp_text:
        autosave_file = Path(temp_text) / "autosave_dictionary.json"
        app = make_test_app(autosave_file)
        app.entries = [app.make_entry("serene", "calm and peaceful")]

        matches = app.search_entries("srene")

        assert len(matches) == 1
        assert matches[0]["word"] == "serene"


def run_test(name, test_function):
    test_function()
    print(f"PASS: {name}")


def run_all_tests():
    run_test("optional_meaning_is_allowed", test_optional_meaning_is_allowed)
    run_test("autosave_loads_entries", test_autosave_loads_entries)
    run_test("search_checks_word_meaning_and_category", test_search_checks_word_meaning_and_category)
    run_test("fuzzy_search_finds_close_spelling", test_fuzzy_search_finds_close_spelling)
    print("All dictionary tests passed.")


if __name__ == "__main__":
    run_all_tests()
