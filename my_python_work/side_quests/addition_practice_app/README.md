# Python Addition Practice App

This is a small offline desktop practice app made with Python's built-in
Tkinter library. It creates ten addition questions, times the page, checks
answers, and shows the questions that need another look.

## Run it

From the repository root, run:

```powershell
python my_python_work/side_quests/addition_practice_app/app.py
```

On Windows, `python` may also be available as `py`:

```powershell
py my_python_work/side_quests/addition_practice_app/app.py
```

Choose **Easy**, **Medium**, **Hard**, or **Mixed**. Press **Enter** to move
from one answer box to the next; pressing Enter in the last box submits the
page. The **Refresh page** button clears the old answers, creates ten new
questions, and starts the timer again.

After a completed page, the app shows the score, accuracy, elapsed time, and
each wrong or blank answer. Finished pages are saved locally in
`addition_progress.json` beside the script, so the results area can show a
small recent progress summary. That file is local practice data and is ignored
by the repository's existing JSON ignore rule.
