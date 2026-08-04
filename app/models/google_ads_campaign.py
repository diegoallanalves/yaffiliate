"""Google Ads campaign models used by Filtrify."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GoogleAdsAsset:
    """Represent one Google Ads campaign."""

    campaign_name: str

    headlines: tuple[str, ...] = field(default_factory=tuple)

    descriptions: tuple[str, ...] = field(default_factory=tuple)

    keywords: tuple[str, ...] = field(default_factory=tuple)

    negative_keywords: tuple[str, ...] = field(default_factory=tuple)

    call_to_action: str = ""

    target_audience: str = ""

    def __post_init__(self) -> None:

        object.__setattr__(
            self,
            "headlines",
            tuple(
                item.strip()
                for item in self.headlines
                if item.strip()
            ),
        )

        object.__setattr__(
            self,
            "descriptions",
            tuple(
                item.strip()
                for item in self.descriptions
                if item.strip()
            ),
        )

        object.__setattr__(
            self,
            "keywords",
            tuple(
                item.strip()
                for item in self.keywords
                if item.strip()
            ),
        )

        object.__setattr__(
            self,
            "negative_keywords",
            tuple(
                item.strip()
                for item in self.negative_keywords
                if item.strip()
            ),
        )

        object.__setattr__(
            self,
            "campaign_name",
            self.campaign_name.strip(),
        )

        object.__setattr__(
            self,
            "call_to_action",
            self.call_to_action.strip(),
        )

        object.__setattr__(
            self,
            "target_audience",
            self.target_audience.strip(),
        )

    @property
    def headline_count(self) -> int:
        return len(self.headlines)

    @property
    def description_count(self) -> int:
        return len(self.descriptions)

    @property
    def keyword_count(self) -> int:
        return len(self.keywords)

    def to_plain_text(self) -> str:

        lines = [
            self.campaign_name,
            "",
            "HEADLINES",
        ]

        lines.extend(self.headlines)

        lines.extend(
            [
                "",
                "DESCRIPTIONS",
            ]
        )

        lines.extend(self.descriptions)

        lines.extend(
            [
                "",
                "KEYWORDS",
            ]
        )

        lines.extend(self.keywords)

        lines.extend(
            [
                "",
                "NEGATIVE KEYWORDS",
            ]
        )

        lines.extend(self.negative_keywords)

        lines.extend(
            [
                "",
                "CALL TO ACTION",
                self.call_to_action,
            ]
        )

        return "\n".join(lines)