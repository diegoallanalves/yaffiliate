"""Supabase connection service for YAffiliate."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


class SupabaseService:
    """
    Provide Supabase clients for YAffiliate.

    Normal clients restore the signed-in Streamlit user's Supabase
    session so Row Level Security (RLS) can evaluate auth.uid().
    """

    def __init__(self) -> None:
        url = os.getenv("SUPABASE_URL", "").strip()
        public_key = os.getenv("SUPABASE_KEY", "").strip()
        service_role_key = os.getenv(
            "SUPABASE_SERVICE_ROLE_KEY",
            "",
        ).strip()

        if not url:
            raise ValueError("SUPABASE_URL is not configured.")

        if not public_key:
            raise ValueError("SUPABASE_KEY is not configured.")

        if not service_role_key:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY is not configured."
            )

        self.client: Client = create_client(url, public_key)
        self.admin_client: Client = create_client(
            url,
            service_role_key,
        )

        self._restore_streamlit_session()

    def _restore_streamlit_session(self) -> None:
        """
        Restore the current user's access/refresh tokens on this client.

        A fresh Supabase client is intentionally created for repository
        operations. This is important because repository objects can be
        created before the user signs in during Streamlit module loading.
        """
        try:
            import streamlit as st

            access_token = str(
                st.session_state.get(
                    "supabase_access_token",
                    "",
                )
                or ""
            ).strip()

            refresh_token = str(
                st.session_state.get(
                    "supabase_refresh_token",
                    "",
                )
                or ""
            ).strip()

        except Exception:
            return

        if not access_token or not refresh_token:
            return

        try:
            response = self.client.auth.set_session(
                access_token,
                refresh_token,
            )

            session = getattr(response, "session", None)

            if session is not None:
                new_access_token = getattr(
                    session,
                    "access_token",
                    None,
                )
                new_refresh_token = getattr(
                    session,
                    "refresh_token",
                    None,
                )

                if new_access_token:
                    st.session_state[
                        "supabase_access_token"
                    ] = str(new_access_token)

                if new_refresh_token:
                    st.session_state[
                        "supabase_refresh_token"
                    ] = str(new_refresh_token)

        except Exception:
            return

    def test_connection(self) -> bool:
        response = (
            self.client
            .table("campaigns")
            .select("id")
            .limit(1)
            .execute()
        )
        return response.data is not None

    def test_admin_connection(self) -> bool:
        response = (
            self.admin_client
            .table("subscriptions")
            .select("id")
            .limit(1)
            .execute()
        )
        return response.data is not None
