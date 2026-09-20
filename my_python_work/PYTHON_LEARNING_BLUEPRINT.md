# Python Learning Blueprint

This file tracks the journey from "I want to write Python scripts on my own" to strong scripting, practical projects, and DS&A.

Use this as the main checklist. When something feels blurry, revisit the matching file and rerun it.

## Current Status

You are no longer at zero.

You have already written interactive scripts, menu programs, file saving/loading, classes, JSON, a practical personal dictionary app, DS&A basics up to stack, queue, DFS, BFS, linked list basics, recursion basics, sorting basics, practical data filtering/grouping, CSV expense reading, a small expense tracker, and a starter file organizer.

Current phase:

- [x] Python scripting basics
- [x] Interactive scripts
- [x] Lists, loops, functions, class basics
- [x] File handling and JSON
- [x] Practical app structure
- [ ] OOP deep dive
- [ ] DS&A fundamentals
- [ ] Real-world automation projects
- [ ] Testing and debugging discipline
- [ ] Full-stack Python web apps

## Phase 1: Starter Python

Goal: get comfortable writing and running small scripts.

Files:

- `my_python_work/scripts/first_script.py`
- `my_python_work/scripts/second_script.py`
- `my_python_work/scripts/script3.py`

Finished:

- [x] Variables
- [x] `print()`
- [x] `input()`
- [x] f-strings
- [x] `int()` conversion
- [x] `if`, `elif`, `else`
- [x] Lists
- [x] `append()`
- [x] `while True`
- [x] `break`
- [x] `continue`
- [x] `for` loops
- [x] `len()`
- [x] `enumerate()`
- [x] `.strip()`
- [x] `.lower()`
- [x] Duplicate checking with `in`

Key lesson:

Scripts are built from small pieces: ask input, store data, make decisions, loop, and print results.

## Phase 2: Shopping List App

Goal: turn small script knowledge into a real menu program.

Files:

- `my_python_work/scripts/script4.py`
- `my_python_work/scripts/script5.py`
- `my_python_work/shopping_app/main.py`
- `my_python_work/shopping_app/shopping_list_app.py`
- `my_python_work/shopping_app/file_dialogs.py`

Finished:

- [x] Menu-based programs
- [x] Add items
- [x] Show items
- [x] Remove by number
- [x] Edit by number
- [x] Save with Windows file dialog
- [x] Open with Windows file dialog
- [x] Plain text saving
- [x] JSON saving
- [x] JSON loading
- [x] `try` / `except`
- [x] Main guard: `if __name__ == "__main__"`
- [x] Split project into multiple files
- [x] Import from another Python file

Key lesson:

A bigger script should be organized into functions, classes, and files.

## Phase 3: Personal Dictionary App

Goal: build something personally useful instead of only practice examples.

Files:

- `my_python_work/personal_dictionary/main.py`
- `my_python_work/personal_dictionary/dictionary_app.py`
- `my_python_work/personal_dictionary/file_dialogs.py`
- `my_python_work/personal_dictionary/test_dictionary_app.py`

Finished:

- [x] Store entries as dictionaries
- [x] Store many entries in a list
- [x] Add word
- [x] Show all words
- [x] Search word
- [x] Fuzzy search with `difflib`
- [x] Edit word
- [x] Remove word
- [x] Save dictionary as JSON
- [x] Open dictionary from JSON
- [x] Clean loaded data before trusting it
- [x] Beginner comments added for readability
- [x] Make meaning optional
- [x] Autosave after changes
- [x] Search by word, meaning, example, and category
- [x] Rank search results
- [x] Test dictionary helper behavior

Important structure:

```python
{
    "word": "serene",
    "meaning": "calm and peaceful",
    "example": "The lake was serene.",
    "category": "vocabulary",
}
```

Key lesson:

Real programs store structured data. A list of dictionaries is one of the most useful Python patterns.

## Phase 4: Git And Project Hygiene

Goal: keep the project clean before committing.

Files:

- `.gitignore`

Finished:

- [x] Ignore `__pycache__/`
- [x] Ignore `.pyc` files
- [x] Ignore virtual environments
- [x] Ignore local `.env`
- [x] Ignore generated JSON output files

Still to practice:

