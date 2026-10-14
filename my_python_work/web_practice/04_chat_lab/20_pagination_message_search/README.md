# Chat Lab Lesson 20: Pagination And Message Search

We previously loaded every unexpired message in a conversation. Expiry limits
how long history lasts, but a busy conversation can still collect many messages
within 24 hours. This lesson limits each page to 20 and adds text search.

## Follow a request

```text
Open conversation
    -> check login and conversation membership
    -> filter out expired messages
    -> optionally filter message text
    -> count results and select one page of 20
    -> load those messages' senders and attachments
    -> display that page in chronological order
```

The same participant check runs before search. Searching a guessed conversation
ID does not grant access to someone else's messages.

## 1. Filter before loading

The search field submits `message_q` with GET. The view trims it to 200
characters and applies a substring filter:

```python
visible_messages = conversation.messages.filter(expires_at__gt=timezone.now())
if message_query:
    visible_messages = visible_messages.filter(body__icontains=message_query)
```

This search covers message text, including captions on images. Image filenames
and image contents are not searched. `message_q` is separate from the sidebar's
`chat_q` and the topbar's people search `q`.

## 2. Select the newest page first

In [views.py](../chat/views.py), the query orders by `-created_at`, then `-pk`:

```python
page_obj = Paginator(
    visible_messages.order_by("-created_at", "-pk")
    .select_related("sender").prefetch_related("attachments"),
    20,
).get_page(request.GET.get("page", 1))
```

Newest-first ordering makes page 1 the latest 20 messages. The primary key is
a tie-breaker if two messages share a timestamp. Django slices the query in SQL;
we do not first load all messages and then discard most of them in Python.

`select_related("sender")` fetches sender data with the message query.
`prefetch_related("attachments")` loads attachments for the selected page
together instead of querying them separately for each bubble.

## 3. Reverse only the small page

The newest-first database order is useful for choosing a page, but bubbles read
more naturally from older to newer. We reverse only the selected page in Python:

```python
messages = list(page_obj.object_list)
display_messages = list(reversed(messages))
```

Example with 25 messages:

| Page | Bubbles displayed from top to bottom |
| --- | --- |
| 1, latest | Messages 6 through 25 |
| 2, older | Messages 1 through 5 |

Only received messages on the displayed page are marked read. Searching or
opening one page does not mark unseen history as read.

## 4. Browse and search

The new controls provide **Older**, **Newer**, **Latest messages**, and a search
field. Pagination links retain the search term. Submitting a new search starts
at page 1. `get_page()` handles invalid page values: a nonnumeric value uses the
first page, while an out-of-range value uses the last page.

The count represents results when the request was handled. Messages can expire
or arrive later, so page counts and boundaries can change on your next request.
Numbered pages are a useful learning foundation; cursor pagination is an option
for a larger, fast-moving inbox. Substring search can still scan matching rows;
limiting rendered messages does not turn it into indexed full-text search.

## 5. Preserve asynchronous sending

On page 1 with no search, the composer appends the newly saved bubble and removes
the oldest visible bubble if the page exceeds 20. The response also updates the
pagination controls. That older bubble is still in the database until expiry;
use **Older** to read it.

On an older page or a search result page, sending still saves normally. We keep
your current selection and show `Sent. Open Latest messages to see your message.`
This prevents a new message from being appended to the wrong historical page or
to results where its text may not match. Opening pages and searches uses normal
navigation; sending remains asynchronous.

## Try it manually

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe my_python_work\web_practice\04_chat_lab\manage.py runserver 8003
```

No new migration or dependency is needed. If the one-minute demo setting is
still active, stop Django, remove it, and restart before building test history:

```powershell
Remove-Item Env:CHAT_MESSAGE_TTL_SECONDS -ErrorAction SilentlyContinue
```

Also check whether you put `CHAT_MESSAGE_TTL_SECONDS=60` in the Chat Lab `.env`;
use `86400` there to return to the 24-hour lifetime.

1. Send more than 20 messages in one conversation.
2. Confirm page 1 shows the most recent 20 and **Older** opens earlier messages.
3. Search for a distinctive word used in a few messages.
4. Send while viewing those results; confirm your search stays in place.
5. Open **Latest messages** to read the new message.

Balanced-mode verification: Python compile check only. No server or deep tests
were run automatically.

Memory hook: **authorize -> filter -> order -> paginate -> render**.

Commit message: `add chat message pagination and search`

Next: Lesson 21, security and moderation.
