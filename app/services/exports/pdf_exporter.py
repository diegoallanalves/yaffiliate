"""PDF campaign-summary exports for Filtrify."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from app.services.exports.base_exporter import BaseExporter


class PdfExporter(BaseExporter):
    """Create a concise, professional campaign-summary PDF."""

    def campaign_summary_to_bytes(self, campaign: Any) -> bytes:
        """Return a complete campaign summary as PDF bytes."""

        self.validate_campaign(campaign)

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
                TableStyle,
            )
        except ImportError as error:
            raise RuntimeError(
                "reportlab is required for PDF exports. "
                "Install it with: pip install reportlab"
            ) from error

        stream = BytesIO()
        document = SimpleDocTemplate(
            stream,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
            title=campaign.campaign_name,
            author="Filtrify",
        )

        styles = getSampleStyleSheet()
        story = [
            Paragraph(campaign.campaign_name, styles["Title"]),
            Paragraph(
                f"Product: {campaign.product_name}",
                styles["Normal"],
            ),
            Spacer(1, 8),
        ]

        summary_data = [
            ["Metric", "Value"],
            ["Campaign assets", str(campaign.asset_count)],
            [
                "Estimated words",
                f"{campaign.total_estimated_words:,}",
            ],
            [
                "Average quality",
                f"{campaign.average_quality_score:.1f}/100",
            ],
            ["Target keyword", campaign.target_keyword],
            ["Target audience", campaign.target_audience],
            ["Writing tone", campaign.tone],
            ["Created", campaign.created_at.isoformat()],
        ]

        summary_table = Table(
            summary_data,
            colWidths=[45 * mm, 110 * mm],
        )
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        story.extend(
            [
                Paragraph("Campaign Summary", styles["Heading1"]),
                summary_table,
                Spacer(1, 12),
                Paragraph("Included Assets", styles["Heading1"]),
            ]
        )

        assets = (
            (
                "SEO Article",
                f"{campaign.seo_article.title} "
                f"({campaign.seo_article.seo_score:.1f}/100 SEO score)",
            ),
            (
                "Landing Page",
                f"{campaign.landing_page.page_title} "
                f"({campaign.landing_page.conversion_score:.1f}/100 conversion score)",
            ),
            (
                "Email Sequence",
                f"{campaign.email_sequence.email_count} emails",
            ),
            (
                "Google Ads",
                f"{campaign.google_ads.headline_count} headlines, "
                f"{campaign.google_ads.description_count} descriptions, "
                f"{campaign.google_ads.keyword_count} keywords",
            ),
        )

        for name, description in assets:
            story.append(
                Paragraph(
                    f"<b>{name}</b>: {description}",
                    styles["BodyText"],
                )
            )
            story.append(Spacer(1, 5))

        document.build(story)
        stream.seek(0)
        return stream.read()

    def export_campaign_summary(
        self,
        campaign: Any,
        *,
        output_directory: str | Path = "outputs/campaigns",
        file_name: str | None = None,
    ) -> Path:
        """Write a campaign-summary PDF to disk."""

        resolved_name = file_name or self.build_file_name(
            stem=f"{campaign.campaign_name}_summary",
            extension="pdf",
        )

        if not resolved_name.lower().endswith(".pdf"):
            resolved_name = self.build_file_name(
                stem=resolved_name,
                extension="pdf",
            )

        return self.write_bytes(
            data=self.campaign_summary_to_bytes(campaign),
            output_directory=output_directory,
            file_name=resolved_name,
        )
