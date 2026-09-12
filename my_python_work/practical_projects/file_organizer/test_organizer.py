import json
from pathlib import Path
from tempfile import TemporaryDirectory

import organizer


def make_file(file_path, text="test"):
    # Small helper so each test can create fake files quickly.
    file_path.write_text(text, encoding="utf-8")


def test_get_category():
    # assert means "this must be true". If it is false, Python shows an error.
    assert organizer.get_category(Path("photo.JPG")) == "images"
    assert organizer.get_category(Path("report.pdf")) == "documents"
    assert organizer.get_category(Path("movie.mp4")) == "videos"
    assert organizer.get_category(Path("unknown.something")) == "others"


def test_load_custom_categories():
    with TemporaryDirectory() as temp_text:
        folder = Path(temp_text)
        old_categories_file = organizer.CATEGORIES_FILE
        organizer.CATEGORIES_FILE = folder / "categories.json"

        try:
            custom_categories = {
                "audio": ["mp3", ".wav"],
                "ebooks": [".epub"],
                "../Music Files": [".flac"],
            }

            with open(organizer.CATEGORIES_FILE, "w", encoding="utf-8") as file:
                json.dump(custom_categories, file, indent=4)

            categories = organizer.load_categories()

            assert categories["audio"] == [".mp3", ".wav"]
            assert categories["music_files"] == [".flac"]
            assert organizer.get_category(Path("song.mp3"), categories) == "audio"
            assert organizer.get_category(Path("book.epub"), categories) == "ebooks"
            assert organizer.get_category(Path("album.flac"), categories) == "music_files"
        finally:
            organizer.CATEGORIES_FILE = old_categories_file


def test_get_unique_path():
    # TemporaryDirectory gives us a safe practice folder and deletes it after.
    with TemporaryDirectory() as temp_text:
        folder = Path(temp_text)
        original_file = folder / "report.txt"
        make_file(original_file)

        unique_path = organizer.get_unique_path(original_file)

        assert unique_path == folder / "report_1.txt"


def test_build_plan_ignores_folders():
    with TemporaryDirectory() as temp_text:
        folder = Path(temp_text)
        make_file(folder / "photo.jpg")
        (folder / "old_images").mkdir()

        plan = organizer.build_plan(folder)

        assert len(plan) == 1
        assert plan[0]["category"] == "images"
        assert plan[0]["destination"] == folder / "images" / "photo.jpg"


def test_build_plan_recursive_includes_subfolders():
    with TemporaryDirectory() as temp_text:
        folder = Path(temp_text)
        downloads = folder / "downloads"
        downloads.mkdir()
        make_file(downloads / "photo.jpg")

        plan = organizer.build_plan(folder, recursive=True)

        assert len(plan) == 1
        assert plan[0]["source"] == downloads / "photo.jpg"
        assert plan[0]["destination"] == folder / "images" / "photo.jpg"


def test_build_plan_recursive_skips_category_folders():
    with TemporaryDirectory() as temp_text:
        folder = Path(temp_text)
        images = folder / "images"
        images.mkdir()
        make_file(images / "already_organized.jpg")

        plan = organizer.build_plan(folder, recursive=True)

        assert len(plan) == 0


def test_build_plan_recursive_avoids_duplicate_destinations():
    with TemporaryDirectory() as temp_text:
        folder = Path(temp_text)
        first_folder = folder / "first"
        second_folder = folder / "second"
        first_folder.mkdir()
        second_folder.mkdir()
        make_file(first_folder / "photo.jpg")
        make_file(second_folder / "photo.jpg")

        plan = organizer.build_plan(folder, recursive=True)
        destination_names = sorted(item["destination"].name for item in plan)

        assert destination_names == ["photo.jpg", "photo_1.jpg"]


def test_organize_and_undo():
    with TemporaryDirectory() as temp_text:
        folder = Path(temp_text)

        # Use a temporary log file so the test does not touch the real app log.
        old_log_file = organizer.LOG_FILE
        organizer.LOG_FILE = folder / "last_move_log.json"

        try:
            make_file(folder / "note.txt")
            make_file(folder / "photo.jpg")

            plan = organizer.build_plan(folder)
            organizer.organize_files(plan)

            assert not (folder / "note.txt").exists()
            assert not (folder / "photo.jpg").exists()
            assert (folder / "documents" / "note.txt").exists()
            assert (folder / "images" / "photo.jpg").exists()
            assert organizer.LOG_FILE.exists()

            organizer.undo_last_move()

            assert (folder / "note.txt").exists()
            assert (folder / "photo.jpg").exists()
            assert not organizer.LOG_FILE.exists()
        finally:
            organizer.LOG_FILE = old_log_file


def run_test(name, test_function):
    test_function()
    print(f"PASS: {name}")


def run_all_tests():
    run_test("get_category", test_get_category)
    run_test("load_custom_categories", test_load_custom_categories)
    run_test("get_unique_path", test_get_unique_path)
    run_test("build_plan_ignores_folders", test_build_plan_ignores_folders)
    run_test("build_plan_recursive_includes_subfolders", test_build_plan_recursive_includes_subfolders)
    run_test("build_plan_recursive_skips_category_folders", test_build_plan_recursive_skips_category_folders)
    run_test(
        "build_plan_recursive_avoids_duplicate_destinations",
        test_build_plan_recursive_avoids_duplicate_destinations,
    )
    run_test("organize_and_undo", test_organize_and_undo)
    print("All tests passed.")


if __name__ == "__main__":
    run_all_tests()


# python -B my_python_work/practical_projects/file_organizer/test_organizer.py to make it run without creating .pyc files which are cached compiled versions of the source code.
