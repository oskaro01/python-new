# Chat Lab Lesson 18: Attachment Expiry

Lesson 17 made attachments private. Lesson 18 gives them a lifetime so old
files do not remain available forever.

Each `MessageAttachment` receives an `expires_at` timestamp when it is created.
The default lifetime is seven days and can be changed with:

```text
CHAT_ATTACHMENT_TTL_DAYS=7
```

The protected preview/download view filters with `expires_at > now`. An expired
attachment therefore returns `404` even if the conversation participant still
knows its ID. The conversation template shows `Image expired.` instead of a
broken preview.

Physical cleanup is handled by an idempotent management command:

```powershell
..\..\..\.venv\Scripts\python.exe manage.py purge_expired_attachments
```

The command deletes the storage object first and then removes its metadata row.
Running it again is safe. Lesson 19 will move this work to a background worker;
this lesson keeps the lifecycle visible and easy to run locally.

## Compile checkpoint

Apply the new migration before running the updated project:

```powershell
..\..\..\.venv\Scripts\python.exe manage.py migrate
```

From this directory:

```powershell
..\..\..\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\..\..\.venv\Scripts\python.exe -m compileall -q chat chat_project manage.py
```

Next: Lesson 19 introduces background jobs and Redis later in the architecture.
