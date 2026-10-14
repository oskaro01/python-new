# Chat Lab

This is a planned, separate messaging project. It is not part of the
Personal Dictionary app and it is not part of the customer checkout flow yet.

Status: Lesson 19 implemented: messages expire after 24 hours and a separate
cleanup process deletes them with their attachment files. Use a 60-second
setting for local demonstrations. The next checkpoint adds pagination and search.

## Lesson 17: Temporary Image Attachments

The conversation composer now accepts small JPEG, PNG, and WebP images. Image
metadata is stored in `MessageAttachment`, while file bytes are written to a
private storage root. Previews and downloads use a participant-filtered view,
so an outsider cannot guess a file URL and read it.

See [17_temporary_image_attachments/README.md](17_temporary_image_attachments/README.md)
for the architecture and checkpoint.

## Lesson 18: Attachment Expiry

Attachments now receive a configurable seven-day lifetime. Expired files are
hidden from previews and downloads, and
`purge_expired_attachments` removes their storage objects and metadata. See
[18_attachment_expiry/README.md](18_attachment_expiry/README.md).

## Lesson 19: Background Cleanup And Disappearing Messages

`CHAT_MESSAGE_TTL_SECONDS=86400` gives messages a 24-hour lifetime. Set it to
`60` before starting Django to demonstrate expiry on newly sent messages.
`run_chat_cleanup` periodically removes expired messages and their image files;
run it in a separate terminal. No Redis dependency is needed for this process.
See [19_background_jobs/README.md](19_background_jobs/README.md) for the two-terminal
demonstration, migration instructions, and cleanup lifecycle.

## Continuation from Lesson 17

The previous checkpoints through Lesson 16 covered identity, friendships,
conversation access, messaging, the Messenger shell, and profile pictures.

17. Temporary image attachments
18. Attachment expiry
19. Background jobs
20. Pagination and message search
21. Security and moderation
22. PostgreSQL and Render deployment
23. Real-time chat with Django Channels and WebSockets

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

## Lesson 06: Read State and Message Ownership

Opening a conversation now marks unread messages from other participants as
read. Messages sent by the current user remain separate from received messages
in the template, which gives the future Messenger-style layout the information
it needs for left/right message alignment.

The update excludes the current user as sender, so opening a thread does not
pretend that the user has received their own message.

## Lesson 07: Messenger-Style Inbox Shell

The chat home now has the first major layout shape: a conversation list on the
left and an empty active-thread area on the right. It is responsive and stacks
on narrow screens. The search field is visual groundwork for a later search
lesson; it does not filter yet.

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

## Lesson 08: Find a User and Start a Conversation

The inbox search can now find users by username. Selecting a result creates a
private two-person conversation, or reuses the existing one for that pair.
The action is a `POST` protected by CSRF, and users cannot start a conversation
with themselves.

## Lesson 09: Inbox Unread Counts

The inbox now annotates each conversation with unread messages received from
other participants. Messages sent by the current user do not increase the
badge. Opening the conversation uses the existing read-state update, so the
badge disappears naturally after the thread is viewed.

## Lesson 12: User Search and Friend Requests

The people search now updates while typing. It returns registered users who are
not the current user and shows an avatar slot, username, and request state.
Clicking **Add** creates a pending `FriendRequest` for the selected account and
changes the button to **Pending**. The request is stored in the database and
can later be accepted or declined by the recipient.

The current avatar slot uses the user's initial. The profile menu lesson will
replace it with an uploaded profile picture. Existing friendships and pending
requests are protected from duplicate Add actions.

## Lesson 13: Live User Suggestions

The search box now queries the user-search endpoint while typing instead of
waiting for a full page reload. Each suggestion contains an avatar slot, the
registered username, and an Add button. The button sends a CSRF-protected
request to the server and changes to Pending after the `FriendRequest` is
stored.

Next planned account lesson: let the recipient view, accept, or decline the
request. Profile names and uploaded pictures will then be connected to these
same suggestion rows.

## Lesson 14: Signup and Search Fallback

New users can now register at `/accounts/signup/`. Django validates the
username and passwords, saves the account, signs the user in, and creates the
self-chat on the first visit to the inbox.

The people search works in two ways: live suggestions while JavaScript is
available, and server-rendered suggestions after pressing Enter. This keeps
the workflow usable while the live request is loading or unavailable.

## Lesson 11: Conversation Names and Self Chat

Conversation rows now show the other participant's username instead of an
internal conversation number. Each signed-in user also receives a dedicated
self conversation labeled `<username> (You)`. It is a normal conversation, so
the same message and future attachment workflow can be reused for personal
notes.

