"""Verified Stripe subscription management for YAffiliate."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.services.stripe_service import StripeService
from app.services.supabase_service import SupabaseService


class SubscriptionService:
    """Manage recurring and fixed-term YAffiliate Pro access."""

    ACTIVE_STATUSES = {"active", "trialing"}

    def __init__(self) -> None:
        """Initialize authenticated and administrative Supabase clients."""
        self.supabase = SupabaseService()
        self.client = self.supabase.client
        self.admin_client = self.supabase.admin_client

    def get_subscription(self, user_id: str) -> dict[str, Any] | None:
        """Return the subscription/access record for a user."""

        user_id = str(user_id or "").strip()

        if not user_id:
            raise ValueError("User ID is required.")

        response = (
            self.admin_client
            .table("subscriptions")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None

    def is_pro(self, user_id: str) -> bool:
        """
        Return True when the user currently has YAffiliate Pro access.

        Pro access can come from:
        1. An active recurring Stripe subscription.
        2. An active fixed-term access period, such as 30 days from Pix.
        """

        subscription = self.get_subscription(user_id)

        if not subscription:
            return False

        plan = str(
            subscription.get("plan") or ""
        ).strip().lower()

        status = str(
            subscription.get("status") or ""
        ).strip().lower()

        access_type = str(
            subscription.get("access_type") or "subscription"
        ).strip().lower()

        if plan != "pro":
            return False

        # ---------------------------------------------------------
        # Recurring Stripe subscription
        # ---------------------------------------------------------
        if access_type == "subscription":
            return status in self.ACTIVE_STATUSES

        # ---------------------------------------------------------
        # Fixed-term access
        # Example: one Pix payment gives 30 days of Pro access.
        # ---------------------------------------------------------
        if access_type == "fixed_term":
            expires_at = subscription.get("access_expires_at")

            if not expires_at:
                return False

            try:
                expiration = datetime.fromisoformat(
                    str(expires_at).replace("Z", "+00:00")
                )

                if expiration.tzinfo is None:
                    expiration = expiration.replace(
                        tzinfo=timezone.utc
                    )

                return (
                    status in self.ACTIVE_STATUSES
                    and expiration > datetime.now(timezone.utc)
                )

            except (TypeError, ValueError):
                return False

        return False

    @staticmethod
    def _stripe_id(value: Any) -> str | None:
        """Extract a Stripe object ID from a string or Stripe object."""

        if value is None:
            return None

        if isinstance(value, str):
            return value

        object_id = getattr(value, "id", None)

        return str(object_id) if object_id else None

    @staticmethod
    def _metadata_value(metadata: Any, key: str) -> str:
        """Safely retrieve a value from Stripe metadata."""

        if metadata is None:
            return ""

        if isinstance(metadata, dict):
            return str(metadata.get(key) or "").strip()

        return str(
            getattr(metadata, key, "") or ""
        ).strip()

    @staticmethod
    def _iso_from_unix(value: Any) -> str | None:
        """Convert a Unix timestamp into a UTC ISO timestamp."""

        if value in (None, ""):
            return None

        try:
            return datetime.fromtimestamp(
                int(value),
                tz=timezone.utc,
            ).isoformat()

        except (TypeError, ValueError, OSError):
            return None

    @staticmethod
    def _database_status(stripe_status: str) -> str:
        """Translate Stripe subscription statuses to YAffiliate statuses."""

        mapping = {
            "active": "active",
            "trialing": "trialing",
            "past_due": "past_due",
            "unpaid": "unpaid",
            "canceled": "cancelled",
            "cancelled": "cancelled",
            "incomplete": "inactive",
            "incomplete_expired": "inactive",
            "paused": "inactive",
        }

        return mapping.get(
            (stripe_status or "").strip().lower(),
            "inactive",
        )

    def sync_from_stripe_subscription(
        self,
        subscription: Any,
        *,
        fallback_user_id: str | None = None,
        checkout_session_id: str | None = None,
        currency: str | None = None,
        country: str | None = None,
    ) -> dict[str, Any]:
        """
        Synchronize a recurring Stripe subscription with Supabase.

        This method is used only for recurring Stripe subscriptions.
        """

        subscription_id = self._stripe_id(subscription)

        if not subscription_id:
            raise ValueError("Stripe subscription ID is required.")

        metadata = getattr(
            subscription,
            "metadata",
            None,
        )

        user_id = (
            self._metadata_value(
                metadata,
                "yaffiliate_user_id",
            )
            or str(fallback_user_id or "").strip()
        )

        if not user_id:
            raise ValueError(
                "Stripe subscription does not contain "
                "a YAffiliate user ID."
            )

        stripe_status = str(
            getattr(subscription, "status", "") or ""
        ).lower()

        record = {
            "user_id": user_id,
            "plan": "pro",
            "status": self._database_status(stripe_status),

            # This record represents a recurring subscription.
            "access_type": "subscription",
            "access_expires_at": None,

            "stripe_customer_id": self._stripe_id(
                getattr(
                    subscription,
                    "customer",
                    None,
                )
            ),
            "stripe_subscription_id": subscription_id,
            "stripe_checkout_session_id": checkout_session_id,

            "country": country,
            "currency": currency,

            "current_period_end": self._iso_from_unix(
                getattr(
                    subscription,
                    "current_period_end",
                    None,
                )
            ),

            "updated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        response = (
            self.admin_client
            .table("subscriptions")
            .upsert(
                record,
                on_conflict="user_id",
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Supabase did not return the "
                "synchronized subscription."
            )

        return response.data[0]

    def activate_fixed_term_access(
        self,
        *,
        user_id: str,
        days: int = 30,
        checkout_session_id: str | None = None,
        currency: str | None = None,
        country: str | None = None,
    ) -> dict[str, Any]:
        """
        Grant fixed-term YAffiliate Pro access.

        Intended for confirmed one-time payments such as Pix.

        IMPORTANT:
        This method does NOT verify a payment. Payment verification must
        happen before this method is called.
        """

        user_id = str(user_id or "").strip()

        if not user_id:
            raise ValueError("User ID is required.")

        if days <= 0:
            raise ValueError(
                "Access duration must be greater than zero."
            )

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=days)

        record = {
            "user_id": user_id,
            "plan": "pro",
            "status": "active",

            # Fixed-term access instead of recurring subscription.
            "access_type": "fixed_term",
            "access_expires_at": expires_at.isoformat(),

            "stripe_checkout_session_id": checkout_session_id,

            "currency": (
                str(currency).strip().lower()
                if currency
                else None
            ),

            "country": (
                str(country).strip().upper()
                if country
                else None
            ),

            "updated_at": now.isoformat(),
        }

        # Do not send optional None values to Supabase.
        record = {
            key: value
            for key, value in record.items()
            if value is not None
        }

        response = (
            self.admin_client
            .table("subscriptions")
            .upsert(
                record,
                on_conflict="user_id",
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Supabase did not return the "
                "activated fixed-term access."
            )

        return response.data[0]

    def activate_from_checkout(
        self,
        *,
        session_id: str,
        expected_user_id: str,
    ) -> dict[str, Any]:
        """
        Verify a completed recurring Stripe Checkout Session
        and activate YAffiliate Pro.
        """

        session_id = str(
            session_id or ""
        ).strip()

        expected_user_id = str(
            expected_user_id or ""
        ).strip()

        if not session_id:
            raise ValueError(
                "Checkout Session ID is required."
            )

        if not expected_user_id:
            raise ValueError(
                "Authenticated user ID is required."
            )

        stripe_service = StripeService()

        session = (
            stripe_service.retrieve_checkout_session(
                session_id
            )
        )

        session_user_id = str(
            getattr(
                session,
                "client_reference_id",
                "",
            )
            or ""
        ).strip()

        if session_user_id != expected_user_id:
            raise ValueError(
                "Stripe Checkout does not belong "
                "to the signed-in user."
            )

        session_status = str(
            getattr(
                session,
                "status",
                "",
            )
            or ""
        ).lower()

        if session_status != "complete":
            raise ValueError(
                "Stripe Checkout has not been completed."
            )

        payment_status = str(
            getattr(
                session,
                "payment_status",
                "",
            )
            or ""
        ).lower()

        if payment_status not in {
            "paid",
            "no_payment_required",
        }:
            raise ValueError(
                "Stripe has not confirmed payment "
                "for this Checkout."
            )

        subscription = getattr(
            session,
            "subscription",
            None,
        )

        if subscription is None:
            raise ValueError(
                "Stripe did not return a subscription."
            )

        if isinstance(subscription, str):
            subscription = (
                stripe_service
                .client
                .Subscription
                .retrieve(subscription)
            )

        stripe_status = str(
            getattr(
                subscription,
                "status",
                "",
            )
            or ""
        ).lower()

        database_status = self._database_status(
            stripe_status
        )

        if database_status not in self.ACTIVE_STATUSES:
            raise ValueError(
                "Stripe subscription is not active "
                f"(status: {stripe_status})."
            )

        currency = str(
            getattr(
                session,
                "currency",
                "",
            )
            or ""
        ).lower() or None

        country = None

        details = getattr(
            session,
            "customer_details",
            None,
        )

        address = (
            getattr(
                details,
                "address",
                None,
            )
            if details
            else None
        )

        if address:
            value = getattr(
                address,
                "country",
                None,
            )

            country = (
                str(value).upper()
                if value
                else None
            )

        return self.sync_from_stripe_subscription(
            subscription,
            fallback_user_id=expected_user_id,
            checkout_session_id=session_id,
            currency=currency,
            country=country,
        )