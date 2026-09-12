"""
Task 4: Stack and Queue

Stack:
Last In, First Out.
Example: undo button.

Queue:
First In, First Out.
Example: people waiting in line.
"""

from collections import deque


print("=== STACK ===")

# A normal list can work as a stack.
stack = []

# push means add to the top.
stack.append("open browser")
stack.append("type message")
stack.append("send message")

print(stack)

# pop removes the last item.
last_action = stack.pop()
print(f"Undo: {last_action}")
print(stack)


print("\n=== QUEUE ===")

# deque is good for queues.
queue = deque()

# append adds to the back of the queue.
queue.append("Ayzal")
queue.append("Jene")
queue.append("Rose")

print(queue)

# popleft removes from the front of the queue.
next_person = queue.popleft()
print(f"Now serving: {next_person}")
print(queue)


print("\n=== MINI CHALLENGE ===")

# Your task for next time:
# 1. Make a stack called browser_history.
# 2. Add 3 websites.
# 3. Use pop() to go back one page.
# 4. Make a queue called print_queue.
# 5. Add 3 documents.
# 6. Use popleft() to print the first document.
