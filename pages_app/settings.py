import io
import json
import pandas as pd
import streamlit as st
from datetime import date
from database.database import get_conn, get_setting, set_setting, reset_user_data
from services.expense_service import list_categories, add_category, delete_category
from services.auth_service import change_password, update_profile
from utils.constants import CURRENCIES


def _uid():
    return st.session_state["user_id"]


def render():
    uid = _uid()

    st.markdown("<h1 style='margin-bottom:0'>Settings</h1>", unsafe_allow_html=True)
    st.caption("Personalize your account, manage categories and back up your data.")

    _profile_section(uid)
    st.write("")
    _whatsapp_section(uid)
    st.write("")
    _categories_section(uid)
    st.write("")
    _data_section(uid)
    st.write("")
    _password_section(uid)
    st.write("")
    _danger_section(uid)


def _profile_section(uid):
    st.markdown('<div class="pf-card">', unsafe_allow_html=True)
    st.markdown("#### Profile & preferences")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Your name",
                             value=get_setting(uid, "user_name", "You"))
    with c2:
        cur = st.selectbox(
            "Currency", list(CURRENCIES.keys()),
            index=list(CURRENCIES.keys()).index(get_setting(uid, "currency", "INR")),
            format_func=lambda x: f"{CURRENCIES[x]}  {x}",
        )
    c3, c4 = st.columns(2)
    with c3:
        theme = st.radio("Theme", ["light", "dark"],
                         index=0 if get_setting(uid, "theme", "light") == "light" else 1,
                         horizontal=True, key="settings_theme_radio")
    with c4:
        start = st.number_input("Default starting balance",
                                min_value=-1_000_000.0, step=100.0, format="%.2f",
                                value=float(get_setting(uid, "starting_balance", "0")))
    if st.button("Save preferences"):
        set_setting(uid, "user_name", name.strip() or "You")
        set_setting(uid, "currency", cur)
        set_setting(uid, "theme", theme)
        set_setting(uid, "starting_balance", start)
        update_profile(uid, name=name.strip())
        st.session_state["theme"] = theme
        st.session_state["user_name"] = name.strip() or "You"
        st.success("Preferences saved.")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _whatsapp_section(uid):
    from services.auth_service import get_user_by_id
    user = get_user_by_id(uid)
    st.markdown('<div class="pf-card">', unsafe_allow_html=True)
    st.markdown("#### 💬 WhatsApp bot")
    st.caption("Link your WhatsApp number so future messages to the bot are matched to "
               "your account. In-app **Quick Add** already works with the same message format.")
    number = st.text_input(
        "WhatsApp number (E.164 format, e.g. +919876543210)",
        value=user.get("whatsapp_number", "") or "",
        placeholder="+91XXXXXXXXXX",
    )
    if st.button("Save WhatsApp number"):
        update_profile(uid, whatsapp_number=number.strip())
        st.success("WhatsApp number saved.")

    st.markdown(
        "<div class='pf-chip' style='margin-top:10px;'>MOCKED — Twilio credentials required to enable live receiving</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "To go live: sign up for the free Twilio WhatsApp Sandbox, then set the webhook "
        "URL to `<your-app>/whatsapp/inbound` (endpoint already scaffolded in "
        "`webhook_server.py`). Add `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` env vars "
        "and restart. Meanwhile, the **Quick Add** page in the sidebar accepts the "
        "exact same message format."
    )
    st.markdown("</div>", unsafe_allow_html=True)


