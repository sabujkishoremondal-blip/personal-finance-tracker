"""User-scoped expense, category, debt and budget helpers."""
from datetime import date, datetime
from typing import Optional
from database.database import get_conn


def _iso(d) -> str:
    if isinstance(d, (datetime, date)):
        return d.isoformat()
    return str(d)


# ---------- expenses ----------
def add_expense(user_id: int, amount: float, category: str, description: str = "",
                d: Optional[date] = None, merchant: str = "",
                source: str = "manual", screenshot_path: str = "") -> int:
    d = d or date.today()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO expenses(user_id,amount,category,description,date,merchant,source,screenshot_path) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (user_id, float(amount), category, description, _iso(d), merchant,
             source, screenshot_path),
        )
        return cur.lastrowid


def update_expense(user_id: int, expense_id: int, **fields):
    if not fields:
        return
    if "date" in fields:
        fields["date"] = _iso(fields["date"])
    cols = ",".join(f"{k}=?" for k in fields)
    with get_conn() as conn:
        conn.execute(
            f"UPDATE expenses SET {cols} WHERE id=? AND user_id=?",
            (*fields.values(), expense_id, user_id),
        )


def delete_expense(user_id: int, expense_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM expenses WHERE id=? AND user_id=?",
                     (expense_id, user_id))


def list_expenses(user_id: int, year: Optional[int] = None,
                  month: Optional[int] = None, category: Optional[str] = None,
                  search: Optional[str] = None, sort: str = "date_desc",
                  limit: Optional[int] = None) -> list:
    q = "SELECT * FROM expenses WHERE user_id=?"
    params = [user_id]
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
        "date_desc": "date DESC, id DESC", "date_asc": "date ASC, id ASC",
        "amount_desc": "amount DESC", "amount_asc": "amount ASC",
    }.get(sort, "date DESC, id DESC")
    q += f" ORDER BY {order}"
    if limit:
        q += f" LIMIT {int(limit)}"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def category_totals(user_id: int, year: int, month: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT category, SUM(amount) AS total, COUNT(*) AS cnt "
            "FROM expenses WHERE user_id=? "
            "AND strftime('%Y',date)=? AND strftime('%m',date)=? "
            "GROUP BY category ORDER BY total DESC",
            (user_id, str(year), f"{month:02d}"),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------- categories ----------
def list_categories(user_id: int) -> list:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM categories WHERE user_id=? ORDER BY id",
            (user_id,),
        ).fetchall()]


def add_category(user_id: int, name: str, icon: str = "📦", color: str = "#8F002B"):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO categories(user_id,name,icon,color) VALUES(?,?,?,?)",
            (user_id, name, icon, color),
        )


def delete_category(user_id: int, name: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM categories WHERE user_id=? AND name=?",
                     (user_id, name))


def category_icon(user_id: int, name: str) -> str:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT icon FROM categories WHERE user_id=? AND name=?",
            (user_id, name),
        ).fetchone()
        return row["icon"] if row else "📦"


def monthly_totals(user_id: int, months: int = 6) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT strftime('%Y-%m', date) AS ym, SUM(amount) AS total "
            "FROM expenses WHERE user_id=? "
            "GROUP BY ym ORDER BY ym DESC LIMIT ?",
            (user_id, months),
        ).fetchall()
        return list(reversed([dict(r) for r in rows]))


# ---------- debts ----------
def add_debt(user_id: int, direction: str, person: str, amount: float,
             reason: str = "", d: Optional[date] = None) -> int:
    d = d or date.today()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO debts(user_id,direction,person,amount,reason,date) "
            "VALUES(?,?,?,?,?,?)",
            (user_id, direction, person, float(amount), reason, _iso(d)),
        )
        debt_id = cur.lastrowid
        if direction == "borrowed":
            conn.execute(
                "INSERT INTO balance_transactions(user_id,amount,tx_type,source,description,date,related_debt_id) "
                "VALUES(?,?,?,?,?,?,?)",
                (user_id, float(amount), "borrowed_received", person, reason, _iso(d), debt_id),
            )
        return debt_id


def settle_debt(user_id: int, debt_id: int) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM debts WHERE id=? AND user_id=?",
            (debt_id, user_id),
        ).fetchone()
        if not row or row["status"] == "settled":
            return False
        today_iso = date.today().isoformat()
        if row["direction"] == "borrowed":
            conn.execute(
                "INSERT INTO balance_transactions(user_id,amount,tx_type,source,description,date,related_debt_id) "
                "VALUES(?,?,?,?,?,?,?)",
                (user_id, float(row["amount"]), "borrowed_repaid", row["person"],
                 f"Repaid to {row['person']}", today_iso, debt_id),
            )
        else:
            conn.execute(
                "INSERT INTO balance_transactions(user_id,amount,tx_type,source,description,date,related_debt_id) "
                "VALUES(?,?,?,?,?,?,?)",
                (user_id, float(row["amount"]), "friend_repaid", row["person"],
                 f"Received from {row['person']}", today_iso, debt_id),
            )
        conn.execute(
            "UPDATE debts SET status='settled', settled_date=? WHERE id=? AND user_id=?",
            (today_iso, debt_id, user_id),
        )
        return True


def list_debts(user_id: int, direction: Optional[str] = None,
               status: Optional[str] = None) -> list:
    q = "SELECT * FROM debts WHERE user_id=?"
    params = [user_id]
    if direction:
        q += " AND direction=?"; params.append(direction)
    if status:
        q += " AND status=?"; params.append(status)
    q += " ORDER BY date DESC, id DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def delete_debt(user_id: int, debt_id: int):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM balance_transactions WHERE user_id=? AND related_debt_id=?",
            (user_id, debt_id),
        )
        conn.execute(
            "DELETE FROM debts WHERE user_id=? AND id=?",
            (user_id, debt_id),
        )


# ---------- balance transactions (read) ----------
def list_balance_transactions(user_id: int, year: Optional[int] = None,
                              month: Optional[int] = None) -> list:
    q = "SELECT * FROM balance_transactions WHERE user_id=?"
    params = [user_id]
    if year and month:
        q += " AND strftime('%Y',date)=? AND strftime('%m',date)=?"
        params += [str(year), f"{month:02d}"]
    q += " ORDER BY date DESC, id DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


# ---------- budgets ----------
def set_budget(user_id: int, year: int, month: int, category: str, amount: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO budgets(user_id,year,month,category,amount) VALUES(?,?,?,?,?) "
            "ON CONFLICT(user_id,year,month,category) DO UPDATE SET amount=excluded.amount",
            (user_id, year, month, category, float(amount)),
        )


def get_budgets(user_id: int, year: int, month: int) -> dict:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT category, amount FROM budgets WHERE user_id=? AND year=? AND month=?",
            (user_id, year, month),
        ).fetchall()
        return {r["category"]: float(r["amount"]) for r in rows}
