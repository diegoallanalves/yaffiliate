"""Format ArticleDocument objects for editors and export destinations.

The formatter keeps content structure separate from presentation format.

Supported output formats:

- plain text for the Filtrify editor;
- Markdown for Markdown-compatible destinations;
- HTML for web pages and future landing-page integrations.

HTML means HyperText Markup Language.

FAQ means Frequently Asked Questions.

CTA means Call to Action.
"""

from __future__ import annotations

from enum import Enum
from html import escape

from app.domain import (
    ArticleDocument,
    ArticleSection,
)


class ArticleOutputFormat(str, Enum):
    """Represent supported article output formats."""

    PLAIN_TEXT = "plain_text"
    MARKDOWN = "markdown"
    HTML = "html"


class ArticleDocumentOutputFormatter:
    """Convert a structured ArticleDocument into presentation-ready content."""

    def format(
        self,
        document: ArticleDocument,
        *,
        output_format: ArticleOutputFormat | str = (
            ArticleOutputFormat.PLAIN_TEXT
        ),
    ) -> str:
        """Format an ArticleDocument.

        Args:
            document:
                Structured article to format.

            output_format:
                Desired output format. Supported values are plain_text,
                markdown, and html.

        Returns:
            Formatted article content.

        Raises:
            TypeError:
                If document is not an ArticleDocument.

            ValueError:
                If the requested output format is unsupported.
        """

        self._validate_document(
            document
        )

        normalized_output_format = (
            self._normalize_output_format(
                output_format
            )
        )

        if (
            normalized_output_format
            == ArticleOutputFormat.PLAIN_TEXT
        ):
            return self.to_plain_text(
                document
            )

        if (
            normalized_output_format
            == ArticleOutputFormat.MARKDOWN
        ):
            return self.to_markdown(
                document
            )

        if (
            normalized_output_format
            == ArticleOutputFormat.HTML
        ):
            return self.to_html(
                document
            )

        raise ValueError(
            "Unsupported article output format: "
            f"{normalized_output_format}"
        )

    def to_plain_text(
        self,
        document: ArticleDocument,
    ) -> str:
        """Format a document as clean editor-friendly plain text.

        Markdown syntax is not included. This is the preferred format for the
        Filtrify structured editor and accepted Artificial Intelligence
        suggestions.
        """

        self._validate_document(
            document
        )

        blocks: list[str] = []

        if document.title:
            blocks.append(
                document.title
            )

        if document.meta_description:
            blocks.append(
                "\n".join(
                    [
                        "Meta Description",
                        document.meta_description,
                    ]
                )
            )

        if document.introduction:
            blocks.append(
                "\n".join(
                    [
                        "Introduction",
                        document.introduction,
                    ]
                )
            )

        for section in document.sections:
            blocks.append(
                self._section_to_plain_text(
                    section
                )
            )

        if document.faq_items:
            faq_blocks: list[str] = [
                "Frequently Asked Questions"
            ]

            for question, answer in document.faq_items:
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

        if document.conclusion:
            blocks.append(
                "\n".join(
                    [
                        "Conclusion",
                        document.conclusion,
                    ]
                )
            )

        if document.call_to_action:
            blocks.append(
                "\n".join(
                    [
                        "Call to Action",
                        document.call_to_action,
                    ]
                )
            )

        return self._join_blocks(
            blocks
        )

    def to_markdown(
        self,
        document: ArticleDocument,
    ) -> str:
        """Format a document as Markdown."""

        self._validate_document(
            document
        )

        blocks: list[str] = []

        if document.title:
            blocks.append(
                f"# {document.title}"
            )

        if document.meta_description:
            blocks.append(
                "\n".join(
                    [
                        "## Meta Description",
                        document.meta_description,
                    ]
                )
            )

        if document.introduction:
            blocks.append(
                "\n".join(
                    [
                        "## Introduction",
                        document.introduction,
                    ]
                )
            )

        for section in document.sections:
            blocks.append(
                self._section_to_markdown(
                    section
                )
            )

        if document.faq_items:
            faq_blocks: list[str] = [
                "## Frequently Asked Questions"
            ]

            for question, answer in document.faq_items:
                faq_blocks.append(
                    "\n".join(
                        [
                            f"### {question}",
                            answer,
                        ]
                    )
                )

            blocks.append(
                "\n\n".join(
                    faq_blocks
                )
            )

        if document.conclusion:
            blocks.append(
                "\n".join(
                    [
                        "## Conclusion",
                        document.conclusion,
                    ]
                )
            )

        if document.call_to_action:
            blocks.append(
                "\n".join(
                    [
                        "## Call to Action",
                        document.call_to_action,
                    ]
                )
            )

        return self._join_blocks(
            blocks
        )

    def to_html(
        self,
        document: ArticleDocument,
    ) -> str:
        """Format a document as semantic HTML."""

        self._validate_document(
            document
        )

        html_blocks: list[str] = [
            "<article>"
        ]

        if document.title:
            html_blocks.append(
                f"  <h1>{escape(document.title)}</h1>"
            )

        if document.meta_description:
            html_blocks.extend(
                [
                    '  <section data-section-type="meta-description">',
                    "    <h2>Meta Description</h2>",
                    (
                        "    <p>"
                        f"{escape(document.meta_description)}"
                        "</p>"
                    ),
                    "  </section>",
                ]
            )

        if document.introduction:
            html_blocks.extend(
                [
                    '  <section data-section-type="introduction">',
                    "    <h2>Introduction</h2>",
                    self._paragraphs_to_html(
                        document.introduction,
                        indent="    ",
                    ),
                    "  </section>",
                ]
            )

        for section in document.sections:
            html_blocks.extend(
                self._section_to_html(
                    section
                )
            )

        if document.faq_items:
            html_blocks.extend(
                [
                    '  <section data-section-type="faq">',
                    "    <h2>Frequently Asked Questions</h2>",
                ]
            )

            for question, answer in document.faq_items:
                html_blocks.extend(
                    [
                        "    <article>",
                        f"      <h3>{escape(question)}</h3>",
                        self._paragraphs_to_html(
                            answer,
                            indent="      ",
                        ),
                        "    </article>",
                    ]
                )

            html_blocks.append(
                "  </section>"
            )

        if document.conclusion:
            html_blocks.extend(
                [
                    '  <section data-section-type="conclusion">',
                    "    <h2>Conclusion</h2>",
                    self._paragraphs_to_html(
                        document.conclusion,
                        indent="    ",
                    ),
                    "  </section>",
                ]
            )

        if document.call_to_action:
            html_blocks.extend(
                [
                    '  <section data-section-type="call-to-action">',
                    "    <h2>Call to Action</h2>",
                    self._paragraphs_to_html(
                        document.call_to_action,
                        indent="    ",
                    ),
                    "  </section>",
                ]
            )

        html_blocks.append(
            "</article>"
        )

        return "\n".join(
            html_blocks
        ).strip()

    @staticmethod
    def _section_to_plain_text(
        section: ArticleSection,
    ) -> str:
        """Format one section as plain text."""

        return "\n".join(
            [
                section.heading,
                section.content,
            ]
        )

    @staticmethod
    def _section_to_markdown(
        section: ArticleSection,
    ) -> str:
        """Format one section as Markdown."""

        return "\n".join(
            [
                f"## {section.heading}",
                section.content,
            ]
        )

    def _section_to_html(
        self,
        section: ArticleSection,
    ) -> list[str]:
        """Format one section as HTML lines."""

        safe_section_type = escape(
            section.section_type,
            quote=True,
        )

        return [
            (
                "  <section "
                f'data-section-type="{safe_section_type}">'
            ),
            f"    <h2>{escape(section.heading)}</h2>",
            self._paragraphs_to_html(
                section.content,
                indent="    ",
            ),
            "  </section>",
        ]

    @staticmethod
    def _paragraphs_to_html(
        content: str,
        *,
        indent: str,
    ) -> str:
        """Convert text paragraphs into escaped HTML paragraphs."""

        paragraphs = [
            paragraph.strip()
            for paragraph in content.split(
                "\n\n"
            )
            if paragraph.strip()
        ]

        if not paragraphs:
            return (
                f"{indent}<p></p>"
            )

        html_paragraphs = []

        for paragraph in paragraphs:
            normalized_paragraph = " ".join(
                line.strip()
                for line in paragraph.splitlines()
                if line.strip()
            )

            html_paragraphs.append(
                f"{indent}<p>{escape(normalized_paragraph)}</p>"
            )

        return "\n".join(
            html_paragraphs
        )

    @staticmethod
    def _join_blocks(
        blocks: list[str],
    ) -> str:
        """Join non-empty article blocks with consistent spacing."""

        return "\n\n".join(
            block.strip()
            for block in blocks
            if block.strip()
        ).strip()

    @staticmethod
    def _validate_document(
        document: ArticleDocument,
    ) -> None:
        """Validate the document supplied to the formatter."""

        if not isinstance(
            document,
            ArticleDocument,
        ):
            raise TypeError(
                "The formatter requires an ArticleDocument instance."
            )

    @staticmethod
    def _normalize_output_format(
        output_format: ArticleOutputFormat | str,
    ) -> ArticleOutputFormat:
        """Normalize a string or enumeration output-format value."""

        if isinstance(
            output_format,
            ArticleOutputFormat,
        ):
            return output_format

        if not isinstance(
            output_format,
            str,
        ):
            raise TypeError(
                "Article output format must be a string or "
                "ArticleOutputFormat value."
            )

        normalized_value = (
            output_format.strip().lower()
        )

        try:
            return ArticleOutputFormat(
                normalized_value
            )
        except ValueError as error:
            supported_formats = ", ".join(
                output_format_item.value
                for output_format_item
                in ArticleOutputFormat
            )

            raise ValueError(
                "Unsupported article output format. "
                f"Supported formats: {supported_formats}."
            ) from error