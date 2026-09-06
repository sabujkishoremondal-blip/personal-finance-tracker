"""Login / Register screens rendered when user is not authenticated."""
import streamlit as st
from services.auth_service import register_user, login


def render_auth_gate():
    st.markdown(
        "<div style='max-width:460px;margin:40px auto 20px;text-align:center;'>"
        "<div style='width:64px;height:64px;margin:0 auto 16px;border-radius:20px;"
        "background:linear-gradient(135deg,var(--primary),var(--primary-x));display:flex;"
        "align-items:center;justify-content:center;color:white;font-family:Fraunces,serif;"
        "font-weight:700;font-size:32px;box-shadow:0 8px 24px rgba(143,0,43,0.25);'>₹</div>"
        "<h1 style='margin:0;font-family:Fraunces,serif;font-size:36px;'>Personal Finance</h1>"
        "<p style='color:var(--muted);margin-top:6px;'>Your money command center — track, save, thrive.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        _login_form()
    with tab_register:
        _register_form()

    st.markdown(
        "<div style='max-width:460px;margin:24px auto;text-align:center;color:var(--muted);font-size:12px;'>"
        "Your data stays private and local. Passwords are hashed with bcrypt."
        "</div>",
        unsafe_allow_html=True,
    )


def _login_form():
    st.markdown('<div class="pf-card" style="max-width:460px;margin:12px auto;">',
                unsafe_allow_html=True)
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com",
                              key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        if submitted:
            user, err = login(email, password)
            if err:
                st.error(err)
            else:
                _set_logged_in(user)
                st.rerun()
    st.caption("Demo account: **demo@example.com** / **demo123**")
    st.markdown("</div>", unsafe_allow_html=True)


def _register_form():
    st.markdown('<div class="pf-card" style="max-width:460px;margin:12px auto;">',
                unsafe_allow_html=True)
    with st.form("register_form"):
        name = st.text_input("Your name", placeholder="Alex Kumar", key="reg_name")
        email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
        password = st.text_input("Password (min 6 chars)", type="password", key="reg_pw")
        pw2 = st.text_input("Confirm password", type="password", key="reg_pw2")
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        if submitted:
            if password != pw2:
                st.error("Passwords do not match.")
            else:
                user, err = register_user(email, password, name)
                if err:
                    st.error(err)
                else:
                    st.success("Account created. Welcome!")
                    _set_logged_in(user)
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _set_logged_in(user: dict):
    st.session_state["user_id"] = user["id"]
    st.session_state["user_email"] = user["email"]
    st.session_state["user_name"] = user.get("name") or user["email"].split("@")[0]
    from database.database import get_setting
    st.session_state["theme"] = get_setting(user["id"], "theme", "light")
    st.session_state["_pending_nav"] = "Dashboard"
