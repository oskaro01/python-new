# Python Review And Daily Practice Plan

This plan is for reviewing everything learned so far, slowly turning it from "I saw this once" into "I can write this on my own."

Use this together with `PYTHON_LEARNING_BLUEPRINT.md`.

## Main Goal

You are training for practical independence:

- You can open a blank Python file and start.
- You can choose the right data structure.
- You can split code into functions/classes.
- You can save/load data.
- You can debug errors without panicking.
- You can explain what your code is doing.

The goal is not to memorize every line. The goal is to recognize patterns.

## Daily Practice Time

Recommended:

- Light day: 30 minutes
- Normal day: 60 minutes
- Strong day: 90 minutes
- Weekend deep session: 2 to 3 hours

If you are tired, do the light day. Consistency beats one huge study day.

## Daily Practice Loop

Use this loop almost every day:

1. Run one old file.
2. Explain it out loud in simple words.
3. Change one small thing.
4. Break it on purpose.
5. Fix the error.
6. Write one tiny challenge version without looking.
7. Commit when the checkpoint feels clean.

Example:

```powershell
python -B my_python_work/dsa_practice/task28_hash_prefix_sliding_patterns.py
```

Then ask:

- What data structure is used?
- Why is it faster than the simple way?
- What input does the function need?
- What does the function return?
- What edge case can break it?

## Weekly Rhythm

Use this rhythm each week:

- Day 1: review notes and run examples
- Day 2: rewrite 2 to 3 functions from memory
- Day 3: solve tiny practice tasks
- Day 4: connect the pattern to a real project
- Day 5: test/debug/refactor
- Day 6: mixed review
- Day 7: rest or light recap

Do not skip rest. Rest is when the brain quietly organizes the mess.

## 6 Week Review Plan

This is the recommended pace. It is fast enough to feel progress, but slow enough to actually learn.

## Pre-Review Bridge: OOP Deep Dive

Spend: 2 to 4 days before starting the full review

Files:

- `my_python_work/oop_practice/01_objects_instances.py`
- `my_python_work/oop_practice/02_encapsulation.py`
- `my_python_work/oop_practice/03_inheritance_polymorphism.py`
- `my_python_work/oop_practice/04_abstraction.py`
- `my_python_work/oop_practice/05_composition.py`
- `my_python_work/oop_practice/06_class_static_methods.py`
- `my_python_work/oop_practice/07_oop_checkpoint_project.py`

Review:

- Class vs object/instance
- Attributes
- Methods
- `self`
- Encapsulation
- Inheritance
- Polymorphism
- Abstraction
- Composition
- Class methods
- Static methods

Practice:

- Run each file.
- Explain each class in one sentence.
- Explain what data each object stores.
- Rewrite one small class without looking.
- Change the checkpoint project by adding one more task type.

You are ready for the ultimate review when:

- You can explain class vs object.
- You can explain why `self` exists.
- You can explain inheritance vs composition.
- You can recognize when a class makes code clearer.

## Week 1: Python Core And Small Scripts

Spend: 5 to 7 days

Files:

- `my_python_work/scripts/first_script.py`
- `my_python_work/scripts/second_script.py`
- `my_python_work/scripts/script3.py`
- `my_python_work/scripts/script4.py`
- `my_python_work/scripts/script5.py`

Review:

- Variables
- `print()`
- `input()`
- f-strings
- `int()` conversion
- `if`, `elif`, `else`
- `while True`
- `break`
- `continue`
- `for`
- `enumerate()`
- `.strip()`
- `.lower()`

Practice:

- Make a small menu program.
- Ask the user for input.
- Store answers in a list.
- Let the user add, edit, remove, and show items.

You are ready to move on when:

- You can write a simple menu without copying.
- You understand why input is text until you convert it.
- You can use loops without getting lost.

## Week 2: Functions, Classes, Files, JSON

Spend: 5 to 7 days

Files:

- `my_python_work/shopping_app/main.py`
- `my_python_work/shopping_app/shopping_list_app.py`
- `my_python_work/shopping_app/file_dialogs.py`
- `my_python_work/personal_dictionary/main.py`
- `my_python_work/personal_dictionary/dictionary_app.py`
- `my_python_work/personal_dictionary/file_dialogs.py`

