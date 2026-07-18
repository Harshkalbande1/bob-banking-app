"""
test_account_service.py — Unit tests for services/account_service.py.

Tests balance retrieval, deposit, and withdrawal logic in isolation from Flask.
"""

import os
import sys

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, os.path.join(BACKEND_DIR, "services"))


def _get_user_id(test_db_path: str) -> int:
    """Helper: fetch the seeded testuser's ID directly from the test database."""
    import sqlite3
    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT id FROM users WHERE username='testuser'").fetchone()
    conn.close()
    return row["id"]


# ---------------------------------------------------------------------------
# get_balance
# ---------------------------------------------------------------------------

class TestGetBalance:
    def test_returns_correct_initial_balance(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import get_balance

        uid = _get_user_id(test_db_path)
        balance = get_balance(uid)
        assert balance == pytest.approx(500.0)

    def test_raises_for_unknown_user(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import get_balance

        with pytest.raises(ValueError, match="No account found"):
            get_balance(99999)


# ---------------------------------------------------------------------------
# deposit
# ---------------------------------------------------------------------------

class TestDeposit:
    def test_increases_balance_by_exact_amount(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import deposit, get_balance

        uid = _get_user_id(test_db_path)
        new_balance = deposit(uid, 250.0)
        assert new_balance == pytest.approx(750.0)
        assert get_balance(uid) == pytest.approx(750.0)

    def test_zero_amount_raises_value_error(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import deposit

        uid = _get_user_id(test_db_path)
        with pytest.raises(ValueError, match="greater than zero"):
            deposit(uid, 0)

    def test_negative_amount_raises_value_error(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import deposit

        uid = _get_user_id(test_db_path)
        with pytest.raises(ValueError, match="greater than zero"):
            deposit(uid, -50.0)

    def test_exceeding_max_raises_value_error(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import deposit

        uid = _get_user_id(test_db_path)
        with pytest.raises(ValueError, match="maximum"):
            deposit(uid, 2_000_000.0)

    def test_multiple_deposits_accumulate(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import deposit, get_balance

        uid = _get_user_id(test_db_path)
        deposit(uid, 100.0)
        deposit(uid, 200.0)
        assert get_balance(uid) == pytest.approx(800.0)


# ---------------------------------------------------------------------------
# withdraw
# ---------------------------------------------------------------------------

class TestWithdraw:
    def test_decreases_balance_by_exact_amount(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import withdraw, get_balance

        uid = _get_user_id(test_db_path)
        new_balance = withdraw(uid, 100.0)
        assert new_balance == pytest.approx(400.0)
        assert get_balance(uid) == pytest.approx(400.0)

    def test_withdraw_exact_balance_leaves_zero(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import withdraw, get_balance

        uid = _get_user_id(test_db_path)
        new_balance = withdraw(uid, 500.0)
        assert new_balance == pytest.approx(0.0)
        assert get_balance(uid) == pytest.approx(0.0)

    def test_overdraft_raises_value_error(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import withdraw, get_balance

        uid = _get_user_id(test_db_path)
        with pytest.raises(ValueError, match="Insufficient funds"):
            withdraw(uid, 600.0)
        # Balance must NOT have changed after the failed attempt.
        assert get_balance(uid) == pytest.approx(500.0)

    def test_zero_amount_raises_value_error(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import withdraw

        uid = _get_user_id(test_db_path)
        with pytest.raises(ValueError, match="greater than zero"):
            withdraw(uid, 0)

    def test_negative_amount_raises_value_error(self, test_db_path, monkeypatch):
        import db as db_module
        monkeypatch.setattr(db_module, "DB_PATH", test_db_path)
        from services.account_service import withdraw

        uid = _get_user_id(test_db_path)
        with pytest.raises(ValueError, match="greater than zero"):
            withdraw(uid, -10.0)
