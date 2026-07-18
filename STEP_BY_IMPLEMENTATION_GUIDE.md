# Banking Web Application — Step-by-Step Implementation Guide

> **Reference:** This guide follows the architecture and roadmap defined in [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md).
> Instructions are written in plain English. No raw code is included — each step explains *what* to do and *why*.

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Backend Implementation](#2-backend-implementation)
3. [Frontend Implementation](#3-frontend-implementation)
4. [Integration Steps](#4-integration-steps)
5. [Validation Rules](#5-validation-rules)
6. [Testing](#6-testing)
7. [Deployment](#7-deployment)

---

## 1. Environment Setup

### 1.1 Prerequisites
Before writing a single line of code, confirm that the following tools are installed on your machine:

- **Python 3.10 or later** — Flask requires a modern Python version. Confirm by running `python --version` or `python3 --version` in your terminal.
- **pip** — Python's package manager, bundled with Python. Used to install Flask and other dependencies.
- **A code editor** — VS Code is recommended, but any editor works.
- **A terminal / command prompt** — all commands in this guide are run from the terminal.

### 1.2 Create the Project Directory Structure
Create the top-level project folder (`banking-workshop/`) and the two main sub-folders inside it: `FRONTEND/` and `BACKEND/`. Inside `FRONTEND/`, create two sub-folders: `templates/` (for HTML pages) and `static/` (for CSS and images). Inside `BACKEND/`, create two sub-folders: `routes/` (for URL handlers) and `services/` (for business logic). Also create an empty `css/` folder inside `FRONTEND/static/`.

The final skeleton should match the folder structure described in Section 4 of `IMPLEMENTATION_PLAN.md`.

### 1.3 Create and Activate a Python Virtual Environment
A virtual environment keeps your project's Python packages isolated from the rest of your system, preventing version conflicts.

- Navigate into the `BACKEND/` folder in your terminal.
- Create a virtual environment by running the `python -m venv` command and giving it a name such as `venv`. This creates a hidden folder that holds a private copy of Python and pip.
- **Activate** the environment before installing anything:
  - On **macOS / Linux**: run `source venv/bin/activate`. Your terminal prompt will change to show `(venv)`.
  - On **Windows**: run `venv\Scripts\activate`.
- You must activate the virtual environment every time you open a new terminal session to work on this project.

### 1.4 Create the Requirements File
Inside `BACKEND/`, create a plain text file named `requirements.txt`. List the two packages you need, each on its own line:

- `flask` — the web framework
- `werkzeug` — ships with Flask but listing it explicitly ensures the correct version is used; it provides the password-hashing utilities

### 1.5 Install Dependencies
With the virtual environment active, install all packages listed in `requirements.txt` using pip's `-r` flag. Pip will download and install Flask and all of its own internal dependencies automatically.

### 1.6 Configure Flask Environment Variables
Flask needs to know two things before it can start:

- **Which file is the application entry point** — set the `FLASK_APP` environment variable to point to `app.py` inside `BACKEND/`.
- **Which mode to run in** — set `FLASK_ENV` (or `FLASK_DEBUG` in newer Flask versions) to `development`. This enables the auto-reloader (the server restarts when you save a file) and shows detailed error pages in the browser.

You can set these variables in your terminal directly, or create a `.flaskenv` file in `BACKEND/` which Flask reads automatically if the `python-dotenv` package is installed.

### 1.7 Verify the Setup
Create a minimal `app.py` in `BACKEND/` that does only one thing: creates a Flask application object and defines a single route (e.g., `/health`) that returns the text "OK". Run `flask run` from inside `BACKEND/`. Open a browser and visit `http://127.0.0.1:5000/health`. If you see "OK", your environment is working correctly.

---

## 2. Backend Implementation

### 2.1 Application Entry Point — `app.py`
`app.py` is the heart of the backend. Its responsibilities are:

1. **Create the Flask app object** — instantiate Flask and tell it where to find templates (`FRONTEND/templates/`) and static files (`FRONTEND/static/`). Flask accepts these as constructor arguments.
2. **Set a secret key** — Flask uses this to cryptographically sign session cookies. Without it, sessions will not work. Use a long, random string. During development a hardcoded string is fine; in production this must come from an environment variable.
3. **Register blueprints** — import and register each feature's blueprint (auth, dashboard, transactions) so Flask knows about all your routes.
4. **Initialise the database** — call a database initialisation function (from `db.py`) inside an `app.before_first_request` hook or directly at startup, so the database tables and seed data are created if the `bank.db` file does not exist yet.

### 2.2 Database Helper — `db.py`
This file is the single place where the application talks to SQLite. It has two responsibilities:

**Opening connections:** Write a function `get_db_connection()` that opens a connection to `bank.db` (using Python's built-in `sqlite3` module), sets the row factory to `sqlite3.Row` so that query results behave like dictionaries (columns accessible by name), and returns the connection. Every route that needs the database calls this function, uses the connection, then closes it when done.

**Initialising the database:** Write a function `init_db()` that checks whether the required tables exist and creates them if not. After creating the tables, it checks whether any customer rows exist; if the database is empty, it inserts one or two test customers with hashed passwords (use Werkzeug's `generate_password_hash` for this). This seeds the database so you can log in immediately without a registration feature.

### 2.3 Routes — What They Are and How to Structure Them
Flask routes are Python functions that are bound to a URL. When the browser visits that URL, Flask calls the corresponding function. Each function reads request data, calls a service function to do the real work, then either renders an HTML template or redirects the browser to another URL.

Organise routes into three separate files inside `BACKEND/routes/`, using Flask **Blueprints**. A Blueprint is simply a way to group related routes together and register them all at once in `app.py`.

#### 2.3.1 Authentication Routes — `routes/auth.py`
Create a Blueprint named `auth`.

**GET /login:** This route simply renders the login page template. It should first check whether the user is already logged in (i.e., `user_id` exists in the session); if so, redirect straight to the dashboard — there's no point showing the login form to someone who is already authenticated.

**POST /login:** This route handles the form submission from the login page. It reads the username and password from the request's form data, passes them to the `auth_service`, and then:
- If authentication succeeds: write the returned user ID into the session and redirect to `/dashboard`.
- If authentication fails: flash an error message and re-render the login template so the user can try again.

**GET /logout:** Clear the entire session (Flask provides a `session.clear()` call for this). Then redirect to the login page. After this redirect, the user's browser no longer holds a valid session cookie, so all protected pages will redirect back to login.

#### 2.3.2 Dashboard Route — `routes/dashboard.py`
Create a Blueprint named `dashboard`.

**GET /dashboard:** This is a protected route — the very first thing it should do is check that `user_id` exists in the session; if not, redirect to `/login`. If the user is authenticated, call `account_service.get_balance()` passing the `user_id` from the session. Pass the returned balance value to the dashboard template for display.

#### 2.3.3 Transaction Routes — `routes/transactions.py`
Create a Blueprint named `transactions`.

**GET /deposit:** Render the deposit form page. Protect with session check.

**POST /deposit:** Read the `amount` field from the form, validate it (see Section 5), call `account_service.deposit()`, flash a success or error message, then redirect to `/dashboard`.

**GET /withdraw:** Render the withdraw form page. Protect with session check.

**POST /withdraw:** Read the `amount` field from the form, validate it, call `account_service.withdraw()`, flash a success or error message, then redirect to `/dashboard`.

#### 2.3.4 The `login_required` Guard
Rather than copy-pasting the session check into every protected route, create a reusable helper. This can be a simple Python function that checks for `user_id` in the session and calls Flask's `redirect()` if it is absent. Alternatively, implement it as a Python decorator so you can annotate any route function with `@login_required` and the check happens automatically before the route body runs.

### 2.4 Services — Business Logic
Services are plain Python functions with no Flask dependency. They accept data, perform logic, interact with the database, and return results. Keeping them separate from routes makes them easy to test in isolation.

#### 2.4.1 `services/auth_service.py`
**`verify_credentials(username, password)`:** Open a database connection, query the users table for a row matching the given username. If no row is found, return `None` (user does not exist). If a row is found, use Werkzeug's `check_password_hash()` to compare the submitted password against the stored hash. If the hash matches, return the user's ID. If it does not match, return `None`. The calling route uses the return value to decide whether to set the session.

#### 2.4.2 `services/account_service.py`
**`get_balance(user_id)`:** Open a connection, query the accounts table for the balance of the given user ID, close the connection, and return the balance as a number.

**`deposit(user_id, amount)`:** Open a connection, read the current balance, add the deposit amount to it, update the accounts table with the new balance, commit the transaction, close the connection, and return the new balance.

**`withdraw(user_id, amount)`:** Open a connection, read the current balance, check that the requested amount does not exceed the balance (this is a guard that should also exist in the route, but defence-in-depth is good). Subtract the amount from the balance, update the row, commit, close, and return the new balance.

### 2.5 Session Management
Flask sessions work via a **signed cookie** stored in the browser. When you write to `session['user_id']`, Flask serialises that data, signs it with the app's secret key, and sends it to the browser as a cookie. On the next request, Flask reads the cookie back, verifies the signature, and makes the session data available again.

Key behaviours to be aware of:

- **Persistence:** The session persists across requests as long as the browser keeps the cookie and the server's secret key does not change. Restarting Flask with the same secret key does not log users out.
- **Clearing:** `session.clear()` removes all keys from the session and sends an empty cookie to the browser, effectively logging the user out.
- **Security:** Never store sensitive data (passwords, raw balances) in the session. Store only the minimum needed to identify the user — the `user_id` is sufficient.
- **Secret key:** If the secret key is changed, all existing sessions are immediately invalidated because their signatures can no longer be verified.

### 2.6 Error Handling
At the application level, register error handlers in `app.py` for the two most common HTTP errors:

- **404 Not Found:** Shown when a user visits a URL that does not map to any route. Render a simple "Page not found" template.
- **500 Internal Server Error:** Shown when an unhandled exception occurs in a route. Render a simple "Something went wrong" template.

At the route level, wrap database calls in try/except blocks. If an unexpected database error occurs (e.g., the `bank.db` file is corrupted), catch the exception, log it, flash a generic user-facing error message, and redirect to a safe page rather than crashing.

---

## 3. Frontend Implementation

### 3.1 Base Layout — `base.html`
All pages share a common shell defined in `base.html`. This template should contain:

- The HTML `<head>` element with the page title, meta charset, and the Bootstrap 5 CDN link (a single `<link>` tag pointing to the Bootstrap CSS file hosted on jsDelivr or the official Bootstrap CDN).
- A **navigation bar** using Bootstrap's `navbar` component. Show the bank name/logo on the left. If the user is logged in (you can pass a flag from the route, or check the session variable in the template), show a "Logout" button on the right.
- A **flash message block** directly below the navbar. Flask's `get_flashed_messages()` function returns a list of messages set by the backend. Loop over them and render each as a Bootstrap `alert` component. Use `alert-success` for success messages and `alert-danger` for errors.
- A `{% block content %}{% endblock %}` placeholder where child templates inject their unique page content.
- A minimal `<footer>` with the bank name and year.

Every other template (`login.html`, `dashboard.html`, `deposit.html`, `withdraw.html`) starts with `{% extends "base.html" %}` and fills in the `{% block content %}` section.

### 3.2 Login Page — `login.html`
The login page should have a centred card (Bootstrap `card` component) that contains:

- A heading such as "Welcome — Please Log In".
- A form with the `method="POST"` attribute and `action="/login"`. The form needs two input fields: one for username (`type="text"`) and one for password (`type="password"`). Both should use Bootstrap's `form-control` class for styling.
- A submit button styled with Bootstrap's `btn btn-primary`.
- Because this page extends `base.html`, flash messages (e.g., "Invalid credentials") will appear automatically above the card via the flash block.

There is no client-side JavaScript needed. The form submits to the server and Flask handles everything.

### 3.3 Dashboard — `dashboard.html`
The dashboard is the main page a customer sees after logging in. It should contain:

- A greeting that includes the customer's username (passed from the route as a template variable).
- A prominent **balance card** using Bootstrap's `card` component. Display the balance as a formatted currency value (e.g., `$1,250.00`). The Jinja2 template can apply Python's string formatting to the balance number passed from the route.
- Two action buttons:
  - **Deposit** — a button that links to `/deposit`
  - **Withdraw** — a button that links to `/withdraw`
- A **Logout** link that links to `/logout`.

Style the balance card to stand out — a light background colour, a larger font size for the balance figure, and sufficient padding all help readability.

### 3.4 Deposit Form — `deposit.html`
A simple, focused page containing:

- A heading: "Deposit Funds".
- A short explanatory sentence: "Enter the amount you wish to deposit into your account."
- A form with `method="POST"` and `action="/deposit"`. One input field for the amount (`type="number"`, with a `min` attribute of `0.01` and a `step` attribute of `0.01` for two-decimal precision). A submit button labelled "Deposit".
- A "Back to Dashboard" link below the form.
- Flash messages are inherited from `base.html` and will show validation errors automatically.

### 3.5 Withdraw Form — `withdraw.html`
Structurally identical to the deposit form, with these differences:

- Heading: "Withdraw Funds".
- Explanatory sentence: "Enter the amount you wish to withdraw. You cannot withdraw more than your current balance."
- Form `action` points to `/withdraw`.
- Optionally, display the current balance on this page (pass it from the route) so the user knows their limit before submitting.
- Flash messages will surface "Insufficient funds" errors automatically.

### 3.6 Bootstrap Layout Principles
Use Bootstrap's **grid system** to ensure pages look good on different screen sizes:

- Wrap each page's content in a `container` div, which adds horizontal padding and centres the content.
- For form pages (login, deposit, withdraw), use a single centred column (`col-md-6 offset-md-3`) so the form does not stretch to the full width on wider screens.
- Use Bootstrap utility classes (`mt-4`, `mb-3`, `p-4`) for spacing instead of writing custom CSS.
- Reserve `custom.css` only for changes Bootstrap cannot handle out of the box — for example, a custom brand colour for the navbar or a special style for the balance figure.

---

## 4. Integration Steps

### 4.1 Tell Flask Where to Find Templates and Static Files
By default, Flask looks for templates in a folder named `templates/` and static files in `static/` — both relative to `app.py`. Since your project places these inside `FRONTEND/`, you must explicitly configure the paths when creating the Flask app object. Pass the correct filesystem paths as the `template_folder` and `static_folder` arguments. Use Python's `os.path` or `pathlib` to construct the paths relative to `app.py` so they work regardless of where the project is cloned.

### 4.2 Register All Blueprints in `app.py`
Each routes file defines a Flask Blueprint. After creating the app object in `app.py`, import each Blueprint and call `app.register_blueprint()` for each one. This makes Flask aware of all the routes defined in `auth.py`, `dashboard.py`, and `transactions.py`. Without this step, visiting those URLs returns a 404 error.

### 4.3 Connect Flask to SQLite via `db.py`
Every service function that needs data calls `get_db_connection()` from `db.py`. The connection returns an open SQLite connection object. After running queries, always close the connection explicitly. This open-use-close pattern is simple and safe for a single-user workshop application.

The database file path in `db.py` should be constructed relative to the `db.py` file itself (using `os.path` or `pathlib`), so the `bank.db` file is always created inside `BACKEND/` regardless of the working directory from which `flask run` is invoked.

### 4.4 Pass Data from Routes to Templates
Flask's `render_template()` function accepts keyword arguments. Any keyword argument you pass becomes a variable available inside the Jinja2 template. For example, pass the balance as `balance=get_balance(user_id)` and it becomes `{{ balance }}` in the template. Pass the username similarly so the dashboard greeting can display it.

### 4.5 Pass Feedback from Backend to Frontend via Flash Messages
When a route needs to communicate success or failure to the user, it calls Flask's `flash()` function with a message string before redirecting or re-rendering. The `base.html` template reads all pending flash messages using `get_flashed_messages()` and displays them. This one-time display mechanism means the message appears exactly once — on the very next page load — and then disappears.

Use descriptive, user-friendly messages: "Deposit of $50.00 was successful." is better than "OK". "Insufficient funds. Your balance is $20.00." is better than "Error".

---

## 5. Validation Rules

Validation must happen on the **server side** (in the route or service layer), even if the HTML form uses `min` and `type="number"` attributes. Browser-level validation is helpful but can always be bypassed.

### 5.1 Login Validation
These checks run inside the `POST /login` route before calling `auth_service`:

| Check | Rule | Action if Failed |
|---|---|---|
| Username not empty | The submitted username field must not be blank | Flash "Username is required" and re-render login |
| Password not empty | The submitted password field must not be blank | Flash "Password is required" and re-render login |
| Credentials valid | `auth_service` must return a non-None user ID | Flash "Invalid username or password" and re-render login |

**Important:** Never tell the user *which* field was wrong (e.g., "Username not found"). A generic "Invalid username or password" message prevents attackers from enumerating valid usernames.

### 5.2 Balance Validation
These checks run in `account_service.get_balance()` and the dashboard route:

| Check | Rule | Action if Failed |
|---|---|---|
| User exists | The user ID from the session must correspond to a real row in the database | Log the anomaly and redirect to logout — the session is corrupted |
| Balance is numeric | The value retrieved from the database must be a number | Raise an error; this would indicate data corruption |

### 5.3 Deposit Validation
These checks run inside the `POST /deposit` route:

| Check | Rule | Action if Failed |
|---|---|---|
| Amount present | The form must include an `amount` field | Flash "Amount is required" and re-render deposit form |
| Amount is a number | The value must be parseable as a float | Flash "Please enter a valid number" |
| Amount is positive | The parsed float must be greater than zero | Flash "Deposit amount must be greater than zero" |
| Amount is reasonable | Optionally cap the maximum single deposit (e.g., $1,000,000) to prevent data overflow | Flash "Amount exceeds the maximum allowed deposit" |

Only if all checks pass should the route call `account_service.deposit()`.

### 5.4 Withdrawal Validation
These checks run inside the `POST /withdraw` route:

| Check | Rule | Action if Failed |
|---|---|---|
| Amount present | Same as deposit | Flash "Amount is required" |
| Amount is a number | Same as deposit | Flash "Please enter a valid number" |
| Amount is positive | Same as deposit | Flash "Withdrawal amount must be greater than zero" |
| Sufficient funds | The amount must be less than or equal to the current balance | Flash "Insufficient funds. Your current balance is $X.XX" |

The "Insufficient funds" message should include the current balance so the user immediately knows their limit without having to navigate back to the dashboard.

---

## 6. Testing

### 6.1 Unit Tests
Unit tests verify individual functions in isolation — specifically the **service layer** — without starting a web server or touching a real database.

**What to test in `auth_service.py`:**
- Given a correct username and password, `verify_credentials()` returns a valid user ID.
- Given an incorrect password, `verify_credentials()` returns `None`.
- Given a non-existent username, `verify_credentials()` returns `None`.
- Passwords are never stored or compared as plaintext.

**What to test in `account_service.py`:**
- `get_balance()` returns the correct numeric value for a known user.
- `deposit()` increases the balance by the exact amount passed.
- `withdraw()` decreases the balance by the exact amount passed.
- Attempting to `withdraw()` more than the current balance does not update the database (the check inside the service should prevent the write).

**How to set up unit tests:** Use Python's built-in `unittest` module or the popular `pytest` library. For tests that need the database, create an in-memory SQLite database (`:memory:`) in the test setup, seed it with known test data, run the service function, and assert the result. Tear down after each test so tests are independent.

### 6.2 Integration Tests
Integration tests verify that the **HTTP layer and service layer work together correctly** — they make real HTTP requests to a Flask test client and check the responses.

Flask provides a built-in test client that simulates a browser without starting an actual server. Use it to:

**Authentication flow:**
- `POST /login` with valid credentials → expect a redirect (HTTP 302) to `/dashboard`.
- `POST /login` with invalid credentials → expect HTTP 200 (re-render of login page) and the error flash message in the response body.
- `GET /dashboard` without a session → expect a redirect to `/login`.
- `GET /logout` → expect a redirect to `/login`, and a subsequent `GET /dashboard` should also redirect to `/login`.

**Transaction flow:**
- Log in first (using the test client's session context), then:
- `POST /deposit` with a valid amount → expect redirect to `/dashboard`; query the database directly and confirm balance increased.
- `POST /deposit` with a negative amount → expect re-render of deposit form with error message.
- `POST /withdraw` with a valid amount ≤ balance → expect redirect; confirm balance decreased.
- `POST /withdraw` with an amount exceeding the balance → expect re-render of withdraw form with "Insufficient funds" message.

### 6.3 Manual Testing Checklist
Run through this checklist in a browser before considering the application complete:

**Authentication:**
- [ ] Visit `http://127.0.0.1:5000/` — should redirect to `/login`.
- [ ] Visit `/dashboard` directly without logging in — should redirect to `/login`.
- [ ] Submit the login form with blank fields — appropriate error message appears.
- [ ] Submit the login form with a wrong password — "Invalid username or password" appears.
- [ ] Submit the login form with correct credentials — redirected to `/dashboard`.

**Dashboard:**
- [ ] Balance is displayed correctly after login.
- [ ] "Deposit" button navigates to `/deposit`.
- [ ] "Withdraw" button navigates to `/withdraw`.
- [ ] "Logout" button logs out and redirects to `/login`.

**Deposit:**
- [ ] Submit the deposit form with no amount — error message appears.
- [ ] Submit with a negative number — error message appears.
- [ ] Submit with zero — error message appears.
- [ ] Submit with a valid positive amount — redirected to dashboard, balance has increased by exactly that amount.
- [ ] Flash message confirms the deposit amount.

**Withdraw:**
- [ ] Submit with no amount — error message appears.
- [ ] Submit with an amount greater than the balance — "Insufficient funds" message appears with current balance shown.
- [ ] Submit with the exact balance amount — redirected to dashboard, balance is now zero.
- [ ] Submit with a valid amount less than the balance — redirected to dashboard, balance decreased correctly.

**Security:**
- [ ] After logging out, press the browser Back button and attempt to access `/dashboard` — should redirect to `/login`.
- [ ] Try visiting `/deposit` and `/withdraw` without being logged in — both should redirect to `/login`.

---

## 7. Deployment

### 7.1 Running Locally (Development)
This is the standard workflow during development:

1. Open a terminal and navigate to the `BACKEND/` folder.
2. Activate the virtual environment (`source venv/bin/activate` on Mac/Linux, `venv\Scripts\activate` on Windows).
3. Run `flask run`.
4. Flask prints the local URL, typically `http://127.0.0.1:5000`. Open this in a browser.
5. The development server watches for file changes and auto-reloads — you do not need to restart it manually after editing Python files.
6. To stop the server, press `Ctrl + C` in the terminal.

### 7.2 Production Considerations
Flask's built-in development server is **not suitable for production**. It is single-threaded, does not handle concurrent requests, and exposes debug information. The following considerations apply when deploying beyond a local workshop:

**Use a production WSGI server:** Replace `flask run` with a production-grade WSGI server such as **Gunicorn** (Linux/macOS) or **Waitress** (cross-platform, including Windows). These servers handle multiple concurrent connections properly. Add the chosen server to `requirements.txt`.

**Upgrade the database:** SQLite is a file-based database with no support for concurrent writes. For any production workload with multiple users, replace SQLite with **PostgreSQL** or **MySQL**. The service layer is designed to be database-agnostic, so only `db.py` needs to change.

**Use environment variables for secrets:** The Flask secret key must not be hardcoded in `app.py` in production. Load it from an environment variable using `os.environ.get('SECRET_KEY')`. Set this variable in your hosting environment's configuration panel, never in source code.

**Enable HTTPS:** All traffic should be encrypted in transit. In production, place the application behind a reverse proxy (e.g., **Nginx**) that handles TLS termination with a certificate from Let's Encrypt.

**Set `FLASK_DEBUG=0`:** Never run with debug mode enabled in production. Debug mode exposes an interactive Python shell in the browser error page, which is a critical security vulnerability.

**Containerise with Docker (optional, recommended):** Package the application in a Docker container to ensure consistent behaviour across development, staging, and production environments. The container should copy `BACKEND/` contents, install `requirements.txt`, and run Gunicorn as the entry point.

**Database backup:** Even in development, periodically back up `bank.db` by copying the file. In production, configure automated database backups on a schedule.

---

*End of Step-by-Step Implementation Guide*
