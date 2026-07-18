# SecureBank — Banking Web Application

A lightweight, full-stack banking application built with **Python Flask**, **Bootstrap 5**, and **SQLite**.

---

## Quick Start

### 1. Navigate to the backend folder

```bash
cd BACKEND
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
flask run
```

Open your browser at **http://127.0.0.1:5000**

---

## Demo Credentials

| Username | Password     | Starting Balance |
|----------|--------------|-----------------|
| alice    | password123  | $1,500.00        |
| bob      | securepass   | $750.50          |

---

## Features

| Feature        | Description                                         |
|----------------|-----------------------------------------------------|
| Login          | Secure credential verification with hashed passwords |
| Dashboard      | View current account balance                        |
| Deposit        | Add funds — validates positive amounts              |
| Withdraw       | Remove funds — validates against current balance    |
| Logout         | Invalidates the session immediately                 |
| Error pages    | Custom 404 and 500 pages                            |

---

## Project Structure

```
banking-workshop/
├── FRONTEND/
│   ├── templates/
│   │   ├── base.html          # Shared layout: navbar, flash messages
│   │   ├── login.html         # Login form
│   │   ├── dashboard.html     # Balance + action buttons
│   │   ├── deposit.html       # Deposit form
│   │   ├── withdraw.html      # Withdraw form
│   │   └── errors/
│   │       ├── 404.html
│   │       └── 500.html
│   └── static/
│       └── css/
│           └── custom.css     # Bootstrap overrides
│
├── BACKEND/
│   ├── app.py                 # Flask entry point, blueprint registration
│   ├── db.py                  # SQLite connection helper + DB init + seed data
│   ├── routes/
│   │   ├── auth.py            # /login, /logout
│   │   ├── dashboard.py       # /dashboard
│   │   └── transactions.py    # /deposit, /withdraw
│   ├── services/
│   │   ├── auth_service.py    # Credential verification
│   │   └── account_service.py # Balance, deposit, withdraw logic
│   ├── tests/
│   │   ├── conftest.py        # Shared pytest fixtures
│   │   ├── test_auth_service.py
│   │   ├── test_account_service.py
│   │   └── test_routes.py
│   ├── bank.db                # SQLite database (auto-created on first run)
│   ├── requirements.txt
│   └── .flaskenv              # FLASK_APP and FLASK_DEBUG settings
│
├── IMPLEMENTATION_PLAN.md
├── STEP_BY_IMPLEMENTATION_GUIDE.md
└── README.md
```

---

## Running Tests

From the `BACKEND/` directory (with the virtual environment active):

```bash
pytest tests/ -v
```

The test suite covers:
- **Unit tests** — `auth_service` and `account_service` in isolation using a temporary in-memory-style database.
- **Integration tests** — all HTTP routes via Flask's test client.

---

## Security Notes

- Passwords are stored as **Werkzeug PBKDF2-SHA256 hashes** — never plaintext.
- Sessions are signed with a secret key; `session.clear()` invalidates them immediately on logout.
- All validation is server-side; client-side HTML attributes are a convenience only.
- The generic "Invalid username or password" message prevents username enumeration.

---

## Production Checklist

Before deploying to a real environment:

- [ ] Replace the hardcoded `SECRET_KEY` in `app.py` with an environment variable.
- [ ] Set `FLASK_DEBUG=0` (or remove `.flaskenv`).
- [ ] Replace Flask's dev server with **Gunicorn**: `gunicorn -w 4 app:app`
- [ ] Replace SQLite with PostgreSQL or MySQL for concurrent users.
- [ ] Place the app behind **Nginx** with TLS (Let's Encrypt).

---

*Built as part of the IBM Banking Workshop.*