- [ ] `git status`
- [ ] `git add`
- [ ] `git commit`
- [ ] reading a clean vs dirty working tree

Key lesson:

Do not commit generated Python cache files or personal saved data.

## Phase 4.5: OOP Deep Dive

Goal: properly understand classes before the ultimate review session.

Files:

- `my_python_work/oop_practice/README.md`
- `my_python_work/oop_practice/01_objects_instances.py`
- `my_python_work/oop_practice/02_encapsulation.py`
- `my_python_work/oop_practice/03_inheritance_polymorphism.py`
- `my_python_work/oop_practice/04_abstraction.py`
- `my_python_work/oop_practice/05_composition.py`
- `my_python_work/oop_practice/06_class_static_methods.py`
- `my_python_work/oop_practice/07_oop_checkpoint_project.py`

To learn:

- [ ] Class vs object/instance
- [ ] Attributes
- [ ] Methods
- [ ] `self`
- [ ] Encapsulation
- [ ] `@property`
- [ ] Inheritance
- [ ] Polymorphism
- [ ] Abstraction
- [ ] Composition
- [ ] Class methods
- [ ] Static methods
- [ ] When to use classes
- [ ] When not to use classes

Key lesson:

Classes are useful when data and behavior belong together. OOP is not about making every script complicated; it is about organizing related ideas cleanly.

## Phase 4.6: Practical Design Patterns

Goal: learn common ways to organize growing apps after OOP basics feel comfortable.

Status:

- [ ] Do this after OOP deep dive

Best patterns for our daily Python projects:

- [ ] Repository pattern
- [ ] Strategy pattern
- [ ] Factory pattern
- [ ] Command pattern
- [ ] Adapter pattern

Priority:

1. Repository pattern
2. Strategy pattern

Why these two first:

- Repository is useful because our apps save/load JSON, CSV, and files.
- Strategy is useful because our apps search, filter, sort, and switch behavior.

Example future use:

```text
PersonalDictionary uses DictionaryRepository to save/load words.
PersonalDictionary uses search strategies for exact, fuzzy, and autocomplete search.
```

Key lesson:

Design patterns are reusable organization ideas. They are most useful after classes, objects, composition, and methods make sense.

## Phase 5: DS&A Foundation

Goal: learn the data structures and algorithms that make you stronger at future coding.

Files:

- `my_python_work/dsa_practice/01_list_dict_set.py`
- `my_python_work/dsa_practice/task1.py`
- `my_python_work/dsa_practice/task2.py`
- `my_python_work/dsa_practice/task3_big_o.py`
- `my_python_work/dsa_practice/task4_stack_queue.py`
- `my_python_work/dsa_practice/task5.py`
- `my_python_work/dsa_practice/task6_dfs_bfs.py`
- `my_python_work/dsa_practice/task7_dfs_bfs_visual.py`
- `my_python_work/dsa_practice/task8_linked_list.py`
- `my_python_work/dsa_practice/task9_recursion.py`
- `my_python_work/dsa_practice/task10_sorting.py`
- `my_python_work/dsa_practice/task11_filter_group.py`
- `my_python_work/dsa_practice/task12_csv_expenses.py`
- `my_python_work/dsa_practice/task13_binary_search.py`
- `my_python_work/dsa_practice/task14_two_pointers.py`
- `my_python_work/dsa_practice/task15_sliding_window.py`
- `my_python_work/dsa_practice/task16_heap_priority_queue.py`
- `my_python_work/dsa_practice/task17_trees.py`
- `my_python_work/dsa_practice/task18_graphs_deeper.py`
- `my_python_work/dsa_practice/task19_trie_autocomplete.py`
- `my_python_work/dsa_practice/task20_fuzzy_search_deeper.py`
- `my_python_work/dsa_practice/task21_greedy_algorithms.py`
- `my_python_work/dsa_practice/task22_intervals.py`
- `my_python_work/dsa_practice/task23_topological_sort.py`
- `my_python_work/dsa_practice/task24_dynamic_programming.py`
- `my_python_work/dsa_practice/task25_hashing_deeper.py`
- `my_python_work/dsa_practice/task26_union_find.py`
- `my_python_work/dsa_practice/task27_arrays_strings_patterns.py`
- `my_python_work/dsa_practice/task28_hash_prefix_sliding_patterns.py`
- `my_python_work/dsa_practice/task29_lis_and_graph_patterns.py`
- `my_python_work/dsa_practice/task30_sql_union_vs_union_all.py`
- `my_python_work/dsa_practice/expenses.csv`

