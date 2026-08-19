"""Stripe payment service for YAffiliate."""

from __future__ import annotations

import os
from typing import Any

import stripe
from dotenv import load_dotenv


class StripeService:
    """Provide Stripe payment operations for YAffiliate."""

    def __init__(self) -> None:
        """Configure Stripe using the global multi-currency Price."""

        load_dotenv()

        secret_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
        price_id = os.getenv("STRIPE_PRICE_ID", "").strip()

        if not secret_key:
            raise ValueError("STRIPE_SECRET_KEY is not configured.")

        if not secret_key.startswith("sk_test_"):
            raise ValueError(
                "YAFFiliate currently requires a Stripe test-mode secret key."
            )

        if not price_id:
            raise ValueError("STRIPE_PRICE_ID is not configured.")

        if not price_id.startswith("price_"):
            raise ValueError(
                "STRIPE_PRICE_ID does not appear to be a valid Stripe Price ID."
            )

        stripe.api_key = secret_key
        self.client = stripe
        self.price_id = price_id

    def test_connection(self) -> dict[str, Any]:
        """Verify that YAffiliate can communicate with Stripe."""

        account = self.client.Account.retrieve()

        return {
            "id": account.id,
            "country": getattr(account, "country", None),
            "email": getattr(account, "email", None),
        }

    def get_price(self) -> dict[str, Any]:
        """Retrieve the configured global YAffiliate Pro Price."""

        price = self.client.Price.retrieve(self.price_id)

        recurring = getattr(price, "recurring", None)
        interval = getattr(recurring, "interval", None) if recurring else None

        default_currency = str(
            getattr(price, "currency", "") or ""
        ).lower()

        # Stripe's Python SDK does not consistently expose currency_options
        # as a normal mapping on retrieved Price objects. The application's
        # Checkout flow does not need to enumerate those options: Stripe uses
        # the multi-currency Price itself when creating Checkout.
        return {
            "id": getattr(price, "id", None),
            "active": bool(getattr(price, "active", False)),
            "default_currency": default_currency,
            "unit_amount": getattr(price, "unit_amount", None),
            "interval": interval,
            "product": getattr(price, "product", None),
        }

    def create_checkout_session(
        self,
        *,
        user_id: str,
        email: str,
        success_url: str = "http://localhost:8501/?payment=success",
        cancel_url: str = "http://localhost:8501/?payment=cancelled",
    ) -> dict[str, Any]:
        """
        Create a Stripe Checkout Session for YAffiliate Pro.

        The configured Stripe Price contains the supported currency options.
        YAffiliate does not expose a customer-facing currency selector and
        does not force a currency in the Checkout Session.

        Creating Checkout does not activate Pro access. A completed Stripe
        subscription must be verified before YAffiliate grants Pro.
        """

        user_id = user_id.strip()
        email = email.strip().lower()

        if not user_id:
            raise ValueError(
                "An authenticated user ID is required to create checkout."
            )

        if not email:
            raise ValueError(
                "An authenticated user email is required to create checkout."
            )

        session = self.client.checkout.Session.create(
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
                + "&session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=cancel_url,
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

        return {
            "id": session.id,
            "url": session.url,
            "status": getattr(session, "status", None),
            "currency": getattr(session, "currency", None),
            "customer": getattr(session, "customer", None),
        }

    def retrieve_checkout_session(self, session_id: str) -> Any:
        """Retrieve Checkout and expand its customer and subscription."""

        session_id = session_id.strip()

        if not session_id:
            raise ValueError("Checkout Session ID is required.")

        return self.client.checkout.Session.retrieve(
            session_id,
            expand=["subscription", "customer"],
        )
