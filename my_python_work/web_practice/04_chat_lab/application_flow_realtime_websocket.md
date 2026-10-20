# Chat Lab: WebSocket and Real-Time Delivery Flow

This document traces how a saved Chat Lab message travels from one browser to
another without a page refresh. WebSockets add instant delivery; they do not
replace the database, permissions, or attachment storage.

## The connection path

```text
browser WebSocket
  -> ASGI ProtocolTypeRouter
  -> AuthMiddlewareStack
  -> URLRouter
  -> ConversationConsumer
  -> channel-layer group
  -> connected browsers
```

The browser chooses `ws://` for local HTTP and `wss://` for HTTPS. The URL is:

```text
/ws/chat/conversations/<conversation_id>/
```

## 1. ASGI receives the upgrade

`chat_project/asgi.py` builds a `ProtocolTypeRouter` with two branches:

```text
HTTP       -> Django ASGI application
WebSocket  -> AuthMiddlewareStack + URLRouter
```

The WebSocket branch uses `chat/routing.py` to match the conversation ID and
select `ConversationConsumer.as_asgi()`. `AuthMiddlewareStack` reads the
Django session so the consumer receives the authenticated user in
`self.scope["user"]`.

This is why the ASGI server and WebSocket protocol library matter. A plain WSGI
server or incomplete Uvicorn installation can serve normal pages while treating
the WebSocket request as ordinary HTTP.

## 2. Consumer connection authorization

When `ConversationConsumer.connect()` runs, it:

1. Reads the conversation ID from the URL.
2. Builds the group name `chat_conversation_<id>`.
3. Checks authentication.
4. Checks conversation membership.
5. Checks both directions of `UserBlock`.
6. Adds the socket to the conversation group.
7. Adds it to the user's notification group.
8. Accepts the WebSocket.
9. Sends a small `ready` event.

An unauthorized connection closes with code 4403. A logged-out notification
socket closes with code 4401.

The permission check happens at connection time and again before saving a
message. A user could be blocked after the socket opened, so the later check
must still exist.

## 3. Channel groups

There are two logical groups:

```text
chat_conversation_12
  -> every connection currently viewing conversation 12

user_notifications_7
  -> every authenticated page belonging to user 7
```

A conversation socket joins both. The separate `NotificationConsumer` joins
only the user's notification group, allowing unread badges and friend-request
events to work while the user is on another page.

On disconnect, the consumer discards both group memberships.

## 4. Sending text through the socket

`message_send.js` intercepts the composer. When there is text but no
attachment, it calls `window.chatRealtimeSend(body)`.

`message_realtime.js` checks that the socket is open, the body is non-empty,
and the body is at most 5,000 characters. It sends JSON:

```json
{"body": "Hello"}
```

The consumer's `receive_json()` validates the body again. Browser validation is
only a convenience; the server is authoritative.

The consumer calls the synchronous database operation through
`database_sync_to_async`. That operation:

```text
rechecks authenticated membership
rechecks blocks
creates Message
sets expiry
updates Conversation.updated_at
builds safe payload
returns recipient IDs
```

The database remains the source of truth. The channel layer only carries the
event after the durable row exists.

## 5. Broadcasting the message

After the database operation succeeds, the consumer sends:

```text
group_send(chat_conversation_<id>, chat.message)
```

Every connected conversation consumer receives the event through
`chat_message()`, which sends the payload as JSON to its browser.

The consumer also sends notification events to each other participant:

```text
group_send(user_notifications_<recipient_id>, chat.notification)
```

The sender's own conversation socket receives the message through the
conversation group. Other pages receive the notification through the user
group.

## 6. The payload

`message_payload()` creates a small browser-safe object:

```text
type
message_id
conversation_id
sender_id
sender_name
body
attachments metadata
created_at
expires_at
```

Attachment entries contain protected application URLs, not raw filesystem
paths. The browser must still request the attachment endpoint, where normal
participant and expiry checks run.

The payload contains metadata and URLs; binary image bytes do not travel through
the WebSocket.

## 7. Browser rendering and duplicate prevention

When `message_realtime.js` receives a `message` event, it:

