"""Login / Register / Forgot Password screens."""

import streamlit as st

from services.auth_service import (
    register_user,
    login,
    create_password_reset_token,
    reset_password,
)

def render_auth_gate():
    st.markdown(
        """
        <div class="auth-header">
            <div class="auth-logo">₹</div>
            <h1>Personal Finance</h1>
            <p>Your money command center — track, save, thrive.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_register, tab_forgot = st.tabs(
        ["Sign In", "Create Account", "Forgot Password"]
    )

    with tab_login:
        _login_form()

    with tab_register:
        _register_form()


  

    
    with tab_forgot:
        _forgot_password_form()

def _login_form():
    with st.form("login_form_main", border=False):

        email = st.text_input(
            "Email",
            placeholder="you@example.com",
            key="login_email",
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_pw",
        )

        submitted = st.form_submit_button(
            "Sign In",
            use_container_width=True,
        )

        if submitted:
            user, err = login(email, password)

            if err:
                st.error(err)

            else:
                _set_logged_in(user)
                st.rerun()

    st.caption(
        "Demo account: **demo@example.com** / **demo123**"
    )


def _register_form():
    with st.form("register_form", border=False):

        name = st.text_input(
            "Your name",
            placeholder="Alex Kumar",
            key="reg_name",
        )

        email = st.text_input(
            "Email",
            placeholder="you@example.com",
            key="reg_email",
        )

        password = st.text_input(
            "Password (min 6 chars)",
            type="password",
            key="reg_pw",
        )

        pw2 = st.text_input(
            "Confirm password",
            type="password",
            key="reg_pw2",
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True,
        )

        if submitted:

            if password != pw2:
                st.error("Passwords do not match.")

            else:
                user, err = register_user(
                    email,
                    password,
                    name,
                )

                if err:
                    st.error(err)

                else:
                    st.success("Account created. Welcome!")
                    _set_logged_in(user)
                    st.rerun()


def _forgot_password_form():

    st.markdown(
        """
        <div style="
            color:var(--muted);
            font-size:14px;
            margin:4px 0 18px;
            line-height:1.5;
        ">
            Enter your account email and we'll generate a
            temporary 6-digit reset code.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("forgot_password_form", border=False):

        email = st.text_input(
            "Account Email",
            placeholder="you@example.com",
            key="forgot_email",
        )

        submitted = st.form_submit_button(
            "Send Reset Code",
            use_container_width=True,
        )

        if submitted:

            if not email.strip():
                st.error("Please enter your email address.")

            else:
                token, err = create_password_reset_token(email)

                # We intentionally don't reveal whether an email exists.
                st.session_state["reset_email"] = email.strip().lower()

                if token:
                    st.session_state["reset_token"] = token

                    st.success(
                        "Reset code generated. "
                        "Enter it below to create your new password."
                    )

                    # Development version:
                    # Later we can replace this with real email delivery.
                    st.info(
                        f"Your reset code is: **{token}**"
                    )

                else:
                    st.success(
                        "If an account exists for this email, "
                        "a reset code has been generated."
                    )

    # Show password reset fields after requesting a code.
    if st.session_state.get("reset_email"):

        st.markdown(
            """
            <div style="
                height:1px;
                background:rgba(212,175,55,.18);
                margin:24px 0;
            "></div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="
                font-family:Georgia,serif;
                font-size:20px;
                font-weight:600;
                margin-bottom:12px;
                color:var(--text);
            ">
                Create a new password
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("reset_password_form", border=False):

            token = st.text_input(
                "6-digit Reset Code",
                placeholder="123456",
                max_chars=6,
                key="reset_code",
            )

            new_password = st.text_input(
                "New Password",
                type="password",
                key="new_password",
            )

            confirm_password = st.text_input(
                "Confirm New Password",
                type="password",
                key="confirm_new_password",
            )

            reset_submitted = st.form_submit_button(
                "Reset Password",
                use_container_width=True,
            )

            if reset_submitted:

                if len(token.strip()) != 6:
                    st.error("Please enter the 6-digit reset code.")

                elif new_password != confirm_password:
                    st.error("Passwords do not match.")

                else:
                    error = reset_password(
                        st.session_state["reset_email"],
                        token,
                        new_password,
                    )

                    if error:
                        st.error(error)

                    else:
                        st.success(
                            "Password reset successfully. "
                            "You can now sign in with your new password."
                        )

                        # Clear reset information
                        st.session_state.pop("reset_email", None)
                        st.session_state.pop("reset_token", None)
                        st.session_state.pop("reset_code", None)
                        st.session_state.pop("new_password", None)
                        st.session_state.pop("confirm_new_password", None)


def _set_logged_in(user: dict):
    st.session_state["user_id"] = user["id"]
    st.session_state["user_email"] = user["email"]
    st.session_state["user_name"] = (
        user.get("name")
        or user["email"].split("@")[0]
    )

    # Dark-only theme
    st.session_state["theme"] = "dark"

    st.session_state["_pending_nav"] = "Dashboard"