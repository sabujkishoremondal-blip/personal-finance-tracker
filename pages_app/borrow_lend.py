import streamlit as st
from datetime import date
from components.cards import stat_card, empty_state
from services.expense_service import add_debt, settle_debt, list_debts, delete_debt
from services.balance_service import owed_by_friends, owed_to_others, available_balance
from database.database import get_setting
from utils.formatting import format_money, get_symbol


def render():
    currency = get_setting("currency", "INR")

    st.markdown("<h1 style='margin-bottom:0'>Borrow &amp; Lend</h1>", unsafe_allow_html=True)
    st.caption("Track money you borrowed and money friends owe you.")

    owe_them = owed_to_others()
    owe_you = owed_by_friends()
    net = owe_you - owe_them

    c1, c2, c3 = st.columns(3)
    with c1: stat_card("You Owe", format_money(owe_them, currency), "borrowed")
    with c2: stat_card("Friends Owe You", format_money(owe_you, currency), "to receive")
    with c3: stat_card("Net To Receive", format_money(net, currency),
                        "positive = they owe more")

    st.write("")
    tab_bor, tab_lent, tab_add = st.tabs(["I Borrowed", "Friends Owe Me", "＋ Add Entry"])

    with tab_bor:
        items = list_debts(direction="borrowed")
        _render_list(items, currency, "borrowed")

    with tab_lent:
        items = list_debts(direction="lent")
        _render_list(items, currency, "lent")

    with tab_add:
        _add_form(currency)


def _render_list(items, currency, direction):
    if not items:
        msg = "You haven't borrowed anything yet." if direction == "borrowed" \
              else "No friends owe you money yet."
        empty_state(msg, "Use the 'Add Entry' tab to record one.", "🤝")
        return

    for it in items:
        settled = it["status"] == "settled"
        card_color = "var(--success)" if settled else "var(--primary)"
        action_label = "Mark as Repaid" if direction == "borrowed" else "Mark as Received"
        status_pill = "✅ Settled" if settled else "🕓 Open"

        st.markdown(
            f"<div class='pf-card' style='margin-bottom:10px;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;'>"
            f"<div><div style='font-weight:700;font-size:18px;'>{it['person']}</div>"
            f"<div style='color:var(--muted);font-size:12px;'>{it['reason'] or '—'} · {it['date']}</div></div>"
            f"<div style='text-align:right;'>"
            f"<div style='font-family:Fraunces,serif;font-weight:600;font-size:22px;color:{card_color};'>"
            f"{format_money(it['amount'], currency)}</div>"
            f"<div class='pf-chip' style='margin-top:4px;'>{status_pill}</div></div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
        if not settled:
            cc1, cc2 = st.columns([2, 1])
            with cc1:
                confirm_key = f"confirm_{it['id']}"
                if st.session_state.get(confirm_key):
                    warn_msg = (
                        f"Repay {format_money(it['amount'], currency)} to {it['person']}? "
                        "This will reduce your available balance."
                        if direction == "borrowed"
                        else f"Did you receive {format_money(it['amount'], currency)} "
                             f"from {it['person']}? This will add to your balance."
                    )
                    st.warning(warn_msg)
                    a, b = st.columns(2)
                    if a.button("Confirm", key=f"confirm_yes_{it['id']}", use_container_width=True):
                        settle_debt(it["id"])
                        st.session_state.pop(confirm_key, None)
                        st.success("Updated.")
                        st.rerun()
                    if b.button("Cancel", key=f"confirm_no_{it['id']}",
                                use_container_width=True, type="secondary"):
                        st.session_state.pop(confirm_key, None)
                        st.rerun()
                else:
                    if st.button(action_label, key=f"settle_{it['id']}"):
                        st.session_state[confirm_key] = True
                        st.rerun()
            with cc2:
                if st.button("Delete", key=f"del_debt_{it['id']}", type="secondary",
                             use_container_width=True):
                    delete_debt(it["id"])
                    st.success("Deleted.")
                    st.rerun()


def _add_form(currency):
    st.markdown('<div class="pf-card">', unsafe_allow_html=True)
    with st.form("add_debt_form", clear_on_submit=True):
        direction = st.radio("Type", ["I Borrowed", "Friend Owes Me"], horizontal=True)
        c1, c2 = st.columns(2)
        with c1:
            person = st.text_input("Person")
        with c2:
            amt = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
        reason = st.text_input("Reason (optional)")
        dt = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Save", use_container_width=True)
        if submitted:
            if not person.strip() or amt <= 0:
                st.error("Person and a positive amount are required.")
            else:
                d_val = "borrowed" if direction == "I Borrowed" else "lent"
                add_debt(d_val, person.strip(), amt, reason, dt)
                st.success("Saved.")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
