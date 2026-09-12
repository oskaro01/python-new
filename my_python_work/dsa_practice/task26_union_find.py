"""
Task 26: Union-Find

Union-Find is also called Disjoint Set.

It is useful for grouping connected things.

Real examples:
- friend groups
- network components
- duplicate clusters
- connected computers
- accounts that belong to the same person

Two main actions:
- find(x): which group is x in?
- union(a, b): connect the groups of a and b
"""


class UnionFind:
    def __init__(self):
        self.parent = {}
        self.size = {}

    def add(self, item):
        if item not in self.parent:
            self.parent[item] = item
            self.size[item] = 1

    def find(self, item):
        self.add(item)

        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])

        return self.parent[item]

    def union(self, first, second):
        first_root = self.find(first)
        second_root = self.find(second)

        if first_root == second_root:
            return

        if self.size[first_root] < self.size[second_root]:
            first_root, second_root = second_root, first_root

        self.parent[second_root] = first_root
        self.size[first_root] = self.size[first_root] + self.size[second_root]

    def connected(self, first, second):
        return self.find(first) == self.find(second)

    def groups(self):
        grouped_items = {}

        for item in self.parent:
            root = self.find(item)

            if root not in grouped_items:
                grouped_items[root] = []

            grouped_items[root].append(item)

        return list(grouped_items.values())


print("=== FRIEND GROUPS ===")

friends = UnionFind()

friend_connections = [
    ("Ayzal", "Jene"),
    ("Jene", "Rose"),
    ("Mira", "Nora"),
    ("Sam", "Tara"),
]

for first, second in friend_connections:
    friends.union(first, second)

print(f"Ayzal connected to Rose: {friends.connected('Ayzal', 'Rose')}")
print(f"Ayzal connected to Mira: {friends.connected('Ayzal', 'Mira')}")
print(f"Groups: {friends.groups()}")


print("\n=== NETWORK COMPONENTS ===")

network = UnionFind()

connections = [
    ("laptop", "router"),
    ("phone", "router"),
    ("printer", "office_pc"),
]

for first, second in connections:
    network.union(first, second)

print(network.groups())


print("\n=== DUPLICATE CLUSTERS ===")

duplicates = UnionFind()

duplicate_pairs = [
    ("serene", "Serene"),
    ("python", "PYTHON"),
    ("PYTHON", "Python"),
    ("bug", "Bug"),
]

for first, second in duplicate_pairs:
    duplicates.union(first, second)

print(duplicates.groups())


print("\n=== PRACTICAL EXAMPLE: ACCOUNTS ===")

accounts = UnionFind()

same_person_links = [
    ("email:a@example.com", "phone:111"),
    ("phone:111", "username:ayzal"),
    ("email:b@example.com", "phone:222"),
]

for first, second in same_person_links:
    accounts.union(first, second)

for group in accounts.groups():
    print(group)


print("\n=== MINI CHALLENGE ===")

# Your task for later:
# 1. Make a UnionFind object.
# 2. Add connections between classmates or devices.
# 3. Check if two items are connected.
# 4. Print all groups.
# 5. Try adding a connection between two separate groups and print again.
