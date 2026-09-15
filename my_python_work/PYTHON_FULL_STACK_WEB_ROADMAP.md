# Python Full-Stack Web Roadmap

This roadmap is for building real web apps with Python as the main world.

The target is:

```text
Python + Django + PostgreSQL + Django templates + HTMX
```

This path can replace most of what a Next.js ecommerce app gave you, while keeping your brain mostly in Python.

## Important Truth

A browser still uses:

- HTML
- CSS
- JavaScript

But you do not need to live in React/Next.js to build useful web apps.

Our future web stack:

- Backend: Django
- Language: Python
- Database: PostgreSQL
- Frontend: Django templates
- Interactivity: HTMX and small JavaScript only when needed
- Styling: Bootstrap first, Tailwind later if wanted
- Auth: Django auth, then Google login later
- Payments: Stripe first, PayPal later
- Email: Django email templates with SMTP or Resend
- Admin: Django Admin, then custom dashboard

## Old Next.js Stack To Python Map

| Old Stack | Python Path |
| --- | --- |
| Next.js App Router | Django URLs and views |
| React components | Django templates and partials |
| TypeScript / TSX | Python type hints, Django forms, Pydantic later |
| Tailwind / shadcn/ui | Bootstrap first, Tailwind later |
| Radix UI | Django templates + simple accessible HTML |
| lucide-react | SVG/icons, icon libraries, or simple UI icons |
| MongoDB / Mongoose | PostgreSQL + Django ORM |
| NextAuth/Auth.js | Django auth + django-allauth later |
| bcrypt password hashing | Django built-in password hashing |
| Zustand cart state | Django sessions or database cart |
| React Hook Form + Zod | Django Forms / ModelForms |
| Stripe / PayPal | Stripe Python SDK / PayPal API |
| Resend + React Email | Django email templates + SMTP/Resend |
| Recharts dashboard | Chart.js, server summaries, or custom dashboard |
| Admin dashboard | Django Admin + custom admin pages |

## Learning Order

Do this after:

- OOP deep dive
- Practical design patterns
- Ultimate Python review

Then start web slowly.

Tiny early start:

- `my_python_work/web_practice/01_web_foundations/simple_server.py`

This file is allowed before the big review because it teaches the basic browser/server idea without adding Django complexity yet.

## Phase 1: Web Foundations

Goal: understand what a web app really is.

Files:

- `my_python_work/web_practice/README.md`
- `my_python_work/web_practice/01_web_foundations/simple_server.py`

Learn:

- What a browser does
- What a server does
- HTTP request and response
- URLs and routes
- GET vs POST
- Status codes
- HTML forms
- Query parameters
- Cookies
- Sessions
- Static files
- Media uploads

Practice:

- Build a tiny page.
- Submit a form.
- Show submitted data.
- Store something in a session.

You are ready to move on when:

- You can explain what happens after clicking a form submit button.
- You know why GET is for reading and POST is for changing data.

## Phase 2: Django Basics

Goal: build simple pages with Django.

Learn:

- Django project vs Django app
- `settings.py`
- `urls.py`
- Views
- Templates
- Template inheritance
- Context data
- Static files
- Redirects
- Messages

Practice project:

```text
mini_notes_site
```

Features:

- Home page
- Notes list
- Add note form
- Detail page
- Delete note

You are ready to move on when:

- You can create a Django app.
- You can connect a URL to a view.
- You can send data from a view to a template.

## Phase 3: Django Models And Database

Goal: save real data in a database.

Learn:

- Models
- Fields
- Migrations
- Django ORM
- QuerySets
- `filter()`
- `get()`
- `create()`
- `update()`
- `delete()`
- ForeignKey relationships
- Many-to-many relationships
- Model methods
- Django Admin

Database path:

1. SQLite while learning
2. PostgreSQL for serious projects

Practice:

- Product model
- Category model
- Review model
- Order model

You are ready to move on when:

- You can create models and run migrations.
- You can query data without writing SQL directly.
- You can edit data in Django Admin.

## Phase 4: Forms And Validation

Goal: safely accept user input.

Learn:

- Django Forms
- ModelForms
- Field validation
- Custom validation
- Error messages
- Cleaned data
- CSRF protection
- Form redirects

Practice:

- Product review form
- Contact form
- Edit profile form
- Add to cart form

You are ready to move on when:

- You can build a form that saves valid data.
- You can show useful errors for invalid data.

## Phase 5: Auth And Accounts

Goal: support real users.

Learn:

- User model basics
- Register
- Login
- Logout
- Password reset
- Permissions
- Groups
- Profile model
- Staff/admin users
- Google login later with django-allauth

Practice:

- Register page
- Login page
- Account page
- Order history page
- Admin-only product page

You are ready to move on when:

- You can protect a page so only logged-in users can see it.
- You can show different UI for normal users and staff users.

## Phase 6: Styling And Frontend Without React

Goal: make useful interfaces without drowning in frontend complexity.

Learn:

- Template partials
- Base layout
- Navigation
- Tables
- Cards
- Forms
- Pagination UI
- Bootstrap first
- Tailwind later if wanted
- HTMX basics

HTMX is useful for:

- Search without full page reload
- Add to cart without full page reload
- Inline edit
- Filter product list
- Load more products

Practice:

- Product grid
- Product search
- Category filter
- Cart quantity update

You are ready to move on when:

- You can build a clean Django template page.
- You can reuse layout pieces.
- You understand that not every interaction needs React.

## Phase 7: Ecommerce Core

Goal: build the main store features.

Learn and build:

