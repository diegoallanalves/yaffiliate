"""YAffiliate workspace and subscription settings."""

from __future__ import annotations

import os
from datetime import datetime

import streamlit as st

from app.components.layout import page_header
from app.repositories.database import get_setting, upsert_setting
from app.services.stripe_service import StripeService
from app.services.subscription_service import SubscriptionService
from app.services.translation_service import ui


CHECKOUT_URL_KEY = "stripe_checkout_url"
CHECKOUT_USER_KEY = "stripe_checkout_user_id"

PORTAL_URL_KEY = "stripe_portal_url"
PORTAL_USER_KEY = "stripe_portal_user_id"


# =============================================================
# CHECKOUT HELPERS
# =============================================================

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


# =============================================================
# CUSTOMER PORTAL HELPERS
# =============================================================

def _clear_portal_session() -> None:
    """Remove a previously prepared Stripe Customer Portal URL."""

    st.session_state.pop(PORTAL_URL_KEY, None)
    st.session_state.pop(PORTAL_USER_KEY, None)


def _get_portal_url(
    user_id: str,
    customer_id: str,
) -> str | None:
    """
    Create or return a Stripe Customer Portal URL.

    The Stripe Customer ID comes from the authenticated user's
    subscription record in Supabase. It is never supplied manually
    by the customer.
    """

    user_id = str(user_id or "").strip()
    customer_id = str(customer_id or "").strip()

    if not user_id:
        st.error(
            "You must be signed in to manage your subscription."
        )
        return None

    if not customer_id:
        st.error(
            "No Stripe customer is associated with this account."
        )
        return None

    cached_user_id = str(
        st.session_state.get(PORTAL_USER_KEY, "") or ""
    ).strip()

    cached_url = str(
        st.session_state.get(PORTAL_URL_KEY, "") or ""
    ).strip()

    if cached_url and cached_user_id == user_id:
        return cached_url

    try:
        portal = StripeService().create_customer_portal_session(
            customer_id=customer_id,
        )

        portal_url = str(
            portal.get("url", "") or ""
        ).strip()

        if not portal_url:
            return None

        st.session_state[PORTAL_URL_KEY] = portal_url
        st.session_state[PORTAL_USER_KEY] = user_id

        return portal_url

    except Exception as exc:
        st.error(
            f"Unable to open Stripe billing portal: {exc}"
        )
        return None


# =============================================================
# DATE FORMATTING
# =============================================================

def _format_subscription_date(value: object) -> str | None:
    """Format a Supabase ISO timestamp for display."""

    if not value:
        return None

    try:
        date_value = datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

        return date_value.strftime(
            "%B %d, %Y"
        )

    except (TypeError, ValueError):
        return None


