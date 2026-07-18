# Banking Web Application — Implementation Plan

> **Status:** Planning Document — No code has been written yet.
> This document covers architecture, folder structure, module breakdown, and development roadmap only.

---

## 1. Solution Overview

### Objective
Build a simple, browser-based Banking Web Application that allows customers to securely log in, view their account balance, deposit funds, withdraw funds, and log out — all through a clean, responsive interface backed by a lightweight Python API and a local SQLite database.

### Scope
| In Scope | Out of Scope |
|---|---|
| Customer login / logout | Admin portal |
| View account balance | Multi-currency support |
| Deposit & withdrawal transactions | Inter-bank transfers |
| Session management | Email / SMS notifications |
| Responsive UI (Bootstrap) | Mobile native app |
| SQLite persistence | Production-grade database (PostgreSQL, MySQL) |

### Users
- **Bank Customer** — the sole actor in this application. Authenticates with credentials and performs self-service account operations.

### Functional Requirements
1. A customer can log in with a username and password.
2. A logged-in customer is redirected to a personal dashboard.
3. The dashboard displays the customer's current account balance.
4. A customer can deposit a positive monetary amount; the balance updates immediately.
5. A customer can withdraw a monetary amount not exceeding the current balance; the balance updates immediately.
6. A customer can log out, terminating the active session.
7. Unauthenticated requests to protected pages are redirected to the login page.

### Non-Functional Requirements
- **Security** — Passwords must be stored hashed (not plaintext). Sessions must be invalidated on logout.
- **Usability** — All pages must render correctly on desktop and tablet viewports using Bootstrap's responsive grid.
- **Simplicity** — The stack must remain minimal: HTML + Bootstrap, Python Flask, SQLite. No JavaScript frameworks.
- **Portability** — The application must run locally with a single `flask run` command and no external services.

### Assumptions
- A single SQLite database file is sufficient for this workshop context; no concurrent write contention is expected.
- User accounts are pre-seeded (registration is out of scope).
- HTTPS / TLS termination is out of scope; the app runs on `localhost`.
- Flask's built-in development server is acceptable for this workshop.

---

## 2. High-Level Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          FRONTEND  (FRONTEND/)                           │   │
│  │  HTML templates rendered by Flask (Jinja2)               │   │
│  │  Bootstrap 5 for layout, forms, and responsive design    │   │
│  └───────────────────┬──────────────────────────────────────┘   │
└──────────────────────│──────────────────────────────────────────┘
                       │  HTTP Request (form POST / GET)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND  (BACKEND/)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Flask Application                                       │   │
│  │  • Route handlers (views)                                │   │
│  │  • Session management (Flask session / secret key)       │   │
│  │  • Business logic (auth, deposit, withdrawal validation) │   │
│  │  • Password hashing (Werkzeug)                           │   │
│  └───────────────────┬──────────────────────────────────────┘   │
└──────────────────────│──────────────────────────────────────────┘
                       │  SQL queries via sqlite3 / SQLAlchemy
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE  (BACKEND/)                         │
│  SQLite file (bank.db)                                          │
│  • Stores customer credentials and account balances             │
└─────────────────────────────────────────────────────────────────┘
```

### Frontend → Backend → Database Interaction

```
Browser ──[GET /dashboard]──► Flask Route ──[query balance]──► SQLite
                                                                   │
Browser ◄──[render dashboard.html + balance]──────────────────────┘

