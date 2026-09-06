import streamlit as st
from datetime import date
from components.cards import empty_state
from services.recurring_service import add_rule, list_rules, toggle_rule, delete_rule, run_due
from services.expense_service import list_categories
from database.database import get_setting
from utils.formatting import format_money


def _uid():
    return st.session_state["user_id"]


DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def render():
    uid = _uid()
    currency = get_setting(uid, "currency", "INR")

    st.markdown("<h1 style='margin-bottom:0'>🔁 Recurring</h1>", unsafe_allow_html=True)
    st.caption("Rent, subscriptions and other bills post themselves each cycle.")

    if st.button("Post any due now", key="run_now", type="secondary"):
        n = run_due(uid)
        if n:
            st.success(f"Posted {n} recurring expense(s).")
        else:
            st.info("Nothing due right now.")
        st.rerun()

    st.markdown("### New recurring rule")
    with st.form("recurring_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            amt = st.number_input("Amount", min_value=0.0, step=50.0, format="%.2f")
        with c2:
            cats = [c["name"] for c in list_categories(uid)]
            cat = st.selectbox("Category", cats)
        desc = st.text_input("Description",
                             placeholder="e.g. Netflix subscription / House rent")
        freq = st.radio("Frequency", ["monthly", "weekly"], horizontal=True)
        c3, c4 = st.columns(2)
        with c3:
            start = st.date_input("Start date", value=date.today())
        with c4:
            has_end = st.checkbox("Set end date?")
            end = st.date_input("End date", value=date.today(),
                                disabled=not has_end)
        if freq == "monthly":
            dom = st.number_input("Day of month", min_value=1, max_value=31,
                                  value=start.day)
            dow = None
        else:
            dow_label = st.selectbox("Day of week", DAYS,
                                     index=start.weekday())
            dow = DAYS.index(dow_label)
            dom = None
        if st.form_submit_button("Save rule", use_container_width=True):
            if amt <= 0 or not desc.strip():
                st.error("Amount and description are required.")
            else:
                add_rule(uid, amt, cat, desc.strip(), freq, start,
                         day_of_month=dom, day_of_week=dow,
                         end_date=end if has_end else None)
                st.success("Recurring rule saved. It will auto-post on due dates.")
                st.rerun()

    st.markdown("### Your rules")
    rules = list_rules(uid)
    if not rules:
        empty_state("No recurring rules yet",
                    "Add rent, streaming subscriptions or any repeating spend.", "🔁")
        return

    for r in rules:
        active = r["active"] == 1
        when = (f"Every month on day {r['day_of_month']}"
                if r["frequency"] == "monthly"
                else f"Every {DAYS[r['day_of_week']]}")
        status_pill = "🟢 Active" if active else "⚪ Paused"
        st.markdown(
            f"<div class='pf-card' style='margin-bottom:10px;'>"
            f"<div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;'>"
            f"<div><div style='font-weight:700;font-size:16px;'>{r['description'] or r['category']}</div>"
            f"<div style='color:var(--muted);font-size:12px;'>{r['category']} · {when} · from {r['start_date']}</div></div>"
            f"<div style='text-align:right;'>"
            f"<div style='font-family:Fraunces,serif;font-size:22px;font-weight:600;color:var(--primary);'>"
            f"{format_money(r['amount'], currency)}</div>"
            f"<div class='pf-chip' style='margin-top:4px;'>{status_pill}</div></div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
        a, b = st.columns(2)
        if a.button("Pause" if active else "Activate",
                    key=f"toggle_{r['id']}", use_container_width=True):
            toggle_rule(uid, r["id"])
            st.rerun()
        if b.button("Delete", key=f"delrule_{r['id']}", type="secondary",
                    use_container_width=True):
            delete_rule(uid, r["id"])
            st.rerun()
