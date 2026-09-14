"""
OOP 03: Inheritance and Polymorphism

Inheritance:
Child classes reuse code from a parent class.

Polymorphism:
Different classes can have the same method name,
but each class can behave differently.
"""


class Notification:
    def __init__(self, recipient, message):
        self.recipient = recipient
        self.message = message

    def send(self):
        print("Sending a generic notification.")


class EmailNotification(Notification):
    def send(self):
        print(f"Email to {self.recipient}: {self.message}")


class SmsNotification(Notification):
    def send(self):
        print(f"SMS to {self.recipient}: {self.message}")


class AppNotification(Notification):
    def send(self):
        print(f"App alert for {self.recipient}: {self.message}")


def send_all(notifications):
    for notification in notifications:
        # Same method name: send()
        # Different object types: EmailNotification, SmsNotification, AppNotification
        # That is polymorphism.
        notification.send()


def main():
    notifications = [
        EmailNotification("jene@example.com", "Your report is ready."),
        SmsNotification("+880123456789", "Your code ran successfully."),
        AppNotification("Jene", "You learned polymorphism."),
    ]

    print("=== INHERITANCE + POLYMORPHISM ===")
    send_all(notifications)


if __name__ == "__main__":
    main()

