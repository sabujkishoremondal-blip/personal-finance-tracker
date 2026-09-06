"""User-scoped balance & transaction helpers."""
from datetime import datetime, date
from typing import Optional
from database.database import get_conn, get_setting
from utils.constants import (
    TX_BALANCE_ADD, TX_BORROW_RECEIVED, TX_BORROW_REPAID, TX_FRIEND_RECEIVED,
)


def _iso(d) -> str:
    if isinstance(d, (datetime, date)):
        return d.isoformat()
    return str(d)


def get_starting_balance(user_id: int) -> float:
    return float(get_setting(user_id, "starting_balance", "0") or 0)


def total_expenses(user_id: int, year: Optional[int] = None,
                   month: Optional[int] = None) -> float:
    with get_conn() as conn:
        q = "SELECT COALESCE(SUM(amount),0) AS s FROM expenses WHERE user_id=?"
        params = [user_id]
        if year and month:
            q += " AND strftime('%Y',date)=? AND strftime('%m',date)=?"
            params += [str(year), f"{month:02d}"]
        return float(conn.execute(q, params).fetchone()["s"])


def total_balance_in(user_id: int, year: Optional[int] = None,
                     month: Optional[int] = None,
                     tx_types: Optional[list] = None) -> float:
    with get_conn() as conn:
        q = "SELECT COALESCE(SUM(amount),0) AS s FROM balance_transactions WHERE user_id=?"
        params = [user_id]
        if tx_types:
            q += f" AND tx_type IN ({','.join(['?']*len(tx_types))})"
            params.extend(tx_types)
        if year and month:
            q += " AND strftime('%Y',date)=? AND strftime('%m',date)=?"
            params.extend([str(year), f"{month:02d}"])
        return float(conn.execute(q, params).fetchone()["s"])


def available_balance(user_id: int) -> float:
    start = get_starting_balance(user_id)
    added = total_balance_in(user_id, tx_types=[TX_BALANCE_ADD])
    borrowed_in = total_balance_in(user_id, tx_types=[TX_BORROW_RECEIVED])
    friend_paid = total_balance_in(user_id, tx_types=[TX_FRIEND_RECEIVED])
    repaid_out = total_balance_in(user_id, tx_types=[TX_BORROW_REPAID])
    spent = total_expenses(user_id)
    return start + added + borrowed_in + friend_paid - repaid_out - spent


def month_summary(user_id: int, year: int, month: int) -> dict:
    added = total_balance_in(user_id, year, month, [TX_BALANCE_ADD])
    borrowed = total_balance_in(user_id, year, month, [TX_BORROW_RECEIVED])
    friend_in = total_balance_in(user_id, year, month, [TX_FRIEND_RECEIVED])
    repaid = total_balance_in(user_id, year, month, [TX_BORROW_REPAID])
    spent = total_expenses(user_id, year, month)
    return {
        "added": added, "borrowed_received": borrowed, "friend_received": friend_in,
        "repaid": repaid, "spent": spent,
        "net_flow": added + borrowed + friend_in - repaid - spent,
    }


def add_balance(user_id: int, amount: float, source: str,
                description: str = "", d: Optional[date] = None) -> int:
    d = d or date.today()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO balance_transactions(user_id,amount,tx_type,source,description,date) "
            "VALUES(?,?,?,?,?,?)",
            (user_id, float(amount), TX_BALANCE_ADD, source, description, _iso(d)),
        )
        return cur.lastrowid


def owed_by_friends(user_id: int) -> float:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount),0) AS s FROM debts "
            "WHERE user_id=? AND direction='lent' AND status='open'",
            (user_id,),
        ).fetchone()
        return float(row["s"])


def owed_to_others(user_id: int) -> float:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount),0) AS s FROM debts "
            "WHERE user_id=? AND direction='borrowed' AND status='open'",
            (user_id,),
        ).fetchone()
        return float(row["s"])
