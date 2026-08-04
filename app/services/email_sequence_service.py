"""Generate coordinated email sequences from product intelligence.

This service creates a structured series of marketing emails for one
affiliate product.

CTA means Call to Action.
"""

from __future__ import annotations

from typing import Any

from app.models.discovery_product import (
    DiscoveryProduct,
)
from app.models.email_sequence import (
    CampaignEmail,
    EmailSequence,
)
from app.models.product_analysis import (
    ProductAnalysis,
)
from app.services.base_content_generator import (
    BaseContentGenerator,
)


class EmailSequenceService(BaseContentGenerator):
    """Generate a coordinated affiliate-marketing email sequence."""

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

    MINIMUM_EMAIL_COUNT = 3
    MAXIMUM_EMAIL_COUNT = 5

    def generate(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        target_audience: str | None = None,
        tone: str = "Professional",
        email_count: int = 3,
        primary_goal: str = "Visit Sales Page",
        sequence_name: str | None = None,
        **kwargs: Any,
    ) -> EmailSequence:
        """Generate one complete email sequence.

        Args:
            product:
                Product promoted by the sequence.

            analysis:
                Product-intelligence analysis used to shape the messages.

            target_audience:
                Intended email recipients. When omitted, the audience from
                the product analysis is used.

            tone:
                Shared writing style.

            email_count:
                Number of emails to generate. Supported values are three to
                five.

            primary_goal:
                Main action the reader should take.

            sequence_name:
                Optional custom name for the sequence.

            kwargs:
                Additional future generator settings.

        Returns:
            A structured EmailSequence.
        """

        self._validate_inputs(
            product=product,
            analysis=analysis,
        )

        resolved_audience = self._resolve_audience(
            analysis=analysis,
            target_audience=target_audience,
        )

        resolved_tone = self._resolve_tone(
            tone
        )

        resolved_email_count = self._resolve_email_count(
            email_count
        )

        resolved_goal = self._resolve_goal(
            primary_goal
        )

        resolved_sequence_name = (
            self._resolve_sequence_name(
                product=product,
                sequence_name=sequence_name,
            )
        )

        emails = self._build_emails(
            product=product,
            analysis=analysis,
            audience=resolved_audience,
            tone=resolved_tone,
            email_count=resolved_email_count,
            primary_goal=resolved_goal,
        )

        strategy_summary = self._build_strategy_summary(
            product=product,
            email_count=resolved_email_count,
            primary_goal=resolved_goal,
        )

        return EmailSequence(
            sequence_name=resolved_sequence_name,
            product_name=product.product_name,
            target_audience=resolved_audience,
            tone=resolved_tone,
            emails=tuple(
                emails
            ),
            strategy_summary=strategy_summary,
            primary_goal=resolved_goal,
        )

    @staticmethod
    def _validate_inputs(
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
    ) -> None:
        """Validate the required service inputs."""

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
    def _resolve_audience(
        *,
        analysis: ProductAnalysis,
        target_audience: str | None,
    ) -> str:
        """Resolve the intended email audience."""

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

    def _resolve_email_count(
        self,
        email_count: int,
    ) -> int:
        """Validate and normalize the requested email count."""

        try:
            resolved_count = int(
                email_count
            )
        except (
            TypeError,
            ValueError,
        ):
            return self.MINIMUM_EMAIL_COUNT

        return max(
            self.MINIMUM_EMAIL_COUNT,
            min(
                resolved_count,
                self.MAXIMUM_EMAIL_COUNT,
            ),
        )

    def _resolve_goal(
        self,
        primary_goal: str,
    ) -> str:
        """Validate and normalize the primary sequence goal."""

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
    def _resolve_sequence_name(
        *,
        product: DiscoveryProduct,
        sequence_name: str | None,
    ) -> str:
        """Resolve the sequence display name."""

        if (
            sequence_name
            and sequence_name.strip()
        ):
            return sequence_name.strip()

        return (
            f"{product.product_name} "
            "Email Sequence"
        )

    def _build_emails(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        audience: str,
        tone: str,
        email_count: int,
        primary_goal: str,
    ) -> list[CampaignEmail]:
        """Build the requested sequence emails."""

        email_builders = [
            self._build_introduction_email,
            self._build_problem_email,
            self._build_value_email,
            self._build_objection_email,
            self._build_decision_email,
        ]

        emails: list[CampaignEmail] = []

        for sequence_number, email_builder in enumerate(
            email_builders[:email_count],
            start=1,
        ):
            emails.append(
                email_builder(
                    sequence_number=sequence_number,
                    product=product,
                    analysis=analysis,
                    audience=audience,
                    tone=tone,
                    primary_goal=primary_goal,
                )
            )

        return emails

    def _build_introduction_email(
        self,
        *,
        sequence_number: int,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        audience: str,
        tone: str,
        primary_goal: str,
    ) -> CampaignEmail:
        """Build the introductory email."""

        body = (
            f"If you are part of {audience}, improving your skills or "
            f"finding a more structured learning path may be important to "
            f"you. {product.product_name} is positioned as an option worth "
            "reviewing carefully. Before making a decision, it is useful to "
            "understand who the product is for, what the available market "
            "signals suggest, and whether it matches your goals."
        )

        return CampaignEmail(
            sequence_number=sequence_number,
            subject=(
                f"Is {product.product_name} "
                "right for you?"
            ),
            preview_text=(
                "A practical introduction before you decide."
            ),
            purpose="Introduction",
            body=self._apply_tone(
                text=body,
                tone=tone,
            ),
            call_to_action=self._build_call_to_action(
                product=product,
                primary_goal=primary_goal,
            ),
        )

    def _build_problem_email(
        self,
        *,
        sequence_number: int,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        audience: str,
        tone: str,
        primary_goal: str,
    ) -> CampaignEmail:
        """Build the audience-problem email."""

        body = (
            "Choosing a course or digital product can be difficult when "
            "there are many alternatives and limited reliable information. "
            f"For {audience}, the most important step is comparing the "
            "curriculum, delivery format, expected outcomes, price, and "
            f"refund terms. {product.product_name} currently has an "
            f"opportunity score of {product.opportunity_score:.1f}/100, "
            "but this score should support your research rather than replace "
            "your own review."
        )

        return CampaignEmail(
            sequence_number=sequence_number,
            subject=(
                "What should you check before "
                "choosing a course?"
            ),
            preview_text=(
                "Use these practical points to compare your options."
            ),
            purpose="Problem awareness",
            body=self._apply_tone(
                text=body,
                tone=tone,
            ),
            call_to_action=self._build_call_to_action(
                product=product,
                primary_goal=primary_goal,
            ),
        )

    def _build_value_email(
        self,
        *,
        sequence_number: int,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        audience: str,
        tone: str,
        primary_goal: str,
    ) -> CampaignEmail:
        """Build the product-value email."""

        strengths = self._join_items(
            analysis.strengths
        )

        body = (
            f"The current Filtrify analysis identifies these strengths for "
            f"{product.product_name}: {strengths}. The product is priced at "
            f"R$ {product.price:,.2f}. Market information also indicates "
            f"approximately {product.search_volume:,} monthly searches and "
            f"a Google Trend score of "
            f"{product.google_trend_score:.0f}/100. These figures do not "
            "guarantee a result, but they provide useful context when "
            "evaluating market interest."
        )

        return CampaignEmail(
            sequence_number=sequence_number,
            subject=(
                f"What stands out about "
                f"{product.product_name}?"
            ),
            preview_text=(
                "Review the product and market signals."
            ),
            purpose="Value and benefits",
            body=self._apply_tone(
                text=body,
                tone=tone,
            ),
            call_to_action=self._build_call_to_action(
                product=product,
                primary_goal=primary_goal,
            ),
        )

    def _build_objection_email(
        self,
        *,
        sequence_number: int,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        audience: str,
        tone: str,
        primary_goal: str,
    ) -> CampaignEmail:
        """Build the objection-handling email."""

        weaknesses = self._join_items(
            analysis.weaknesses
        )

        body = (
            "A responsible decision should consider possible limitations as "
            f"well as benefits. The current analysis highlights: "
            f"{weaknesses}. The recorded refund rate is "
            f"{product.refund_rate:.1f}%. Before purchasing, check the "
            "official product page, refund conditions, instructor details, "
            "course contents, and whether the offer suits your current skill "
            "level and objectives."
        )

        return CampaignEmail(
            sequence_number=sequence_number,
            subject=(
                f"Important points to consider before "
                f"buying {product.product_name}"
            ),
            preview_text=(
                "Review the risks and limitations before deciding."
            ),
            purpose="Objection handling",
            body=self._apply_tone(
                text=body,
                tone=tone,
            ),
            call_to_action=self._build_call_to_action(
                product=product,
                primary_goal=primary_goal,
            ),
        )

    def _build_decision_email(
        self,
        *,
        sequence_number: int,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        audience: str,
        tone: str,
        primary_goal: str,
    ) -> CampaignEmail:
        """Build the final decision email."""

        recommendations = self._join_items(
            analysis.recommendations
        )

        body = (
            f"Based on the available data, {product.product_name} has "
            f"{analysis.commercial_potential.lower()} commercial potential. "
            f"The estimated probability of success is "
            f"{analysis.probability_of_success:.1f}%, with an analysis "
            f"confidence of {analysis.confidence_score:.1f}%. These figures "
            "are estimates rather than guarantees. Recommended next steps "
            f"include: {recommendations}. Review the official information "
            "and make a decision based on your own needs, budget, and goals."
        )

        return CampaignEmail(
            sequence_number=sequence_number,
            subject=(
                f"Should you consider "
                f"{product.product_name}?"
            ),
            preview_text=(
                "A final checklist before making your decision."
            ),
            purpose="Decision and conversion",
            body=self._apply_tone(
                text=body,
                tone=tone,
            ),
            call_to_action=self._build_call_to_action(
                product=product,
                primary_goal=primary_goal,
            ),
        )

    @staticmethod
    def _build_call_to_action(
        *,
        product: DiscoveryProduct,
        primary_goal: str,
    ) -> str:
        """Build the email call to action."""

        if primary_goal == "Generate Leads":
            return (
                "Get the free guide and continue your research."
            )

        if primary_goal == "Promote Product":
            return (
                f"Explore {product.product_name} and review the details."
            )

        return (
            f"Visit the official {product.product_name} sales page."
        )

    @staticmethod
    def _build_strategy_summary(
        *,
        product: DiscoveryProduct,
        email_count: int,
        primary_goal: str,
    ) -> str:
        """Build the sequence strategy summary."""

        return (
            f"This {email_count}-email sequence introduces "
            f"{product.product_name}, explains the reader's decision problem, "
            "presents available product and market signals, addresses likely "
            f"concerns, and finishes with the goal: {primary_goal}. "
            "Review all claims and links before sending the campaign."
        )

    @staticmethod
    def _apply_tone(
        *,
        text: str,
        tone: str,
    ) -> str:
        """Apply a simple deterministic tone adjustment."""

        if tone == "Friendly":
            return (
                "Here is a simple way to look at it. "
                f"{text}"
            )

        if tone == "Persuasive":
            return (
                f"{text} If the offer matches your goals, it may deserve "
                "a closer look."
            )

        if tone == "Educational":
            return (
                "To understand the decision clearly, "
                f"{text}"
            )

        return text

    @staticmethod
    def _join_items(
        items: list[str],
    ) -> str:
        """Join analysis items into readable text."""

        cleaned_items = [
            str(item).strip().rstrip(".")
            for item in items
            if str(item).strip()
        ]

        if not cleaned_items:
            return "no major points were identified"

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