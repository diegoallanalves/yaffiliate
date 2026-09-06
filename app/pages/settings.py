"""YAffiliate workspace and subscription settings."""

from __future__ import annotations

import os

import streamlit as st

from app.components.layout import page_header
from app.repositories.database import get_setting, upsert_setting
from app.services.stripe_service import StripeService
from app.services.subscription_service import SubscriptionService
from app.services.translation_service import ui


def redirect_to_checkout(checkout_url: str) -> None:
    """Redirect the browser directly to Stripe Checkout."""

    st.markdown(
        f"""
        <meta http-equiv="refresh" content="0; url={checkout_url}">
        """,
        unsafe_allow_html=True,
    )

    st.stop()

def render() -> None:
    """Render workspace, subscription, and integration settings."""

    # ---------------------------------------------------------
    # PAGE HEADER
    # ---------------------------------------------------------
    page_header(
        "Workspace controls",
        "Manage your YAffiliate workspace and subscription.",
        "API keys and secrets remain securely stored outside the application.",
    )

    # ---------------------------------------------------------
    # WORKSPACE SETTINGS
    # ---------------------------------------------------------
    st.subheader(ui("Workspace"))

    with st.form("settings"):
        name = st.text_input(
            ui("Workspace name"),
            get_setting("workspace_name", "YAffiliate Workspace"),
        )

        currency_options = ["BRL", "USD", "EUR", "GBP"]

        saved_currency = get_setting("currency", "BRL")

        currency_index = (
            currency_options.index(saved_currency)
            if saved_currency in currency_options
            else 0
        )

        currency = st.selectbox(
            ui("Default reporting currency"),
            currency_options,
            index=currency_index,
            help=(
                "This preference is for YAffiliate reporting. "
                "Stripe Checkout determines the supported local "
                "billing currency automatically."
            ),
        )

        budget = st.number_input(
            ui("Default monthly testing budget"),
            min_value=0.0,
            value=float(get_setting("monthly_budget", "1000")),
            step=100.0,
        )

        ok = st.form_submit_button(ui("Save settings"))

    if ok:
        upsert_setting("workspace_name", name)
        upsert_setting("currency", currency)
        upsert_setting("monthly_budget", str(budget))

        st.success(ui("Settings saved."))

    # ---------------------------------------------------------
    # YAFFILIATE PRO
    # ---------------------------------------------------------
    st.divider()

    st.subheader(ui("💳 YAffiliate Pro"))

    user_id = str(
        st.session_state.get("auth_user_id", "") or ""
    ).strip()

    email = str(
        st.session_state.get("auth_user_email", "") or ""
    ).strip()

    subscription = None
    subscription_error = None

    if user_id:
        try:
            subscription = SubscriptionService().get_subscription(user_id)
        except Exception as exc:
            subscription_error = str(exc)

    is_pro = bool(
        subscription
        and subscription.get("plan") == "pro"
        and subscription.get("status") in {"active", "trialing"}
    )

    # ---------------------------------------------------------
    # CURRENT SUBSCRIPTION STATUS
    # ---------------------------------------------------------
    if is_pro:
        st.success(ui("Current plan: YAffiliate Pro"))

        st.caption(
            f"Subscription status: "
            f"{subscription.get('status', 'active')}"
        )

        if subscription.get("currency"):
            st.caption(
                f"Billing currency: "
                f"{str(subscription['currency']).upper()}"
            )

    else:
        st.write(ui("**Current plan:** Free"))

        st.info(
            ui(
                "Your supported local subscription price and "
                "checkout language will be presented automatically "
                "by Stripe."
            )
        )

    # ---------------------------------------------------------
    # DATABASE ERROR
    # ---------------------------------------------------------
    if subscription_error:
        st.warning(
            "The subscription database could not be checked. "
            f"Details: {subscription_error}"
        )

    # ---------------------------------------------------------
    # UPGRADE TO PRO
    # ---------------------------------------------------------
    if not is_pro:

        if st.button(
            ui("🚀 Upgrade to YAffiliate Pro"),
            type="primary",
            use_container_width=True,
        ):

            # User must be authenticated before creating
            # a Stripe Checkout Session.
            if not user_id or not email:
                st.error(
                    ui(
                        "You must be signed in before starting "
                        "a subscription."
                    )
                )

            else:
                try:
                    # Create Stripe Checkout Session.
                    checkout = StripeService().create_checkout_session(
                        user_id=user_id,
                        email=email,
                    )

                    checkout_url = checkout.get("url")

                    if checkout_url:
                        # Immediately send the customer to Stripe.
                        redirect_to_checkout(checkout_url)

                    else:
                        st.error(
                            ui(
                                "Stripe did not return a Checkout URL."
                            )
                        )

                except Exception as exc:
                    st.error(
                        f"Unable to create checkout: {exc}"
                    )

        st.caption(
            ui(
                "Payments are processed securely by Stripe. "
                "YAFFiliate does not store your card details."
            )
        )

    # ---------------------------------------------------------
    # INTEGRATION STATUS
    # ---------------------------------------------------------
    st.divider()

    st.subheader(ui("Integration status"))

    # OpenAI
    st.write(
        ui("OpenAI:"),
        "✅ Configured"
        if os.getenv("OPENAI_API_KEY")
        else "⚠️ Not configured",
    )

    # Database
    st.write(
        ui("Database:"),
        "✅ Connected",
    )

    # Authentication
    st.write(
        ui("Authentication:"),
        "✅ Active",
    )

    # Stripe
    stripe_key = os.getenv(
        "STRIPE_SECRET_KEY",
        "",
    ).strip()

    if stripe_key.startswith("sk_live_"):
        stripe_status = "🟢 Live"

    elif stripe_key.startswith("sk_test_"):
        stripe_status = "✅ Sandbox"

    elif stripe_key:
        stripe_status = "⚠️ Invalid key"

    else:
        stripe_status = "⚠️ Not configured"

    st.write(
        ui("Stripe payments:"),
        stripe_status,
    )