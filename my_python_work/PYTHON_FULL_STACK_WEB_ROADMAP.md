# Python Full-Stack Web Roadmap

This roadmap is for building real web apps with Python as the main world.

The target is:

```text
Python + Django + PostgreSQL + Django templates + HTMX
```

This path can teach the same serious full-stack skills you used in a Next.js ecommerce app, but through a lighter personal dictionary app that is more useful to you.

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
- Payments: optional later in a tiny checkout lab, not in the main dictionary app
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

- `my_python_work/web_practice/01_web_foundations/01_request_response/simple_server.py`
- `my_python_work/web_practice/01_web_foundations/02_get_query_products/app.py`
- `my_python_work/web_practice/01_web_foundations/03_post_json_guestbook/app.py`
- `my_python_work/web_practice/01_web_foundations/04_cookies_sessions_cart/app.py`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/app.py`
- `my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/app.py`
- `my_python_work/web_practice/01_web_foundations/07_sqlite_database_basics/app.py`
- `my_python_work/web_practice/01_web_foundations/08_database_search_pagination/app.py`
- `my_python_work/web_practice/01_web_foundations/09_better_search_ranking/app.py`
- `my_python_work/web_practice/01_web_foundations/10_file_uploads_media/app.py`
- `my_python_work/web_practice/02_django_basics/01_setup_django_environment/check_setup.py`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py`
- `my_python_work/web_practice/02_django_basics/03_first_django_app/README.md`
- `my_python_work/web_practice/02_django_basics/04_django_templates/README.md`
- `my_python_work/web_practice/02_django_basics/05_django_static_files/README.md`
- `my_python_work/web_practice/02_django_basics/06_django_forms/README.md`
- `my_python_work/web_practice/02_django_basics/07_django_models_migrations/README.md`
- `my_python_work/web_practice/02_django_basics/08_save_words_to_database/README.md`
- `my_python_work/web_practice/02_django_basics/09_word_detail_404/README.md`

These files are allowed before the big review because they teach the basic browser/server idea without adding Django complexity yet.

## Phase 1: Web Foundations

Goal: understand what a web app really is.

Files:

- `my_python_work/web_practice/README.md`
- `my_python_work/web_practice/01_web_foundations/01_request_response/README.md`
- `my_python_work/web_practice/01_web_foundations/01_request_response/simple_server.py`
- `my_python_work/web_practice/01_web_foundations/02_get_query_products/README.md`
- `my_python_work/web_practice/01_web_foundations/02_get_query_products/app.py`
- `my_python_work/web_practice/01_web_foundations/03_post_json_guestbook/README.md`
- `my_python_work/web_practice/01_web_foundations/03_post_json_guestbook/app.py`
- `my_python_work/web_practice/01_web_foundations/04_cookies_sessions_cart/README.md`
- `my_python_work/web_practice/01_web_foundations/04_cookies_sessions_cart/app.py`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/README.md`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/app.py`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/templates/base.html`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/templates/home.html`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/templates/products.html`
- `my_python_work/web_practice/01_web_foundations/05_templates_static_files/static/styles.css`
- `my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/README.md`
- `my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/app.py`
- `my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/templates/base.html`
- `my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/templates/products.html`
- `my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/templates/product_detail.html`
- `my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/templates/not_found.html`
- `my_python_work/web_practice/01_web_foundations/06_dynamic_routes_404/static/styles.css`
- `my_python_work/web_practice/01_web_foundations/07_sqlite_database_basics/README.md`
- `my_python_work/web_practice/01_web_foundations/07_sqlite_database_basics/app.py`
- `my_python_work/web_practice/01_web_foundations/08_database_search_pagination/README.md`
- `my_python_work/web_practice/01_web_foundations/08_database_search_pagination/app.py`
- `my_python_work/web_practice/01_web_foundations/09_better_search_ranking/README.md`
- `my_python_work/web_practice/01_web_foundations/09_better_search_ranking/app.py`
- `my_python_work/web_practice/01_web_foundations/10_file_uploads_media/README.md`
- `my_python_work/web_practice/01_web_foundations/10_file_uploads_media/app.py`

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
- SQLite database basics
- Database search, filtering, and pagination
- Better search and ranking
- Media uploads

Practice:

- Build a tiny page.
- Submit a form.
- Show submitted data.
- Store something in a session.
- Upload and list a small file.

You are ready to move on when:

- You can explain what happens after clicking a form submit button.
- You know why GET is for reading and POST is for changing data.

## Phase 2: Django Basics

Goal: build simple pages with Django.

Files:

- `my_python_work/web_practice/02_django_basics/01_setup_django_environment/README.md`
- `my_python_work/web_practice/02_django_basics/01_setup_django_environment/check_setup.py`
- `my_python_work/web_practice/02_django_basics/01_setup_django_environment/requirements.txt`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/README.md`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/manage.py`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/mini_site/settings.py`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/mini_site/urls.py`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/pages/apps.py`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/pages/urls.py`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/pages/views.py`
- `my_python_work/web_practice/02_django_basics/03_first_django_app/README.md`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/pages/templates/pages/base.html`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/pages/templates/pages/home.html`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/pages/templates/pages/about.html`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/pages/static/pages/styles.css`
- `my_python_work/web_practice/02_django_basics/04_django_templates/README.md`
- `my_python_work/web_practice/02_django_basics/05_django_static_files/README.md`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/pages/forms.py`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/pages/templates/pages/word_form.html`
- `my_python_work/web_practice/02_django_basics/06_django_forms/README.md`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/dictionary/models.py`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/dictionary/admin.py`
- `my_python_work/web_practice/02_django_basics/02_first_django_project/dictionary/migrations/0001_initial.py`
- `my_python_work/web_practice/02_django_basics/07_django_models_migrations/README.md`

