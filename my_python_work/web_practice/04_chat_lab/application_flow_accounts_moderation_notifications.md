# Chat Lab: Accounts, Notifications, and Moderation

This flow covers the user-level controls around messaging: profile pictures,
account deletion, blocking, message reports, friend-request notifications,
and unread badges.

## Profile picture flow

The profile page submits:

```text
POST /chat/profile/
multipart/form-data
profile_picture=<image>
```

`ProfileForm` validates the uploaded image and its 5 MB limit. The profile is
a one-to-one row linked to Django's User. The database stores the file
reference; the image bytes are handled by storage.

After a successful replacement, the view deletes the previous file. If storage
fails, it adds a form error and keeps the user on the page instead of returning
a server error. The profile preview and sidebar use the protected profile
picture route.

The route accepts only paths under `uploads/profile_pictures/`, requires a
signed-in user, opens through Django storage, and returns private/no-store
content. It does not expose arbitrary filesystem paths.

## Account deletion

The deletion form requires:

```text
current password
explicit confirmation checkbox
```

The server verifies both before deleting the account. Inside a transaction,
Django deletes the user and cascading account-owned rows. The view then deletes
the user's profile image and message attachment files from storage, logs out
the session, and redirects to the landing page.

Database cascades remove relationship rows, profile data, conversations, and
messages. File cleanup is explicit because storage objects are outside normal
database cascade behavior.

## Blocking

The thread header submits:

```text
POST /chat/users/<user_id>/block/
```

The server creates a directional `UserBlock(blocker, blocked)` row with a
unique constraint. It also declines pending friend requests in either
direction.

A block is enforced at every relevant boundary:

```text
user search
friend request
conversation creation
conversation page
WebSocket connection
message save
```

Existing conversation rows and old messages are retained, but the blocked
relationship makes them inaccessible. This separates moderation access policy
from data deletion.

Unblocking removes only the current user's outgoing block:

```text
POST /chat/users/<user_id>/unblock/
```

## Reporting a message

A participant can report another user's unexpired message:

```text
POST /chat/messages/<message_id>/report/
reason=<spam|harassment|threat|other>
```

The server loads the message through a conversation-participant filter. Guessing
a message ID from another conversation does not work.

A `MessageReport` stores:

```text
message
reporter
reason
status = open/reviewed/dismissed
created_at
```

A unique constraint allows one reporter to create only one report for one
message. Reporting does not delete the message or declare the report true.
Staff review the record in Admin and choose the outcome.

## Live friend notifications

When a new friend request is created, the HTTP view sends a notification event
to:

```text
user_notifications_<recipient_id>
```

The recipient's `NotificationConsumer` forwards it through the open
`/ws/notifications/` socket. `notifications.js` inserts the request row,
shows Accept/Decline controls, and updates the Friends count.

The database FriendRequest row remains the source of truth. If the recipient was
offline, the next inbox request loads the pending row normally.

## Live chat notifications

When a message is created, the server sends:

```text
conversation group -> message bubbles for open participants
user group        -> notification for users on other pages
```

The notification JavaScript ignores the current conversation for the global
badge and increments the relevant conversation's unread count when the event is
for another thread.

On refresh, unread counts are rebuilt from unexpired database messages whose
sender is someone else. WebSocket events improve speed; they do not replace
that query.

## Moderation and account boundaries

```text
profile picture -> signed-in storage access
account deletion -> password + confirmation + transaction
block            -> directional relationship + server checks
report           -> participant-filtered review record
notification     -> authenticated user's channel group
unread badge     -> current user's database query
```

Hiding a button with JavaScript is not a security boundary. Every important
action has a server-side check.

## Complete moderation sequence

```text
user opens conversation
  -> POST block
  -> UserBlock row
  -> pending requests declined
  -> conversation/page/WebSocket access returns 404 or closes
  -> profile lists outgoing blocked users
  -> POST unblock
  -> block row deleted
  -> future access can be evaluated normally

participant sees message
  -> POST report
  -> participant-filtered lookup
  -> unique MessageReport row
  -> Admin review
  -> reviewed or dismissed status
```

## Debugging checklist

```text
profile upload 500       -> storage exception handling or backend config
old avatar remains       -> previous storage file cleanup
delete leaves files      -> explicit storage cleanup did not run
blocked user still chats -> missing check in one endpoint or consumer
report exposes others    -> participant filter missing
friend notification absent -> notification socket/channel layer
badge resets incorrectly -> database unread query or expiry filter
offline request missing  -> expected; database sidebar must load it on refresh
```

## Files involved

- `chat/forms.py`: profile, account deletion, and report validation.
- `chat/views.py`: profile storage, deletion, block, unblock, and report flows.
- `chat/models.py`: Profile, UserBlock, MessageReport, and relationships.
- `chat/consumers.py`: authenticated notification socket.
- `chat/static/chat/notifications.js`: live request and unread UI.
- `chat/templates/chat/profile.html`: profile, blocked users, and deletion forms.
- `chat/templates/chat/_message.html`: report controls.
- `chat/templates/chat/_sidebar.html`: friend requests and unread badges.

