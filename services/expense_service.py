from datetime import date, datetime
from typing import Optional
from database.database import get_conn


def _iso(d) -> str:
    if isinstance(d, (datetime, date)):
        return d.isoformat()
    return str(d)


def add_expense(amount: float, category: str, description: str = "",
                d: Optional[date] = None, merchant: str = "",
                source: str = "manual", screenshot_path: str = "") -> int:
    d = d or date.today()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO expenses(amount,category,description,date,merchant,source,screenshot_path) "
            "VALUES(?,?,?,?,?,?,?)",
            (float(amount), category, description, _iso(d), merchant, source, screenshot_path),
        )
        return cur.lastrowid


def update_expense(expense_id: int, **fields):
    if not fields:
        return
    cols = ",".join(f"{k}=?" for k in fields)
    vals = list(fields.values())
    if "date" in fields:
        idx = list(fields.keys()).index("date")
        vals[idx] = _iso(vals[idx])
    with get_conn() as conn:
        conn.execute(f"UPDATE expenses SET {cols} WHERE id=?", (*vals, expense_id))


def delete_expense(expense_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))


def list_expenses(year: Optional[int] = None, month: Optional[int] = None,
                  category: Optional[str] = None, search: Optional[str] = None,
                  sort: str = "date_desc", limit: Optional[int] = None) -> list:
    q = "SELECT * FROM expenses WHERE 1=1"
    params = []
    if year and month:
        q += " AND strftime('%Y',date)=? AND strftime('%m',date)=?"
        params += [str(year), f"{month:02d}"]
    if category and category != "All":
        q += " AND category=?"
        params.append(category)
    if search:
        q += " AND (description LIKE ? OR merchant LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    order = {
        "date_desc": "date DESC, id DESC",
        "date_asc": "date ASC, id ASC",
        "amount_desc": "amount DESC",
        "amount_asc": "amount ASC",
    }.get(sort, "date DESC, id DESC")
    q += f" ORDER BY {order}"
    if limit:
        q += f" LIMIT {int(limit)}"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def category_totals(year: int, month: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT category, SUM(amount) AS total, COUNT(*) AS cnt FROM expenses "
            "WHERE strftime('%Y',date)=? AND strftime('%m',date)=? "
            "GROUP BY category ORDER BY total DESC",
            (str(year), f"{month:02d}"),
        ).fetchall()
        return [dict(r) for r in rows]


def list_categories() -> list:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM categories ORDER BY id").fetchall()]


def add_category(name: str, icon: str = "📦", color: str = "#8F002B"):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO categories(name,icon,color) VALUES(?,?,?)",
                     (name, icon, color))


def delete_category(name: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM categories WHERE name=?", (name,))


def category_icon(name: str) -> str:
    with get_conn() as conn:
        row = conn.execute("SELECT icon FROM categories WHERE name=?", (name,)).fetchone()
        return row["icon"] if row else "📦"


def monthly_totals(months: int = 6) -> list:
    """Returns spending totals for last N months (most recent last)."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT strftime('%Y-%m', date) AS ym, SUM(amount) AS total "
            "FROM expenses GROUP BY ym ORDER BY ym DESC LIMIT ?",
            (months,),
        ).fetchall()
        return list(reversed([dict(r) for r in rows]))


# Debts
def add_debt(direction: str, person: str, amount: float, reason: str = "",
             d: Optional[date] = None) -> int:
    d = d or date.today()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO debts(direction,person,amount,reason,date) VALUES(?,?,?,?,?)",
            (direction, person, float(amount), reason, _iso(d)),
        )
        debt_id = cur.lastrowid
        if direction == "borrowed":
            # money enters our wallet
            conn.execute(
                "INSERT INTO balance_transactions(amount,tx_type,source,description,date,related_debt_id) "
                "VALUES(?,?,?,?,?,?)",
                (float(amount), "borrowed_received", person, reason, _iso(d), debt_id),
            )
        return debt_id


def settle_debt(debt_id: int) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM debts WHERE id=?", (debt_id,)).fetchone()
        if not row or row["status"] == "settled":
            return False
        today_iso = date.today().isoformat()
        if row["direction"] == "borrowed":
            # repay: money leaves wallet
            conn.execute(
                "INSERT INTO balance_transactions(amount,tx_type,source,description,date,related_debt_id) "
                "VALUES(?,?,?,?,?,?)",
                (float(row["amount"]), "borrowed_repaid", row["person"],
                 f"Repaid to {row['person']}", today_iso, debt_id),
            )
        else:  # lent -> mark as received
            conn.execute(
                "INSERT INTO balance_transactions(amount,tx_type,source,description,date,related_debt_id) "
                "VALUES(?,?,?,?,?,?)",
                (float(row["amount"]), "friend_repaid", row["person"],
                 f"Received from {row['person']}", today_iso, debt_id),
            )
        conn.execute("UPDATE debts SET status='settled', settled_date=? WHERE id=?",
                     (today_iso, debt_id))
        return True


def list_debts(direction: Optional[str] = None, status: Optional[str] = None) -> list:
    q = "SELECT * FROM debts WHERE 1=1"
    params = []
    if direction:
        q += " AND direction=?"
        params.append(direction)
    if status:
        q += " AND status=?"
        params.append(status)
    q += " ORDER BY date DESC, id DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def delete_debt(debt_id: int):
    with get_conn() as conn:
        # remove associated balance transactions
        conn.execute("DELETE FROM balance_transactions WHERE related_debt_id=?", (debt_id,))
        conn.execute("DELETE FROM debts WHERE id=?", (debt_id,))


# Balance transactions listing
def list_balance_transactions(year: Optional[int] = None, month: Optional[int] = None) -> list:
    q = "SELECT * FROM balance_transactions WHERE 1=1"
    params = []
    if year and month:
        q += " AND strftime('%Y',date)=? AND strftime('%m',date)=?"
        params += [str(year), f"{month:02d}"]
    q += " ORDER BY date DESC, id DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


# Budgets
def set_budget(year: int, month: int, category: str, amount: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO budgets(year,month,category,amount) VALUES(?,?,?,?) "
            "ON CONFLICT(year,month,category) DO UPDATE SET amount=excluded.amount",
            (year, month, category, float(amount)),
        )


def get_budgets(year: int, month: int) -> dict:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT category, amount FROM budgets WHERE year=? AND month=?",
            (year, month),
        ).fetchall()
        return {r["category"]: float(r["amount"]) for r in rows}
