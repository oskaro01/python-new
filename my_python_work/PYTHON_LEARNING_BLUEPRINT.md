# Python Learning Blueprint

This file tracks the journey from "I want to write Python scripts on my own" to strong scripting, practical projects, and DS&A.

Use this as the main checklist. When something feels blurry, revisit the matching file and rerun it.

## Current Status

You are no longer at zero.

You have already written interactive scripts, menu programs, file saving/loading, classes, JSON, a practical personal dictionary app, DS&A basics up to stack, queue, DFS, BFS, linked list basics, recursion basics, sorting basics, practical data filtering/grouping, CSV expense reading, a small expense tracker, and a starter file organizer.

Current phase:

- [x] Python scripting basics
- [x] Interactive scripts
- [x] Lists, loops, functions, classes
- [x] File handling and JSON
- [x] Practical app structure
- [ ] DS&A fundamentals
- [ ] Real-world automation projects
- [ ] Testing and debugging discipline

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
- [ ] Binary search
- [ ] Two pointers
- [ ] Sliding window
- [ ] Heap / priority queue
- [ ] Trees
- [ ] Graphs deeper
- [ ] Trie / autocomplete
- [ ] Fuzzy search deeper
- [ ] Greedy algorithms
- [ ] Dynamic programming basics

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
- [ ] Autocomplete
- [ ] Search by word, meaning, and category
- [ ] Ranking search results
- [x] Folder traversal
- [x] File organizer
- [x] Expense tracker
- [ ] Notes manager

## Phase 6: Practical Projects

Goal: build useful scripts that feel close to real life.

Files:

- `my_python_work/practical_projects/expense_tracker/main.py`
- `my_python_work/practical_projects/expense_tracker/README.md`
- `my_python_work/practical_projects/file_organizer/main.py`
- `my_python_work/practical_projects/file_organizer/organizer.py`
- `my_python_work/practical_projects/file_organizer/config.py`
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

In progress:

- [ ] Add monthly report totals by category
- [ ] Add backup/export all data
- [ ] Test helper functions in a small practice test file

## Learning Queue For Later

These are important, but we are not doing them right now.

Practical queue:

- [ ] Expense tracker monthly category totals
- [ ] Expense tracker backup/export all data
- [x] File organizer undo/log file
- [x] File organizer choose custom folder
- [ ] Personal dictionary autosave
- [ ] Personal dictionary search by meaning/category
- [ ] Notes manager

DS&A queue:

- [ ] Binary search
- [ ] Two pointers
- [ ] Sliding window
- [ ] Heap / priority queue
- [ ] Trees
- [ ] Deeper graphs
- [ ] Trie / autocomplete
- [ ] Fuzzy search deeper
- [ ] Greedy algorithms
- [ ] Dynamic programming basics

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

1. Reopen `my_python_work/practical_projects/expense_tracker/main.py`.
2. Add two expenses manually.
3. Show totals and category totals.
4. Test edit and delete from the menu.
5. Test monthly summary with `YYYY-MM`.
6. Test monthly report export.
7. Reopen `my_python_work/practical_projects/file_organizer/main.py`.
8. Preview the sample folder organization.
9. Test undo after organizing sample files.
10. Try custom-folder preview on a small safe test folder.
11. Add a small practice test file for organizer helper functions.

## Long-Term Mastery Path

Target skill:

You can think of a small problem, choose the right data structure, write the script, save/load data, handle errors, and explain your code.

Long-term checkpoints:

- [ ] Build personal dictionary v2 with autosave
- [ ] Build folder organizer
- [ ] Build expense tracker
- [ ] Build note manager
- [ ] Build search/autocomplete for dictionary
- [ ] Solve 30 beginner DS&A problems
- [ ] Solve 30 intermediate DS&A problems
- [ ] Write tests for one project
- [ ] Refactor one project cleanly

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

That is real progress. The next goal is not speed. The next goal is repetition until these patterns feel natural.