Review:

- Functions
- Return values
- Classes
- Methods
- `self`
- OOP deep dive files
- File reading/writing
- JSON saving/loading
- Windows file dialogs
- Main guard
- Imports between files

Practice:

- Take repeated code and turn it into a function.
- Take related data and behavior and put them in a class.
- Save a list of dictionaries to JSON.
- Load JSON and clean the data before trusting it.

You are ready to move on when:

- You can explain why code is split across files.
- You can explain what `self` means.
- You can save and load structured data.

## Week 3: Practical Data Work

Spend: 5 to 7 days

Files:

- `my_python_work/dsa_practice/task11_filter_group.py`
- `my_python_work/dsa_practice/task12_csv_expenses.py`
- `my_python_work/dsa_practice/expenses.csv`
- `my_python_work/practical_projects/expense_tracker/main.py`
- `my_python_work/practical_projects/expense_tracker/test_expense_tracker.py`

Review:

- Lists of dictionaries
- Filtering
- Searching
- Grouping
- Sorting with `key=`
- CSV reading
- CSV writing
- Converting text into numbers
- Monthly summaries
- Exporting reports

Practice:

- Add 10 fake expenses.
- Show total by category.
- Filter one category.
- Sort highest first.
- Export a monthly report.
- Add one test for a helper function.

You are ready to move on when:

- You can read CSV data into dictionaries.
- You can summarize rows by category.
- You can edit/delete data and rewrite the file.

## Week 4: Core DS&A Foundations

Spend: 7 days

Files:

- `my_python_work/dsa_practice/01_list_dict_set.py`
- `my_python_work/dsa_practice/task1.py`
- `my_python_work/dsa_practice/task2.py`
- `my_python_work/dsa_practice/task3_big_o.py`
- `my_python_work/dsa_practice/task4_stack_queue.py`
- `my_python_work/dsa_practice/task5.py`
- `my_python_work/dsa_practice/task8_linked_list.py`
- `my_python_work/dsa_practice/task9_recursion.py`
- `my_python_work/dsa_practice/task10_sorting.py`

Review:

- List
- Dict
- Set
- Big O
- Stack
- Queue
- Linked list
- Recursion
- Sorting

Practice:

- Count repeated words with a dict.
- Remove duplicates with a set.
- Use a stack to reverse something.
- Use a queue to process tasks.
- Write one recursive function.
- Sort records by name, price, or date.

You are ready to move on when:

- You know when to use list vs dict vs set.
- You understand stack means last in, first out.
- You understand queue means first in, first out.
- You can trace a small recursive function.

## Week 5: Practical Algorithm Patterns

Spend: 7 to 10 days

Files:

- `my_python_work/dsa_practice/task13_binary_search.py`
- `my_python_work/dsa_practice/task14_two_pointers.py`
- `my_python_work/dsa_practice/task15_sliding_window.py`
- `my_python_work/dsa_practice/task16_heap_priority_queue.py`
- `my_python_work/dsa_practice/task21_greedy_algorithms.py`
- `my_python_work/dsa_practice/task22_intervals.py`
- `my_python_work/dsa_practice/task25_hashing_deeper.py`
- `my_python_work/dsa_practice/task27_arrays_strings_patterns.py`
- `my_python_work/dsa_practice/task28_hash_prefix_sliding_patterns.py`

Review:

- Binary search
- Two pointers
- Sliding window
- Prefix sum
- Hash map lookup
- Frequency map
- Heap / priority queue
- Greedy choice
- Intervals
- Product except self
- Majority element
- Minimum window substring

Practice:

- Write Two Sum from memory.
- Write longest substring without repeating from memory.
- Write subarray sum equals K from memory.
- Merge overlapping intervals.
- Use a heap to get top 3 items.
- Use binary search on a sorted list.

You are ready to move on when:

- You can recognize "fast lookup" means dict/set.
- You can recognize "continuous part of list/string" often means sliding window or prefix sum.
- You can recognize "sorted data" often means binary search or two pointers.

