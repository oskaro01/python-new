"""
Task 18: Graphs Deeper

A graph is data about connections.

Real examples:
- friends connected to friends
- cities connected by roads
- pages linked to pages
- tasks that depend on other tasks
- files that import other files

Graph shape in Python:

graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
}
graphs: routes, friends, dependencies
graph = connections, not order
"""

from collections import deque


def show_connections(graph, node):
    connections = graph.get(node, [])

    if len(connections) == 0:
        print(f"{node} has no connections.")
        return

    print(f"{node} is connected to: {connections}")


def shortest_path(graph, start, target):
    queue = deque()
    queue.append((start, [start]))
    visited = {start}

    while len(queue) > 0:
        current, path = queue.popleft()

        if current == target:
            return path

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None


def reachable_nodes(graph, start):
    queue = deque([start])
    visited = {start}

    while len(queue) > 0:
        current = queue.popleft()

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return visited


def has_connection(graph, start, target):
    path = shortest_path(graph, start, target)
    return path is not None


print("=== FRIEND GRAPH ===")

friend_graph = {
    "Ayzal": ["Jene", "Rose"],
    "Jene": ["Ayzal", "Mira"],
    "Rose": ["Ayzal", "Nora"],
    "Mira": ["Jene", "Nora"],
    "Nora": ["Rose", "Mira"],
}

show_connections(friend_graph, "Ayzal")
print(f"Path from Ayzal to Nora: {shortest_path(friend_graph, 'Ayzal', 'Nora')}")
print(f"Can Ayzal reach Mira? {has_connection(friend_graph, 'Ayzal', 'Mira')}")


print("\n=== ROUTE GRAPH ===")

route_graph = {
    "Home": ["Market", "School"],
    "Market": ["Home", "Station"],
    "School": ["Home", "Library"],
    "Library": ["School", "Station"],
    "Station": ["Market", "Library", "Office"],
    "Office": ["Station"],
}

route = shortest_path(route_graph, "Home", "Office")
print(f"Shortest route from Home to Office: {route}")


print("\n=== REACHABLE NODES ===")

reachable = reachable_nodes(route_graph, "Home")
print(f"Places reachable from Home: {sorted(reachable)}")


print("\n=== DEPENDENCY GRAPH ===")

# This graph means:
# "install packages" must happen before "run tests" and "build app".
dependency_graph = {
    "install packages": ["run tests", "build app"],
    "run tests": ["deploy app"],
    "build app": ["deploy app"],
    "deploy app": [],
}


def dependency_order(graph):
    visited = set()
    order = []

    def visit(node):
        if node in visited:
            return

        visited.add(node)

        for child in graph.get(node, []):
            visit(child)

        order.append(node)

    for node in graph:
        visit(node)

    order.reverse()
    return order


print("Good order:")
print(dependency_order(dependency_graph))


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Make a graph of rooms in a house.
# 2. Use shortest_path() to find a route from bedroom to kitchen.
# 3. Make a graph of tasks that connect to other tasks.
# 4. Use reachable_nodes() to see everything connected to one task.
