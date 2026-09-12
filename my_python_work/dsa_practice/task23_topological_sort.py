"""
Task 23: Topological Sort

Topological sort answers:

"What order should I do these tasks in?"

It works on dependencies.

Examples:
- install packages before running tests
- learn variables before functions
- cook rice before serving dinner
- build files before deploying app

Important rule:
Topological sort works on directed graphs with no cycles.
Cycle means:
A needs B, but B also needs A.
That makes the order impossible.
"""

from collections import deque


def topological_sort(dependencies):
    graph = {}
    indegree = {}

    for task, prerequisites in dependencies.items():
        if task not in graph:
            graph[task] = []

        if task not in indegree:
            indegree[task] = 0

        for prerequisite in prerequisites:
            if prerequisite not in graph:
                graph[prerequisite] = []

            if prerequisite not in indegree:
                indegree[prerequisite] = 0

            graph[prerequisite].append(task)
            indegree[task] = indegree[task] + 1

    queue = deque()

    for task, count in indegree.items():
        if count == 0:
            queue.append(task)

    order = []

    while len(queue) > 0:
        current = queue.popleft()
        order.append(current)

        for next_task in graph[current]:
            indegree[next_task] = indegree[next_task] - 1

            if indegree[next_task] == 0:
                queue.append(next_task)

    if len(order) != len(indegree):
        return None

    return order


print("=== LEARNING PLAN ===")

learning_dependencies = {
    "learn variables": [],
    "learn dictionaries": ["learn variables"],
    "learn functions": ["learn variables"],
    "learn JSON": ["learn dictionaries"],
    "learn classes": ["learn functions"],
    "build dictionary app": ["learn classes", "learn JSON"],
}

learning_order = topological_sort(learning_dependencies)

for number, task in enumerate(learning_order, start=1):
    print(f"{number}. {task}")


print("\n=== PROJECT WORKFLOW ===")

project_dependencies = {
    "write code": [],
    "install packages": [],
    "run tests": ["write code", "install packages"],
    "build app": ["run tests"],
    "deploy app": ["build app"],
}

project_order = topological_sort(project_dependencies)

for number, task in enumerate(project_order, start=1):
    print(f"{number}. {task}")


print("\n=== COOKING EXAMPLE ===")

cooking_dependencies = {
    "wash rice": [],
    "cook rice": ["wash rice"],
    "cut vegetables": [],
    "cook curry": ["cut vegetables"],
    "serve dinner": ["cook rice", "cook curry"],
}

print(topological_sort(cooking_dependencies))


print("\n=== CYCLE DETECTION ===")

bad_dependencies = {
    "task A": ["task B"],
    "task B": ["task A"],
}

bad_order = topological_sort(bad_dependencies)

if bad_order is None:
    print("No valid order. There is a cycle.")
else:
    print(bad_order)


print("\n=== PRACTICAL EXAMPLE: FILE IMPORTS ===")

file_dependencies = {
    "main.py": ["dictionary_app.py"],
    "dictionary_app.py": ["file_dialogs.py"],
    "file_dialogs.py": [],
}

print("Files should be understood in this order:")

for filename in topological_sort(file_dependencies):
    print(filename)

"""
It teaches:
- ordering tasks by prerequisites
- learning plans
- project workflows
- cooking steps
- file import order
- cycle detection, where no valid order exists
Practical meaning: topological sort answers “what must happen before what?”

"""

print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Make a dictionary of tasks and prerequisites.
# 2. Use topological_sort() to find the order.
# 3. Make one bad cycle and confirm it returns None.
# 4. Try a school/study plan:
#    quiz depends on reading,
#    reading depends on choosing topic,
#    final review depends on quiz.
