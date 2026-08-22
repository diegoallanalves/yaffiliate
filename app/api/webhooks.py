"""Stripe webhook endpoint for YAffiliate."""

from __future__ import annotations

import os

import stripe
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from app.services.stripe_service import StripeService
from app.services.subscription_service import SubscriptionService


load_dotenv()

app = FastAPI(title="YAFFiliate Stripe Webhooks", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request) -> dict[str, str]:
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()

    if not webhook_secret:
        raise HTTPException(
            status_code=500,
            detail="STRIPE_WEBHOOK_SECRET is not configured.",
        )

    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=webhook_secret,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe webhook payload.",
        ) from exc
    except stripe.error.SignatureVerificationError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe webhook signature.",
        ) from exc

    event_type = str(getattr(event, "type", "") or "")
    event_object = event["data"]["object"]

    subscription_service = SubscriptionService()
    stripe_service = StripeService()

    if event_type == "checkout.session.completed":
        user_id = str(
            getattr(event_object, "client_reference_id", "") or ""
        ).strip()
        session_id = str(
            getattr(event_object, "id", "") or ""
        ).strip()

        if user_id and session_id:
            subscription_service.activate_from_checkout(
                session_id=session_id,
                expected_user_id=user_id,
            )

    elif event_type in {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:
        subscription_service.sync_from_stripe_subscription(
            event_object
        )

    elif event_type in {
        "invoice.payment_succeeded",
        "invoice.payment_failed",
    }:
        subscription_value = getattr(
            event_object,
            "subscription",
            None,
        )

        if subscription_value:
            subscription_id = (
                subscription_value
                if isinstance(subscription_value, str)
                else getattr(subscription_value, "id", None)
            )

            if subscription_id:
                subscription = (
                    stripe_service.client.Subscription.retrieve(
                        subscription_id
                    )
                )
                subscription_service.sync_from_stripe_subscription(
                    subscription
                )

    return {"received": "true", "event": event_type}
