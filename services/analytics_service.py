"""User-scoped analytics."""
from datetime import date
from calendar import monthrange
from services.expense_service import category_totals, monthly_totals, get_budgets
from services.balance_service import month_summary


def month_report(user_id: int, year: int, month: int) -> dict:
    cats = category_totals(user_id, year, month)
    total = sum(c["total"] for c in cats)
    count = sum(c["cnt"] for c in cats)
    ms = month_summary(user_id, year, month)
    highest = cats[0] if cats else None
    days_elapsed = _days_in_month_so_far(year, month)
    avg_daily = total / days_elapsed if days_elapsed else 0
    total_funds = ms["added"] + ms["borrowed_received"] + ms["friend_received"]
    return {
        "total_spent": total, "total_funds": total_funds,
        "remaining": total_funds - total, "avg_daily": avg_daily,
        "highest_category": highest["category"] if highest else "—",
        "highest_amount": highest["total"] if highest else 0,
        "num_expenses": count, "categories": cats,
    }


def _days_in_month_so_far(year: int, month: int) -> int:
    today = date.today()
    if year == today.year and month == today.month:
        return today.day
    return monthrange(year, month)[1]


def compare_last_months(user_id: int, months: int = 6) -> dict:
    data = monthly_totals(user_id, months=months)
    if len(data) < 2:
        return {"data": data, "change_pct": None, "highest": None,
                "lowest": None, "avg": None, "biggest_driver": None}
    totals = [d["total"] for d in data]
    avg = sum(totals) / len(totals)
    highest = max(data, key=lambda x: x["total"])
    lowest = min(data, key=lambda x: x["total"])
    prev, curr = data[-2]["total"], data[-1]["total"]
    change_pct = ((curr - prev) / prev * 100) if prev else 0
    cy, cm = map(int, data[-1]["ym"].split("-"))
    py, pm = map(int, data[-2]["ym"].split("-"))
    curr_cats = {c["category"]: c["total"] for c in category_totals(user_id, cy, cm)}
    prev_cats = {c["category"]: c["total"] for c in category_totals(user_id, py, pm)}
    diffs = {k: curr_cats.get(k, 0) - prev_cats.get(k, 0)
             for k in set(curr_cats) | set(prev_cats)}
    biggest_driver = max(diffs.items(), key=lambda x: x[1])[0] if diffs else None
    return {"data": data, "change_pct": change_pct, "highest": highest,
            "lowest": lowest, "avg": avg, "biggest_driver": biggest_driver}


def budget_progress(user_id: int, year: int, month: int) -> list:
    budgets = get_budgets(user_id, year, month)
    cats = {c["category"]: c["total"] for c in category_totals(user_id, year, month)}
    out = []
    for cat, budget in budgets.items():
        spent = sum(cats.values()) if cat == "TOTAL" else cats.get(cat, 0)
        pct = (spent / budget * 100) if budget else 0
        out.append({"category": cat, "budget": budget, "spent": spent,
                    "pct": pct, "remaining": budget - spent,
                    "over": spent > budget})
    return out
