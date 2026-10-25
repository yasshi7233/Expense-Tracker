# Smart Spend — Personal Expense Tracker

> **A Production-Oriented Personal Expense Management System**  
> Built with Python, Flask, SQLAlchemy, PostgreSQL, Alembic, Flask-Login, and Flask-WTF.

---

## 1. Project Overview & Problem Statement

Managing personal income and expenses is a fundamental financial habit. However, many learners and young professionals struggle with:
1. Lack of clear visibility into where monthly money goes.
2. Inaccurate categorization and reliance on insecure, unformatted spreadsheets.
3. Complex, overloaded personal finance software filled with unnecessary distractions.

**Smart Spend** solves this by providing a clean, focused, modular web application that records daily incomes and expenditures, provides clear net savings metrics, visualizes category distributions and monthly trends through server-rendered charts, and allows safe CSV report downloads with anti-injection protection.

---

## 2. Key Features

1. **Authentication & Session Management**:
   - Secure user registration, login, and logout.
   - Salted password hashing using `werkzeug.security` (Scrypt / PBKDF2).
   - Session lifecycle handling and protected routes enforced via `Flask-Login`.
   - Strict multi-tenant user data isolation preventing Insecure Direct Object References (IDOR).

2. **Transactions CRUD**:
   - Full CRUD operations: Add, view, edit, and delete transactions.
   - Distinct classification of income vs. expense with fixed financial categories (`Food`, `Transport`, `Rent`, `Salary`, `Entertainment`, `Health`, `Other`).
   - Real-time search by note and category, type filtering, and multi-field table sorting.
   - Server-side pagination with responsive styling.
   - Exact numerical precision via SQLAlchemy `Numeric(12,2)` to avoid floating-point rounding errors.

3. **Financial Dashboard & Visual Charts**:
   - Live KPI cards: Total Income, Total Expenses, and Net Savings (`Income - Expenses`).
   - Filter by specific month or custom date range (`start_date` to `end_date`).
   - Server-rendered base64 charts powered by Matplotlib (`Agg` non-interactive backend):
     - **Spending by Category Pie Chart**: Visual percentage breakdown of expense categories.
     - **Monthly Cash Flow Bar Chart**: Multi-month comparison of income vs. expenses.
   - Graceful empty states when no records exist.

4. **Reports & Sanitized CSV Export**:
   - Dedicated Analytics report view with category metrics and net savings rate.
   - Export user transactions to standard CSV.
   - Formula injection protection: all exported cells beginning with `=`, `+`, `-`, or `@` are automatically sanitized.
   - User data isolation: exports strictly contain only the authenticated user's records.

---

## 3. Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend Framework** | Flask 3.x (Application Factory Pattern) | Modular architecture using Blueprints; clean separation of concerns. |
| **ORM / Data Access** | SQLAlchemy 2.x & Flask-SQLAlchemy | Strong typing, parameterized queries, exact `Numeric(12,2)` precision. |
| **Database Migrations** | Flask-Migrate & Alembic | Declarative, version-controlled schema migrations. |
| **Database** | SQLite (Local Dev / Tests), PostgreSQL (Production) | Lightweight local testing paired with production ACID compliance. |
| **Authentication & AuthZ** | Flask-Login & Werkzeug Security | Secure session cookies (`HttpOnly`, `SameSite=Lax`), salted password hashes. |
| **Forms & CSRF** | Flask-WTF & WTForms | Server-side validation and anti-CSRF token protection on all POST requests. |
| **Visualization** | Matplotlib (Agg backend) + HTML5 | High-resolution charts rendered server-side and encoded to base64. |
| **Testing** | Pytest | Fast, deterministic test suite using isolated in-memory SQLite fixtures. |
| **Production WSGI** | Gunicorn | Production-grade WSGI HTTP server for cloud deployments. |

---

## 4. Application Architecture & Folder Structure

The application adopts the **Flask Application Factory** pattern with modular Blueprints:

