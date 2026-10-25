# Python Addition Practice App

This is a small offline desktop practice app made with Python's built-in
Tkinter library. It creates ten addition questions, times the page, checks
answers, and shows the questions that need another look.

The `web` folder contains a matching mobile-friendly browser edition. It uses
browser storage on the current device and does not need an account or a
server-side database.

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

## Mobile browser edition

Open `web/index.html` locally for a quick test, or deploy the `web` folder as
a Render **Static Site**. The static site will provide a public URL that can
be opened from a phone, tablet, or computer.

To test it on a phone before deploying, run this from the repository root:

```powershell
py -m http.server 8000 --directory my_python_work/side_quests/addition_practice_app/web --bind 0.0.0.0
```

Keep the computer and phone on the same Wi-Fi network, then open
`http://YOUR-COMPUTER-IP:8000` on the phone. Replace `YOUR-COMPUTER-IP` with
the IPv4 address shown by `ipconfig`.

For Render, create **New > Static Site**, connect the repository, set the root
directory to `my_python_work/side_quests/addition_practice_app/web`, leave the
build command empty, and use `.` as the publish directory. Render will then
give the page its own public `onrender.com` URL.
