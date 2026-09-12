"""
Task 7: Visual DFS and BFS

This file shows DFS and BFS step by step.

Important idea:

DFS uses a stack:
- add with append()
- remove with pop()
- Last In, First Out

BFS uses a queue:
- add with append()
- remove with popleft()
- First In, First Out
"""

from collections import deque


graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [],
    "E": ["F"],
    "F": [],
}


def show_graph(graph):
    print("Graph connections:")

    for node, neighbors in graph.items():
        if len(neighbors) == 0:
            print(f"  {node} -> no neighbors")
        else:
            print(f"  {node} -> {', '.join(neighbors)}")


def show_visited(visited):
    if len(visited) == 0:
        return "{}"

    return "{" + ", ".join(sorted(visited)) + "}"


def visual_dfs(graph, start):
    print("\n=== VISUAL DFS ===")
    print("DFS goes deep first.")
    print("Container type: stack")
    print("Stack removes from the END with pop().")

    visited = set()
    stack = [start]
    step = 1

    while len(stack) > 0:
        print(f"\nStep {step}")
        print(f"  Stack before pop: {stack}")

        node = stack.pop()
        print(f"  Popped node: {node}")

        if node in visited:
            print(f"  {node} was already visited, so skip it.")
            step = step + 1
            continue

        visited.add(node)
        print(f"  Visit: {node}")
        print(f"  Visited now: {show_visited(visited)}")

        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)
                print(f"  Push neighbor onto stack: {neighbor}")

        print(f"  Stack after pushes: {stack}")
        step = step + 1


def visual_bfs(graph, start):
    print("\n=== VISUAL BFS ===")
    print("BFS goes level by level.")
    print("Container type: queue")
    print("Queue removes from the FRONT with popleft().")

    visited = set()
    queue = deque([start])
    step = 1

    while len(queue) > 0:
        print(f"\nStep {step}")
        print(f"  Queue before popleft: {list(queue)}")

        node = queue.popleft()
        print(f"  Removed node: {node}")

        if node in visited:
            print(f"  {node} was already visited, so skip it.")
            step = step + 1
            continue

        visited.add(node)
        print(f"  Visit: {node}")
        print(f"  Visited now: {show_visited(visited)}")

        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append(neighbor)
                print(f"  Add neighbor to queue: {neighbor}")

        print(f"  Queue after adds: {list(queue)}")
        step = step + 1


show_graph(graph)
visual_dfs(graph, "A")
visual_bfs(graph, "A")


print("\n=== WHAT TO NOTICE ===")
print("DFS visits C before B because B and C are pushed, then C is popped first.")
print("BFS visits B before C because B enters the queue first, so B leaves first.")
