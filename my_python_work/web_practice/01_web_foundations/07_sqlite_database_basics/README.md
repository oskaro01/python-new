# Lesson 07: SQLite Database Basics

This lesson shows the next step after JSON files:

```text
Browser form -> POST request -> Python -> SQLite database
```

SQLite is a small database built into Python. Django can use SQLite while learning, then PostgreSQL later for serious projects.

## Run

From the project root:

```powershell
python -B my_python_work/web_practice/01_web_foundations/07_sqlite_database_basics/app.py
```

Open:

```text
http://127.0.0.1:8000/products
```

Stop:

```text
Ctrl+C
```

## What This Teaches

- Creating a database table
- Inserting rows
- Selecting rows
- Finding one row by ID
- Deleting rows
- Using SQL parameters safely
- Why databases are better than plain JSON for growing apps

## Files

- `app.py`
- `products.db` is generated when you run the lesson

## Try This

1. Open `/products`.
2. Add a new product.
3. Open that product's detail page.
4. Stop the server.
5. Start it again.
6. Open `/products` again.

Your product should still be there because it was saved in SQLite.

For this beginner version, the price must be a whole number like `25`, not `25.99`.

## Key Memory Hook

```text
JSON file = simple saved data
SQLite database = tables, rows, queries
Django models = Python classes that talk to database tables
```
