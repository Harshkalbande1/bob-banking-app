"""
account_service.py — Account management business logic.

Handles balance retrieval, deposits, and withdrawals.
Has no Flask dependency — purely Python so it can be unit-tested in isolation.
"""

from db import get_db_connection


# Maximum single transaction amount — prevents absurd data overflow.
MAX_TRANSACTION = 1_000_000.00


def get_balance(user_id: int) -> float:
    """
    Return the current balance for user_id.

    Raises:
        ValueError: if no account row exists for the given user_id.
    """
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT balance FROM accounts WHERE user_id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise ValueError(f"No account found for user_id={user_id}")

    return float(row["balance"])


def deposit(user_id: int, amount: float) -> float:
    """
    Add *amount* to the user's balance.

    Args:
        user_id: the authenticated customer's ID.
        amount:  must be a positive float (caller is responsible for
                 pre-validating; this function also guards internally).

    Returns:
        The new balance after the deposit.

    Raises:
        ValueError: if amount is not positive or exceeds MAX_TRANSACTION.
    """
    if amount <= 0:
        raise ValueError("Deposit amount must be greater than zero.")
    if amount > MAX_TRANSACTION:
        raise ValueError(
            f"Deposit amount exceeds the maximum of ${MAX_TRANSACTION:,.2f}."
        )

    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE accounts SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id),
        )
        conn.commit()
        row = conn.execute(
            "SELECT balance FROM accounts WHERE user_id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()

    return float(row["balance"])


def withdraw(user_id: int, amount: float) -> float:
    """
    Subtract *amount* from the user's balance.

    Args:
        user_id: the authenticated customer's ID.
        amount:  must be positive and must not exceed the current balance.

    Returns:
        The new balance after the withdrawal.

    Raises:
        ValueError: if amount is invalid or exceeds the current balance.
    """
    if amount <= 0:
        raise ValueError("Withdrawal amount must be greater than zero.")
    if amount > MAX_TRANSACTION:
        raise ValueError(
            f"Withdrawal amount exceeds the maximum of ${MAX_TRANSACTION:,.2f}."
        )

    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT balance FROM accounts WHERE user_id = ?", (user_id,)
        ).fetchone()

        if row is None:
            raise ValueError(f"No account found for user_id={user_id}")

        current = float(row["balance"])
        if amount > current:
            raise ValueError(
                f"Insufficient funds. Your current balance is ${current:,.2f}."
            )

        conn.execute(
            "UPDATE accounts SET balance = balance - ? WHERE user_id = ?",
            (amount, user_id),
        )
        conn.commit()
        new_row = conn.execute(
            "SELECT balance FROM accounts WHERE user_id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()

    return float(new_row["balance"])