Browser ──[POST /deposit  {amount}]──► Flask Route ──[UPDATE balance]──► SQLite
Browser ◄──[redirect → /dashboard]──────────────────────────────────────────┘
```

### Request Lifecycle
1. **Browser** sends an HTTP request (GET page load or POST form submission).
2. **Flask router** matches the URL to a view function.
3. The view function checks the **session** for an authenticated user; redirects to `/login` if absent.
4. The view function calls a **service/helper** function to execute business logic and interact with **SQLite**.
5. SQLite returns the result; the service function returns data to the view.
6. The view function renders a **Jinja2 HTML template** from `FRONTEND/templates/` and returns the HTTP response.

---

## 3. Component Design

### Frontend Responsibilities
- Provide HTML pages (Jinja2 templates) for: Login, Dashboard, Deposit, Withdraw.
- Use Bootstrap 5 for responsive layout, form styling, and navigation bar.
- Display flash messages (success / error feedback) returned by the backend.
- Submit user input to backend routes via standard HTML form `POST`.
- No client-side business logic — all validation happens on the backend.

### Backend Responsibilities
- Expose URL routes for every user-facing action (login, dashboard, deposit, withdraw, logout).
- Authenticate users and manage session state via Flask's signed-cookie session.
- Hash and verify passwords using Werkzeug's security utilities.
- Enforce business rules (positive deposit amounts, sufficient balance for withdrawals).
- Query and mutate the SQLite database in response to validated requests.
- Pass data and flash messages to templates for rendering.

### Database Responsibilities
- Persist customer account information (credentials, balance) in a single SQLite file.
- Serve as the single source of truth for balance state.
- The database file lives inside `BACKEND/` and is created/seeded at application startup if absent.

---

## 4. Folder Structure

```
banking-workshop/
│
├── FRONTEND/                        # All browser-facing assets
│   ├── templates/                   # Jinja2 HTML templates (rendered by Flask)
│   │   ├── base.html                # Shared layout: navbar, flash messages, Bootstrap CDN
│   │   ├── login.html               # Login form page
│   │   ├── dashboard.html           # Balance display + action buttons
│   │   ├── deposit.html             # Deposit form page
│   │   └── withdraw.html            # Withdrawal form page
│   └── static/                      # Static assets served directly
│       ├── css/
│       │   └── custom.css           # Minor overrides on top of Bootstrap
│       └── images/
│           └── logo.png             # Bank logo (optional)
│
├── BACKEND/                         # Python Flask application
│   ├── app.py                       # Application entry point; Flask app factory / runner
│   ├── routes/                      # URL route handlers (views), one file per feature area
│   │   ├── auth.py                  # /login, /logout routes
│   │   ├── dashboard.py             # /dashboard route
│   │   └── transactions.py          # /deposit, /withdraw routes
│   ├── services/                    # Business logic, decoupled from HTTP layer
│   │   ├── auth_service.py          # Password hashing, credential verification
│   │   └── account_service.py       # Balance retrieval, deposit/withdraw logic
│   ├── db.py                        # SQLite connection helper + seed data loader
│   ├── bank.db                      # SQLite database file (auto-created at runtime)
│   └── requirements.txt             # Python dependencies (flask, werkzeug)
│
├── IMPLEMENTATION_PLAN.md           # This document
└── README.md                        # Setup and run instructions
```

### Responsibility of Each Folder / File

| Path | Responsibility |
|---|---|
| `FRONTEND/templates/` | Jinja2 HTML pages served by Flask; no business logic |
| `FRONTEND/static/` | CSS overrides and images; served as-is by Flask |
| `BACKEND/app.py` | Creates the Flask app, registers blueprints, sets config |
| `BACKEND/routes/` | Thin HTTP layer — receives requests, calls services, renders templates |
| `BACKEND/services/` | Pure-Python business logic; no Flask imports; easily unit-tested |
| `BACKEND/db.py` | SQLite connection management and optional seed data |
| `BACKEND/bank.db` | Runtime SQLite database file |
| `BACKEND/requirements.txt` | Pinned Python dependencies |

---

## 5. Module Breakdown

### 5.1 Authentication Module
**Goal:** Allow customers to identify themselves and protect all other pages from unauthenticated access.

| Concern | Detail |
|---|---|
| Routes | `GET /login`, `POST /login`, `GET /logout` |
| Frontend | `login.html` — username + password form, error flash message |
| Backend | `routes/auth.py` — handles form submission, calls `auth_service` |
| Service | `auth_service.py` — fetches user record, verifies hashed password, writes/clears session |
| Session key | `session['user_id']` stored in Flask's signed-cookie session |
| Guard | A `login_required` decorator (or helper) in `routes/` redirects to `/login` if session is absent |

### 5.2 Dashboard Module
**Goal:** Give the authenticated customer a central landing page that displays their current balance and navigation to all actions.

| Concern | Detail |
|---|---|
| Route | `GET /dashboard` |
| Frontend | `dashboard.html` — balance display card, Deposit / Withdraw / Logout buttons |
| Backend | `routes/dashboard.py` — reads `session['user_id']`, calls `account_service.get_balance()` |
| Service | `account_service.py` — queries SQLite for the customer's current balance |

### 5.3 Account Management Module
**Goal:** Provide read access to account state; serves as the data layer shared by the Dashboard and Transactions modules.

| Concern | Detail |
|---|---|
| Responsibility | Retrieve current balance for a given user ID |
| Service | `account_service.get_balance(user_id)` |
| Database | Reads the `accounts` table via `db.py` connection helper |

### 5.4 Transactions Module
**Goal:** Let the customer change their balance through deposits and withdrawals, with validation to prevent invalid states.

| Concern | Detail |
|---|---|
| Routes | `GET /deposit`, `POST /deposit`, `GET /withdraw`, `POST /withdraw` |
| Frontend | `deposit.html`, `withdraw.html` — amount input forms, flash feedback |
| Backend | `routes/transactions.py` — validates form input, calls account service, flashes result, redirects |
| Service | `account_service.deposit(user_id, amount)`, `account_service.withdraw(user_id, amount)` |
| Validation rules | Deposit: amount must be a positive number. Withdrawal: amount must be positive and ≤ current balance |
| Post-action | Redirect to `/dashboard` (POST → Redirect → GET pattern to prevent double-submission) |

---

## 6. Implementation Roadmap

### Phase Overview

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
 Setup      Auth        Dashboard   Transactions  Polish
```

