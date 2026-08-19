"""Supabase connection service for YAffiliate."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


class SupabaseService:
    """
    Provide Supabase clients for YAffiliate.

    self.client:
        Normal application client using SUPABASE_KEY.
        Used for authentication and normal user operations.

    self.admin_client:
        Trusted server-side client using SUPABASE_SERVICE_ROLE_KEY.
        Used for privileged backend operations such as synchronizing
        Stripe subscription information.

    IMPORTANT:
        The service-role key must never be exposed to the browser,
        committed to GitHub, or displayed in the Streamlit interface.
    """

    def __init__(self) -> None:
        """Configure the normal and admin Supabase clients."""

        url = os.getenv("SUPABASE_URL", "").strip()
        public_key = os.getenv("SUPABASE_KEY", "").strip()
        service_role_key = os.getenv(
            "SUPABASE_SERVICE_ROLE_KEY",
            "",
        ).strip()

        if not url:
            raise ValueError(
                "SUPABASE_URL is not configured."
            )

        if not public_key:
            raise ValueError(
                "SUPABASE_KEY is not configured."
            )

        if not service_role_key:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY is not configured."
            )

        # Normal application client.
        #
        # Keep this as `self.client` because AuthService and the rest
        # of YAffiliate already use this property.
        self.client: Client = create_client(
            url,
            public_key,
        )

        # Trusted backend client.
        #
        # This client can bypass normal Row Level Security restrictions,
        # so it must only be used by trusted server-side code.
        self.admin_client: Client = create_client(
            url,
            service_role_key,
        )

    def test_connection(self) -> bool:
        """Test the normal Supabase database connection."""

        response = (
            self.client
            .table("campaigns")
            .select("id")
            .limit(1)
            .execute()
        )

        return response.data is not None

    def test_admin_connection(self) -> bool:
        """Test access to subscriptions using the service-role client."""

        response = (
            self.admin_client
            .table("subscriptions")
            .select("id")
            .limit(1)
            .execute()
        )

        return response.data is not None