Finished:

- [x] List
- [x] Dict
- [x] Set
- [x] Counting with a dictionary
- [x] Reusable function with `return`
- [x] Big O basics
- [x] Why set lookup is fast
- [x] Stack
- [x] Queue
- [x] DFS
- [x] BFS
- [x] Step-by-step DFS/BFS visualization
- [x] Linked list basics
- [x] Recursion basics
- [x] Sorting basics
- [x] Sorting with custom keys
- [x] Filtering lists of dictionaries
- [x] Searching lists of dictionaries
- [x] Grouping data with dictionaries
- [x] Reading CSV files
- [x] Converting CSV text values to numbers
- [x] Summarizing totals by category
- [x] Binary search basics
- [x] Two pointers basics
- [x] Sliding window basics
- [x] Heap / priority queue basics
- [x] Trees basics
- [x] Graphs deeper basics
- [x] Trie / autocomplete basics
- [x] Fuzzy search deeper basics
- [x] Greedy algorithms basics
- [x] Intervals basics
- [x] Topological sort basics
- [x] Dynamic programming basics
- [x] Hashing deeper basics
- [x] Union-Find basics
- [x] Rotate array right by K
- [x] Boyer-Moore majority element
- [x] Longest common prefix
- [x] Product of array except self
- [x] Two Sum with hash map
- [x] Prefix sum + hash map
- [x] Minimum window substring
- [x] Longest subarray with at most K distinct
- [x] Longest Increasing Subsequence
- [x] Directed cycle detection with DFS colors
- [x] Connected components with Union-Find
- [x] SQL UNION vs UNION ALL

In progress:

- [ ] Editing CSV data and rerunning analysis
- [ ] Calculating totals without looking
- [ ] Solving small graph/tree problems without looking

Key lesson:

Stack leads to DFS. Queue leads to BFS. Linked lists teach nodes and references. Recursion teaches a function to solve a smaller version of the same problem. Sorting with `key=` teaches Python how to order complex data. Filtering, grouping, and CSV reading are daily-use scripting patterns.

## Next DS&A Roadmap

Learn in this order:

- [x] Review DFS/BFS with drawings
- [x] Linked list
- [x] Recursion
- [x] Sorting with custom keys
- [x] Binary search
- [x] Two pointers
- [x] Sliding window
- [x] Heap / priority queue
- [x] Trees
- [x] Graphs deeper
- [x] Trie / autocomplete
- [x] Fuzzy search deeper
- [x] Greedy algorithms
- [x] Intervals
- [x] Topological sort
- [x] Dynamic programming basics
- [x] Hashing deeper
- [x] Union-Find

## Practical Algorithms Roadmap

These are useful for daily-life scripts and real apps:

- [x] Counting repeated things
- [x] Duplicate removal
- [x] Fast membership checks
- [x] Fuzzy search suggestions
- [x] Filter records by category or price
- [x] Group records by category
- [x] Read CSV rows into dictionaries
- [x] Summarize expenses by category
- [x] Build a menu-based expense tracker
- [x] Append new rows to CSV
- [x] Autocomplete
- [x] Search by word, meaning, and category
- [x] Ranking search results
- [x] Prefix sum search patterns
- [x] Minimum window substring
- [x] SQL UNION vs UNION ALL
- [x] Folder traversal
- [x] File organizer
- [x] Expense tracker
- [x] Notes manager skipped because it overlaps with the dictionary app

## Phase 6: Practical Projects

Goal: build useful scripts that feel close to real life.

Files:

- `my_python_work/practical_projects/expense_tracker/main.py`
- `my_python_work/practical_projects/expense_tracker/test_expense_tracker.py`
- `my_python_work/practical_projects/expense_tracker/README.md`
- `my_python_work/practical_projects/file_organizer/main.py`
- `my_python_work/practical_projects/file_organizer/organizer.py`
- `my_python_work/practical_projects/file_organizer/config.py`
- `my_python_work/practical_projects/file_organizer/categories.json`
- `my_python_work/practical_projects/file_organizer/test_organizer.py`
- `my_python_work/practical_projects/file_organizer/README.md`