## Week 6: Graphs, Trees, Trie, DP, SQL, Automation

Spend: 7 to 10 days

Files:

- `my_python_work/dsa_practice/task6_dfs_bfs.py`
- `my_python_work/dsa_practice/task7_dfs_bfs_visual.py`
- `my_python_work/dsa_practice/task17_trees.py`
- `my_python_work/dsa_practice/task18_graphs_deeper.py`
- `my_python_work/dsa_practice/task19_trie_autocomplete.py`
- `my_python_work/dsa_practice/task20_fuzzy_search_deeper.py`
- `my_python_work/dsa_practice/task23_topological_sort.py`
- `my_python_work/dsa_practice/task24_dynamic_programming.py`
- `my_python_work/dsa_practice/task26_union_find.py`
- `my_python_work/dsa_practice/task29_lis_and_graph_patterns.py`
- `my_python_work/dsa_practice/task30_sql_union_vs_union_all.py`
- `my_python_work/practical_projects/file_organizer/main.py`
- `my_python_work/practical_projects/file_organizer/organizer.py`
- `my_python_work/practical_projects/file_organizer/test_organizer.py`

Review:

- DFS
- BFS
- Shortest path
- Directed cycle detection
- Tree traversal
- Trie/autocomplete
- Fuzzy search
- Topological sort
- Dynamic programming basics
- Union-Find
- SQL `UNION`
- SQL `UNION ALL`
- File organization automation

Practice:

- Draw DFS and BFS on paper.
- Find shortest path in a small graph.
- Detect a cycle in a directed graph.
- Add autocomplete to the dictionary app.
- Explain when `UNION ALL` keeps duplicates.
- Run file organizer tests.

You are ready to move on when:

- You can explain DFS vs BFS.
- You can use BFS for shortest path in an unweighted graph.
- You can explain Trie as letter-by-letter search.
- You can explain DP as remembering answers to repeated subproblems.

## Monthly Review Cycle

After the 6 week review, repeat monthly:

Week 1:

- Python basics
- Functions
- Classes
- Files
- JSON

Week 2:

- CSV
- Expense tracker
- Dictionary app
- File organizer
- Tests

Week 3:

- DS&A easy patterns
- List/dict/set
- Stack/queue
- Sorting
- Binary search
- Two pointers
- Sliding window

Week 4:

- DS&A harder patterns
- Graphs
- Trees
- Trie
- DP
- Union-Find
- Mixed problems

## What To Practice Most

These are highest value for real scripting:

- Functions
- Lists of dictionaries
- File reading/writing
- JSON
- CSV
- Dict counting
- Set lookup
- Sorting with `key=`
- Filtering and grouping data
- Error handling
- Testing helper functions

These are highest value for algorithm confidence:

- Big O
- Hash maps
- Prefix sums
- Sliding window
- Two pointers
- Binary search
- BFS
- DFS
- Intervals
- Heap

These are important but can be reviewed more slowly:

- Linked list
- Dynamic programming
- Topological sort
- Union-Find
- Trie internals

## Weekly Checkpoint Questions

At the end of each week, answer these:

1. What did I understand better this week?
2. What still feels blurry?
3. Which file did I rewrite without looking?
4. Which error did I debug?
5. Which pattern did I use in a real project?
6. What should I review first next week?

## Commit Habit

Commit after each clean checkpoint.

Good commit message examples:

```text
Review Python basics and menu scripts
```

```text
Practice CSV summaries and expense helpers
```

```text
Review DSA patterns with hash maps and sliding windows
```

```text
Add autocomplete practice to dictionary app
```

## Red Flag List

Slow down and review when:

- You can run the file but cannot explain it.
- You copied a function but cannot change it.
- You do not know what a function returns.
- You are using global variables because passing data feels confusing.
- You cannot tell why a dict/set is faster than a list search.
- You cannot trace a loop with a few example values.

These are not failures. They are signs pointing to the next review.

## Short Version

If you only remember one thing:

```text
Run it.
Explain it.
Change it.
Break it.
Fix it.
Rewrite a tiny version.
```

That loop is how you become independent.
