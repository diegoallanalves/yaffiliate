"""Parse plain article text into a structured ArticleDocument.

The Content Studio currently stores edited content as one plain-text string.
This parser identifies common article elements such as:

- title
- meta description
- introduction
- body sections
- frequently asked questions
- conclusion
- call to action

AI means Artificial Intelligence.

CTA means Call to Action.

FAQ means Frequently Asked Questions.

SEO means Search Engine Optimization.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.domain import (
    ArticleDocument,
    ArticleSection,
)


@dataclass(frozen=True, slots=True)
class _ParsedBlock:
    """Represent one temporary heading-and-content block."""

    heading: str
    content: str
    position: int


class ArticleDocumentParser:
    """Convert plain editor content into a structured article document."""

    _META_DESCRIPTION_PATTERN = re.compile(
        r"^\s*meta\s*(?:description)?\s*:\s*(.+)$",
        flags=re.IGNORECASE,
    )

    _MARKDOWN_HEADING_PATTERN = re.compile(
        r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$"
    )

    _NUMBERED_HEADING_PATTERN = re.compile(
        r"^\s*(?:\d+[\.\)]|[IVXLCDM]+[\.\)])\s+(.+?)\s*$",
        flags=re.IGNORECASE,
    )

    _BULLET_PATTERN = re.compile(
        r"^\s*[-*+•]\s+"
    )

    _FAQ_QUESTION_PATTERN = re.compile(
        r"^\s*(?:q(?:uestion)?\s*[:\-]\s*)?(.+\?)\s*$",
        flags=re.IGNORECASE,
    )

    _CONCLUSION_HEADINGS = {
        "conclusion",
        "final conclusion",
        "final thoughts",
        "final verdict",
        "our verdict",
        "verdict",
        "summary",
        "closing thoughts",
        "is it worth it",
        "is this course worth it",
        "should you buy it",
        "should you join",
    }

    _CTA_HEADINGS = {
        "call to action",
        "cta",
        "next steps",
        "get started",
        "start today",
        "ready to get started",
        "join now",
        "buy now",
        "enrol now",
        "enroll now",
        "learn more",
        "take action",
    }

    _FAQ_HEADINGS = {
        "faq",
        "faqs",
        "frequently asked questions",
        "common questions",
        "questions and answers",
        "questions & answers",
    }

    _INTRODUCTION_HEADINGS = {
        "introduction",
        "overview",
        "article introduction",
    }

    def parse(
        self,
        content: str,
        *,
        primary_keyword: str = "",
        secondary_keywords: tuple[str, ...] = (),
        target_audience: str = "",
        tone: str = "",
        language: str = "English",
        content_type: str = "article",
        metadata: dict[str, Any] | None = None,
    ) -> ArticleDocument:
        """Parse plain text into an ArticleDocument.

        Args:
            content:
                Complete article text from the editor.

            primary_keyword:
                Main Search Engine Optimization keyword.

            secondary_keywords:
                Additional Search Engine Optimization keywords.

            target_audience:
                Intended reader group.

            tone:
                Desired writing style.

            language:
                Main article language.

            content_type:
                Article category, such as SEO article, review, or comparison.

            metadata:
                Optional additional values associated with the document.

        Returns:
            A structured ArticleDocument.

        Raises:
            TypeError:
                If content is not a string.

            ValueError:
                If content contains no meaningful text.
        """

        cleaned_content = self._normalize_content(
            content
        )

        lines = cleaned_content.splitlines()

        title, remaining_lines = self._extract_title(
            lines
        )

        meta_description, remaining_lines = (
            self._extract_meta_description(
                remaining_lines
            )
        )

        preamble_lines, parsed_blocks = self._split_blocks(
            remaining_lines
        )

        introduction = self._join_lines(
            preamble_lines
        )

        body_sections: list[ArticleSection] = []
        faq_items: list[tuple[str, str]] = []
        conclusion = ""
        call_to_action = ""

        for parsed_block in parsed_blocks:
            normalized_heading = self._normalize_heading(
                parsed_block.heading
            )

            if normalized_heading in self._INTRODUCTION_HEADINGS:
                introduction = self._merge_text(
                    introduction,
                    parsed_block.content,
                )
                continue

            if self._is_faq_heading(
                normalized_heading
            ):
                faq_items.extend(
                    self._parse_faq_items(
                        parsed_block.content
                    )
                )
                continue

            if self._is_conclusion_heading(
                normalized_heading
            ):
                conclusion = self._merge_text(
                    conclusion,
                    parsed_block.content,
                )
                continue

            if self._is_cta_heading(
                normalized_heading
            ):
                call_to_action = self._merge_text(
                    call_to_action,
                    parsed_block.content,
                )
                continue

            body_sections.append(
                ArticleSection(
                    heading=parsed_block.heading,
                    content=parsed_block.content,
                    section_type=self._infer_section_type(
                        normalized_heading
                    ),
                    position=len(body_sections),
                )
            )

        return ArticleDocument(
            title=title,
            meta_description=meta_description,
            introduction=introduction,
            sections=tuple(
                body_sections
            ),
            conclusion=conclusion,
            call_to_action=call_to_action,
            primary_keyword=primary_keyword,
            secondary_keywords=secondary_keywords,
            target_audience=target_audience,
            tone=tone,
            language=language,
            content_type=content_type,
            faq_items=tuple(
                faq_items
            ),
            metadata=metadata or {},
        )

    def _normalize_content(
        self,
        content: str,
    ) -> str:
        """Validate and normalize the supplied editor content."""

        if not isinstance(
            content,
            str,
        ):
            raise TypeError(
                "Article content must be a string."
            )

        normalized_content = (
            content.replace(
                "\r\n",
                "\n",
            )
            .replace(
                "\r",
                "\n",
            )
            .strip()
        )

        if not normalized_content:
            raise ValueError(
                "Article content cannot be empty."
            )

        return normalized_content

    def _extract_title(
        self,
        lines: list[str],
    ) -> tuple[str, list[str]]:
        """Extract the first meaningful line as the title."""

        working_lines = list(
            lines
        )

        while (
            working_lines
            and not working_lines[0].strip()
        ):
            working_lines.pop(0)

        if not working_lines:
            raise ValueError(
                "Article content does not contain a title."
            )

        first_line = working_lines.pop(0).strip()

        markdown_match = (
            self._MARKDOWN_HEADING_PATTERN.match(
                first_line
            )
        )

        if markdown_match:
            title = markdown_match.group(1).strip()
        else:
            title = first_line

        return (
            title,
            working_lines,
        )

    def _extract_meta_description(
        self,
        lines: list[str],
    ) -> tuple[str, list[str]]:
        """Extract a labelled meta description near the article beginning."""

        working_lines = list(
            lines
        )

        meta_description = ""

        search_limit = min(
            len(working_lines),
            6,
        )

        for line_index in range(
            search_limit
        ):
            current_line = (
                working_lines[line_index].strip()
            )

            if not current_line:
                continue

            meta_match = (
                self._META_DESCRIPTION_PATTERN.match(
                    current_line
                )
            )

            if not meta_match:
                continue

            meta_description = (
                meta_match.group(1).strip()
            )

            del working_lines[
                line_index
            ]

            break

        return (
            meta_description,
            working_lines,
        )

    def _split_blocks(
        self,
        lines: list[str],
    ) -> tuple[list[str], list[_ParsedBlock]]:
        """Separate introductory text from heading-based article blocks."""

        preamble_lines: list[str] = []
        parsed_blocks: list[_ParsedBlock] = []

        current_heading = ""
        current_content_lines: list[str] = []

        for line_index, raw_line in enumerate(
            lines
        ):
            stripped_line = raw_line.strip()

            if self._is_heading(
                stripped_line,
                lines=lines,
                line_index=line_index,
            ):
                if current_heading:
                    self._append_block(
                        parsed_blocks,
                        heading=current_heading,
                        content_lines=current_content_lines,
                    )
                elif current_content_lines:
                    preamble_lines.extend(
                        current_content_lines
                    )

                current_heading = (
                    self._clean_heading(
                        stripped_line
                    )
                )

                current_content_lines = []
                continue

            current_content_lines.append(
                raw_line
            )

        if current_heading:
            self._append_block(
                parsed_blocks,
                heading=current_heading,
                content_lines=current_content_lines,
            )
        elif current_content_lines:
            preamble_lines.extend(
                current_content_lines
            )

        return (
            preamble_lines,
            parsed_blocks,
        )

    def _append_block(
        self,
        parsed_blocks: list[_ParsedBlock],
        *,
        heading: str,
        content_lines: list[str],
    ) -> None:
        """Append a non-empty temporary article block."""

        content = self._join_lines(
            content_lines
        )

        if not heading or not content:
            return

        parsed_blocks.append(
            _ParsedBlock(
                heading=heading,
                content=content,
                position=len(
                    parsed_blocks
                ),
            )
        )

    def _is_heading(
        self,
        line: str,
        *,
        lines: list[str],
        line_index: int,
    ) -> bool:
        """Determine whether a line is probably an article heading."""

        if not line:
            return False

        if self._META_DESCRIPTION_PATTERN.match(
            line
        ):
            return False

        if self._BULLET_PATTERN.match(
            line
        ):
            return False

        if self._MARKDOWN_HEADING_PATTERN.match(
            line
        ):
            return True

        if self._NUMBERED_HEADING_PATTERN.match(
            line
        ):
            return True

        normalized_heading = self._normalize_heading(
            line
        )

        if (
            normalized_heading
            in self._INTRODUCTION_HEADINGS
            | self._FAQ_HEADINGS
            | self._CONCLUSION_HEADINGS
            | self._CTA_HEADINGS
        ):
            return True

        if len(
            line
        ) > 100:
            return False

        if line.endswith(
            (
                ".",
                ",",
                ";",
                ":",
                "!",
            )
        ):
            return False

        word_count = len(
            line.split()
        )

        if word_count < 1 or word_count > 14:
            return False

        if line.endswith(
            "?"
        ):
            return self._has_content_after_line(
                lines,
                line_index,
            )

        if self._looks_like_title_case(
            line
        ):
            return self._has_content_after_line(
                lines,
                line_index,
            )

        if self._is_surrounded_by_blank_lines(
            lines,
            line_index,
        ):
            return self._has_content_after_line(
                lines,
                line_index,
            )

        return False

    @staticmethod
    def _has_content_after_line(
        lines: list[str],
        line_index: int,
    ) -> bool:
        """Return whether meaningful content follows a possible heading."""

        for next_line in lines[
            line_index + 1:
        ]:
            if next_line.strip():
                return True

        return False

    @staticmethod
    def _is_surrounded_by_blank_lines(
        lines: list[str],
        line_index: int,
    ) -> bool:
        """Return whether a line is separated like a heading."""

        previous_is_blank = (
            line_index == 0
            or not lines[
                line_index - 1
            ].strip()
        )

        next_is_blank = (
            line_index >= len(
                lines
            ) - 1
            or not lines[
                line_index + 1
            ].strip()
        )

        return (
            previous_is_blank
            and next_is_blank
        )

    @staticmethod
    def _looks_like_title_case(
        line: str,
    ) -> bool:
        """Return whether a short line resembles a heading."""

        meaningful_words = [
            word
            for word in re.findall(
                r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+",
                line,
            )
            if word
        ]

        if not meaningful_words:
            return False

        capitalized_words = sum(
            1
            for word in meaningful_words
            if (
                word[0].isupper()
                or word.isupper()
                or word.isdigit()
            )
        )

        capitalization_ratio = (
            capitalized_words
            / len(
                meaningful_words
            )
        )

        return capitalization_ratio >= 0.5

    def _clean_heading(
        self,
        heading: str,
    ) -> str:
        """Remove Markdown and numbering syntax from a heading."""

        markdown_match = (
            self._MARKDOWN_HEADING_PATTERN.match(
                heading
            )
        )

        if markdown_match:
            return (
                markdown_match.group(1).strip()
            )

        numbered_match = (
            self._NUMBERED_HEADING_PATTERN.match(
                heading
            )
        )

        if numbered_match:
            return (
                numbered_match.group(1).strip()
            )

        return heading.strip().rstrip(
            ":"
        )

    @staticmethod
    def _normalize_heading(
        heading: str,
    ) -> str:
        """Normalize a heading for classification."""

        normalized_heading = re.sub(
            r"\s+",
            " ",
            heading.strip().lower(),
        )

        normalized_heading = (
            normalized_heading.rstrip(
                "?:.!-"
            )
        )

        return normalized_heading

    def _is_faq_heading(
        self,
        normalized_heading: str,
    ) -> bool:
        """Return whether a heading introduces an FAQ section."""

        return (
            normalized_heading
            in self._FAQ_HEADINGS
            or "frequently asked question"
            in normalized_heading
        )

    def _is_conclusion_heading(
        self,
        normalized_heading: str,
    ) -> bool:
        """Return whether a heading represents the article conclusion."""

        return (
            normalized_heading
            in self._CONCLUSION_HEADINGS
            or normalized_heading.startswith(
                "final verdict"
            )
            or normalized_heading.startswith(
                "conclusion"
            )
        )

    def _is_cta_heading(
        self,
        normalized_heading: str,
    ) -> bool:
        """Return whether a heading represents a call to action."""

        return (
            normalized_heading
            in self._CTA_HEADINGS
            or normalized_heading.startswith(
                "ready to"
            )
        )

    @staticmethod
    def _infer_section_type(
        normalized_heading: str,
    ) -> str:
        """Infer the purpose of a normal body section."""

        if any(
            keyword in normalized_heading
            for keyword in (
                "benefit",
                "advantage",
                "pros",
                "strength",
            )
        ):
            return "benefits"

        if any(
            keyword in normalized_heading
            for keyword in (
                "risk",
                "disadvantage",
                "cons",
                "limitation",
                "drawback",
            )
        ):
            return "risks"

        if any(
            keyword in normalized_heading
            for keyword in (
                "price",
                "cost",
                "pricing",
                "commission",
            )
        ):
            return "pricing"

        if any(
            keyword in normalized_heading
            for keyword in (
                "feature",
                "what is",
                "overview",
            )
        ):
            return "overview"

        if any(
            keyword in normalized_heading
            for keyword in (
                "who is",
                "audience",
                "for whom",
                "ideal for",
            )
        ):
            return "audience"

        if any(
            keyword in normalized_heading
            for keyword in (
                "comparison",
                "versus",
                " vs ",
                "alternative",
            )
        ):
            return "comparison"

        return "body"

    def _parse_faq_items(
        self,
        content: str,
    ) -> list[tuple[str, str]]:
        """Extract question-and-answer pairs from an FAQ section."""

        lines = content.splitlines()

        faq_items: list[
            tuple[str, str]
        ] = []

        current_question = ""
        current_answer_lines: list[str] = []

        for raw_line in lines:
            stripped_line = raw_line.strip()

            if not stripped_line:
                if current_answer_lines:
                    current_answer_lines.append(
                        ""
                    )
                continue

            question_match = (
                self._FAQ_QUESTION_PATTERN.match(
                    stripped_line
                )
            )

            if question_match:
                if current_question:
                    answer = self._join_lines(
                        current_answer_lines
                    )

                    if answer:
                        faq_items.append(
                            (
                                current_question,
                                answer,
                            )
                        )

                current_question = (
                    question_match.group(1).strip()
                )

                current_answer_lines = []
                continue

            if current_question:
                cleaned_answer_line = re.sub(
                    r"^\s*a(?:nswer)?\s*[:\-]\s*",
                    "",
                    stripped_line,
                    flags=re.IGNORECASE,
                )

                current_answer_lines.append(
                    cleaned_answer_line
                )

        if current_question:
            answer = self._join_lines(
                current_answer_lines
            )

            if answer:
                faq_items.append(
                    (
                        current_question,
                        answer,
                    )
                )

        return faq_items

    @staticmethod
    def _join_lines(
        lines: list[str],
    ) -> str:
        """Join lines while preserving meaningful paragraph breaks."""

        paragraphs: list[str] = []
        current_paragraph_lines: list[str] = []

        for raw_line in lines:
            stripped_line = raw_line.strip()

            if stripped_line:
                current_paragraph_lines.append(
                    stripped_line
                )
                continue

            if current_paragraph_lines:
                paragraphs.append(
                    " ".join(
                        current_paragraph_lines
                    )
                )

                current_paragraph_lines = []

        if current_paragraph_lines:
            paragraphs.append(
                " ".join(
                    current_paragraph_lines
                )
            )

        return "\n\n".join(
            paragraphs
        ).strip()

    @staticmethod
    def _merge_text(
        existing_text: str,
        new_text: str,
    ) -> str:
        """Combine two non-empty content values safely."""

        cleaned_existing_text = (
            existing_text.strip()
        )

        cleaned_new_text = (
            new_text.strip()
        )

        if not cleaned_existing_text:
            return cleaned_new_text

        if not cleaned_new_text:
            return cleaned_existing_text

        return (
            f"{cleaned_existing_text}\n\n"
            f"{cleaned_new_text}"
        )