Finished:

- [x] Create CSV data file if missing
- [x] Add expenses from terminal
- [x] Save new expense rows
- [x] Rewrite all CSV rows after editing/deleting
- [x] Add date field
- [x] Validate date input
- [x] Validate month input
- [x] Refactor repeated input checks into helper functions
- [x] Show all expenses
- [x] Show total spent
- [x] Show total by category
- [x] Filter by category
- [x] Sort highest expenses first
- [x] Edit expense
- [x] Delete expense
- [x] Monthly summary
- [x] Nicer table formatting
- [x] Export monthly report
- [x] Add monthly report totals by category
- [x] Add backup/export all data
- [x] Preview file organization plan
- [x] Organize files by extension
- [x] Use `pathlib`
- [x] Move files safely with confirmation
- [x] Log moved files
- [x] Undo last organization
- [x] Preview custom folder safely
- [x] Organize custom folder safely
- [x] Block risky folders
- [x] Refactor file organizer into multiple files
- [x] Write simple tests with `assert`
- [x] Test organizer helper functions
- [x] Test organize and undo with a temporary folder
- [x] Load category rules from JSON
- [x] Show category rules from the menu
- [x] Normalize extensions from category config
- [x] Add recursive folder organizing mode
- [x] Skip already organized category folders in recursive mode
- [x] Avoid duplicate destination names in recursive mode

In progress:

- [ ] Choose review day or next practical upgrade

## Phase 7: Full-Stack Python Web Apps

Goal: rebuild web app confidence with Python as the main world instead of jumping between Python and Next.js/TypeScript.

Main roadmap:

- `my_python_work/PYTHON_FULL_STACK_WEB_ROADMAP.md`

Early starter files:

- `my_python_work/web_practice/README.md`
- `my_python_work/web_practice/01_web_foundations/01_request_response/README.md`
- `my_python_work/web_practice/01_web_foundations/01_request_response/simple_server.py`
- `my_python_work/web_practice/01_web_foundations/02_get_query_products/README.md`
- `my_python_work/web_practice/01_web_foundations/02_get_query_products/app.py`
- `my_python_work/web_practice/01_web_foundations/03_post_json_guestbook/README.md`
- `my_python_work/web_practice/01_web_foundations/03_post_json_guestbook/app.py`
- `my_python_work/web_practice/01_web_foundations/04_cookies_sessions_cart/README.md`
- `my_python_work/web_practice/01_web_foundations/04_cookies_sessions_cart/app.py`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/README.md`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/app.py`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/templates/base.html`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/templates/home.html`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/templates/products.html`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/static/styles.css`

Recommended future stack:

- Django
- PostgreSQL
- Django templates
- HTMX for small interactivity
- Bootstrap first, Tailwind later if wanted
- Django auth
- Stripe first
- PayPal later
- Django email templates
- Django Admin

To learn:

- [ ] Web foundations: HTTP, URLs, GET/POST, forms, cookies, sessions
- [ ] Run a tiny pure-Python web server
- [ ] Practice GET query parameters with product search/filtering
- [ ] Practice POST form saving with JSON
- [ ] Practice cookies, sessions, and a tiny cart
- [ ] Practice templates and static files
- [ ] Django project/app structure
- [ ] URLs, views, templates, redirects, messages
- [ ] Models, migrations, Django ORM, QuerySets
- [ ] PostgreSQL
- [ ] Forms and validation
- [ ] Auth: register, login, logout, permissions
- [ ] Static files and media uploads
- [ ] Product catalog
- [ ] Search, filters, sorting, pagination
- [ ] Cart and checkout flow
- [ ] Orders and order history
- [ ] Inventory basics
- [ ] Reviews
- [ ] Coupons
- [ ] Stripe payments
- [ ] PayPal later
- [ ] Payment webhooks
- [ ] Receipt emails
- [ ] Admin dashboard
- [ ] CSV exports
- [ ] Tests for models, forms, views, cart, checkout
- [ ] Security basics
- [ ] Deployment
- [ ] Performance basics

First future web project:

- [ ] Build `mini_store` without real payments

Second future web project:

- [ ] Build `django_marketplace` with payments, emails, admin analytics, and deployment

