# Chat Lab: Attachment and Expiry Lifecycle

Chat images use a different transport from text WebSockets. Binary data travels
through a validated multipart HTTP request. The saved message metadata is then
broadcast as a real-time event containing protected URLs.

## The two-channel design

```text
image bytes
  -> multipart HTTP POST
  -> form validation
  -> private storage + database metadata

message metadata
  -> channel layer/WebSocket event
  -> recipient browser
  -> protected HTTP image request
```

The WebSocket never carries the raw image bytes. It carries only the message
ID, filename, content type, expiry, and application URLs.

## 1. Selecting an image

The conversation composer contains a file input accepting:

```text
image/jpeg
image/png
image/webp
```

JavaScript shows the selected filename and intercepts form submission. If there
is an attachment, it does not use the text-only WebSocket path. It sends
`FormData(composer)` to the conversation URL with the CSRF token included.

The browser sets the multipart boundary automatically. JavaScript must not
manually set the multipart Content-Type header.

## 2. Server-side file validation

`MessageForm.clean_attachment()` checks all of these:

```text
file exists when an image message is intended
size <= 3 MB
suffix is .jpg, .jpeg, .png, or .webp
content_type matches the suffix
binary signature matches the claimed type
```

The file signature check matters because a filename and browser MIME header can
be forged. The form-level clean method also requires either a non-empty message
body or a valid attachment, allowing:

```text
text only
image only
text plus image
```

Invalid uploads return a form error and never create a message or attachment
row.

## 3. Database and storage are separate

The database stores `MessageAttachment` metadata:

```text
message relationship
original_name
content_type
size_bytes
storage filename
created_at
expires_at
```

The binary bytes are stored through `PrivateAttachmentStorage` under
`PRIVATE_MEDIA_ROOT`. The storage class has no public `base_url`.

The upload path generates a random UUID filename and keeps only a safe image
suffix:

```text
chat_attachments/<random UUID>.png
```

The original filename is metadata for display/download naming; it is not used as
the storage path.

## 4. The save transaction

The conversation POST handler uses one transaction for the durable records:

```text
create Message
  -> create MessageAttachment metadata and storage file
  -> update Conversation.updated_at
```

If the transaction or attachment creation fails after a file was written, the
exception path deletes that file. This avoids leaving a storage object with no
database owner.

The message and attachment receive expiry deadlines when they are created.
Reading them later does not extend those deadlines.

## 5. Broadcasting after upload

After the transaction succeeds, the view reloads the message with its sender
and attachments and calls the shared broadcast helper.

The payload contains:

```text
message_id
conversation_id
sender metadata
body
attachment preview URL
attachment download URL
original filename
content type
created_at
expires_at
```

The recipient browser receives this metadata over the conversation WebSocket.
It then creates an image element whose `src` points to the protected Django
attachment route.

The sender's HTTP response and the WebSocket event can arrive in either order.
The browser uses `message_id` to prevent duplicate rendering.

## 6. Protected preview and download

Both preview and download use:

```text
GET /chat/attachments/<attachment_id>/
GET /chat/attachments/<attachment_id>/?download=1
```

The view queries an attachment only when:

```text
request.user is authenticated
user participates in the attachment's conversation
attachment.expires_at > now
message.expires_at > now
```

An outsider, anonymous visitor, blocked participant, or expired request receives
404. The file path itself is never accepted from the browser.

Django opens the file through private storage, sets the stored content type, and
uses a safe content-disposition header. Downloads also receive private/no-store
cache behavior and `X-Content-Type-Options: nosniff`.

## 7. Browser-side expiry

Rendered message bubbles carry the message expiry timestamp. The
`message_expiry.js` timer removes the bubble from the current page when the
deadline arrives.

This is only a visual improvement. It is not security. A user can disable
JavaScript or hold an old URL, so the server repeats expiry checks on every
history query and attachment request.

## 8. Cleanup process

Physical deletion happens outside web requests. The management command:

```powershell
.\.venv\Scripts\python.exe manage.py run_chat_cleanup --once
```

runs both message and attachment cleanup. A recurring local worker is:

```powershell
.\.venv\Scripts\python.exe manage.py run_chat_cleanup --interval 30
```

Expired message cleanup deletes attachment files before deleting the expired
message rows. Expired attachment cleanup handles attachment rows whose parent
message still exists.

Cleanup processes batches of 100, so it does not load every expired row into
memory. Re-running it is safe: expired rows are selected again only if they
still exist.

The server hides expired data even if the cleanup process is stopped. Cleanup
controls physical removal, not access authorization.

## 9. Message versus attachment expiry

The parent message and attachment have separate deadlines:

```text
message expires first      -> message and attachment are no longer visible
attachment expires first   -> message remains, image shows expired/unavailable
cleanup pass               -> files and rows are physically removed
```

The protected attachment view checks both deadlines, so an attachment cannot
outlive an expired message through a direct URL.

## Complete attachment sequence

```text
choose image
  -> JavaScript builds FormData
  -> POST conversation URL
  -> CSRF and MessageForm validation
  -> atomic Message + attachment metadata save
  -> random private storage path
  -> conversation activity update
  -> broadcast safe metadata over channel layer
  -> recipient browser appends image link
  -> browser requests protected attachment URL
  -> participant and expiry checks
  -> private FileResponse
  -> browser timer removes expired bubble
  -> cleanup worker deletes file and metadata
```

## Failure and security boundaries

- A filename does not make an upload trustworthy.
- A WebSocket event does not grant file access.
- A private storage path is not a public URL.
- A participant check is repeated at download time.
- Browser timers do not replace server expiry checks.
- Cleanup is separate from authorization.
- Image bytes stay on HTTP; transient channel events carry metadata.
- Production ephemeral files require private object storage.

## Debugging checklist

```text
+ upload rejected          -> size, MIME, suffix, or signature validation
+ message saved, image 404 -> private file path or expiry
+ sender sees duplicate   -> HTTP/WebSocket message_id deduplication
+ recipient needs refresh  -> broadcast or client attachment rendering
+ expired image still opens -> attachment endpoint missing both expiry filters
+ files remain on disk     -> cleanup worker not running
+ outsider can preview     -> participant filter/storage boundary broken
+ Render files disappear   -> local filesystem is not durable storage
```

## Files involved

- `chat/forms.py`: image validation and message-level rules.
- `chat/models.py`: MessageAttachment metadata and expiry fields.
- `chat/storage.py`: private storage boundary.
- `chat/views.py`: multipart save, safe payload broadcast, and file streaming.
- `chat/realtime.py`: attachment URL metadata.
- `chat/static/chat/message_send.js`: FormData upload path.
- `chat/static/chat/message_realtime.js`: live attachment rendering.
- `chat/static/chat/message_expiry.js`: browser-side removal timer.
- `chat/management/commands/run_chat_cleanup.py`: recurring cleanup.
- `chat/management/commands/purge_expired_messages.py`: message/file cleanup.
- `chat/management/commands/purge_expired_attachments.py`: attachment cleanup.

