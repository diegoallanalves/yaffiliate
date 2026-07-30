from __future__ import annotations

from typing import Any

from app.models.discovery_product import DiscoveryProduct
from app.models.product_analysis import ProductAnalysis
from app.models.seo_article import (
    SEOArticle,
    SEOSection,
)
from app.services.base_content_generator import (
    BaseContentGenerator,
)


class SEOArticleService(BaseContentGenerator):
    """
    Generate a structured SEO article using product intelligence.

    SEO = Search Engine Optimization.

    Search Engine Optimization is the process of improving
    content so it can be discovered more easily through
    search engines such as Google and Bing.

    This first version uses deterministic business rules.

    Deterministic:
    The same inputs produce predictable outputs.

    A future GPT integration can improve and expand the
    language without changing the SEOArticle model or the
    rest of the application.

    GPT = Generative Pre-trained Transformer.
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
        """
        Generate one structured SEO article.

        target_keyword:
        Maintains compatibility with older code and tests.

        keyword:
        The field sent by the dynamic Content Studio template.

        tone:
        Controls the intended writing style.

        length:
        Controls the intended article size.

        kwargs:
        Additional keyword arguments that may be introduced
        by future templates without breaking this service.
        """
        resolved_keyword = self._resolve_keyword(
            product=product,
            target_keyword=target_keyword,
            keyword=keyword,
        )

        resolved_tone = self._resolve_tone(
            tone
        )

        resolved_length = self._resolve_length(
            length
        )

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

        estimated_word_count = self._estimate_word_count(
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
            estimated_word_count=estimated_word_count,
            seo_score=seo_score,
        )

    @staticmethod
    def _resolve_keyword(
        *,
        product: DiscoveryProduct,
        target_keyword: str | None,
        keyword: str | None,
    ) -> str:
        """
        Resolve the target keyword from old or new inputs.
        """
        possible_values = [
            target_keyword,
            keyword,
            product.product_name,
        ]

        for value in possible_values:
            if value and value.strip():
                return value.strip()

        raise ValueError(
            "A target keyword is required."
        )

    def _resolve_tone(
        self,
        tone: str,
    ) -> str:
        """
        Validate and normalize the requested writing tone.
        """
        cleaned_tone = (
            tone.strip().title()
            if tone
            else "Professional"
        )

        if cleaned_tone not in self.VALID_TONES:
            return "Professional"

        return cleaned_tone

    def _resolve_length(
        self,
        length: str,
    ) -> str:
        """
        Validate and normalize the requested article length.
        """
        cleaned_length = (
            length.strip().title()
            if length
            else "Medium"
        )

        if cleaned_length not in self.VALID_LENGTHS:
            return "Medium"

        return cleaned_length

    @staticmethod
    def _build_title(
        *,
        product: DiscoveryProduct,
        keyword: str,
    ) -> str:
        return (
            f"{keyword} Review: Is "
            f"{product.product_name} Worth It?"
        )

    @staticmethod
    def _build_meta_description(
        *,
        product: DiscoveryProduct,
        keyword: str,
    ) -> str:
        return (
            f"Read our {keyword} review and discover the strengths, "
            f"risks, audience and commercial potential of "
            f"{product.product_name} before making a decision."
        )

    def _build_introduction(
        self,
        *,
        product: DiscoveryProduct,
        keyword: str,
        tone: str,
    ) -> str:
        description = (
            product.description
            or (
                f"{product.product_name} is an affiliate product "
                f"related to {keyword}."
            )
        )

        base_introduction = (
            f"If you are researching {keyword}, you may be considering "
            f"{product.product_name}. {description} In this review, "
            "we examine the product's audience, market demand, "
            "commercial potential, strengths and possible risks."
        )

        return self._apply_tone(
            text=base_introduction,
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
        audience_text = self._join_items(
            analysis.target_audience
        )

        strengths_text = self._join_items(
            analysis.strengths
        )

        weaknesses_text = self._join_items(
            analysis.weaknesses
        )

        recommendation_text = self._join_items(
            analysis.recommendations
        )

        sections = [
            SEOSection(
                heading=(
                    f"What Is "
                    f"{product.product_name}?"
                ),
                content=(
                    f"{product.product_name} is positioned in the "
                    f"{product.category or 'affiliate education'} "
                    f"market. It is priced at "
                    f"R$ {product.price:,.2f} and offers a "
                    f"commission of "
                    f"R$ {product.commission_amount:,.2f} per sale. "
                    f"The current opportunity score is "
                    f"{product.opportunity_score:.1f}/100."
                ),
            ),
            SEOSection(
                heading=(
                    f"Who Is "
                    f"{product.product_name} For?"
                ),
                content=(
                    f"The product is most relevant to "
                    f"{audience_text}. Potential buyers should "
                    "compare the course content, delivery format "
                    "and expected outcomes with their own needs "
                    "before purchasing."
                ),
            ),
            SEOSection(
                heading=(
                    f"Market Demand for {keyword}"
                ),
                content=(
                    f"The available data indicates approximately "
                    f"{product.search_volume:,} monthly searches, "
                    f"a Google Trend score of "
                    f"{product.google_trend_score:.0f}/100 and "
                    f"competition of "
                    f"{product.competition_score:.0f}/100. "
                    f"Filtrify currently rates the SEO potential "
                    f"as {analysis.seo_potential.lower()}."
                ),
            ),
            SEOSection(
                heading=(
                    "Main Strengths of "
                    f"{product.product_name}"
                ),
                content=(
                    "The main strengths identified are: "
                    f"{strengths_text}."
                ),
            ),
            SEOSection(
                heading=(
                    "Possible Weaknesses and Risks"
                ),
                content=(
                    "The current analysis highlights the following: "
                    f"{weaknesses_text}. The refund rate is "
                    f"{product.refund_rate:.1f}%, so affiliates "
                    "should continue monitoring customer satisfaction "
                    "and conversion quality."
                ),
            ),
            SEOSection(
                heading=(
                    "Affiliate Marketing Potential"
                ),
                content=(
                    f"The product has "
                    f"{analysis.commercial_potential.lower()} "
                    "commercial potential. Its Google Ads potential "
                    f"is {analysis.google_ads_potential.lower()}, "
                    "email marketing potential is "
                    f"{analysis.email_marketing_potential.lower()}, "
                    "and landing-page potential is "
                    f"{analysis.landing_page_potential.lower()}. "
                    "Recommended actions include "
                    f"{recommendation_text}."
                ),
            ),
            SEOSection(
                heading=(
                    f"Is {product.product_name} "
                    "Worth Promoting?"
                ),
                content=(
                    "The estimated probability of success is "
                    f"{analysis.probability_of_success:.1f}%, "
                    "with an analysis confidence of "
                    f"{analysis.confidence_score:.1f}%. "
                    "This does not guarantee results, but it "
                    "suggests whether the product deserves a "
                    "controlled test."
                ),
            ),
        ]

        adjusted_sections = [
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

        return adjusted_sections

    def _build_conclusion(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        tone: str,
    ) -> str:
        if analysis.commercial_potential in {
            "Excellent",
            "Strong",
        }:
            conclusion = (
                f"{product.product_name} appears to be a credible "
                "candidate for controlled promotion. Start with the "
                "recommended organic strategy, monitor real conversion "
                "data and only increase investment after the results "
                "support scaling."
            )

        elif analysis.commercial_potential == "Moderate":
            conclusion = (
                f"{product.product_name} may be worth testing, but "
                "the current evidence is mixed. Use a small budget, "
                "collect performance data and compare the result with "
                "stronger products before scaling."
            )

        else:
            conclusion = (
                f"{product.product_name} should not be prioritised "
                "yet. Continue researching the market and consider "
                "alternatives with stronger demand and commercial "
                "signals."
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
        if product.sales_page_url:
            call_to_action = (
                f"Review the official "
                f"{product.product_name} sales page, verify all "
                "claims and decide whether it fits your needs."
            )

        else:
            call_to_action = (
                "Review the available information about "
                f"{product.product_name} before making a decision."
            )

        return self._apply_tone(
            text=call_to_action,
            tone=tone,
        )

    @staticmethod
    def _apply_tone(
        *,
        text: str,
        tone: str,
    ) -> str:
        """
        Apply a simple deterministic tone adjustment.

        A future LLM integration can provide richer rewriting.

        LLM = Large Language Model.
        """
        if tone == "Friendly":
            return (
                "Let's take a practical look at this. "
                f"{text}"
            )

        if tone == "Persuasive":
            return (
                f"{text} These signals make the opportunity "
                "worthy of serious consideration."
            )

        if tone == "Educational":
            return (
                "To understand the opportunity clearly, "
                f"{text}"
            )

        return text

    @staticmethod
    def _apply_length(
        *,
        text: str,
        length: str,
    ) -> str:
        """
        Apply a simple deterministic length adjustment.
        """
        if length == "Short":
            sentences = [
                sentence.strip()
                for sentence in text.split(".")
                if sentence.strip()
            ]

            return (
                sentences[0] + "."
                if sentences
                else text
            )

        if length == "Long":
            return (
                f"{text} Affiliates should validate these signals "
                "using real traffic, conversion and customer-feedback "
                "data before increasing their investment."
            )

        return text

    @staticmethod
    def _join_items(
        items: list[str],
    ) -> str:
        cleaned_items = [
            item.strip().rstrip(".")
            for item in items
            if item.strip()
        ]

        if not cleaned_items:
            return (
                "no major points were identified"
            )

        if len(cleaned_items) == 1:
            return cleaned_items[0]

        if len(cleaned_items) == 2:
            return (
                f"{cleaned_items[0]} and "
                f"{cleaned_items[1]}"
            )

        return (
            ", ".join(
                cleaned_items[:-1]
            )
            + f", and {cleaned_items[-1]}"
        )

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
        text_parts = [
            title,
            meta_description,
            introduction,
            conclusion,
            call_to_action,
        ]

        for section in sections:
            text_parts.extend(
                [
                    section.heading,
                    section.content,
                ]
            )

        combined_text = " ".join(
            text_parts
        )

        return len(
            combined_text.split()
        )

    @staticmethod
    def _calculate_seo_score(
        *,
        product: DiscoveryProduct,
        keyword: str,
        title: str,
        meta_description: str,
        sections: list[SEOSection],
    ) -> float:
        score = 0.0

        if keyword.casefold() in title.casefold():
            score += 20

        if (
            keyword.casefold()
            in meta_description.casefold()
        ):
            score += 15

        if 45 <= len(title) <= 65:
            score += 15

        if 120 <= len(meta_description) <= 165:
            score += 15

        if len(sections) >= 6:
            score += 15

        if product.search_volume >= 3000:
            score += 10

        if product.google_trend_score >= 70:
            score += 10

        return round(
            min(score, 100),
            1,
        )