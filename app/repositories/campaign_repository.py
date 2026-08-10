"""Supabase repository for YAffiliate campaigns."""

from __future__ import annotations

from typing import Any

from app.services.supabase_service import SupabaseService


class CampaignRepository:
    """Read and write campaign records in Supabase."""

    def __init__(self) -> None:
        self.client = SupabaseService().client

    def save_campaign(
        self,
        user_id: str,
        product_name: str,
        campaign: str,
    ):
        return (
            self.client
            .table("campaigns")
            .insert(
                {
                    "user_id": user_id,
                    "product_name": product_name,
                    "campaign": campaign,
                }
            )
            .execute()
        )

    def list_campaigns(
        self,
        user_id: str,
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        query = (
            self.client
            .table("campaigns")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
        )

        if limit is not None:
            query = query.limit(limit)

        response = query.execute()
        return list(response.data or [])

    def get_campaign(
        self,
        campaign_id: str,
        user_id: str,
    ) -> dict[str, Any] | None:
        response = (
            self.client
            .table("campaigns")
            .select("*")
            .eq("id", campaign_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        rows = list(response.data or [])
        return rows[0] if rows else None

    def delete_campaign(
        self,
        campaign_id: str,
        user_id: str,
    ) -> bool:
        response = (
            self.client
            .table("campaigns")
            .delete()
            .eq("id", campaign_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(response.data)

    def clear_campaigns(
        self,
        user_id: str,
    ) -> int:
        response = (
            self.client
            .table("campaigns")
            .delete()
            .eq("user_id", user_id)
            .execute()
        )
        return len(response.data or [])

    def count_campaigns(
        self,
        user_id: str,
    ) -> int:
        return len(self.list_campaigns(user_id))
