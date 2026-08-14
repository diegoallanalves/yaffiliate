"""Login and account creation UI for YAffiliate."""
from __future__ import annotations
import streamlit as st
from app.services.auth_service import AuthService

def render_auth_page() -> None:
    auth = AuthService()
    st.title("🚀 YAffiliate")
    st.subheader("AI Marketing Platform")
    st.write("Sign in to create, save and manage your affiliate campaigns.")
    sign_in, sign_up = st.tabs(["Sign In", "Create Account"])
    with sign_in:
        _sign_in(auth)
    with sign_up:
        _sign_up(auth)

def _sign_in(auth: AuthService) -> None:
    with st.form("auth_sign_in"):
        email = st.text_input("Email", key="signin_email")
        password = st.text_input("Password", type="password", key="signin_password")
        submitted = st.form_submit_button("🔐 Sign In", type="primary", use_container_width=True)
    if not submitted:
        return
    try:
        response = auth.sign_in(email, password)
        user = getattr(response, "user", None)
        session = getattr(response, "session", None)
        if user is None or session is None:
            st.error("Sign in did not return an authenticated session.")
            return
        st.session_state["auth_user_id"] = str(user.id)
        st.session_state["auth_user_email"] = str(user.email or "")
        st.session_state["authenticated"] = True
        st.success("Signed in successfully.")
        st.rerun()
    except Exception as error:
        st.error(f"Sign in failed: {error}")

def _sign_up(auth: AuthService) -> None:
    with st.form("auth_sign_up"):
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm = st.text_input("Confirm password", type="password", key="signup_confirm")
        submitted = st.form_submit_button("✨ Create Account", type="primary", use_container_width=True)
    if not submitted:
        return
    if password != confirm:
        st.error("Passwords do not match.")
        return
    if len(password) < 8:
        st.error("Password must contain at least 8 characters.")
        return
    try:
        response = auth.sign_up(email, password)
        user = getattr(response, "user", None)
        session = getattr(response, "session", None)
        if user is None:
            st.error("Account could not be created.")
            return
        if session is None:
            st.success("Account created. Check your email, confirm your address, then return and sign in.")
            return
        st.session_state["auth_user_id"] = str(user.id)
        st.session_state["auth_user_email"] = str(user.email or "")
        st.session_state["authenticated"] = True
        st.success("Account created successfully.")
        st.rerun()
    except Exception as error:
        st.error(f"Account creation failed: {error}")

def render_user_sidebar() -> None:
    email = st.session_state.get("auth_user_email", "Signed-in user")
    with st.sidebar:
        st.divider()
        st.caption("SIGNED IN")
        st.write(email)
        if st.button("🚪 Sign Out", use_container_width=True, key="yaffiliate_sign_out"):
            try:
                AuthService().sign_out()
            finally:
                for key in (
                    "authenticated", "auth_user_id", "auth_user_email",
                    "loaded_campaign", "loaded_campaign_id",
                    "generated_campaign", "generated_campaign_id",
                    "quick_generated_campaign", "quick_generated_zip",
                    "quick_generated_custom_product", "quick_generated_campaign_id",
                ):
                    st.session_state.pop(key, None)
                st.rerun()
