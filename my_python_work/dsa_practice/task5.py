from collections import deque


print("=== STACK: Browser History ===")

# A stack is Last In, First Out.
# The last website we visited is the first one we leave when we go back.
browser_history = []

browser_history.append("https://www.google.com")
browser_history.append("https://www.github.com")
browser_history.append("https://www.stackoverflow.com")

print(f"Browser history: {browser_history}")
print(f"Current page: {browser_history[-1]}")

# pop() removes the last website.
# In browser language, this is the page we are leaving.
closed_website = browser_history.pop()

print(f"Leaving: {closed_website}")
print(f"Back to: {browser_history[-1]}") # means “the new last item,” which is now the page you went back to.
print(f"Browser history now: {browser_history}")


print("\n=== QUEUE: Print Queue ===")

# A queue is First In, First Out.
# The first document added is the first document printed.
print_queue = deque()

print_queue.append("document1.pdf")
print_queue.append("document2.pdf")
print_queue.append("document3.pdf")

print(f"Print queue: {print_queue}")

# popleft() removes from the front of the queue.
first_document = print_queue.popleft()

print(f"Printing: {first_document}")
print(f"Print queue now: {print_queue}")
