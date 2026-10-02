# Django Basics 25: Testing

This lesson adds automated tests for the dictionary's important rules.

## Run The Tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py test pages
```

Django creates a temporary test database, runs the `pages` app tests, and
removes the test database afterward. Your real `db.sqlite3` data is not used or
changed.

The `pages` label matters because the command is being run from the repository
root while the Django project lives inside
`my_python_work/web_practice/02_django_basics/02_first_django_project/`.

## What We Test

### Privacy and CRUD

- Logged-out users are redirected to login.
- A user sees only their own words.
- A user cannot open another user's word.
- A user can create, edit, and delete their own word.
- Search can find a word by meaning.

### Import and Export

- CSV export contains only the current user's words.
- JSON export contains only the current user's words.
- Imported words receive the current user as owner.
- Duplicate words are skipped.

### Permissions

- A user without `view_all_words` receives a 403.
- A group with `view_all_words` can open the staff dashboard.

### Accounts

- The account page requires login.
- Logged-in users can open the password-change form.

## How A Test Works

```python
def test_user_sees_only_their_own_words(self):
    self.login_user()
    response = self.client.get(reverse("pages:word_list"))
    self.assertContains(response, "serene")
    self.assertNotContains(response, "stern")
```

The test creates its own users and words, sends a fake request with Django's
test client, and checks the response. It does not open a real browser.

## Important Test Tools

```text
TestCase       -> isolated test database and cleanup
client         -> fake browser requests
reverse()      -> URL names instead of hardcoded paths
assertContains -> checks rendered response text
assertRedirects -> checks redirects
```

## Key Memory Hook

```text
test setup -> fake request -> assert the rule
```

Tests are not proof that every possible situation works. They are a safety net
for the rules we care about most.

## Files

- `pages/tests.py`: dictionary, import/export, permission, and account tests.

## Next Lesson

Next: security hardening for secrets, uploads, permissions, and production
settings.
