"""Export generated Filtrify campaigns.

This first version exports a complete CampaignPackage as a JSON file.

JSON means JavaScript Object Notation.

JSON is a structured text format commonly used for storing and exchanging
application data.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from app.services.campaign_generator_service import (
    CampaignPackage,
)


class CampaignExportService:
    """Export Filtrify campaign packages into reusable files."""

    def export_json(
        self,
        *,
        campaign: CampaignPackage,
        output_directory: str | Path = "outputs/campaigns",
        file_name: str | None = None,
    ) -> Path:
        """Export one campaign as a JSON file.

        Args:
            campaign:
                Generated campaign package to export.

            output_directory:
                Folder where the JSON file should be created.

            file_name:
                Optional custom file name. When omitted, Filtrify creates a
                safe name from the campaign name.

        Returns:
            The complete path of the created JSON file.
        """

        self._validate_campaign(
            campaign
        )

        destination_directory = Path(
            output_directory
        )

        destination_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        resolved_file_name = (
            self._resolve_json_file_name(
                campaign=campaign,
                file_name=file_name,
            )
        )

        destination_path = (
            destination_directory
            / resolved_file_name
        )

        campaign_data = self.to_dictionary(
            campaign
        )

        destination_path.write_text(
            json.dumps(
                campaign_data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return destination_path

    def to_json(
        self,
        campaign: CampaignPackage,
        *,
        indent: int = 2,
    ) -> str:
        """Convert a campaign package into a JSON string.

        This method is useful for Streamlit download buttons because it
        returns the JSON content without first creating a file.
        """

        self._validate_campaign(
            campaign
        )

        return json.dumps(
            self.to_dictionary(
                campaign
            ),
            ensure_ascii=False,
            indent=indent,
        )

    def to_dictionary(
        self,
        campaign: CampaignPackage,
    ) -> dict[str, Any]:
        """Convert a campaign package into a serializable dictionary."""

        self._validate_campaign(
            campaign
        )

        campaign_data = asdict(
            campaign
        )

        campaign_data[
            "created_at"
        ] = campaign.created_at.isoformat()

        campaign_data[
            "campaign_summary"
        ] = {
            "asset_count": campaign.asset_count,
            "total_estimated_words": (
                campaign.total_estimated_words
            ),
            "average_quality_score": (
                campaign.average_quality_score
            ),
        }

        return campaign_data

    @staticmethod
    def _validate_campaign(
        campaign: CampaignPackage,
    ) -> None:
        """Validate the campaign supplied for export."""

        if not isinstance(
            campaign,
            CampaignPackage,
        ):
            raise TypeError(
                "campaign must be a CampaignPackage instance."
            )

    def _resolve_json_file_name(
        self,
        *,
        campaign: CampaignPackage,
        file_name: str | None,
    ) -> str:
        """Resolve a valid JSON export file name."""

        if (
            file_name
            and file_name.strip()
        ):
            cleaned_file_name = (
                file_name.strip()
            )

            if not cleaned_file_name.casefold().endswith(
                ".json"
            ):
                cleaned_file_name = (
                    f"{cleaned_file_name}.json"
                )

            return self._sanitize_file_name(
                cleaned_file_name
            )

        timestamp = campaign.created_at.strftime(
            "%Y%m%d_%H%M%S"
        )

        campaign_name = self._sanitize_file_name(
            campaign.campaign_name
        )

        return (
            f"{campaign_name}_{timestamp}.json"
        )

    @staticmethod
    def _sanitize_file_name(
        value: str,
    ) -> str:
        """Convert text into a file-system-safe name."""

        cleaned_characters = [
            character
            if (
                character.isalnum()
                or character in {
                    "-",
                    "_",
                    ".",
                }
            )
            else "_"
            for character in value.strip()
        ]

        cleaned_value = "".join(
            cleaned_characters
        )

        while "__" in cleaned_value:
            cleaned_value = cleaned_value.replace(
                "__",
                "_",
            )

        cleaned_value = cleaned_value.strip(
            "._"
        )

        if not cleaned_value:
            return "filtrify_campaign"

        return cleaned_value