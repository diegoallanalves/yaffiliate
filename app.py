"""YAFFiliate application entry point."""

from __future__ import annotations

import streamlit as st

from app.bootstrap import bootstrap_app
from app.components.auth_ui import (
    render_auth_page,
    render_user_sidebar,
)
from app.components.layout import sidebar_navigation
from app.router import render_route
from app.services.subscription_service import SubscriptionService
from app.services.translation_service import (
    get_language,
    set_language,
)


# ---------------------------------------------------------
# SUPPORTED LANGUAGES
# ---------------------------------------------------------

DEFAULT_LANGUAGE = "en"

SUPPORTED_LANGUAGES = {
    "en",
    "pt_BR",
    "es",
    "zh_CN",
}


def _query_value(name: str) -> str:
    """Return a single Streamlit query-parameter value."""
    value = st.query_params.get(name, "")

    if isinstance(value, list):
        value = value[0] if value else ""

    return str(value or "").strip()


def _handle_language_return() -> None:
    """
    Apply the language received from the public YAffiliate website.

    Supported:
        ?lang=en
        ?lang=pt_BR
        ?lang=es
        ?lang=zh_CN

    The URL language parameter is a one-time handoff.
    After it is applied, it is removed so the in-app language
    selector can change languages normally.
    """

    requested_language = _query_value("lang")

    # No language parameter means there is nothing to import.
    # Keep the customer's current language unchanged.
    if not requested_language:
        return

    # Unsupported languages fall back to English.
    if requested_language not in SUPPORTED_LANGUAGES:
        requested_language = DEFAULT_LANGUAGE

    # Apply the language received from the website.
    if requested_language != get_language():
        set_language(requested_language)

    # The website-to-app language handoff has now been consumed.
    # Remove only the language parameter so Stripe parameters
    # or other query parameters remain untouched.
    if "lang" in st.query_params:
        del st.query_params["lang"]


def _handle_payment_return() -> None:
    """Handle and verify a Stripe Checkout return."""

    payment = _query_value("payment").lower()
    session_id = _query_value("session_id")

    if payment == "cancelled":
        st.info(
            "Payment was cancelled. Your plan has not changed."
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
        )
        or ""
    ).strip()

    # Stripe Checkout may return in a fresh Streamlit browser
    # session. Keep the payment parameters available until
    # the customer signs in.
    if not user_id:
        st.info(
            "🎉 Payment received. Please sign in to finish "
            "activating YAffiliate Pro."
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
            "🎉 Payment verified! YAffiliate Pro is now active."
        )

        status = subscription.get(
            "status",
            "active",
        )

        currency = subscription.get(
            "currency",
        )

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

    except Exception as exc:
        st.error(
            "We could not verify the Stripe subscription yet. "
            "Your account has not been upgraded."
        )

        st.caption(str(exc))


# =========================================================
# APPLICATION STARTUP
# =========================================================

bootstrap_app()


# ---------------------------------------------------------
# LANGUAGE
# ---------------------------------------------------------

# Import the language selected on the public YAffiliate website.
#
# The URL parameter is consumed once and then removed so the
# customer can freely change language inside the application.
_handle_language_return()


# ---------------------------------------------------------
# STRIPE
# ---------------------------------------------------------

# Handle Stripe before authentication.
#
# If Stripe returns in a fresh Streamlit session, the
# customer can sign in while the Checkout Session ID
# remains available for secure verification.
_handle_payment_return()


# =========================================================
# AUTHENTICATION
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