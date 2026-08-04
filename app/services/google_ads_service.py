"""Generate Google Ads campaign assets from product intelligence.

This service creates:

- responsive-search-ad headlines;
- ad descriptions;
- target keywords;
- negative keywords;
- a recommended call to action.

CTA means Call to Action.
"""

from __future__ import annotations

from typing import Any

from app.models.discovery_product import (
    DiscoveryProduct,
)
from app.models.google_ads_campaign import (
    GoogleAdsAsset,
)
from app.models.product_analysis import (
    ProductAnalysis,
)
from app.services.base_content_generator import (
    BaseContentGenerator,
)


class GoogleAdsService(BaseContentGenerator):
    """Generate a structured Google Ads campaign."""

    VALID_TONES = {
        "Professional",
        "Friendly",
        "Persuasive",
        "Educational",
    }

    VALID_GOALS = {
        "Visit Sales Page",
        "Generate Leads",
        "Promote Product",
    }

    MAX_HEADLINE_LENGTH = 30
    MAX_DESCRIPTION_LENGTH = 90

    def generate(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        target_keyword: str | None = None,
        keyword: str | None = None,
        target_audience: str | None = None,
        tone: str = "Professional",
        primary_goal: str = "Visit Sales Page",
        campaign_name: str | None = None,
        **kwargs: Any,
    ) -> GoogleAdsAsset:
        """Generate one complete Google Ads campaign."""

        self._validate_inputs(
            product=product,
            analysis=analysis,
        )

        resolved_keyword = self._resolve_keyword(
            product=product,
            target_keyword=target_keyword,
            keyword=keyword,
        )

        resolved_audience = self._resolve_audience(
            analysis=analysis,
            target_audience=target_audience,
        )

        resolved_tone = self._resolve_tone(
            tone
        )

        resolved_goal = self._resolve_goal(
            primary_goal
        )

        resolved_campaign_name = (
            self._resolve_campaign_name(
                product=product,
                campaign_name=campaign_name,
            )
        )

        headlines = self._build_headlines(
            product=product,
            keyword=resolved_keyword,
            tone=resolved_tone,
        )

        descriptions = self._build_descriptions(
            product=product,
            analysis=analysis,
            audience=resolved_audience,
            tone=resolved_tone,
        )

        keywords = self._build_keywords(
            product=product,
            keyword=resolved_keyword,
        )

        negative_keywords = (
            self._build_negative_keywords()
        )

        call_to_action = self._build_call_to_action(
            product=product,
            primary_goal=resolved_goal,
        )

        return GoogleAdsAsset(
            campaign_name=resolved_campaign_name,
            headlines=tuple(
                headlines
            ),
            descriptions=tuple(
                descriptions
            ),
            keywords=tuple(
                keywords
            ),
            negative_keywords=tuple(
                negative_keywords
            ),
            call_to_action=call_to_action,
            target_audience=resolved_audience,
        )

    @staticmethod
    def _validate_inputs(
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
    ) -> None:
        """Validate the required generator inputs."""

        if not isinstance(
            product,
            DiscoveryProduct,
        ):
            raise TypeError(
                "product must be a DiscoveryProduct instance."
            )

        if not isinstance(
            analysis,
            ProductAnalysis,
        ):
            raise TypeError(
                "analysis must be a ProductAnalysis instance."
            )

    @staticmethod
    def _resolve_keyword(
        *,
        product: DiscoveryProduct,
        target_keyword: str | None,
        keyword: str | None,
    ) -> str:
        """Resolve the main advertising keyword."""

        possible_values = [
            target_keyword,
            keyword,
            product.product_name,
        ]

        for value in possible_values:
            if (
                isinstance(
                    value,
                    str,
                )
                and value.strip()
            ):
                return value.strip()

        raise ValueError(
            "A Google Ads target keyword is required."
        )

    @staticmethod
    def _resolve_audience(
        *,
        analysis: ProductAnalysis,
        target_audience: str | None,
    ) -> str:
        """Resolve the intended campaign audience."""

        if (
            target_audience
            and target_audience.strip()
        ):
            return target_audience.strip()

        audience_items = [
            str(item).strip()
            for item in analysis.target_audience
            if str(item).strip()
        ]

        if audience_items:
            return ", ".join(
                audience_items
            )

        return "people interested in this product"

    def _resolve_tone(
        self,
        tone: str,
    ) -> str:
        """Validate and normalize the requested tone."""

        cleaned_tone = (
            tone.strip().title()
            if tone
            else "Professional"
        )

        if cleaned_tone not in self.VALID_TONES:
            return "Professional"

        return cleaned_tone

    def _resolve_goal(
        self,
        primary_goal: str,
    ) -> str:
        """Validate and normalize the conversion goal."""

        cleaned_goal = (
            primary_goal.strip().title()
            if primary_goal
            else "Visit Sales Page"
        )

        for valid_goal in self.VALID_GOALS:
            if (
                valid_goal.casefold()
                == cleaned_goal.casefold()
            ):
                return valid_goal

        return "Visit Sales Page"

    @staticmethod
    def _resolve_campaign_name(
        *,
        product: DiscoveryProduct,
        campaign_name: str | None,
    ) -> str:
        """Resolve the campaign display name."""

        if (
            campaign_name
            and campaign_name.strip()
        ):
            return campaign_name.strip()

        return (
            f"{product.product_name} "
            "Google Ads Campaign"
        )

    def _build_headlines(
        self,
        *,
        product: DiscoveryProduct,
        keyword: str,
        tone: str,
    ) -> list[str]:
        """Build responsive-search-ad headlines."""

        product_name = (
            product.product_name.strip()
        )

        keyword_topic = self._extract_keyword_topic(
            keyword
        )

        headline_candidates = [
            product_name,
            f"{keyword} Online",
            f"Learn {keyword_topic}",
            f"Improve Your {keyword_topic}",
            f"Master {keyword_topic}",
            f"{keyword} for Beginners",
            f"Practical {keyword_topic}",
            f"Explore {product_name}",
            f"Review {product_name}",
            "Build Better Skills",
            "Start Learning Today",
            "Compare the Official Offer",
            "See Course Details",
            "Develop Practical Skills",
            f"Is {product_name} Worth It?",
        ]

        if tone == "Friendly":
            headline_candidates.extend(
                [
                    "Ready to Learn More?",
                    "Find the Right Course",
                ]
            )

        elif tone == "Persuasive":
            headline_candidates.extend(
                [
                    "Take Your Skills Further",
                    "Start Improving Today",
                ]
            )

        elif tone == "Educational":
            headline_candidates.extend(
                [
                    "Understand the Course",
                    "Learn Before You Decide",
                ]
            )

        return self._normalize_limited_items(
            headline_candidates,
            maximum_length=(
                self.MAX_HEADLINE_LENGTH
            ),
            maximum_items=15,
        )

    def _build_descriptions(
            self,
            *,
            product: DiscoveryProduct,
            analysis: ProductAnalysis,
            audience: str,
            tone: str,
    ) -> list[str]:
        """Build complete Google Ads descriptions within 90 characters."""

        product_name = product.product_name.strip()

        description_candidates = [
            (
                f"Explore {product_name}. Review the official offer "
                "before deciding."
            ),
            (
                "Compare the course details with your learning goals."
            ),
            (
                f"Review the strengths and risks of {product_name} "
                "before purchasing."
            ),
            (
                f"Commercial potential: "
                f"{analysis.commercial_potential.lower()}. "
                "Verify all claims."
            ),
        ]

        if tone == "Friendly":
            description_candidates[1] = (
                "Take a simple look at the course and see whether it suits you."
            )

        elif tone == "Persuasive":
            description_candidates[1] = (
                "Review the official offer and take the next step toward your goals."
            )

        elif tone == "Educational":
            description_candidates[1] = (
                "Compare the product, audience and price before making a decision."
            )

        return self._normalize_limited_items(
            description_candidates,
            maximum_length=self.MAX_DESCRIPTION_LENGTH,
            maximum_items=4,
        )

    @staticmethod
    def _build_keywords(
        *,
        product: DiscoveryProduct,
        keyword: str,
    ) -> list[str]:
        """Build campaign keyword suggestions."""

        product_name = (
            product.product_name.strip()
        )

        keyword_topic = (
            GoogleAdsService._extract_keyword_topic(
                keyword
            )
        )

        keyword_candidates = [
            keyword,
            product_name,
            f"{keyword} online",
            f"learn {keyword_topic}",
            f"best {keyword}",
            f"{keyword_topic} training",
            f"{keyword_topic} classes",
            f"{keyword} for beginners",
            f"advanced {keyword_topic}",
            f"{product_name} review",
            f"{product_name} price",
            f"{product_name} course",
            f"{product_name} official",
            f"is {product_name} worth it",
            f"buy {product_name}",
            f"{keyword_topic} certification",
            f"online {keyword_topic} training",
            f"practical {keyword_topic} course",
            f"professional {keyword_topic} course",
            f"{keyword_topic} skills course",
        ]

        return GoogleAdsService._deduplicate_items(
            keyword_candidates
        )

    @staticmethod
    def _build_negative_keywords() -> list[str]:
        """Build general negative-keyword suggestions."""

        return [
            "free",
            "torrent",
            "crack",
            "cracked",
            "pirated",
            "download free",
            "pdf free",
            "coupon free",
            "illegal download",
            "refund scam",
            "complaints",
            "jobs",
            "salary",
            "template",
            "software download",
            "youtube free",
            "reddit free",
            "wiki",
            "definition",
            "meaning",
        ]

    @staticmethod
    def _build_call_to_action(
        *,
        product: DiscoveryProduct,
        primary_goal: str,
    ) -> str:
        """Build the recommended Google Ads call to action."""

        if primary_goal == "Generate Leads":
            return "Get the Free Guide"

        if primary_goal == "Promote Product":
            return (
                f"Explore {product.product_name}"
            )

        return "View the Official Offer"

    @staticmethod
    def _normalize_limited_items(
        items: list[str],
        *,
        maximum_length: int,
        maximum_items: int,
    ) -> list[str]:
        """Clean, shorten and deduplicate limited advertising assets."""

        normalized_items: list[str] = []
        seen_items: set[str] = set()

        for item in items:
            cleaned_item = " ".join(
                str(item).split()
            ).strip()

            if not cleaned_item:
                continue

            cleaned_item = (
                GoogleAdsService._shorten_without_cutting_words(
                    cleaned_item,
                    maximum_length=maximum_length,
                )
            )

            normalized_key = (
                cleaned_item.casefold()
            )

            if (
                not cleaned_item
                or normalized_key in seen_items
            ):
                continue

            seen_items.add(
                normalized_key
            )

            normalized_items.append(
                cleaned_item
            )

            if (
                len(normalized_items)
                >= maximum_items
            ):
                break

        return normalized_items

    @staticmethod
    def _shorten_without_cutting_words(
        text: str,
        *,
        maximum_length: int,
    ) -> str:
        """Shorten advertising text without cutting through a word."""

        cleaned_text = " ".join(
            text.split()
        ).strip()

        if len(cleaned_text) <= maximum_length:
            return cleaned_text

        shortened_text = cleaned_text[
            :maximum_length + 1
        ]

        if " " in shortened_text:
            shortened_text = shortened_text.rsplit(
                " ",
                1,
            )[0]

        return shortened_text.rstrip(
            " ,.;:-"
        )

    @staticmethod
    def _extract_keyword_topic(
        keyword: str,
    ) -> str:
        """Remove repeated course-related wording from a keyword."""

        cleaned_keyword = " ".join(
            keyword.split()
        ).strip()

        lowered_keyword = (
            cleaned_keyword.casefold()
        )

        removable_endings = (
            " course",
            " training",
            " classes",
            " class",
        )

        for ending in removable_endings:
            if lowered_keyword.endswith(
                ending
            ):
                topic = cleaned_keyword[
                    :-len(ending)
                ].strip()

                if topic:
                    return topic

        return cleaned_keyword

    @staticmethod
    def _deduplicate_items(
        items: list[str],
    ) -> list[str]:
        """Remove empty and repeated keyword values."""

        normalized_items: list[str] = []
        seen_items: set[str] = set()

        for item in items:
            cleaned_item = " ".join(
                str(item).split()
            ).strip()

            normalized_key = (
                cleaned_item.casefold()
            )

            if (
                not cleaned_item
                or normalized_key in seen_items
            ):
                continue

            seen_items.add(
                normalized_key
            )

            normalized_items.append(
                cleaned_item
            )

        return normalized_items