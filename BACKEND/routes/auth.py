"""
routes/auth.py — Authentication blueprint.

Routes:
  GET  /login  — render the login form (redirect to dashboard if already logged in)
  POST /login  — process credentials; set session on success
  GET  /logout — clear session; redirect to login
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services"))

from services.auth_service import verify_credentials

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Already authenticated — skip the login form.
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # --- Validation ---
        if not username:
            flash("Username is required.", "danger")
            return render_template("login.html")
        if not password:
            flash("Password is required.", "danger")
            return render_template("login.html")

        user_id = verify_credentials(username, password)
        if user_id is None:
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        # --- Success: set session and redirect ---
        session.clear()            # avoid session fixation
        session["user_id"] = user_id
        session["username"] = username
        flash(f"Welcome back, {username}!", "success")
        return redirect(url_for("dashboard.dashboard"))

    # GET — show the login form
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