Key lesson:

Django lets us build serious full-stack apps while keeping Python as the main language. The browser still uses HTML/CSS/JavaScript, but we do not need to live in a React/Next.js world to build useful ecommerce apps.

## Learning Queue For Later

These are important, but we are not doing them right now.

Practical queue:

- [x] Expense tracker monthly category totals
- [x] Expense tracker backup/export all data
- [x] File organizer undo/log file
- [x] File organizer choose custom folder
- [x] File organizer custom categories from JSON
- [x] File organizer recursive mode
- [x] Personal dictionary autosave
- [x] Personal dictionary search by meaning/category
- [x] Notes manager skipped because it overlaps with the dictionary app
- [ ] Learn Repository pattern after OOP
- [ ] Learn Strategy pattern after Repository
- [ ] Later learn Factory, Command, and Adapter patterns
- [ ] Learn Django after OOP, design patterns, and ultimate review
- [ ] Build Python `mini_store`
- [ ] Build larger Django ecommerce app later

DS&A queue:

- [x] Binary search
- [x] Two pointers
- [x] Sliding window
- [x] Heap / priority queue
- [x] Trees
- [x] Deeper graphs
- [x] Trie / autocomplete
- [x] Fuzzy search deeper
- [x] Greedy algorithms
- [x] Intervals
- [x] Topological sort
- [x] Dynamic programming basics
- [x] Hashing deeper
- [x] Union-Find

## Thinking In Functions And Methods

This is the bridge from beginner to independent coder.

Checklist:

- [x] Write a function
- [x] Pass data into a function
- [x] Return data from a function
- [x] Use methods inside a class
- [ ] Decide when code should become a function
- [ ] Decide what a function should return
- [ ] Keep functions small
- [ ] Avoid depending on outside variables too much

Example idea:

```python
def count_items(items):
    counts = {}

    for item in items:
        if item in counts:
            counts[item] = counts[item] + 1
        else:
            counts[item] = 1

    return counts
```

Key lesson:

A good function should work with the data passed into it.

## Recommended Daily Study Loop

Use this pattern every session:

1. Run the previous file.
2. Explain what it does in your own words.
3. Change one thing.
4. Break it.
5. Fix it.
6. Write a tiny challenge version.
7. Commit when the checkpoint feels complete.

## Next Session Plan

Start here next time:

1. Run `my_python_work/oop_practice/01_objects_instances.py`.
2. Run `my_python_work/oop_practice/02_encapsulation.py`.
3. Run `my_python_work/oop_practice/03_inheritance_polymorphism.py`.
4. Run `my_python_work/oop_practice/04_abstraction.py`.
5. Run `my_python_work/oop_practice/05_composition.py`.
6. Run `my_python_work/oop_practice/06_class_static_methods.py`.
7. Run `my_python_work/oop_practice/07_oop_checkpoint_project.py`.
8. After OOP, do the ultimate review session.

## Long-Term Mastery Path

Target skill:

You can think of a small problem, choose the right data structure, write the script, save/load data, handle errors, and explain your code.

Long-term checkpoints:

- [x] Build personal dictionary v2 with autosave
- [x] Build folder organizer
- [x] Build expense tracker
- [x] Skip note manager because it overlaps with the dictionary app
- [ ] Build autocomplete for dictionary
- [ ] Solve 30 beginner DS&A problems
- [ ] Solve 30 intermediate DS&A problems
- [x] Write tests for one project
- [x] Refactor one project cleanly
- [ ] Learn practical design patterns
- [ ] Learn Django full-stack web development
- [ ] Build and deploy a Python ecommerce app

## Motivation Note

You started by asking to become able to write scripts on your own.

Since then, you have built:

- a personal practice folder
- interactive input scripts
- a menu shopping list app
- a class-based app
- file dialog save/open behavior
- JSON save/load
- a practical personal dictionary app
- a practical expense tracker
- a starter file organizer
- fuzzy search
- DS&A practice files
- stack, queue, DFS, BFS, linked list, recursion, sorting, filtering, grouping, and CSV examples

Future direction:

- OOP deep dive
- Practical design patterns
- Ultimate Python review
- Django full-stack web apps

That is real progress. The next goal is not speed. The next goal is repetition until these patterns feel natural.