Planned lessons:

- temporary image attachments with metadata in the database and file storage
- attachment expiry cleanup and recipient downloads
- PostgreSQL configuration and Render deployment

## Lesson 10: Sentry Error Monitoring

Sentry is a hosted error-monitoring service. When Django encounters an
unhandled exception, its SDK sends an error event with a stack trace to your
Sentry project. The dashboard groups related failures so you can see which
code failed and investigate it after deployment. It does not fix bugs itself.

The flow is: Django error -> Sentry SDK -> your Sentry project's Issues page.
This happens independently of our message read/unread state and WebSockets.

Install the Chat Lab dependencies from the workspace root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r my_python_work/web_practice/04_chat_lab/requirements.txt
```

Create `.env` inside `04_chat_lab` using `.env.example` as a template. Click
**Copy DSN** in the Sentry setup page and put that value in this file:

```env
SENTRY_DSN=your_project_dsn_here
SENTRY_ENVIRONMENT=development
```

The DSN tells the SDK which Sentry project should receive events. It is not a
Sentry account password or API authentication token. Keep this configuration
in the ignored `.env`, and commit only the empty `.env.example` template.
Django loads this lab's `.env` automatically without replacing variables
already set in the terminal. Restart an existing server after editing it.

To verify delivery, run this once from the workspace root after adding the DSN:

```powershell
.\.venv\Scripts\python.exe my_python_work/web_practice/04_chat_lab/manage.py shell -c "import sentry_sdk; from django.conf import settings; assert settings.SENTRY_DSN, 'Set SENTRY_DSN in the Chat Lab .env first'; event_id = sentry_sdk.capture_message('Chat Lab Sentry setup test', level='error'); sentry_sdk.flush(timeout=10); print('Event ID:', event_id)"
```

Look for **Chat Lab Sentry setup test** under Issues in your Sentry project.
An event ID means the SDK created an event; seeing it in Sentry confirms
delivery. This avoids leaving a deliberately crashing public URL in the app.
Real unhandled Django exceptions are captured automatically.

Our setup disables request-body collection, local-variable collection, and
automatic personal-data collection. Exception messages and URLs can still
contain sensitive content, so do not put messages or credentials in errors.
Performance tracing is disabled for this lesson; the screenshot's `1.0`
setting would sample every eligible transaction for tracing.

For Render later, set `SENTRY_DSN` and `SENTRY_ENVIRONMENT=production` in the
Chat Lab service's environment variables.

References: [Django integration](https://docs.sentry.io/platforms/python/integrations/django/)
and [SDK options](https://docs.sentry.io/platforms/python/configuration/options/).

## Current Features

## Lesson 15: Respond to Requests and Find Existing Chats

Friend requests now have different controls for each person: the sender sees
Pending, and the recipient sees Accept and Decline. Incoming requests appear
in the sidebar even without searching. Only the recipient can respond, using
a CSRF-protected POST. Acceptance creates a friendship; decline creates none.
Responses record a timestamp, and repeating a response leaves its result intact.

The top-bar search finds registered accounts and shows their relationship
state. Accepted friends have a Chat button. Its suggestions use the same
states as the server-rendered results after submitting without JavaScript.

The sidebar search filters existing conversations and accepted friends by
username or name. Typing filters the displayed list immediately; pressing
Enter or its search button searches on the server. Both controls are present
on the inbox and open-thread screens. Search icons are local Lucide assets.

To try it, send a request from one account, sign in as the recipient, and
accept it under Friend requests. The person then appears under Friends; Chat
opens their conversation. Search their name in Chats and friends to find them.

## Lesson 16: Profile Menu and Account Details

The signed-in user's top-right menu now links to Profile settings. A profile
stores an optional picture separately from Django's built-in user table. Search
and conversation identity continues to use the account's real username or
registered first and last name, so there is only one searchable identity.

Profile pictures are validated as image uploads up to 5 MB and are stored under
the local media directory. The database stores only the file reference. Local
media serving is enabled while `DEBUG` is true; production storage and private
attachment downloads will be separate lessons.

Open the menu, choose **Profile settings**, and save a picture. Search still
uses the account username or registered name.

## Current Features

The project now includes authentication, conversations, participants, message
sending, read state, participant-only access, and a Messenger-inspired thread
screen with an inbox sidebar and bottom composer.

Create local demo data with:

```powershell
..\..\..\.venv\Scripts\python.exe manage.py seed_demo_chat
```

Then sign in as `alice` with `alice-demo-password` or `bob` with
`bob-demo-password`. These credentials are for local learning only.
