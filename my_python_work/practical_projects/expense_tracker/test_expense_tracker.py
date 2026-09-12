from pathlib import Path
from tempfile import TemporaryDirectory

import main as expense_tracker


def sample_expenses():
    return [
        {
            "date": "2026-09-01",
            "name": "Lunch",
            "category": "food",
            "amount": 120,
        },
        {
            "date": "2026-09-02",
            "name": "Bus",
            "category": "transport",
            "amount": 40,
        },
        {
            "date": "2026-09-03",
            "name": "Coffee",
            "category": "food",
            "amount": 80,
        },
    ]


def test_calculate_total_by_category():
    total_by_category = expense_tracker.calculate_total_by_category(sample_expenses())

    assert total_by_category["food"] == 200
    assert total_by_category["transport"] == 40


def test_write_category_totals_to_csv():
    with TemporaryDirectory() as temp_text:
        summary_file = Path(temp_text) / "summary.csv"
        total_by_category = {
            "food": 200,
            "transport": 40,
        }

        expense_tracker.write_category_totals_to_csv(summary_file, total_by_category)
        text = summary_file.read_text(encoding="utf-8")

        assert "category,total" in text
        assert "food,200" in text
        assert "transport,40" in text


def test_backup_all_data():
    with TemporaryDirectory() as temp_text:
        folder = Path(temp_text)
        old_data_file = expense_tracker.DATA_FILE
        old_reports_dir = expense_tracker.REPORTS_DIR
        expense_tracker.DATA_FILE = folder / "expenses.csv"
        expense_tracker.REPORTS_DIR = folder / "reports"

        try:
            expense_tracker.save_all_expenses(sample_expenses())
            expense_tracker.backup_all_data()

            backup_files = list(expense_tracker.REPORTS_DIR.glob("expenses_backup_*.csv"))

            assert len(backup_files) == 1
            text = backup_files[0].read_text(encoding="utf-8")
            assert "Lunch" in text
            assert "Coffee" in text
        finally:
            expense_tracker.DATA_FILE = old_data_file
            expense_tracker.REPORTS_DIR = old_reports_dir


def run_test(name, test_function):
    test_function()
    print(f"PASS: {name}")


def run_all_tests():
    run_test("calculate_total_by_category", test_calculate_total_by_category)
    run_test("write_category_totals_to_csv", test_write_category_totals_to_csv)
    run_test("backup_all_data", test_backup_all_data)
    print("All expense tracker tests passed.")


if __name__ == "__main__":
    run_all_tests()