# =============================================================
# PAGE
# =============================================================

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

    st.subheader(
        ui("Workspace")
    )

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

    # =========================================================
    # YAFFILIATE PRO
    # =========================================================

    st.divider()

    st.subheader(
        ui("💳 YAffiliate Pro")
    )

    # ---------------------------------------------------------
    # AUTHENTICATED USER
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # LOAD SUBSCRIPTION
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # DETERMINE PRO STATUS
    # ---------------------------------------------------------

    is_pro = bool(
        subscription
        and subscription.get("plan") == "pro"
        and subscription.get("status")
        in {
            "active",
            "trialing",
        }
    )

    # =========================================================
    # CURRENT PRO PLAN
    # =========================================================

    if is_pro:

        st.success(
            ui(
                "Current plan: YAffiliate Pro"
            )
        )

        status = str(
            subscription.get(
                "status",
                "active",
            )
            or "active"
        )

        st.caption(
            f"Subscription status: {status.title()}"
        )

        # -----------------------------------------------------
        # BILLING CURRENCY
        # -----------------------------------------------------

        if subscription.get("currency"):

            st.caption(
                "Billing currency: "
                f"{str(subscription['currency']).upper()}"
            )

        # -----------------------------------------------------
        # CURRENT PERIOD END
        # -----------------------------------------------------

        period_end = _format_subscription_date(
            subscription.get(
                "current_period_end"
            )
        )

        cancel_at_period_end = bool(
            subscription.get(
                "cancel_at_period_end",
                False,
            )
        )

        if period_end:

            if cancel_at_period_end:

                st.warning(
                    (
                        "Cancellation scheduled. "
                        "Your YAffiliate Pro access will remain "
                        f"active until {period_end}."
                    )
                )

            else:

                st.caption(
                    f"Current billing period ends: {period_end}"
                )

        elif cancel_at_period_end:

            st.warning(
                (
                    "Cancellation is scheduled. "
                    "Your Pro access remains active until "
                    "Stripe completes the current billing period."
                )
            )

        # -----------------------------------------------------
        # STRIPE CUSTOMER PORTAL
        # -----------------------------------------------------

        stripe_customer_id = str(
            subscription.get(
                "stripe_customer_id",
                "",
            )
            or ""
        ).strip()

        access_type = str(
            subscription.get(
                "access_type",
                "subscription",
            )
            or "subscription"
        ).strip().lower()

        # Only recurring Stripe subscriptions have a Stripe
        # Customer Portal.
        if (
            access_type == "subscription"
            and stripe_customer_id
        ):

            portal_url = _get_portal_url(
                user_id=user_id,
                customer_id=stripe_customer_id,
            )

            if portal_url:

                st.link_button(
                    "💳 Manage Subscription",
                    portal_url,
                    type="primary",
                    use_container_width=True,
                )

                st.caption(
                    (
                        "Manage billing securely through Stripe. "
                        "You can view invoices, update your payment "
                        "method, and manage your subscription."
                    )
                )

            else:

                st.warning(
                    (
                        "Stripe billing management is temporarily "
                        "unavailable."
                    )
                )

        elif access_type == "subscription":

            st.warning(
                (
                    "This subscription does not yet have a Stripe "
                    "Customer ID. Please contact support if you need "
                    "to manage your billing."
                )
            )

        # A Pro user no longer needs an old Checkout URL.
        _clear_checkout_session()

    # =========================================================
    # FREE PLAN
    # =========================================================

    else:

        # A free user should not retain an old billing portal.
        _clear_portal_session()

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

    # =========================================================
    # SUBSCRIPTION DATABASE ERROR
    # =========================================================

    if subscription_error:

        st.warning(
            (
                "The subscription database could not be checked. "
                f"Details: {subscription_error}"
            )
        )

    # =========================================================
    # UPGRADE
    # =========================================================

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

    # =========================================================
    # INTEGRATION STATUS
    # =========================================================

    st.divider()

    st.subheader(
        ui("Integration status")
    )

    # ---------------------------------------------------------
    # OPENAI
    # ---------------------------------------------------------

    st.write(
        ui("OpenAI:"),
        (
            "✅ Configured"
            if os.getenv("OPENAI_API_KEY")
            else "⚠️ Missing API key"
        ),
    )

    # ---------------------------------------------------------
    # SUPABASE
    # ---------------------------------------------------------

    supabase_configured = bool(
        os.getenv("SUPABASE_URL")
        and (
            os.getenv("SUPABASE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
        )
    )

    st.write(
        ui("Supabase:"),
        (
            "✅ Configured"
            if supabase_configured
            else "⚠️ Missing configuration"
        ),
    )

    # ---------------------------------------------------------
    # STRIPE
    # ---------------------------------------------------------

    stripe_configured = bool(
        os.getenv("STRIPE_SECRET_KEY")
        and os.getenv("STRIPE_PRICE_ID")
    )

    st.write(
        ui("Stripe:"),
        (
            "✅ Configured"
            if stripe_configured
            else "⚠️ Missing configuration"
        ),
    )