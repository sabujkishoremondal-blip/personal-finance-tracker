import streamlit as st
from datetime import date
from components.cards import empty_state
from services.analytics_service import budget_progress
from services.expense_service import set_budget, list_categories
from services.recommendation_service import recommendations
from database.database import get_setting, get_conn
from utils.formatting import format_money, month_label, get_symbol


def render():
    currency = get_setting("currency", "INR")

    st.markdown("<h1 style='margin-bottom:0'>Budget &amp; Goals</h1>", unsafe_allow_html=True)
    st.caption("Set spending targets — you'll get warnings but never blocked.")

    today = date.today()
    c1, c2 = st.columns(2)
    with c1:
        year = st.number_input("Year", value=today.year, step=1, min_value=2000, max_value=2100,
                               key="budget_year")
    with c2:
        month = st.selectbox("Month", list(range(1, 13)),
                             index=today.month - 1,
                             format_func=lambda m: month_label(int(year), m),
                             key="budget_month")

    st.markdown("### Set budgets")
    with st.container():
        st.markdown('<div class="pf-card">', unsafe_allow_html=True)
        # existing budgets
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT category, amount FROM budgets WHERE year=? AND month=?",
                (int(year), int(month)),
            ).fetchall()
            existing = {r["category"]: float(r["amount"]) for r in rows}

        with st.form(f"budget_form_{year}_{month}"):
            total = st.number_input(
                "Total monthly budget",
                min_value=0.0, step=100.0, format="%.2f",
                value=float(existing.get("TOTAL", 0.0)),
            )
            st.markdown("**Per-category budgets** (optional)")
            cats = list_categories()
            cat_inputs = {}
            cols = st.columns(2)
            for i, c in enumerate(cats):
                with cols[i % 2]:
                    cat_inputs[c["name"]] = st.number_input(
                        f"{c['icon']} {c['name']}",
                        min_value=0.0, step=50.0, format="%.2f",
                        value=float(existing.get(c["name"], 0.0)),
                        key=f"bud_{c['name']}",
                    )
            if st.form_submit_button("Save budgets", use_container_width=True):
                if total > 0:
                    set_budget(int(year), int(month), "TOTAL", total)
                for name, amt in cat_inputs.items():
                    if amt > 0:
                        set_budget(int(year), int(month), name, amt)
                st.success("Budgets saved.")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Progress")
    prog = budget_progress(int(year), int(month))
    if not prog:
        empty_state("No budgets yet", "Set a budget above to track your progress.", "🎯")
    else:
        # order: TOTAL first
        prog.sort(key=lambda x: (0 if x["category"] == "TOTAL" else 1, -x["budget"]))
        for p in prog:
            over = p["over"]
            label = "Total" if p["category"] == "TOTAL" else p["category"]
            color = "var(--danger)" if over else "var(--primary)"
            pct = min(p["pct"], 100)
            bar = (
                f"<div style='background:var(--chip-bg);border-radius:999px;height:10px;overflow:hidden;'>"
                f"<div style='width:{pct}%;height:100%;background:{color};'></div></div>"
            )
            status_msg = (
                f"<span style='color:var(--danger);font-weight:700;'>{format_money(p['spent']-p['budget'], currency)} over budget</span>"
                if over
                else f"<span style='color:var(--text-soft);'>{format_money(p['remaining'], currency)} remaining</span>"
            )
            st.markdown(
                f"<div class='pf-card' style='margin-bottom:10px;'>"
                f"<div style='display:flex;justify-content:space-between;margin-bottom:6px;'>"
                f"<div style='font-weight:700;'>{label}</div>"
                f"<div style='font-family:Fraunces,serif;font-weight:600;'>"
                f"{format_money(p['spent'], currency)} / {format_money(p['budget'], currency)}</div></div>"
                f"{bar}"
                f"<div style='display:flex;justify-content:space-between;margin-top:6px;font-size:12px;'>"
                f"<span style='color:var(--muted);'>{p['pct']:.0f}% used</span>{status_msg}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("### Suggested next-month targets")
    rec = recommendations(int(year), int(month))
    if rec["insufficient"]:
        empty_state("Not enough data", rec["message"], "🎯")
        return
    with st.container():
        st.markdown('<div class="pf-card">', unsafe_allow_html=True)
        st.markdown(
            f"Keep total spending below **{format_money(rec['target_total'], currency)}** next month.",
            unsafe_allow_html=True,
        )
        for t in rec["targets"]:
            st.markdown(
                f"<div class='cat-row'><div class='left'><div class='name'>{t['category']}</div></div>"
                f"<div class='amt'>{format_money(t['target'], currency)}</div></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
