"""Campaign History service using Supabase."""

from __future__ import annotations

import json
from typing import Any

from app.repositories.campaign_repository import CampaignRepository


class CampaignHistorySupabaseService:
    """Manage Campaign History stored in Supabase."""

    def __init__(self) -> None:
        self.repository = CampaignRepository()

    def list_campaigns(self):
        """Return all campaigns."""

        response = (
            self.repository.client
            .table("campaigns")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    def load_campaign_data(
        self,
        campaign_id: str,
    ) -> dict[str, Any]:

        response = (
            self.repository.client
            .table("campaigns")
            .select("*")
            .eq("id", campaign_id)
            .single()
            .execute()
        )

        return json.loads(
            response.data["campaign"]
        )

    def delete_campaign(
        self,
        campaign_id: str,
    ) -> None:

        (
            self.repository.client
            .table("campaigns")
            .delete()
            .eq("id", campaign_id)
            .execute()
        )

    def clear_history(self) -> None:

        (
            self.repository.client
            .table("campaigns")
            .delete()
            .neq("id", "")
            .execute()
        )

    def count_campaigns(self) -> int:

        return len(
            self.list_campaigns()
        )