# Chat Lab Lesson 17: Temporary Image Attachments

Messages can now carry a small image while keeping the existing text-message
workflow intact.

## What was added

- an optional image input in the message composer
- JPEG, PNG, and WebP validation with a 3 MB limit
- image-only messages as well as text-plus-image messages
- a `MessageAttachment` record that stores file metadata, not file bytes
- a private attachment storage root outside public `MEDIA_ROOT`
- inline previews inside the conversation
- a protected download route for conversation participants

The attachment table stores the original filename, content type, size, and
storage path. The binary itself lives in `private_media/`. The browser never
receives a public `/media/` URL for an attachment. Every preview and download
passes through the participant-filtered view:

```text
request user
  -> attachment
      -> message
          -> conversation participant check
              -> private file stream
```

This is intentionally a temporary-attachment foundation. Expiration timestamps
and cleanup jobs belong to Lesson 18; background workers belong to Lesson 19.

## Try it

From this directory:

```powershell
..\..\..\.venv\Scripts\python.exe manage.py migrate
..\..\..\.venv\Scripts\python.exe manage.py test chat
..\..\..\.venv\Scripts\python.exe manage.py runserver 8003
```

Open a conversation, choose a small image in **Attach image**, and send it.
The recipient can see the protected preview and use its download link. An
outsider receives `404`, and an anonymous visitor is redirected to login.

## Checkpoint

Be able to explain:

1. Why the image bytes are not stored in the `Message` database row.
2. Why the attachment route checks conversation membership again.
3. Why a `multipart/form-data` form is required for file uploads.
4. Why image-only messages need an explicit form-level validation rule.

Next: Lesson 18 adds expiration timestamps and automatic removal of expired
attachment files.
