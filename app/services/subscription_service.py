"""Stripe webhook endpoint for YAffiliate (FastAPI / Render)."""

from __future__ import annotations

import logging
import os
from typing import Any

import stripe
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from app.services.stripe_service import StripeService
from app.services.subscription_service import SubscriptionService
from app.services.supabase_service import SupabaseService

load_dotenv()
logger = logging.getLogger(__name__)
app = FastAPI(title="YAFFiliate Stripe Webhooks", version="1.1.0")


def _field(obj: Any, key: str, default: Any = None) -> Any:
    """Read a field from either a Stripe object or a dictionary."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _stripe_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    result = _field(value, "id") if value is not None else None
    return str(result).strip() if result else None


def _invoice_subscription_id(invoice: Any) -> str | None:
    """Support both legacy and newer Stripe invoice API shapes."""
    direct = _stripe_id(_field(invoice, "subscription"))
    if direct:
        return direct
    parent = _field(invoice, "parent")
    details = _field(parent, "subscription_details")
    return _stripe_id(_field(details, "subscription"))


def _track_growth_event(
    event_name: str,
    *,
    user_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Best-effort analytics; never block payment processing."""
    if not event_name.strip():
        return
    payload = {
        "user_id": str(user_id or "").strip() or None,
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
        SupabaseService().admin_client.table("growth_events").insert(payload).execute()
    except Exception:
        logger.exception("Growth event could not be recorded: %s", event_name)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/stripe/webhook")
async def stripe_webhook(request: Request) -> dict[str, str]:
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
    if not secret:
        logger.error("STRIPE_WEBHOOK_SECRET is not configured")
        raise HTTPException(status_code=500, detail="Webhook is not configured.")

    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=signature, secret=secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        logger.warning("Rejected Stripe webhook: invalid payload or signature")
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook.") from exc

    event_type = str(_field(event, "type", "") or "")
    event_id = str(_field(event, "id", "") or "")
    event_object = _field(_field(event, "data"), "object")
    logger.info("Stripe webhook received: event_id=%s type=%s", event_id, event_type)

    try:
        # Initialize services only for events that require database updates.
        if event_type == "checkout.session.completed":
            user_id = str(_field(event_object, "client_reference_id", "") or "").strip()
            session_id = _stripe_id(event_object)
            if not user_id or not session_id:
                raise ValueError("Checkout event missing user ID or session ID.")

            SubscriptionService().activate_from_checkout(
                session_id=session_id, expected_user_id=user_id
            )
            _track_growth_event(
                "subscription_started",
                user_id=user_id,
                metadata={
                    "stripe_event_id": event_id,
                    "stripe_checkout_session_id": session_id,
                    "stripe_subscription_id": _stripe_id(
                        _field(event_object, "subscription")
                    ),
                    "payment_status": _field(event_object, "payment_status"),
                    "currency": _field(event_object, "currency"),
                    "amount_total": _field(event_object, "amount_total"),
                },
            )

        elif event_type in {
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        }:
            # Retrieve current Stripe state to avoid applying stale events out of order.
            subscription_id = _stripe_id(event_object)
            if not subscription_id:
                raise ValueError("Subscription event missing subscription ID.")
            if event_type == "customer.subscription.deleted":
                # Deleted subscriptions cannot always be retrieved; use event snapshot.
                subscription = event_object
            else:
                subscription = StripeService().client.Subscription.retrieve(
                    subscription_id
                )
            SubscriptionService().sync_from_stripe_subscription(subscription)

        elif event_type in {
            "invoice.paid",
            "invoice.payment_succeeded",
            "invoice.payment_failed",
        }:
            subscription_id = _invoice_subscription_id(event_object)
            if not subscription_id:
                # One-time invoices may have no subscription; log explicitly.
                logger.info(
                    "Invoice event has no subscription: event_id=%s invoice_id=%s",
                    event_id, _stripe_id(event_object),
                )
            else:
                subscription = StripeService().client.Subscription.retrieve(
                    subscription_id
                )
                record = SubscriptionService().sync_from_stripe_subscription(
                    subscription
                )
                logger.info(
                    "Invoice synchronized: event_id=%s subscription_id=%s status=%s",
                    event_id, subscription_id, record.get("status"),
                )
        else:
            logger.info("Stripe event ignored: event_id=%s type=%s", event_id, event_type)

    except Exception as exc:
        # A non-2xx response lets Stripe retry a processing failure.
        logger.exception("Stripe event processing failed: event_id=%s type=%s", event_id, event_type)
        raise HTTPException(status_code=500, detail="Webhook processing failed.") from exc

    logger.info("Stripe webhook processed: event_id=%s type=%s", event_id, event_type)
    return {"received": "true", "event": event_type}
