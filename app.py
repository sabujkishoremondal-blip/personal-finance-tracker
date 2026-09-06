"""Personal Finance — Streamlit app entry point.

Run:
    streamlit run app.py
"""
import streamlit as st
from datetime import date

st.set_page_config(
    page_title="Personal Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.database import init_db, get_setting
from services.auth_service import register_user, get_user_by_email, get_user_by_id
from services.demo_service import seed_demo_data
from services.recurring_service import run_due
from components.theme import inject_css
from pages_app import (
    dashboard, expenses, borrow_lend, reports, budget,
    settings as settings_page, quick_add, recurring, auth,
)
from utils.formatting import month_label

# ---------- boot ----------
init_db()


def _ensure_demo_user():
    """Ensure demo@example.com exists so first-time visitors can log straight in."""
    if get_user_by_email("demo@example.com") is None:
        user, err = register_user("demo@example.com", "demo123", "Demo")
        if user:
            seed_demo_data(user["id"])


_ensure_demo_user()

# Theme (from user setting if logged in, else system default 'light')
if "theme" not in st.session_state:
    if "user_id" in st.session_state:
        st.session_state["theme"] = get_setting(
            st.session_state["user_id"], "theme", "light"
        )
    else:
        st.session_state["theme"] = "light"

inject_css()

# ---------- auth gate ----------
if "user_id" not in st.session_state:
    auth.render_auth_gate()
    st.stop()

# make sure the user still exists (e.g. deleted from DB)
if get_user_by_id(st.session_state["user_id"]) is None:
    st.session_state.clear()
    st.rerun()

# Run recurring expenses that are due (idempotent)
if not st.session_state.get("_recurring_ran_this_session"):
    posted = run_due(st.session_state["user_id"])
    st.session_state["_recurring_ran_this_session"] = True
    if posted:
        st.toast(f"Posted {posted} recurring expense(s).", icon="🔁")

PAGES = {
    "Dashboard":     ("🏠", dashboard.render),
    "Expenses":      ("💸", expenses.render),
    "Quick Add":     ("💬", quick_add.render),
    "Borrow & Lend": ("🤝", borrow_lend.render),
    "Recurring":     ("🔁", recurring.render),
    "Reports":       ("📊", reports.render),
    "Budget & Goals":("🎯", budget.render),
    "Settings":      ("⚙️", settings_page.render),
}

# ---------- sidebar ----------
with st.sidebar:
    user_name = st.session_state.get("user_name", "You")
    user_email = st.session_state.get("user_email", "")
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px;padding:6px 0 18px;'>"
        "<div style='width:38px;height:38px;border-radius:12px;"
        "background:linear-gradient(135deg,var(--primary),var(--primary-x));"
        "display:flex;align-items:center;justify-content:center;color:white;"
        "font-family:Fraunces,serif;font-weight:700;font-size:20px;'>₹</div>"
        "<div><div style='font-family:Fraunces,serif;font-weight:700;font-size:18px;line-height:1;'>Personal Finance</div>"
        f"<div style='font-size:12px;color:var(--muted);'>{user_name}</div></div></div>",
        unsafe_allow_html=True,
    )

    current = st.session_state.get("nav", "Dashboard")
    if "_pending_nav" in st.session_state:
        target = st.session_state.pop("_pending_nav")
        if target in PAGES:
            current = target
            st.session_state.pop("nav", None)
    nav = st.radio(
        "Navigate",
        list(PAGES.keys()),
        index=list(PAGES.keys()).index(current) if current in PAGES else 0,
        format_func=lambda n: f"{PAGES[n][0]}  {n}",
        label_visibility="collapsed",
        key="nav",
    )

    st.markdown("---")
    theme_pick = st.radio(
        "Theme", ["light", "dark"],
        index=0 if st.session_state.get("theme", "light") == "light" else 1,
        horizontal=True, key="theme_radio",
    )
    if theme_pick != st.session_state.get("theme"):
        st.session_state["theme"] = theme_pick
        from database.database import set_setting
        set_setting(st.session_state["user_id"], "theme", theme_pick)
        st.rerun()

    st.markdown("---")
    if st.button("Sign out", type="secondary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown(
        f"<div style='margin-top:12px;color:var(--muted);font-size:11px;line-height:1.4;'>"
        f"<b style='color:var(--text);'>Personal Finance</b><br/>"
        f"{month_label(date.today().year, date.today().month)}<br/>"
        f"<span style='opacity:.75;'>{user_email}</span></div>",
        unsafe_allow_html=True,
    )

# ---------- render ----------
_, render_fn = PAGES[nav]
render_fn()
