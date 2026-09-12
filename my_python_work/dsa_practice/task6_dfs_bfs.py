"""
Task 6: DFS and BFS

DFS = Depth First Search
BFS = Breadth First Search

Both are used to explore graphs and trees.

DFS uses a stack.
BFS uses a queue.
"""

from collections import deque


# A graph is a group of connected things.
# This graph uses a dictionary.
#
# Each key is a place.
# Each value is a list of places connected to it.
graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [],
    "E": ["F"],
    "F": [],
}


def dfs(graph, start):
    # DFS goes deep before it goes wide.
    # We use a stack because stack means Last In, First Out.
    visited = set() # this is a set to keep track of visited nodes, ensuring we don't revisit them
    stack = [start] # whats this entity? [] >> a list representing the stack but it doesnt seem empty because it has the start node in it

    while len(stack) > 0: # why less than 0? because we want to keep exploring until there are no more nodes left in the stack
        node = stack.pop() # what we doing here? we are removing the last node from the stack to explore it

        if node in visited: # what is this doing? we are checking if the node has already been visited to avoid cycles and redundant work
            continue

        print(node) # why we printing the node? to show the order in which nodes are visited during the DFS traversal
        visited.add(node) #  what we doing here? we are marking the node as visited by adding it to the visited set

        for neighbor in graph[node]: # neighbor? graph? node? what is happeing here? we are iterating through all the neighbors (connected nodes) of the current node in the graph
            if neighbor not in visited: # we are checking if the neighbor has not been visited yet to decide whether to add it to the stack for future exploration
                stack.append(neighbor) # we are adding the unvisited neighbor to the stack for future exploration
                # is there difference between append and add? yes, append is used for lists to add an element to the end, while add is used for sets to add an element without duplicates
 # what is the goal of dfs? the goal of DFS is to explore as far down a branch of the graph as possible before backtracking, allowing for a deep traversal of the graph structure

def bfs(graph, start):
    # BFS explores level by level.
    # We use a queue because queue means First In, First Out.
    visited = set()
    queue = deque([start])

    while len(queue) > 0:
        node = queue.popleft()

        if node in visited:
            continue

        print(node)
        visited.add(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append(neighbor)


print("=== DFS ===")
dfs(graph, "A")

print("\n=== BFS ===")
bfs(graph, "A")


print("\n=== MINI CHALLENGE ===")

# Your task:
# 1. Add a new node "G" to the graph.
# 2. Connect "F" to "G".
# 3. Run DFS again.
# 4. Run BFS again.
# 5. Notice how the order can be different.