- Product catalog
- Product detail page
- Categories
- Product images
- Search
- Filtering
- Sorting
- Pagination
- Cart
- Checkout
- Order creation
- Order status
- Inventory
- Reviews
- Coupons
- Shipping address
- Billing address
- Tax/shipping calculation basics

Practice project:

```text
django_marketplace
```

Minimum features:

- Browse products
- View product detail
- Add to cart
- Update cart quantity
- Checkout
- Place order
- View order history

You are ready to move on when:

- You can explain the difference between cart and order.
- You can create an order from cart items.
- You can reduce inventory after purchase.

## Phase 8: Payments

Goal: take payment safely.

Start with:

- Stripe Checkout

Learn:

- Payment session
- Success URL
- Cancel URL
- Webhooks
- Payment status
- Idempotency idea
- Never trusting the browser for payment success

Later:

- PayPal
- Cash on delivery
- Local payment methods if needed

Practice:

- Create Stripe checkout session.
- Handle successful payment webhook.
- Mark order as paid only after trusted confirmation.

You are ready to move on when:

- You understand why payment confirmation should happen server-side.
- You can connect an order to a payment status.

## Phase 9: Email

Goal: send useful transactional emails.

Learn:

- Django email settings
- SMTP
- Resend later if wanted
- Email templates
- Purchase receipt email
- Password reset email
- Order shipped email

Practice:

- Send receipt after successful order.
- Send admin notification after new order.

You are ready to move on when:

- You can send an email from Django.
- You can render an email using order data.

## Phase 10: Admin And Analytics

Goal: manage the business side.

Learn:

- Django Admin customization
- Admin list display
- Search fields
- Filters
- Custom admin actions
- Dashboard views
- Revenue summaries
- Order summaries
- Product performance
- CSV export
- Basic charts

Practice:

- Total revenue this month
- Orders by status
- Top products
- Low-stock products
- Sales CSV export

You are ready to move on when:

- You can manage products/orders from admin.
- You can create a simple dashboard summary.

## Phase 11: Testing

Goal: stop being afraid of changes.

Learn:

- Model tests
- Form tests
- View tests
- Auth tests
- Cart tests
- Checkout tests
- Payment webhook tests
- Factory data

Practice:

- Test product creation.
- Test cart total.
- Test login required pages.
- Test order creation.

You are ready to move on when:

- You can run tests before changing important code.
- You can test the important business rules.

## Phase 12: Security

Goal: avoid common web app mistakes.

Learn:

- CSRF
- XSS
- SQL injection
- Password hashing
- Environment variables
- Secret keys
- Debug mode off in production
- Allowed hosts
- Secure cookies
- File upload validation
- User permissions
- Rate limiting basics

Practice:

- Move secrets into `.env`.
- Protect admin-only views.
- Validate uploads.
- Check that users cannot see other users' orders.

You are ready to move on when:

- You can explain why user input cannot be trusted.
- You can protect pages by login and permission.

## Phase 13: Deployment

Goal: put the app online.

Learn:

- Environment variables
- Production settings
- PostgreSQL in production
- Static files
- Media files
- Domain
- HTTPS
- Backups
- Logging
- Error pages
- Deployment platform basics

Possible deployment paths:

- Render
- Railway
- Fly.io
- VPS later

Practice:

- Deploy a small Django app.
- Add a production database.
- Upload static files correctly.

You are ready to move on when:

- You can deploy without hardcoding secrets.
- You can explain where static files and media files go.

## Phase 14: Performance And Maintenance

Goal: keep the app fast and healthy.

Learn:

- Pagination
- Database indexes
- `select_related`
- `prefetch_related`
- Caching basics
- Avoiding N+1 queries
- Background tasks later
- Logging
- Backups
- Error monitoring

Practice:

- Add pagination to products.
- Optimize product list queries.
- Cache category list.
- Add backup habit.

You are ready to move on when:

- You can notice slow queries.
- You can explain why loading everything at once is bad.

## Design Patterns To Use In Web Apps

Use these after OOP:

1. Repository pattern
2. Strategy pattern
3. Factory pattern
4. Command pattern
5. Adapter pattern

How they fit Django:

- Repository: separate data access when app logic grows
- Strategy: choose search, discount, shipping, or payment behavior
- Factory: create objects from form/API/payment data
- Command: organize actions like checkout, refund, export
- Adapter: connect external APIs like Stripe, PayPal, Resend

Most important for us:

```text
Repository + Strategy
```

## First Big Python Web Project

Build this first:

```text
mini_store
```

Features:

- Product list
- Product detail
- Search
- Category filter
- Cart with session
- Checkout form
- Fake order placement
- Order history
- Admin product management

Do not add payments first.

Add payments only after the fake checkout flow makes sense.

## Full Ecommerce Project Later

Build this after `mini_store`:

```text
django_marketplace
```

Features:

- Product catalog
- Product variants
- Images
- Cart
- Checkout
- Stripe
- PayPal later
- User accounts
- Orders
- Reviews
- Coupons
- Admin dashboard
- Receipt emails
- CSV exports
- Basic analytics
- Deployment

## What Not To Learn Yet

Do not start with:

- React
- Next.js
- TypeScript
- GraphQL
- Microservices
- Kubernetes
- Complex frontend state managers

These can come later if needed.

For now, the goal is:

```text
Become dangerous with Python + Django first.
```

## Success Checkpoint

You are full-stack Python comfortable when you can:

- Build models
- Create pages
- Handle forms
- Save data
- Authenticate users
- Build cart/checkout flow
- Send emails
- Take payments
- Write tests
- Deploy the app
- Debug production-style problems

This is a big path, but it is one path. That is the point.
