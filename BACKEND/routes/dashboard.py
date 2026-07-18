"""
routes/dashboard.py — Dashboard blueprint.

Routes:
  GET /dashboard — show the customer's balance (login required)
"""

from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for,
    flash,
)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services"))

from services.account_service import get_balance

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    username = session.get("username", "Customer")

    try:
        balance = get_balance(user_id)
    except ValueError:
        # Account row is missing — corrupted session; log the user out.
        session.clear()
        flash("Your session has expired. Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        username=username,
        balance=balance,
    )
