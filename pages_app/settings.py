import io
import json
import pandas as pd
import streamlit as st
from datetime import date
from database.database import get_conn, get_setting, set_setting, reset_db, init_db
from services.expense_service import list_categories, add_category, delete_category
from utils.constants import CURRENCIES


def render():
    st.markdown("<h1 style='margin-bottom:0'>Settings</h1>", unsafe_allow_html=True)
    st.caption("Personalize the app, manage categories and back up your data.")

    with st.container():
        st.markdown('<div class="pf-card">', unsafe_allow_html=True)
        st.markdown("#### Profile & preferences")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Your name", value=get_setting("user_name", "You"))
        with c2:
            cur = st.selectbox(
                "Currency", list(CURRENCIES.keys()),
                index=list(CURRENCIES.keys()).index(get_setting("currency", "INR")),
                format_func=lambda x: f"{CURRENCIES[x]}  {x}",
            )
        c3, c4 = st.columns(2)
        with c3:
            theme = st.radio("Theme", ["light", "dark"],
                             index=0 if get_setting("theme", "light") == "light" else 1,
                             horizontal=True)
        with c4:
            start = st.number_input("Default starting balance", min_value=-1_000_000.0,
                                    step=100.0, format="%.2f",
                                    value=float(get_setting("starting_balance", "0")))
        if st.button("Save preferences"):
            set_setting("user_name", name.strip() or "You")
            set_setting("currency", cur)
            set_setting("theme", theme)
            set_setting("starting_balance", start)
            st.session_state["theme"] = theme
            st.success("Preferences saved.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    with st.container():
        st.markdown('<div class="pf-card">', unsafe_allow_html=True)
        st.markdown("#### Categories")
        cats = list_categories()
        for c in cats:
            cc1, cc2, cc3 = st.columns([1, 6, 2])
            with cc1: st.markdown(f"<div style='font-size:26px'>{c['icon']}</div>", unsafe_allow_html=True)
            with cc2: st.markdown(f"**{c['name']}**")
            with cc3:
                if st.button("Delete", key=f"delcat_{c['id']}", type="secondary",
                             use_container_width=True):
                    delete_category(c["name"])
                    st.rerun()
        with st.form("add_cat_form", clear_on_submit=True):
            a, b, c = st.columns([3, 1, 1])
            with a: new_name = st.text_input("New category name")
            with b: new_icon = st.text_input("Icon", value="📦")
            with c: st.markdown("&nbsp;", unsafe_allow_html=True)
            if st.form_submit_button("Add category"):
                if new_name.strip():
                    add_category(new_name.strip(), new_icon or "📦")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    with st.container():
        st.markdown('<div class="pf-card">', unsafe_allow_html=True)
        st.markdown("#### Data export & import")
        # Export
        with get_conn() as conn:
            data = {
                "expenses": [dict(r) for r in conn.execute("SELECT * FROM expenses").fetchall()],
                "balance_transactions": [dict(r) for r in conn.execute("SELECT * FROM balance_transactions").fetchall()],
                "debts": [dict(r) for r in conn.execute("SELECT * FROM debts").fetchall()],
                "categories": [dict(r) for r in conn.execute("SELECT * FROM categories").fetchall()],
                "budgets": [dict(r) for r in conn.execute("SELECT * FROM budgets").fetchall()],
                "app_settings": [dict(r) for r in conn.execute("SELECT * FROM app_settings").fetchall()],
            }
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "⬇️  Export JSON backup",
                data=json.dumps(data, indent=2, default=str).encode(),
                file_name=f"finance_backup_{date.today()}.json",
                mime="application/json",
                use_container_width=True,
            )
        with c2:
            if data["expenses"]:
                df = pd.DataFrame(data["expenses"])
                buf = io.StringIO()
                df.to_csv(buf, index=False)
                st.download_button(
                    "⬇️  Export expenses CSV",
                    data=buf.getvalue().encode(),
                    file_name=f"expenses_{date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                st.button("⬇️  Export expenses CSV", disabled=True, use_container_width=True)

        up = st.file_uploader("Import JSON backup", type=["json"], key="import_json")
        if up and st.button("Restore from backup"):
            try:
                payload = json.loads(up.getvalue().decode())
                with get_conn() as conn:
                    for tbl in ["expenses", "balance_transactions", "debts",
                                "categories", "budgets", "app_settings"]:
                        conn.execute(f"DELETE FROM {tbl}")
                    for tbl, rows in payload.items():
                        for r in rows:
                            cols = ",".join(r.keys())
                            placeholders = ",".join("?" * len(r))
                            conn.execute(
                                f"INSERT INTO {tbl}({cols}) VALUES({placeholders})",
                                tuple(r.values()),
                            )
                st.success("Backup restored.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to restore: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    with st.container():
        st.markdown('<div class="pf-card">', unsafe_allow_html=True)
        st.markdown("#### Danger zone")
        st.caption("This deletes ALL your data and resets the database.")
        if st.session_state.get("confirm_reset"):
            st.warning("Are you absolutely sure? This cannot be undone.")
            a, b = st.columns(2)
            if a.button("Yes, reset everything", use_container_width=True):
                reset_db()
                st.session_state.clear()
                st.success("Database reset.")
                st.rerun()
            if b.button("Cancel", type="secondary", use_container_width=True):
                st.session_state.pop("confirm_reset", None)
                st.rerun()
        else:
            if st.button("Reset database", type="secondary"):
                st.session_state["confirm_reset"] = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