```text
Expense Tracker/
├── app/
│   ├── __init__.py                # Flask application factory (create_app)
│   ├── config.py                  # Dev / Testing / Prod configuration classes
│   ├── extensions.py              # Centralized extensions (db, migrate, login_manager, csrf)
│   ├── core/
│   │   ├── errors.py              # Custom HTTP 400, 403, 404, 500 error handlers
│   │   └── security.py            # CSV formula sanitization & safe redirect validator
│   ├── models/
│   │   ├── __init__.py            # Model exports (User, Transaction, CATEGORIES)
│   │   ├── user.py                # User model with salted password hashing
│   │   └── transaction.py         # Numeric(12,2) Transaction model
│   ├── auth/                      # Authentication Blueprint (login, signup, logout, profile)
│   ├── dashboard/                 # Financial Overview & period filtering Blueprint
│   ├── transactions/              # Transactions CRUD, search & CSV export Blueprint
│   ├── reports/                   # Monthly analytics & Matplotlib charts Blueprint
│   └── templates/                 # Modular Jinja2 templates (Clean Modern Theme)
│       ├── auth/                  # login.html, signup.html, profile.html
│       ├── dashboard/             # index.html, landing.html
│       ├── reports/               # summary.html
│       ├── transactions/          # index.html, add.html, edit.html
│       └── base.html              # Responsive layout with navigation & flash messages
├── migrations/                    # Alembic migration scripts
├── static/                        # Canonical static folder
│   ├── vendor/                    # Local vendor assets (Bootstrap 5, Bootstrap Icons)
│   ├── app.js                     # Interactive table sorting & client utilities
│   ├── style.css                  # Modern theme stylesheet
│   └── favicon.ico
├── tests/                         # Pytest test suite (17 passed)
│   ├── conftest.py                # Isolated SQLite test client fixtures
│   ├── test_architecture_and_demo.py # Factory registration, blueprint checks, demo seeder
│   ├── test_auth.py               # Signup, login, invalid credentials, logout
│   ├── test_authorization.py      # Multi-tenant data isolation & IDOR prevention
│   ├── test_dashboard_and_analytics.py # Period filters, net savings, empty states
│   ├── test_transactions_and_export.py # Add, edit, delete, CSV export security & isolation
│   └── test_validation_and_flash.py    # Form validation & negative amount defense
├── docs/
│   └── screenshots/               # Application UI screenshots
├── demo_seed.py                   # Safe, idempotent demo data seeder (4 months of data)
├── requirements.txt               # Locked dependencies
├── run.py                         # Production server entry point
├── app.py                         # Shell context provider & backwards-compatible entry point
├── charts.py                      # Matplotlib base64 chart generator
├── seed.py                        # Alternative dev data seeder
├── migrate_legacy.py              # Non-destructive legacy data upgrade utility
├── pytest.ini                     # Pytest configuration
├── .env.example                   # Environment variable template
└── .gitignore                     # Git exclusion rules
```

---

## 5. Database Schema

The database design adheres to 3NF relational normalization:

- **`users` Table**:
  - `id` (INTEGER, Primary Key)
  - `name` (VARCHAR(100), NOT NULL)
  - `email` (VARCHAR(120), UNIQUE, NOT NULL, Indexed)
  - `password_hash` (VARCHAR(255), NOT NULL)
  - `created_at` (DATETIME, UTC)
  - `updated_at` (DATETIME, UTC)

- **`transactions` Table**:
  - `id` (INTEGER, Primary Key)
  - `user_id` (INTEGER, Foreign Key -> `users.id` ON DELETE CASCADE, Indexed)
  - `date` (VARCHAR(10), NOT NULL, Indexed: `YYYY-MM-DD`)
  - `type` (VARCHAR(10), NOT NULL, Check: `type IN ('income', 'expense')`)
  - `category` (VARCHAR(50), NOT NULL)
  - `amount` (NUMERIC(12,2), NOT NULL, Check: `amount > 0`)
  - `note` (VARCHAR(255), DEFAULT '')
  - `created_at` (DATETIME, UTC)
  - `updated_at` (DATETIME, UTC)

---

## 6. Local Setup and Installation (Windows & VS Code)

### Prerequisites
- Python 3.10+ installed.
- Git installed.

### Step-by-Step Installation

1. **Clone the repository**:
   ```powershell
   git clone <repository-url>
   cd "Expense Tracker"
   ```

2. **Create and activate a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create your local `.env` from the provided template:
   ```powershell
   Copy-Item .env.example .env
   ```

5. **Apply Database Migrations**:
   ```powershell
   python migrate_legacy.py
   python -m flask --app run.py db upgrade
   ```

6. **Seed Realistic Demo Data**:
   ```powershell
   python demo_seed.py
   ```
   *Creates a demo account (`demo@test.com` / `demo123`) populated with 40 realistic transactions across 4 months.*

7. **Start the Development Server**:
   ```powershell
   python run.py
   ```
   Open your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## 7. Render Deployment

This repository includes [`render.yaml`](./render.yaml), which provisions a PostgreSQL
database, installs the dependencies, applies migrations, and starts Gunicorn on Render's
assigned `$PORT`.

To deploy:

1. Push the repository to GitHub.
2. In Render, choose **New > Blueprint** and select the repository.
3. Confirm the generated `SECRET_KEY` and PostgreSQL database resources.
4. Deploy the blueprint. Do not use `python app.py` as the production start command;
   use `gunicorn --bind 0.0.0.0:$PORT run:app`.

The `DATABASE_URL` environment variable must point to the Render PostgreSQL database.
SQLite is suitable for local development only because Render's web-service filesystem
is ephemeral.

