# name = input("what is your name ")
# age = int(input("whats your age "))


# city = input("where do you live ")

name = "sabit"
age = 25
city = "mindanao"

next_year_age = age + 1

print(f"my name is {name}, im {age} years old and i live in {city}")
print(f"and next year i will be {next_year_age}")

if age < 13:
    print("You are a child.")
elif age < 18:
    print("You are a teenager.")
elif age < 60:
    print("You are an adult.")
else:
    print("You are a senior.")


foods = ["rice", "chicken", "pizza", "burger"]

print("My favorite foods:")

for food in foods:
    print(food)


shopping_list = []

item1 = input("Enter first item: ")
item2 = input("Enter second item: ")
item3 = input("Enter third item: ")

shopping_list.append(item1)
shopping_list.append(item2)
shopping_list.append(item3)

print("Your shopping list:")

for item in shopping_list:
    print(f"- {item}")