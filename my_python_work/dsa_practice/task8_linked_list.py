"""
Task 8: Linked List

A linked list is made of nodes.

Each node stores:
1. a value
2. a link to the next node

Python's normal list is usually better for daily coding.
But linked lists teach an important idea:
objects can point to other objects.
"""


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


def show_chain(head):
    current = head

    while current is not None:
        print(current.value, end=" -> ")
        current = current.next

    print("None")


print("=== MANUAL LINKED LIST ===")

# Create three separate nodes.
first = Node("A")
second = Node("B")
third = Node("C")

# Link them together.
first.next = second
second.next = third

# first is the head, meaning the first node in the chain.
show_chain(first)

print(f"first value: {first.value}")
print(f"first.next value: {first.next.value}")
print(f"first.next.next value: {first.next.next.value}")


print("\n=== LINKED LIST CLASS ===")


class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, value):
        new_node = Node(value)

        if self.head is None:
            self.head = new_node
            return

        current = self.head

        while current.next is not None:
            current = current.next

        current.next = new_node

    def show(self):
        current = self.head

        while current is not None:
            print(current.value, end=" -> ")
            current = current.next

        print("None")

    def contains(self, target):
        current = self.head

        while current is not None:
            if current.value == target:
                return True

            current = current.next

        return False


foods = LinkedList()

foods.append("rice")
foods.append("milk")
foods.append("eggs")

foods.show()

print(foods.contains("milk"))
print(foods.contains("pizza"))


print("\n=== MINI CHALLENGE ===")

# Your task:
# 1. Make a linked list called websites.
# 2. Add 3 websites.
# 3. Show the linked list.
# 4. Check if one website exists with contains().
#
# Do it below this line next time.
