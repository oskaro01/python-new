"""A small offline addition-practice app built with Python and Tkinter.

Run it with:
    python app.py

Tkinter is part of the standard Python installation on Windows, so this
side quest does not need an internet connection or third-party packages.
"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import random
import time
import tkinter as tk
from tkinter import ttk


QUESTION_COUNT = 10
HISTORY_FILE = Path(__file__).with_name("addition_progress.json")

# Each tuple is (minimum and maximum for the first number,
#                minimum and maximum for the second number).
DIFFICULTY_RANGES = {
    "Easy": ((10, 99), (10, 99)),
    "Medium": ((100, 999), (100, 999)),
    "Hard": ((1_000, 99_999), (1_000, 99_999)),
}


def format_duration(seconds: float) -> str:
    """Turn elapsed seconds into a readable minutes/seconds sentence."""
    total_seconds = max(0, int(round(seconds)))
    minutes, remaining_seconds = divmod(total_seconds, 60)
    minute_word = "minute" if minutes == 1 else "minutes"
    second_word = "second" if remaining_seconds == 1 else "seconds"

    if minutes and remaining_seconds:
        return f"{minutes} {minute_word} {remaining_seconds} {second_word}"
    if minutes:
        return f"{minutes} {minute_word}"
    return f"{remaining_seconds} {second_word}"


def generate_questions(difficulty: str, count: int = QUESTION_COUNT) -> list[dict[str, int]]:
    """Create a fresh list of addition questions for the selected mode."""
    modes = list(DIFFICULTY_RANGES)
    questions: list[dict[str, int]] = []

    for _ in range(count):
        selected_mode = random.choice(modes) if difficulty == "Mixed" else difficulty
        first_range, second_range = DIFFICULTY_RANGES[selected_mode]
        left = random.randint(*first_range)
        right = random.randint(*second_range)
        questions.append({
            "left": left,
            "right": right,
            "answer": left + right,
            "mode": selected_mode,
        })
    return questions


def load_history() -> list[dict]:
    """Read finished rounds from the local progress file, if it exists."""
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        # A missing or damaged history file should never stop practice.
        return []


def save_history(history: list[dict]) -> None:
    """Save only the latest 100 rounds so the file stays small."""
    try:
        HISTORY_FILE.write_text(
            json.dumps(history[-100:], indent=2),
            encoding="utf-8",
        )
    except OSError:
        # The round itself still works if the folder is temporarily read-only.
        pass


class AdditionPracticeApp:
    """The window and the state for one practice session."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Addition Practice")
        self.root.geometry("760x700")
        self.root.minsize(600, 560)
        self.root.configure(bg="#eeeeee")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.questions: list[dict[str, int]] = []
        self.entries: list[ttk.Entry] = []
        self.history = load_history()
        self.started_at = 0.0
        self.timer_job: str | None = None
        self.submitted = False

        self.difficulty_var = tk.StringVar(value="Easy")
        self.timer_var = tk.StringVar(value="Time: 0 seconds")
        self.round_var = tk.StringVar(value="Round 1")
        self.status_var = tk.StringVar(value="Type an answer for each question.")

        self.setup_styles()
        self.build_interface()
        self.start_round()

    def setup_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Page.TFrame", background="#ffffff")
        style.configure("Header.TLabel", background="#ffffff", foreground="#222222", font=("Segoe UI", 16, "bold"))
        style.configure("Muted.TLabel", background="#ffffff", foreground="#555555")
        style.configure("Question.TLabel", background="#ffffff", foreground="#222222", font=("Consolas", 11))

    def build_interface(self) -> None:
        # The page uses ordinary frames and separators to keep the notepad feel.
        page = ttk.Frame(self.root, padding=18, style="Page.TFrame")
        page.pack(fill="both", expand=True, padx=12, pady=12)

        header = ttk.Frame(page, style="Page.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Addition Practice", style="Header.TLabel").pack(side="left")
        ttk.Label(header, textvariable=self.round_var, style="Muted.TLabel").pack(side="right", pady=5)

        controls = ttk.Frame(page, style="Page.TFrame")
        controls.pack(fill="x", pady=(14, 8))
        ttk.Label(controls, text="Difficulty:", style="Muted.TLabel").pack(side="left")
        self.difficulty_box = ttk.Combobox(
            controls,
            textvariable=self.difficulty_var,
            values=("Easy", "Medium", "Hard", "Mixed"),
            state="readonly",
            width=10,
        )
        self.difficulty_box.pack(side="left", padx=(7, 14))
        self.difficulty_box.bind("<<ComboboxSelected>>", lambda _event: self.start_round())
        ttk.Button(controls, text="Refresh round", command=self.start_round).pack(side="left")
        ttk.Label(controls, textvariable=self.timer_var, style="Muted.TLabel").pack(side="right")

        ttk.Separator(page).pack(fill="x", pady=(0, 10))
        ttk.Label(page, text="Answer all ten questions, then press Enter on the last answer.", style="Muted.TLabel").pack(anchor="w")

        self.questions_frame = ttk.Frame(page, style="Page.TFrame")
        self.questions_frame.pack(fill="x", pady=(12, 4))

        actions = ttk.Frame(page, style="Page.TFrame")
        actions.pack(fill="x", pady=(8, 4))
        self.check_button = ttk.Button(actions, text="Check Answers", command=self.check_answers)
        self.check_button.pack(side="left")
        ttk.Label(actions, textvariable=self.status_var, style="Muted.TLabel").pack(side="left", padx=12)

        ttk.Separator(page).pack(fill="x", pady=12)
        ttk.Label(page, text="Results", style="Header.TLabel").pack(anchor="w")
        self.results = tk.Text(
            page,
            height=12,
            wrap="word",
            bg="#fffef5",
            fg="#222222",
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=8,
            font=("Consolas", 10),
        )
        self.results.pack(fill="both", expand=True, pady=(6, 0))
        self.results.configure(state="disabled")

    def start_round(self) -> None:
        """Reset the page, generate ten questions, and start the timer."""
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.questions = generate_questions(self.difficulty_var.get())
        self.entries.clear()
        self.submitted = False
        self.started_at = time.perf_counter()
        self.round_var.set(f"Round {len(self.history) + 1}")
        self.timer_var.set("Time: 0 seconds")
        self.status_var.set("Type an answer for each question.")
        self.check_button.configure(state="normal")
        self.clear_results()
        self.build_question_inputs()
        self.update_timer()

    def build_question_inputs(self) -> None:
        for child in self.questions_frame.winfo_children():
            child.destroy()

        for index, question in enumerate(self.questions):
            row = ttk.Frame(self.questions_frame, style="Page.TFrame")
            row.pack(fill="x", pady=3)
            prompt = f"{index + 1:>2}. {question['left']:,} + {question['right']:,} ="
            ttk.Label(row, text=prompt, width=25, style="Question.TLabel").pack(side="left")
            entry = ttk.Entry(row, width=18, justify="right")
            entry.pack(side="left")
            entry.bind("<Return>", lambda _event, current=index: self.handle_enter(current))
            self.entries.append(entry)

        if self.entries:
            self.entries[0].focus_set()

    def handle_enter(self, index: int) -> str:
        """Move through fields with Enter; submit after the final field."""
        if self.submitted:
            return "break"
        if index < len(self.entries) - 1:
            self.entries[index + 1].focus_set()
            self.entries[index + 1].selection_range(0, tk.END)
        else:
            self.check_answers()
        return "break"

    def update_timer(self) -> None:
        if self.submitted:
            return
        elapsed = time.perf_counter() - self.started_at
        self.timer_var.set(f"Time: {format_duration(elapsed)}")
        self.timer_job = self.root.after(250, self.update_timer)

    def check_answers(self) -> None:
        if self.submitted:
            return

        elapsed = time.perf_counter() - self.started_at
        correct_count = 0
        wrong: list[tuple[int, dict[str, int], str]] = []

        for index, (question, entry) in enumerate(zip(self.questions, self.entries), start=1):
            raw_answer = entry.get().strip()
            try:
                is_correct = raw_answer != "" and int(raw_answer) == question["answer"]
            except ValueError:
                is_correct = False

            if is_correct:
                correct_count += 1
            else:
                wrong.append((index, question, raw_answer or "blank"))

        self.submitted = True
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.timer_var.set(f"Time: {format_duration(elapsed)}")
        self.status_var.set("Round complete. Choose Refresh round to practise again.")
        self.check_button.configure(state="disabled")
        for entry in self.entries:
            entry.configure(state="disabled")

        accuracy = correct_count / QUESTION_COUNT * 100
        self.save_round(correct_count, accuracy, elapsed)
        self.show_results(correct_count, accuracy, elapsed, wrong)

    def save_round(self, correct_count: int, accuracy: float, elapsed: float) -> None:
        self.history.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "difficulty": self.difficulty_var.get(),
            "correct": correct_count,
            "accuracy": round(accuracy, 1),
            "seconds": round(elapsed, 2),
        })
        save_history(self.history)
        self.round_var.set(f"Round {len(self.history)}")

    def show_results(
        self,
        correct_count: int,
        accuracy: float,
        elapsed: float,
        wrong: list[tuple[int, dict[str, int], str]],
    ) -> None:
        lines = [
            f"Score: {correct_count}/{QUESTION_COUNT}",
            f"Accuracy: {accuracy:.0f}%",
            f"Time: {format_duration(elapsed)}",
            "",
        ]
        if wrong:
            lines.append("Review these answers:")
            for index, question, user_answer in wrong:
                lines.append(
                    f"{index:>2}. {question['left']:,} + {question['right']:,} "
                    f"| You: {user_answer} | Correct: {question['answer']:,}"
                )
        else:
            lines.append("Perfect round! Every answer was correct.")

        lines.extend(["", self.progress_summary()])
        self.write_results("\n".join(lines))

    def progress_summary(self) -> str:
        if not self.history:
            return "Progress: no completed rounds yet."
        recent = self.history[-5:]
        average_accuracy = sum(item["accuracy"] for item in recent) / len(recent)
        average_seconds = sum(item["seconds"] for item in recent) / len(recent)
        best_accuracy = max(item["accuracy"] for item in self.history)
        return (
            f"Progress (last {len(recent)} rounds): average accuracy "
            f"{average_accuracy:.0f}%, average time {format_duration(average_seconds)}; "
            f"best accuracy {best_accuracy:.0f}%."
        )

    def clear_results(self) -> None:
        self.write_results("Your score and answer review will appear here after submission.")

    def write_results(self, text: str) -> None:
        self.results.configure(state="normal")
        self.results.delete("1.0", tk.END)
        self.results.insert("1.0", text)
        self.results.configure(state="disabled")

    def close(self) -> None:
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    AdditionPracticeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
