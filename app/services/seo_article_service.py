
"""Generate evidence-aware SEO article drafts for YAffiliate."""

from __future__ import annotations

import re
from typing import Any

from app.models.discovery_product import DiscoveryProduct
from app.models.product_analysis import ProductAnalysis
from app.models.seo_article import SEOArticle, SEOSection
from app.services.base_content_generator import BaseContentGenerator


class SEOArticleService(BaseContentGenerator):
    """
    Generate structured SEO (Search Engine Optimization) articles.

    This is a deterministic template-based generator, not an LLM.
    LLM means Large Language Model.

    Missing numerical data is not treated as verified zero.
    Generated text must be reviewed before publication.
    """

    VALID_TONES = {
        "Professional",
        "Friendly",
        "Persuasive",
        "Educational",
    }

    VALID_LENGTHS = {
        "Short",
        "Medium",
        "Long",
    }

    def generate(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        target_keyword: str | None = None,
        keyword: str | None = None,
        tone: str = "Professional",
        length: str = "Medium",
        **kwargs: Any,
    ) -> SEOArticle:
        """Create an article using the existing SEOArticle model."""

        resolved_keyword = self._resolve_keyword(
            product=product,
            target_keyword=target_keyword,
            keyword=keyword,
        )
        resolved_tone = self._resolve_tone(tone)
        resolved_length = self._resolve_length(length)

        title = self._build_title(
            product=product,
            keyword=resolved_keyword,
        )
        meta_description = self._build_meta_description(
            product=product,
            keyword=resolved_keyword,
        )
        introduction = self._build_introduction(
            product=product,
            keyword=resolved_keyword,
            tone=resolved_tone,
        )
        sections = self._build_sections(
            product=product,
            analysis=analysis,
            keyword=resolved_keyword,
            tone=resolved_tone,
            length=resolved_length,
        )
        conclusion = self._build_conclusion(
            product=product,
            analysis=analysis,
            tone=resolved_tone,
        )
        call_to_action = self._build_call_to_action(
            product=product,
            tone=resolved_tone,
        )

        word_count = self._estimate_word_count(
            title=title,
            meta_description=meta_description,
            introduction=introduction,
            sections=sections,
            conclusion=conclusion,
            call_to_action=call_to_action,
        )

        seo_score = self._calculate_seo_score(
            product=product,
            keyword=resolved_keyword,
            title=title,
            meta_description=meta_description,
            sections=sections,
        )

        return SEOArticle(
            title=title,
            meta_description=meta_description,
            target_keyword=resolved_keyword,
            introduction=introduction,
            sections=sections,
            conclusion=conclusion,
            call_to_action=call_to_action,
            estimated_word_count=word_count,
            seo_score=seo_score,
        )

    @staticmethod
    def _resolve_keyword(
        *,
        product: DiscoveryProduct,
        target_keyword: str | None,
        keyword: str | None,
    ) -> str:
        for value in (
            target_keyword,
            keyword,
            product.product_name,
        ):
            if isinstance(value, str) and value.strip():
                return value.strip()

        raise ValueError("A target keyword is required.")

    @classmethod
    def _resolve_tone(cls, tone: str) -> str:
        value = str(tone or "Professional").strip().title()
        return value if value in cls.VALID_TONES else "Professional"

    @classmethod
    def _resolve_length(cls, length: str) -> str:
        value = str(length or "Medium").strip().title()
        return value if value in cls.VALID_LENGTHS else "Medium"

    @staticmethod
    def _has_verified_metric(value: Any) -> bool:
        """
        Zero is treated as unknown for imported market metrics.

        This is deliberately conservative: the current product model
        cannot distinguish a measured zero from a missing value
        stored using zero as its default.
        """
        if value is None or isinstance(value, bool):
            return False

        try:
            return float(value) > 0
        except (TypeError, ValueError, OverflowError):
            return False

    @staticmethod
    def _clean_sentence(text: str) -> str:
        text = " ".join(str(text).split()).strip()
        if not text:
            return ""
        return text[0].upper() + text[1:].rstrip(".") + "."

    @staticmethod
    def _join_items(items: list[str] | None) -> str:
        cleaned = [
            str(item).strip().rstrip(".")
            for item in (items or [])
            if str(item).strip()
        ]

        if not cleaned:
            return ""

        if len(cleaned) == 1:
            return cleaned[0]

        if len(cleaned) == 2:
            return f"{cleaned[0]} and {cleaned[1]}"

        return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"

    @staticmethod
    def _build_title(
        *,
        product: DiscoveryProduct,
        keyword: str,
    ) -> str:
        name = product.product_name.strip()

        if keyword.casefold() == name.casefold():
            return f"{name} Review: What Should Buyers Know?"

        return f"{name} Review: A Guide to {keyword}"

    @staticmethod
    def _build_meta_description(
        *,
        product: DiscoveryProduct,
        keyword: str,
    ) -> str:
        name = product.product_name.strip()

        if keyword.casefold() == name.casefold():
            return (
                f"Considering {name}? Explore the available product "
                "information, important questions, possible limitations "
                "and what to verify before buying."
            )

        return (
            f"Explore {name} in this {keyword} guide. "
            "Learn what to check, which questions to ask "
            "and how to evaluate the offer before buying."
        )

    def _build_introduction(
        self,
        *,
        product: DiscoveryProduct,
        keyword: str,
        tone: str,
    ) -> str:
        name = product.product_name.strip()
        description = str(product.description or "").strip()

        if description:
            opening = (
                f"If you are considering {name}, it helps to start "
                f"with the available product information. {description}"
            )
        else:
            opening = (
                f"Considering {name}? Before choosing this offer, "
                "it is worth checking exactly what is included, "
                "who it is intended for and whether its claims "
                "are supported by reliable information."
            )

        closing = (
            "This guide separates the details currently available "
            "from the questions that still need answers."
        )

        return self._apply_tone(
            text=f"{opening} {closing}",
            tone=tone,
        )

    def _build_sections(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        keyword: str,
        tone: str,
        length: str,
    ) -> list[SEOSection]:
        name = product.product_name.strip()

        description = str(product.description or "").strip()
        category = str(product.category or "").strip()

        if description:
            overview = description
        elif category:
            overview = (
                f"{name} is listed in the {category} category. "
                "A detailed product description has not yet "
                "been provided, so its specific features "
                "should be confirmed with the seller."
            )
        else:
            overview = (
                f"{name} is a product currently being researched. "
                "Its specific features, delivery format and "
                "seller claims have not yet been verified."
            )

        # Buyer-facing articles should not disclose affiliate
        # commissions or internal opportunity scores as benefits.
        price = getattr(product, "price", None)
        if self._has_verified_metric(price):
            overview += (
                f" The recorded price is R$ {float(price):,.2f}, "
                "but buyers should confirm the current amount "
                "and currency on the official sales page."
            )
        else:
            overview += (
                " The current selling price has not been verified."
            )

        audience = (
            "Readers should assess whether the offer fits "
            "their experience level, learning goals, budget "
            "and preferred way of learning."
        )

        if category and any(
            word in category.casefold()
            for word in ("education", "course", "training")
        ):
            audience += (
                " For training products, check prerequisites, "
                "course content, instructor credentials "
                "and the support provided."
            )

        buyer_checks = (
            "Start with the official product description. "
            "Check what is included, how the product is delivered, "
            "whether updates or support are provided, "
            "and whether the advertised outcomes are realistic."
        )

        market_parts = []

        if self._has_verified_metric(product.search_volume):
            market_parts.append(
                f"the stored search-volume estimate is "
                f"{int(product.search_volume):,} searches"
            )

        if self._has_verified_metric(product.google_trend_score):
            market_parts.append(
                f"the stored Google Trends indicator is "
                f"{float(product.google_trend_score):.0f}/100"
            )

        if market_parts:
            market_text = (
                "The research record contains the following "
                "indicators: "
                + self._join_items(market_parts)
                + ". Their sources, dates and measurement "
                "methods should be checked before drawing "
                "conclusions about demand."
            )
        else:
            market_text = (
                f"Reliable search-demand figures for {keyword} "
                "have not been provided. This does not mean "
                "there is no demand; it means the available "
                "record is insufficient to measure it."
            )

        market_text += (
            " Search trends alone cannot establish whether "
            "a product is suitable or good value."
        )

        strengths_text = (
            "Product-specific benefits have not yet been "
            "independently verified. Review the official "
            "description and seek reliable customer feedback "
            "before making claims about results."
        )

        if description:
            strengths_text = (
                "The supplied description offers a starting "
                "point for understanding the product, but "
                "its claims should be checked against "
                "independent evidence and customer feedback."
            )

        risks_text = (
            "Important details may still be missing, including "
            "verified customer reviews, current pricing, "
            "refund terms and evidence of advertised outcomes. "
            "Avoid assuming that missing information indicates "
            "either a positive or negative result."
        )

        decision_text = (
            f"Before purchasing {name}, compare it with "
            "relevant alternatives. Consider total cost, "
            "the content or features offered, support, "
            "refund conditions and how well the product "
            "matches your personal goals."
        )

        sections = [
            SEOSection(
                heading=f"What Is {name}?",
                content=overview,
            ),
            SEOSection(
                heading=f"Who Might {name} Suit?",
                content=audience,
            ),
            SEOSection(
                heading="What Should You Check First?",
                content=buyer_checks,
            ),
            SEOSection(
                heading=f"Search Interest in {keyword}",
                content=market_text,
            ),
            SEOSection(
                heading="Potential Benefits and Evidence",
                content=strengths_text,
            ),
            SEOSection(
                heading="Limitations and Unanswered Questions",
                content=risks_text,
            ),
            SEOSection(
                heading=f"Is {name} Worth Considering?",
                content=decision_text,
            ),
        ]

        return [
            SEOSection(
                heading=section.heading,
                content=self._apply_tone(
                    text=self._apply_length(
                        text=section.content,
                        length=length,
                    ),
                    tone=tone,
                ),
            )
            for section in sections
        ]

    def _build_conclusion(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        tone: str,
    ) -> str:
        name = product.product_name.strip()

        conclusion = (
            f"{name} may be worth investigating, but the "
            "information currently available is not enough "
            "to make a confident purchasing recommendation. "
            "Check the official offer, confirm the price "
            "and terms, and compare alternatives before deciding."
        )

        return self._apply_tone(
            text=conclusion,
            tone=tone,
        )

    def _build_call_to_action(
        self,
        *,
        product: DiscoveryProduct,
        tone: str,
    ) -> str:
        name = product.product_name.strip()

        if product.sales_page_url:
            text = (
                f"Review the official {name} sales page, "
                "verify the details and decide whether "
                "the offer meets your needs."
            )
        else:
            text = (
                f"Find verified information about {name} "
                "and compare your options before purchasing."
            )

        return self._apply_tone(text=text, tone=tone)

    @staticmethod
    def _apply_tone(
        *,
        text: str,
        tone: str,
    ) -> str:
        """Make a restrained style adjustment without adding claims."""
        if tone == "Friendly":
            return text.replace(
                "Before purchasing",
                "Before you buy",
            )

        if tone == "Educational":
            return text.replace(
                "Check what is included",
                "To evaluate the offer, check what is included",
            )

        if tone == "Persuasive":
            return text.replace(
                "compare your options",
                "take the next step by comparing your options",
            )

        return text

    @staticmethod
    def _apply_length(
        *,
        text: str,
        length: str,
    ) -> str:
        """Adjust length without inventing extra product facts."""
        if length == "Short":
            sentences = re.split(r"(?<=[.!?])\s+", text.strip())
            return sentences[0] if sentences else text

        if length == "Long":
            return (
                f"{text} Where information is incomplete, "
                "ask the seller for clarification and "
                "look for independent evidence rather "
                "than relying on assumptions."
            )

        return text

    @staticmethod
    def _estimate_word_count(
        *,
        title: str,
        meta_description: str,
        introduction: str,
        sections: list[SEOSection],
        conclusion: str,
        call_to_action: str,
    ) -> int:
        parts = [
            title,
            meta_description,
            introduction,
            conclusion,
            call_to_action,
        ]

        for section in sections:
            parts.extend([section.heading, section.content])

        return len(" ".join(parts).split())

    @staticmethod
    def _calculate_seo_score(
        *,
        product: DiscoveryProduct,
        keyword: str,
        title: str,
        meta_description: str,
        sections: list[SEOSection],
    ) -> float:
        """
        Calculate a basic structural SEO score.

        This is an internal checklist score, not a prediction
        of Google rankings, traffic or commercial success.
        """
        score = 0.0

        if keyword.casefold() in title.casefold():
            score += 20

        if keyword.casefold() in meta_description.casefold():
            score += 15

        if 45 <= len(title) <= 65:
            score += 15

        if 120 <= len(meta_description) <= 165:
            score += 15

        if len(sections) >= 6:
            score += 15

        if any(
            keyword.casefold() in section.heading.casefold()
            for section in sections
        ):
            score += 10

        if all(section.content.strip() for section in sections):
            score += 10

        return round(min(score, 100.0), 1)
