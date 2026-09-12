names = ["ayzal", "jene", "rose", "diagdigan", "ayzal"]
print(names)

unique_names = set(names)
print(unique_names)

name_count = {}

for name in names:
    if name in name_count:
        name_count[name] = name_count[name] + 1
    else:
        name_count[name] = 1

print(name_count)
