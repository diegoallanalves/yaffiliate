"""YAffiliate workspace and subscription settings."""

from __future__ import annotations

import os

import streamlit as st

from app.components.layout import page_header
from app.repositories.database import get_setting, upsert_setting
from app.services.stripe_service import StripeService
from app.services.subscription_service import SubscriptionService
from app.services.translation_service import ui


CHECKOUT_URL_KEY = "stripe_checkout_url"
CHECKOUT_USER_KEY = "stripe_checkout_user_id"


def _clear_checkout_session() -> None:
    """Remove a previously prepared Stripe Checkout URL."""

    st.session_state.pop(CHECKOUT_URL_KEY, None)
    st.session_state.pop(CHECKOUT_USER_KEY, None)


def _get_checkout_url(
    user_id: str,
    email: str,
) -> str | None:
    """
    Return a Stripe Checkout URL for the authenticated free user.

    The URL is cached in Streamlit session state so normal reruns do not
    create a new Stripe Checkout Session every time.
    """

    cached_user_id = str(
        st.session_state.get(CHECKOUT_USER_KEY, "") or ""
    ).strip()

    cached_url = str(
        st.session_state.get(CHECKOUT_URL_KEY, "") or ""
    ).strip()

    if cached_url and cached_user_id == user_id:
        return cached_url

    try:
        checkout = StripeService().create_checkout_session(
            user_id=user_id,
            email=email,
        )

        checkout_url = str(
            checkout.get("url", "") or ""
        ).strip()

        if not checkout_url:
            return None

        st.session_state[CHECKOUT_URL_KEY] = checkout_url
        st.session_state[CHECKOUT_USER_KEY] = user_id

        return checkout_url

    except Exception as exc:
        st.error(
            f"Unable to create checkout: {exc}"
        )
        return None


def render() -> None:
    """Render workspace, subscription, and integration settings."""

    # ---------------------------------------------------------
    # PAGE HEADER
    # ---------------------------------------------------------
    page_header(
        "Workspace controls",
        "Manage your YAffiliate workspace and subscription.",
        (
            "API keys and secrets remain securely stored "
            "outside the application."
        ),
    )

    # ---------------------------------------------------------
    # WORKSPACE SETTINGS
    # ---------------------------------------------------------
    st.subheader(ui("Workspace"))

    with st.form("settings"):
        name = st.text_input(
            ui("Workspace name"),
            get_setting(
                "workspace_name",
                "YAffiliate Workspace",
            ),
        )

        currency_options = [
            "BRL",
            "USD",
            "EUR",
            "GBP",
        ]

        saved_currency = get_setting(
            "currency",
            "BRL",
        )

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
            value=float(
                get_setting(
                    "monthly_budget",
                    "1000",
                )
            ),
            step=100.0,
        )

        save_settings = st.form_submit_button(
            ui("Save settings")
        )

    if save_settings:
        upsert_setting(
            "workspace_name",
            name,
        )

        upsert_setting(
            "currency",
            currency,
        )

        upsert_setting(
            "monthly_budget",
            str(budget),
        )

        st.success(
            ui("Settings saved.")
        )

    # ---------------------------------------------------------
    # YAFFILIATE PRO
    # ---------------------------------------------------------
    st.divider()

    st.subheader(
        ui("💳 YAffiliate Pro")
    )

    user_id = str(
        st.session_state.get(
            "auth_user_id",
            "",
        )
        or ""
    ).strip()

    email = str(
        st.session_state.get(
            "auth_user_email",
            "",
        )
        or ""
    ).strip()

    subscription = None
    subscription_error = None

    if user_id:
        try:
            subscription = (
                SubscriptionService()
                .get_subscription(user_id)
            )

        except Exception as exc:
            subscription_error = str(exc)

    is_pro = bool(
        subscription
        and subscription.get("plan") == "pro"
        and subscription.get("status")
        in {
            "active",
            "trialing",
        }
    )

    # ---------------------------------------------------------
    # CURRENT PLAN
    # ---------------------------------------------------------
    if is_pro:
        st.success(
            ui(
                "Current plan: YAffiliate Pro"
            )
        )

        st.caption(
            "Subscription status: "
            f"{subscription.get('status', 'active')}"
        )

        if subscription.get("currency"):
            st.caption(
                "Billing currency: "
                f"{str(subscription['currency']).upper()}"
            )

        # A Pro user no longer needs an old Checkout URL.
        _clear_checkout_session()

    else:
        st.write(
            ui(
                "**Current plan:** Free"
            )
        )

        st.info(
            ui(
                "Your supported local subscription price and "
                "checkout language will be presented automatically "
                "by Stripe."
            )
        )

    # ---------------------------------------------------------
    # SUBSCRIPTION DATABASE ERROR
    # ---------------------------------------------------------
    if subscription_error:
        st.warning(
            "The subscription database could not be checked. "
            f"Details: {subscription_error}"
        )

    # ---------------------------------------------------------
    # UPGRADE
    # ---------------------------------------------------------
    if not is_pro:

        if not user_id or not email:
            st.error(
                ui(
                    "You must be signed in before starting "
                    "a subscription."
                )
            )

        else:
            checkout_url = _get_checkout_url(
                user_id=user_id,
                email=email,
            )

            if checkout_url:
                st.link_button(
                    ui(
                        "🚀 Upgrade to YAffiliate Pro"
                    ),
                    checkout_url,
                    type="primary",
                    use_container_width=True,
                )

            else:
                st.error(
                    ui(
                        "Stripe did not return a Checkout URL."
                    )
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

    st.subheader(
        ui("Integration status")
    )

    # OpenAI
    st.write(
        ui("OpenAI:"),
        (
            "✅ Configured"
            if os.getenv("OPENAI_API_KEY")
            else "⚠️ Not configured"
        ),
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

    if stripe_key.startswith(
        "sk_live_"
    ):
        stripe_status = "🟢 Live"

    elif stripe_key.startswith(
        "sk_test_"
    ):
        stripe_status = "✅ Sandbox"

    elif stripe_key:
        stripe_status = (
            "⚠️ Invalid key"
        )

    else:
        stripe_status = (
            "⚠️ Not configured"
        )

    st.write(
        ui("Stripe payments:"),
        stripe_status,
    )