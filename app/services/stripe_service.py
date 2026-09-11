"""Stripe payment service for YAffiliate."""

from __future__ import annotations

import os
from typing import Any

import stripe
from dotenv import load_dotenv


class StripeService:
    """Provide Stripe payment and billing operations for YAffiliate."""

    def __init__(self) -> None:
        """Configure Stripe using the configured multi-currency Price."""

        load_dotenv()

        secret_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
        price_id = os.getenv("STRIPE_PRICE_ID", "").strip()

        # ---------------------------------------------------------
        # Application URL
        # ---------------------------------------------------------
        # Local development:
        # APP_URL=http://localhost:8501
        #
        # Production:
        # APP_URL=https://yaffiliate-ai.streamlit.app
        #
        # If APP_URL is missing, production is used as a safe default.
        # ---------------------------------------------------------
        self.app_url = os.getenv(
            "APP_URL",
            "https://yaffiliate-ai.streamlit.app",
        ).strip().rstrip("/")

        if not secret_key:
            raise ValueError(
                "STRIPE_SECRET_KEY is not configured."
            )

        if not secret_key.startswith(
            ("sk_test_", "sk_live_")
        ):
            raise ValueError(
                "STRIPE_SECRET_KEY does not appear to be a valid "
                "Stripe secret key."
            )

        if not price_id:
            raise ValueError(
                "STRIPE_PRICE_ID is not configured."
            )

        if not price_id.startswith("price_"):
            raise ValueError(
                "STRIPE_PRICE_ID does not appear to be a valid "
                "Stripe Price ID."
            )

        if not self.app_url.startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "APP_URL must start with http:// or https://."
            )

        # Configure the Stripe Python SDK.
        stripe.api_key = secret_key

        self.client = stripe
        self.price_id = price_id

        self.mode = (
            "live"
            if secret_key.startswith("sk_live_")
            else "test"
        )

    # =============================================================
    # CONNECTION
    # =============================================================

    def test_connection(self) -> dict[str, Any]:
        """Verify that YAffiliate can communicate with Stripe."""

        account = self.client.Account.retrieve()

        return {
            "id": account.id,
            "country": getattr(
                account,
                "country",
                None,
            ),
            "email": getattr(
                account,
                "email",
                None,
            ),
            "mode": self.mode,
        }

    # =============================================================
    # PRICE
    # =============================================================

    def get_price(self) -> dict[str, Any]:
        """Retrieve the configured global YAffiliate Pro Price."""

        price = self.client.Price.retrieve(
            self.price_id
        )

        recurring = getattr(
            price,
            "recurring",
            None,
        )

        interval = (
            getattr(
                recurring,
                "interval",
                None,
            )
            if recurring
            else None
        )

        default_currency = str(
            getattr(
                price,
                "currency",
                "",
            )
            or ""
        ).lower()

        return {
            "id": getattr(
                price,
                "id",
                None,
            ),
            "active": bool(
                getattr(
                    price,
                    "active",
                    False,
                )
            ),
            "default_currency": default_currency,
            "unit_amount": getattr(
                price,
                "unit_amount",
                None,
            ),
            "interval": interval,
            "product": getattr(
                price,
                "product",
                None,
            ),
            "mode": self.mode,
        }

    # =============================================================
    # CHECKOUT
    # =============================================================

    def create_checkout_session(
        self,
        *,
        user_id: str,
        email: str,
        success_url: str | None = None,
        cancel_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a Stripe Checkout Session for YAffiliate Pro.

        Creating Checkout does not activate Pro access.

        A completed Stripe subscription must be verified before
        YAffiliate grants Pro access.
        """

        user_id = user_id.strip()
        email = email.strip().lower()

        if not user_id:
            raise ValueError(
                "An authenticated user ID is required "
                "to create checkout."
            )

        if not email:
            raise ValueError(
                "An authenticated user email is required "
                "to create checkout."
            )

        # ---------------------------------------------------------
        # Environment-aware redirect URLs
        # ---------------------------------------------------------
        # Local:
        # http://localhost:8501/?payment=success
        #
        # Production:
        # https://yaffiliate-ai.streamlit.app/?payment=success
        # ---------------------------------------------------------

        if success_url is None:
            success_url = (
                f"{self.app_url}/?payment=success"
            )

        if cancel_url is None:
            cancel_url = (
                f"{self.app_url}/?payment=cancelled"
            )

        session = (
            self.client.checkout.Session.create(
                mode="subscription",

                customer_email=email,

                line_items=[
                    {
                        "price": self.price_id,
                        "quantity": 1,
                    }
                ],

                success_url=(
                    success_url
                    + "&session_id="
                    "{CHECKOUT_SESSION_ID}"
                ),

                cancel_url=cancel_url,

                # Connect Stripe Checkout to the authenticated
                # YAffiliate user.
                client_reference_id=user_id,

                metadata={
                    "yaffiliate_user_id": user_id,
                    "plan": "pro",
                },

                subscription_data={
                    "metadata": {
                        "yaffiliate_user_id": user_id,
                        "plan": "pro",
                    }
                },

                allow_promotion_codes=True,
            )
        )

        return {
            "id": session.id,
            "url": session.url,
            "status": getattr(
                session,
                "status",
                None,
            ),
            "currency": getattr(
                session,
                "currency",
                None,
            ),
            "customer": getattr(
                session,
                "customer",
                None,
            ),
        }

    # =============================================================
    # RETRIEVE CHECKOUT
    # =============================================================

    def retrieve_checkout_session(
        self,
        session_id: str,
    ) -> Any:
        """
        Retrieve Checkout and expand its customer and subscription.
        """

        session_id = session_id.strip()

        if not session_id:
            raise ValueError(
                "Checkout Session ID is required."
            )

        return (
            self.client.checkout.Session.retrieve(
                session_id,
                expand=[
                    "subscription",
                    "customer",
                ],
            )
        )

    # =============================================================
    # CUSTOMER PORTAL
    # =============================================================

    def create_customer_portal_session(
        self,
        *,
        customer_id: str,
        return_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a Stripe Customer Portal session.

        The Stripe Customer Portal allows a YAffiliate Pro customer
        to securely manage their subscription directly through
        Stripe.

        Depending on the options enabled in the Stripe Dashboard,
        customers can:

        - View their subscription.
        - Update payment methods.
        - View invoices.
        - Cancel their subscription.
        - Manage billing information.

        YAffiliate never handles or stores card information.
        """

        customer_id = str(
            customer_id or ""
        ).strip()

        if not customer_id:
            raise ValueError(
                "Stripe Customer ID is required "
                "to open the billing portal."
            )

        if not customer_id.startswith("cus_"):
            raise ValueError(
                "The supplied Stripe Customer ID "
                "does not appear to be valid."
            )

        # ---------------------------------------------------------
        # Where Stripe sends the customer after they finish
        # managing their subscription.
        # ---------------------------------------------------------

        if return_url is None:
            return_url = self.app_url

        return_url = str(
            return_url or ""
        ).strip()

        if not return_url.startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "Customer Portal return_url must start "
                "with http:// or https://."
            )

        # ---------------------------------------------------------
        # Create the secure Stripe-hosted billing portal.
        # ---------------------------------------------------------

        session = (
            self.client.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
        )

        portal_url = str(
            getattr(
                session,
                "url",
                "",
            )
            or ""
        ).strip()

        if not portal_url:
            raise RuntimeError(
                "Stripe created the Customer Portal session "
                "but did not return a portal URL."
            )

        return {
            "id": getattr(
                session,
                "id",
                None,
            ),
            "url": portal_url,
            "customer": customer_id,
            "mode": self.mode,
        }