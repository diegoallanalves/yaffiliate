from __future__ import annotations

from html import escape
from io import BytesIO
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.report_data import ReportData


class PdfReportService:
    """
    Render a ReportData object as a professional Filtrify PDF.

    The generated report is returned as bytes so it can be:
    - downloaded through Streamlit;
    - saved locally;
    - attached to an email;
    - uploaded to cloud storage.
    """

    BRAND_NAME = "FILTRIFY"

    ACCENT_COLOR = colors.HexColor("#7C3AED")
    DARK_COLOR = colors.HexColor("#111827")
    DARK_PANEL_COLOR = colors.HexColor("#182235")
    DARK_BORDER_COLOR = colors.HexColor("#334155")

    MUTED_COLOR = colors.HexColor("#64748B")
    LIGHT_TEXT_COLOR = colors.HexColor("#CBD5E1")

    LIGHT_BACKGROUND = colors.HexColor("#F8FAFC")
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    SUCCESS_COLOR = colors.HexColor("#059669")
    SUCCESS_BACKGROUND = colors.HexColor("#ECFDF5")

    WARNING_COLOR = colors.HexColor("#B45309")

    PAGE_WIDTH, PAGE_HEIGHT = A4

    def generate(
        self,
        report: ReportData,
    ) -> bytes:
        """
        Generate the complete PDF and return it as raw bytes.
        """
        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=18 * mm,
            title=report.title,
            author=self.BRAND_NAME,
            subject=report.subtitle,
        )

        styles = self._build_styles()

        story = self._build_story(
            report=report,
            styles=styles,
        )

        document.build(
            story,
            onFirstPage=self._draw_page,
            onLaterPages=self._draw_page,
        )

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def save(
        self,
        report: ReportData,
        file_path: str,
    ) -> str:
        """
        Generate the report and save it to a local path.
        """
        destination = Path(file_path)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination.write_bytes(
            self.generate(report)
        )

        return str(destination)

    def _build_story(
        self,
        *,
        report: ReportData,
        styles: dict[str, ParagraphStyle],
    ) -> list:
        story: list = []

        story.extend(
            self._build_cover(
                report=report,
                styles=styles,
            )
        )

        story.append(PageBreak())

        story.extend(
            self._build_report_overview(
                report=report,
                styles=styles,
            )
        )

        story.extend(
            self._build_strategy_sections(
                report=report,
                styles=styles,
            )
        )

        story.extend(
            self._build_list_section(
                title="Key Strengths",
                items=report.strengths,
                styles=styles,
                marker_type="positive",
            )
        )

        story.extend(
            self._build_list_section(
                title="Weaknesses and Risks",
                items=report.weaknesses,
                styles=styles,
                marker_type="warning",
            )
        )

        story.extend(
            self._build_list_section(
                title="Strategic Recommendations",
                items=report.recommendations,
                styles=styles,
                marker_type="number",
            )
        )

        story.extend(
            self._build_list_section(
                title="Recommended Next Actions",
                items=report.next_actions,
                styles=styles,
                marker_type="number",
            )
        )

        story.extend(
            self._build_final_verdict(
                report=report,
                styles=styles,
            )
        )

        return story

    def _build_cover(
        self,
        *,
        report: ReportData,
        styles: dict[str, ParagraphStyle],
    ) -> list:
        """
        Build a single-page cover.

        All metadata stays inside one compact table so no cover
        content can overflow onto a second page.
        """
        metadata_table = self._cover_metrics_table(
            report=report,
            styles=styles,
        )

        cover_table = Table(
            [
                [
                    Paragraph(
                        self.BRAND_NAME,
                        styles["brand"],
                    )
                ],
                [
                    Spacer(
                        1,
                        23 * mm,
                    )
                ],
                [
                    Paragraph(
                        escape(report.title),
                        styles["cover_title"],
                    )
                ],
                [
                    Spacer(
                        1,
                        4 * mm,
                    )
                ],
                [
                    Paragraph(
                        escape(report.subtitle),
                        styles["cover_subtitle"],
                    )
                ],
                [
                    Spacer(
                        1,
                        18 * mm,
                    )
                ],
                [
                    metadata_table
                ],
            ],
            colWidths=[174 * mm],
        )

        cover_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        self.DARK_COLOR,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0,
                        self.DARK_COLOR,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        15 * mm,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        15 * mm,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7 * mm,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7 * mm,
                    ),
                ]
            )
        )

        return [
            Spacer(
                1,
                4 * mm,
            ),
            cover_table,
        ]

    def _cover_metrics_table(
        self,
        *,
        report: ReportData,
        styles: dict[str, ParagraphStyle],
    ) -> Table:
        """
        Display the client, selected product and confidence
        on the cover.
        """
        table = Table(
            [
                [
                    Paragraph(
                        "Prepared for",
                        styles["cover_label"],
                    ),
                    Paragraph(
                        "Best opportunity",
                        styles["cover_label"],
                    ),
                    Paragraph(
                        "Confidence",
                        styles["cover_label"],
                    ),
                ],
                [
                    Paragraph(
                        escape(report.generated_for),
                        styles["cover_value"],
                    ),
                    Paragraph(
                        escape(report.best_product),
                        styles["cover_value"],
                    ),
                    Paragraph(
                        f"{report.confidence_score:.1f}%",
                        styles["cover_value"],
                    ),
                ],
            ],
            colWidths=[
                47 * mm,
                64 * mm,
                39 * mm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        self.DARK_PANEL_COLOR,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        self.DARK_BORDER_COLOR,
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        self.DARK_BORDER_COLOR,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4 * mm,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4 * mm,
                    ),
                ]
            )
        )

        return table

    def _build_report_overview(
        self,
        *,
        report: ReportData,
        styles: dict[str, ParagraphStyle],
    ) -> list:
        metrics_table = Table(
            [
                [
                    Paragraph(
                        "Selected product",
                        styles["metric_label"],
                    ),
                    Paragraph(
                        "Analysis confidence",
                        styles["metric_label"],
                    ),
                ],
                [
                    Paragraph(
                        escape(report.best_product),
                        styles["metric_value"],
                    ),
                    Paragraph(
                        f"{report.confidence_score:.1f}%",
                        styles["metric_value"],
                    ),
                ],
            ],
            colWidths=[
                115 * mm,
                55 * mm,
            ],
        )

        metrics_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        self.LIGHT_BACKGROUND,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.8,
                        self.BORDER_COLOR,
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        self.BORDER_COLOR,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6 * mm,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6 * mm,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4 * mm,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4 * mm,
                    ),
                ]
            )
        )

        return [
            self._section_heading(
                title="Executive Overview",
                styles=styles,
            ),
            metrics_table,
            Spacer(
                1,
                5 * mm,
            ),
            self._content_box(
                title="Executive Summary",
                content=report.executive_summary,
                styles=styles,
            ),
            Spacer(
                1,
                4 * mm,
            ),
            self._content_box(
                title="Business Consultant Summary",
                content=report.business_consultant_summary,
                styles=styles,
            ),
            Spacer(
                1,
                6 * mm,
            ),
        ]

    def _build_strategy_sections(
        self,
        *,
        report: ReportData,
        styles: dict[str, ParagraphStyle],
    ) -> list:
        sections = [
            (
                "Commercial Strategy",
                report.commercial_strategy,
            ),
            (
                "SEO Strategy",
                report.seo_strategy,
            ),
            (
                "Google Ads Strategy",
                report.google_ads_strategy,
            ),
            (
                "Email Marketing Strategy",
                report.email_strategy,
            ),
            (
                "Landing Page Strategy",
                report.landing_page_strategy,
            ),
            (
                "Risk Analysis",
                report.risk_analysis,
            ),
        ]

        output: list = [
            self._section_heading(
                title="Recommended Growth Strategy",
                styles=styles,
            )
        ]

        for title, content in sections:
            output.append(
                KeepTogether(
                    [
                        self._content_box(
                            title=title,
                            content=content,
                            styles=styles,
                        ),
                        Spacer(
                            1,
                            3 * mm,
                        ),
                    ]
                )
            )

        return output

    def _build_list_section(
        self,
        *,
        title: str,
        items: Iterable[str],
        styles: dict[str, ParagraphStyle],
        marker_type: str,
    ) -> list:
        prepared_items = [
            str(item).strip()
            for item in items
            if str(item).strip()
        ]

        if not prepared_items:
            return []

        rows: list[list] = []

        for index, item in enumerate(
            prepared_items,
            start=1,
        ):
            marker_text, marker_style = self._get_list_marker(
                index=index,
                marker_type=marker_type,
                styles=styles,
            )

            rows.append(
                [
                    Paragraph(
                        marker_text,
                        marker_style,
                    ),
                    Paragraph(
                        escape(item),
                        styles["body"],
                    ),
                ]
            )

        list_table = Table(
            rows,
            colWidths=[
                9 * mm,
                161 * mm,
            ],
        )

        list_table.setStyle(
            TableStyle(
                [
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (0, -1),
                        2 * mm,
                    ),
                    (
                        "RIGHTPADDING",
                        (1, 0),
                        (1, -1),
                        0,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        1.1 * mm,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        1.1 * mm,
                    ),
                ]
            )
        )

        return [
            Spacer(
                1,
                3 * mm,
            ),
            self._section_heading(
                title=title,
                styles=styles,
            ),
            list_table,
            Spacer(
                1,
                2 * mm,
            ),
        ]

    def _get_list_marker(
        self,
        *,
        index: int,
        marker_type: str,
        styles: dict[str, ParagraphStyle],
    ) -> tuple[str, ParagraphStyle]:
        """
        Return a stable marker without relying on ListFlowable.

        This prevents every bullet item from being rendered
        incorrectly as the number 1.
        """
        if marker_type == "number":
            return (
                f"{index}.",
                styles["number_marker"],
            )

        if marker_type == "positive":
            return (
                "+",
                styles["positive_marker"],
            )

        return (
            "-",
            styles["warning_marker"],
        )

    def _build_final_verdict(
        self,
        *,
        report: ReportData,
        styles: dict[str, ParagraphStyle],
    ) -> list:
        verdict_table = Table(
            [
                [
                    Paragraph(
                        "Final Verdict",
                        styles["verdict_label"],
                    )
                ],
                [
                    Paragraph(
                        escape(report.final_verdict),
                        styles["verdict_text"],
                    )
                ],
                [
                    Paragraph(
                        (
                            "Analysis confidence: "
                            f"{report.confidence_score:.1f}%"
                        ),
                        styles["verdict_confidence"],
                    )
                ],
            ],
            colWidths=[170 * mm],
        )

        verdict_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        self.SUCCESS_BACKGROUND,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1,
                        self.SUCCESS_COLOR,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7 * mm,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        7 * mm,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        2.5 * mm,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        2.5 * mm,
                    ),
                ]
            )
        )

        return [
            Spacer(
                1,
                2 * mm,
            ),
            KeepTogether(
                [
                    verdict_table,
                    Spacer(
                        1,
                        3 * mm,
                    ),
                    Paragraph(
                        (
                            "This report is a strategic planning aid. "
                            "It does not guarantee revenue, rankings, "
                            "conversions or investment returns."
                        ),
                        styles["disclaimer"],
                    ),
                ]
            ),
        ]

    def _section_heading(
        self,
        *,
        title: str,
        styles: dict[str, ParagraphStyle],
    ) -> KeepTogether:
        """
        Keep each section heading attached to its divider.
        """
        return KeepTogether(
            [
                Paragraph(
                    escape(title),
                    styles["section_title"],
                ),
                HRFlowable(
                    width="100%",
                    thickness=1,
                    color=self.ACCENT_COLOR,
                    spaceAfter=4 * mm,
                ),
            ]
        )

    def _content_box(
        self,
        *,
        title: str,
        content: str,
        styles: dict[str, ParagraphStyle],
    ) -> Table:
        """
        Build a complete strategy or analysis card.

        The heading and body stay inside the same table so they
        cannot be separated across pages.
        """
        table = Table(
            [
                [
                    Paragraph(
                        escape(title),
                        styles["box_title"],
                    )
                ],
                [
                    Paragraph(
                        escape(content),
                        styles["body"],
                    )
                ],
            ],
            colWidths=[170 * mm],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        self.LIGHT_BACKGROUND,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        self.BORDER_COLOR,
                    ),
                    (
                        "LINEBEFORE",
                        (0, 0),
                        (0, -1),
                        3,
                        self.ACCENT_COLOR,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6 * mm,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6 * mm,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        3.2 * mm,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        3.2 * mm,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )

        return table

    def _build_styles(
        self,
    ) -> dict[str, ParagraphStyle]:
        base_styles = getSampleStyleSheet()

        return {
            "brand": ParagraphStyle(
                "FiltrifyBrand",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=15,
                textColor=self.ACCENT_COLOR,
                alignment=TA_LEFT,
                tracking=2,
            ),
            "cover_title": ParagraphStyle(
                "CoverTitle",
                parent=base_styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=27,
                leading=33,
                textColor=colors.white,
                alignment=TA_LEFT,
            ),
            "cover_subtitle": ParagraphStyle(
                "CoverSubtitle",
                parent=base_styles["Normal"],
                fontName="Helvetica",
                fontSize=13,
                leading=18,
                textColor=self.LIGHT_TEXT_COLOR,
                alignment=TA_LEFT,
            ),
            "cover_label": ParagraphStyle(
                "CoverLabel",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=7.5,
                leading=10,
                textColor=colors.HexColor("#94A3B8"),
            ),
            "cover_value": ParagraphStyle(
                "CoverValue",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                textColor=colors.white,
            ),
            "section_title": ParagraphStyle(
                "SectionTitle",
                parent=base_styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=15,
                leading=19,
                textColor=self.DARK_COLOR,
                spaceBefore=2 * mm,
                spaceAfter=1.5 * mm,
            ),
            "box_title": ParagraphStyle(
                "BoxTitle",
                parent=base_styles["Heading3"],
                fontName="Helvetica-Bold",
                fontSize=10.5,
                leading=13,
                textColor=self.ACCENT_COLOR,
                spaceAfter=1.5 * mm,
            ),
            "body": ParagraphStyle(
                "Body",
                parent=base_styles["BodyText"],
                fontName="Helvetica",
                fontSize=9.2,
                leading=13.2,
                textColor=self.DARK_COLOR,
                alignment=TA_LEFT,
            ),
            "metric_label": ParagraphStyle(
                "MetricLabel",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=11,
                textColor=self.MUTED_COLOR,
            ),
            "metric_value": ParagraphStyle(
                "MetricValue",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=13,
                leading=17,
                textColor=self.DARK_COLOR,
            ),
            "number_marker": ParagraphStyle(
                "NumberMarker",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=13.2,
                textColor=self.ACCENT_COLOR,
                alignment=TA_LEFT,
            ),
            "positive_marker": ParagraphStyle(
                "PositiveMarker",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13.2,
                textColor=self.SUCCESS_COLOR,
                alignment=TA_LEFT,
            ),
            "warning_marker": ParagraphStyle(
                "WarningMarker",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13.2,
                textColor=self.WARNING_COLOR,
                alignment=TA_LEFT,
            ),
            "verdict_label": ParagraphStyle(
                "VerdictLabel",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                textColor=self.SUCCESS_COLOR,
            ),
            "verdict_text": ParagraphStyle(
                "VerdictText",
                parent=base_styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=13,
                leading=17,
                textColor=self.DARK_COLOR,
                spaceBefore=1 * mm,
                spaceAfter=1 * mm,
            ),
            "verdict_confidence": ParagraphStyle(
                "VerdictConfidence",
                parent=base_styles["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                textColor=self.MUTED_COLOR,
            ),
            "disclaimer": ParagraphStyle(
                "Disclaimer",
                parent=base_styles["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=7.4,
                leading=10,
                textColor=self.MUTED_COLOR,
                alignment=TA_CENTER,
            ),
        }

    def _draw_page(
        self,
        canvas,
        document,
    ) -> None:
        """
        Draw the branded footer and page number.
        """
        canvas.saveState()

        page_width, _ = A4

        canvas.setStrokeColor(
            self.BORDER_COLOR
        )

        canvas.line(
            18 * mm,
            13 * mm,
            page_width - 18 * mm,
            13 * mm,
        )

        canvas.setFont(
            "Helvetica",
            7.5,
        )

        canvas.setFillColor(
            self.MUTED_COLOR
        )

        canvas.drawString(
            18 * mm,
            8.5 * mm,
            (
                "Generated by Filtrify - "
                "Affiliate Intelligence Platform"
            ),
        )

        canvas.drawRightString(
            page_width - 18 * mm,
            8.5 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()