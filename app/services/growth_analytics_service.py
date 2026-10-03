"""Growth analytics service for YAffiliate."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import streamlit as st

from app.services.supabase_service import SupabaseService


class GrowthAnalyticsService:
    """Record customer-acquisition and conversion events."""

    TABLE_NAME = "growth_events"

    def __init__(self) -> None:
        self.supabase = SupabaseService()
        self.client = self.supabase.admin_client

    @staticmethod
    def get_session_id() -> str:
        """
        Return a lightweight anonymous session identifier.

        This allows multiple events in the same Streamlit session to
        be connected even before the visitor signs in.
        """
        if "growth_session_id" not in st.session_state:
            st.session_state["growth_session_id"] = str(uuid4())

        return str(st.session_state["growth_session_id"])

    @staticmethod
    def capture_utm_parameters() -> None:
        """
        Capture acquisition parameters from the URL once and preserve
        them throughout the Streamlit session.
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