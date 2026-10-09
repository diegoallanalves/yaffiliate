"""Growth analytics service for YAffiliate."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import streamlit as st

from app.services.supabase_service import SupabaseService


class GrowthAnalyticsService:
    """Record and analyse customer-acquisition events."""

    TABLE_NAME = "growth_events"

    def __init__(self) -> None:
        self.supabase = SupabaseService()
        self.client = self.supabase.admin_client

    @staticmethod
    def get_session_id() -> str:
        """
        Return a lightweight anonymous session identifier.

        This allows multiple events in the same Streamlit session
        to be connected even before the visitor signs in.
        """
        if "growth_session_id" not in st.session_state:
            st.session_state["growth_session_id"] = str(uuid4())

        return str(st.session_state["growth_session_id"])

    @staticmethod
    def capture_utm_parameters() -> None:
        """
        Capture acquisition parameters from the URL once.

        The values remain available throughout the Streamlit session.
        """
        parameters = (
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_content",
            "utm_term",
        )

        for parameter in parameters:
            if st.session_state.get(parameter):
                continue

            try:
                value = st.query_params.get(parameter)
            except Exception:
                value = None

            if value:
                st.session_state[parameter] = str(value)

    def track(
        self,
        event_name: str,
        *,
        event_page: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Write one Growth Analytics event to Supabase."""
        event_name = str(event_name or "").strip()

        if not event_name:
            return False

        self.capture_utm_parameters()

        resolved_user_id = (
            user_id
            or st.session_state.get("auth_user_id")
            or None
        )

        payload = {
            "user_id": (
                str(resolved_user_id)
                if resolved_user_id
                else None
            ),
            "session_id": self.get_session_id(),
            "event_name": event_name,
            "event_page": event_page,
            "utm_source": st.session_state.get("utm_source"),
            "utm_medium": st.session_state.get("utm_medium"),
            "utm_campaign": st.session_state.get("utm_campaign"),
            "utm_content": st.session_state.get("utm_content"),
            "utm_term": st.session_state.get("utm_term"),
            "metadata": metadata or {},
        }

        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .insert(payload)
                .execute()
            )

            return bool(response.data)

        except Exception:
            # Analytics must never break the customer experience.
            return False

    def get_events(
        self,
        limit: int = 5000,
    ) -> list[dict[str, Any]]:
        """Return recent Growth Analytics events."""
        safe_limit = max(1, min(int(limit), 10000))

        response = (
            self.client
            .table(self.TABLE_NAME)
            .select("*")
            .order("created_at", desc=True)
            .limit(safe_limit)
            .execute()
        )

        return list(response.data or [])

    def get_event_counts(
        self,
        limit: int = 5000,
    ) -> dict[str, int]:
        """Return event totals grouped by event name."""
        events = self.get_events(limit=limit)
        counts: dict[str, int] = {}

        for event in events:
            event_name = str(
                event.get("event_name") or ""
            ).strip()

            if not event_name:
                continue

            counts[event_name] = (
                counts.get(event_name, 0) + 1
            )

        return counts

    def get_funnel_metrics(
        self,
        limit: int = 5000,
    ) -> dict[str, int | float]:
        """Return the main YAffiliate conversion funnel."""
        events = self.get_events(limit=limit)

        signup_users: set[str] = set()
        campaign_users: set[str] = set()
        upgrade_users: set[str] = set()
        paid_users: set[str] = set()

        campaign_events = 0
        upgrade_events = 0
        subscription_events = 0

        for event in events:
            event_name = str(
                event.get("event_name") or ""
            ).strip()

            user_id = event.get("user_id")
            user_key = str(user_id) if user_id else ""

            if event_name == "signup":
                if user_key:
                    signup_users.add(user_key)

            elif event_name == "campaign_generated":
                campaign_events += 1

                if user_key:
                    campaign_users.add(user_key)

            elif event_name == "upgrade_clicked":
                upgrade_events += 1

                if user_key:
                    upgrade_users.add(user_key)

            elif event_name == "subscription_started":
                subscription_events += 1

                if user_key:
                    paid_users.add(user_key)

        signups = len(signup_users)
        campaign_users_count = len(campaign_users)
        upgrade_users_count = len(upgrade_users)
        paid_customers = len(paid_users)

        signup_to_campaign = self._percentage(
            campaign_users_count,
            signups,
        )

        campaign_to_upgrade = self._percentage(
            upgrade_users_count,
            campaign_users_count,
        )

        upgrade_to_paid = self._percentage(
            paid_customers,
            upgrade_users_count,
        )

        signup_to_paid = self._percentage(
            paid_customers,
            signups,
        )

        return {
            "signups": signups,
            "campaign_users": campaign_users_count,
            "campaign_events": campaign_events,
            "upgrade_users": upgrade_users_count,
            "upgrade_events": upgrade_events,
            "paid_customers": paid_customers,
            "subscription_events": subscription_events,
            "signup_to_campaign": signup_to_campaign,
            "campaign_to_upgrade": campaign_to_upgrade,
            "upgrade_to_paid": upgrade_to_paid,
            "signup_to_paid": signup_to_paid,
        }

    def get_acquisition_sources(
        self,
        limit: int = 5000,
    ) -> list[dict[str, Any]]:
        """Return event totals grouped by UTM source."""
        events = self.get_events(limit=limit)
        sources: dict[str, int] = {}

        for event in events:
            source = str(
                event.get("utm_source") or "Direct / Unknown"
            ).strip()

            if not source:
                source = "Direct / Unknown"

            sources[source] = sources.get(source, 0) + 1

        ranked = sorted(
            sources.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            {
                "source": source,
                "events": count,
            }
            for source, count in ranked
        ]

    @staticmethod
    def _percentage(
        numerator: int,
        denominator: int,
    ) -> float:
        """Safely calculate a percentage."""
        if denominator <= 0:
            return 0.0

        return round(
            (numerator / denominator) * 100,
            2,
        )