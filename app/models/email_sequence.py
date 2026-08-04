"""Email-sequence models used by Filtrify campaigns.

An email sequence is a coordinated group of marketing emails sent in a
planned order.

CTA means Call to Action.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CampaignEmail:
    """Represent one email inside a campaign sequence.

    Attributes:
        sequence_number:
            Position of the email within the sequence.

        subject:
            Email subject line.

        preview_text:
            Short inbox-preview text.

        purpose:
            Main role of the email, such as education, trust, objection
            handling, or promotion.

        body:
            Complete email body.

        call_to_action:
            Main action the reader should take.
    """

    sequence_number: int
    subject: str
    preview_text: str
    purpose: str
    body: str
    call_to_action: str

    def __post_init__(self) -> None:
        """Validate and normalize the email values."""

        if self.sequence_number < 1:
            raise ValueError(
                "Email sequence number must be greater than zero."
            )

        text_fields = (
            "subject",
            "preview_text",
            "purpose",
            "body",
            "call_to_action",
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
                    f"CampaignEmail.{field_name} must be a string."
                )

            cleaned_value = field_value.strip()

            if not cleaned_value:
                raise ValueError(
                    f"CampaignEmail.{field_name} cannot be empty."
                )

            object.__setattr__(
                self,
                field_name,
                cleaned_value,
            )

    @property
    def word_count(self) -> int:
        """Return the approximate email word count."""

        combined_text = " ".join(
            [
                self.subject,
                self.preview_text,
                self.body,
                self.call_to_action,
            ]
        )

        return len(
            combined_text.split()
        )


@dataclass(frozen=True, slots=True)
class EmailSequence:
    """Represent a complete coordinated email campaign.

    Attributes:
        sequence_name:
            Human-readable name for the email sequence.

        product_name:
            Product promoted by the emails.

        target_audience:
            Intended reader group.

        tone:
            Shared writing tone.

        emails:
            Ordered campaign emails.

        strategy_summary:
            Short explanation of how the sequence should be used.

        primary_goal:
            Main conversion goal for the sequence.
    """

    sequence_name: str
    product_name: str
    target_audience: str
    tone: str
    emails: tuple[CampaignEmail, ...] = field(
        default_factory=tuple
    )
    strategy_summary: str = ""
    primary_goal: str = "Visit Sales Page"

    def __post_init__(self) -> None:
        """Validate and normalize the sequence values."""

        text_fields = (
            "sequence_name",
            "product_name",
            "target_audience",
            "tone",
            "strategy_summary",
            "primary_goal",
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
                    f"EmailSequence.{field_name} must be a string."
                )

            object.__setattr__(
                self,
                field_name,
                field_value.strip(),
            )

        normalized_emails = tuple(
            sorted(
                self.emails,
                key=lambda email: email.sequence_number,
            )
        )

        for email in normalized_emails:
            if not isinstance(
                email,
                CampaignEmail,
            ):
                raise TypeError(
                    "Every email must be a CampaignEmail instance."
                )

        sequence_numbers = [
            email.sequence_number
            for email in normalized_emails
        ]

        if len(sequence_numbers) != len(
            set(sequence_numbers)
        ):
            raise ValueError(
                "Email sequence numbers must be unique."
            )

        object.__setattr__(
            self,
            "emails",
            normalized_emails,
        )

    @property
    def email_count(self) -> int:
        """Return the number of emails in the sequence."""

        return len(
            self.emails
        )

    @property
    def total_estimated_words(self) -> int:
        """Return the combined approximate word count."""

        return sum(
            email.word_count
            for email in self.emails
        )

    def to_plain_text(self) -> str:
        """Convert the complete sequence into readable plain text."""

        blocks = [
            self.sequence_name,
            "",
            f"Product: {self.product_name}",
            f"Target audience: {self.target_audience}",
            f"Tone: {self.tone}",
            f"Primary goal: {self.primary_goal}",
        ]

        if self.strategy_summary:
            blocks.extend(
                [
                    "",
                    "Strategy Summary",
                    self.strategy_summary,
                ]
            )

        for email in self.emails:
            blocks.extend(
                [
                    "",
                    (
                        f"Email {email.sequence_number}: "
                        f"{email.purpose}"
                    ),
                    f"Subject: {email.subject}",
                    (
                        "Preview text: "
                        f"{email.preview_text}"
                    ),
                    "",
                    email.body,
                    "",
                    (
                        "Call to Action: "
                        f"{email.call_to_action}"
                    ),
                ]
            )

        return "\n".join(
            blocks
        ).strip()