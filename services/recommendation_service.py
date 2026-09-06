"""Rule-based recommendation engine — 'How Can I Save?'"""
from datetime import date
from services.expense_service import category_totals, monthly_totals, list_expenses
from services.analytics_service import compare_last_months


def recommendations(year: int, month: int) -> dict:
    cats = category_totals(year, month)
    total = sum(c["total"] for c in cats)
    if total == 0 or len(list_expenses()) < 5:
        return {
            "insufficient": True,
            "message": "We need a little more spending history before we can identify strong patterns.",
            "tips": [],
            "target_total": 0,
            "targets": [],
            "potential_saving": 0,
        }

    # Historical averages across last up to 6 months
    hist = monthly_totals(months=6)
    tips = []
    potential = 0
    targets = []

    # 1) Biggest category > 30% of spend -> suggest 20% cut
    if cats:
        top = cats[0]
        share = top["total"] / total * 100 if total else 0
        cut = round(top["total"] * 0.2)
        if share >= 25 and top["total"] > 100:
            tips.append({
                "title": f"{top['category']} is your biggest expense",
                "body": f"You spent ₹{top['total']:.0f} on {top['category']} this month "
                        f"({share:.0f}% of total). Try trimming it by 20%.",
                "suggested_target": round(top["total"] * 0.8),
                "potential_saving": cut,
            })
            potential += cut

    # 2) Month-over-month spikes per category
    if len(hist) >= 2:
        prev_ym = hist[-2]["ym"]
        py, pm = map(int, prev_ym.split("-"))
        prev_cats = {c["category"]: c["total"] for c in category_totals(py, pm)}
        for c in cats:
            prev = prev_cats.get(c["category"], 0)
            if prev > 0:
                delta_pct = (c["total"] - prev) / prev * 100
                if delta_pct >= 25 and c["total"] > 100:
                    save = round((c["total"] - prev) * 0.5)
                    tips.append({
                        "title": f"{c['category']} spending jumped {delta_pct:.0f}%",
                        "body": f"Up from ₹{prev:.0f} last month to ₹{c['total']:.0f}. "
                                f"Bring it closer to last month's level.",
                        "suggested_target": round(prev * 1.1),
                        "potential_saving": save,
                    })
                    potential += save

    # 3) High-frequency category (many small expenses)
    for c in cats:
        if c["cnt"] >= 8 and c["total"] > 200:
            avg = c["total"] / c["cnt"]
            save = round(c["total"] * 0.15)
            tips.append({
                "title": f"You bought {c['category']} {c['cnt']} times",
                "body": f"Avg ₹{avg:.0f} per purchase. Reducing 2–3 of these can save ~₹{save}.",
                "suggested_target": round(c["total"] * 0.85),
                "potential_saving": save,
            })
            potential += save
            break

    # 4) Unusually large single transactions
    all_exp = list_expenses(year=year, month=month)
    if all_exp:
        amounts = sorted([e["amount"] for e in all_exp], reverse=True)
        if amounts and amounts[0] > (total / max(len(amounts), 1)) * 3:
            biggest = amounts[0]
            tips.append({
                "title": "Watch out for outlier expenses",
                "body": f"Your biggest single expense was ₹{biggest:.0f}. "
                        "Try planning larger purchases in advance.",
                "suggested_target": 0,
                "potential_saving": 0,
            })

    # Suggest per-category targets (10-20% cut on top categories)
    for c in cats:
        cut = 0.85 if c["total"] > (total * 0.2) else 0.95
        targets.append({"category": c["category"], "target": round(c["total"] * cut)})
    target_total = sum(t["target"] for t in targets)

    return {
        "insufficient": False,
        "tips": tips[:5],
        "targets": targets,
        "target_total": target_total,
        "potential_saving": potential,
        "current_total": total,
    }
