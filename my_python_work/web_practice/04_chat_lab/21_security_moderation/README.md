# Chat Lab Lesson 21: Security And Moderation

Lesson 20 helped us find and page messages. Lesson 21 adds the boundaries that
keep that search and conversation system usable when someone behaves badly.

## What was added

- `UserBlock` records who blocked whom and prevents duplicate blocks
- blocked relationships stop new conversations and existing conversation access
- pending friend requests are declined when a block is created
- `MessageReport` stores one participant's report for one message
- reports have a reason and an admin-review status
- report controls appear on other participants' messages
- the conversation header provides a compact Block action
- expired messages and non-participant access remain protected

## The important rule

The browser is only a client. Hiding a button does not enforce a block. The
server checks blocks before returning a conversation, starting a conversation,
or sending a friend request:

```text
request -> authenticated user
        -> conversation participant check
        -> block relationship check
        -> allowed action or 404/blocked response
```

Reports use the same participant boundary. A user cannot report a message by
guessing an ID from a conversation they cannot access. The unique constraint
prevents one reporter from creating unlimited duplicate reports for one message.

## Block versus report

Blocking is an immediate relationship decision: the two users cannot start or
continue a chat while either direction of the block exists. Reporting creates a
reviewable record for staff. It does not silently delete a message or decide
that a report is true. Admins can inspect `MessageReport.status` and decide
whether to review or dismiss it.

## Files and flow

```text
UserBlock(blocker, blocked)
MessageReport(message, reporter, reason, status)
```

The block action also closes pending friend requests in either direction. The
existing conversation row and message history are retained for this lesson;
the blocked users simply cannot access the conversation. Later policy work can
decide whether a block should also hide old history or delete a user's copy.

## Try it manually

Apply the migration before running the project:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py migrate
```

1. Open a conversation with another user.
2. Submit **Block** in the thread header.
3. Confirm the user can no longer open the thread or start a new one.
4. In another conversation, open **Report** on the other user's message.
5. Choose a reason and submit it.
6. Inspect the report at `/admin/` as a staff user.

The block and report forms use POST and CSRF protection. There is no new Redis
or background-worker dependency in this lesson.

## Balanced-mode verification

Python compile check only. Migrations and the manual moderation flow are run by
you. No server or deep test run is claimed automatically.

Commit message: `add chat blocking and message reports`

Next: Lesson 22, PostgreSQL and Render deployment.
