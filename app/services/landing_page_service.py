from __future__ import annotations

from typing import Any

from app.models.discovery_product import DiscoveryProduct
from app.models.landing_page import (
    LandingPage,
    LandingPageSection,
)
from app.models.product_analysis import ProductAnalysis
from app.services.base_content_generator import (
    BaseContentGenerator,
)


class LandingPageService(BaseContentGenerator):
    """
    Generate structured landing-page copy from product intelligence.

    CTA = Call to Action.

    A Call to Action is the text or button that encourages
    the visitor to take the next step, such as:
    - Buy now
    - Learn more
    - Start today
    - View the official offer

    FAQ = Frequently Asked Questions.

    FAQ sections answer common visitor concerns and can improve
    trust before the visitor clicks the CTA.
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
        """
        Generate one complete landing page.

        target_audience:
        The group of people the page is designed to persuade.

        primary_goal:
        The main action the page should encourage.

        tone:
        The intended writing style.

        kwargs:
        Extra keyword arguments accepted through the shared
        BaseContentGenerator contract.
        """
        resolved_audience = self._resolve_audience(
            analysis=analysis,
            target_audience=target_audience,
        )

        resolved_goal = self._resolve_goal(
            primary_goal
        )

        resolved_tone = self._resolve_tone(
            tone
        )

        page_title = self._build_page_title(
            product=product,
        )

        meta_description = self._build_meta_description(
            product=product,
            audience=resolved_audience,
        )

        hero_headline = self._build_hero_headline(
            product=product,
            tone=resolved_tone,
        )

        hero_subheadline = self._build_hero_subheadline(
            product=product,
            audience=resolved_audience,
            analysis=analysis,
        )

        primary_cta = self._build_primary_cta(
            goal=resolved_goal,
        )

        sections = self._build_sections(
            product=product,
            analysis=analysis,
            audience=resolved_audience,
            tone=resolved_tone,
        )

        final_cta_heading = (
            f"Ready to explore {product.product_name}?"
        )

        final_cta_text = (
            "Review the official offer, verify the product claims "
            "and decide whether it matches your needs."
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
            audience=resolved_audience,
            sections=sections,
            primary_cta=primary_cta,
        )

        return LandingPage(
            page_title=page_title,
            meta_description=meta_description,
            product_name=product.product_name,
            target_audience=resolved_audience,
            primary_goal=resolved_goal,
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
    def _resolve_audience(
        *,
        analysis: ProductAnalysis,
        target_audience: str | None,
    ) -> str:
        if target_audience and target_audience.strip():
            return target_audience.strip()

        cleaned_audience = [
            item.strip()
            for item in analysis.target_audience
            if item.strip()
        ]

        if cleaned_audience:
            return ", ".join(
                cleaned_audience
            )

        return "people interested in this product"

    def _resolve_goal(
        self,
        primary_goal: str,
    ) -> str:
        cleaned_goal = (
            primary_goal.strip().title()
            if primary_goal
            else "Visit Sales Page"
        )

        for valid_goal in self.VALID_GOALS:
            if valid_goal.casefold() == cleaned_goal.casefold():
                return valid_goal

        return "Visit Sales Page"

    def _resolve_tone(
        self,
        tone: str,
    ) -> str:
        cleaned_tone = (
            tone.strip().title()
            if tone
            else "Persuasive"
        )

        if cleaned_tone not in self.VALID_TONES:
            return "Persuasive"

        return cleaned_tone

    @staticmethod
    def _build_page_title(
        *,
        product: DiscoveryProduct,
    ) -> str:
        return (
            f"{product.product_name}: "
            "Benefits, Audience and Official Offer"
        )

    @staticmethod
    def _build_meta_description(
        *,
        product: DiscoveryProduct,
        audience: str,
    ) -> str:
        return (
            f"Discover whether {product.product_name} is suitable "
            f"for {audience}. Review its benefits, risks and official "
            "offer before making a decision."
        )

    def _build_hero_headline(
        self,
        *,
        product: DiscoveryProduct,
        tone: str,
    ) -> str:
        base_headline = (
            f"Build stronger skills with "
            f"{product.product_name}"
        )

        if tone == "Friendly":
            return (
                f"Ready to learn with "
                f"{product.product_name}?"
            )

        if tone == "Professional":
            return (
                f"Advance your capabilities with "
                f"{product.product_name}"
            )

        if tone == "Educational":
            return (
                f"Discover what "
                f"{product.product_name} can teach you"
            )

        return base_headline

    @staticmethod
    def _build_hero_subheadline(
        *,
        product: DiscoveryProduct,
        audience: str,
        analysis: ProductAnalysis,
    ) -> str:
        return (
            f"Designed for {audience}, "
            f"{product.product_name} combines structured learning "
            f"with {analysis.commercial_potential.lower()} commercial "
            "potential and a focused path toward practical results."
        )

    @staticmethod
    def _build_primary_cta(
        *,
        goal: str,
    ) -> str:
        if goal == "Generate Leads":
            return "Get the Free Guide"

        if goal == "Promote Product":
            return "Explore the Product"

        return "View the Official Offer"

    def _build_sections(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        audience: str,
        tone: str,
    ) -> list[LandingPageSection]:
        strengths = [
            item.rstrip(".")
            for item in analysis.strengths
            if item.strip()
        ]

        weaknesses = [
            item.rstrip(".")
            for item in analysis.weaknesses
            if item.strip()
        ]

        recommendations = [
            item.rstrip(".")
            for item in analysis.recommendations
            if item.strip()
        ]

        benefits = strengths[:4]

        if not benefits:
            benefits = [
                "Structured product positioning",
                "Clear target audience",
                "Practical affiliate opportunity",
            ]

        faq_items = [
            (
                f"Who is {product.product_name} for? — "
                f"It is designed for {audience}."
            ),
            (
                f"What is the opportunity score? — "
                f"The current score is "
                f"{product.opportunity_score:.1f}/100."
            ),
            (
                f"How strong is market demand? — "
                f"The current search volume is approximately "
                f"{product.search_volume:,} searches per month."
            ),
            (
                f"What should users consider before purchasing? — "
                "They should review the official sales page, product "
                "claims, refund terms and suitability for their goals."
            ),
        ]

        trust_items = [
            (
                f"Refund rate monitored at "
                f"{product.refund_rate:.1f}%"
            ),
            (
                f"Google Trend score of "
                f"{product.google_trend_score:.0f}/100"
            ),
            (
                f"Competition score of "
                f"{product.competition_score:.0f}/100"
            ),
            (
                f"Analysis confidence of "
                f"{analysis.confidence_score:.1f}%"
            ),
        ]

        sections = [
            LandingPageSection(
                section_type="benefits",
                heading="Why consider this product?",
                content=(
                    "The available product and market data suggest "
                    "several reasons this offer may deserve attention."
                ),
                items=benefits,
            ),
            LandingPageSection(
                section_type="audience",
                heading="Who is this for?",
                content=(
                    f"{product.product_name} is most relevant to "
                    f"{audience}. Visitors should compare the product "
                    "content and outcomes with their own goals."
                ),
            ),
            LandingPageSection(
                section_type="value",
                heading="What makes the offer valuable?",
                content=(
                    f"The product has "
                    f"{analysis.commercial_potential.lower()} commercial "
                    f"potential, an opportunity score of "
                    f"{product.opportunity_score:.1f}/100 and a "
                    f"commission value of "
                    f"R$ {product.commission_amount:,.2f}."
                ),
            ),
            LandingPageSection(
                section_type="trust",
                heading="Trust and market signals",
                content=(
                    "These indicators help visitors understand the "
                    "commercial and market context before deciding."
                ),
                items=trust_items,
            ),
            LandingPageSection(
                section_type="risks",
                heading="What should you consider?",
                content=(
                    self._join_items(
                        weaknesses
                    )
                ),
            ),
            LandingPageSection(
                section_type="recommendations",
                heading="Recommended next steps",
                content=(
                    "Use a controlled strategy and validate performance "
                    "before making a larger commitment."
                ),
                items=recommendations[:4],
            ),
            LandingPageSection(
                section_type="faq",
                heading="Frequently Asked Questions",
                content=(
                    "Common questions visitors may ask before clicking "
                    "through to the official offer."
                ),
                items=faq_items,
            ),
        ]

        return [
            LandingPageSection(
                section_type=section.section_type,
                heading=section.heading,
                content=self._apply_tone(
                    text=section.content,
                    tone=tone,
                ),
                items=section.items,
            )
            for section in sections
        ]

    @staticmethod
    def _apply_tone(
        *,
        text: str,
        tone: str,
    ) -> str:
        if tone == "Friendly":
            return (
                "Here is the simple version: "
                f"{text}"
            )

        if tone == "Educational":
            return (
                "To understand this clearly, "
                f"{text}"
            )

        if tone == "Persuasive":
            return (
                f"{text} These signals support taking a closer look."
            )

        return text

    @staticmethod
    def _join_items(
        items: list[str],
    ) -> str:
        if not items:
            return (
                "No major weakness was detected from the "
                "currently available data."
            )

        if len(items) == 1:
            return items[0] + "."

        if len(items) == 2:
            return (
                f"{items[0]} and {items[1]}."
            )

        return (
            ", ".join(
                items[:-1]
            )
            + f", and {items[-1]}."
        )

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
        text_parts = [
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
            text_parts.extend(
                [
                    section.heading,
                    section.content,
                    *section.items,
                ]
            )

        return len(
            " ".join(
                text_parts
            ).split()
        )

    @staticmethod
    def _calculate_conversion_score(
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        audience: str,
        sections: list[LandingPageSection],
        primary_cta: str,
    ) -> float:
        score = 0.0

        if audience.strip():
            score += 15

        if primary_cta.strip():
            score += 15

        if len(sections) >= 6:
            score += 20

        if analysis.landing_page_potential == "Excellent":
            score += 20

        elif analysis.landing_page_potential == "Strong":
            score += 15

        if product.opportunity_score >= 60:
            score += 15

        if product.refund_rate <= 5:
            score += 10

        if product.google_trend_score >= 70:
            score += 5

        return round(
            min(score, 100),
            1,
        )