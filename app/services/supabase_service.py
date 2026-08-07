from __future__ import annotations

import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


class SupabaseService:
    def __init__(self) -> None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be configured."
            )

        self.client: Client = create_client(url, key)

    def test_connection(self) -> bool:
        response = (
            self.client
            .table("campaigns")
            .select("id")
            .limit(1)
            .execute()
        )

        return response.data is not None