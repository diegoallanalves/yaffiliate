"""Parse Artificial Intelligence output into an ArticleDocument.

The Artificial Intelligence provider currently returns generated content as a
plain-text string. This service converts that response back into Filtrify's
structured ArticleDocument domain model.

AI means Artificial Intelligence.

SEO means Search Engine Optimization.
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from app.domain import ArticleDocument
from app.services.article_document_parser import (
    ArticleDocumentParser,
)


class ArticleDocumentResponseParser:
    """Convert an Artificial Intelligence response into an ArticleDocument.

    The parser performs three operations:

    1. Validate and normalize the provider response.
    2. Remove common response wrappers and Markdown formatting.
    3. Parse the cleaned article using ArticleDocumentParser.

    Existing article context can be supplied so that keywords, audience,
    language, tone, content type, and metadata are preserved when the model
    does not explicitly return those values.
    """

    _CODE_FENCE_PATTERN = re.compile(
        r"^\s*```(?:markdown|md|text|plaintext)?\s*\n"
        r"(?P<content>.*?)"
        r"\n```\s*$",
        flags=(
            re.IGNORECASE
            | re.DOTALL
        ),
    )

    _HEADING_PATTERN = re.compile(
        r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$"
    )

    _BOLD_LINE_PATTERN = re.compile(
        r"^\s*\*\*(.+?)\*\*\s*$"
    )

    _ITALIC_LINE_PATTERN = re.compile(
        r"^\s*__(.+?)__\s*$"
    )

    _HORIZONTAL_RULE_PATTERN = re.compile(
        r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$"
    )

    _INTRODUCTORY_PREFIX_PATTERNS = (
        re.compile(
            r"^\s*here(?:'s| is)\s+(?:the|your)\s+"
            r"(?:expanded|improved|rewritten|revised)\s+"
            r"(?:article|content)\s*:?\s*$",
            flags=re.IGNORECASE,
        ),
        re.compile(
            r"^\s*(?:expanded|improved|rewritten|revised)\s+"
            r"(?:article|content)\s*:?\s*$",
            flags=re.IGNORECASE,
        ),
        re.compile(
            r"^\s*final\s+(?:article|version|content)\s*:?\s*$",
            flags=re.IGNORECASE,
        ),
    )

    def __init__(
        self,
        parser: ArticleDocumentParser | None = None,
    ) -> None:
        """Initialize the response parser.

        Args:
            parser:
                Optional plain-text article parser. A default
                ArticleDocumentParser is created when one is not supplied.
        """

        self._parser = (
            parser
            or ArticleDocumentParser()
        )

    def parse(
        self,
        response_text: str,
        *,
        source_document: ArticleDocument | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ArticleDocument:
        """Parse an Artificial Intelligence response.

        Args:
            response_text:
                Text returned by the Artificial Intelligence provider.

            source_document:
                Optional original article. Its contextual fields are preserved
                when parsing the generated response.

            metadata:
                Additional metadata to attach to the parsed response.

        Returns:
            A structured ArticleDocument representing the generated article.

        Raises:
            TypeError:
                If the response is not a string or the source document is not
                an ArticleDocument.

            ValueError:
                If the response contains no meaningful article content.
        """

        if (
            source_document is not None
            and not isinstance(
                source_document,
                ArticleDocument,
            )
        ):
            raise TypeError(
                "source_document must be an ArticleDocument instance."
            )

        cleaned_response = self.clean_response(
            response_text
        )

        inherited_metadata = self._build_metadata(
            source_document=source_document,
            metadata=metadata,
        )

        parsed_document = self._parser.parse(
            cleaned_response,
            primary_keyword=(
                source_document.primary_keyword
                if source_document
                else ""
            ),
            secondary_keywords=(
                source_document.secondary_keywords
                if source_document
                else ()
            ),
            target_audience=(
                source_document.target_audience
                if source_document
                else ""
            ),
            tone=(
                source_document.tone
                if source_document
                else ""
            ),
            language=(
                source_document.language
                if source_document
                else "English"
            ),
            content_type=(
                source_document.content_type
                if source_document
                else "article"
            ),
            metadata=inherited_metadata,
        )

        return self._preserve_missing_fields(
            parsed_document=parsed_document,
            source_document=source_document,
        )

    def clean_response(
        self,
        response_text: str,
    ) -> str:
        """Normalize provider output before article parsing.

        This method removes:

        - surrounding Markdown code fences;
        - introductory provider commentary;
        - Markdown heading symbols;
        - bold formatting around complete heading lines;
        - horizontal divider lines;
        - excessive blank lines.

        Inline emphasis inside normal paragraphs is preserved for the later
        output-formatting stage.

        Args:
            response_text:
                Raw provider response.

        Returns:
            Cleaned article text suitable for ArticleDocumentParser.
        """

        normalized_response = self._validate_response(
            response_text
        )

        normalized_response = self._remove_code_fence(
            normalized_response
        )

        lines = normalized_response.splitlines()

        lines = self._remove_introductory_lines(
            lines
        )

        cleaned_lines: list[str] = []

        for raw_line in lines:
            cleaned_line = self._clean_line(
                raw_line
            )

            if cleaned_line is None:
                continue

            cleaned_lines.append(
                cleaned_line
            )

        cleaned_response = self._normalize_blank_lines(
            cleaned_lines
        )

        if not cleaned_response:
            raise ValueError(
                "The Artificial Intelligence response does not contain "
                "meaningful article content."
            )

        return cleaned_response

    @staticmethod
    def _validate_response(
        response_text: str,
    ) -> str:
        """Validate and normalize raw response text."""

        if not isinstance(
            response_text,
            str,
        ):
            raise TypeError(
                "Artificial Intelligence response text must be a string."
            )

        normalized_response = (
            response_text
            .replace(
                "\r\n",
                "\n",
            )
            .replace(
                "\r",
                "\n",
            )
            .strip()
        )

        if not normalized_response:
            raise ValueError(
                "Artificial Intelligence response text cannot be empty."
            )

        return normalized_response

    def _remove_code_fence(
        self,
        response_text: str,
    ) -> str:
        """Remove one surrounding Markdown code fence."""

        code_fence_match = (
            self._CODE_FENCE_PATTERN.match(
                response_text
            )
        )

        if not code_fence_match:
            return response_text

        return (
            code_fence_match.group(
                "content"
            ).strip()
        )

    def _remove_introductory_lines(
        self,
        lines: list[str],
    ) -> list[str]:
        """Remove common provider commentary from the response beginning."""

        working_lines = list(
            lines
        )

        while (
            working_lines
            and not working_lines[0].strip()
        ):
            working_lines.pop(0)

        if not working_lines:
            return []

        first_line = working_lines[0].strip()

        if any(
            pattern.match(
                first_line
            )
            for pattern in self._INTRODUCTORY_PREFIX_PATTERNS
        ):
            working_lines.pop(0)

        while (
            working_lines
            and not working_lines[0].strip()
        ):
            working_lines.pop(0)

        return working_lines

    def _clean_line(
        self,
        raw_line: str,
    ) -> str | None:
        """Clean one provider-response line."""

        stripped_line = raw_line.strip()

        if not stripped_line:
            return ""

        if self._HORIZONTAL_RULE_PATTERN.match(
            stripped_line
        ):
            return None

        heading_match = (
            self._HEADING_PATTERN.match(
                stripped_line
            )
        )

        if heading_match:
            return self._strip_wrapping_emphasis(
                heading_match.group(1)
            )

        bold_line_match = (
            self._BOLD_LINE_PATTERN.match(
                stripped_line
            )
        )

        if bold_line_match:
            return self._strip_wrapping_emphasis(
                bold_line_match.group(1)
            )

        italic_line_match = (
            self._ITALIC_LINE_PATTERN.match(
                stripped_line
            )
        )

        if italic_line_match:
            return self._strip_wrapping_emphasis(
                italic_line_match.group(1)
            )

        return stripped_line

    @staticmethod
    def _strip_wrapping_emphasis(
        value: str,
    ) -> str:
        """Remove emphasis markers wrapped around a complete line."""

        cleaned_value = value.strip()

        emphasis_pairs = (
            (
                "**",
                "**",
            ),
            (
                "__",
                "__",
            ),
            (
                "*",
                "*",
            ),
            (
                "_",
                "_",
            ),
        )

        for opening_marker, closing_marker in emphasis_pairs:
            if (
                cleaned_value.startswith(
                    opening_marker
                )
                and cleaned_value.endswith(
                    closing_marker
                )
                and len(cleaned_value)
                > len(opening_marker)
                + len(closing_marker)
            ):
                cleaned_value = cleaned_value[
                    len(opening_marker):
                    -len(closing_marker)
                ].strip()

        return cleaned_value

    @staticmethod
    def _normalize_blank_lines(
        lines: list[str],
    ) -> str:
        """Collapse repeated blank lines while preserving paragraphs."""

        normalized_lines: list[str] = []
        previous_line_was_blank = False

        for line in lines:
            cleaned_line = line.rstrip()

            if not cleaned_line:
                if (
                    normalized_lines
                    and not previous_line_was_blank
                ):
                    normalized_lines.append(
                        ""
                    )

                previous_line_was_blank = True
                continue

            normalized_lines.append(
                cleaned_line
            )

            previous_line_was_blank = False

        while (
            normalized_lines
            and not normalized_lines[-1]
        ):
            normalized_lines.pop()

        return "\n".join(
            normalized_lines
        ).strip()

    @staticmethod
    def _build_metadata(
        *,
        source_document: ArticleDocument | None,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Combine source and response metadata."""

        combined_metadata: dict[str, Any] = {}

        if source_document is not None:
            combined_metadata.update(
                source_document.metadata
            )

        combined_metadata.update(
            {
                "source": "ai_response",
                "parsed_response": True,
            }
        )

        if metadata:
            combined_metadata.update(
                metadata
            )

        return combined_metadata

    @staticmethod
    def _preserve_missing_fields(
        *,
        parsed_document: ArticleDocument,
        source_document: ArticleDocument | None,
    ) -> ArticleDocument:
        """Preserve important source fields omitted by the model.

        The generated response remains the source of truth for article text.
        Only missing structured values are inherited.
        """

        if source_document is None:
            return parsed_document

        return replace(
            parsed_document,
            title=(
                parsed_document.title
                or source_document.title
            ),
            meta_description=(
                parsed_document.meta_description
                or source_document.meta_description
            ),
            introduction=(
                parsed_document.introduction
                or source_document.introduction
            ),
            conclusion=(
                parsed_document.conclusion
                or source_document.conclusion
            ),
            call_to_action=(
                parsed_document.call_to_action
                or source_document.call_to_action
            ),
            primary_keyword=(
                parsed_document.primary_keyword
                or source_document.primary_keyword
            ),
            secondary_keywords=(
                parsed_document.secondary_keywords
                or source_document.secondary_keywords
            ),
            target_audience=(
                parsed_document.target_audience
                or source_document.target_audience
            ),
            tone=(
                parsed_document.tone
                or source_document.tone
            ),
            language=(
                parsed_document.language
                or source_document.language
            ),
            content_type=(
                parsed_document.content_type
                or source_document.content_type
            ),
        )