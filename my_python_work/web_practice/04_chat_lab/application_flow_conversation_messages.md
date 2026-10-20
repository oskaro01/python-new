# Chat Lab: Conversation and Message Flow

This document traces the ordinary HTTP foundation of Chat Lab before we study
WebSockets: identity, user search, friend requests, conversation access,
message persistence, read state, expiry, and attachments.

## The data model

```text
User -> ConversationParticipant -> Conversation -> Message -> User(sender)
User -> FriendRequest
User -> Friendship
User -> UserBlock
Message -> MessageAttachment
User -> Profile
```

`ConversationParticipant` is the access-control relationship. A conversation
is not public because its numeric ID appears in a URL.

## Opening the inbox

`GET /chat/` passes through login protection and calls `chat_home()`. The
sidebar context queries the current user's conversations, friends, incoming
requests, blocked users, search results, and unread counts.

Unread counts include only unexpired messages from other participants. The
sidebar is a database projection of the current user's relationships and
message state.

## Searching and requesting friendship

Typing in people search calls:

```text
GET /chat/users/search/?q=...
```

The server searches username, names, and email, then excludes the current
user, inactive accounts, and blocked users. Each result reports `add`,
`pending`, `incoming`, or `friends`.

The Add action sends:

```text
POST /chat/users/<user_id>/request/
```

The view rejects self-requests, blocked users, existing friendships, and
duplicate pending requests. A new `FriendRequest` stores `from_user`,
`to_user`, and `status=pending`. A database conditional uniqueness
constraint protects pending requests. The recipient also receives a user
notification event for the later real-time UI.

The recipient responds with:

```text
POST /chat/requests/<request_id>/respond/
action=accept or decline
```

Only `to_user=request.user` may respond. A transaction changes only a still
pending request. Accepting creates a deterministic friendship row; declining
creates no friendship. Repeated clicks are harmless.

## Starting a conversation

The Chat action sends:

```text
POST /chat/users/<user_id>/start/
```

For self-chat, the view finds or creates one `is_self=True` conversation with
one participant. For another user, it rejects blocks, searches for an existing
two-person conversation, and creates the conversation plus two participant
rows if needed.

The server creates participant relationships; the browser does not choose an
arbitrary conversation membership.

## Opening a conversation safely

```text
GET /chat/conversations/<conversation_id>/
```

The view loads the conversation only when the requested ID belongs to a
conversation whose participants include `request.user`. It returns 404 when
the user is not a participant or when either side is blocked. This prevents
message access and conversation existence leaks.

The view filters out expired messages, applies optional body search, orders
newest-first for pagination, loads senders and attachments efficiently, and
reverses the displayed page for normal chat reading. The newest page has 20
messages.

## Sending a normal message

The composer submits:

```text
POST /chat/conversations/<conversation_id>/
body=Hello
csrfmiddlewaretoken=...
```

`MessageForm` trims the body and requires text or an attachment. The server
assigns the authorized conversation and `request.user` as sender. The browser
cannot choose another sender through hidden fields.

Inside `transaction.atomic()` the view creates the Message, stores its
expiry deadline, updates `Conversation.updated_at`, and optionally creates
attachment metadata.

With `X-Chat-Async: 1`, the response is JSON containing the rendered message
HTML and updated pagination HTML. Otherwise the view redirects back to the
conversation. Both are ordinary HTTP behavior; WebSockets are a later
delivery optimization.

## Read state and expiry

After loading a page, only displayed received messages are marked read:

```text
displayed IDs
and is_read=false
and sender != current user
```

Messages have an `expires_at` deadline. Reading them never extends it. The
same expiry filtering is used for unread counts and attachment access.

## Image attachment request path

The composer can send:

```text
multipart/form-data
attachment=<image bytes>
```

The form validates a maximum of 3 MB, JPEG/PNG/WebP MIME type and suffix, and
a file signature matching the claimed type.

The message and attachment metadata are saved in one transaction. The bytes
go through private storage. If saving fails, the exception path removes a file
that was already written.

Attachment downloads later require participant access, an unexpired message,
an unexpired attachment, and a valid private storage file.

## Complete ordinary flow

```text
login session
  -> GET /chat/
  -> current-user sidebar query
  -> POST start conversation
  -> participant-only conversation
  -> GET conversation page
  -> expiry/block/access checks
  -> POST message form
  -> CSRF and MessageForm validation
  -> assign request.user and authorized conversation
  -> atomic Message and optional attachment save
  -> JSON or redirect response
  -> displayed received messages marked read
```

## Security boundaries

- Login protects conversation operations.
- Participant filtering protects conversation pages and messages.
- Block checks prevent interaction in both directions.
- CSRF protects friendship, message, block, and account mutations.
- Sender and conversation come from server-side authorization.
- File validation checks size, MIME type, suffix, and signature.
- Expiry filters protect disappearing messages and attachments.

## Debugging checklist

```text
conversation 404        -> participant or block query
message not saved        -> CSRF, form, or transaction failure
message appears twice    -> HTTP insertion plus a later live append
unread count is wrong    -> expiry, sender exclusion, or read update
friend request repeats   -> pending uniqueness or response transition
attachment rejected      -> size, MIME, suffix, or signature validation
attachment leaks         -> private storage or participant filter
```

## Files involved

- `chat/models.py`: relationships, conversations, messages, and attachments.
- `chat/forms.py`: signup, message, attachment, profile, and report validation.
- `chat/views.py`: search, friendship, access, message, and file flows.
- `chat/urls.py`: HTTP route mapping.
- `chat/templates/chat/conversation_detail.html`: thread and composer.
- `chat/templates/chat/_message.html`: rendered message fragment.
- `chat_project/settings.py`: sessions, database, storage, TTL, and channels.
- `chat_project/asgi.py`: later HTTP/WebSocket protocol split.

