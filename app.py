"""Personal Finance — Streamlit app entry point.

Run:
    streamlit run app.py
"""
import streamlit as st
from datetime import date

# IMPORTANT: page config must be first Streamlit call
st.set_page_config(
    page_title="Personal Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

from database.database import init_db, get_setting
from services.demo_service import seed_demo_data
from components.theme import inject_css
from pages_app import dashboard, expenses, borrow_lend, reports, budget, settings as settings_page
from utils.formatting import month_label

# ---------- boot ----------
init_db()
# Seed once
if get_setting("onboarded", "0") == "0":
    seed_demo_data()

# Sync theme into session_state
if "theme" not in st.session_state:
    st.session_state["theme"] = get_setting("theme", "light")

inject_css()

PAGES = {
    "Dashboard":     ("🏠", dashboard.render),
    "Expenses":      ("💸", expenses.render),
    "Borrow & Lend": ("🤝", borrow_lend.render),
    "Reports":       ("📊", reports.render),
    "Budget & Goals":("🎯", budget.render),
    "Settings":      ("⚙️", settings_page.render),
}

# ---------- sidebar / mobile nav ----------
with st.sidebar:
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px;padding:6px 0 18px;'>"
        "<div style='width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,var(--primary),var(--primary-x));"
        "display:flex;align-items:center;justify-content:center;color:white;font-family:Fraunces,serif;font-weight:700;font-size:20px;'>₹</div>"
        "<div><div style='font-family:Fraunces,serif;font-weight:700;font-size:20px;line-height:1;'>Personal Finance</div>"
        "<div style='font-size:12px;color:var(--muted);'>My Money Command Center</div></div></div>",
        unsafe_allow_html=True,
    )

    current = st.session_state.get("nav", "Dashboard")
    nav = st.radio(
        "Navigate",
        list(PAGES.keys()),
        index=list(PAGES.keys()).index(current) if current in PAGES else 0,
        format_func=lambda n: f"{PAGES[n][0]}  {n}",
        label_visibility="collapsed",
        key="nav",
    )

    st.markdown("---")
    # theme toggle
    theme_pick = st.radio(
        "Theme", ["light", "dark"],
        index=0 if st.session_state.get("theme", "light") == "light" else 1,
        horizontal=True,
        key="theme_radio",
    )
    if theme_pick != st.session_state.get("theme"):
        st.session_state["theme"] = theme_pick
        from database.database import set_setting
        set_setting("theme", theme_pick)
        st.rerun()

    st.markdown(
        f"<div style='margin-top:auto;padding-top:20px;color:var(--muted);font-size:12px;'>"
        f"<b style='color:var(--text);'>Personal Finance</b><br/>"
        f"{month_label(date.today().year, date.today().month)}</div>",
        unsafe_allow_html=True,
    )

# ---------- render active page ----------
_, render_fn = PAGES[nav]
render_fn()
