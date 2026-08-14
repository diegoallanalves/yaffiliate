"""Stripe payment service for YAffiliate."""

from __future__ import annotations

import os
from typing import Any

import stripe
from dotenv import load_dotenv


class StripeService:
    """Provide Stripe payment operations for YAffiliate."""

    def __init__(self) -> None:
        """Configure Stripe using environment variables."""

        load_dotenv()

        secret_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
        price_id = os.getenv("STRIPE_PRICE_ID", "").strip()

        if not secret_key:
            raise ValueError(
                "STRIPE_SECRET_KEY is not configured."
            )

        if not secret_key.startswith("sk_test_"):
            raise ValueError(
                "YAFFiliate currently requires a Stripe test-mode secret key."
            )

        if not price_id:
            raise ValueError(
                "STRIPE_PRICE_ID is not configured."
            )

        if not price_id.startswith("price_"):
            raise ValueError(
                "STRIPE_PRICE_ID does not appear to be a valid Stripe Price ID."
            )

        stripe.api_key = secret_key

        self.client = stripe
        self.price_id = price_id

    def test_connection(self) -> dict[str, Any]:
        """
        Verify that YAffiliate can communicate with Stripe.

        This retrieves the Stripe account associated with the configured
        test API key. It does not create customers, payments, or charges.
        """

        account = self.client.Account.retrieve()

        return {
            "id": account.id,
            "country": getattr(account, "country", None),
            "email": getattr(account, "email", None),
        }

    def get_price(self) -> dict[str, Any]:
        """Retrieve the configured YAffiliate Pro Stripe price."""

        price = self.client.Price.retrieve(self.price_id)

        recurring = getattr(price, "recurring", None)

        if recurring:
            interval = getattr(recurring, "interval", None)
        else:
            interval = None

        return {
            "id": price.id,
            "active": price.active,
            "currency": price.currency,
            "unit_amount": price.unit_amount,
            "interval": interval,
            "product": price.product,
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

        The session is created in subscription mode using the configured
        Stripe Price ID.

        No payment is charged merely by creating the session.
        """

        user_id = user_id.strip()
        email = email.strip()

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
            success_url=success_url + "&session_id={CHECKOUT_SESSION_ID}",
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
        }