Learn:

- Virtual environment basics
- Installing Django
- Checking the Django version
- Creating the first Django project
- Django project vs Django app
- Creating the first Django app
- `settings.py`
- `urls.py`
- Views
- Templates
- Template inheritance
- Context data
- Django forms
- `request.POST`
- `form.cleaned_data`
- Static files
- Models
- Migrations
- Django Admin registration
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

- Word model
- Category model
- Tag model
- Example sentence model
- Review/practice history model

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

- Add word form
- Edit word form
- Search/filter form
- Contact form
- Edit profile form

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
- Mark favorite without full page reload
- Mark reviewed without full page reload
- Inline edit
- Filter word list
- Load more words

Practice:

- Word grid
- Word search
- Category filter
- Favorite/review status update

You are ready to move on when:

- You can build a clean Django template page.
- You can reuse layout pieces.
- You understand that not every interaction needs React.

## Phase 7: Personal Dictionary Core

Goal: build the main dictionary features.

Learn and build:

- Word list
- Word detail page
- Categories
- Tags
- Optional word image/audio
- Search
- Filtering
- Sorting
- Pagination
- Fuzzy search
- Favorites
- Private words per user
- Import/export
- Review/practice mode
- Admin word management

Practice project:

```text
django_dictionary
```

Minimum features:

- Browse words
- View word detail
- Add/edit/delete words
- Search and filter words
- Mark favorites
- Export words
- Use Django Admin for cleanup

You are ready to move on when:

- You can explain model, form, view, template, and URL flow.
- You can protect a user's private words.
- You can search and filter saved database records.

## Phase 8: Import, Export, And Review Workflow

Goal: make the dictionary useful every day.

Learn:

- CSV import
- CSV export
- JSON backup
- Favorites
- Review status
- Due-for-review filtering
- Safer user-owned data

Practice:

- Import old words from CSV or JSON.
- Export your dictionary backup.
- Build a simple review/practice page.

You are ready to move on when:

- You can move data in and out safely.
- You can build a small workflow around saved records.

## Phase 8.5: Optional Mini Checkout Lab

Goal: learn the ecommerce-specific systems without turning our main project into a giant store.

Project:

```text
mini_checkout_lab
```

Learn:

- Cart
- Checkout form
- Shipping address
- Billing address
- Order model
- Order items
- Order status
- Fake payment status
- Receipt email
- Stripe later if needed
- Never trusting the browser for payment success

Practice:

- Add simple items to a cart.
- Convert cart items into an order.
- Save shipping/contact details.
- Mark an order as pending/paid/cancelled.
- Send or preview a receipt email.

You are ready to move on when:

- You can explain cart vs order.
- You understand why payment confirmation must happen server-side.
- You know how shipping/payment concepts map to database models.

## Phase 9: Email

Goal: send useful transactional emails.

Learn:

- Django email settings
- SMTP
- Resend later if wanted
- Email templates
- Dictionary backup/export email
- Review reminder email
- Optional checkout receipt email
- Password reset email

Practice:

- Send a dictionary export email.
- Send a review reminder email.
- Send a checkout receipt later if we build `mini_checkout_lab`.

You are ready to move on when:

- You can send an email from Django.
- You can render an email using saved app data.

## Phase 10: Admin And Analytics

Goal: manage the business side.

Learn:

- Django Admin customization
- Admin list display
- Search fields
- Filters
- Custom admin actions
- Dashboard views
- Dictionary growth summaries
- Review progress summaries
- Word/category performance
- CSV export
- Basic charts

Practice:

- Total words added this month
- Words by category
- Due-for-review count
- Most reviewed words
- Dictionary CSV export

You are ready to move on when:

- You can manage words/categories/review data from admin.
- You can create a simple dashboard summary.

## Phase 11: Testing

Goal: stop being afraid of changes.

Learn:

- Model tests
- Form tests
- View tests
- Auth tests
- Search tests
- Permission tests
- Import/export tests
- Optional checkout tests later
- Factory data

Practice:

- Test word creation.
- Test private word protection.
- Test login required pages.
- Test search results.

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
- Check that users cannot see other users' private words.

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

- Add pagination to words.
- Optimize word list queries.
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
- Strategy: choose search, review, import/export, or optional payment behavior
- Factory: create objects from form/API/import data
- Command: organize actions like import, export, review, and backup
- Adapter: connect external APIs like email, dictionary APIs, or Resend

Most important for us:

```text
Repository + Strategy
```

## First Big Python Web Project

Build this first:

```text
django_dictionary
```

Features:

- Word list
- Word detail
- Add/edit/delete words
- Search
- Category/tag filter
- Fuzzy search
- Favorites
- User login
- Private words per user
- Import/export
- Review/practice mode
- Admin word management

Do not add payments.

Payments belong to a future ecommerce project, not this lightweight dictionary path.

## Skill Coverage Map

Main project:

```text
django_dictionary
```

Teaches:

- CRUD
- database models
- forms and validation
- auth and permissions
- user-owned private data
- search/filter/sort/pagination
- fuzzy search
- import/export
- file/media uploads
- admin dashboards
- tests
- deployment
- security
- performance

Optional small lab:

```text
mini_checkout_lab
```

Teaches:

- cart
- checkout
- shipping address
- billing address
- orders
- order status
- fake payment
- Stripe later if needed
- receipt email

This keeps the main road light while still covering the business systems a dictionary app does not naturally need.

## Optional Ecommerce Project Later

Only build this later if you actually want ecommerce again:

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
- Build a useful user-owned workflow
- Send emails
- Import/export data
- Write tests
- Deploy the app
- Debug production-style problems

This is a big path, but it is one path. That is the point.
