"""JSON exports for Filtrify campaigns."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.services.exports.base_exporter import BaseExporter


class JsonExporter(BaseExporter):
    """Export complete campaign data as JSON."""

    def to_dictionary(self, campaign: Any) -> dict[str, Any]:
        """Convert a campaign into a JSON-serializable dictionary."""

        self.validate_campaign(campaign)

        if is_dataclass(campaign):
            payload = asdict(campaign)
        else:
            payload = dict(vars(campaign))

        payload["campaign_summary"] = {
            "asset_count": campaign.asset_count,
            "total_estimated_words": campaign.total_estimated_words,
            "average_quality_score": campaign.average_quality_score,
        }

        return self._normalize(payload)

    def to_json(
        self,
        campaign: Any,
        *,
        indent: int = 2,
    ) -> str:
        """Return the complete campaign as JSON text."""

        return json.dumps(
            self.to_dictionary(campaign),
            ensure_ascii=False,
            indent=indent,
        )

    def to_bytes(
        self,
        campaign: Any,
        *,
        indent: int = 2,
    ) -> bytes:
        """Return the complete campaign as UTF-8 JSON bytes."""

        return self.to_json(
            campaign,
            indent=indent,
        ).encode("utf-8")

    def export(
        self,
        campaign: Any,
        *,
        output_directory: str | Path = "outputs/campaigns",
        file_name: str | None = None,
    ) -> Path:
        """Write a complete campaign JSON file to disk."""

        self.validate_campaign(campaign)

        resolved_name = file_name or self.build_file_name(
            stem=campaign.campaign_name,
            extension="json",
        )

        if not resolved_name.lower().endswith(".json"):
            resolved_name = self.build_file_name(
                stem=resolved_name,
                extension="json",
            )

        return self.write_bytes(
            data=self.to_bytes(campaign),
            output_directory=output_directory,
            file_name=resolved_name,
        )

    def _normalize(self, value: Any) -> Any:
        """Recursively normalize values for JSON serialization."""

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, Path):
            return str(value)

        if isinstance(value, dict):
            return {
                str(key): self._normalize(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [
                self._normalize(item)
                for item in value
            ]

        if is_dataclass(value):
            return self._normalize(asdict(value))

        return value
