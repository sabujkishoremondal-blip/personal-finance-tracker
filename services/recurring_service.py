"""Recurring expense rules — auto-post when due on app load."""
from datetime import date, datetime, timedelta
from calendar import monthrange
from typing import Optional
from database.database import get_conn
from services.expense_service import add_expense


def add_rule(user_id: int, amount: float, category: str, description: str,
             frequency: str, start_date: date,
             day_of_month: Optional[int] = None,
             day_of_week: Optional[int] = None,
             end_date: Optional[date] = None) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO recurring_expenses(user_id,amount,category,description,frequency,"
            "day_of_month,day_of_week,start_date,end_date) VALUES(?,?,?,?,?,?,?,?,?)",
            (user_id, float(amount), category, description, frequency,
             day_of_month, day_of_week,
             start_date.isoformat(),
             end_date.isoformat() if end_date else None),
        )
        return cur.lastrowid


def list_rules(user_id: int, active_only: bool = False) -> list:
    q = "SELECT * FROM recurring_expenses WHERE user_id=?"
    params = [user_id]
    if active_only:
        q += " AND active=1"
    q += " ORDER BY id DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def toggle_rule(user_id: int, rule_id: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE recurring_expenses SET active = 1-active WHERE id=? AND user_id=?",
            (rule_id, user_id),
        )


def delete_rule(user_id: int, rule_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM recurring_expenses WHERE id=? AND user_id=?",
                     (rule_id, user_id))


def _due_dates(rule: dict, today: date) -> list[date]:
    """Return all dates on which this rule should have fired that haven't fired yet."""
    start = datetime.fromisoformat(rule["start_date"]).date()
    end = datetime.fromisoformat(rule["end_date"]).date() if rule["end_date"] else today
    last_run = datetime.fromisoformat(rule["last_run"]).date() if rule["last_run"] else None
    from_date = max(start, last_run + timedelta(days=1)) if last_run else start
    to_date = min(today, end)
    if from_date > to_date:
        return []

    dates = []
    if rule["frequency"] == "monthly":
        dom = rule["day_of_month"] or start.day
        # walk months from from_date to to_date
        y, m = from_date.year, from_date.month
        while (y, m) <= (to_date.year, to_date.month):
            last_day = monthrange(y, m)[1]
            d = date(y, m, min(dom, last_day))
            if from_date <= d <= to_date:
                dates.append(d)
            m += 1
            if m > 12:
                m = 1; y += 1
    elif rule["frequency"] == "weekly":
        dow = rule["day_of_week"] if rule["day_of_week"] is not None else start.weekday()
        d = from_date
        while d <= to_date:
            if d.weekday() == dow:
                dates.append(d)
            d += timedelta(days=1)
    return dates


def run_due(user_id: int) -> int:
    """Post any due recurring expenses. Returns count posted."""
    today = date.today()
    posted = 0
    for rule in list_rules(user_id, active_only=True):
        due = _due_dates(rule, today)
        for d in due:
            add_expense(user_id, rule["amount"], rule["category"],
                        rule["description"] or f"[Recurring] {rule['category']}",
                        d, merchant="", source="recurring")
            posted += 1
        if due:
            with get_conn() as conn:
                conn.execute(
                    "UPDATE recurring_expenses SET last_run=? WHERE id=?",
                    (due[-1].isoformat(), rule["id"]),
                )
    return posted