### Phase 1 — Project Setup & Scaffolding
**Goal:** Establish the folder structure, install dependencies, and verify the Flask app boots.

- Create `FRONTEND/` and `BACKEND/` directory trees as defined in Section 4.
- Create `BACKEND/requirements.txt` with `flask` and `werkzeug`.
- Create `BACKEND/app.py` with a minimal Flask app and a health-check route.
- Create `BACKEND/db.py` with a SQLite connection helper and seed data for at least one test customer.
- Create `FRONTEND/templates/base.html` with Bootstrap 5 CDN link, navbar stub, and flash message block.
- Verify the app starts with `flask run`.

**Dependencies:** None — this is the foundation for all subsequent phases.

---

### Phase 2 — Authentication
**Goal:** Implement login and logout so that all subsequent features can be developed behind a session guard.

- Build `BACKEND/routes/auth.py` with `GET /login` and `POST /login` routes.
- Build `BACKEND/services/auth_service.py` for credential verification.
- Create `FRONTEND/templates/login.html` extending `base.html`.
- Implement the `login_required` session guard.
- Build `GET /logout` route that clears the session and redirects to `/login`.
- Register the `auth` blueprint in `app.py`.

**Dependencies:** Phase 1 (Flask app and DB connection must be available).

---

### Phase 3 — Dashboard
**Goal:** Give authenticated users a landing page that confirms their identity and shows their balance.

- Build `BACKEND/routes/dashboard.py` with `GET /dashboard` protected by `login_required`.
- Build `BACKEND/services/account_service.py` with `get_balance(user_id)`.
- Create `FRONTEND/templates/dashboard.html` displaying balance and action buttons.
- Register the `dashboard` blueprint in `app.py`.
- Redirect successful login to `/dashboard`.

**Dependencies:** Phase 2 (session guard must exist before protecting this route).

---

### Phase 4 — Transactions (Deposit & Withdraw)
**Goal:** Allow customers to modify their balance through validated deposit and withdrawal operations.

- Extend `account_service.py` with `deposit(user_id, amount)` and `withdraw(user_id, amount)`.
- Build `BACKEND/routes/transactions.py` with all four deposit/withdraw routes.
- Create `FRONTEND/templates/deposit.html` and `withdraw.html`.
- Apply `login_required` guard to all transaction routes.
- Implement POST → Redirect → GET pattern on form submission.
- Register the `transactions` blueprint in `app.py`.

**Dependencies:** Phase 3 (dashboard redirect target must exist; `get_balance` must be available to share the pattern).

---

### Phase 5 — UI Polish & Validation
**Goal:** Ensure the application is presentable and robust against bad input.

- Add `FRONTEND/static/css/custom.css` for minor Bootstrap overrides.
- Add server-side input validation with user-friendly flash messages for all forms.
- Ensure consistent Bootstrap card/button styling across all pages.
- Verify all redirect flows work correctly (unauthenticated → login, post-transaction → dashboard).
- Manual end-to-end walkthrough: login → view balance → deposit → withdraw → logout.

**Dependencies:** Phase 4 (all routes and templates must be in place).

---

### Phase Dependencies Summary

| Phase | Depends On |
|---|---|
| 1 — Scaffolding | — |
| 2 — Authentication | Phase 1 |
| 3 — Dashboard | Phase 2 |
| 4 — Transactions | Phase 3 |
| 5 — Polish & Validation | Phase 4 |

---

*End of Planning Document*
