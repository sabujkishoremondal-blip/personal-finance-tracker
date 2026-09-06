"""Balance math correctness tests.

The Streamlit frontend calls these services directly, so validating them
is equivalent to validating the financial correctness of the app.
"""
import os
import sys
import pytest

# make /app importable
sys.path.insert(0, "/app")

from database.database import init_db, get_conn, set_setting
from services.balance_service import available_balance, add_balance
from services.expense_service import (
    add_expense, update_expense, delete_expense,
    add_debt, settle_debt, list_debts,
)


@pytest.fixture(scope="module", autouse=True)
def _setup():
    init_db()
    yield


def _reset_db(starting: float = 0.0):
    with get_conn() as conn:
        conn.execute("DELETE FROM expenses")
        conn.execute("DELETE FROM balance_transactions")
        conn.execute("DELETE FROM debts")
        conn.execute("DELETE FROM budgets")
    set_setting("starting_balance", str(starting))


class TestBalanceMath:
    def test_add_expense_decreases_balance(self):
        _reset_db(1000)
        assert available_balance() == 1000
        add_expense(300, "Food", "test")
        assert available_balance() == 700

    def test_add_balance_increases(self):
        _reset_db(1000)
        add_balance(500, "Salary")
        assert available_balance() == 1500

    def test_borrow_flow_increases_then_repay_decreases(self):
        _reset_db(1000)
        did = add_debt("borrowed", "TestUser", 250)
        # borrowing increases wallet
        assert available_balance() == 1250
        # open debt exists
        open_borrowed = [d for d in list_debts("borrowed", "open") if d["id"] == did]
        assert len(open_borrowed) == 1
        # settling ("Mark as Repaid") decreases balance
        assert settle_debt(did) is True
        assert available_balance() == 1000
        # debt now settled
        settled = [d for d in list_debts("borrowed") if d["id"] == did][0]
        assert settled["status"] == "settled"

    def test_friend_owes_no_effect_until_received(self):
        _reset_db(1000)
        did = add_debt("lent", "TestFriend", 150)
        # lending does NOT change balance
        assert available_balance() == 1000
        # settle -> receive -> +150
        assert settle_debt(did) is True
        assert available_balance() == 1150

    def test_negative_balance_allowed(self):
        _reset_db(100)
        add_expense(300, "Food", "big")
        assert available_balance() == -200
        # can still add more
        add_expense(50, "Food", "another")
        assert available_balance() == -250

    def test_edit_expense_updates_balance(self):
        _reset_db(1000)
        eid = add_expense(200, "Food", "orig")
        assert available_balance() == 800
        update_expense(eid, amount=500)
        assert available_balance() == 500

    def test_delete_expense_restores_balance(self):
        _reset_db(1000)
        eid = add_expense(400, "Food", "to delete")
        assert available_balance() == 600
        delete_expense(eid)
        assert available_balance() == 1000

    def test_delete_debt_removes_related_tx(self):
        from services.expense_service import delete_debt
        _reset_db(1000)
        did = add_debt("borrowed", "X", 500)
        assert available_balance() == 1500
        delete_debt(did)
        assert available_balance() == 1000
