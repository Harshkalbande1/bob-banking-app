"""
test_routes.py — Integration tests for all HTTP routes.

Uses Flask's built-in test client to simulate browser requests.
Each test gets its own isolated database via the fixtures in conftest.py.
"""

import os
import sys

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)


# ===========================================================================
# Authentication routes
# ===========================================================================

class TestLoginRoute:
    def test_get_login_page_returns_200(self, client):
        response = client.get("/login")
        assert response.status_code == 200
        assert b"SecureBank" in response.data

    def test_post_valid_credentials_redirects_to_dashboard(self, client):
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]

    def test_post_invalid_password_returns_200_with_error(self, client):
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "badpass"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Invalid username or password" in response.data

    def test_post_empty_username_shows_error(self, client):
        response = client.post(
            "/login",
            data={"username": "", "password": "testpass"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Username is required" in response.data

    def test_post_empty_password_shows_error(self, client):
        response = client.post(
            "/login",
            data={"username": "testuser", "password": ""},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Password is required" in response.data

    def test_already_logged_in_redirects_to_dashboard(self, auth_client):
        response = auth_client.get("/login", follow_redirects=False)
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]


class TestLogoutRoute:
    def test_logout_redirects_to_login(self, auth_client):
        response = auth_client.get("/logout", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_dashboard_inaccessible_after_logout(self, auth_client):
        auth_client.get("/logout")
        response = auth_client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


# ===========================================================================
# Dashboard route
# ===========================================================================

class TestDashboardRoute:
    def test_unauthenticated_redirects_to_login(self, client):
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_authenticated_shows_balance(self, auth_client):
        response = auth_client.get("/dashboard", follow_redirects=True)
        assert response.status_code == 200
        # Seeded balance is $500.00
        assert b"500.00" in response.data
        assert b"testuser" in response.data


# ===========================================================================
# Deposit routes
# ===========================================================================

class TestDepositRoute:
    def test_unauthenticated_get_redirects_to_login(self, client):
        response = client.get("/deposit", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_get_deposit_page_shows_form(self, auth_client):
        response = auth_client.get("/deposit")
        assert response.status_code == 200
        assert b"Deposit" in response.data

    def test_valid_deposit_redirects_to_dashboard(self, auth_client):
        response = auth_client.post(
            "/deposit",
            data={"amount": "100.00"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]

    def test_valid_deposit_updates_balance(self, auth_client):
        auth_client.post("/deposit", data={"amount": "100.00"})
        response = auth_client.get("/dashboard")
        # New balance should be 500 + 100 = 600
        assert b"600.00" in response.data

    def test_zero_amount_shows_error(self, auth_client):
        response = auth_client.post(
            "/deposit",
            data={"amount": "0"},
            follow_redirects=True,
        )
        assert b"greater than zero" in response.data

    def test_negative_amount_shows_error(self, auth_client):
        response = auth_client.post(
            "/deposit",
            data={"amount": "-50"},
            follow_redirects=True,
        )
        assert b"greater than zero" in response.data

    def test_empty_amount_shows_error(self, auth_client):
        response = auth_client.post(
            "/deposit",
            data={"amount": ""},
            follow_redirects=True,
        )
        assert b"required" in response.data

    def test_non_numeric_amount_shows_error(self, auth_client):
        response = auth_client.post(
            "/deposit",
            data={"amount": "abc"},
            follow_redirects=True,
        )
        assert b"valid number" in response.data


# ===========================================================================
# Withdraw routes
# ===========================================================================

class TestWithdrawRoute:
    def test_unauthenticated_get_redirects_to_login(self, client):
        response = client.get("/withdraw", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_get_withdraw_page_shows_balance(self, auth_client):
        response = auth_client.get("/withdraw")
        assert response.status_code == 200
        assert b"500.00" in response.data

    def test_valid_withdrawal_redirects_to_dashboard(self, auth_client):
        response = auth_client.post(
            "/withdraw",
            data={"amount": "100.00"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers["Location"]

    def test_valid_withdrawal_updates_balance(self, auth_client):
        auth_client.post("/withdraw", data={"amount": "100.00"})
        response = auth_client.get("/dashboard")
        # New balance: 500 - 100 = 400
        assert b"400.00" in response.data

    def test_overdraft_shows_insufficient_funds_error(self, auth_client):
        response = auth_client.post(
            "/withdraw",
            data={"amount": "9999.00"},
            follow_redirects=True,
        )
        assert b"Insufficient funds" in response.data

    def test_exact_balance_withdrawal_succeeds(self, auth_client):
        response = auth_client.post(
            "/withdraw",
            data={"amount": "500.00"},
            follow_redirects=True,
        )
        assert b"0.00" in response.data

    def test_empty_amount_shows_error(self, auth_client):
        response = auth_client.post(
            "/withdraw",
            data={"amount": ""},
            follow_redirects=True,
        )
        assert b"required" in response.data


# ===========================================================================
# Root redirect
# ===========================================================================

class TestRootRedirect:
    def test_root_redirects_to_login(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]