---

## 8. Demo Account Instructions

To quickly evaluate and demo the project during interviews:

| Attribute | Demo Credential |
|---|---|
| **Login URL** | `http://127.0.0.1:5000/auth/login` |
| **Email** | `demo@test.com` |
| **Password** | `demo123` |
| **Data Scope** | 40 transactions spanning July 2026 to October 2026 |

> [!WARNING]
> This demo account is configured strictly for local development, testing, and portfolio demonstration. The sample password must never be used in a public production deployment.

---

## 9. Running the Automated Test Suite

Run the full Pytest test suite with:

```powershell
python -m pytest -v
```

### Verified Test Matrix (17 Passed)
- `tests/test_architecture_and_demo.py`:
  - `test_app_factory_and_blueprint_registration`: Validates factory initializes cleanly with only the 4 core Blueprints.
  - `test_demo_seeder_creates_user_and_transactions`: Validates creation of demo user and 40 transactions across 4 months.
  - `test_demo_seeder_idempotency_and_preservation`: Confirms repeat execution never creates duplicate records or resets passwords.
  - `test_demo_seeder_rejects_production_mode`: Asserts that production environments block demo seeding.
- `tests/test_auth.py`:
  - `test_signup_and_login`: User registration, hash verification, authentication flow.
  - `test_duplicate_email_rejected`: Duplicate email registration rejection.
  - `test_unauthenticated_access_redirects`: Route protection and login redirection.
  - `test_login_invalid_credentials`: Incorrect password handling and user flash feedback.
  - `test_logout`: Session teardown and logout redirect.
- `tests/test_authorization.py`:
  - `test_data_isolation_between_users`: Multi-tenant data isolation; prevents IDOR attacks (User B cannot view, edit, or delete User A's transactions).
- `tests/test_dashboard_and_analytics.py`:
  - `test_dashboard_period_filtering_and_net_savings`: Monthly and custom date range cash flow calculations.
  - `test_empty_dashboard_renders_cleanly`: Clean zero-state rendering without calculation errors.
- `tests/test_transactions_and_export.py`:
  - `test_transactions_add_and_list`: Transaction creation and tabular listing.
  - `test_csv_export_format_and_security`: CSV formula injection mitigation (`'` prefixing).
  - `test_csv_export_user_data_isolation`: Verifies that exported CSV contains only records owned by the requester.
  - `test_transactions_edit_and_delete`: Full update and delete lifecycle.
- `tests/test_validation_and_flash.py`:
  - `test_transaction_validation_errors`: Negative and zero amount prevention.

---

## 9. Application Screenshots

### 1. Financial Overview Dashboard
Displays monthly income, expenses, net savings KPI cards, recent transactions, and custom period filters.
*(Relative path: `docs/screenshots/dashboard.png`)*

```text
+--------------------------------------------------------------------------+
|  Smart Spend               Overview   Transactions   Analytics   [User]  |
+--------------------------------------------------------------------------+
|  Financial Overview                                                      |
|  Showing cash flow summary for 2026-10                                   |
|                                                                          |
|  [ Total Income ]        [ Total Expenses ]       [ Net Savings ]        |
|  Rs. 30,500.00           Rs. 11,890.00            Rs. 18,610.00          |
|                                                                          |
|  [ Spending by Category ]             [ Monthly Cash Flow Trend ]        |
|  (Matplotlib Pie Chart)               (Income vs Expense Bar Chart)      |
+--------------------------------------------------------------------------+
```

### 2. Monthly Analytics & Reports
Displays category breakdown percentages with visual progress bars and server-rendered charts.
*(Relative path: `docs/screenshots/analytics.png`)*

### 3. Authentication & Sign In
Clean login form with CSRF protection, error flash alerts, and direct sign-up navigation.
*(Relative path: `docs/screenshots/login.png`)*

> [!NOTE]
> To update or save high-resolution PNG screenshots into `docs/screenshots/`:
> 1. Start the app: `python run.py`.
> 2. Open `http://127.0.0.1:5000/auth/login` and capture `login.png`.
> 3. Log in with `demo@test.com` / `demo123`, capture the dashboard to `dashboard.png`.
> 4. Navigate to `http://127.0.0.1:5000/reports/` and capture `analytics.png`.

---

## 10. Future Improvements (Clearly Labeled as Future Scope)

The following capabilities are intentional future enhancements beyond the current core scope:
1. **Automated Category Tagging**: Machine learning or rule-based auto-categorization based on transaction notes.
2. **Multi-Currency Support**: Real-time currency conversions and multi-currency wallets.
3. **Advanced Export Formats**: PDF statement summary downloads alongside CSV export.
4. **Email Reminders & Alerts**: Automated email notifications when monthly expenses exceed a user-defined threshold.
