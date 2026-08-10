"""Campaign History service backed by Supabase."""

from __future__ import annotations

import json
from typing import Any

from app.repositories.campaign_repository import CampaignRepository


BETA_USER_ID = "beta-test-user"


class CampaignHistorySupabaseService:
    """Manage the current user's campaign history."""

    def __init__(
        self,
        *,
        repository: CampaignRepository | None = None,
        user_id: str = BETA_USER_ID,
    ) -> None:
        self.repository = repository or CampaignRepository()
        self.user_id = user_id

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
            raise ValueError("The selected campaign could not be found.")

        campaign_value = row.get("campaign")

        if isinstance(campaign_value, dict):
            return campaign_value

        if not isinstance(campaign_value, str):
            raise ValueError("The saved campaign does not contain valid data.")

        try:
            loaded = json.loads(campaign_value)
        except json.JSONDecodeError as error:
            raise ValueError("The saved campaign contains invalid JSON.") from error

        if not isinstance(loaded, dict):
            raise ValueError("The saved campaign must contain a JSON object.")

        return loaded

    def delete_campaign(
        self,
        campaign_id: str,
    ) -> bool:
        return self.repository.delete_campaign(
            campaign_id,
            self.user_id,
        )

    def clear_history(self) -> int:
        return self.repository.clear_campaigns(self.user_id)

    def count_campaigns(self) -> int:
        return self.repository.count_campaigns(self.user_id)
