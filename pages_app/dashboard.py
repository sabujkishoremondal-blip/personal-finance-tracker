import streamlit as st
from datetime import date
from components.cards import hero_balance, stat_card, transaction_card, empty_state
from components.charts import donut
from services.balance_service import (
    available_balance, get_starting_balance, month_summary,
    owed_by_friends, owed_to_others,
)
from services.expense_service import (
    list_expenses, category_totals, category_icon,
)
from database.database import get_setting
from utils.formatting import format_money, greeting, month_label, get_symbol


def render():
    uid = st.session_state["user_id"]
    currency = get_setting(uid, "currency", "INR")
    sym = get_symbol(currency)
    today = date.today()
    y, m = today.year, today.month

    user = get_setting(uid, "user_name", st.session_state.get("user_name", "You"))
    st.markdown(
        f"<div style='display:flex; justify-content:space-between; align-items:baseline;'>"
        f"<div><div style='color:var(--muted); font-size:14px; font-weight:600;'>{greeting()} 👋</div>"
        f"<h1 style='margin:2px 0 0; font-size:32px;'>{month_label(y, m)}</h1></div>"
        f"<div class='pf-chip'>{user}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    ms = month_summary(uid, y, m)
    starting = get_starting_balance(uid)
    avail = available_balance(uid)
    hero_balance(avail, starting, ms["added"], ms["spent"], currency)

    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("This Month Spent", format_money(ms["spent"], currency),
                  f"{len(list_expenses(uid, y, m))} expenses")
    with c2:
        stat_card("Added", format_money(ms["added"], currency), "money in")
    with c3:
        stat_card("You Owe", format_money(owed_to_others(uid), currency), "borrowed")
    with c4:
        stat_card("Friends Owe", format_money(owed_by_friends(uid), currency), "to receive")

    st.write("")
    st.markdown("### Quick actions")
    q1, q2, q3, q4 = st.columns(4)
    if q1.button("＋ Add Expense", key="qa_expense", use_container_width=True):
        st.session_state["_pending_nav"] = "Expenses"; st.rerun()
    if q2.button("＋ Add Balance", key="qa_balance", use_container_width=True):
        st.session_state["_pending_nav"] = "Expenses"; st.rerun()
    if q3.button("🤝 Borrow / Lend", key="qa_borrow", use_container_width=True):
        st.session_state["_pending_nav"] = "Borrow & Lend"; st.rerun()
    if q4.button("💬 Quick Add", key="qa_chat", use_container_width=True):
        st.session_state["_pending_nav"] = "Quick Add"; st.rerun()

    st.write("")
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown("### This month by category")
        cats = category_totals(uid, y, m)
        if cats:
            st.markdown('<div class="pf-card">', unsafe_allow_html=True)
            fig = donut(cats, sym)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            total = sum(c["total"] for c in cats)
            for c in cats:
                pct = c["total"] / total * 100 if total else 0
                icon = category_icon(uid, c["category"])
                st.markdown(
                    f'<div class="cat-row"><div class="left">'
                    f'<span class="icon">{icon}</span>'
                    f'<div><div class="name">{c["category"]}</div>'
                    f'<div style="font-size:12px;color:var(--muted);">{pct:.0f}% · {c["cnt"]} txn</div></div>'
                    f'</div><div class="amt">{format_money(c["total"], currency)}</div></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            empty_state("No expenses this month yet",
                        "Add your first expense to see insights.", "🍽️")

    with right:
        st.markdown("### Recent transactions")
        recent = list_expenses(uid, limit=6)
        if not recent:
            empty_state("Nothing to show yet",
                        "Your recent transactions will appear here.", "🧾")
        else:
            for e in recent:
                icon = category_icon(uid, e["category"])
                transaction_card(icon, e["description"] or e["category"],
                                 f"{e['category']} · {e['date']}",
                                 format_money(e["amount"], currency), positive=False)
