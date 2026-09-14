"""
=============================================
  27 - HEAPS (Priority Queues)
=============================================
  From: quickref.me/python
  Binary heaps for quickly accessing the
  smallest (or largest) element.
=============================================
"""

import heapq

# ===========================================
# What is a Heap?
# ===========================================
# A heap is a binary tree where every parent
# node is <= its children (min-heap).
#
# - heapify(list): O(n) to turn list into heap
# - heappush(heap, item): O(log n)
# - heappop(heap): O(log n) — returns smallest item
# - heap[0]: O(1) — peek at smallest item

# ===========================================
# Creating a Heap
# ===========================================
print("=== CREATING A HEAP ===")

myList = [9, 5, 4, 1, 3, 2]
print(f"Original list: {myList}")

heapq.heapify(myList)  # Turn into a min-heap (in-place)
print(f"After heapify: {myList}")
print(f"Smallest element (heap[0]): {myList[0]}")

# ===========================================
# Push and Pop
# ===========================================
print("\n=== PUSH AND POP ===")

heap = [9, 5, 4, 1, 3, 2]
heapq.heapify(heap)

# Push a new item
heapq.heappush(heap, 10)
print(f"After push(10): {heap}")

# Pop the smallest item
smallest = heapq.heappop(heap)
print(f"Popped smallest: {smallest}")
print(f"After pop: {heap}")

# ===========================================
# Using a Max Heap (by negating values)
# ===========================================
print("\n=== MAX HEAP (VIA NEGATION) ===")

myList = [9, 5, 4, 1, 3, 2]
print(f"Original: {myList}")

# Multiply by -1 to negate all values
myList = [-val for val in myList]
print(f"Negated:  {myList}")

heapq.heapify(myList)
largest = -heapq.heappop(myList)  # Remember to negate back!
print(f"Largest element: {largest}")

# ===========================================
# Practical Example: Task Priority Queue
# ===========================================
print("\n=== PRACTICAL: TASK PRIORITY QUEUE ===")

# Heaps are great for job scheduling!
# Lower priority number = more urgent
tasks = [
    (3, "Check emails"),
    (1, "Fix critical bug!"),    # Most urgent
    (4, "Write documentation"),
    (2, "Review pull request"),   # Second most urgent
]

print("Task queue (priority, task):")
for task in tasks:
    print(f"  Priority {task[0]}: {task[1]}")

# Process tasks in priority order
print("\nProcessing tasks in order:")
while tasks:
    priority, task = heapq.heappop(tasks)
    print(f"  [Priority {priority}] {task}")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a heap from [7, 2, 9, 4, 1, 8]
#   2. Pop the smallest 3 elements
#   3. Use a heap to find the 3 largest numbers in a list
#      (Hint: use negation or heapq.nlargest)
# ===========================================
