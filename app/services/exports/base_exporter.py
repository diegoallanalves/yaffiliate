"""Shared helpers for Filtrify export services."""

from __future__ import annotations

import re
from abc import ABC
from pathlib import Path
from typing import Any


class BaseExporter(ABC):
    """Provide reusable validation, naming, and file-writing helpers."""

    @staticmethod
    def validate_campaign(campaign: Any) -> None:
        """Validate that an object resembles a CampaignPackage."""

        required_attributes = (
            "campaign_name",
            "product_name",
            "seo_article",
            "landing_page",
            "email_sequence",
            "google_ads",
            "created_at",
        )

        missing_attributes = [
            attribute
            for attribute in required_attributes
            if not hasattr(campaign, attribute)
        ]

        if missing_attributes:
            raise TypeError(
                "campaign must be a CampaignPackage-compatible object. "
                "Missing attributes: "
                + ", ".join(missing_attributes)
            )

    @staticmethod
    def safe_file_stem(value: str, fallback: str = "filtrify_campaign") -> str:
        """Return a safe file-name stem without an extension."""

        cleaned_value = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            str(value).strip(),
        )
        cleaned_value = re.sub(
            r"_+",
            "_",
            cleaned_value,
        ).strip("_")

        return cleaned_value or fallback

    @classmethod
    def build_file_name(
        cls,
        *,
        stem: str,
        extension: str,
    ) -> str:
        """Build a safe file name using the requested extension."""

        clean_extension = extension.strip().lower().lstrip(".")
        if not clean_extension:
            raise ValueError("File extension cannot be empty.")

        return f"{cls.safe_file_stem(stem)}.{clean_extension}"

    @staticmethod
    def ensure_output_directory(
        output_directory: str | Path,
    ) -> Path:
        """Create and return an output directory."""

        path = Path(output_directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def write_bytes(
        cls,
        *,
        data: bytes,
        output_directory: str | Path,
        file_name: str,
    ) -> Path:
        """Write bytes to disk and return the created path."""

        directory = cls.ensure_output_directory(output_directory)
        destination = directory / file_name
        destination.write_bytes(data)
        return destination

    @classmethod
    def write_text(
        cls,
        *,
        data: str,
        output_directory: str | Path,
        file_name: str,
        encoding: str = "utf-8",
    ) -> Path:
        """Write text to disk and return the created path."""

        directory = cls.ensure_output_directory(output_directory)
        destination = directory / file_name
        destination.write_text(data, encoding=encoding)
        return destination
