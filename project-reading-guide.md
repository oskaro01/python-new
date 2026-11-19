# Learn to Read a Project, Not Just Its Files

This is a practice workbook. You will make predictions, find evidence, trace
real code and explain it back. Reading the explanations is only half the work.

**Start with Session 1 only.** You do not need to finish this whole document
today. The later sessions give you a path, not more material to memorize.
Recognizing every filename is not the goal. Connecting a user action to the
code, data and result is.

## Your Learning Path

| Session | What you practice | What you should be able to show |
| --- | --- | --- |
| 1 | Identify the stack and follow Daynotes startup | A small project map backed by code, not guesses. |
| 2 | Trace an edit, its data and the scroll bug | A complete save trace and a testable debugging hypothesis. |
| 3 | Follow PDF Glue through a background thread | Explain who does the work and who updates the window. |
| 4 | Follow Chat Lab across browser and server | Separate HTTP, WebSockets, database writes and UI updates. |
| 5 | Investigate a feature without a walkthrough | Produce a handover map and a safe change/test plan. |

Expect several focused sessions. A 20-minute first look can identify a
project's broad shape; it cannot prove that you understand every feature,
security rule, failure path and deployment detail.

Contents:

- [The Skill You Are Building](#the-skill-you-are-building)
- [Before You Start](#before-you-start)
- [Session 1: Read the Project Like a Machine](#session-1-read-the-project-like-a-machine)
- [Session 2: Trace Daynotes End to End](#session-2-trace-daynotes-end-to-end)
- [Session 3: Transfer the Method to PDF Glue](#session-3-transfer-the-method-to-pdf-glue)
- [Session 4: Cross the Browser-Server Boundary](#session-4-cross-the-browser-server-boundary)
- [Session 5: Investigate Without the Walkthrough](#session-5-investigate-without-the-walkthrough)
- [Your Investigation Toolkit](#your-investigation-toolkit)
- [Practice and Progress Check](#practice-and-progress-check)

## The Skill You Are Building

Suppose someone asks: "Where would you change how saving works?"

A weak answer is: "Probably in `app.js`."

A useful answer is: "The input listener in `app.js` schedules `flush()`.
`flush()` calls `NotesStore.save()` in `storage.js`. I would change the timer
for save timing, but the store for persistence rules. I would check both a
successful save and a failed save before trusting the success indicator."

The second answer connects an action to specific code and evidence. That is
the goal. Memorizing the folder tree is not.

Use this loop for every exercise:

```text
PREDICT what you think happens
-> FIND the relevant code
-> TRACE its inputs, decisions and effects
-> OBSERVE it running when safe
-> EXPLAIN it without looking
-> CHECK your explanation against the evidence
```

Keep guesses separate from facts:

| Claim | Evidence | What is still unknown? |
| --- | --- | --- |
| Daynotes loads browser JavaScript | Script tags in `index.html` | Whether those scripts call a server. |
| Text notes are saved locally | `NotesStore.write()` calls `storage.setItem()` | Whether saving succeeds in this browser profile. |
| This Chat Lab deployment uses Redis | Not established just by finding Redis code | Which settings branch the running service selects. |

"The code supports this" and "I observed this happening" are different claims.
When an exercise has a hidden answer, attempt it first. If stuck, write the
missing connection before opening the answer. That is useful evidence too.

## Before You Start

All terminal commands below assume the repository root:

```text
C:\Users\ASUS\Desktop\python-new
```

Search/read commands do not start servers or modify application data. Optional
runtime exercises are marked. Writing this workbook does not start servers
or change application behavior.

Safety rules:

- Read install/build/start scripts before executing an unfamiliar repository.
- Use disposable browser notes, sample PDFs and test accounts for exercises.
- Use a disposable browser profile for Daynotes practice, not important notes.
- Daynotes notes expire after 24 hours. Download anything you need to keep.
- Do not clear site storage to debug a display problem.
- Inspect `.env.example` for configuration names, not real `.env` secrets.
- Do not run migrations, cleanup commands or test payments against production.
- A local Django process can connect to a remote database if configured that way. Check its environment before running it.

The current source is the reference for these examples. Older README lessons
can describe an earlier checkpoint. Runtime observations still need a safe
local setup, especially for server and WebSocket exercises.

Use VS Code's Markdown preview (`Ctrl+Shift+V`) for the collapsible checkpoints.
The plain-text editor shows their answer text directly. Try the exercise
before opening its checkpoint.

## Session 1: Read the Project Like a Machine

### 1.1 Find the Actual App Root

Open the repository in your terminal:

```powershell
Get-ChildItem -Force
```

This tells you which folders exist. It does not tell you which code runs.
Our repository contains multiple applications. Narrow the scope:

```powershell
rg --files my_python_work/side_quests/daynotes
```

`rg --files` lists filenames; it is not searching contents yet. Ignore icons
and tests on your first pass. Find the README, HTML, CSS and application scripts.

**Write before continuing:**

```text
Repository root:
Daynotes app root:
Likely first file opened by the user:
What I think saves the notes:
Evidence I still need:
```

<details>
<summary>Checkpoint: repository versus application</summary>

The app root is `my_python_work/side_quests/daynotes`, not the repository root.
The user opens `index.html`. Do not conclude where notes are stored until you
inspect the scripts it loads. A filename such as `storage.js` is a clue, not
proof of a particular storage mechanism.

</details>

### 1.2 What Actually Makes Code Run?

Open [Daynotes index.html](my_python_work/side_quests/daynotes/index.html).
Find its script tags and the editor's `note-body` ID. Ask:

1. Which scripts load, and in what order?
2. Where does the element with ID `note-body` come from?
3. Does the HTML itself save anything?
4. Why might loading the storage scripts before `app.js` matter?

<details>
<summary>Checkpoint: startup</summary>

The scripts are `storage.js`, `image-storage.js`, then `app.js`, with `defer`.
These classic deferred scripts execute in document order after HTML parsing.
The textarea is created from the HTML. `app.js` finds it and connects behavior
to it. The storage scripts define APIs that `app.js` expects to exist.

The HTML defines the surface; JavaScript supplies behavior. CSS changes the
appearance and layout, not the persistence rules. Missing a required script
can stop startup before any button works.

</details>

Open [Daynotes app.js](my_python_work/side_quests/daynotes/app.js). Near the top:

```javascript
const byId = (id) => document.getElementById(id);
const body = byId("note-body");
```

Translate that into ordinary language:

```text
Find the existing textarea and keep a reference to that element.
```

`body` is an element, not the note's text. `body.value` is its current text.
A function that changes `body.style.height` is changing layout, not replacing
the saved note. Learn to distinguish the object from its properties.

### 1.3 Definition, Registration and Execution Are Different

These do not all mean "the work runs now":

```javascript
function flush() { /* saving logic */ }   // define a function
input.addEventListener("input", handler); // register a callback
setTimeout(flush, 250);                   // schedule a later callback
flush();                                 // call it now
```

`input` and `handler` above are teaching placeholders. Find the actual names
and anonymous callback in Daynotes; do not paste this snippet into the app.

Python has the same distinction:

```python
button = ttk.Button(frame, command=self.start)  # pass the callback
result = self.start()                          # call it now
```

**Exercise:** find one function definition, event registration, timer
registration and immediate function call in `app.js`. Explain what triggers
each. If you cannot say when it runs, you do not have that part of the flow yet.

### 1.4 Make a Small Responsibility Map

```text
index.html          creates the editor and controls
styles.css          lays out the page and text area
app.js              handles events and coordinates the UI
storage.js          validates/stores/expires text notes
image-storage.js    stores and cleans up screenshot blobs
tests/              checks behavior; not the website's runtime backend
```

Explain without looking: why is Daynotes not a Python website just because its
tests include `.py` files? Why is browser storage not cloud sync?

**Session 1 completion check:** you can identify the actual app root, explain
which files load first, distinguish an element from its value, and find one
real callback registration. Stop here before adding another framework.

## Session 2: Trace Daynotes End to End

### 2.1 Choose One Precise User Story

Your investigation is:

> I type `Milk` into a new note. What changes before and after it is saved?

Avoid "how does Daynotes work?" for now. That question is too wide.
Search for a unique UI identifier, then its handler:

```powershell
rg -n -F 'note-body' my_python_work/side_quests/daynotes/index.html my_python_work/side_quests/daynotes/app.js
rg -n -F '[title, body]' my_python_work/side_quests/daynotes/app.js
```

`-n` prints line numbers. `-F` searches literal text rather than a regular
expression. Results are navigation points: read the surrounding function,
not just the matching line. VS Code Search is an alternative.

### 2.2 Ask Five Questions of Every Important Function

```text
TRIGGER: Who calls it, and when?
INPUT: What arguments/state does it read?
DECISIONS: Which conditions change its path?
EFFECTS: What does it change or write?
NEXT: What return value, callback or response continues the flow?
```

Apply this to the input listener before opening the checkpoint:

<details>
<summary>Checkpoint: the input listener</summary>

- Trigger: an input event on the title or body.
- Input: current editor values and existing timer/state.
- Decisions: important save checks are in `flush()` and the store, not all in this listener.
- Effects: mark dirty, show Saving, update metadata, resize the body and cancel the previous timer.
- Next: schedule `flush()` after 250 ms. A subsequent edit can replace that timer.

A direct JavaScript assignment to a field's value does not inherently dispatch
an input event. A normal user edit and assigning a property are not identical.

</details>

Follow `flush()`, then `NotesStore.save()`, then `write()` in
[storage.js](my_python_work/side_quests/daynotes/storage.js). Do not read all
other UI handlers you pass along the way.

### 2.3 Track Data, Not Just Function Names

| Place | Meaning | Survives a normal reload? |
| --- | --- | --- |
| `body.value` | Current text in the textarea | Not by itself. |
| `dirty` | Whether the current draft needs saving | No; in-memory state. |
| `active` | Current saved note object, or no note yet | The variable does not; the note can be reconstructed. |
| `notes` | Current in-memory list | Rebuilt from storage. |
| `daynotes.v1` in localStorage | Serialized saved note records | Normally, until expiry/clearing/eviction; not a permanent backup. |
| IndexedDB screenshot store | Image blobs associated with note IDs | Normally, subject to cleanup and browser storage limits. |

**Predict:** after typing but before the scheduled save, can the displayed text
and stored text temporarily differ? What should `dirty` indicate?

<details>
<summary>Checkpoint: state versus persistence</summary>

Yes. The editor can show new text while storage still holds the previous
successful save. `dirty` becomes true. Successful `flush()` updates `active`,
clears dirty, reports Saved and refreshes the list.

`NotesStore.save()` preserves an existing note's creation time. Editing updates
its text/update time, not its original 24-hour lifetime. `write()` serializes
records with `JSON.stringify()` and writes localStorage.

</details>

Now write the flow this specifically:

```text
User changes textarea
-> registered input callback in app.js
-> dirty = true, Saving status, updateMeta(), sizeBody()
-> clear previous timer; schedule flush()
-> timer callback runs later
-> flush() checks whether saving is needed/possible
-> NotesStore.save({ id, title, body })
-> validation, expiry checks, record creation/update
-> write() -> localStorage.setItem(...)
-> updated note returns to flush()
-> Saved status and refreshed list
```

The input callback finishes before the timer runs. Do not expect one continuous
call stack across that delay. Connect the parts using the scheduled callback
and the state it reads. The debounce is not a background server/worker.

### 2.4 Observe It Instead of Trusting the Diagram

Optional: use only disposable notes in a disposable browser profile.

1. Open Daynotes and browser DevTools.
2. In Sources, find `app.js`; set a breakpoint on `dirty = true` in the input listener.
3. Set another breakpoint where `flush()` calls `store.save(...)`.
4. Type one letter. Inspect `body.value`, `dirty` and `active` while paused.
5. Step over executes a line without descending into every function. Step into enters a function you deliberately want to inspect.
6. Resume, observe the timer breakpoint, then follow `save()` and `write()`.
7. In Application, inspect the `daynotes.v1` localStorage entry for this practice profile.
8. Reload; locate the startup calls that read/prune notes and open one.

These read-only Console expressions help:

```javascript
document.getElementById("note-body").value
document.getElementById("writing-surface").scrollTop
```

Check Network too. The text-save path needs no HTTP save request in this
version. An absent XHR/fetch save request is consistent with local storage,
not proof that saving failed.

Record what you observed. If you did not run it, label your conclusion
"code traced, not runtime verified."

### 2.5 Investigate the Scroll Bug Like a Debugger

Symptom: Space or Backspace makes a long note jump while editing.
Do not immediately rewrite saving. Compare hypotheses:

| Hypothesis | Evidence to find |
| --- | --- |
| The note reopens on every edit | Does the normal input/save path call `openNote()`? |
| Auto-sizing shrinks the scrollable layout | Does `sizeBody()` temporarily reduce the textarea height? |
| Focus/selection changes move the viewport | Which code changes focus, selection or uses `scrollIntoView()`? |

```powershell
rg -n -F -e 'function sizeBody' -e 'function openNote' -e 'scrollTop' -e 'scrollIntoView' my_python_work/side_quests/daynotes/app.js
```

`-e` lets you search several literal patterns. Read both functions.
`openNote()` intentionally starts a different note at the top. That does not
make it the cause of an edit-time jump. The normal save refresh only reopens
the editor for an expired/deleted active note. Prove the executed path.

Auto-sizing briefly sets the textarea height to zero to measure
`scrollHeight`. That can shrink the outer scroll range and clamp its position.
The fix preserves the writing surface's scroll coordinates around measurement.
It still uses auto-sizing; it controls the unwanted side effect.

**Design a regression test before looking at ours:**

- What size note makes the bug visible?
- Where must the cursor and viewport be before Space?
- What must remain unchanged after Space, Backspace and autosave?
- What should happen when replacing the long note with short text?
- Which note property must editing never extend?

<details>
<summary>Checkpoint: testing the explanation</summary>

Use a note much longer than the viewport, scroll into its middle and place the
caret there. Compare scroll/selection before and after real keyboard input,
then after autosave. Space followed by Backspace should restore the text.
Replacing all text with a short note should still shrink the editor and
legitimately clamp scroll to the top.

Check that `expiresAt` stays unchanged. Test desktop/mobile in an isolated
profile. See [editing_scroll_smoke.py](my_python_work/side_quests/daynotes/tests/editing_scroll_smoke.py).
The important skill is explaining why each assertion tests the suspected cause.

</details>

### 2.6 Explain It Back

Close the code and answer in your own words:

1. What runs immediately when I type, and what runs later?
2. Where is the actual persistence operation?
3. Why does new visible text not prove it was saved?
4. Why was the scroll fix in the resize helper, not the storage adapter?
5. How does opening a different note differ from editing this note?
6. If saving throws, who reports it, and is the draft discarded?

<details>
<summary>Hint for question 6</summary>

The general error branch in `flush()` reports the error and returns false
without pretending success. Dirty text remains in the editor. Distinguish
that from the special expired-note path that refreshes the stored note list.

</details>

Your deliverable: a trace with function names, data read/written, one failure
path and a test that distinguishes persistence from a convincing-looking UI.

## Session 3: Transfer the Method to PDF Glue

This is not a website. That helps test whether you learned the method or only
memorized Daynotes names. Read:

- [app.py](my_python_work/side_quests/pdf_glue/app.py)
- [gui.py](my_python_work/side_quests/pdf_glue/gui.py)
- [merger.py](my_python_work/side_quests/pdf_glue/merger.py)

### 3.1 Find the Two Entry Paths

Predict what happens when `app.py` receives no arguments, and when it receives
PDF paths plus an output argument. Then read `main()`.

<details>
<summary>Checkpoint: two interfaces, one core operation</summary>

Without arguments, `main()` imports `launch()` and opens the desktop window.
With arguments, it parses CLI options and calls `merge_pdfs()` directly.
These are two interfaces to the same merge engine. The `if __name__ ==
"__main__"` guard selects script execution rather than merely importing it.

</details>

### 3.2 Follow the Merge Button and Its Background Work

Find the button whose `command` is `self.start`. Read only `start()`,
`worker()` and `poll()` first. Answer the five function-reading questions.
Draw which work runs on the GUI thread and which on the worker thread.

<details>
<summary>Checkpoint: GUI and worker timeline</summary>

```text
GUI thread:
  Merge button -> start()
  -> validate paths; confirm overwrite if needed
  -> disable controls; show progress
  -> start worker thread; schedule poll()

Worker thread:
  worker() -> merge_pdfs(...)
  -> queue progress events
  -> queue ("done", MergeResult) or ("error", text)

GUI thread later:
  poll() reads queue events
  -> update progress/status
  -> re-enable controls on completion/failure
  -> optionally open the completed PDF
```

`Thread(...).start()` begins concurrent work. `Queue` carries messages.
`root.after(...)` schedules GUI polling. The worker does not need to manipulate
Tk widgets directly. The GUI prevents normal closing while a merge is busy.

This is a thread and in-memory queue inside one desktop process. It is not
Redis or a durable server queue, and it does not make the merge survive
termination of the application process.

</details>

### 3.3 Follow Data to Its Durable Output

In `merge_pdfs()`, locate input/output validation, the source loop, temporary
output, page-count verification, final publication, failure cleanup and the
returned `MergeResult`.

Predict:

- A has two pages; B has three. What should `A, B, A` produce?
- What happens if the output path is also an input path?
- What happens if the last source is invalid after earlier ones were read?
- Does a progress event prove the final output exists?

<details>
<summary>Checkpoint: ordering, output safety and results</summary>

`A, B, A` should have seven pages in that order; duplicates are intentional.
`validate_paths()` rejects using an input as output. Filename checks do not
replace PDF content checks performed by the reader.

The merger writes a temporary file, verifies page count, then publishes it
through the appropriate overwrite/non-overwrite path. A failed merge must not
replace an existing output with a partial document. A remaining temporary file
is removed in `finally`. Progress means work in flight, not final success.

`MergeResult` contains the final path, file count, page count and size. It is
not the PDF bytes. The GUI reads this result to report completion.

</details>

### 3.4 Optional Safe Runtime Exercise

Use only small disposable PDFs and a new output filename. Read the app README
and requirements before running anything. The code-reading exercise does not
require launching the GUI.

If you run it, record selected order, predicted page count, progress messages
and actual output page count. Compare CLI and GUI paths. Never overwrite your
sources or use confidential documents for practice.

Explain back: why does a progress label belong in `gui.py`, while output safety
belongs in `merger.py`? What would happen if the expensive merge ran directly
on the button's GUI thread?

## Session 4: Cross the Browser-Server Boundary

Move to [Chat Lab](my_python_work/web_practice/04_chat_lab/README.md).
Do the code trace first. Runtime work needs a verified local/test database,
test accounts and the processes in the current README. Do not start a
production-connected process just to follow the workbook.

### 4.1 Map the Route Before Reading Every View

Read in order:

1. [chat_project/urls.py](my_python_work/web_practice/04_chat_lab/chat_project/urls.py)
2. [chat/urls.py](my_python_work/web_practice/04_chat_lab/chat/urls.py)
3. `conversation_detail()` in [views.py](my_python_work/web_practice/04_chat_lab/chat/views.py).

Trace `/chat/conversations/7/` using a hypothetical ID. That is not a claim
that conversation 7 exists or that your account can access it.

<details>
<summary>Checkpoint: URL to handler</summary>

Project URLs include `chat.urls` at the empty prefix. The app pattern
`chat/conversations/<int:conversation_id>/` selects `views.conversation_detail`.
The captured integer becomes the argument. The request method then determines
display versus input-processing behavior. Selecting a handler is not yet a
database write.

</details>

### 4.2 Inspect the Browser Before Assuming the Transport

Open:

- [conversation_detail.html](my_python_work/web_practice/04_chat_lab/chat/templates/chat/conversation_detail.html)
- [message_send.js](my_python_work/web_practice/04_chat_lab/chat/static/chat/message_send.js)
- [message_realtime.js](my_python_work/web_practice/04_chat_lab/chat/static/chat/message_realtime.js)

Find `message-composer`, its submit listener and the conditional before
`fetch()`. Predict the path for each case:

| Case | Your prediction |
| --- | --- |
| Valid short text, no image, socket ready | |
| Image selected | |
| Text with unavailable socket | |

<details>
<summary>Checkpoint: more than one send path</summary>

The submit handler first attempts `window.chatRealtimeSend()` for text without
an attachment. If it returns true, it skips HTTP. Images use HTTP `fetch()`
and `FormData`. Refused/unavailable realtime sending can fall back to HTTP.

`event.preventDefault()` stops ordinary form submission so JavaScript can
choose. Reading only the HTML form would miss this decision. The template
loads the realtime script before the submit-handling script.

</details>

### 4.3 Trace the HTTP Path in Detail

Follow a request containing an image through:

- [MessageForm](my_python_work/web_practice/04_chat_lab/chat/forms.py)
- `conversation_detail()` in [views.py](my_python_work/web_practice/04_chat_lab/chat/views.py)
- `Message` and `MessageAttachment` in [models.py](my_python_work/web_practice/04_chat_lab/chat/models.py)

Fill this in before opening the answer:

```text
Browser URL/method:
Payload format and fields:
Login check:
Conversation access check:
Form validation:
Who supplies sender/conversation:
First database write:
Attachment metadata versus file bytes:
Response format:
Client success check:
UI insertion and duplicate prevention:
```

<details>
<summary>Checkpoint: HTTP end-to-end trace</summary>

```text
Composer submit
-> fetch POST to conversation page URL, using FormData
-> session/authentication and request protections
-> login_required; participant-filtered lookup; block checks
-> MessageForm(request.POST, request.FILES).is_valid()
-> form.save(commit=False): construct an unsaved Message
-> assign conversation and sender from server context
-> message.save() inside the atomic block
-> create MessageAttachment for an upload; update conversation activity
-> reload message relationships and broadcast
-> JSON response for X-Chat-Async: 1
-> client checks response.ok AND payload.ok
-> append HTML when appropriate, unless that message ID already exists
```

The form permits text-only or image-only messages, but not empty text with
no image. It checks attachment size/type/signature. Sender and conversation
come from server context, not trusted hidden fields.

`commit=False` is not a background job. It returns an unsaved model instance
so the view can assign trusted fields before saving.

`MessageAttachment` holds metadata and a file reference. Its FileField uses
private storage for image bytes; the database row is not the image itself.
JSON includes the message ID and rendered HTML/pagination. A successful normal
non-async form POST instead returns a redirect.

`X-Chat-Async` selects response style here. It does not mean the view queues
the save for an independent worker.

</details>

### 4.4 Follow WebSockets Separately

Read:

- [chat_project/asgi.py](my_python_work/web_practice/04_chat_lab/chat_project/asgi.py)
- [chat/routing.py](my_python_work/web_practice/04_chat_lab/chat/routing.py)
- `ConversationConsumer` in [consumers.py](my_python_work/web_practice/04_chat_lab/chat/consumers.py)
- [realtime.py](my_python_work/web_practice/04_chat_lab/chat/realtime.py)

Draw the text-message path without routing it through `conversation_detail()`
by habit.

<details>
<summary>Checkpoint: realtime text</summary>

```text
message_send.js chooses chatRealtimeSend(body)
-> message_realtime.js socket.send(JSON.stringify({ body }))
-> existing /ws/chat/conversations/<id>/ connection
-> ASGI websocket branch with authentication middleware
-> ConversationConsumer.receive_json()
-> text validation
-> create_message() rechecks access and writes Message
-> message_payload() shapes output
-> channel-layer group_send()
-> consumer chat_message() sends JSON to connected group members
-> browser message listener
-> appendRealtimeMessage(), unless the ID is already displayed
```

The channel layer distributes events. Redis is one configured implementation,
not the durable Message database. Settings also offer an in-memory fallback:
finding Redis code does not prove the current deployment uses Redis.

`database_sync_to_async` adapts synchronous database work for the async
consumer. It does not turn that write into a separate durable job queue.

</details>

### 4.5 Ask Stronger Questions Than "Did It Work?"

Answer from source; mark which you also observed safely:

1. Why does login not authorize every conversation ID?
2. What stops a client choosing another user as sender?
3. Why can HTTP response and socket broadcast describe the same message?
4. Why check a durable message ID before inserting a bubble?
5. Does `chatRealtimeSend()` returning true prove server persistence?
6. Can a message exist in the database but not appear in this browser?

<details>
<summary>Checkpoint: boundaries and evidence</summary>

Authentication establishes identity; participant/block checks establish access
to this conversation. Server-assigned ownership avoids trusting a client
sender field.

The HTTP path also broadcasts, so two delivery paths can race. Checking the
message ID prevents duplicate insertion. The realtime helper returning true
only establishes that local conditions passed and `send()` was called, not
server persistence or recipient receipt.

A browser might be disconnected, showing an older/search page or encountering
a render failure. Stored, broadcast and displayed are different milestones.
Find the first failing boundary rather than treating them as one event.

</details>

Optional investigation: compare blank-text and length validation in both
paths. Search for `5000`, then inspect the form/model too. Do not assume a
frontend helper protects every server entry point. Record checks you found
and checks you did not find; propose a focused test before declaring either
consistency or a defect.

### 4.6 Optional Runtime Observation

Only in an intentionally configured local/test environment:

- Open Network before sending a throwaway message.
- Inspect WebSocket frames for text sent with a ready socket.
- Inspect the HTTP POST/payload/JSON response for a small image send.
- Follow Initiator to the JavaScript that started each request.
- Compare IDs across HTTP response, socket event and rendered element.
- Inspect relevant server logs; never copy session cookies/tokens into notes.

An HTTP status alone is not a complete business result. Inspect the response
body and expected storage/UI effect. An open socket is not delivery proof.

## Session 5: Investigate Without the Walkthrough

Reduce the help. Choose one feature not traced above:

- Daynotes: Markdown import and its failure path.
- PDF Glue: duplicate/reorder entries and the resulting output order.
- Chat Lab: friend request acceptance or attachment-download permissions.
- Evidence Desk: backup restore, including screenshot IDs and restored workbooks.

Choose one, not all four.

### 5.1 Submit a Feature Trace

Copy into your own scratch notes, without changing application code:

```text
FEATURE / exact user action:
MY PREDICTION before opening code:

ENTRY: file + symbol + event/route:
INPUT: names, shapes and origin:
AUTHORIZATION / validation:
DECISIONS and alternate paths:
TRANSFORMATIONS: how data changes shape:
SIDE EFFECT: exact storage/file/API write:
RESULT: return value, response, event or callback:
UI: who displays success/failure:
ASYNC BOUNDARY: timer, promise, socket, thread or worker, if any:

ONE FAILURE PATH:
ONE IMPORTANT INVARIANT:
EVIDENCE: file/symbol for each important claim:
OBSERVED AT RUNTIME versus CODE-TRACED ONLY:
WHAT I STILL DO NOT KNOW:
```

An invariant is a rule that must remain true across operations. Examples:
editing does not extend a note's creation-based expiry; a merge never uses an
input as output; outsiders cannot read private conversation attachments.
Name the rule before choosing the test.

### 5.2 Make a Change Plan Without Making the Change

Choose a requirement:

> Imported Markdown should have a different allowed size.

Or:

> A failed operation should display a clearer error.

Before editing, answer:

1. What behavior changes, and what must stay unchanged?
2. Which symbols own the rule and the displayed message?
3. Are there alternate paths, such as CLI, HTTP or WebSocket?
4. Is the constraint enforced in several places?
5. Which data/configuration is affected?
6. What success, failure and boundary tests demonstrate the change?
7. How would you detect an unrelated regression?

If the plan is "replace every occurrence of this number/string," identify each
occurrence's responsibility first. Equal text does not guarantee equal meaning;
a visible validation check may not be the authoritative check.

Only implement a practice change in a disposable copy/branch when you choose
to do that exercise. Preserve unrelated edits and user data.

### 5.3 Simulate a Real Handover

Imagine receiving a new website repository. Produce a defensible first map:

```text
What problem does it solve?
Actual runnable app root(s), or monorepo?
What runs in browser, server, build step and worker?
What starts each process?
Required configuration names, without secret values?
Persistent data locations and ownership?
One user action traced completely?
External dependencies for that action?
Where failures appear; which logs/tests distinguish them?
Which conclusions are observed, deduced from code or guessed?
```

For each unknown, name the next file, search or safe observation that could
answer it. "Not verified; next I would inspect X" is stronger than pretending.

## Your Investigation Toolkit

### Identify the Stack With Evidence

| Clue | What it can tell you | What it does not prove |
| --- | --- | --- |
| `package.json` | Dependencies and named scripts | That Node is the production backend; it might only build static assets. |
| Lockfile | Resolved dependency versions | Which optional runtime/configuration branch is active. |
| `pyproject.toml` / `requirements.txt` | Python dependency declarations | That every library is used in this feature. |
| `manage.py` | Django management entry | The actual deployed database. |
| `index.html` + script tags | Browser entry/scripts | That no remote API is used by those scripts. |
| Docker/Compose/deployment config | Build/start processes and service wiring | That the current deployment matches this file. |
| `.env.example` | Expected configuration names | Real values or the selected environment. |
| Tests and lesson READMEs | Intended behavior/history | That current execution matches an older checkpoint. |

In an unfamiliar repository, locate manifests and entry candidates first:

```powershell
rg --files -g 'README*' -g 'package.json' -g 'pyproject.toml' -g 'requirements*.txt' -g 'manage.py' -g 'composer.json' -g 'Dockerfile*' -g '*compose*.yml' -g '*compose*.yaml' -g '!**/node_modules/**' -g '!**/.venv/**' -g '!**/vendor/**'
```

Then narrow to one app. Folder conventions vary; follow actual imports,
route registrations and startup scripts rather than assuming every project
has `controllers`, `services` and `models` directories.

### Follow Both Directions

From a visible label, find its template/component and follow its event or URL
forward. From a database/file write, find callers backward. The two directions
should meet in one feature trace.

Search distinctive IDs, routes, errors or function names, not generic `save`
across the whole repository. Exclude vendor/generated directories. Read one
caller and immediate callee before opening the next unrelated file.

### Distinguish the Milestones

```text
Callback registered != callback executed
Input visible != value persisted
Request started != request succeeded
HTTP success != downstream work completed
Job queued != worker finished
Socket open != message stored/delivered
Database row created != every browser updated
File hidden in UI != file deleted from storage
Test defined != test executed successfully
Dependency installed != service configured and used
```

When someone says "it worked," ask which milestone they observed.

### Debug the First Unproven Boundary

| Observation | Useful next check |
| --- | --- |
| Click has no visible effect | Event binding, disabled state, Console error, actual loaded version. |
| No HTTP request appears | Is it local-only or using an existing socket? Inspect the right transport. |
| Request fails before the view | Reachability, routing, authentication/CSRF and server logs. |
| Handler receives input but no data appears | Validation, authorization, rollback and correct database/environment. |
| Data exists but UI is wrong | Response payload, client state, rendering, pagination/filtering and duplicate suppression. |
| Queued work never finishes | Worker availability, job state, errors/retries and external dependencies. |
| Hosted and local versions differ | Actual URL, deployed commit/build, configuration and cached assets. |

These are hypotheses, not automatic diagnoses. Test the boundary before
modifying a nearby layer merely because its name looks suspicious.

### Common Traps

- Reading every file alphabetically without a feature question.
- Treating a function's name as proof of behavior.
- Finding a definition but never its caller/trigger.
- Following names while ignoring input/output data shapes.
- Ending at a database write without tracing the response/UI.
- Ending at a success label without proving persistence.
- Treating all async code as jobs or every queue as Redis.
- Assuming the current environment uses a default configuration branch.
- Assuming frontend validation protects every server entry point.
- Running unfamiliar scripts/migrations before checking environment safety.
- Asking for the entire app explanation before attempting a small trace.

## Practice and Progress Check

Repeat with one feature per session:

1. Predict its path before browsing the whole repository.
2. Find the entry and follow calls/data.
3. Resolve one uncertainty with code or a safe observation.
4. Explain aloud with the code closed.
5. Compare to source and correct one mistake.
6. Propose one change and the smallest convincing test.

Score each feature honestly:

| Level | What you can demonstrate |
| --- | --- |
| 0 | Recognize filenames but cannot connect them. |
| 1 | Find entry/handler and name likely storage. |
| 2 | Trace a successful action with actual symbols and data shapes. |
| 3 | Explain validation, ownership, failures and async boundaries with evidence. |
| 4 | Predict affected paths and design focused tests, then verify safely when appropriate. |

Reach Level 2 on Daynotes before adding frameworks. Then repeat on PDF Glue
and Chat Lab. Being stuck is useful when you can name the missing connection
and the evidence needed to resolve it.

### Your First Feature Trace After Session 2

Do only this before moving on:

> Trace typing `Milk` into a new Daynotes note, through the actual storage
> operation and back to Saved. Include the delay, the data changes and what
> happens if saving fails.

Write 6-12 lines in your own words, with filenames/function names. Mark any
step you cannot prove. Use the checkpoint after your first attempt. The goal
is to make the connections yourself and learn to verify them, not copy the
provided diagram.
