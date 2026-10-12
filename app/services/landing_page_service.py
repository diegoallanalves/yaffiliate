
"""Generate evidence-aware affiliate landing pages for YAffiliate."""

from __future__ import annotations

from typing import Any

from app.models.discovery_product import DiscoveryProduct
from app.models.landing_page import LandingPage, LandingPageSection
from app.models.product_analysis import ProductAnalysis
from app.services.base_content_generator import BaseContentGenerator


class LandingPageService(BaseContentGenerator):
    """
    Build structured, buyer-focused landing-page copy.

    CTA means Call to Action: a prompt encouraging a visitor
    to take a next step.

    FAQ means Frequently Asked Questions.

    This generator uses deterministic templates. It does not
    verify product claims or publish a working website.
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

    def generate(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        target_audience: str | None = None,
        primary_goal: str = "Visit Sales Page",
        tone: str = "Persuasive",
        **kwargs: Any,
    ) -> LandingPage:
        """Return a landing-page draft in the existing data model."""

        audience = self._resolve_audience(
            analysis=analysis,
            target_audience=target_audience,
        )
        goal = self._resolve_goal(primary_goal)
        resolved_tone = self._resolve_tone(tone)

        name = self._clean(product.product_name, "This product")
        description = self._clean(product.description)
        category = self._clean(product.category)

        page_title = f"{name} | Product Information and Buyer Guide"

        meta_description = (
            f"Explore {name}, review available information, "
            "check important product details and decide "
            "whether the offer fits your needs."
        )

        hero_headline = self._hero_headline(
            name=name,
            tone=resolved_tone,
        )

        hero_subheadline = self._hero_subheadline(
            name=name,
            description=description,
            audience=audience,
        )

        primary_cta = self._primary_cta(goal)

        sections = self._build_sections(
            name=name,
            description=description,
            category=category,
            audience=audience,
            product=product,
            goal=goal,
            tone=resolved_tone,
        )

        final_cta_heading = f"Ready to learn more about {name}?"

        if goal == "Generate Leads":
            final_cta_text = (
                "Review the available product information. "
                "A verified lead form and any promised resource "
                "must be configured before this page goes live."
            )
        elif self._valid_url(product.sales_page_url):
            final_cta_text = (
                "Visit the official product page to confirm "
                "current features, pricing, terms and availability."
            )
        else:
            final_cta_text = (
                "Confirm the official product page and seller "
                "details before making a purchasing decision."
            )

        final_cta_button = primary_cta

        estimated_word_count = self._estimate_word_count(
            page_title=page_title,
            meta_description=meta_description,
            hero_headline=hero_headline,
            hero_subheadline=hero_subheadline,
            primary_cta=primary_cta,
            sections=sections,
            final_cta_heading=final_cta_heading,
            final_cta_text=final_cta_text,
            final_cta_button=final_cta_button,
        )

        conversion_score = self._calculate_conversion_score(
            product=product,
            analysis=analysis,
            audience=audience,
            sections=sections,
            primary_cta=primary_cta,
        )

        return LandingPage(
            page_title=page_title,
            meta_description=meta_description,
            product_name=product.product_name,
            target_audience=audience,
            primary_goal=goal,
            tone=resolved_tone,
            hero_headline=hero_headline,
            hero_subheadline=hero_subheadline,
            primary_cta=primary_cta,
            sections=sections,
            final_cta_heading=final_cta_heading,
            final_cta_text=final_cta_text,
            final_cta_button=final_cta_button,
            estimated_word_count=estimated_word_count,
            conversion_score=conversion_score,
        )

    @staticmethod
    def _clean(value: Any, fallback: str = "") -> str:
        if value is None:
            return fallback

        result = " ".join(str(value).split())
        return result or fallback

    @staticmethod
    def _valid_url(value: Any) -> bool:
        """Basic URL check, not verification of a live destination."""
        if not isinstance(value, str):
            return False

        url = value.strip().lower()

        return (
            url.startswith(("https://", "http://"))
            and "." in url.split("/")[2]
            and " " not in url
        )

    @classmethod
    def _resolve_audience(
        cls,
        *,
        analysis: ProductAnalysis,
        target_audience: str | None,
    ) -> str:
        if isinstance(target_audience, str):
            if target_audience.strip():
                return target_audience.strip()

        candidates = getattr(analysis, "target_audience", None) or []

        cleaned = [
            cls._clean(item)
            for item in candidates
            if cls._clean(item)
        ]

        if cleaned:
            return ", ".join(cleaned)

        return "people considering this type of product"

    @classmethod
    def _resolve_goal(cls, primary_goal: str) -> str:
        supplied = str(primary_goal or "").strip()

        for goal in cls.VALID_GOALS:
            if supplied.casefold() == goal.casefold():
                return goal

        return "Visit Sales Page"

    @classmethod
    def _resolve_tone(cls, tone: str) -> str:
        supplied = str(tone or "").strip()

        for valid_tone in cls.VALID_TONES:
            if supplied.casefold() == valid_tone.casefold():
                return valid_tone

        return "Professional"

    @staticmethod
    def _hero_headline(*, name: str, tone: str) -> str:
        if tone == "Friendly":
            return f"Curious about {name}? Start here."

        if tone == "Educational":
            return f"Understanding {name}: A Practical Buyer Guide"

        if tone == "Persuasive":
            return f"Explore {name} Before You Decide"

        return f"{name}: Product Overview and Key Considerations"

    @staticmethod
    def _hero_subheadline(
        *,
        name: str,
        description: str,
        audience: str,
    ) -> str:
        if description:
            return (
                f"Explore the available details about {name}, "
                "check the seller's claims and decide whether "
                "this offer is right for you."
            )

        return (
            f"Researching {name}? Review the information "
            "currently available, identify what still needs "
            "verification and compare your options."
        )

    @staticmethod
    def _primary_cta(goal: str) -> str:
        if goal == "Generate Leads":
            return "Request More Information"

        if goal == "Promote Product":
            return "Explore Product Details"

        return "View the Official Offer"

    def _build_sections(
        self,
        *,
        name: str,
        description: str,
        category: str,
        audience: str,
        product: DiscoveryProduct,
        goal: str,
        tone: str,
    ) -> list[LandingPageSection]:
        """Build sections without inventing benefits or testimonials."""

        if description:
            overview = description
        elif category:
            overview = (
                f"{name} is listed in the {category} category. "
                "The available record does not yet provide "
                "enough information to confirm its specific "
                "features or outcomes."
            )
        else:
            overview = (
                f"{name} is currently being researched. "
                "Its features, delivery method and advertised "
                "results still need to be verified."
            )

        benefits = [
            "Review the seller's description of the product",
            "Confirm which features or services are included",
            "Compare the offer with relevant alternatives",
            "Check whether the product matches your goals",
        ]

        audience_content = (
            f"This page is intended for {audience}. "
            "The product's actual suitability for this audience "
            "has not been independently established. "
            "Check any prerequisites, limitations and "
            "eligibility requirements with the seller."
        )

        price = getattr(product, "price", None)

        if self._positive_number(price):
            value_content = (
                f"The recorded product price is "
                f"R$ {float(price):,.2f}. "
                "This amount may change. Confirm the currency, "
                "final checkout price, taxes and any recurring "
                "charges on the official product page."
            )
        else:
            value_content = (
                "The current product price has not been verified. "
                "Check the official offer for pricing, payment "
                "terms, recurring charges and any additional fees."
            )

        trust_items = [
            "Check the identity and contact details of the seller",
            "Look for independent customer feedback",
            "Confirm the refund and cancellation policies",
            "Verify any performance or outcome claims",
        ]

        risks_content = (
            "Important details may be incomplete or unverified. "
            "Do not assume that missing complaints, refund data "
            "or negative reviews mean a product has no risks. "
            "Review the seller's terms and seek independent "
            "information before purchasing."
        )

        next_steps = [
            "Read the complete official product description",
            "Confirm the current price and what is included",
            "Review refund, cancellation and support terms",
            "Compare the offer with other suitable options",
        ]

        faq_items = [
            (
                f"What is {name}? — "
                + (
                    description
                    if description
                    else "Its detailed features have not yet "
                    "been verified. Consult the official seller."
                )
            ),
            (
                f"Who should consider {name}? — "
                "People whose needs match the verified product "
                "features and any stated prerequisites."
            ),
            (
                "Is the price confirmed? — "
                "Check the official checkout page for the "
                "current price, currency and payment terms."
            ),
            (
                "What if I am not satisfied? — "
                "Review the seller's current refund and "
                "cancellation policies before purchasing."
            ),
        ]

        disclosure = (
            "Affiliate disclosure: This page may contain "
            "affiliate links. If you purchase through one "
            "of those links, the publisher may earn a "
            "commission, at no additional cost to you. "
            "This disclosure must be reviewed and adjusted "
            "to reflect the actual commercial relationship."
        )

        sections = [
            LandingPageSection(
                section_type="benefits",
                heading="What Should You Look For?",
                content=(
                    "Before deciding, focus on the features "
                    "and conditions that matter to you. "
                    "The following are evaluation steps, "
                    "not verified product benefits."
                ),
                items=benefits,
            ),
            LandingPageSection(
                section_type="audience",
                heading="Who Might This Product Suit?",
                content=audience_content,
            ),
            LandingPageSection(
                section_type="value",
                heading="Pricing and Value",
                content=value_content,
            ),
            LandingPageSection(
                section_type="trust",
                heading="How to Verify the Offer",
                content=(
                    "Use independent evidence and official "
                    "seller information to evaluate the offer."
                ),
                items=trust_items,
            ),
            LandingPageSection(
                section_type="risks",
                heading="Important Considerations",
                content=risks_content,
            ),
            LandingPageSection(
                section_type="recommendations",
                heading="Your Next Steps",
                content=(
                    "Use this checklist before making "
                    "a purchasing decision."
                ),
                items=next_steps,
            ),
            LandingPageSection(
                section_type="faq",
                heading="Frequently Asked Questions",
                content=(
                    "Answers are based on available information. "
                    "Confirm product-specific details with "
                    "the official seller."
                ),
                items=faq_items,
            ),
            LandingPageSection(
                section_type="disclosure",
                heading="Affiliate Disclosure",
                content=disclosure,
            ),
        ]

        return sections

    @staticmethod
    def _positive_number(value: Any) -> bool:
        if value is None or isinstance(value, bool):
            return False

        try:
            return float(value) > 0
        except (TypeError, ValueError, OverflowError):
            return False

    @staticmethod
    def _estimate_word_count(
        *,
        page_title: str,
        meta_description: str,
        hero_headline: str,
        hero_subheadline: str,
        primary_cta: str,
        sections: list[LandingPageSection],
        final_cta_heading: str,
        final_cta_text: str,
        final_cta_button: str,
    ) -> int:
        parts = [
            page_title,
            meta_description,
            hero_headline,
            hero_subheadline,
            primary_cta,
            final_cta_heading,
            final_cta_text,
            final_cta_button,
        ]

        for section in sections:
            parts.append(section.heading)
            parts.append(section.content)
            parts.extend(section.items or [])

        return len(" ".join(parts).split())

    @classmethod
    def _calculate_conversion_score(
        cls,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        audience: str,
        sections: list[LandingPageSection],
        primary_cta: str,
    ) -> float:
        """
        Score draft completeness only.

        This is not a predicted conversion rate or
        a measure of expected sales performance.
        """
        score = 0.0

        if audience.strip():
            score += 15

        if primary_cta.strip():
            score += 15

        if len(sections) >= 7:
            score += 20

        if cls._clean(product.description):
            score += 15

        if cls._valid_url(product.sales_page_url):
            score += 15

        if cls._valid_url(product.affiliate_url):
            score += 10

        if cls._positive_number(product.price):
            score += 10

        return round(min(score, 100.0), 1)
