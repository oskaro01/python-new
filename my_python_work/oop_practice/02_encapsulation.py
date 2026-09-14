"""
OOP 02: Encapsulation

Encapsulation means:

- keep data inside the object
- change that data through methods
- prevent random outside code from making the object invalid

In Python, a single underscore like _balance means:
"Please treat this as internal/private."
"""


class BankAccount:
    def __init__(self, owner, starting_balance=0):
        self.owner = owner
        self._balance = starting_balance

    @property
    def balance(self):
        # Outside code can read the balance.
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            print("Deposit amount must be positive.")
            return

        self._balance += amount
        print(f"Deposited {amount}. New balance: {self._balance}")

    def withdraw(self, amount):
        if amount <= 0:
            print("Withdraw amount must be positive.")
            return

        if amount > self._balance:
            print("Not enough money.")
            return

        self._balance -= amount
        print(f"Withdrew {amount}. New balance: {self._balance}")


def main():
    account = BankAccount("Jene", 100)

    print("=== ENCAPSULATION ===")
    print(account.owner)
    print(account.balance)

    account.deposit(50)
    account.withdraw(30)
    account.withdraw(999)

    print("\nThe balance is controlled by methods.")


if __name__ == "__main__":
    main()

