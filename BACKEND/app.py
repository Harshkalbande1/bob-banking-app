"""
app.py — Flask application entry point.

Responsibilities:
  - Create and configure the Flask app object.
  - Point Flask at FRONTEND/ for templates and static files.
  - Register all feature blueprints.
  - Register 404 / 500 error handlers.
  - Initialise the SQLite database on first startup.
"""

import os
import sys

from flask import Flask, render_template

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
# BACKEND/ is this file's directory.
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Project root is one level up.
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
# Frontend assets live in FRONTEND/ at the project root.
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "FRONTEND")

# Make BACKEND/ importable (routes and services use relative imports to db.py).
sys.path.insert(0, BACKEND_DIR)

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, "templates"),
    static_folder=os.path.join(FRONTEND_DIR, "static"),
)

# Secret key — signs Flask's session cookies.
# In development a hardcoded value is fine; in production load from env var.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-in-production-use-a-long-random-string",
)

# ---------------------------------------------------------------------------
# Blueprint registration
# ---------------------------------------------------------------------------
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.transactions import transactions_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(transactions_bp)

# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("errors/500.html"), 500


# ---------------------------------------------------------------------------
# Database initialisation
# ---------------------------------------------------------------------------
from db import init_db

with app.app_context():
    init_db()

# ---------------------------------------------------------------------------
# Root redirect → login
# ---------------------------------------------------------------------------
from flask import redirect, url_for

@app.route("/")
def index():
    return redirect(url_for("auth.login"))


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
