import csv
from datetime import date, datetime
from pathlib import Path


DATA_FILE = Path("my_python_work/practical_projects/expense_tracker/expenses.csv")
REPORTS_DIR = Path("my_python_work/practical_projects/expense_tracker/reports")
FIELDNAMES = ["date", "name", "category", "amount"]
CATEGORY_TOTAL_FIELDNAMES = ["category", "total"]


def ensure_data_file():
    if DATA_FILE.exists():
        return

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()


def read_expenses():
    ensure_data_file()
    expenses = []

    with open(DATA_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            expense = {
                "date": row.get("date") or date.today().isoformat(),
                "name": row["name"],
                "category": row["category"],
                "amount": int(row["amount"]),
            }

            expenses.append(expense)

    return expenses


def save_expense(expense):
    ensure_data_file()

    with open(DATA_FILE, "a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(expense)


def save_all_expenses(expenses):
    ensure_data_file()

    with open(DATA_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(expenses)


def write_expenses_to_csv(filename, expenses):
    filename.parent.mkdir(parents=True, exist_ok=True)

    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(expenses)


def write_category_totals_to_csv(filename, total_by_category):
    filename.parent.mkdir(parents=True, exist_ok=True)

    with open(filename, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CATEGORY_TOTAL_FIELDNAMES)
        writer.writeheader()

        for category in sorted(total_by_category):
            writer.writerow(
                {
                    "category": category,
                    "total": total_by_category[category],
                }
            )


def get_monthly_expenses(expenses, month):
    monthly_expenses = []

    for expense in expenses:
        if expense["date"].startswith(month):
            monthly_expenses.append(expense)

    return monthly_expenses


def calculate_total(expenses):
    total = 0

    for expense in expenses:
        total = total + expense["amount"]

    return total


def calculate_total_by_category(expenses):
    total_by_category = {}

    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]

        if category in total_by_category:
            total_by_category[category] = total_by_category[category] + amount
        else:
            total_by_category[category] = amount

    return total_by_category


def show_category_totals(total_by_category):
    if len(total_by_category) == 0:
        print("No expenses found.")
        return

    for category in sorted(total_by_category):
        total = total_by_category[category]
        print(f"{category}: {total} taka")


def get_expense_table_widths(expenses, numbered=False):
    date_width = len("Date")
    name_width = len("Name")
    category_width = len("Category")
    amount_width = len("Amount")
    number_width = len("No.")

    if numbered:
        number_width = max(number_width, len(str(len(expenses))))

    for expense in expenses:
        date_width = max(date_width, len(expense["date"]))
        name_width = max(name_width, len(expense["name"]))
        category_width = max(category_width, len(expense["category"]))
        amount_width = max(amount_width, len(f"{expense['amount']} taka"))

    return {
        "number": number_width,
        "date": date_width,
        "name": name_width,
        "category": category_width,
        "amount": amount_width,
    }


def show_expense_table(expenses, numbered=False):
    if len(expenses) == 0:
        print("No expenses found.")
        return

    widths = get_expense_table_widths(expenses, numbered)

    if numbered:
        header = (
            f"{'No.':>{widths['number']}}  "
            f"{'Date':<{widths['date']}}  "
            f"{'Name':<{widths['name']}}  "
            f"{'Category':<{widths['category']}}  "
            f"{'Amount':>{widths['amount']}}"
        )
    else:
        header = (
            f"{'Date':<{widths['date']}}  "
            f"{'Name':<{widths['name']}}  "
            f"{'Category':<{widths['category']}}  "
            f"{'Amount':>{widths['amount']}}"
        )

    print(header)
    print("-" * len(header))

    for number, expense in enumerate(expenses, start=1):
        amount = f"{expense['amount']} taka"

        if numbered:
            print(
                f"{number:>{widths['number']}}  "
                f"{expense['date']:<{widths['date']}}  "
                f"{expense['name']:<{widths['name']}}  "
                f"{expense['category']:<{widths['category']}}  "
                f"{amount:>{widths['amount']}}"
            )
        else:
            print(
                f"{expense['date']:<{widths['date']}}  "
                f"{expense['name']:<{widths['name']}}  "
                f"{expense['category']:<{widths['category']}}  "
                f"{amount:>{widths['amount']}}"
            )


def show_expenses(expenses):
    show_expense_table(expenses)


def show_numbered_expenses(expenses):
    show_expense_table(expenses, numbered=True)


def get_expense_index(expenses, action):
    if len(expenses) == 0:
        print("No expenses found.")
        return None

    show_numbered_expenses(expenses)
    number_text = input(f"Enter the number to {action}: ").strip()

    if not number_text.isdigit():
        print("Please enter a valid number.")
        return None

    index = int(number_text) - 1

    if index < 0 or index >= len(expenses):
        print("That expense number does not exist.")
        return None

    return index


def ask_required_text(prompt):
    value = input(prompt).strip()

    if value == "":
        print("This field is required.")
        return None

    return value


def ask_amount(prompt, allow_empty=False):
    amount_text = input(prompt).strip()

    if allow_empty and amount_text == "":
        return ""

    if not amount_text.isdigit():
        print("Please enter a valid number.")
        return None

    return int(amount_text)


def ask_date(prompt, default_today=False, allow_empty=False):
    date_text = input(prompt).strip()

    if default_today and date_text == "":
        return date.today().isoformat()

    if allow_empty and date_text == "":
        return ""

    try:
        parsed_date = datetime.strptime(date_text, "%Y-%m-%d")
        return parsed_date.date().isoformat()
    except ValueError:
        print("Please enter a valid date like 2026-09-12.")
        return None


def ask_month(prompt):
    month_text = input(prompt).strip()

    if month_text == "":
        print("Please enter a month.")
        return None

    try:
        parsed_month = datetime.strptime(month_text, "%Y-%m")
        return parsed_month.strftime("%Y-%m")
    except ValueError:
        print("Please enter a valid month like 2026-09.")
        return None


def add_expense():
    expense_date = ask_date("Date (YYYY-MM-DD, Enter for today): ", default_today=True)

    if expense_date is None:
        return

    name = ask_required_text("Expense name: ")

    if name is None:
        return

    category = ask_required_text("Category: ")

    if category is None:
        return

    amount = ask_amount("Amount: ")

    if amount is None:
        return

    expense = {
        "date": expense_date,
        "name": name,
        "category": category,
        "amount": amount,
    }

    save_expense(expense)
    print("Expense saved.")


def show_all_expenses():
    expenses = read_expenses()
    show_expenses(expenses)


def show_total_spent():
    expenses = read_expenses()
    total = calculate_total(expenses)

    print(f"Total spent: {total} taka")


def show_total_by_category():
    expenses = read_expenses()
    total_by_category = calculate_total_by_category(expenses)
    show_category_totals(total_by_category)


def show_expenses_by_category():
    category = ask_required_text("Category to filter: ")

    if category is None:
        return

    expenses = read_expenses()
    matches = []

    for expense in expenses:
        if expense["category"].lower() == category.lower():
            matches.append(expense)

    show_expenses(matches)


def show_highest_expenses():
    expenses = read_expenses()
    highest_first = sorted(
        expenses,
        key=lambda expense: expense["amount"],
        reverse=True,
    )

    show_expenses(highest_first)


def show_monthly_summary():
    month = ask_month("Month (YYYY-MM): ")

    if month is None:
        return

    expenses = read_expenses()
    monthly_expenses = get_monthly_expenses(expenses, month)

    if len(monthly_expenses) == 0:
        print("No expenses found for that month.")
        return

    print(f"Expenses for {month}:")
    show_expenses(monthly_expenses)

    total = calculate_total(monthly_expenses)
    total_by_category = calculate_total_by_category(monthly_expenses)

    print(f"Monthly total: {total} taka")
    print("Monthly total by category:")
    show_category_totals(total_by_category)


def export_monthly_report():
    month = ask_month("Month to export (YYYY-MM): ")

    if month is None:
        return

    expenses = read_expenses()
    monthly_expenses = get_monthly_expenses(expenses, month)

    if len(monthly_expenses) == 0:
        print("No expenses found for that month.")
        return

    report_file = REPORTS_DIR / f"expenses_{month}.csv"
    category_report_file = REPORTS_DIR / f"expenses_{month}_by_category.csv"
    write_expenses_to_csv(report_file, monthly_expenses)

    total = calculate_total(monthly_expenses)
    total_by_category = calculate_total_by_category(monthly_expenses)
    write_category_totals_to_csv(category_report_file, total_by_category)

    print(f"Exported {len(monthly_expenses)} expenses to {report_file}")
    print(f"Exported category totals to {category_report_file}")
    print(f"Monthly total: {total} taka")


def backup_all_data():
    expenses = read_expenses()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = REPORTS_DIR / f"expenses_backup_{timestamp}.csv"

    write_expenses_to_csv(backup_file, expenses)
    print(f"Backed up {len(expenses)} expenses to {backup_file}")


def edit_expense():
    expenses = read_expenses()
    index = get_expense_index(expenses, "edit")

    if index is None:
        return

    expense = expenses[index]

    print("Press Enter to keep the old value.")
    new_date = ask_date(f"Date [{expense['date']}]: ", allow_empty=True)
    new_name = input(f"Name [{expense['name']}]: ").strip()
    new_category = input(f"Category [{expense['category']}]: ").strip()
    new_amount = ask_amount(f"Amount [{expense['amount']}]: ", allow_empty=True)

    if new_date is None or new_amount is None:
        return

    if new_date != "":
        expense["date"] = new_date

    if new_name != "":
        expense["name"] = new_name

    if new_category != "":
        expense["category"] = new_category

    if new_amount != "":
        expense["amount"] = new_amount

    save_all_expenses(expenses)
    print("Expense updated.")


def delete_expense():
    expenses = read_expenses()
    index = get_expense_index(expenses, "delete")

    if index is None:
        return

    deleted_expense = expenses.pop(index)
    save_all_expenses(expenses)
    print(f"Deleted: {deleted_expense['name']}")


def show_menu():
    print("\nExpense Tracker")
    print("1. Add expense")
    print("2. Show all expenses")
    print("3. Show total spent")
    print("4. Show total by category")
    print("5. Filter by category")
    print("6. Show highest expenses")
    print("7. Edit expense")
    print("8. Delete expense")
    print("9. Monthly summary")
    print("10. Export monthly report")
    print("11. Backup all data")
    print("12. Quit")


def run():
    while True:
        show_menu()
        choice = input("Choose 1-12: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            show_all_expenses()
        elif choice == "3":
            show_total_spent()
        elif choice == "4":
            show_total_by_category()
        elif choice == "5":
            show_expenses_by_category()
        elif choice == "6":
            show_highest_expenses()
        elif choice == "7":
            edit_expense()
        elif choice == "8":
            delete_expense()
        elif choice == "9":
            show_monthly_summary()
        elif choice == "10":
            export_monthly_report()
        elif choice == "11":
            backup_all_data()
        elif choice == "12":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    run()
