"""YAFFiliate application entry point."""

from __future__ import annotations

import streamlit as st

from app.bootstrap import bootstrap_app
from app.components.auth_ui import render_auth_page, render_user_sidebar
from app.components.layout import sidebar_navigation
from app.router import render_route
from app.services.subscription_service import SubscriptionService


def _query_value(name: str) -> str:
    """Return a single Streamlit query-parameter value."""

    value = st.query_params.get(name, "")

    if isinstance(value, list):
        value = value[0] if value else ""

    return str(value or "").strip()


def _handle_payment_return() -> None:
    """Verify a Stripe Checkout return before granting Pro access."""

    payment = _query_value("payment").lower()
    session_id = _query_value("session_id")

    if payment == "cancelled":
        st.info("Payment was cancelled. Your plan has not changed.")
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
        st.session_state.get("auth_user_id", "") or ""
    ).strip()

    if not user_id:
        st.error(
            "Please sign in again before YAffiliate verifies your payment."
        )
        return

    processed_key = f"stripe_verified_{session_id}"

    if st.session_state.get(processed_key):
        st.query_params.clear()
        return

    try:
        subscription = SubscriptionService().activate_from_checkout(
            session_id=session_id,
            expected_user_id=user_id,
        )

        st.session_state[processed_key] = True
        st.session_state.pop("stripe_checkout_url", None)

        st.success(
            "🎉 Payment verified! YAffiliate Pro is now active."
        )

        status = subscription.get("status", "active")
        currency = subscription.get("currency")

        if currency:
            st.caption(
                f"Subscription status: {status} · "
                f"Billing currency: {str(currency).upper()}"
            )
        else:
            st.caption(f"Subscription status: {status}")

        st.query_params.clear()

    except Exception as exc:
        st.error(
            "We could not verify the Stripe subscription yet. "
            "Your account has not been upgraded."
        )
        st.caption(str(exc))


bootstrap_app()

if not st.session_state.get("authenticated", False):
    render_auth_page()
    st.stop()

_handle_payment_return()

render_user_sidebar()

route = sidebar_navigation()
render_route(route)
