"""
Task 29: LIS and Graph Patterns

This file covers:

1. Longest Increasing Subsequence (LIS)
2. Shortest path in an unweighted graph
3. Detect cycle in directed graph using 3 colors
4. Number of connected components with Union-Find
"""

from bisect import bisect_left
from collections import deque


def length_of_lis(numbers):
    piles = []

    for number in numbers:
        position = bisect_left(piles, number)

        if position == len(piles):
            piles.append(number)
        else:
            piles[position] = number

    return len(piles)


def shortest_path(graph, start, target):
    queue = deque([start])
    parent = {start: None}

    while len(queue) > 0:
        current = queue.popleft()

        if current == target:
            break

        for neighbor in graph.get(current, []):
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)

    if target not in parent:
        return None

    path = []
    current = target

    while current is not None:
        path.append(current)
        current = parent[current]

    path.reverse()
    return path


def has_cycle_directed(graph):
    white = 0
    gray = 1
    black = 2
    colors = {}

    for node in graph:
        colors[node] = white

    def visit(node):
        colors[node] = gray

        for neighbor in graph.get(node, []):
            if neighbor not in colors:
                colors[neighbor] = white

            if colors[neighbor] == gray:
                return True

            if colors[neighbor] == white and visit(neighbor):
                return True

        colors[node] = black
        return False

    for node in list(colors):
        if colors[node] == white and visit(node):
            return True

    return False


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, item):
        if item not in self.parent:
            self.parent[item] = item

        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])

        return self.parent[item]

    def union(self, first, second):
        first_root = self.find(first)
        second_root = self.find(second)

        if first_root != second_root:
            self.parent[second_root] = first_root


def count_connected_components(nodes, edges):
    union_find = UnionFind()

    for node in nodes:
        union_find.find(node)

    for first, second in edges:
        union_find.union(first, second)

    roots = set()

    for node in nodes:
        roots.add(union_find.find(node))

    return len(roots)


print("=== LONGEST INCREASING SUBSEQUENCE ===")

numbers = [10, 9, 2, 5, 3, 7, 101, 18]
print(length_of_lis(numbers))


print("\n=== SHORTEST PATH IN UNWEIGHTED GRAPH ===")

graph = {
    "Home": ["Market", "School"],
    "Market": ["Home", "Station"],
    "School": ["Home", "Library"],
    "Library": ["School", "Station"],
    "Station": ["Market", "Library", "Office"],
    "Office": ["Station"],
}

print(shortest_path(graph, "Home", "Office"))


print("\n=== DETECT CYCLE IN DIRECTED GRAPH ===")

good_graph = {
    "A": ["B"],
    "B": ["C"],
    "C": [],
}

bad_graph = {
    "A": ["B"],
    "B": ["C"],
    "C": ["A"],
}

print(f"Good graph has cycle: {has_cycle_directed(good_graph)}")
print(f"Bad graph has cycle: {has_cycle_directed(bad_graph)}")


print("\n=== CONNECTED COMPONENTS ===")

nodes = ["A", "B", "C", "D", "E"]
edges = [
    ("A", "B"),
    ("B", "C"),
    ("D", "E"),
]

print(count_connected_components(nodes, edges))


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Try length_of_lis() with [0, 1, 0, 3, 2, 3].
# 2. Make your own graph and find a shortest path.
# 3. Make a directed graph with a cycle.
# 4. Count connected components in your own node/edge list.
