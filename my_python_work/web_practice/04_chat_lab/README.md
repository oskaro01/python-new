# Chat Lab

This is a planned, separate messaging project. It is not part of the
Personal Dictionary app and it is not part of the customer checkout flow yet.

Status: Lesson 01 complete: project foundation and authentication boundary.

## Lesson 01: Project Foundation

The project now has:

- a standalone Django project and `manage.py`
- a `chat` application with public and authenticated routes
- Django's built-in login and logout flow
- a protected `/chat/` home page
- a local SQLite database for development
- a small responsive visual foundation

Run it from this directory:

```powershell
..\..\..\.venv\Scripts\python.exe manage.py runserver 8003
```

Open `http://127.0.0.1:8003/`. The `/chat/` page requires a Django user. Create
one with:

```powershell
..\..\..\.venv\Scripts\python.exe manage.py createsuperuser
```

The first lesson intentionally stopped before creating conversations or
messages. A message must belong to an authenticated sender, so identity and
access became the foundation for this data model.

## Lesson 02: Conversation Data Model

The first real chat entities are now defined:

- `Conversation` groups one thread and tracks its latest activity.
- `ConversationParticipant` connects users to conversations and prevents the
  same user being added twice to one conversation.
- `Message` stores the sender, body, read state, and creation time.

The database is intentionally SQLite for local learning. Redis is not a
replacement for these durable records. We will introduce Redis later for
temporary state, caching, background jobs, and real-time delivery support.

Create the migration after changing the models:

```powershell
..\..\..\.venv\Scripts\python.exe manage.py makemigrations chat
```

The future UI will follow the classic Messenger layout: an inbox list on the
left, the selected conversation in the main panel, and a composer fixed at the
bottom of that conversation. We will build that after participant-only access
and normal message forms are in place.

## Lesson 03: Participant-Only Access

Conversation pages now require both conditions:

1. The visitor must be signed in.
2. The signed-in user must be a participant in that conversation.

The permission check happens inside the database query. A non-participant
receives a normal `404` response instead of learning that someone else's
conversation exists. This is a useful privacy boundary for private messaging.

The route is:

```text
/chat/conversations/<conversation_id>/
```

## Lesson 04: Inbox Conversation List

The authenticated chat home now loads the current user's conversations only.
Each row links to the protected conversation detail page and shows the thread
participants. `distinct()` prevents duplicate rows when the database query
joins through the participant table.

This is the first piece of the Messenger-style layout. The next UI step will
replace the simple rows with a two-column inbox and active-thread layout after
message sending exists.

## Lesson 05: Send Messages with a Django Form

The conversation page now accepts normal `POST` requests through
`MessageForm`. The view sets the conversation and sender on the server, rather
than trusting hidden form fields from the browser. The participant query still
protects the whole page before the form can be submitted.

After a successful save, the view redirects back to the conversation. This
post/redirect/get pattern prevents a browser refresh from submitting the same
message again.

## Learning Order

We will build it in small checkpoints:

1. User accounts and user search
2. Conversation and message models
3. Inbox and conversation history
4. Send messages with normal Django forms
5. Participant-only permissions
6. Read and unread message state
7. Pagination and basic search
8. Block/report rules and moderation basics
9. Tests and security review
10. Real-time delivery with Django Channels and WebSockets

## Why Normal Requests Come First

The first version will use ordinary Django requests and responses. That makes
the data model, permissions, and message workflow easy to understand before
we add real-time behavior.

Later, WebSockets can provide:

- instant message delivery
- online status
- typing indicators
- read receipts

Those features need more infrastructure and are deliberately postponed.

## Planned Core Models

```text
Conversation
  created_at
  updated_at

ConversationParticipant
  conversation
  user

Message
  conversation
  sender
  body
  is_read
  created_at
```

The exact model design may change after we practice the first working version.

## What This Lab Will Teach

- user-to-user data relationships
- participant-only access rules
- conversation history
- unread counts
- pagination for growing message lists
- moderation and abuse boundaries
- the difference between normal HTTP and WebSockets
- when real-time features are worth their complexity

## What It Will Not Be

This will not try to recreate all of Facebook Messenger. We will start with
private text conversations and add complexity only when the underlying
concept is understood.
