"""Saved campaign metadata used by Filtrify Campaign History.

This model stores the information required to list, identify, and reopen a
previously generated campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class SavedCampaign:
    """Represent one campaign stored in Filtrify history.

    Attributes:
        campaign_id:
            Unique identifier for the saved campaign.

        campaign_name:
            Human-readable campaign name.

        product_name:
            Product used to generate the campaign.

        target_keyword:
            Main campaign keyword.

        target_audience:
            Intended campaign audience.

        tone:
            Shared writing tone.

        asset_count:
            Number of generated campaign assets.

        total_estimated_words:
            Combined estimated word count.

        average_quality_score:
            Average quality score for scored assets.

        created_at:
            Time when the campaign was originally generated.

        saved_at:
            Time when the campaign was stored in history.

        data_file:
            Path of the JSON file containing the complete campaign data.
    """

    campaign_id: str
    campaign_name: str
    product_name: str
    target_keyword: str
    target_audience: str
    tone: str
    asset_count: int
    total_estimated_words: int
    average_quality_score: float
    created_at: datetime
    saved_at: datetime
    data_file: str

    def __post_init__(self) -> None:
        """Validate and normalize saved campaign values."""

        text_fields = (
            "campaign_id",
            "campaign_name",
            "product_name",
            "target_keyword",
            "target_audience",
            "tone",
            "data_file",
        )

        for field_name in text_fields:
            field_value = getattr(
                self,
                field_name,
            )

            if not isinstance(
                field_value,
                str,
            ):
                raise TypeError(
                    f"SavedCampaign.{field_name} must be a string."
                )

            cleaned_value = field_value.strip()

            if not cleaned_value:
                raise ValueError(
                    f"SavedCampaign.{field_name} cannot be empty."
                )

            object.__setattr__(
                self,
                field_name,
                cleaned_value,
            )

        if self.asset_count < 1:
            raise ValueError(
                "SavedCampaign.asset_count must be greater than zero."
            )

        if self.total_estimated_words < 0:
            raise ValueError(
                "SavedCampaign.total_estimated_words cannot be negative."
            )

        if not 0 <= self.average_quality_score <= 100:
            raise ValueError(
                "SavedCampaign.average_quality_score must be between 0 and 100."
            )

        object.__setattr__(
            self,
            "created_at",
            self._ensure_timezone(
                self.created_at
            ),
        )

        object.__setattr__(
            self,
            "saved_at",
            self._ensure_timezone(
                self.saved_at
            ),
        )

    @property
    def display_name(self) -> str:
        """Return a readable campaign-history label."""

        return (
            f"{self.campaign_name} — "
            f"{self.saved_at.strftime('%d %b %Y, %H:%M')}"
        )

    @property
    def summary(self) -> str:
        """Return a compact campaign-history summary."""

        return (
            f"{self.product_name} | "
            f"{self.asset_count} assets | "
            f"{self.total_estimated_words:,} words | "
            f"{self.average_quality_score:.1f}/100"
        )

    def to_dictionary(self) -> dict[str, object]:
        """Convert the saved campaign metadata into a dictionary."""

        return {
            "campaign_id": self.campaign_id,
            "campaign_name": self.campaign_name,
            "product_name": self.product_name,
            "target_keyword": self.target_keyword,
            "target_audience": self.target_audience,
            "tone": self.tone,
            "asset_count": self.asset_count,
            "total_estimated_words": self.total_estimated_words,
            "average_quality_score": self.average_quality_score,
            "created_at": self.created_at.isoformat(),
            "saved_at": self.saved_at.isoformat(),
            "data_file": self.data_file,
        }

    @classmethod
    def from_dictionary(
        cls,
        data: dict[str, object],
    ) -> "SavedCampaign":
        """Create saved campaign metadata from a dictionary."""

        return cls(
            campaign_id=str(
                data["campaign_id"]
            ),
            campaign_name=str(
                data["campaign_name"]
            ),
            product_name=str(
                data["product_name"]
            ),
            target_keyword=str(
                data["target_keyword"]
            ),
            target_audience=str(
                data["target_audience"]
            ),
            tone=str(
                data["tone"]
            ),
            asset_count=int(
                data["asset_count"]
            ),
            total_estimated_words=int(
                data["total_estimated_words"]
            ),
            average_quality_score=float(
                data["average_quality_score"]
            ),
            created_at=datetime.fromisoformat(
                str(
                    data["created_at"]
                )
            ),
            saved_at=datetime.fromisoformat(
                str(
                    data["saved_at"]
                )
            ),
            data_file=str(
                data["data_file"]
            ),
        )

    @staticmethod
    def _ensure_timezone(
        value: datetime,
    ) -> datetime:
        """Return a timezone-aware datetime value."""

        if not isinstance(
            value,
            datetime,
        ):
            raise TypeError(
                "Campaign date values must be datetime instances."
            )

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value