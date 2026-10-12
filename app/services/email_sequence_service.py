
"""Generate responsible affiliate email sequences for YAffiliate."""

from __future__ import annotations

from typing import Any

from app.models.discovery_product import DiscoveryProduct
from app.models.email_sequence import CampaignEmail, EmailSequence
from app.models.product_analysis import ProductAnalysis
from app.services.base_content_generator import BaseContentGenerator


class EmailSequenceService(BaseContentGenerator):
    """
    Generate a structured sequence of three to five emails.

    CTA means Call to Action: the next step requested from a reader.

    This service generates drafts, not verified product reviews.
    It does not send emails or manage subscriber consent.
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
        """Generate an email sequence using the existing data model."""

        self._validate_inputs(product=product, analysis=analysis)

        audience = self._resolve_audience(
            analysis=analysis,
            target_audience=target_audience,
        )

        resolved_tone = self._resolve_tone(tone)
        count = self._resolve_email_count(email_count)
        goal = self._resolve_goal(primary_goal)

        name = (
            self._clean(sequence_name)
            or f"{product.product_name} Email Sequence"
        )

        stages = self._select_stages(count)
        emails = []

        for number, stage in enumerate(stages, start=1):
            emails.append(
                self._build_email(
                    sequence_number=number,
                    stage=stage,
                    product=product,
                    audience=audience,
                    tone=resolved_tone,
                    goal=goal,
                )
            )

        summary = self._build_strategy_summary(
            product=product,
            email_count=count,
            primary_goal=goal,
        )

        return EmailSequence(
            sequence_name=name,
            product_name=product.product_name,
            target_audience=audience,
            tone=resolved_tone,
            emails=tuple(emails),
            strategy_summary=summary,
            primary_goal=goal,
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
    def _resolve_audience(
        cls,
        *,
        analysis: ProductAnalysis,
        target_audience: str | None,
    ) -> str:
        supplied = cls._clean(target_audience)
        if supplied:
            return supplied

        audience_items = getattr(analysis, "target_audience", None) or []
        cleaned = [
            cls._clean(item)
            for item in audience_items
            if cls._clean(item)
        ]

        return (
            ", ".join(cleaned)
            if cleaned
            else "people researching this type of product"
        )

    @classmethod
    def _resolve_tone(cls, tone: str) -> str:
        supplied = cls._clean(tone)

        for valid in cls.VALID_TONES:
            if supplied.casefold() == valid.casefold():
                return valid

        return "Professional"

    @classmethod
    def _resolve_goal(cls, primary_goal: str) -> str:
        supplied = cls._clean(primary_goal)

        for valid in cls.VALID_GOALS:
            if supplied.casefold() == valid.casefold():
                return valid

        return "Visit Sales Page"

    @classmethod
    def _resolve_email_count(cls, email_count: int) -> int:
        try:
            count = int(email_count)
        except (TypeError, ValueError, OverflowError):
            count = cls.MINIMUM_EMAIL_COUNT

        return max(
            cls.MINIMUM_EMAIL_COUNT,
            min(count, cls.MAXIMUM_EMAIL_COUNT),
        )

    @staticmethod
    def _select_stages(email_count: int) -> list[str]:
        """
        Ensure every sequence ends with a decision email.

        3 emails: introduction, evaluation, decision
        4 emails: introduction, evaluation, concerns, decision
        5 emails: introduction, evaluation, value,
                  concerns, decision
        """
        if email_count == 3:
            return ["introduction", "evaluation", "decision"]

        if email_count == 4:
            return [
                "introduction",
                "evaluation",
                "concerns",
                "decision",
            ]

        return [
            "introduction",
            "evaluation",
            "value",
            "concerns",
            "decision",
        ]

    @staticmethod
    def _has_url(value: Any) -> bool:
        """Basic URL format check; does not verify the destination."""
        if not isinstance(value, str):
            return False

        url = value.strip().lower()

        if not url.startswith(("https://", "http://")):
            return False

        parts = url.split("/")
        return len(parts) > 2 and "." in parts[2] and " " not in url

    @staticmethod
    def _positive_number(value: Any) -> bool:
        if value is None or isinstance(value, bool):
            return False

        try:
            return float(value) > 0
        except (TypeError, ValueError, OverflowError):
            return False

    def _build_email(
        self,
        *,
        sequence_number: int,
        stage: str,
        product: DiscoveryProduct,
        audience: str,
        tone: str,
        goal: str,
    ) -> CampaignEmail:
        name = self._clean(product.product_name) or "this product"
        description = self._clean(
            getattr(product, "description", None)
        )
        category = self._clean(
            getattr(product, "category", None)
        )

        if stage == "introduction":
            subject = f"Considering {name}? Start with these questions"
            preview = "A useful starting point for evaluating the offer."
            purpose = "Introduction"

            body = (
                f"Hello,\n\n"
                f"If you are exploring {name}, it helps to know "
                "what you are actually getting before you commit.\n\n"
                "Start with three questions:\n"
                "- What does the product include?\n"
                "- Who is it intended for?\n"
                "- What are the total costs and conditions?\n\n"
                "A careful review can help you decide whether "
                "the offer fits your needs."
            )

        elif stage == "evaluation":
            subject = f"How to evaluate {name} before buying"
            preview = "A practical checklist to compare your options."
            purpose = "Product evaluation"

            category_line = (
                f"The product is listed under {category}. "
                if category
                else ""
            )

            body = (
                f"Hello,\n\n"
                f"Before choosing {name}, compare the offer "
                "with your own requirements.\n\n"
                f"{category_line}"
                "Look for a clear description of the features, "
                "delivery method, support, current pricing "
                "and refund terms.\n\n"
                "If important details are missing, ask the seller "
                "for clarification. You should not have to guess "
                "what a purchase includes."
            )

        elif stage == "value":
            subject = f"What do you actually get with {name}?"
            preview = "Separate confirmed features from open questions."
            purpose = "Value and benefits"

            if description:
                product_details = (
                    "The available product description states:\n"
                    f"{description}\n\n"
                    "These details come from the product record "
                    "and have not been independently verified."
                )
            else:
                product_details = (
                    "The current product record does not provide "
                    "enough detail to verify specific features "
                    "or benefits."
                )

            body = (
                f"Hello,\n\n"
                f"One way to assess {name} is to focus on "
                "what the offer includes rather than relying "
                "on promotional language.\n\n"
                f"{product_details}\n\n"
                "Check the official description, compare alternatives "
                "and look for independent evidence before deciding."
            )

        elif stage == "concerns":
            subject = f"Questions worth asking about {name}"
            preview = "Pricing, refunds and other details to verify."
            purpose = "Objection handling"

            if self._positive_number(
                getattr(product, "price", None)
            ):
                pricing = (
                    "A price is recorded in the product data, "
                    "but its currency and current validity "
                    "must be confirmed at checkout."
                )
            else:
                pricing = (
                    "The current selling price has not been verified."
                )

            body = (
                f"Hello,\n\n"
                f"Still comparing options for {name}? "
                "A few checks may help:\n\n"
                f"- Pricing: {pricing}\n"
                "- Refunds: What are the current refund conditions?\n"
                "- Support: How can you contact the seller?\n"
                "- Suitability: Are there prerequisites or limitations?\n\n"
                "Missing information does not automatically mean "
                "an offer is good or bad. It means more verification "
                "is needed."
            )

        else:
            subject = f"Is {name} the right choice for you?"
            preview = "A final checklist before making a decision."
            purpose = "Decision and conversion"

            body = (
                f"Hello,\n\n"
                f"Before making a final decision about {name}, "
                "consider the following:\n\n"
                "- Does the product address your actual needs?\n"
                "- Have you verified its features and seller claims?\n"
                "- Do you understand the price and payment terms?\n"
                "- Have you reviewed the refund policy?\n"
                "- Have you compared relevant alternatives?\n\n"
                "If the answers are clear and the offer fits "
                "your goals, you can review the official details "
                "and decide on your next step."
            )

        body = self._apply_tone(body, tone)

        disclosure = (
            "\n\nAffiliate disclosure: This message may contain "
            "affiliate links. If you purchase through one of "
            "those links, the sender may earn a commission. "
            "Review this wording to match the actual relationship."
        )

        body += disclosure

        return CampaignEmail(
            sequence_number=sequence_number,
            subject=subject,
            preview_text=preview,
            purpose=purpose,
            body=body,
            call_to_action=self._build_call_to_action(
                product=product,
                primary_goal=goal,
            ),
        )

    @classmethod
    def _build_call_to_action(
        cls,
        *,
        product: DiscoveryProduct,
        primary_goal: str,
    ) -> str:
        name = cls._clean(product.product_name) or "the product"

        affiliate_url = getattr(product, "affiliate_url", None)
        sales_url = getattr(product, "sales_page_url", None)

        if primary_goal == "Generate Leads":
            return (
                "Request more information. "
                "[Add a verified lead-capture link before sending.]"
            )

        if cls._has_url(affiliate_url):
            return (
                f"Review the {name} offer: "
                f"{affiliate_url.strip()}"
            )

        if cls._has_url(sales_url):
            return (
                f"Review the official {name} product page: "
                f"{sales_url.strip()} "
                "[No affiliate tracking link is configured.]"
            )

        return (
            f"Learn more about {name}. "
            "[Add and verify the destination link before sending.]"
        )

    @staticmethod
    def _apply_tone(text: str, tone: str) -> str:
        """Make a modest tone adjustment without adding new claims."""

        if tone == "Friendly":
            return text.replace(
                "Hello,\n\n",
                "Hi there,\n\n",
                1,
            )

        if tone == "Educational":
            return text.replace(
                "Hello,\n\n",
                "Hello,\n\nHere is a practical way to assess "
                "the offer.\n\n",
                1,
            )

        if tone == "Persuasive":
            return text.replace(
                "Hello,\n\n",
                "Hello,\n\nA little research now can help "
                "you make a more confident decision.\n\n",
                1,
            )

        return text

    @staticmethod
    def _build_strategy_summary(
        *,
        product: DiscoveryProduct,
        email_count: int,
        primary_goal: str,
    ) -> str:
        return (
            f"This {email_count}-email sequence introduces "
            f"{product.product_name}, helps readers evaluate "
            "the offer, addresses relevant concerns where "
            "the sequence length permits, and ends with "
            f"a decision-focused message. Goal: {primary_goal}. "
            "Before sending, verify product claims and links, "
            "confirm recipient consent, add sender identification "
            "and a working unsubscribe mechanism, and review "
            "applicable email-marketing requirements."
        )
