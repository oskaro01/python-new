"""
OOP 07: Checkpoint Project

This small project combines:

- objects
- attributes
- methods
- encapsulation
- composition
- polymorphism

It is a tiny study tracker.
"""


class StudyTask:
    def __init__(self, title, minutes):
        self.title = title
        self.minutes = minutes
        self.completed = False

    def complete(self):
        self.completed = True

    def summary(self):
        status = "done" if self.completed else "not done"
        return f"{self.title} ({self.minutes} min) - {status}"


class CodingTask(StudyTask):
    def __init__(self, title, minutes, file_path):
        super().__init__(title, minutes)
        self.file_path = file_path

    def summary(self):
        status = "done" if self.completed else "not done"
        return f"{self.title} in {self.file_path} ({self.minutes} min) - {status}"


class StudyPlan:
    def __init__(self, name):
        self.name = name
        self._tasks = []

    def add_task(self, task):
        self._tasks.append(task)

    def total_minutes(self):
        total = 0

        for task in self._tasks:
            total += task.minutes

        return total

    def show(self):
        print(f"Study plan: {self.name}")
        print(f"Total minutes: {self.total_minutes()}")

        for task in self._tasks:
            # Polymorphism:
            # StudyTask and CodingTask both have summary().
            print(f"- {task.summary()}")


def main():
    plan = StudyPlan("OOP Review")

    read_task = StudyTask("Read objects and instances", 20)
    code_task = CodingTask(
        "Practice composition",
        30,
        "my_python_work/oop_practice/05_composition.py",
    )

    code_task.complete()

    plan.add_task(read_task)
    plan.add_task(code_task)

    print("=== OOP CHECKPOINT PROJECT ===")
    plan.show()


if __name__ == "__main__":
    main()

