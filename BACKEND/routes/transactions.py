"""
routes/transactions.py — Deposit and withdrawal blueprint.

Routes:
  GET  /deposit   — render deposit form (login required)
  POST /deposit   — process deposit; redirect to dashboard
  GET  /withdraw  — render withdrawal form (login required)
  POST /withdraw  — process withdrawal; redirect to dashboard
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

from services.account_service import deposit, withdraw, get_balance

transactions_bp = Blueprint("transactions", __name__)


def _login_required():
    """Return a redirect response if the user is not logged in, else None."""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return None


# ---------------------------------------------------------------------------
# Deposit
# ---------------------------------------------------------------------------

@transactions_bp.route("/deposit", methods=["GET", "POST"])
def deposit_funds():
    guard = _login_required()
    if guard:
        return guard

    user_id = session["user_id"]

    if request.method == "POST":
        raw_amount = request.form.get("amount", "").strip()

        # --- Validation ---
        if not raw_amount:
            flash("Amount is required.", "danger")
            return render_template("deposit.html")

        try:
            amount = float(raw_amount)
        except ValueError:
            flash("Please enter a valid number.", "danger")
            return render_template("deposit.html")

        if amount <= 0:
            flash("Deposit amount must be greater than zero.", "danger")
            return render_template("deposit.html")

        # --- Service call (also validates internally for defence-in-depth) ---
        try:
            new_balance = deposit(user_id, amount)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("deposit.html")

        flash(
            f"Deposit of ${amount:,.2f} was successful. "
            f"New balance: ${new_balance:,.2f}.",
            "success",
        )
        return redirect(url_for("dashboard.dashboard"))

    # GET
    return render_template("deposit.html")


# ---------------------------------------------------------------------------
# Withdraw
# ---------------------------------------------------------------------------

@transactions_bp.route("/withdraw", methods=["GET", "POST"])
def withdraw_funds():
    guard = _login_required()
    if guard:
        return guard

    user_id = session["user_id"]
    current_balance = get_balance(user_id)

    if request.method == "POST":
        raw_amount = request.form.get("amount", "").strip()

        # --- Validation ---
        if not raw_amount:
            flash("Amount is required.", "danger")
            return render_template("withdraw.html", balance=current_balance)

        try:
            amount = float(raw_amount)
        except ValueError:
            flash("Please enter a valid number.", "danger")
            return render_template("withdraw.html", balance=current_balance)

        if amount <= 0:
            flash("Withdrawal amount must be greater than zero.", "danger")
            return render_template("withdraw.html", balance=current_balance)

        # --- Service call (also validates insufficient funds internally) ---
        try:
            new_balance = withdraw(user_id, amount)
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("withdraw.html", balance=current_balance)

        flash(
            f"Withdrawal of ${amount:,.2f} was successful. "
            f"New balance: ${new_balance:,.2f}.",
            "success",
        )
        return redirect(url_for("dashboard.dashboard"))

    # GET
    return render_template("withdraw.html", balance=current_balance)
