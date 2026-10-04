# Chat Lab

This is a planned, separate messaging project. It is not part of the
Personal Dictionary app and it is not part of the customer checkout flow yet.

Status: planned, not started.

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
