"""Campaign History service backed by Supabase."""

from __future__ import annotations

from typing import Any

from app.repositories.campaign_repository import CampaignRepository
from app.services.auth_service import AuthService
from app.services.campaign_record_service import decode_campaign_payload


class CampaignHistorySupabaseService:
    """Manage the authenticated user's campaign history."""

    def __init__(
        self,
        *,
        repository: CampaignRepository | None = None,
        user_id: str | None = None,
    ) -> None:
        self.repository = repository or CampaignRepository()

        self.user_id = (
            user_id
            or AuthService().get_current_user_id()
        )

        if not self.user_id:
            raise ValueError(
                "An authenticated user is required to access campaign history."
            )

    def list_campaigns(self) -> list[dict[str, Any]]:
        return self.repository.list_campaigns(self.user_id)

    def load_campaign_data(
        self,
        campaign_id: str,
    ) -> dict[str, Any]:
        row = self.repository.get_campaign(
            campaign_id,
            self.user_id,
        )

        if row is None:
            raise ValueError(
                "The selected campaign could not be found."
            )

        return decode_campaign_payload(
            row.get("campaign")
        )

    def delete_campaign(
        self,
        campaign_id: str,
    ) -> bool:
        return self.repository.delete_campaign(
            campaign_id,
            self.user_id,
        )

    def clear_history(self) -> int:
        return self.repository.clear_campaigns(
            self.user_id
        )

    def count_campaigns(self) -> int:
        return self.repository.count_campaigns(
            self.user_id
        )