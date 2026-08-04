"""Persist and manage Filtrify campaign history.

This service stores complete campaign JSON files and maintains a lightweight
history index containing campaign metadata.

The history index allows Filtrify to:

- save generated campaigns;
- list saved campaigns;
- retrieve campaign metadata;
- read saved campaign JSON data;
- delete saved campaigns safely.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.models.saved_campaign import (
    SavedCampaign,
)
from app.services.campaign_export_service import (
    CampaignExportService,
)
from app.services.campaign_generator_service import (
    CampaignPackage,
)


class CampaignHistoryService:
    """Store and manage generated campaigns on the local file system."""

    def __init__(
        self,
        *,
        storage_directory: str | Path = "outputs/campaign_history",
        campaign_export_service: CampaignExportService | None = None,
    ) -> None:
        """Initialize the campaign-history service.

        Args:
            storage_directory:
                Main folder used for campaign history.

            campaign_export_service:
                Optional export service used to serialize campaigns.
        """

        self._storage_directory = Path(
            storage_directory
        )

        self._campaigns_directory = (
            self._storage_directory
            / "campaigns"
        )

        self._index_file = (
            self._storage_directory
            / "history_index.json"
        )

        self._campaign_export_service = (
            campaign_export_service
            or CampaignExportService()
        )

        self._ensure_storage_exists()

    @property
    def storage_directory(self) -> Path:
        """Return the main campaign-history folder."""

        return self._storage_directory

    @property
    def campaigns_directory(self) -> Path:
        """Return the folder containing saved campaign files."""

        return self._campaigns_directory

    @property
    def index_file(self) -> Path:
        """Return the campaign-history index path."""

        return self._index_file

    def save_campaign(
        self,
        campaign: CampaignPackage,
    ) -> SavedCampaign:
        """Save a complete campaign and return its history metadata.

        Args:
            campaign:
                Campaign package that should be stored.

        Returns:
            SavedCampaign metadata for the newly stored campaign.
        """

        self._validate_campaign(
            campaign
        )

        campaign_id = str(
            uuid4()
        )

        saved_at = datetime.now(
            timezone.utc
        )

        file_name = (
            f"{campaign_id}.json"
        )

        campaign_path = (
            self._campaigns_directory
            / file_name
        )

        campaign_json = (
            self._campaign_export_service.to_json(
                campaign
            )
        )

        campaign_path.write_text(
            campaign_json,
            encoding="utf-8",
        )

        saved_campaign = SavedCampaign(
            campaign_id=campaign_id,
            campaign_name=campaign.campaign_name,
            product_name=campaign.product_name,
            target_keyword=campaign.target_keyword,
            target_audience=campaign.target_audience,
            tone=campaign.tone,
            asset_count=campaign.asset_count,
            total_estimated_words=(
                campaign.total_estimated_words
            ),
            average_quality_score=(
                campaign.average_quality_score
            ),
            created_at=campaign.created_at,
            saved_at=saved_at,
            data_file=str(
                campaign_path
            ),
        )

        history_items = self.list_campaigns()

        history_items.append(
            saved_campaign
        )

        self._write_index(
            history_items
        )

        return saved_campaign

    def list_campaigns(
        self,
    ) -> list[SavedCampaign]:
        """Return all saved campaigns, newest first."""

        raw_items = self._read_index()

        saved_campaigns: list[
            SavedCampaign
        ] = []

        for item in raw_items:
            try:
                saved_campaign = (
                    SavedCampaign.from_dictionary(
                        item
                    )
                )
            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

            saved_campaigns.append(
                saved_campaign
            )

        return sorted(
            saved_campaigns,
            key=lambda campaign: (
                campaign.saved_at
            ),
            reverse=True,
        )

    def get_campaign(
        self,
        campaign_id: str,
    ) -> SavedCampaign | None:
        """Return saved campaign metadata by identifier."""

        cleaned_campaign_id = (
            self._clean_campaign_id(
                campaign_id
            )
        )

        for campaign in self.list_campaigns():
            if (
                campaign.campaign_id
                == cleaned_campaign_id
            ):
                return campaign

        return None

    def load_campaign_data(
        self,
        campaign_id: str,
    ) -> dict[str, Any]:
        """Load the complete saved campaign JSON data.

        This method returns the stored dictionary.

        Reconstructing a CampaignPackage object can be added later when the
        Campaign History page needs to reopen campaigns in the editor.
        """

        saved_campaign = self.get_campaign(
            campaign_id
        )

        if saved_campaign is None:
            raise ValueError(
                "The requested saved campaign does not exist."
            )

        campaign_path = Path(
            saved_campaign.data_file
        )

        if not campaign_path.exists():
            raise FileNotFoundError(
                "The saved campaign data file could not be found."
            )

        try:
            loaded_data = json.loads(
                campaign_path.read_text(
                    encoding="utf-8"
                )
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                "The saved campaign file contains invalid JSON."
            ) from error

        if not isinstance(
            loaded_data,
            dict,
        ):
            raise ValueError(
                "The saved campaign data must contain a JSON object."
            )

        return loaded_data

    def delete_campaign(
        self,
        campaign_id: str,
    ) -> bool:
        """Delete one saved campaign and its metadata.

        Returns:
            True when a campaign was deleted.
            False when the campaign did not exist.
        """

        cleaned_campaign_id = (
            self._clean_campaign_id(
                campaign_id
            )
        )

        history_items = self.list_campaigns()

        selected_campaign = next(
            (
                campaign
                for campaign in history_items
                if (
                    campaign.campaign_id
                    == cleaned_campaign_id
                )
            ),
            None,
        )

        if selected_campaign is None:
            return False

        campaign_path = Path(
            selected_campaign.data_file
        )

        if campaign_path.exists():
            campaign_path.unlink()

        remaining_items = [
            campaign
            for campaign in history_items
            if (
                campaign.campaign_id
                != cleaned_campaign_id
            )
        ]

        self._write_index(
            remaining_items
        )

        return True

    def clear_history(
        self,
    ) -> int:
        """Delete all saved campaigns.

        Returns:
            Number of campaigns removed.
        """

        history_items = self.list_campaigns()

        removed_count = 0

        for campaign in history_items:
            campaign_path = Path(
                campaign.data_file
            )

            if campaign_path.exists():
                campaign_path.unlink()

            removed_count += 1

        self._write_index(
            []
        )

        return removed_count

    def count_campaigns(
        self,
    ) -> int:
        """Return the number of saved campaigns."""

        return len(
            self.list_campaigns()
        )

    def _ensure_storage_exists(
        self,
    ) -> None:
        """Create the required history folders and index."""

        self._campaigns_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self._index_file.exists():
            self._index_file.write_text(
                "[]",
                encoding="utf-8",
            )

    def _read_index(
        self,
    ) -> list[dict[str, Any]]:
        """Read the raw campaign-history index."""

        self._ensure_storage_exists()

        try:
            loaded_data = json.loads(
                self._index_file.read_text(
                    encoding="utf-8"
                )
            )
        except json.JSONDecodeError:
            return []

        if not isinstance(
            loaded_data,
            list,
        ):
            return []

        return [
            item
            for item in loaded_data
            if isinstance(
                item,
                dict,
            )
        ]

    def _write_index(
        self,
        campaigns: list[SavedCampaign],
    ) -> None:
        """Write campaign metadata to the history index."""

        sorted_campaigns = sorted(
            campaigns,
            key=lambda campaign: (
                campaign.saved_at
            ),
            reverse=True,
        )

        serialized_campaigns = [
            campaign.to_dictionary()
            for campaign in sorted_campaigns
        ]

        temporary_file = (
            self._index_file
            .with_suffix(
                ".tmp"
            )
        )

        temporary_file.write_text(
            json.dumps(
                serialized_campaigns,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temporary_file.replace(
            self._index_file
        )

    @staticmethod
    def _validate_campaign(
        campaign: CampaignPackage,
    ) -> None:
        """Validate the campaign supplied for storage."""

        if not isinstance(
            campaign,
            CampaignPackage,
        ):
            raise TypeError(
                "campaign must be a CampaignPackage instance."
            )

    @staticmethod
    def _clean_campaign_id(
        campaign_id: str,
    ) -> str:
        """Validate and normalize a campaign identifier."""

        if not isinstance(
            campaign_id,
            str,
        ):
            raise TypeError(
                "campaign_id must be a string."
            )

        cleaned_campaign_id = (
            campaign_id.strip()
        )

        if not cleaned_campaign_id:
            raise ValueError(
                "campaign_id cannot be empty."
            )

        return cleaned_campaign_id