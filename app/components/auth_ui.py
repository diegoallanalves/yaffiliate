"""Login and account creation UI for YAffiliate."""

from __future__ import annotations

import logging

import streamlit as st

from app.services.auth_service import AuthService
from app.services.growth_analytics_service import GrowthAnalyticsService
from app.services.persistent_session_service import PersistentSessionService
from app.services.translation_service import get_language, t, ui

logger = logging.getLogger(__name__)
PENDING_KEY = "_persistent_login_pending"


def _store_auth_session(response) -> bool:
    """Store the authenticated Supabase session in Streamlit."""
    user = getattr(response, "user", None)
    session = getattr(response, "session", None)
    if user is None or session is None:
        return False

    access_token = getattr(session, "access_token", None)
    refresh_token = getattr(session, "refresh_token", None)
    user_id = getattr(user, "id", None)
    if not access_token or not refresh_token or not user_id:
        return False

    st.session_state["auth_user_id"] = str(user_id)
    st.session_state["auth_user_email"] = str(
        getattr(user, "email", "") or ""
    )
    st.session_state["supabase_access_token"] = str(access_token)
    st.session_state["supabase_refresh_token"] = str(refresh_token)
    st.session_state["authenticated"] = True
    return True


def _queue_persistent_session() -> None:
    """Create the cookie on the next full app render, not before rerun."""
    st.session_state[PENDING_KEY] = True


def _finish_persistent_session() -> None:
    """Write the cookie without immediately interrupting its component."""
    if not st.session_state.get(PENDING_KEY):
        return

    user_id = st.session_state.get("auth_user_id")
    refresh_token = st.session_state.get("supabase_refresh_token")
    if not user_id or not refresh_token:
        st.session_state.pop(PENDING_KEY, None)
        return

    try:
        service = PersistentSessionService()
        service.create(
            user_id=str(user_id),
            refresh_token=str(refresh_token),
        )
    except Exception:
        logger.exception("Could not create persistent login session.")
        return
    st.session_state.pop(PENDING_KEY, None)
    # Mount the browser bridge again to send the queued write.
    st.rerun()


def render_auth_page() -> None:
    auth = AuthService()
    st.title(ui("🚀 YAffiliate"))
    st.subheader(ui("AI Marketing Platform"))
    st.write(
        ui(
            "Sign in to create, save and manage "
            "your affiliate campaigns."
        )
    )

    sign_in, sign_up = st.tabs(
        [ui("Sign In"), ui("Create Account")]
    )
    with sign_in:
        _sign_in(auth)
    with sign_up:
        _sign_up(auth)


def _sign_in(auth: AuthService) -> None:
    with st.form("auth_sign_in"):
        email = st.text_input(ui("Email"), key="signin_email")
        password = st.text_input(
            ui("Password"), type="password", key="signin_password"
        )
        submitted = st.form_submit_button(
            ui("🔐 Sign In"),
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    try:
        response = auth.sign_in(email, password)
        if not _store_auth_session(response):
            st.error(
                ui("Sign in did not return an authenticated session.")
            )
            return

        _queue_persistent_session()
        st.rerun()
    except Exception:
        logger.exception("Sign in failed.")
        st.error(ui("Sign in failed. Please check your credentials."))


def _sign_up(auth: AuthService) -> None:
    with st.form("auth_sign_up"):
        email = st.text_input(ui("Email"), key="signup_email")
        password = st.text_input(
            ui("Password"), type="password", key="signup_password"
        )
        confirm = st.text_input(
            ui("Confirm password"),
            type="password",
            key="signup_confirm",
        )
        submitted = st.form_submit_button(
            ui("✨ Create Account"),
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return
    if password != confirm:
        st.error(ui("Passwords do not match."))
        return
    if len(password) < 8:
        st.error(ui("Password must contain at least 8 characters."))
        return

    try:
        response = auth.sign_up(email, password, get_language())
        user = getattr(response, "user", None)
        session = getattr(response, "session", None)
        if user is None:
            st.error(ui("Account could not be created."))
            return

        try:
            GrowthAnalyticsService().track(
                "signup",
                event_page="auth",
                user_id=str(user.id),
                metadata={
                    "language": get_language(),
                    "email_confirmation_required": session is None,
                },
            )
        except Exception:
            logger.exception("Signup analytics tracking failed.")

        if session is None:
            st.success(
                ui(
                    "Account created. Check your email, "
                    "confirm your address, then return and sign in."
                )
            )
            return

        if not _store_auth_session(response):
            st.error(
                ui(
                    "Account was created but the authenticated "
                    "session could not be stored. Please sign in."
                )
            )
            return

        _queue_persistent_session()
        st.rerun()
    except Exception:
        logger.exception("Account creation failed.")
        st.error(ui("Account creation failed. Please try again."))


def _persistent_cookie_writer() -> None:
    """Create the persistent session once after sign-in."""
    if st.session_state.get(PENDING_KEY):
        _finish_persistent_session()


def render_user_sidebar() -> None:
    _persistent_cookie_writer()

    email = st.session_state.get(
        "auth_user_email", "Signed-in user"
    )
    with st.sidebar:
        st.divider()
        st.caption(t("signed_in"))
        st.write(email)

        if st.button(
            t("sign_out"),
            use_container_width=True,
            key="yaffiliate_sign_out",
        ):
            try:
                PersistentSessionService().revoke_current()
            except Exception:
                logger.exception("Persistent session revocation failed.")

            try:
                AuthService().sign_out()
            except Exception:
                logger.exception("Supabase sign out failed.")
            finally:
                for key in (
                    PENDING_KEY,
                    "authenticated",
                    "auth_user_id",
                    "auth_user_email",
                    "supabase_access_token",
                    "supabase_refresh_token",
                    "loaded_campaign",
                    "loaded_campaign_id",
                    "generated_campaign",
                    "generated_campaign_id",
                    "quick_generated_campaign",
                    "quick_generated_zip",
                    "quick_generated_custom_product",
                    "quick_generated_campaign_id",
                ):
                    st.session_state.pop(key, None)
                st.rerun()
