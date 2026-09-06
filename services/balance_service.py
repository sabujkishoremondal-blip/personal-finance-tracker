"""Balance calculation & transaction helpers.

The available balance is derived entirely from the transactions table.
It is NEVER stored as a mutable single value.
"""
from datetime import datetime, date
from typing import Optional
from database.database import get_conn, get_setting
from utils.constants import (
    TX_BALANCE_ADD, TX_BORROW_RECEIVED, TX_BORROW_REPAID, TX_FRIEND_RECEIVED,
)


def _to_iso(d) -> str:
    if isinstance(d, (datetime, date)):
        return d.isoformat()
    return str(d)


def get_starting_balance() -> float:
    return float(get_setting("starting_balance", "0") or 0)


def total_expenses(year: Optional[int] = None, month: Optional[int] = None) -> float:
    with get_conn() as conn:
        q = "SELECT COALESCE(SUM(amount),0) AS s FROM expenses"
        params = []
        if year and month:
            q += " WHERE strftime('%Y',date)=? AND strftime('%m',date)=?"
            params = [str(year), f"{month:02d}"]
        return float(conn.execute(q, params).fetchone()["s"])


def total_balance_in(year: Optional[int] = None, month: Optional[int] = None,
                     tx_types: Optional[list] = None) -> float:
    with get_conn() as conn:
        q = "SELECT COALESCE(SUM(amount),0) AS s FROM balance_transactions WHERE 1=1"
        params = []
        if tx_types:
            q += f" AND tx_type IN ({','.join(['?']*len(tx_types))})"
            params.extend(tx_types)
        if year and month:
            q += " AND strftime('%Y',date)=? AND strftime('%m',date)=?"
            params.extend([str(year), f"{month:02d}"])
        return float(conn.execute(q, params).fetchone()["s"])


def available_balance() -> float:
    """Global available balance across all history."""
    start = get_starting_balance()
    added = total_balance_in(tx_types=[TX_BALANCE_ADD])
    borrowed_in = total_balance_in(tx_types=[TX_BORROW_RECEIVED])
    friend_paid = total_balance_in(tx_types=[TX_FRIEND_RECEIVED])
    repaid_out = total_balance_in(tx_types=[TX_BORROW_REPAID])
    spent = total_expenses()
    return start + added + borrowed_in + friend_paid - repaid_out - spent


def month_summary(year: int, month: int) -> dict:
    added = total_balance_in(year, month, [TX_BALANCE_ADD])
    borrowed = total_balance_in(year, month, [TX_BORROW_RECEIVED])
    friend_in = total_balance_in(year, month, [TX_FRIEND_RECEIVED])
    repaid = total_balance_in(year, month, [TX_BORROW_REPAID])
    spent = total_expenses(year, month)
    return {
        "added": added,
        "borrowed_received": borrowed,
        "friend_received": friend_in,
        "repaid": repaid,
        "spent": spent,
        "net_flow": added + borrowed + friend_in - repaid - spent,
    }


def add_balance(amount: float, source: str, description: str = "",
                d: Optional[date] = None) -> int:
    d = d or date.today()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO balance_transactions(amount,tx_type,source,description,date) "
            "VALUES(?,?,?,?,?)",
            (float(amount), TX_BALANCE_ADD, source, description, _to_iso(d)),
        )
        return cur.lastrowid


def owed_by_friends() -> float:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount),0) AS s FROM debts "
            "WHERE direction='lent' AND status='open'"
        ).fetchone()
        return float(row["s"])


def owed_to_others() -> float:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount),0) AS s FROM debts "
            "WHERE direction='borrowed' AND status='open'"
        ).fetchone()
        return float(row["s"])