1. Checks whether the page is the newest unfiltered message page.
2. Creates a message article.
3. Sets text with `textContent`.
4. Adds protected image preview/download links.
5. Stores the message ID and expiry deadline.
6. Limits the visible list to 20 messages.
7. Scrolls the list to the newest message.
8. Removes the bubble when its expiry deadline arrives.

The HTTP fallback can receive the same message HTML around the same time as the
WebSocket broadcast. The browser checks:

```text
[data-message-id="<message_id>"]
```

before inserting. The durable message ID prevents a duplicate bubble.

If the user is viewing search results or an older page, the event is not
inserted into the wrong result set. The page shows a notice and the user opens
Latest messages.

## 8. Notification socket

Every page loads `notifications.js`, which opens:

```text
/ws/notifications/
```

`NotificationConsumer` authenticates the session, joins the user's group,
and forwards `chat.notification` events.

For a new message in another conversation, JavaScript:

```text
increments the Chats count
increments the conversation unread badge
leaves the open conversation's own badge unchanged
```

For a new friend request, it inserts the request row and updates the Friends
count. The server sends the friend event only after creating the database row.

## 9. HTTP fallback and attachments

Text can fall back to the existing HTTP POST when the WebSocket is closed. The
server saves the message and returns rendered HTML through the async request
path.

Attachments always use the multipart HTTP path:

```text
file input
  -> MessageForm validation
  -> HTTP POST
  -> Message + MessageAttachment transaction
  -> private storage
  -> _broadcast_message()
  -> WebSocket metadata event
  -> each browser fetches protected image URL
```

This keeps binary upload validation and private storage in the existing Django
flow. The WebSocket distributes only the saved message metadata.

## 10. Redis and local fallback

Settings choose the channel layer:

```text
REDIS_URL present -> channels_redis RedisChannelLayer
REDIS_URL absent  -> InMemoryChannelLayer
```

The in-memory layer works for one local process. It is not a shared production
bus: a second web process has different memory.

Redis carries transient events. PostgreSQL/SQLite stores users, conversations,
messages, friendships, and attachments. If a socket misses an event, normal
HTTP history and pagination recover the durable message.

## 11. Reconnection

Both browser sockets reconnect after close. The delay starts at one second and
grows up to ten seconds. A successful open resets the delay.

This handles temporary network loss, but it does not replay every missed event.
After reconnect, the page's durable HTTP history is the repair mechanism.

## Complete real-time sequence

```text
conversation page loads
  -> browser opens WebSocket
  -> ASGI authenticates session
  -> consumer checks participant/block access
  -> joins conversation and user groups
  -> sender sends JSON body
  -> consumer validates and saves Message
  -> channel layer broadcasts message event
  -> conversation browsers append by message ID
  -> notification browsers update unread badges
  -> HTTP history repairs missed events
```

## Failure and security boundaries

- WebSocket authentication comes from the Django session.
- Membership and block checks happen before accept and before save.
- The database row is saved before broadcast.
- Redis/in-memory events are not the source of truth.
- Payloads contain protected URLs, not filesystem paths.
- DOM text uses safe text insertion.
- Message IDs prevent HTTP/WebSocket duplicate rendering.
- Reconnection does not bypass participant checks.

## Debugging checklist

```text
+ normal HTTP works, WebSocket 404 -> ASGI/worker/protocol support
+ socket closes 4401              -> missing authentication session
+ socket closes 4403              -> participant or block rejection
+ message saves, no live event    -> channel layer or Redis configuration
+ duplicate bubbles               -> message_id deduplication missing
+ unread badge stale               -> notification socket or group name
+ attachment needs refresh         -> multipart/broadcast/client rendering path
+ reconnect loops                  -> browser URL, HTTPS scheme, or server logs
```

## Files involved

- `chat_project/asgi.py`: HTTP/WebSocket protocol split.
- `chat/routing.py`: WebSocket URL patterns.
- `chat/consumers.py`: connection, authorization, save, and broadcast.
- `chat/realtime.py`: shared safe message payload.
- `chat/views.py`: HTTP save path and broadcast for attachments.
- `chat/static/chat/message_realtime.js`: conversation socket and rendering.
- `chat/static/chat/message_send.js`: WebSocket/HTTP send choice.
- `chat/static/chat/notifications.js`: user notification socket.
- `chat_project/settings.py`: Redis or in-memory channel layer.

