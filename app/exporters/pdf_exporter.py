from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from app.exporters.content_exporter import (
    ExportedContent,
)


class PDFExporter:
    """
    Export generated content as a PDF document.

    PDF = Portable Document Format.

    PDF preserves the document layout across different
    devices and operating systems.
    """

    @property
    def format_key(self) -> str:
        """
        Return the internal export-format identifier.
        """
        return "pdf"

    @property
    def display_name(self) -> str:
        """
        Return the format name shown to users.
        """
        return "PDF"

    def export(
        self,
        *,
        title: str,
        content: str,
        filename_stem: str,
    ) -> ExportedContent:
        """
        Convert generated content into a PDF document.
        """
        output_buffer = BytesIO()

        document = SimpleDocTemplate(
            output_buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            title=title.strip(),
            author="Filtrify",
        )

        styles = self._build_styles()

        document_elements = self._build_document_elements(
            title=title,
            content=content,
            styles=styles,
        )

        document.build(
            document_elements
        )

        output_buffer.seek(0)

        return ExportedContent(
            filename=f"{filename_stem}.pdf",
            data=output_buffer.getvalue(),
            mime_type="application/pdf",
        )

    @staticmethod
    def _build_styles() -> dict[str, ParagraphStyle]:
        """
        Create the paragraph styles used in the PDF.
        """
        sample_styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="FiltrifyTitle",
            parent=sample_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=25,
            alignment=TA_CENTER,
            spaceAfter=16,
        )

        heading_style = ParagraphStyle(
            name="FiltrifyHeading",
            parent=sample_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            spaceBefore=10,
            spaceAfter=8,
        )

        body_style = ParagraphStyle(
            name="FiltrifyBody",
            parent=sample_styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            spaceAfter=8,
        )

        metadata_style = ParagraphStyle(
            name="FiltrifyMetadata",
            parent=body_style,
            fontName="Helvetica-Oblique",
            fontSize=9.5,
            leading=14,
            spaceAfter=12,
        )

        bullet_style = ParagraphStyle(
            name="FiltrifyBullet",
            parent=body_style,
            leftIndent=0,
            firstLineIndent=0,
            spaceAfter=4,
        )

        return {
            "title": title_style,
            "heading": heading_style,
            "body": body_style,
            "metadata": metadata_style,
            "bullet": bullet_style,
        }

    def _build_document_elements(
        self,
        *,
        title: str,
        content: str,
        styles: dict[str, ParagraphStyle],
    ) -> list[object]:
        """
        Convert plain text into PDF document elements.
        """
        elements: list[object] = []

        cleaned_title = title.strip()

        if cleaned_title:
            elements.append(
                Paragraph(
                    escape(cleaned_title),
                    styles["title"],
                )
            )

            elements.append(
                Spacer(
                    1,
                    4 * mm,
                )
            )

        content_lines = content.splitlines()

        bullet_items: list[str] = []

        for line_index, raw_line in enumerate(
            content_lines
        ):
            cleaned_line = raw_line.strip()

            if not cleaned_line:
                self._append_bullet_list(
                    elements=elements,
                    bullet_items=bullet_items,
                    styles=styles,
                )

                bullet_items.clear()

                elements.append(
                    Spacer(
                        1,
                        3 * mm,
                    )
                )

                continue

            if cleaned_line.startswith("- "):
                bullet_items.append(
                    cleaned_line[2:].strip()
                )
                continue

            self._append_bullet_list(
                elements=elements,
                bullet_items=bullet_items,
                styles=styles,
            )

            bullet_items.clear()

            if (
                line_index == 0
                and cleaned_title
                and cleaned_line == cleaned_title
            ):
                continue

            if cleaned_line.lower().startswith(
                "meta description:"
            ):
                elements.append(
                    Paragraph(
                        escape(cleaned_line),
                        styles["metadata"],
                    )
                )
                continue

            if self._looks_like_heading(
                cleaned_line
            ):
                elements.append(
                    Paragraph(
                        escape(cleaned_line),
                        styles["heading"],
                    )
                )
                continue

            elements.append(
                Paragraph(
                    escape(cleaned_line),
                    styles["body"],
                )
            )

        self._append_bullet_list(
            elements=elements,
            bullet_items=bullet_items,
            styles=styles,
        )

        return elements

    @staticmethod
    def _append_bullet_list(
        *,
        elements: list[object],
        bullet_items: list[str],
        styles: dict[str, ParagraphStyle],
    ) -> None:
        """
        Add accumulated bullet points to the PDF document.
        """
        if not bullet_items:
            return

        list_items = [
            ListItem(
                Paragraph(
                    escape(item),
                    styles["bullet"],
                ),
                leftIndent=12,
            )
            for item in bullet_items
            if item.strip()
        ]

        if not list_items:
            return

        elements.append(
            ListFlowable(
                list_items,
                bulletType="bullet",
                start="circle",
                leftIndent=18,
                bulletFontName="Helvetica",
                bulletFontSize=8,
            )
        )

        elements.append(
            Spacer(
                1,
                3 * mm,
            )
        )

    @staticmethod
    def _looks_like_heading(
        text: str,
    ) -> bool:
        """
        Estimate whether a text line should appear as a heading.
        """
        normalized_text = text.strip()

        if not normalized_text:
            return False

        known_headings = {
            "hero section",
            "conclusion",
            "call to action",
            "final call to action",
            "benefits",
            "features",
            "testimonials",
            "frequently asked questions",
        }

        if normalized_text.lower() in known_headings:
            return True

        word_count = len(
            normalized_text.split()
        )

        if word_count > 10:
            return False

        if normalized_text.endswith(
            (
                ".",
                ",",
                ";",
                ":",
                "!",
                "?",
            )
        ):
            return False

        return normalized_text == normalized_text.title()