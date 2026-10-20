# Chat Lab: Complete End-to-End Review

This is the capstone map of Chat Lab. It connects the separate flows into one
user journey and shows where durable data, private files, transient events, and
browser UI each belong.

## 1. Account and identity

```text
signup/login form
  -> Django authentication
  -> auth_user row and session cookie
  -> request.user on HTTP requests
  -> scope["user"] on WebSocket connections
```

The session identifies the user; it does not give the browser permission to
choose a sender or conversation.

## 2. People and friendship

```text
people search
  -> server filters users and blocks
  -> FriendRequest row
  -> notification group event
  -> recipient accepts or declines
  -> Friendship row on acceptance
```

The database relationship remains authoritative when a recipient is offline.
The WebSocket only makes the UI update sooner.

## 3. Conversation access

```text
Chat button
  -> existing two-person Conversation or new Conversation
  -> ConversationParticipant rows
  -> participant-only HTTP page
  -> participant/block check on WebSocket connect
```

Every layer repeats the access boundary. A URL, event, or message ID is never
treated as permission by itself.

## 4. Text message journey

```text
composer
  -> WebSocket JSON when available
  -> consumer validates body and access
  -> database Message row
  -> channel group broadcast
  -> connected browsers append by message_id
```

If the socket is closed, JavaScript falls back to an HTTP POST. The database
save and normal history remain the recovery path.

## 5. Attachment journey

```text
file input
  -> multipart HTTP POST
  -> size/MIME/signature validation
  -> Message + MessageAttachment transaction
  -> private storage bytes
  -> safe attachment metadata broadcast
  -> protected preview/download request
```

Binary files stay outside the database and outside the WebSocket. The browser
receives a protected application URL, never a public filesystem path.

## 6. Notification journey

```text
new message or friend request
  -> user_notifications_<id> group
  -> NotificationConsumer
  -> notifications.js
  -> Chats/Friends count and sidebar update
```

On refresh, Django rebuilds unread counts from unexpired database messages.
This prevents a missed transient event from becoming permanently lost state.

## 7. Expiry and cleanup

```text
message created
  -> message and attachment expiry timestamps
  -> server filters expired rows
  -> browser removes expired bubbles
  -> cleanup worker deletes files and metadata
```

The browser timer is visual only. The server continues enforcing expiry if a
user disables JavaScript or keeps an old URL.

## 8. Moderation journey

```text
block request
  -> UserBlock row
  -> pending requests declined
  -> HTTP and WebSocket access rejected

report message
  -> participant-filtered lookup
  -> MessageReport row
  -> Admin review
```

Blocking changes access; reporting creates a review record. Neither action is
implemented as a browser-only UI decision.

## 9. Production journey

```text
git push
  -> Render installs dependencies
  -> collectstatic and migrations
  -> Gunicorn starts ASGI
  -> PostgreSQL stores durable records
  -> Redis shares WebSocket events
  -> private storage serves protected files
  -> cleanup worker removes expired data
  -> Sentry receives unexpected errors
```

Each infrastructure service has a distinct job:

```text
PostgreSQL = durable application state
Redis      = transient real-time transport
storage    = binary files
ASGI       = HTTP and WebSocket execution
Sentry     = error visibility
worker     = periodic cleanup
```

## The complete journey

```text
signup/login
  -> search person
  -> send and accept friendship
  -> create/reuse conversation
  -> authorize participant
  -> send text or image
  -> save durable record
  -> broadcast live event
  -> update open chat and global badges
  -> read only received visible messages
  -> expire messages/files
  -> cleanup worker deletes expired data
  -> PostgreSQL remains the history source
```

## What each layer must never do

```text
browser      -> never authorize itself
WebSocket    -> never replace database persistence
Redis        -> never become message history
database     -> never store secrets or unnecessary file blobs
file storage  -> never expose public attachment paths
cleanup      -> never decide whether a file is authorized
notification -> never be the only record of a friend request/message
```

## Final debugging order

When a feature fails, trace the same journey in order:

1. Is the browser sending the expected HTTP or WebSocket request?
2. Is the session authenticated?
3. Does the route or ASGI pattern match?
4. Does participant/block authorization pass?
5. Was the database row created?
6. Was the event sent through the channel layer?
7. Did the browser receive and deduplicate it?
8. Is the protected file route or expiry filter rejecting it?
9. Is production using the intended PostgreSQL, Redis, and storage settings?

## Remaining feature ideas

The current Chat Lab is complete as a learning application. Production-grade
extensions would be separate features rather than missing foundations:

```text
presence and online status
typing indicators
read receipts over WebSockets
durable object storage for uploads
multi-worker cleanup scheduling
push notifications outside the browser
```

The existing architecture gives each of those features a clear place without
changing the core user, conversation, message, and attachment relationships.
