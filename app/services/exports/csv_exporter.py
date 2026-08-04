"""CSV exports for Filtrify campaign advertising assets."""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from app.services.exports.base_exporter import BaseExporter


class CsvExporter(BaseExporter):
    """Export Google Ads and keyword data as spreadsheet-friendly CSV."""

    def google_ads_to_csv(self, google_ads: Any) -> str:
        """Return Google Ads assets as one UTF-8 CSV string."""

        required = (
            "campaign_name",
            "headlines",
            "descriptions",
            "keywords",
            "negative_keywords",
            "call_to_action",
        )
        missing = [
            attribute
            for attribute in required
            if not hasattr(google_ads, attribute)
        ]
        if missing:
            raise TypeError(
                "google_ads is missing required attributes: "
                + ", ".join(missing)
            )

        stream = io.StringIO(newline="")
        writer = csv.writer(stream)

        writer.writerow(
            [
                "campaign_name",
                "asset_type",
                "position",
                "text",
            ]
        )

        for asset_type, items in (
            ("headline", google_ads.headlines),
            ("description", google_ads.descriptions),
            ("keyword", google_ads.keywords),
            ("negative_keyword", google_ads.negative_keywords),
        ):
            for position, text in enumerate(items, start=1):
                writer.writerow(
                    [
                        google_ads.campaign_name,
                        asset_type,
                        position,
                        text,
                    ]
                )

        writer.writerow(
            [
                google_ads.campaign_name,
                "call_to_action",
                1,
                google_ads.call_to_action,
            ]
        )

        return stream.getvalue()

    def google_ads_to_bytes(self, google_ads: Any) -> bytes:
        """Return Google Ads CSV as Excel-friendly UTF-8 bytes."""

        return self.google_ads_to_csv(
            google_ads
        ).encode("utf-8-sig")

    def export_google_ads(
        self,
        google_ads: Any,
        *,
        output_directory: str | Path = "outputs/campaigns",
        file_name: str | None = None,
    ) -> Path:
        """Write Google Ads assets to a CSV file."""

        resolved_name = file_name or self.build_file_name(
            stem=f"{google_ads.campaign_name}_google_ads",
            extension="csv",
        )

        if not resolved_name.lower().endswith(".csv"):
            resolved_name = self.build_file_name(
                stem=resolved_name,
                extension="csv",
            )

        return self.write_bytes(
            data=self.google_ads_to_bytes(google_ads),
            output_directory=output_directory,
            file_name=resolved_name,
        )
