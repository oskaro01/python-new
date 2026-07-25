"""
=============================================
  28 - DEQUE (Stacks & Queues)
=============================================
  From: quickref.me/python
  Double-ended queue — fast appends/pops
  from both ends. O(1) for these operations!
=============================================
"""

from collections import deque

# ===========================================
# Creating a Deque
# ===========================================
print("=== CREATING A DEQUE ===")

# Empty deque
q = deque()
print(f"Empty deque: {q}")

# Deque with initial values
q = deque([1, 2, 3])
print(f"Deque from list: {q}")

# ===========================================
# Adding Elements
# ===========================================
print("\n=== ADDING ELEMENTS ===")

q = deque([1, 2, 3])
print(f"Before: {q}")

q.append(4)        # Add to right side
print(f"After append(4) to right: {q}")

q.appendleft(0)    # Add to left side
print(f"After appendleft(0) to left: {q}")

# ===========================================
# Removing Elements
# ===========================================
print("\n=== REMOVING ELEMENTS ===")

q = deque([0, 1, 2, 3, 4])
print(f"Before: {q}")

x = q.pop()        # Remove & return from right
print(f"pop() from right: {x}, remaining: {q}")

y = q.popleft()    # Remove & return from left
print(f"popleft() from left: {y}, remaining: {q}")

# ===========================================
# Rotating
# ===========================================
print("\n=== ROTATING ===")

q = deque([1, 2, 3, 4, 5])
print(f"Before: {q}")

q.rotate(1)  # Rotate 1 step to the right
print(f"After rotate(1) (right): {q}")

q.rotate(-2)  # Rotate 2 steps to the left
print(f"After rotate(-2) (left):  {q}")

# ===========================================
# Using Deque as a Stack (LIFO)
# ===========================================
print("\n=== DEQUE AS STACK (LIFO) ===")
# Stack = Last In, First Out (like a stack of plates)

stack = deque()
stack.append("Page 1")   # Push
stack.append("Page 2")   # Push
stack.append("Page 3")   # Push
print(f"Stack: {stack}")

current = stack.pop()    # Pop
print(f"Current page: '{current}'")
print(f"Stack: {stack}")

current = stack.pop()    # Pop again
print(f"Previous page: '{current}'")

# ===========================================
# Using Deque as a Queue (FIFO)
# ===========================================
print("\n=== DEQUE AS QUEUE (FIFO) ===")
# Queue = First In, First Out (like a line of people)

queue = deque()
queue.append("Customer 1")  # Enqueue
queue.append("Customer 2")  # Enqueue
queue.append("Customer 3")  # Enqueue
print(f"Queue: {queue}")

served = queue.popleft()    # Dequeue (from front)
print(f"Now serving: '{served}'")
print(f"Queue: {queue}")

# ===========================================
# Other Useful Methods
# ===========================================
print("\n=== OTHER METHODS ===")

q = deque(["a", "b", "c", "d", "e"])
print(f"Deque: {q}")
print(f"Count of 'c': {q.count('c')}")
print(f"Index of 'd': {q.index('d')}")

q.reverse()
print(f"Reversed: {q}")

# Max-length deque (drops old items when full)
recent = deque(maxlen=3)
recent.append("msg1")
recent.append("msg2")
recent.append("msg3")
recent.append("msg4")  # 'msg1' is dropped!
print(f"Max-length deque (3): {recent}")

# ===========================================
# 🧪 TRY IT YOURSELF:
#   1. Create a queue of tasks and process them FIFO
#   2. Use a stack to reverse "Hello, World!" (hint: pop each char)
#   3. Use rotate() to make a circular buffer
# ===========================================
