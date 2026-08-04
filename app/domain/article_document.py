"""Structured article models used throughout Filtrify.

This module represents an article as structured information instead of one
unlabelled block of text.

AI means Artificial Intelligence.

SEO means Search Engine Optimization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ArticleSection:
    """Represent one named section of an article.

    Attributes:
        heading:
            Section heading displayed to the reader.

        content:
            Main written content contained in the section.

        section_type:
            Optional category describing the purpose of the section, such as
            introduction, body, benefits, risks, conclusion, or call_to_action.

        position:
            Optional numerical position used to preserve section order.
    """

    heading: str
    content: str
    section_type: str = "body"
    position: int = 0

    def __post_init__(self) -> None:
        """Validate and normalize the section values."""

        cleaned_heading = self.heading.strip()
        cleaned_content = self.content.strip()
        cleaned_section_type = (
            self.section_type.strip().lower()
            or "body"
        )

        if not cleaned_heading:
            raise ValueError(
                "Article section heading cannot be empty."
            )

        if not cleaned_content:
            raise ValueError(
                "Article section content cannot be empty."
            )

        if self.position < 0:
            raise ValueError(
                "Article section position cannot be negative."
            )

        object.__setattr__(
            self,
            "heading",
            cleaned_heading,
        )

        object.__setattr__(
            self,
            "content",
            cleaned_content,
        )

        object.__setattr__(
            self,
            "section_type",
            cleaned_section_type,
        )

    @property
    def word_count(self) -> int:
        """Return the approximate number of words in this section."""

        return len(
            self.content.split()
        )

    def to_prompt_text(self) -> str:
        """Convert the section into labelled prompt text."""

        return "\n".join(
            [
                f"Section type: {self.section_type}",
                f"Heading: {self.heading}",
                "Content:",
                self.content,
            ]
        )


@dataclass(frozen=True, slots=True)
class ArticleDocument:
    """Represent a complete structured article.

    The model contains fields commonly needed by Filtrify generators,
    editors, Artificial Intelligence actions, Search Engine Optimization
    tools, and export services.

    Attributes:
        title:
            Main article title.

        meta_description:
            Search-engine description associated with the article.

        introduction:
            Opening section of the article.

        sections:
            Ordered body sections.

        conclusion:
            Closing summary of the article.

        call_to_action:
            Final instruction encouraging the reader to take an action.

        primary_keyword:
            Main Search Engine Optimization keyword.

        secondary_keywords:
            Additional relevant keywords.

        target_audience:
            Intended reader group.

        tone:
            Desired writing style or voice.

        language:
            Article language.

        content_type:
            Type of article, such as SEO article, review, comparison, or blog.

        faq_items:
            Frequently asked questions stored as question-and-answer pairs.

        metadata:
            Additional structured values required by future Filtrify modules.
    """

    title: str = ""
    meta_description: str = ""
    introduction: str = ""
    sections: tuple[ArticleSection, ...] = field(
        default_factory=tuple
    )
    conclusion: str = ""
    call_to_action: str = ""
    primary_keyword: str = ""
    secondary_keywords: tuple[str, ...] = field(
        default_factory=tuple
    )
    target_audience: str = ""
    tone: str = ""
    language: str = "English"
    content_type: str = "article"
    faq_items: tuple[tuple[str, str], ...] = field(
        default_factory=tuple
    )
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Normalize text and validate structured article values."""

        text_fields = (
            "title",
            "meta_description",
            "introduction",
            "conclusion",
            "call_to_action",
            "primary_keyword",
            "target_audience",
            "tone",
            "language",
            "content_type",
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
                    f"ArticleDocument.{field_name} must be a string."
                )

            object.__setattr__(
                self,
                field_name,
                field_value.strip(),
            )

        normalized_sections = tuple(
            sorted(
                self.sections,
                key=lambda section: section.position,
            )
        )

        for section in normalized_sections:
            if not isinstance(
                section,
                ArticleSection,
            ):
                raise TypeError(
                    "Every article section must be an "
                    "ArticleSection instance."
                )

        object.__setattr__(
            self,
            "sections",
            normalized_sections,
        )

        normalized_keywords = tuple(
            keyword.strip()
            for keyword in self.secondary_keywords
            if isinstance(
                keyword,
                str,
            )
            and keyword.strip()
        )

        object.__setattr__(
            self,
            "secondary_keywords",
            normalized_keywords,
        )

        normalized_faq_items: list[tuple[str, str]] = []

        for faq_item in self.faq_items:
            if (
                not isinstance(
                    faq_item,
                    tuple,
                )
                or len(faq_item) != 2
            ):
                raise TypeError(
                    "Each FAQ item must be a tuple containing a question "
                    "and an answer."
                )

            question = str(
                faq_item[0]
            ).strip()

            answer = str(
                faq_item[1]
            ).strip()

            if question and answer:
                normalized_faq_items.append(
                    (
                        question,
                        answer,
                    )
                )

        object.__setattr__(
            self,
            "faq_items",
            tuple(
                normalized_faq_items
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            dict(
                self.metadata
            ),
        )

    @property
    def word_count(self) -> int:
        """Return the approximate total article word count."""

        return len(
            self.to_plain_text().split()
        )

    @property
    def is_empty(self) -> bool:
        """Return whether the document has no meaningful article content."""

        return not any(
            [
                self.title,
                self.meta_description,
                self.introduction,
                self.sections,
                self.conclusion,
                self.call_to_action,
                self.faq_items,
            ]
        )

    @property
    def keywords(self) -> tuple[str, ...]:
        """Return the primary and secondary keywords together."""

        keyword_values: list[str] = []

        if self.primary_keyword:
            keyword_values.append(
                self.primary_keyword
            )

        keyword_values.extend(
            self.secondary_keywords
        )

        return tuple(
            dict.fromkeys(
                keyword_values
            )
        )

    def to_plain_text(self) -> str:
        """Convert the structured article into readable plain text.

        This format can be displayed in the editor or exported as a text file.
        """

        blocks: list[str] = []

        if self.title:
            blocks.append(
                self.title
            )

        if self.meta_description:
            blocks.append(
                "Meta description: "
                f"{self.meta_description}"
            )

        if self.introduction:
            blocks.append(
                self.introduction
            )

        for section in self.sections:
            blocks.append(
                "\n".join(
                    [
                        section.heading,
                        section.content,
                    ]
                )
            )

        if self.faq_items:
            faq_blocks = [
                "Frequently Asked Questions"
            ]

            for question, answer in self.faq_items:
                faq_blocks.append(
                    "\n".join(
                        [
                            question,
                            answer,
                        ]
                    )
                )

            blocks.append(
                "\n\n".join(
                    faq_blocks
                )
            )

        if self.conclusion:
            blocks.append(
                "\n".join(
                    [
                        "Conclusion",
                        self.conclusion,
                    ]
                )
            )

        if self.call_to_action:
            blocks.append(
                "\n".join(
                    [
                        "Call to Action",
                        self.call_to_action,
                    ]
                )
            )

        return "\n\n".join(
            block
            for block in blocks
            if block.strip()
        ).strip()

    def to_prompt_text(self) -> str:
        """Convert the article into clearly labelled AI prompt text."""

        blocks: list[str] = []

        if self.title:
            blocks.extend(
                [
                    "TITLE",
                    self.title,
                ]
            )

        if self.meta_description:
            blocks.extend(
                [
                    "META DESCRIPTION",
                    self.meta_description,
                ]
            )

        if self.introduction:
            blocks.extend(
                [
                    "INTRODUCTION",
                    self.introduction,
                ]
            )

        if self.sections:
            section_blocks = [
                section.to_prompt_text()
                for section in self.sections
            ]

            blocks.extend(
                [
                    "ARTICLE SECTIONS",
                    "\n\n".join(
                        section_blocks
                    ),
                ]
            )

        if self.faq_items:
            formatted_faq_items = []

            for question, answer in self.faq_items:
                formatted_faq_items.append(
                    "\n".join(
                        [
                            f"Question: {question}",
                            f"Answer: {answer}",
                        ]
                    )
                )

            blocks.extend(
                [
                    "FREQUENTLY ASKED QUESTIONS",
                    "\n\n".join(
                        formatted_faq_items
                    ),
                ]
            )

        if self.conclusion:
            blocks.extend(
                [
                    "CONCLUSION",
                    self.conclusion,
                ]
            )

        if self.call_to_action:
            blocks.extend(
                [
                    "CALL TO ACTION",
                    self.call_to_action,
                ]
            )

        context_lines: list[str] = []

        if self.content_type:
            context_lines.append(
                f"Content type: {self.content_type}"
            )

        if self.language:
            context_lines.append(
                f"Language: {self.language}"
            )

        if self.tone:
            context_lines.append(
                f"Tone: {self.tone}"
            )

        if self.target_audience:
            context_lines.append(
                "Target audience: "
                f"{self.target_audience}"
            )

        if self.primary_keyword:
            context_lines.append(
                "Primary keyword: "
                f"{self.primary_keyword}"
            )

        if self.secondary_keywords:
            context_lines.append(
                "Secondary keywords: "
                + ", ".join(
                    self.secondary_keywords
                )
            )

        if context_lines:
            blocks.extend(
                [
                    "ARTICLE CONTEXT",
                    "\n".join(
                        context_lines
                    ),
                ]
            )

        return "\n\n".join(
            block
            for block in blocks
            if block.strip()
        ).strip()