def _categories_section(uid):
    st.markdown('<div class="pf-card">', unsafe_allow_html=True)
    st.markdown("#### Categories")
    for c in list_categories(uid):
        c1, c2, c3 = st.columns([1, 6, 2])
        c1.markdown(f"<div style='font-size:26px'>{c['icon']}</div>",
                    unsafe_allow_html=True)
        c2.markdown(f"**{c['name']}**")
        if c3.button("Delete", key=f"delcat_{c['id']}", type="secondary",
                     use_container_width=True):
            delete_category(uid, c["name"])
            st.rerun()
    st.markdown("**Add new category**")
    with st.form("add_cat_form", clear_on_submit=True):
        a, b = st.columns([3, 1])
        with a:
            new_name = st.text_input(
                "Category name",
                placeholder="e.g. Groceries, Transport, Health, Bills",
                label_visibility="collapsed",
                key="new_cat_name",
            )
        with b:
            new_icon = st.text_input(
                "Icon",
                value="📦",
                max_chars=4,
                label_visibility="collapsed",
                key="new_cat_icon",
            )
        st.caption("Tip: paste any emoji for the icon (🏠 🚗 💊 🎁 …)")
        if st.form_submit_button("＋ Add category", use_container_width=True):
            name = new_name.strip()
            if not name:
                st.error("Please enter a category name.")
            elif name.lower() in [c["name"].lower() for c in list_categories(uid)]:
                st.error(f"'{name}' already exists.")
            else:
                add_category(uid, name, new_icon.strip() or "📦")
                st.success(f"Added '{name}'.")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _data_section(uid):
    st.markdown('<div class="pf-card">', unsafe_allow_html=True)
    st.markdown("#### Data export & import")
    with get_conn() as conn:
        data = {}
        for tbl in ["expenses", "balance_transactions", "debts",
                    "categories", "budgets", "app_settings",
                    "recurring_expenses", "whatsapp_messages"]:
            data[tbl] = [dict(r) for r in conn.execute(
                f"SELECT * FROM {tbl} WHERE user_id=?", (uid,)
            ).fetchall()]

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️  Export JSON backup",
            data=json.dumps(data, indent=2, default=str).encode(),
            file_name=f"finance_backup_{date.today()}.json",
            mime="application/json", use_container_width=True,
        )
    with c2:
        if data["expenses"]:
            df = pd.DataFrame(data["expenses"])
            buf = io.StringIO(); df.to_csv(buf, index=False)
            st.download_button(
                "⬇️  Export expenses CSV",
                data=buf.getvalue().encode(),
                file_name=f"expenses_{date.today()}.csv",
                mime="text/csv", use_container_width=True,
            )
        else:
            st.button("⬇️  Export expenses CSV", disabled=True, use_container_width=True)

    up = st.file_uploader("Import JSON backup (your own data only)",
                          type=["json"], key="import_json")
    if up and st.button("Restore from backup"):
        try:
            payload = json.loads(up.getvalue().decode())
            with get_conn() as conn:
                for tbl in ["expenses", "balance_transactions", "debts",
                            "categories", "budgets", "app_settings",
                            "recurring_expenses", "whatsapp_messages"]:
                    conn.execute(f"DELETE FROM {tbl} WHERE user_id=?", (uid,))
                for tbl, rows in payload.items():
                    for r in rows:
                        r["user_id"] = uid  # force ownership
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


def _password_section(uid):
    st.markdown('<div class="pf-card">', unsafe_allow_html=True)
    st.markdown("#### 🔒 Change password")
    with st.form("change_pw_form"):
        old = st.text_input("Current password", type="password")
        new = st.text_input("New password", type="password")
        new2 = st.text_input("Confirm new password", type="password")
        if st.form_submit_button("Update password"):
            if new != new2:
                st.error("Passwords do not match.")
            else:
                err = change_password(uid, old, new)
                if err:
                    st.error(err)
                else:
                    st.success("Password updated.")
    st.markdown("</div>", unsafe_allow_html=True)


def _danger_section(uid):
    st.markdown('<div class="pf-card">', unsafe_allow_html=True)
    st.markdown("#### Danger zone")
    st.caption("This wipes ALL your finance data (categories reset too). "
               "Your account stays.")
    if st.session_state.get("confirm_reset"):
        st.warning("Are you absolutely sure? This cannot be undone.")
        a, b = st.columns(2)
        if a.button("Yes, reset my data", use_container_width=True):
            reset_user_data(uid)
            st.session_state.pop("confirm_reset", None)
            st.success("Your data was reset.")
            st.rerun()
        if b.button("Cancel", type="secondary", use_container_width=True):
            st.session_state.pop("confirm_reset", None)
            st.rerun()
    else:
        if st.button("Reset my data", type="secondary"):
            st.session_state["confirm_reset"] = True
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
