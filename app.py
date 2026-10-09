
"""YAFFiliate application entry point."""

from __future__ import annotations

import logging
import time

import streamlit as st

from browser_session_cookie import mount_browser_cookie

from app.bootstrap import bootstrap_app
from app.components.auth_ui import (
    render_auth_page,
    render_user_sidebar,
)
from app.components.layout import sidebar_navigation
from app.router import render_route
from app.services.persistent_session_service import (
    PersistentSessionService,
)
from app.services.subscription_service import (
    SubscriptionService,
)
from app.services.translation_service import (
    get_language,
    set_language,
)


# =========================================================
# CONFIGURATION
# =========================================================

logger = logging.getLogger(__name__)

DEFAULT_LANGUAGE = "en"

SUPPORTED_LANGUAGES = {
    "en",
    "pt_BR",
    "es",
    "zh_CN",
}

AUTH_WAIT_SECONDS = 3.0
AUTH_WAIT_INTERVAL = 0.4

AUTH_WAIT_KEY = "_auth_restore_started"
AUTH_WAIT_DONE_KEY = "_auth_restore_wait_done"


# =========================================================
# QUERY PARAMETERS
# =========================================================

def _query_value(name: str) -> str:
    """Return a single query parameter."""

    value = st.query_params.get(name, "")

    if isinstance(value, list):
        value = value[0] if value else ""

    return str(value or "").strip()


# =========================================================
# LANGUAGE
# =========================================================

def _handle_language_return() -> None:
    """Apply language received from the website."""

    requested = _query_value("lang")

    if not requested:
        return

    if requested not in SUPPORTED_LANGUAGES:
        requested = DEFAULT_LANGUAGE

    if requested != get_language():
        set_language(requested)

    if "lang" in st.query_params:
        del st.query_params["lang"]


# =========================================================
# PERSISTENT AUTHENTICATION
# =========================================================

def _restore_persistent_login() -> None:
    """Restore authentication from browser cookies."""

    if st.session_state.get("authenticated", False):
        st.session_state.pop(AUTH_WAIT_KEY, None)
        st.session_state.pop(AUTH_WAIT_DONE_KEY, None)
        return

    try:
        restored = PersistentSessionService().restore()

    except Exception:
        logger.exception(
            "Persistent session restoration failed."
        )
        restored = False

    if restored:
        st.session_state.pop(AUTH_WAIT_KEY, None)
        st.session_state.pop(AUTH_WAIT_DONE_KEY, None)
        st.rerun()


def _wait_for_authentication() -> None:
    """Wait briefly for browser cookies to initialize."""

    if st.session_state.get("authenticated", False):
        return

    if st.session_state.get(AUTH_WAIT_DONE_KEY, False):
        return

    now = time.monotonic()

    if AUTH_WAIT_KEY not in st.session_state:
        st.session_state[AUTH_WAIT_KEY] = now

    elapsed = now - st.session_state[AUTH_WAIT_KEY]

    if elapsed >= AUTH_WAIT_SECONDS:
        st.session_state[AUTH_WAIT_DONE_KEY] = True
        st.session_state.pop(AUTH_WAIT_KEY, None)
        return

    st.title("🚀 YAffiliate")
    st.info("Restoring your session...")

    progress = min(
        elapsed / AUTH_WAIT_SECONDS,
        1.0,
    )

    st.progress(progress)

    time.sleep(AUTH_WAIT_INTERVAL)
    st.rerun()


# =========================================================
# STRIPE PAYMENT RETURN
# =========================================================

def _handle_payment_return() -> None:
    """Handle and verify a Stripe Checkout return."""

    payment = _query_value("payment").lower()
    session_id = _query_value("session_id")

    if payment == "cancelled":
        st.info(
            "Payment was cancelled. "
            "Your plan has not changed."
        )
        st.query_params.clear()
        return

    if payment != "success":
        return

    if not session_id:
        st.error(
            "Stripe returned without a Checkout Session ID. "
            "Your plan has not been changed."
        )
        st.query_params.clear()
        return

    user_id = str(
        st.session_state.get(
            "auth_user_id",
            "",
        ) or ""
    ).strip()

    if not user_id:
        st.info(
            "🎉 Payment received. "
            "Please sign in to finish activating "
            "YAffiliate Pro."
        )
        return

    processed_key = f"stripe_verified_{session_id}"

    if st.session_state.get(processed_key):
        st.query_params.clear()
        return

    try:
        subscription = (
            SubscriptionService().activate_from_checkout(
                session_id=session_id,
                expected_user_id=user_id,
            )
        )

        st.session_state[processed_key] = True

        st.session_state.pop(
            "stripe_checkout_url",
            None,
        )

        st.success(
            "🎉 Payment verified! "
            "YAffiliate Pro is now active."
        )

        status = subscription.get(
            "status",
            "active",
        )

        currency = subscription.get("currency")

        if currency:
            st.caption(
                f"Subscription status: {status} · "
                f"Billing currency: "
                f"{str(currency).upper()}"
            )
        else:
            st.caption(
                f"Subscription status: {status}"
            )

        st.query_params.clear()

    except Exception:
        logger.exception(
            "Stripe subscription verification failed."
        )

        st.error(
            "We could not verify the Stripe "
            "subscription yet. "
            "Your account has not been upgraded."
        )


# =========================================================
# APPLICATION STARTUP
# =========================================================

bootstrap_app()

# Initialize browser cookie bridge on every app execution.
mount_browser_cookie()


# =========================================================
# LANGUAGE
# =========================================================

_handle_language_return()


# =========================================================
# RESTORE SESSION
# =========================================================

_restore_persistent_login()


# =========================================================
# AUTHENTICATION LOADING
# =========================================================

if not st.session_state.get(
    "authenticated",
    False,
):
    _wait_for_authentication()


# =========================================================
# STRIPE
# =========================================================

_handle_payment_return()


# =========================================================
# LOGIN / REGISTRATION
# =========================================================

if not st.session_state.get(
    "authenticated",
    False,
):
    render_auth_page()
    st.stop()


# =========================================================
# AUTHENTICATED APPLICATION
# =========================================================

render_user_sidebar()

route = sidebar_navigation()

render_route(route)
