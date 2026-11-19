understand the application flow end-to-end."

usually mean:

✅ Know the major features

✅ Know how data moves through the system

✅ Know which frontend components call which APIs

✅ Know which APIs talk to which database tables

✅ Be able to trace a user action from start to finish

✅ Be able to debug issues anywhere in that flow

=========

You have built three major web applications and several smaller tools.
The meaningful project count is:
Group	Projects
Major applications	10
Web foundation mini-apps	10
Django dictionary checkpoints	35
Checkout checkpoints	24
Chat lessons	23 conceptual lessons
Side quests	3
DSA/OOP practice tracks	2


The 10 substantial applications are:
1. Personal Dictionary
2. Shopping List App
3. Expense Tracker
4. File Organizer
5. Django Dictionary
6. Mini Checkout Lab
7. Chat Lab
8. Ecommerce Profit Calculator
9. Bookmark Metadata Collector
10. Browser Metadata Collector
The overall application flow is:
User action
    ↓
Frontend: browser form, JavaScript, or Tkinter UI
    ↓
Route/handler: Django view, WebSocket consumer, or Python function
    ↓
Validation: forms, permissions, CSRF, input checks
    ↓
Business logic
    ↓
Database / file storage / external API
    ↓
Response or real-time broadcast
    ↓
UI updates
For the Dictionary app:
Form submission
→ Django view
→ form validation
→ Word model
→ SQLite/PostgreSQL
→ redirect and success message
For Checkout:
Product page
→ session cart
→ checkout form
→ Order and OrderItem rows
→ payment provider
→ callback
→ payment verification
→ mark order paid
→ email or fulfillment
For bKash specifically:
Grant token
→ create payment
→ redirect customer to bKash
→ customer enters PIN
→ callback returns to Django
→ execute payment
→ verify amount, invoice, currency, and status
→ mark order paid
For Chat Lab:
Login
→ participant permission check
→ conversation page
→ text sent through WebSocket
→ Channels consumer
→ Message database row
→ Redis broadcasts event
→ connected browsers update instantly
Attachments use a different path:
Image upload
→ HTTP multipart request
→ Django view
→ MessageAttachment database row
→ image file storage
→ authorized preview/download
That difference explains why text became real-time before attachments.
The browser metadata side quest follows:
URL/bookmark file
→ URL parser
→ Playwright opens Edge
→ Edge renders page
→ app reads page DOM
→ metadata record
→ editable Markdown
→ saved file
The main project documentation is here:
- [Web Practice](C:/Users/ASUS/Desktop/python-new/my_python_work/web_practice/README.md)
- [Mini Checkout Lab](C:/Users/ASUS/Desktop/python-new/my_python_work/web_practice/03_mini_checkout_lab/README.md)
- [Chat Lab](C:/Users/ASUS/Desktop/python-new/my_python_work/web_practice/04_chat_lab/README.md)
- [Browser Metadata Collector](C:/Users/ASUS/Desktop/python-new/my_python_work/my_python_work/side_quests/browser_metadata_collector/README.md)

=========