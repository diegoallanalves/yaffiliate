"""Stripe webhook endpoint for YAffiliate."""

from __future__ import annotations

import os
from typing import Any

import stripe
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from app.services.stripe_service import StripeService
from app.services.subscription_service import SubscriptionService
from app.services.supabase_service import SupabaseService


load_dotenv()

app = FastAPI(
    title="YAFFiliate Stripe Webhooks",
    version="1.0.0",
)


# =============================================================
# GROWTH ANALYTICS
# =============================================================

def _track_growth_event(
    event_name: str,
    *,
    user_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Record a server-side growth event.

    Webhook analytics must not depend on Streamlit session state.
    Analytics failures must never break Stripe webhook processing.
    """

    event_name = str(event_name or "").strip()

    if not event_name:
        return

    resolved_user_id = str(user_id or "").strip() or None

    payload = {
        "user_id": resolved_user_id,
        "session_id": None,
        "event_name": event_name,
        "event_page": "stripe_webhook",
        "utm_source": None,
        "utm_medium": None,
        "utm_campaign": None,
        "utm_content": None,
        "utm_term": None,
        "metadata": metadata or {},
    }

    try:
        SupabaseService().admin_client.table(
            "growth_events"
        ).insert(payload).execute()

    except Exception:
        # Analytics must never cause Stripe to retry a valid webhook.
        pass


# =============================================================
# HEALTH
# =============================================================

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# =============================================================
# STRIPE WEBHOOK
# =============================================================

@app.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
) -> dict[str, str]:

    webhook_secret = os.getenv(
        "STRIPE_WEBHOOK_SECRET",
        "",
    ).strip()

    if not webhook_secret:
        raise HTTPException(
            status_code=500,
            detail="STRIPE_WEBHOOK_SECRET is not configured.",
        )

    payload = await request.body()
    signature = request.headers.get(
        "stripe-signature",
        "",
    )

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

    event_type = str(
        getattr(event, "type", "") or ""
    )

    event_object = event["data"]["object"]

    subscription_service = SubscriptionService()
    stripe_service = StripeService()

    # =========================================================
    # CHECKOUT COMPLETED
    # =========================================================

    if event_type == "checkout.session.completed":

        user_id = str(
            getattr(
                event_object,
                "client_reference_id",
                "",
            )
            or ""
        ).strip()

        session_id = str(
            getattr(
                event_object,
                "id",
                "",
            )
            or ""
        ).strip()

        payment_status = str(
            getattr(
                event_object,
                "payment_status",
                "",
            )
            or ""
        ).strip()

        currency = str(
            getattr(
                event_object,
                "currency",
                "",
            )
            or ""
        ).strip().upper()

        amount_total = getattr(
            event_object,
            "amount_total",
            None,
        )

        subscription_id = str(
            getattr(
                event_object,
                "subscription",
                "",
            )
            or ""
        ).strip()

        if user_id and session_id:

            subscription_service.activate_from_checkout(
                session_id=session_id,
                expected_user_id=user_id,
            )

            # Record the authoritative completed checkout.
            _track_growth_event(
                "subscription_started",
                user_id=user_id,
                metadata={
                    "stripe_checkout_session_id": session_id,
                    "stripe_subscription_id": (
                        subscription_id or None
                    ),
                    "payment_status": (
                        payment_status or None
                    ),
                    "currency": (
                        currency or None
                    ),
                    "amount_total": amount_total,
                },
            )

    # =========================================================
    # SUBSCRIPTION CREATED / UPDATED / DELETED
    # =========================================================

    elif event_type in {
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    }:

        subscription_service.sync_from_stripe_subscription(
            event_object
        )

    # =========================================================
    # INVOICE PAYMENT
    # =========================================================

    elif event_type in {
        "invoice.paid",
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
                if isinstance(
                    subscription_value,
                    str,
                )
                else getattr(
                    subscription_value,
                    "id",
                    None,
                )
            )

            if subscription_id:

                subscription = (
                    stripe_service.client
                    .Subscription.retrieve(
                        subscription_id
                    )
                )

                subscription_service.sync_from_stripe_subscription(
                    subscription
                )

    return {
        "received": "true",
        "event": event_type,
    }