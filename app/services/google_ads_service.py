
"""Generate evidence-aware Google Ads assets for YAffiliate."""

from __future__ import annotations

from typing import Any

from app.models.discovery_product import DiscoveryProduct
from app.models.google_ads_campaign import GoogleAdsAsset
from app.models.product_analysis import ProductAnalysis
from app.services.base_content_generator import BaseContentGenerator


class GoogleAdsService(BaseContentGenerator):
    """
    Generate draft responsive search ads.

    RSA = Responsive Search Ad.
    CTA = Call to Action.

    Assets are suggestions, not approved or published Google Ads.
    """

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
    MAX_HEADLINES = 15
    MAX_DESCRIPTIONS = 4

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
        """Return a structured Google Ads draft."""

        self._validate_inputs(product=product, analysis=analysis)

        product_name = self._clean(product.product_name)
        if not product_name:
            raise ValueError("A product name is required.")

        resolved_keyword = self._resolve_keyword(
            product=product,
            target_keyword=target_keyword,
            keyword=keyword,
        )

        audience = self._resolve_audience(
            analysis=analysis,
            target_audience=target_audience,
        )

        resolved_tone = self._resolve_tone(tone)
        resolved_goal = self._resolve_goal(primary_goal)

        name = (
            self._clean(campaign_name)
            or f"{product_name} Google Ads Campaign"
        )

        headlines = self._build_headlines(
            product=product,
            keyword=resolved_keyword,
            tone=resolved_tone,
        )

        descriptions = self._build_descriptions(
            product=product,
            analysis=analysis,
            audience=audience,
            tone=resolved_tone,
        )

        keywords = self._build_keywords(
            product=product,
            keyword=resolved_keyword,
        )

        negative_keywords = self._build_negative_keywords()

        cta = self._build_call_to_action(
            product=product,
            primary_goal=resolved_goal,
        )

        return GoogleAdsAsset(
            campaign_name=name,
            headlines=tuple(headlines),
            descriptions=tuple(descriptions),
            keywords=tuple(keywords),
            negative_keywords=tuple(negative_keywords),
            call_to_action=cta,
            target_audience=audience,
        )

    @staticmethod
    def _validate_inputs(
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
    ) -> None:
        if not isinstance(product, DiscoveryProduct):
            raise TypeError(
                "product must be a DiscoveryProduct instance."
            )

        if not isinstance(analysis, ProductAnalysis):
            raise TypeError(
                "analysis must be a ProductAnalysis instance."
            )

    @staticmethod
    def _clean(value: Any) -> str:
        if value is None:
            return ""
        return " ".join(str(value).split())

    @classmethod
    def _resolve_keyword(
        cls,
        *,
        product: DiscoveryProduct,
        target_keyword: str | None,
        keyword: str | None,
    ) -> str:
        for candidate in (
            target_keyword,
            keyword,
            product.product_name,
        ):
            cleaned = cls._clean(candidate)
            if cleaned:
                return cleaned

        raise ValueError("A Google Ads target keyword is required.")

    @classmethod
    def _resolve_audience(
        cls,
        *,
        analysis: ProductAnalysis,
        target_audience: str | None,
    ) -> str:
        supplied = cls._clean(target_audience)
        if supplied:
            return supplied

        items = getattr(analysis, "target_audience", None) or []
        cleaned = [
            cls._clean(item)
            for item in items
            if cls._clean(item)
        ]

        return (
            ", ".join(cleaned)
            if cleaned
            else "people researching this product"
        )

    @classmethod
    def _resolve_tone(cls, tone: str) -> str:
        supplied = cls._clean(tone)

        for valid in cls.VALID_TONES:
            if supplied.casefold() == valid.casefold():
                return valid

        return "Professional"

    @classmethod
    def _resolve_goal(cls, goal: str) -> str:
        supplied = cls._clean(goal)

        for valid in cls.VALID_GOALS:
            if supplied.casefold() == valid.casefold():
                return valid

        return "Visit Sales Page"

    @classmethod
    def _build_headlines(
        cls,
        *,
        product: DiscoveryProduct,
        keyword: str,
        tone: str,
    ) -> list[str]:
        name = cls._clean(product.product_name)
        topic = cls._clean(keyword)

        # Use only claims that can be made without knowing
        # unverified product features or outcomes.
        candidates = [
            name,
            f"Explore {name}",
            f"Discover {name}",
            f"{name} Details",
            f"{name} Information",
            f"{name} Overview",
            f"{name} Review Guide",
            f"Considering {name}?",
            f"Compare {name}",
            f"About {name}",
            f"Explore {topic}",
            f"{topic} Options",
            f"{topic} Information",
            "Review Before You Buy",
            "Explore Product Details",
            "Compare Your Options",
            "Check the Product Details",
            "Make an Informed Choice",
            "Understand the Offer",
            "Explore the Available Info",
            "See What to Consider",
        ]

        if tone == "Friendly":
            candidates.extend([
                "Curious? Learn More",
                "Take a Closer Look",
            ])
        elif tone == "Persuasive":
            candidates.extend([
                "Find Out More Today",
                "Explore Your Options",
            ])
        elif tone == "Educational":
            candidates.extend([
                "Learn Before You Decide",
                "Understand Your Options",
            ])

        return cls._normalize_limited_items(
            candidates,
            maximum_length=cls.MAX_HEADLINE_LENGTH,
            maximum_items=cls.MAX_HEADLINES,
        )

    @classmethod
    def _build_descriptions(
        cls,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        audience: str,
        tone: str,
    ) -> list[str]:
        name = cls._clean(product.product_name)

        candidates = [
            f"Explore {name}. Review the available product details before deciding.",
            "Compare features, pricing and terms to see whether the offer fits your needs.",
            "Check the seller's information, conditions and relevant alternatives.",
            "Take a closer look at the offer and make an informed purchasing decision.",
            "Review product information and consider the questions that matter to you.",
            "Explore the available details before choosing your next step.",
        ]

        if tone == "Friendly":
            candidates.insert(
                1,
                "Curious about the offer? Explore the details and compare your options.",
            )
        elif tone == "Persuasive":
            candidates.insert(
                1,
                "Explore the offer today and decide whether it fits your needs.",
            )
        elif tone == "Educational":
            candidates.insert(
                1,
                "Understand the offer, check the terms and compare relevant alternatives.",
            )

        return cls._normalize_limited_items(
            candidates,
            maximum_length=cls.MAX_DESCRIPTION_LENGTH,
            maximum_items=cls.MAX_DESCRIPTIONS,
        )

    @classmethod
    def _build_keywords(
        cls,
        *,
        product: DiscoveryProduct,
        keyword: str,
    ) -> list[str]:
        name = cls._clean(product.product_name)
        topic = cls._clean(keyword)

        # These are ideas, not validated search-volume data.
        candidates = [
            name,
            topic,
            f"{name} review",
            f"{name} reviews",
            f"{name} price",
            f"{name} pricing",
            f"{name} details",
            f"{name} information",
            f"{name} official website",
            f"{name} alternatives",
            f"{name} comparison",
            f"is {name} worth it",
            f"buy {name}",
            f"{topic} options",
            f"{topic} products",
            f"{topic} comparison",
        ]

        return cls._deduplicate_items(candidates)

    @staticmethod
    def _build_negative_keywords() -> list[str]:
        """
        Conservative negative-keyword suggestions.

        Review every exclusion before uploading to Google Ads.
        Do not automatically exclude review or complaint searches.
        """
        return [
            "torrent",
            "cracked",
            "pirated",
            "illegal download",
        ]

    @classmethod
    def _build_call_to_action(
        cls,
        *,
        product: DiscoveryProduct,
        primary_goal: str,
    ) -> str:
        if primary_goal == "Generate Leads":
            return "Request More Information"

        if primary_goal == "Promote Product":
            return "Explore Product Details"

        return "View Product Details"

    @classmethod
    def _normalize_limited_items(
        cls,
        items: list[str],
        *,
        maximum_length: int,
        maximum_items: int,
    ) -> list[str]:
        """
        Keep complete phrases within the character limit.

        Do not cut sentences in the middle of a word.
        Oversized candidates are skipped instead.
        """
        result = []
        seen = set()

        for item in items:
            cleaned = cls._clean(item)

            if not cleaned or len(cleaned) > maximum_length:
                continue

            key = cleaned.casefold()
            if key in seen:
                continue

            seen.add(key)
            result.append(cleaned)

            if len(result) >= maximum_items:
                break

        return result

    @classmethod
    def _deduplicate_items(cls, items: list[str]) -> list[str]:
        result = []
        seen = set()

        for item in items:
            cleaned = cls._clean(item)
            key = cleaned.casefold()

            if not cleaned or key in seen:
                continue

            seen.add(key)
            result.append(cleaned)

        return result
